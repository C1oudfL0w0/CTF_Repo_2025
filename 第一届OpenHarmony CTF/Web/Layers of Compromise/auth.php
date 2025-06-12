<?php
// 移除session_start()，改用cookie认证

function authenticate($username, $password) {
    global $USERS, $CONFIG;
    
    // 漏洞1: 可以使用换行符绕过的正则表达式检查
    if (preg_match('/^[a-zA-Z0-9_]+$/', $username)) {
        if (isset($USERS[$username]) && $USERS[$username]['password'] === $password) {
            setcookie('username', $username, time() + 3600, '/');
            setcookie('role', $USERS[$username]['role'], time() + 3600, '/');
            return true;
        }
    }
    return false;
}

function check_auth() {
    if (isset($_COOKIE['username'])) {
        return true;
    }
    return false;
}

function get_role() {
    return isset($_COOKIE['role']) ? $_COOKIE['role'] : 'guest';
}

function is_admin() {
    return get_role() === 'admin';
}

function is_developer() {
    global $CONFIG;
    
    // 检查开发者cookie
    if (isset($_COOKIE['auth_token'])) {
        $auth_data = unserialize(base64_decode($_COOKIE['auth_token']));
        if (isset($auth_data['username']) && isset($auth_data['hash'])) {
            if ($auth_data['username'] === 'dev' && 
                $auth_data['hash'] === md5('dev' . $CONFIG['auth_key'])) {
                return true;
            }
        }
    }
    
    return get_role() === 'developer';
}
?>