from api import app
from flask import request, jsonify
from api.db.db import mysql
import jwt
import datetime
from werkzeug.security import check_password_hash


class Usuario():
    """
    Clase que representa a un usuario y contiene métodos relacionados con la autenticación.
    """

    def __init__(self, data):
        """
        Constructor de la clase Usuario.

        Parameters:
            data (tuple): Datos del usuario.
        """
        self._id_usuario = data[0]
        self._nombre = data[1]
        self._correo = data[2]
        self._id_negocio = data[3]

    def to_json(self):
        """
        Convierte el usuario a un objeto JSON.

        Returns:
            dict: Usuario en formato JSON.
        """
        return {
            'id_usuario': self._id_usuario,
            'nombre': self._nombre,
            'correo': self._correo            
        }
    
    @staticmethod
    def login():
        """
        Método estático para la autenticación de usuarios.

        Returns:
            tuple: Respuesta JSON y código de estado HTTP.
        """
        try:
            # Recibo el request del front
            auth = request.authorization
            
            if not auth.username and not auth.password:
                return jsonify({"message": "El campo Usuario y Contraseña no pueden estar vacíos"}), 401
            else:
                if not auth.username:
                    return jsonify({"message": "El campo Usuario no puede estar vacío"}), 401
                else:
                    if not auth.password:
                        return jsonify({"message": "El campo Contraseña no puede estar vacío"}), 401
            
            # Control: ¿existen valores para la autenticación?
            if not auth or not auth.username or not auth.password:
                return jsonify({"message": "No autorizado"}), 401       
                    
            # Control: ¿existe el usuario en la BD?
            cur = mysql.connection.cursor()
            cur.callproc('sp_obtenerPWDByUsuario', (auth.username,))
            data = cur.fetchone()
            cur.close()
            
            if data is None:
                return jsonify({"message": "El usuario es incorrecto o no se ha registrado en el sistema"}), 401

            # Obtengo la contraseña encriptada de la BD y la comparo con la contraseña ingresada por el usuario
            pwd_encriptada = data[0]
            if check_password_hash(pwd_encriptada, auth.password):
                cur = mysql.connection.cursor()
                cur.callproc('sp_loginUsuario', (auth.username, pwd_encriptada))
                data = cur.fetchone()
                cur.close()
            else:
                return jsonify({"message":"La contraseña ingresada es incorrecta"}), 401
            
            # En este paso verifico que el usuario esté vigente, es decir, no haya sido eliminado
            usuario = Usuario(data)
            if usuario._id_tipoEstado == 2:
                return jsonify({"message": "El usuario se encuentra desactivado. Consulte al administrador"}), 402
            
            # El usuario existe en la BD y coincide su contraseña
            token = jwt.encode({'id_usuario': usuario._id_usuario,
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=100)}, app.config['SECRET_KEY'])

            usuario_json = usuario.to_json()
            usuario_json['token'] =  token

            return jsonify(usuario_json)
        
        except Exception as ex:
            return {'message': str(ex)}, 401