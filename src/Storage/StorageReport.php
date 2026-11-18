<?php

declare(strict_types=1);

namespace App\Storage;

final readonly class StorageReport
{
    public function __construct(private string $projectDir)
    {
    }

    public function read(): array
    {
        $empty = ['status' => 'missing', 'projects' => [], 'directories' => [],
            'generated_at' => null, 'stale' => false, 'partial' => false,
            'sites_root' => dirname($this->projectDir), 'scope' => 'sites'];
        $file = $this->projectDir.'/var/storage-audit.json';
        if (is_link(dirname($file)) || is_link($file)) {
            return array_replace($empty, ['status' => 'invalid']);
        }
        if (!is_file($file)) {
            return $empty;
        }
        if (!is_readable($file) || filesize($file) > 8_000_000) {
            return array_replace($empty, ['status' => 'invalid']);
        }
        $bytes = @file_get_contents($file);
        $data = $bytes === false ? null : json_decode($bytes, true);
        if (!is_array($data) || ($data['schema_version'] ?? null) !== 1
            || !is_string($data['generated_at'] ?? null) || strtotime($data['generated_at']) === false
            || !is_string($data['sites_root'] ?? null) || !is_bool($data['partial'] ?? null)
            || !in_array($data['scope'] ?? null, ['sites', 'whole-mac'], true)
            || !$this->validRows($data['projects'] ?? null)
            || !$this->validRows($data['directories'] ?? null)) {
            return array_replace($empty, ['status' => 'invalid']);
        }

        return array_replace($empty, [
            'status' => 'ready', 'projects' => $data['projects'], 'directories' => $data['directories'],
            'generated_at' => $data['generated_at'], 'sites_root' => $data['sites_root'],
            'scope' => $data['scope'], 'partial' => $data['partial'],
            'stale' => time() - strtotime($data['generated_at']) > 86400,
        ]);
    }

    private function validRows(mixed $rows): bool
    {
        if (!is_array($rows) || !array_is_list($rows)) {
            return false;
        }
        foreach ($rows as $row) {
            if (!is_array($row) || !is_string($row['name'] ?? null) || !is_string($row['path'] ?? null)
                || !is_bool($row['partial'] ?? null) || !is_array($row['children'] ?? null)) {
                return false;
            }
            foreach (['allocated_bytes', 'logical_bytes', 'files', 'errors', 'skipped'] as $key) {
                if (!is_int($row[$key] ?? null) || $row[$key] < 0) {
                    return false;
                }
            }
            foreach ($row['children'] as $child) {
                if (!is_array($child) || !is_string($child['name'] ?? null)
                    || !is_int($child['allocated_bytes'] ?? null) || $child['allocated_bytes'] < 0) {
                    return false;
                }
            }
        }

        return true;
    }

    public function volume(): array
    {
        $total = @disk_total_space($this->projectDir);
        $free = @disk_free_space($this->projectDir);
        if ($total === false || $free === false || $total <= 0) {
            return ['available' => false, 'total_bytes' => 0, 'free_bytes' => 0,
                'used_bytes' => 0, 'used_percent' => 0];
        }

        return ['available' => true, 'total_bytes' => (int) $total, 'free_bytes' => (int) $free,
            'used_bytes' => (int) ($total - $free), 'used_percent' => round((1 - $free / $total) * 100, 1)];
    }

    public static function formatBytes(int|float $bytes): string
    {
        foreach (['B', 'KiB', 'MiB', 'GiB', 'TiB'] as $unit) {
            if ($bytes < 1024 || $unit === 'TiB') {
                return number_format($bytes, $unit === 'B' ? 0 : 1).' '.$unit;
            }
            $bytes /= 1024;
        }

        return '0 B';
    }
}
