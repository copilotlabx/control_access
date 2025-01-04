import cv2
import numpy as np
import hashlib
import os
import sys
import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "photo_employees"
}

# Ruta del clasificador Haar
HAAR_PATH = 'C:/xampp/htdocs/detec_3.0/htdocs/cascade/haarcascade_frontalface_default.xml'

def calculate_hash(face_image):
    # Redimensiona la imagen a un tamaño estándar
    resized_face = cv2.resize(face_image, (100, 100))
    # Convierte a escala de grises
    gray_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2GRAY)
    # Codifica la imagen a formato JPG
    _, buffer = cv2.imencode('.jpg', gray_face)
    return hashlib.sha256(buffer).hexdigest()

def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        return None

def is_hash_in_db(face_hash):
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        query = "SELECT nombre, dni FROM empleados WHERE foto_hash = %s"
        cursor.execute(query, (face_hash,))
        return cursor.fetchone()
    finally:
        conn.close()

def detect_face(image_path):
    if not os.path.exists(HAAR_PATH):
        return "Error: Archivo Haarcascade no encontrado."

    face_cascade = cv2.CascadeClassifier(HAAR_PATH)
    if face_cascade.empty():
        return "Error: No se pudo cargar el clasificador Haarcascade."

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    if len(faces) == 0:
        return "Error: No se detectó ningún rostro."

    # Extraemos el rostro de la imagen
    x, y, w, h = faces[0]
    face_image = image[y:y+h, x:x+w]
    # Calculamos el hash de la imagen del rostro
    face_hash = calculate_hash(face_image)

    # Verificamos si el hash del rostro existe en la base de datos
    user = is_hash_in_db(face_hash)
    if user:
        return f"Acceso permitido: {user[0]}, DNI: {user[1]}"
    else:
        return "Error: Rostro no registrado."

if __name__ == "__main__":
    image_path = sys.argv[1]
    print(detect_face(image_path))

