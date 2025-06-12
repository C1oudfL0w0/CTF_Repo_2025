<?php
require_once 'config.php';
require_once 'auth.php';

if (!check_auth()) {
    header('Location: index.php');
    exit;
}

$username = $_COOKIE['username'];
$role = get_role();
?>
<!DOCTYPE html>
<html>
<head>
    <title>控制面板 - 安全文档系统</title>
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
            position:relative;
            top: 0;
            height: calc(100vh - 90px);
            padding-top: .5rem;
            overflow-x: hidden;
            overflow-y: auto;
        }
        .main-content {
            padding: 20px;
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
                        <a class="nav-link active" href="dashboard.php">控制面板</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <span class="navbar-text me-3">
                        欢迎, <?php echo htmlspecialchars($username); ?> (<?php echo htmlspecialchars($role); ?>)
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
                            <a class="nav-link active" href="dashboard.php">
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
                            <a class="nav-link" href="logs.php">
                                日志 <span class="badge bg-warning">DEV</span>
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
                    <h1 class="h2">控制面板</h1>
                </div>
                <div class="alert alert-success">
                    欢迎使用安全文档系统。使用导航菜单访问不同功能。
                </div>
                
                <?php if ($role === 'admin'): ?>
                <div class="alert alert-info">
                    <strong>管理员权限:</strong> 您可以访问机密文档和API功能。
                </div>
                <?php elseif ($role === 'developer'): ?>
                <div class="alert alert-warning">
                    <strong>开发者权限:</strong> 您拥有完整的系统访问权限，包括日志查看功能。
                </div>
                <?php else: ?>
                <div class="alert alert-secondary">
                    <strong>普通用户:</strong> 您可以使用基本的文档和模板功能。
                </div>
                <?php endif; ?>
            </main>
        </div>
    </div>
</body>
</html>