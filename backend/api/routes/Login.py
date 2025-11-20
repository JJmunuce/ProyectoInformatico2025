# Importa la instancia de la aplicación 'app' desde el módulo 'api'
from api import app

# Importa clases y módulos necesarios desde 'flask', y 'api.models.Usuario'
from flask import request, jsonify
from api.models.usuario import Usuario

# Ruta para manejar el proceso de inicio de sesión (login)
@app.route('/login', methods=['POST'])
def login_post():
    """
    Maneja el proceso de inicio de sesión (login) para un usuario.

    Métodos admitidos:
    - POST: Se espera que se envíen las credenciales de autenticación en el encabezado.

    Parámetros de Solicitud:
    - Las credenciales de autenticación deben incluirse en el encabezado de la solicitud.

    Respuestas:
    - 200 OK: Retorna el resultado del proceso de inicio de sesión en formato JSON.
    - 401 Unauthorized: Si las credenciales son inválidas.
    - 500 Internal Server Error: Si hay un error interno durante el proceso de inicio de sesión.
    """
    try:
        # Obtiene las credenciales de autenticación del encabezado de la solicitud
        auth = request.authorization
        
        # Llama al método 'login' del modelo 'Usuario' (esto debería recibir y usar las credenciales)
        return Usuario.login()
    except Exception as ex:
        # Si hay una excepción, devuelve un mensaje de error como JSON
        return jsonify({'message': str(ex)})