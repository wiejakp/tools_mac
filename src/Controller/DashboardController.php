<?php

declare(strict_types=1);

namespace App\Controller;

use App\Storage\StorageReport;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class DashboardController extends AbstractController
{
    #[Route('/', name: 'dashboard', methods: ['GET'])]
    public function index(StorageReport $storage): Response
    {
        $report = $storage->read();
        $projects = $report['projects'];
        $total = array_sum(array_column($projects, 'allocated_bytes'));
        $tools = [
            ['name' => 'Inspect disk usage', 'description' => 'Measure local storage and rank your largest projects.', 'category' => 'Storage', 'icon' => 'storage', 'command' => 'make audit-mac', 'badge' => 'Read only'],
            ['name' => 'Clear application caches', 'description' => 'Preview generated framework caches before cleaning.', 'category' => 'Cleanup', 'icon' => 'spark', 'command' => 'make preview-cache', 'badge' => 'Preview'],
            ['name' => 'Clear application logs', 'description' => 'Preview runtime and rotated logs across your sites.', 'category' => 'Cleanup', 'icon' => 'file', 'command' => 'make preview-logs', 'badge' => 'Preview'],
            ['name' => 'Mount network drives', 'description' => 'Connect work and home drives in Terminal.', 'category' => 'Network', 'icon' => 'network', 'command' => 'make mount', 'badge' => 'Interactive'],
            ['name' => 'Check agent tooling', 'description' => 'Check local coding tools, hooks and repository context.', 'category' => 'Development', 'icon' => 'code', 'command' => 'make check-agent-tools', 'badge' => 'Diagnostic'],
            ['name' => 'Verify this project', 'description' => 'Run application checks and disposable tool tests.', 'category' => 'Development', 'icon' => 'check', 'command' => 'make verify', 'badge' => 'Local'],
        ];

        return $this->render('dashboard/index.html.twig', [
            'report' => $report, 'volume' => $storage->volume(), 'tools' => $tools,
            'projects_bytes' => $total,
            'project_dir' => $this->getParameter('kernel.project_dir'),
        ]);
    }

    #[Route('/health', name: 'health', methods: ['GET'])]
    public function health(): JsonResponse
    {
        return $this->json(['status' => 'ok', 'php' => PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION,
            'symfony' => \Symfony\Component\HttpKernel\Kernel::VERSION]);
    }
}
