from api import mysql

class Cliente:
    def __init__(self, row):
        self._id = row['id_cliente']
        self._nombre = row['nombre']
        self._telefono = row['telefono']
        self._id_negocio = row['id_negocio']

    def to_json(self):
        return {
            "id_cliente": self._id,
            "nombre": self._nombre,
            "telefono": self._telefono,
            "id_negocio": self._id_negocio
        }

    @classmethod
    def get_all(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cliente")
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cliente (nombre, telefono, id_negocio) VALUES (%s, %s, %s)",
                    (data['nombre'], data.get('telefono'), data['id_negocio']))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Cliente creado exitosamente"}
    