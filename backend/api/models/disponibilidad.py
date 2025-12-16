from api import mysql

class Disponibilidad:
    def __init__(self, row):
        self._id = row['id_disponibilidad']
        self._id_profesional = row['id_profesional']
        self._dia_semana = row['dia_semana']
        self._hora_inicio = str(row['hora_inicio'])
        self._hora_fin = str(row['hora_fin'])

    def to_json(self):
        return {
            "id_disponibilidad": self._id,
            "id_profesional": self._id_profesional,
            "dia_semana": self._dia_semana,
            "hora_inicio": self._hora_inicio,
            "hora_fin": self._hora_fin
        }

    @classmethod
    def get_all_by_negocio(cls, id_negocio):
        cur = mysql.connection.cursor()
        # JOIN clave para filtrar horarios solo de TU negocio
        query = """
            SELECT d.* FROM disponibilidad d
            JOIN profesional p ON d.id_profesional = p.id_profesional
            WHERE p.id_negocio = %s
        """
        cur.execute(query, (id_negocio,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def get_by_profesional(cls, id_profesional):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM disponibilidad WHERE id_profesional = %s", (id_profesional,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]
    
    @classmethod
    def get_by_id(cls, id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM disponibilidad WHERE id_disponibilidad = %s", (id,))
        row = cur.fetchone()
        cur.close()
        return cls(row).to_json() if row else None

    @classmethod
    def create(cls, data):
        # Validación básica de solapamiento
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_disponibilidad FROM disponibilidad 
            WHERE id_profesional = %s AND dia_semana = %s
            AND (
                (hora_inicio <= %s AND hora_fin > %s) OR
                (hora_inicio < %s AND hora_fin >= %s) OR
                (hora_inicio >= %s AND hora_fin <= %s)
            )
        """, (data['id_profesional'], data['dia_semana'], 
              data['hora_inicio'], data['hora_inicio'], 
              data['hora_fin'], data['hora_fin'],
              data['hora_inicio'], data['hora_fin']))
        
        if cur.fetchone():
            cur.close()
            raise Exception("El horario se superpone con otro existente")

        cur.execute("INSERT INTO disponibilidad (id_profesional, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                    (data['id_profesional'], data['dia_semana'], data['hora_inicio'], data['hora_fin']))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Disponibilidad creada"}

    @classmethod
    def update(cls, id, data):
        # Lógica de actualización si la necesitas
        return {"mensaje": "Actualizado"}

    @classmethod
    def delete(cls, id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM disponibilidad WHERE id_disponibilidad = %s", (id,))
        affected = cur.rowcount
        mysql.connection.commit()
        cur.close()
        return affected > 0