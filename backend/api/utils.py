from functools import wraps
from flask import request, jsonify
import jwt
from api import app

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        # Buscar token en headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"message": "Falta el token"}), 401
        
        try:
            # Decodificar token usando la clave secreta de app config
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
          
        except Exception as ex:
            return jsonify({"message": "Token inválido o expirado"}), 401

        return func(*args, **kwargs)
    return decorated

