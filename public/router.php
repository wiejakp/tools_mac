<?php

// Router for the optional local PHP development server; Valet uses index.php.
$path = rawurldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?? '/');
$candidate = realpath(__DIR__.$path);
if ($candidate !== false && str_starts_with($candidate, __DIR__.'/') && is_file($candidate) && pathinfo($candidate, PATHINFO_EXTENSION) !== 'php') {
    return false;
}
require __DIR__.'/index.php';
