from api import mysql

class Usuario:
    def __init__(self, row):
        self._id = row['id_usuario']
        self._nombre = row['nombre']
        self._correo = row['correo']
        self._id_negocio = row['id_negocio']

    def to_json(self):
        return {
            "id_usuario": self._id,
            "nombre": self._nombre,
            "correo": self._correo,
            "id_negocio": self._id_negocio
        }

    @classmethod
    def get_all(cls, id_negocio): # <--- Recibe id_negocio
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id_negocio = %s", (id_negocio,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre, correo, contraseña, id_negocio) VALUES (%s, %s, %s, %s)",
                    (data['nombre'], data['correo'], data['contraseña'], data['id_negocio']))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Usuario registrado exitosamente"}