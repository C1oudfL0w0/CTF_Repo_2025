<?php
require_once '../config.php';

if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1' && $_SERVER['REMOTE_ADDR'] !== '::1') {
    header('HTTP/1.1 403 Forbidden');
    echo json_encode(['error' => '访问被拒绝。此端点仅可从localhost访问。']);
    exit;
}

// 如果我们到达这里，说明是从localhost访问的（XXE可以绕过这个限制）
echo json_encode([
    'debug' => true,
    'secret_files' => ['/var/www/secrets/token.txt', '/flag'], 
    'message' => '此端点揭示敏感信息。flag位于/flag'
]);