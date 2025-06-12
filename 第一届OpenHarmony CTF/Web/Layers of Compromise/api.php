<?php
require_once 'config.php';
require_once 'auth.php';

if (!check_auth() || (!is_admin() && !is_developer())) {
    header('Location: index.php');
    exit;
}

$role = get_role();
$result = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if ($_POST['action'] === 'api_call' && isset($_POST['endpoint']) && isset($_POST['api_token'])) {
        $endpoint = $_POST['endpoint'];
        $api_token = $_POST['api_token'];
        
        if ($api_token === $CONFIG['api_secret']) {
            switch ($endpoint) {
                case 'status':
                    $result = json_encode(['status' => 'ok', 'server' => 'Apache/2.4.52', 'php' => PHP_VERSION]);
                    break;
                case 'config':
                    $result = json_encode(['debug_mode' => false, 'max_upload' => '2M', 'log_path' => '/var/log/apache2/access.log']);
                    break;
                case 'debug':
                    // 仅允许本地访问debug端点
                    if ($_SERVER['REMOTE_ADDR'] === '127.0.0.1' || $_SERVER['REMOTE_ADDR'] === '::1') {
                        if ($api_token === $CONFIG['debug_token'] || is_developer()) {
                            $result = json_encode(['debug' => true, 'secret_files' => ['/var/www/secrets/token.txt', '/flag']]);
                        } else {
                            $error = '无效的debug令牌。此端点需要特殊权限。';
                        }
                    } else {
                        $error = 'Debug端点仅限本地访问 (127.0.0.1)。';
                    }
                    break;
                default:
                    $error = '未知端点: ' . htmlspecialchars($endpoint);
            }
        } else {
            $error = '无效的API令牌。';
        }
    } elseif ($_POST['action'] === 'import_xml' && isset($_FILES['xml_file']) && $_FILES['xml_file']['error'] === UPLOAD_ERR_OK) {
        
        //$xml_content = file_get_contents($_FILES['xml_file']['tmp_name']);
        
        //$old_value = libxml_disable_entity_loader(false); // 漏洞 - 允许XXE
        
        try {
            $dom = new DOMDocument();
            $dom->loadXML($xml_content, LIBXML_NOENT | LIBXML_DTDLOAD);
            
            $document = simplexml_import_dom($dom);
            if ($document) {
                $result = "XML导入成功: <br>";
                $result .= "标题: " . htmlspecialchars($document->title) . "<br>";
                $result .= "内容: " . htmlspecialchars($document->content);
            } else {
                $error = '无法解析XML文档。';
            }
        } catch (Exception $e) {
            $error = 'XML解析错误: ' . $e->getMessage();
        }
        
        libxml_disable_entity_loader($old_value);
    }
}
?>