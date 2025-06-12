<?php
// 配置信息
$CONFIG = [
    'db_name' => 'ctf_challenge',
    'auth_key' => 'S3cr3tK3y!2023',
    'api_secret' => 'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec',
    'debug_token' => '7f8a1a4b3c7d9e6f2b5s8d7f9g6h5j4k3l2m1n'
];

// 数据库模拟（在实际环境中，这会是一个真正的数据库）
$USERS = [
    'user' => [
        'password' => 'password123',
        'role' => 'user'
    ],
    'admin' => [
        'password' => 'admin_secure_password',
        'role' => 'admin'
    ],
    'dev' => [
        'password' => 'dev_password',
        'role' => 'developer'
    ]
];

$DOCUMENTS = [
    'welcome.txt' => [
        'content' => '欢迎使用我们安全的文档管理系统!',
        'access' => 'user'
    ],
    'confidential_note.txt' => [
        'content' => "内部API令牌: c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec",
        'access' => 'admin'
    ],
    'confidential_dev.txt' => [
        'content' => "内部API端点:\n- status\n- config\n- debug (仅限本地访问)\n\n查看 /data/app/www/secrettttts/ 获取开发令牌。",
        'access' => 'admin'
    ]
];
?>