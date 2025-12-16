from api import app, mysql
from flask import jsonify, request
from api.models.usuario import Usuario
from werkzeug.security import check_password_hash
import jwt
import datetime
import traceback

@app.route('/login', methods=['POST'])
def login():
    # 1. Obtener datos de forma segura
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Faltan datos en la solicitud"}), 400

    # 2. Aceptar variantes de nombres de campo
    username = data.get('username') or data.get('email') or data.get('correo')
    password = str(data.get('password') or data.get('contraseña'))

    if not username or not password or password == 'None':
        return jsonify({"message": "Falta usuario/correo o contraseña"}), 400

    try:
        cur = mysql.connection.cursor()
        # Buscamos por correo
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if not user_data:
            return jsonify({"message": "Usuario no encontrado"}), 401

        # 3. Validar Hash
        # Convertimos de bytes a string si es necesario para compatibilidad
        stored_hash = user_data.get('contraseña')
        if isinstance(stored_hash, bytes):
            stored_hash = stored_hash.decode('utf-8')
        
        # Aquí ocurre la magia: Compara el texto plano (password) con el hash guardado
        if check_password_hash(stored_hash, password):
            
            id_negocio = user_data.get('id_negocio')
            
            # Generamos el Token
            token_payload = {
                'id_usuario': user_data['id_usuario'],
                'id_negocio': id_negocio, 
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)
            }
            
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            if isinstance(token, bytes): token = token.decode('utf-8')

            resp = Usuario(user_data).to_json()
            resp['token'] = token
            # Bandera para saber si redirigir a "Crear Negocio"
            resp['sin_negocio'] = (id_negocio is None)

            return jsonify(resp), 200
            
        return jsonify({"message": "Contraseña incorrecta"}), 401

    except Exception as ex:
        print("ERROR LOGIN:", ex)
        traceback.print_exc()
        return jsonify({'message': 'Error interno del servidor', 'error': str(ex)}), 500