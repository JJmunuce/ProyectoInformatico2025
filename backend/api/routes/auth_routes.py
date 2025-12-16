from api import app, mysql
from flask import jsonify, request
from api.models.usuario import Usuario
from werkzeug.security import check_password_hash
import jwt
import datetime
import traceback

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    username = data.get('username')
    password = str(data.get('password'))

    if not username or not password:
        return jsonify({"message": "Credenciales incompletas"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if not user_data:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

        # Verificar contraseña
        pwd_hash = user_data.get('contraseña')
        if isinstance(pwd_hash, bytes): pwd_hash = pwd_hash.decode('utf-8')
        
        if check_password_hash(pwd_hash, password):
            # GENERAR TOKEN CON ID_NEGOCIO
            token_payload = {
                'id_usuario': user_data['id_usuario'],
                'id_negocio': user_data['id_negocio'], # <--- CLAVE PARA SEGURIDAD
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) # 24hs
            }
            
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            if isinstance(token, bytes): token = token.decode('utf-8')

            resp = Usuario(user_data).to_json()
            resp['token'] = token
            return jsonify(resp), 200
            
        return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

    except Exception as ex:
        print(ex)
        return jsonify({'message': 'Error de servidor'}), 500