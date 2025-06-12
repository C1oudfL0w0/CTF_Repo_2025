<?php
require_once 'config.php';
require_once 'auth.php';

if (!check_auth()) {
    header('Location: index.php');
    exit;
}

$role = get_role();
$selected_doc = isset($_GET['doc']) ? $_GET['doc'] : '';
$doc_content = '';

if ($selected_doc && isset($DOCUMENTS[$selected_doc])) {
    // 访问控制检查
    if ($DOCUMENTS[$selected_doc]['access'] === 'admin' && !is_admin() && !is_developer()) {
        $doc_content = "访问拒绝：您需要管理员权限才能查看此文档。";
    } else {
        $doc_content = $DOCUMENTS[$selected_doc]['content'];
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>文档 - 安全文档系统</title>
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
        .document-list {
            margin-bottom: 20px;
        }
        .document-content {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
            white-space: pre-wrap;
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
                            <a class="nav-link active" href="documents.php">
                                文档
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="templates.php">
                                模板编辑器
                            </a>
                        </li>
                        <?php if (is_admin() || is_developer()): ?>
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
                    <h1 class="h2">文档</h1>
                </div>
                
                <div class="row">
                    <div class="col-md-4">
                        <div class="document-list">
                            <div class="list-group">
                                <?php foreach ($DOCUMENTS as $doc_name => $doc_data): ?>
                                    <a href="?doc=<?php echo urlencode($doc_name); ?>" class="list-group-item list-group-item-action <?php echo ($selected_doc === $doc_name) ? 'active' : ''; ?>">
                                        <?php echo htmlspecialchars($doc_name); ?>
                                        <?php if ($doc_data['access'] === 'admin'): ?>
                                            <span class="badge bg-danger float-end">仅限管理员</span>
                                        <?php endif; ?>
                                    </a>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <?php if ($selected_doc): ?>
                            <h3><?php echo htmlspecialchars($selected_doc); ?></h3>
                            <div class="document-content">
                                <?php echo nl2br(htmlspecialchars($doc_content)); ?>
                            </div>
                        <?php else: ?>
                            <div class="alert alert-info">
                                从列表中选择一个文档以查看其内容。
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            </main>
        </div>
    </div>
</body>
</html>