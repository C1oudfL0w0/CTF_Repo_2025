<?php
// JWT Helper Functions
function base64UrlDecode($data) {
    return base64_decode(strtr($data, '-_', '+/'));
}

function verifyJWT($token, $secret) {
    $parts = explode('.', $token);
    if (count($parts) !== 3) {
        return false;
    }

    list($header, $payload, $signature) = $parts;

    // Verify signature
    $validSignature = rtrim(strtr(base64_encode(hash_hmac('sha256', "$header.$payload", $secret, true)), '+/', '-_'), '=');

    if ($signature !== $validSignature) {
        return false;
    }

    // Decode payload
    $payloadData = json_decode(base64UrlDecode($payload), true);
    return $payloadData;
}

// Check if JWT token exists
if (!isset($_COOKIE['auth_token'])) {
    header('Location: index.php');
    exit();
}

$token = $_COOKIE['auth_token'];

// Try to decode JWT (we need to know the secret!)
// The secret is hidden in the gallery photos: GALLERY2024SECRET
$jwtSecret = 'GALLERY2024SECRET';

$payload = verifyJWT($token, $jwtSecret);

if (!$payload) {
    $error = "Invalid JWT token! Unable to verify signature.";
    $isAdmin = false;
} else {
    $username = $payload['user'] ?? 'Unknown';
    $role = $payload['role'] ?? 'guest';
    $isAdmin = ($role === 'admin');
}

// Handle file export functionality
$fileContent = '';
$exportError = '';
$exportSuccess = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if (!$isAdmin) {
        $exportError = "Access Denied! Only admin users can export files.";
    } else {
        $action = $_POST['action'];

        if ($action === 'export') {
            $filepath = $_POST['filepath'] ?? '';

            if (empty($filepath)) {
                $exportError = "Please specify a file path!";
            } else {
                // Filter dangerous wrappers
                $filepath_lower = strtolower($filepath);
                if (strpos($filepath_lower, 'base64') !== false) {
                    $exportError = "Blocked: base64 filter is not allowed!";
                } elseif (strpos($filepath_lower, 'rot13') !== false) {
                    $exportError = "Blocked: rot13 filter is not allowed!";
                } else {
                    // Vulnerable to path traversal and PHP filter bypass!

                        $fileContent = include($filepath);
                        $exportSuccess = "File exported successfully: " . htmlspecialchars($filepath);
                    
                }
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Secret Photo Gallery</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .admin-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .admin-header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .admin-header h1 {
            color: #667eea;
            margin: 0;
        }
        .admin-panel {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .jwt-info {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            word-break: break-all;
        }
        .file-output {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 500px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .btn-export {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
        }
        .access-denied {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 20px;
            border-radius: 5px;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="admin-container">
        <div class="admin-header">
            <div class="d-flex justify-content-between align-items-center">
                <h1><i class="fas fa-shield-alt"></i> Admin Panel</h1>
                <a href="gallery.php" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Gallery
                </a>
            </div>
        </div>

        <?php if (!$isAdmin): ?>
        <!-- Access Denied -->
        <div class="admin-panel">
            <div class="access-denied">
                <h3><i class="fas fa-exclamation-triangle"></i> Access Denied!</h3>
                <p><strong>You need admin privileges to access this panel.</strong></p>
                <p>Current user: <code><?php echo htmlspecialchars($username ?? 'Unknown'); ?></code></p>
                <p>Current role: <code><?php echo htmlspecialchars($role ?? 'guest'); ?></code></p>
            </div>

            <div class="jwt-info mt-4">
                <strong��>���ｽ�� ��Your JWT Token:</strong><br>
                <?php echo htmlspecialchars($token); ?>
            </div>
        </div>

        <?php else: ?>
        <!-- Admin Access Granted -->
        <div class="admin-panel">
            <div class="alert alert-success">
                <h4><i class="fas fa-check-circle"></i> Admin Access Granted!</h4>
                <p class="mb-0">Welcome, <strong><?php echo htmlspecialchars($username); ?></strong>! You have successfully forged the JWT token.</p>
            </div>

            <div class="jwt-info">
                <strong��>���ｽ� Verified JWT Token:</strong><br>
                <?php echo htmlspecialchars($token); ?><br><br>
                <strong>Decoded Payload:</strong><br>
                <?php echo htmlspecialchars(json_encode($payload, JSON_PRETTY_PRINT)); ?>
            </div>

            <hr>

            <h3><i class="fas fa-file-export"></i> File Export Tool</h3>
            <p class="text-muted">Export system files for backup purposes</p>

            <form method="POST" action="">
                <input type="hidden" name="action" value="export">
                <div class="mb-3">
                    <label class="form-label"><strong>File Path:</strong></label>
                    <input type="text" class="form-control" name="filepath"
                           placeholder="e.g., /etc/passwd, /flag.txt, /var/www/html/index.php"
                           value="<?php echo htmlspecialchars($_POST['filepath'] ?? ''); ?>" required>
                    <small class="text-muted">Enter the absolute path of the file you want to export</small>
                </div>
                <button type="submit" class="btn-export">
                    <i class="fas fa-download"></i> Export File
                </button>
            </form>

            <?php if ($exportError): ?>
            <div class="alert alert-danger mt-3">
                <i class="fas fa-exclamation-circle"></i> <?php echo $exportError; ?>
            </div>
            <?php endif; ?>

            <?php if ($exportSuccess): ?>
            <div class="alert alert-success mt-3">
                <i class="fas fa-check-circle"></i> <?php echo $exportSuccess; ?>
            </div>
            <?php endif; ?>

            <?php if ($fileContent): ?>
            <div class="file-output">
                <strong��>���ｽ�� ��File Content:</strong><br><br><?php echo htmlspecialchars($fileContent); ?>
            </div>
            <?php endif; ?>
        </div>
        <?php endif; ?>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>