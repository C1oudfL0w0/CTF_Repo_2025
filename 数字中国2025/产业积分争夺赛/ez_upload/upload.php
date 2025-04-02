<?php
$targetDirectory = "uploads/"; // 上传文件保存的目录
$timestamp = time();
if(isset($_POST["submit"])) {
    $targetFile = $targetDirectory .$timestamp."-". basename($_FILES["fileToUpload"]["name"]);
    $fileType = strtolower(pathinfo($targetFile,PATHINFO_EXTENSION));

    // 检查文件是否已经存在
    if (file_exists($targetFile)) {
        echo "NONO ALREADY THERE";
        exit();
    }

    // 检查文件大小
    if ($_FILES["fileToUpload"]["size"] > 500000) {
        echo "NONO 2 BIG";
        exit();
    }
    // 允许的文件类型
    if($fileType != "jpg" && $fileType != "png" && $fileType != "jpeg"
        && $fileType != "gif"&& $fileType != "phtml") {
        echo "NOT THIS";
        exit();
    }
    $fileContent = file_get_contents($_FILES["fileToUpload"]["tmp_name"]);
    if ($fileType == "phtml"){
        
        if (strpos($fileContent, 'php') !== false) {
            echo "NOT THIS CONTEHT";
            exit();
        }
    }


    // 检查上传状态
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $targetFile)) {
            echo "文件 ".$targetFile. " 上传成功。";
        } else {
            echo "ERROR";
        }
}
?>




