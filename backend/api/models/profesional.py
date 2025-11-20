from api import mysql

class Profesional:
    def __init__(self, row):
        self._id = row['id_profesional']
        self._nombre = row['nombre']
        self._id_negocio = row['id_negocio']

    def to_json(self):
        return {
            "id_profesional": self._id,
            "nombre": self._nombre,
            "id_negocio": self._id_negocio
        }

    @classmethod
    def get_all(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM profesional")
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO profesional (nombre, id_negocio) VALUES (%s, %s)",
                    (data['nombre'], data['id_negocio']))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Profesional creado exitosamente"}
    