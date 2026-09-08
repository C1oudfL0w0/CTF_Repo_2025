<?php
class test
{
    public function __construct()
    {
        if (isset($_FILES['file']) && $_FILES['file']['error'] == 0) {
            $time = date('Hi');
            $filename = $GLOBALS['filename'];
            $seed = $time . intval($filename);
            mt_srand($seed);
            $uploadDir = 'uploads/';
            $files = glob($uploadDir . '*');
            foreach ($files as $file) {
                if (is_file($file)) unlink($file);
            }
            $randomStr = generateRandomString(8);
            $newFilename = $time . '.' . $randomStr . '.' . 'jpg';
            $GLOBALS['file'] = $newFilename;
            $uploadedFile = $_FILES['file']['tmp_name'];
            $uploadPath = $uploadDir . $newFilename;
            if (system("cp " . $uploadedFile . " " . $uploadPath)) {
                echo "success upload!";
            } else {
                echo "error";
            }
        }
    }
    public function __wakeup()
    {
        phpinfo();
    }
    public function readflag()
    {
        function readflag()
        {
            if (isset($GLOBALS['file'])) {
                $file = $GLOBALS['file'];
                $file = basename($file);
                if (preg_match('/:\/\//', $file)) die("error");
                $file_content = file_get_contents("uploads/" . $file);
                if (preg_match('/<\?|\:\/\/|ph|\?\=/i', $file_content)) {
                    die("Illegal content detected in the file.");
                }
                include("uploads/" . $file);
            }
        }
    }
}
unserialize($_GET['land']);