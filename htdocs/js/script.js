// Capturar imagen desde la cámara
document.getElementById("capture-button").addEventListener("click", async () => {
    const video = document.getElementById("video-stream");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const capturedImage = canvas.toDataURL("image/jpeg");

    // Mostrar la imagen capturada en un contenedor de vista previa
    const preview = document.getElementById("preview");
    preview.src = capturedImage;

    // Asignar la imagen capturada al input oculto del formulario
    document.getElementById("foto").value = capturedImage;
});

// Iniciar la cámara
(async () => {
    const video = document.getElementById("video-stream");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.play();
    } catch (error) {
        console.error("Error al iniciar la cámara:", error);
        alert("No se pudo acceder a la cámara. Verifica los permisos del navegador.");
    }
})();

