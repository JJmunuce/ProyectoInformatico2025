from functools import wraps
from flask import request, jsonify
import jwt
from api import app

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"message": "Falta el token"}), 401
        
        try:
            # Decodificamos el token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Pasamos los datos del usuario actual a la función
            current_user = {
                'id_usuario': data.get('id_usuario'),
                'id_negocio': data.get('id_negocio') # Ahora el token trae el negocio
            }
        except Exception as ex:
            return jsonify({"message": "Token inválido o expirado"}), 401

        return func(current_user, *args, **kwargs) # Inyectamos current_user
    return decorated