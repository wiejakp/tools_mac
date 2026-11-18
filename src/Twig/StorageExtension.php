<?php

declare(strict_types=1);

namespace App\Twig;

use App\Storage\StorageReport;
use Twig\Extension\AbstractExtension;
use Twig\TwigFilter;

final class StorageExtension extends AbstractExtension
{
    public function getFilters(): array
    {
        return [new TwigFilter('bytes', StorageReport::formatBytes(...))];
    }
}
