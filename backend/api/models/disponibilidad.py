from datetime import datetime, timedelta

class Disponibilidad:
    def __init__(self, row):
        self._id = row['id_disponibilidad']
        self._id_profesional = row['id_profesional']
        self._dia_semana = row['dia_semana']
        # Convertimos timedelta a string (HH:MM:SS) si es necesario para JSON
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
    def get_all(cls):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM disponibilidad")
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def get_by_profesional(cls, id_profesional):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM disponibilidad WHERE id_profesional = %s", (id_profesional,))
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def get_by_id(cls, id):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM disponibilidad WHERE id_disponibilidad = %s", (id,))
        row = cur.fetchone()
        cur.close()
        return cls(row).to_json() if row else None

    @classmethod
    def create(cls, data):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        
        # 1. Validar formato y lógica básica (Inicio < Fin)
        h_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        h_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
        
        if h_inicio >= h_fin:
            raise Exception("La hora de inicio debe ser anterior a la hora de fin")

        # 2. VALIDACIÓN DE SUPERPOSICIÓN (El arreglo crítico)
        # Buscamos si ya existe algún registro para ese profesional en ese día
        # que se solape con el horario nuevo.
        cur.execute("""
            SELECT id_disponibilidad FROM disponibilidad 
            WHERE id_profesional = %s 
            AND dia_semana = %s
            AND (
                (hora_inicio < %s AND hora_fin > %s) -- Caso: Nuevo solapa al existente
                OR
                (hora_inicio >= %s AND hora_inicio < %s) -- Caso: Existente empieza dentro del nuevo
            )
        """, (
            data['id_profesional'], 
            data['dia_semana'], 
            data['hora_fin'],   # Nuevo Fin
            data['hora_inicio'], # Nuevo Inicio
            data['hora_inicio'], # Nuevo Inicio
            data['hora_fin']     # Nuevo Fin
        ))
        
        if cur.fetchone():
            cur.close()
            raise Exception("El horario se superpone con una disponibilidad existente.")

        # 3. Insertar si no hay conflictos
        cur.execute("INSERT INTO disponibilidad (id_profesional, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                    (data['id_profesional'], data['dia_semana'], data['hora_inicio'], data['hora_fin']))
        
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Disponibilidad creada exitosamente"}

    @classmethod
    def update(cls, id, data):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        # Obtener datos actuales
        cur.execute("SELECT * FROM disponibilidad WHERE id_disponibilidad = %s", (id,))
        actual = cur.fetchone()
        if not actual:
            cur.close()
            return None

        # Usar nuevos datos o mantener los viejos
        id_prof = data.get('id_profesional', actual['id_profesional'])
        dia = data.get('dia_semana', actual['dia_semana'])
        inicio = data.get('hora_inicio', str(actual['hora_inicio']))
        fin = data.get('hora_fin', str(actual['hora_fin']))

        # Nota: Idealmente deberías validar superposición aquí también (excluyendo el id actual),
        # pero para mantenerlo simple solo aplicamos el UPDATE.

        cur.execute("UPDATE disponibilidad SET id_profesional=%s, dia_semana=%s, hora_inicio=%s, hora_fin=%s WHERE id_disponibilidad=%s",
                    (id_prof, dia, inicio, fin, id))
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Disponibilidad actualizada"}

    @classmethod
    def delete(cls, id):
        from api import mysql  # Importación tardía
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM disponibilidad WHERE id_disponibilidad = %s", (id,))
        mysql.connection.commit()
        row_count = cur.rowcount
        cur.close()
        return row_count > 0