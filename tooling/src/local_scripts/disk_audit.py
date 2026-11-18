"""Read-only local storage audit. Reads metadata, never file contents or links."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import time

PROJECT = Path(__file__).absolute().parents[3]
CLOUD = ("googledrive", "google drive", "onedrive", "sharepoint", "dropbox", "icloud", "fileprovider", "file provider")
PRIVATE = {"cloudstorage", "mobile documents", "box", ".ssh", ".aws", ".gnupg", ".azure", "keychains", "credentials", ".kube"}
MOUNTS = {"Volumes", "Network", "net", "dev", "automount"}
FIELDS = ("allocated_bytes", "logical_bytes", "files", "errors", "skipped")


def excluded(path):
    return any(part.casefold() in PRIVATE or part in MOUNTS or
               any(word in part.casefold() for word in CLOUD) for part in Path(path).parts)


def empty():
    return dict.fromkeys(FIELDS, 0)


def open_directory(path):
    """Open every component without following symlinks (including the root)."""
    path = Path(os.path.abspath(path))
    if excluded(path):
        raise ValueError("Excluded local path")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def measure(path, deadline=None, cache=None, device=None):
    """Allocated and logical regular-file totals, deduplicated by inode per scan."""
    path = Path(os.path.abspath(path))
    result = empty()
    children, seen, stack = {}, set(), []
    deadline = deadline if deadline is not None else time.monotonic() + 180
    try:
        fd = open_directory(path)
        info = os.fstat(fd)
        if device is not None and info.st_dev != device:
            os.close(fd)
            result["skipped"] += 1
        else:
            device = info.st_dev
            stack.append((fd, path, None))
        while stack:
            if time.monotonic() > deadline:
                result["errors"] += 1
                break
            current_fd, current, bucket = stack.pop()
            try:
                with os.scandir(current_fd) as entries:
                    for entry in entries:
                        if time.monotonic() > deadline:
                            result["errors"] += 1
                            break
                        child_path = current / entry.name
                        # Ancestors were already checked before opening; check the
                        # new component without rechecking every ancestor per file.
                        if excluded(Path(entry.name)):
                            result["skipped"] += 1
                            continue
                        group = bucket or entry.name
                        totals = children.setdefault(group, empty())
                        try:
                            info = entry.stat(follow_symlinks=False)
                            if info.st_dev != device or stat.S_ISLNK(info.st_mode):
                                result["skipped"] += 1
                                totals["skipped"] += 1
                            elif stat.S_ISDIR(info.st_mode):
                                cached = (cache or {}).get(str(child_path))
                                if cached is not None:
                                    for key in FIELDS:
                                        result[key] += cached[key]
                                        totals[key] += cached[key]
                                else:
                                    child_fd = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                                       dir_fd=current_fd)
                                    if os.fstat(child_fd).st_dev != device:
                                        os.close(child_fd)
                                        result["skipped"] += 1
                                    else:
                                        stack.append((child_fd, child_path, group))
                            elif stat.S_ISREG(info.st_mode):
                                inode = (info.st_dev, info.st_ino)
                                if inode not in seen:
                                    seen.add(inode)
                                    values = {"allocated_bytes": info.st_blocks * 512,
                                              "logical_bytes": info.st_size, "files": 1}
                                    for key, value in values.items():
                                        result[key] += value
                                        totals[key] += value
                        except OSError:
                            result["errors"] += 1
                            totals["errors"] += 1
            except OSError:
                result["errors"] += 1
            finally:
                os.close(current_fd)
    except (OSError, ValueError):
        result["errors"] += 1
    finally:
        for remaining, _, _ in stack:
            os.close(remaining)
    result["partial"] = result["errors"] > 0
    result["children"] = sorted((dict(name=name, **data) for name, data in children.items()),
                                key=lambda row: row["allocated_bytes"], reverse=True)[:20]
    return result


def project_usage(sites, deadline=None, cache=None):
    projects = []
    fd = open_directory(sites)
    try:
        device = os.fstat(fd).st_dev
        with os.scandir(fd) as entries:
            names = sorted(e.name for e in entries if not excluded(Path(e.name)) and
                           e.is_dir(follow_symlinks=False))
        for name in names:
            path = Path(sites) / name
            result = measure(path, deadline=deadline, device=device)
            if cache is not None:
                cache[str(path)] = result
            projects.append(dict(name=name, path=str(path), **result))
    finally:
        os.close(fd)
    return sorted(projects, key=lambda row: row["allocated_bytes"], reverse=True)


def human(value):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return "{:.1f} {}".format(value, unit)
        value /= 1024


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites-root", type=Path, default=PROJECT.parent,
                        help="sites directory (default: parent of this checkout)")
    parser.add_argument("--whole-mac", action="store_true", help="also measure local user, application and system-data folders")
    parser.add_argument("--output", type=Path, default=PROJECT / "var/storage-audit.json",
                        help="local JSON report (default: this checkout's var/storage-audit.json)")
    parser.add_argument("--max-seconds", type=int, default=600, help="scan time budget, 1–3600 seconds")
    args = parser.parse_args(argv)
    if not 1 <= args.max_seconds <= 3600:
        parser.error("--max-seconds must be between 1 and 3600")
    started = time.monotonic()
    deadline = started + args.max_seconds
    sites = Path(os.path.abspath(args.sites_root))
    cache = {}
    print("Measuring local storage metadata; cloud folders and mounts are excluded.", flush=True)
    try:
        projects = project_usage(sites, deadline=deadline, cache=cache)
    except (OSError, ValueError):
        print("Cannot inspect the sites directory; no report was replaced.", file=sys.stderr)
        return 1
    scopes = []
    roots = [sites]
    if args.whole_mac:
        roots = [Path(p) for p in ("/Users", "/Applications", "/Library", "/opt", "/usr/local", "/private")]
    for root in roots:
        print("Measuring " + str(root), flush=True)
        scopes.append(dict(name=root.name, path=str(root), **measure(root, deadline=deadline, cache=cache,
                                                                  device=PROJECT.stat().st_dev)))
    capacity = shutil.disk_usage(PROJECT)
    used_percent = round(capacity.used / capacity.total * 100, 1) if capacity.total else 0
    report = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
              "scope": "whole-mac" if args.whole_mac else "sites", "sites_root": str(sites),
              "duration_seconds": round(time.monotonic() - started, 2),
              "volume": {"total_bytes": capacity.total, "used_bytes": capacity.used,
                         "free_bytes": capacity.free, "used_percent": used_percent},
              "projects": projects, "directories": sorted(scopes, key=lambda row: row["allocated_bytes"], reverse=True),
              "partial": any(p["partial"] for p in projects + scopes),
              "exclusions": "Cloud/File Provider folders, credential stores, symlinks and other mounted filesystems.",
              "measurement": "Allocated regular-file bytes; hardlinks counted once within each directory scan. APFS clones and snapshots can differ from these totals."}
    output = Path(os.path.abspath(args.output))
    try:
        # Only write reports inside this checkout, through non-symlink parents.
        output.relative_to(PROJECT)
        if excluded(output) or output.is_symlink():
            raise ValueError()
        output.parent.mkdir(parents=True, exist_ok=True)
        fd = open_directory(output.parent)
        os.close(fd)
        with tempfile.NamedTemporaryFile(mode="w", dir=output.parent, prefix=".audit-", delete=False) as stream:
            temp_path = Path(stream.name)
            os.fchmod(stream.fileno(), 0o600)
            json.dump(report, stream, indent=2)
            stream.write("\n")
        os.replace(temp_path, output)
    except (OSError, ValueError):
        print("Cannot write report inside this checkout.", file=sys.stderr)
        return 1
    print("\nVolume: {} used / {} total ({:.1f}%); {} free".format(
        human(capacity.used), human(capacity.total), used_percent, human(capacity.free)))
    print("\nLargest site projects (allocated file data):")
    for project in projects[:12]:
        print("  {:>11}  {}{}".format(human(project["allocated_bytes"]), project["name"],
                                       " [partial]" if project["partial"] else ""))
    if args.whole_mac:
        print("\nLargest measured local folders:")
        for directory in report["directories"]:
            print("  {:>11}  {}{}".format(human(directory["allocated_bytes"]), directory["path"],
                                           " [partial]" if directory["partial"] else ""))
    print("\n" + ("Partial audit: some folders were inaccessible or exceeded the time budget." if report["partial"] else "Audit complete."))
    print("No files deleted. Report: " + str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
