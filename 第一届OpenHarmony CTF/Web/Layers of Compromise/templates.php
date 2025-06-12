<?php
require_once 'config.php';
require_once 'auth.php';

if (!check_auth()) {
    header('Location: index.php');
    exit;
}

$role = get_role();
$message = '';
$preview = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if ($_POST['action'] === 'preview' && isset($_POST['template_name']) && isset($_POST['template_content'])) {
        $template_name = $_POST['template_name'];
        $template_content = $_POST['template_content'];
        
        $data = [
            'title' => isset($_POST['title']) ? $_POST['title'] : '默认标题',
            'content' => isset($_POST['content']) ? $_POST['content'] : '默认内容',
            'author' => isset($_POST['author']) ? $_POST['author'] : $_COOKIE['username']
        ];
        
        try {
            ob_start();
            
            $content = $data['content'];
            
            $allowed_patterns = [
                'cat secrettttts/token.txt',
                'cat /data/app/www/secrettttts/token.txt',
                'file_get_contents("secrettttts/token.txt")',
                'file_get_contents("/data/app/www/secrettttts/token.txt")'
            ];
            
            $is_allowed = false;
            foreach ($allowed_patterns as $pattern) {
                if (strpos($content, $pattern) !== false) {
                    $is_allowed = true;
                    break;
                }
            }
            
            $blocked_functions = [
                'system', 'exec', 'passthru', 'proc_open', 'popen',
                'shell_exec', 'eval', 'file_get_contents', 'readfile',
                'fopen', 'fread', 'include', 'require', 'curl_exec',
                'mail', 'fsockopen', 'socket_create', 'mysqli_',
                'mysql_', 'pg_', 'sqlite_', 'ldap_', 'ssh2_',
                '`', 'escapeshellcmd', 'escapeshellarg', 'proc_close',
                'proc_get_status', 'proc_nice', 'proc_terminate'
            ];
            
            $dangerous_chars = ['$', '`', ';', '|', '&', '>', '<', '*', '?', '[', ']', '{', '}'];
            $has_dangerous_content = false;
            
            $content_lower = strtolower($content);
            foreach ($blocked_functions as $func) {
                if (strpos($content_lower, $func) !== false) {
                    $has_dangerous_content = true;
                    break;
                }
            }
            
            if (!$has_dangerous_content && !$is_allowed) {
                foreach ($dangerous_chars as $char) {
                    if (strpos($content, $char) !== false) {
                        $has_dangerous_content = true;
                        break;
                    }
                }
            }
            
            if ($is_allowed && !$has_dangerous_content) {
                if (strpos($content, 'cat secrettttts/token.txt') !== false || 
                    strpos($content, 'cat /data/app/www/secrettttts/token.txt') !== false) {
                    $token_content = @file_get_contents('/data/app/www/secrettttts/token.txt');
                    if ($token_content !== false) {
                        echo $token_content;
                        echo "\n\n提示：使用此开发令牌可以获得更高权限访问。查看内部文档了解如何使用开发者认证机制。";
                    } else {
                        echo "无法读取token文件";
                    }
                } else if (strpos($content, 'file_get_contents') !== false && strpos($content, 'token.txt') !== false) {
                    $token_content = @file_get_contents('/data/app/www/secrettttts/token.txt');
                    if ($token_content !== false) {
                        echo $token_content;
                        echo "\n\n提示：使用此开发令牌可以获得更高权限访问。查看内部文档了解如何使用开发者认证机制。";
                    } else {
                        echo "无法读取token文件";
                    }
                }
            } else if ($has_dangerous_content) {
                echo "检测到危险内容，模板被阻止执行。";
            } else {
                $safe_content = htmlspecialchars($content, ENT_QUOTES, 'UTF-8');
                echo $safe_content;
            }
            
            $preview = ob_get_clean();
            $message = '模板预览生成成功。';
        } catch (Exception $e) {
            $preview = '';
            $message = '模板错误: ' . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>模板编辑器 - 安全文档系统</title>
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
        .template-editor, .template-preview {
            margin-bottom: 20px;
        }
        .template-preview {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
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
                            <a class="nav-link active" href="templates.php">
                                模板编辑器
                            </a>
                        </li>
                        <?php if (is_developer()): ?>
                        <li class="nav-item">
                            <a class="nav-link" href="logs.php">
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
                    <h1 class="h2">模板编辑器</h1>
                </div>
                
                <?php if ($message): ?>
                    <div class="alert alert-info"><?php echo htmlspecialchars($message); ?></div>
                <?php endif; ?>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="template-editor">
                            <h3>创建模板</h3>
                            <form method="post">
                                <input type="hidden" name="action" value="preview">
                                <div class="mb-3">
                                    <label for="template_name" class="form-label">模板名称:</label>
                                    <input type="text" class="form-control" id="template_name" name="template_name" required>
                                </div>
                                <div class="mb-3">
                                    <label for="template_content" class="form-label">模板结构:</label>
                                    <textarea class="form-control" id="template_content" name="template_content" rows="3" placeholder="输入模板结构">默认模板结构</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="title" class="form-label">标题:</label>
                                    <input type="text" class="form-control" id="title" name="title" value="模板标题">
                                </div>
                                <div class="mb-3">
                                    <label for="content" class="form-label">内容:</label>
                                    <textarea class="form-control" id="content" name="content" rows="5" placeholder="输入模板内容">你好，欢迎使用模板系统！</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="author" class="form-label">作者:</label>
                                    <input type="text" class="form-control" id="author" name="author" value="<?php echo htmlspecialchars($_COOKIE['username']); ?>">
                                </div>
                                <button type="submit" class="btn btn-primary">预览模板</button>
                            </form>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h3>模板预览</h3>
                        <?php if ($preview): ?>
                            <div class="template-preview">
                                <?php echo $preview; ?>
                            </div>
                        <?php else: ?>
                            <div class="alert alert-info">
                                填写表单并点击预览以查看模板。
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </main>
        </div>
    </div>
</body>
</html>