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
    def get_all(cls, id_negocio): # <--- Recibe id_negocio
        cur = mysql.connection.cursor()
        # Filtramos por negocio
        cur.execute("SELECT * FROM profesional WHERE id_negocio = %s", (id_negocio,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def get_by_servicio(cls, id_servicio):
        cur = mysql.connection.cursor()
        query = """
            SELECT p.* FROM profesional p
            JOIN servicio_profesional sp ON p.id_profesional = sp.id_profesional
            WHERE sp.id_servicio = %s
        """
        cur.execute(query, (id_servicio,))
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

    @classmethod
    def get_services(cls, id_profesional):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_servicio FROM servicio_profesional WHERE id_profesional = %s", (id_profesional,))
        rows = cur.fetchall()
        cur.close()
        return [row['id_servicio'] for row in rows]

    @classmethod
    def assign_service(cls, id_profesional, id_servicio):
        cur = mysql.connection.cursor()
        cur.execute("INSERT IGNORE INTO servicio_profesional (id_profesional, id_servicio) VALUES (%s, %s)", (id_profesional, id_servicio))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Servicio asignado"}

    @classmethod
    def remove_service(cls, id_profesional, id_servicio):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM servicio_profesional WHERE id_profesional = %s AND id_servicio = %s", (id_profesional, id_servicio))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Servicio removido"}