from functools import wraps
from flask import request, jsonify
import jwt
from api import app
from api.db.db import mysql

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"message": "Falta el token"}), 401
        
        id_usuario = None

        if 'user-id' in request.headers:
            id_usuario = request.headers['user-id']

        if not id_usuario:
            return jsonify({"message": "Falta el usuario"}), 401
        
        try:
            data = jwt.decode(token , app.config['SECRET_KEY'], algorithms = ['HS256'])
            token_id = data['id_usuario']

            if int(id_usuario) != int(token_id):
                 return jsonify({"message": "Error de id"}), 401
            
        except Exception as ex:
            return jsonify({"message": "No tiene permisos para acceder a esta ruta"}), 401

        return func(*args, **kwargs)
    return decorated

def client_resource(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        id_cliente = kwargs['id_cliente']
        cur = mysql.connection.cursor()
        cur.callproc('sp_obtenerId_UsuarioById_Cliente', [id_cliente]) 
        data = cur.fetchone()
        cur.close()
        
        if data:
            id_prop = data[0]
            user_id = request.headers['user-id']
            if int(id_prop) != int(user_id):
                return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated

def user_resources(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        id_user_route = kwargs['id_usuario']
        user_id = request.headers['user-id']
        if int(id_user_route) != int(user_id):
            return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated