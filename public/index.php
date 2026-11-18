<?php

declare(strict_types=1);

require dirname(__DIR__).'/vendor/autoload.php';

use Symfony\Component\HttpFoundation\Request;

$kernel = new App\Kernel($_SERVER['APP_ENV'] ?? 'dev', false);
$request = Request::createFromGlobals();
$response = $kernel->handle($request);
$response->send();
$kernel->terminate($request, $response);
