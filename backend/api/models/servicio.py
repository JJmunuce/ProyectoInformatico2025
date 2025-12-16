from api import mysql

class Servicio:
    def __init__(self, row):
        self._id = row['id_servicio']
        self._nombre = row['nombre']
        self._duracion = row['duracion_minutos']
        self._id_negocio = row['id_negocio']

    def to_json(self):
        return {
            "id_servicio": self._id,
            "nombre": self._nombre,
            "duracion_minutos": self._duracion,
            "id_negocio": self._id_negocio
        }

    @classmethod
    def get_all(cls, id_negocio):
        cur = mysql.connection.cursor()
        # Filtramos por negocio
        cur.execute("SELECT * FROM servicio WHERE id_negocio = %s", (id_negocio,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO servicio (nombre, duracion_minutos, id_negocio) VALUES (%s, %s, %s)",
                    (data['nombre'], data['duracion_minutos'], data['id_negocio']))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Servicio creado exitosamente"}