from api import mysql

class Negocio:
    def __init__(self, row):
        self._id = row['id_negocio']
        self._nombre = row['nombre']
        self._direccion = row['direccion']
        self._telefono = row['telefono']

    def to_json(self):
        return {
            "id_negocio": self._id,
            "nombre": self._nombre,
            "direccion": self._direccion,
            "telefono": self._telefono
        }

    @classmethod
    def get_all(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM negocio")
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def get_by_id(cls, id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM negocio WHERE id_negocio = %s", (id,))
        row = cur.fetchone()
        cur.close()
        return cls(row).to_json() if row else None

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO negocio (nombre, direccion, telefono) VALUES (%s, %s, %s)",
                    (data['nombre'], data.get('direccion'), data.get('telefono')))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Negocio creado exitosamente"}

    @classmethod
    def update(cls, id, data):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE negocio SET nombre=%s, direccion=%s, telefono=%s WHERE id_negocio=%s",
                    (data.get('nombre'), data.get('direccion'), data.get('telefono'), id))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Negocio actualizado"}

    @classmethod
    def delete(cls, id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM negocio WHERE id_negocio = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Negocio eliminado"}