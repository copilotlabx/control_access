import sys
import os
import hashlib
import mysql.connector
import logging
import shutil
from datetime import datetime
import uuid
import json

# Configuración de logs
logging.basicConfig(
    filename="registro.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Conexión a la base de datos
def connect_db():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='photo_employees'
        )
    except mysql.connector.Error as err:
        logging.error(f"Error al conectar a la base de datos: {err}")
        print(json.dumps({"error": f"No se pudo conectar a la base de datos: {err}"}))
        sys.exit(1)

# Calcular el hash de una imagen
def calculate_image_hash(image_path):
    try:
        with open(image_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logging.error(f"Error al calcular el hash de la imagen: {e}")
        print(json.dumps({"error": f"Error al procesar la imagen: {e}"}))
        sys.exit(1)

# Validaciones
def validar_edad(edad_str):
    try:
        edad = int(edad_str)
        if edad < 18:
            raise ValueError(f"La edad debe ser mayor o igual a 18. Recibido: {edad}")
        return edad
    except ValueError:
        logging.error(f"Validación de edad fallida: valor no numérico o menor a 18 ({edad_str})")
        print(json.dumps({"error": "La edad debe ser un número válido mayor o igual a 18."}))
        sys.exit(1)

def validar_sexo(sexo):
    if sexo not in ["Masculino", "Femenino"]:
        logging.error(f"Validación de sexo fallida: valor inválido ({sexo})")
        print(json.dumps({"error": "Sexo no válido. Debe ser 'Masculino' o 'Femenino'."}))
        sys.exit(1)
    return sexo

def validar_dni(dni):
    if not dni.isdigit() or len(dni) < 8:
        logging.error(f"Validación de DNI fallida: valor inválido ({dni})")
        print(json.dumps({"error": "DNI no válido. Debe ser numérico y contener al menos 8 dígitos."}))
        sys.exit(1)
    return dni

# Verificar si el registro ya existe por DNI
def verificar_registro_existente(conn, dni):
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM empleados WHERE dni = %s"
    cursor.execute(query, (dni,))
    return cursor.fetchone()[0] > 0

# Verificar si el hash de la foto ya existe
def verificar_foto_existente(conn, foto_hash):
    cursor = conn.cursor()
    query = "SELECT nombre, dni FROM empleados WHERE foto_hash = %s"
    cursor.execute(query, (foto_hash,))
    return cursor.fetchone()

# Guardar el registro en la base de datos
def save_registration(conn, nombre, edad, sexo, dni, foto_hash, foto_ruta):
    cursor = conn.cursor()
    query = """
        INSERT INTO empleados (nombre, edad, sexo, dni, foto_hash, foto_ruta, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    try:
        cursor.execute(query, (nombre, edad, sexo, dni, foto_hash, foto_ruta))
        conn.commit()
    except mysql.connector.Error as e:
        logging.error(f"Error al guardar el registro: {e}")
        print(json.dumps({"error": f"Error al guardar el registro: {e}"}))
        sys.exit(1)

# Manejo de argumentos seguros
def parse_arguments(args):
    if len(args) < 6:
        print(json.dumps({"error": "Parámetros insuficientes."}))
        sys.exit(1)
    photo_path = args[1]
    nombre = " ".join(args[2:-3])  # Tomar todos los argumentos entre la foto y los últimos tres
    edad = args[-3]
    sexo = args[-2]
    dni = args[-1]
    return photo_path, nombre, edad, sexo, dni

# Main
if __name__ == "__main__":
    try:
        photo_path, nombre, edad, sexo, dni = parse_arguments(sys.argv)
        logging.info(f"Datos recibidos: Nombre: {nombre}, Edad: {edad}, Sexo: {sexo}, DNI: {dni}")

        conn = connect_db()

        # Validaciones
        edad = validar_edad(edad)
        sexo = validar_sexo(sexo)
        dni = validar_dni(dni)

        if not os.path.exists(photo_path):
            print(json.dumps({"error": "No se encontró la imagen."}))
            sys.exit(1)

        # Procesamiento de la imagen
        foto_hash = calculate_image_hash(photo_path)
        if verificar_registro_existente(conn, dni):
            print(json.dumps({"error": "El DNI ya está registrado."}))
            sys.exit(1)

        foto_existente = verificar_foto_existente(conn, foto_hash)
        if foto_existente:
            print(json.dumps({
                "error": f"El rostro ya está registrado como {foto_existente[0]} con DNI {foto_existente[1]}."
            }))
            sys.exit(1)

        final_photo_path = os.path.join(
            "C:/xampp/htdocs/detec_3.0/htdocs/registered_faces",
            f"{dni}_{uuid.uuid4()}.jpg"
        )
        shutil.move(photo_path, final_photo_path)

        # Guardar en la base de datos
        save_registration(conn, nombre, edad, sexo, dni, foto_hash, final_photo_path)
        print(json.dumps({"success": "Registro exitoso."}))

    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        print(json.dumps({"error": f"Error inesperado: {e}"}))
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

