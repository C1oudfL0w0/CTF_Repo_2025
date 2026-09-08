<?php
// JWT Helper Functions
function base64UrlEncode($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function createJWT($payload, $secret) {
    $header = json_encode(['typ' => 'JWT', 'alg' => 'HS256']);
    $header = base64UrlEncode($header);
    $payload = base64UrlEncode(json_encode($payload));
    $signature = base64UrlEncode(hash_hmac('sha256', "$header.$payload", $secret, true));
    return "$header.$payload.$signature";
}

// If already logged in, redirect to gallery
if (isset($_COOKIE['auth_token'])) {
    header('Location: gallery.php');
    exit();
}

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    // Initialize database
    $db = new SQLite3('/tmp/gallery.db');

    // Create users table (empty database)
    $db->exec('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)');

    // Vulnerable SQL query - direct string concatenation
    $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";

    $result = $db->query($query);

    if ($result && $row = $result->fetchArray()) {
        // Generate JWT token with weak secret
        // The secret will be hidden in the gallery photos!
        $jwtSecret = 'GALLERY2024SECRET';

        $payload = [
            'user' => $username,
            'role' => 'guest',
            'iat' => time()
        ];

        $token = createJWT($payload, $jwtSecret);

        // Set JWT as cookie
        setcookie('auth_token', $token, time() + 3600, '/', '', false, true);

        // Also keep session for compatibility
        $_SESSION['logged_in'] = true;
        $_SESSION['username'] = $username;

        header('Location: gallery.php');
        exit();
    } else {
        $error = 'Invalid username or password!';
    }

    $db->close();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Photo Gallery - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 450px;
            width: 100%;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo i {
            font-size: 60px;
            color: #667eea;
        }
        .logo h1 {
            color: #333;
            margin-top: 15px;
            font-weight: bold;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .form-control {
            border-radius: 10px;
            padding: 12px;
            border: 2px solid #e0e0e0;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-weight: bold;
            width: 100%;
            color: white;
            transition: transform 0.2s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .alert {
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <i class="fas fa-camera-retro"></i>
            <h1>Secret Photo Gallery</h1>
            <p��>���ｽ�� ��Discover the hidden treasure in our mysterious gallery</p>
        </div>
        
        <?php if ($error): ?>
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-circle"></i> <?php echo htmlspecialchars($error); ?>
        </div>
        <?php endif; ?>
        
        <form method="POST" action="">
            <div class="mb-3">
                <label class="form-label"><i class="fas fa-user"></i> Username</label>
                <input type="text" class="form-control" name="username" placeholder="Enter username" required>
            </div>
            <div class="mb-3">
                <label class="form-label"><i class="fas fa-lock"></i> Password</label>
                <input type="password" class="form-control" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit" class="btn btn-login">
                <i class="fas fa-sign-in-alt"></i> Login
            </button>
        </form>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>