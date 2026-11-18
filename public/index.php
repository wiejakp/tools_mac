<?php

declare(strict_types=1);

require dirname(__DIR__).'/vendor/autoload.php';

use Symfony\Component\HttpFoundation\Request;

$environment = $_SERVER['APP_ENV'] ?? 'dev';
$kernel = new App\Kernel($environment, $environment !== 'prod');
$request = Request::createFromGlobals();
$response = $kernel->handle($request);
$response->send();
$kernel->terminate($request, $response);
