from werkzeug.security import generate_password_hash

class Usuario():
    """
    Clase que representa a un usuario.
    """

    def __init__(self, data):
        self._id_usuario = data['id_usuario']
        self._nombre = data['nombre']
        self._correo = data['correo']
        self._id_negocio = data.get('id_negocio')

    def to_json(self):
        return {
            'id_usuario': self._id_usuario,
            'nombre': self._nombre,
            'correo': self._correo,
            'id_negocio': self._id_negocio
        }
    
    
    @classmethod
    def create(cls, data):
        from api import app, mysql
        """
        Método para registrar un nuevo usuario (Usado por usuario_routes.py)
        """
        pwd_hash = generate_password_hash(data['contraseña'])
        cur = mysql.connection.cursor()
        
        # Nota: Si id_negocio es None (cliente), MySQL lo aceptará si la columna permite NULL
        cur.execute("INSERT INTO usuario (nombre, correo, contraseña, id_negocio) VALUES (%s, %s, %s, %s)",
                    (data['nombre'], data['correo'], pwd_hash, data.get('id_negocio')))
        
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Usuario registrado"}
