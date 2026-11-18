# Enforce HTTPS and repair command copying — 2026-11-18

## Request and initial evidence

The user completed their Terminal setup and reported that command copying shows
"Clipboard unavailable". They explicitly requested that the application force
HTTPS. The Git root is this checkout; the working tree was clean at `6bedea3`.
Previously loaded debugging and verification guidance continues to apply. There
is no matching CCE registration; use bounded local retrieval without new global
configuration or another repository's index.

A local TLS handshake with SNI `tools_mac.test` currently presents a certificate
for a different Valet site, `app_budget.test`. Its subject alternative names do
not include `tools_mac.test`. A local HTTP HEAD request for `/health` returned
200, not a redirect. Browser HTTPS verification stops at the hostname mismatch;
no certificate warning will be bypassed. Clipboard API access is restricted on
ordinary HTTP origins, and the existing JavaScript has no copy fallback.

## Exact planned effects and order

1. Preserve original bytes/modes of `public/assets/app.js`, `public/assets/app.css`,
   `templates/base.html.twig`, `src/EventSubscriber/LocalRequestSubscriber.php`,
   `tests/run.php`, `Makefile`, `README.md` and `public/index.php` in ignored
   `tooling/logs/change-backups/2026-11-18-https-clipboard/`. Record the absent new
   paths `public/assets/clipboard.mjs` and `tests/clipboard.test.mjs`.
2. Add failing application checks for a permanent HTTPS redirect on the Valet
   hostname, preserved path/query, secure requests and loopback preview behavior.
   Add clipboard tests for API success, API rejection, unavailable APIs, copy
   fallback cleanup/focus and graceful manual copying.
3. Redirect non-secure requests to trusted non-loopback hostnames to HTTPS,
   preserving path/query and using 308. Keep local-only access restrictions and
   loopback HTTP preview support. Do not trust spoofed forwarded headers.
4. Add a small local ES module for native clipboard copying with a DOM copy
   fallback. If both APIs fail, show a persistent dialog with selected command
   text for the user's normal Copy shortcut. No command is executed by the app.
5. Try only native site-scoped Valet certificate setup if it can authenticate;
   do not modify global PHP, unrelated Nginx sites or trust settings. Capture
   native status before any native change. Never read/copy TLS private keys.
6. Run focused failing/passing tests and `make verify`; inspect actual HTTP/TLS
   behavior and browser copying. Keep private reports and mounted shares intact.
   Stop only owned diagnostic processes and record any remaining native blocker.

## Risks and rollback

Redirects must not loop on real HTTPS or change the local preview scheme. Copy
fallback must work from inside a modal, restore focus, remove its temporary
textarea, and honestly report failure. Native TLS setup can require interactive
sudo, which cannot be supplied by the assistant; no password will be requested
through chat. No weakening of browser TLS validation is permitted.

1. Run the local guarded recovery check listed in the final results below before
   restoration; it refuses later edits or unexpected file replacements.
2. Restore the eight original source files byte-for-byte with their saved modes;
   remove only unchanged task-created module/test files. Retain this audit record
   and the local recovery archive. Regenerable runtime caches may be refreshed
   through Symfony; never overwrite the saved storage report.
3. If a new native secure-site configuration is actually created, compare its
   final public certificate fingerprint to the recorded value before considering
   `valet unsecure tools_mac`. Only undo this exact site's new configuration;
   never change global trust or another site's certificate.
4. Verify original routes and tools and review the working tree. No disk cleanup,
   dependency update, global configuration repair or remote publication is planned.

## Results

In progress. Backup manifests, verification, observed browser behavior and exact
recovery commands will be recorded before completion.
