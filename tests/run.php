<?php

declare(strict_types=1);

require dirname(__DIR__).'/vendor/autoload.php';

use App\Storage\StorageReport;
use Symfony\Component\HttpFoundation\Request;

$checks = 0;
$assert = static function (bool $condition, string $message) use (&$checks): void {
    ++$checks;
    if (!$condition) {
        throw new RuntimeException($message);
    }
};
$root = dirname(__DIR__);
$fixture = __DIR__.'/.report-test-'.bin2hex(random_bytes(6));
mkdir($fixture, 0700);

try {
    $reader = new StorageReport($fixture);
    $assert($reader->read()['status'] === 'missing', 'Missing report must show an empty state');
    mkdir($fixture.'/var');
    file_put_contents($fixture.'/var/storage-audit.json', '{broken');
    $assert($reader->read()['status'] === 'invalid', 'Malformed report must not break the page');
    file_put_contents($fixture.'/var/storage-audit.json', json_encode(['schema_version' => 1, 'projects' => 'wrong']));
    $assert($reader->read()['status'] === 'invalid', 'Malformed report schema must be rejected');
    $sample = [
        'schema_version' => 1, 'generated_at' => '2020-01-01T00:00:00+00:00',
        'sites_root' => dirname($fixture), 'scope' => 'sites', 'partial' => true,
        'projects' => [['name' => '<script>private</script>', 'path' => '/sample', 'allocated_bytes' => 4096,
                        'logical_bytes' => 12, 'files' => 1, 'errors' => 1, 'skipped' => 0, 'partial' => true, 'children' => []]],
        'directories' => [], 'volume' => ['total_bytes' => 100, 'used_bytes' => 90, 'free_bytes' => 10, 'used_percent' => 90],
    ];
    file_put_contents($fixture.'/var/storage-audit.json', json_encode($sample));
    $data = $reader->read();
    $assert($data['status'] === 'ready' && $data['stale'], 'Old reports must be marked stale');
    $assert($data['partial'], 'Incomplete scans must remain visible');
    $assert($reader->volume()['total_bytes'] > 0, 'Live capacity must be available');
    $sample['projects'][0]['allocated_bytes'] = -1;
    file_put_contents($fixture.'/var/storage-audit.json', json_encode($sample));
    $assert($reader->read()['status'] === 'invalid', 'Negative or invalid measurements must be rejected');

    $kernel = new App\Kernel('test', true);
    $request = Request::create('http://localhost/');
    $response = $kernel->handle($request);
    $assert($response->getStatusCode() === 200, 'Dashboard must return 200');
    $assert(str_contains($response->getContent(), 'Storage overview'), 'Dashboard must render storage');
    $assert(str_contains($response->getContent(), 'Largest site projects'), 'Dashboard must render sites');
    $assert(str_contains($response->getContent(), 'Clear application caches'), 'Dashboard must render tools');
    $assert(!str_contains($response->getContent(), 'https://fonts.'), 'No external fonts or trackers');
    $assert($response->headers->get('Cache-Control') === 'no-store, private', 'Private reports must not be cached');
    $kernel->terminate($request, $response);
    $response = $kernel->handle(Request::create('http://localhost/health'));
    $assert($response->getStatusCode() === 200, 'Health endpoint must return 200');
    $assert(json_decode($response->getContent(), true)['php'] === '8.3', 'Health must verify the serving PHP minor');
    $response = $kernel->handle(Request::create('http://localhost/', 'GET', server: ['REMOTE_ADDR' => '192.168.1.2']));
    $assert($response->getStatusCode() === 403, 'Remote clients cannot view private storage reports');
    $response = $kernel->handle(Request::create('http://localhost/', 'POST'));
    $assert($response->getStatusCode() === 405, 'Web requests cannot execute tools');
    $response = $kernel->handle(Request::create('http://localhost/?path=/etc&command=rm'));
    $assert($response->getStatusCode() === 200, 'Query parameters cannot execute tools or arbitrary scans');
    $kernel->shutdown();
    $webKernel = new App\Kernel('dev', false);
    $webResponse = $webKernel->handle(Request::create('http://localhost/health'));
    $assert($webResponse->getStatusCode() === 200, 'The non-debug web kernel must use current dependency services');
    $webKernel->shutdown();
    echo "Application checks: {$checks} passed\n";
} finally {
    @unlink($fixture.'/var/storage-audit.json');
    @rmdir($fixture.'/var');
    rmdir($fixture);
}
