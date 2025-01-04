<?php
$python_script = 'C:/xampp/htdocs/detec_3.0/registro.py';
$uploadsDir = 'C:/xampp/htdocs/detec_3.0/htdocs/registered_faces/';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $fotoBase64 = $_POST['foto'] ?? '';
    $nombre = $_POST['nombre'] ?? '';
    $sexo = $_POST['sexo'] ?? '';
    $edad = $_POST['edad'] ?? '';
    $dni = $_POST['dni'] ?? '';

    // Validación de datos en PHP
    if (empty($fotoBase64) || empty($nombre) || empty($edad) || empty($sexo) || empty($dni)) {
        echo json_encode(['status' => 'error', 'message' => 'Datos incompletos.']);
        exit;
    }

    if (!ctype_digit($edad) || (int)$edad < 18) {
        echo json_encode(['status' => 'error', 'message' => 'La edad debe ser un número mayor o igual a 18.']);
        exit;
    }

    if (!in_array($sexo, ['Masculino', 'Femenino'])) {
        echo json_encode(['status' => 'error', 'message' => 'El sexo debe ser "Masculino" o "Femenino".']);
        exit;
    }

    if (!ctype_digit($dni) || strlen($dni) < 8) {
        echo json_encode(['status' => 'error', 'message' => 'El DNI debe ser numérico y tener al menos 8 dígitos.']);
        exit;
    }

    try {
        // Guardar la imagen como archivo temporal
        $tempPhotoPath = $uploadsDir . 'temp_photo_' . uniqid() . '.jpg';
        $decodedImage = base64_decode(explode(',', $fotoBase64)[1]);

        if (!$decodedImage) {
            echo json_encode(['status' => 'error', 'message' => 'Error al decodificar la imagen.']);
            exit;
        }

        file_put_contents($tempPhotoPath, $decodedImage);

        // Verificar si la persona ya está registrada en la base de datos
        $conn = new mysqli('localhost', 'root', '', 'photo_employees');
        if ($conn->connect_error) {
            echo json_encode(['status' => 'error', 'message' => 'Error al conectar con la base de datos.']);
            exit;
        }

        $stmt = $conn->prepare("SELECT COUNT(*) FROM empleados WHERE dni = ?");
        $stmt->bind_param("s", $dni);
        $stmt->execute();
        $stmt->bind_result($count);
        $stmt->fetch();
        $stmt->close();
        $conn->close();

        if ($count > 0) {
            echo json_encode(['status' => 'error', 'message' => 'El DNI ya está registrado.']);
            exit;
        }

        // Ejecutar el script de Python
        $command = escapeshellcmd("python \"$python_script\" \"$tempPhotoPath\" \"$nombre\" \"$edad\" \"$sexo\" \"$dni\"");
        $output = shell_exec($command . " 2>&1");

        $output = trim($output);

        if (strpos($output, 'Registro exitoso') !== false) {
            echo json_encode(['status' => 'success', 'message' => 'Registro exitoso.']);
        } elseif (strpos($output, 'Error:') !== false) {
            echo json_encode(['status' => 'error', 'message' => $output]);
        } else {
            echo json_encode(['status' => 'error', 'message' => 'Error desconocido en el script de Python.']);
        }

        // Nota: La imagen temporal ya no se elimina automáticamente
    } catch (Exception $e) {
        echo json_encode(['status' => 'error', 'message' => 'Error interno del servidor: ' . $e->getMessage()]);
    }
}
?>

