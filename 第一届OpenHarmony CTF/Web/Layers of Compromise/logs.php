<?php
require_once 'config.php';
require_once 'auth.php';


if (!check_auth() || !is_developer()) {
    header('Location: index.php');
    exit;
}

$role = get_role();


if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $log_dir = 'E:\tools\Web\phpStudy_64\Extensions\Nginx1.15.11\logs';
    $log_file = $log_dir . '\access.log';
} else {
    $log_dir = '/data/app/nginx/logs';
    $log_file = $log_dir . '/access.log';
}

$log_content = '';
$filter = '';
$debug_info = '';
$error_message = '';


if (!is_dir($log_dir)) {
    mkdir($log_dir, 0755, true);
}

// 如果不存在则创建示例日志文件
if (!file_exists($log_file)) {
    $dummy_log = "192.168.1.1 - - [01/Jan/2023:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1234 \"-\" \"Mozilla/5.0\"\n";
    $dummy_log .= "192.168.1.2 - - [01/Jan/2023:12:05:00 +0000] \"GET /login.php HTTP/1.1\" 200 987 \"-\" \"Mozilla/5.0\"\n";
    $dummy_log .= "192.168.1.1 - - [01/Jan/2023:12:10:00 +0000] \"POST /login.php HTTP/1.1\" 302 0 \"-\" \"Mozilla/5.0\"\n";
    file_put_contents($log_file, $dummy_log);
}

// 输入过滤函数
function validate_filter_input($input) {
    // 禁用的字符和字符串
    $forbidden = [' ', '|', 'cat', 'tac', 'tail', 'more', 'less', 'flag'];
    
    foreach ($forbidden as $forbidden_str) {
        if (strpos($input, $forbidden_str) !== false) {
            return false;
        }
    }
    
    return true;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if ($_POST['action'] === 'filter_logs' && isset($_POST['filter'])) {
        $filter = $_POST['filter'];
        
        // 输入验证：检查是否包含禁用字符
        if (!validate_filter_input($filter)) {
            $error_message = "不可以这样！！";
            $log_content = '';
        } else {
            // 漏洞4: 命令注入漏洞
            if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
                // Windows命令
                $cmd = 'findstr "' . $filter . '" "' . $log_file . '" 2>&1';
            } else {
                // Linux命令
                $cmd = "grep \"" . $filter . "\" \"" . $log_file . "\" 2>&1";
            }
            
            // 执行命令
            $log_content = shell_exec($cmd);
            
            // 调试信息
           
            $debug_info .= "<strong>text:</strong> <pre>" . htmlspecialchars($log_content) . "</pre>";
            $debug_info .= "</div>";
            
            // 如果没有输出，尝试其他方法
            if (empty($log_content)) {
                if (function_exists('exec')) {
                    exec($cmd, $output, $return_var);
                    $log_content = implode("\n", $output);
                    $debug_info .= "<div style='background:#ffffcc; padding:10px; margin:10px 0;'>";
                    $debug_info .= "<strong>尝试exec函数:</strong><br>";
                    $debug_info .= "<strong>返回值:</strong> " . $return_var . "<br>";
                    $debug_info .= "<strong>输出:</strong> <pre>" . htmlspecialchars($log_content) . "</pre>";
                    $debug_info .= "</div>";
                }
            }
        }
    }
} else {
    // 默认显示所有日志
    if (file_exists($log_file)) {
        $log_content = file_get_contents($log_file);
    } else {
        $log_content = "日志文件不存在: " . $log_file;
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>日志 - 安全文档系统</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
        body {
            padding-top: 60px;
        }
        .sidebar {
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            z-index: 100;
            padding: 90px 0 0;
            box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
            background-color: #f8f9fa;
        }
        .sidebar-sticky {
            position: relative;
            top: 0;
            height: calc(100vh - 90px);
            padding-top: .5rem;
            overflow-x: hidden;
            overflow-y: auto;
        }
        .main-content {
            padding: 20px;
        }
        .logs-display {
            font-family: monospace;
            background-color: #000;
            color: #ccc;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            max-height: 500px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">安全文档系统</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto mb-2 mb-md-0">
                    <li class="nav-item">
                        <a class="nav-link" href="dashboard.php">控制面板</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <span class="navbar-text me-3">
                        欢迎, <?php echo htmlspecialchars($_COOKIE['username']); ?> (<?php echo htmlspecialchars($role); ?>)
                    </span>
                    <form method="post" action="index.php">
                        <input type="hidden" name="action" value="logout">
                        <button type="submit" class="btn btn-outline-light">退出</button>
                    </form>
                </div>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <nav id="sidebar" class="col-md-3 col-lg-2 d-md-block sidebar">
                <div class="sidebar-sticky">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="dashboard.php">
                                首页
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="documents.php">
                                文档
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="templates.php">
                                模板编辑器
                            </a>
                        </li>
                        <?php if (is_developer()): ?>
                        <li class="nav-item">
                            <a class="nav-link active" href="logs.php">
                                日志
                            </a>
                        </li>
                        <?php endif; ?>
                        <?php if (is_admin() || is_developer()): ?>
                        <li class="nav-item">
                            <a class="nav-link" href="api.php">
                                API访问
                            </a>
                        </li>
                        <?php endif; ?>
                    </ul>
                </div>
            </nav>

            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">系统日志 <span class="badge bg-warning">仅限开发者</span></h1>
                </div>
                
                <?php if ($error_message): ?>
                <div class="alert alert-danger" role="alert">
                    <?php echo htmlspecialchars($error_message); ?>
                </div>
                <?php endif; ?>
                
                <?php echo $debug_info; ?>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h3 class="h5 mb-0">过滤日志</h3>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            <input type="hidden" name="action" value="filter_logs">
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" placeholder="按关键词过滤日志" name="filter" value="<?php echo htmlspecialchars($filter); ?>">
                                <button class="btn btn-outline-primary" type="submit">过滤</button>
                            </div>
                            <small class="text-muted">不可以这样！！</small>
                        </form>
                    </div>
                </div>
                
                <h3>日志内容 <?php echo $filter ? '(已过滤: ' . htmlspecialchars($filter) . ')' : ''; ?></h3>
                <div class="logs-display">
                    <?php echo htmlspecialchars($log_content ?: '没有找到日志。'); ?>
                </div>
            </main>
        </div>
    </div>
</body>
</html>