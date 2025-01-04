<?php
$python_script = 'C:/xampp/htdocs/detec_3.0/deteccion.py';  // Cambiar a la ruta de registro.py
$uploadsDir = 'C:/xampp/htdocs/detec_3.0/htdocs/captures/';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $imageBase64 = $_POST['image'] ?? '';
    $nombre = $_POST['nombre'] ?? '';
    $dni = $_POST['dni'] ?? '';

    if (empty($imageBase64) || empty($nombre) || empty($dni)) {
        echo "Error: Datos incompletos.";
        exit;
    }

    $tempPhotoPath = $uploadsDir . 'temp_photo_' . time() . '.jpg';
    file_put_contents($tempPhotoPath, base64_decode(explode(',', $imageBase64)[1]));

    if (!file_exists($tempPhotoPath)) {
        echo "Error: No se pudo guardar la imagen.";
        exit;
    }

    // Ejecutar el script Python para la verificación y registro
    $output = shell_exec("python $python_script $tempPhotoPath $nombre $dni");
    echo $output;
}
?>

