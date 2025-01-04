document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");
    const startCameraButton = document.getElementById("start-camera");
    const capturePhotoButton = document.getElementById("capture-photo");
    const videoElement = document.getElementById("video");
    const fotoInput = document.getElementById("foto");
    const resultMessage = document.getElementById("resultMessage");

    let stream;

    // Iniciar cámara
    startCameraButton.addEventListener("click", async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = stream;
            startCameraButton.style.display = "none";
            capturePhotoButton.style.display = "inline-block";
        } catch (error) {
            alert("Error al iniciar la cámara. Verifique los permisos.");
        }
    });

    // Capturar foto
    capturePhotoButton.addEventListener("click", () => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        // Convertir la foto a Base64 y almacenarla en un campo oculto
        const photoData = canvas.toDataURL("image/jpeg");
        fotoInput.value = photoData;

        alert("Foto capturada correctamente.");
    });

    // Manejar el envío del formulario
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        resultMessage.textContent = "Procesando registro...";

        const formData = new FormData(form);

        try {
            const response = await fetch("save_registration.php", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Error en la comunicación con el servidor.");
            }

            const result = await response.json();
            if (result.status === "success") {
                resultMessage.textContent = "Registro exitoso.";
            } else {
                resultMessage.textContent = `Error: ${result.message}`;
            }
        } catch (error) {
            console.error("Error en el servidor:", error);
            resultMessage.textContent = "Error en el servidor.";
        }
    });
});

