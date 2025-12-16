from api import mysql
from datetime import datetime, timedelta

class Turno:
    def __init__(self, row):
        self._id = row['id_turno']
        self._id_profesional = row['id_profesional']
        self._id_cliente = row['id_cliente']
        self._id_servicio = row['id_servicio']
        self._fecha = str(row['fecha'])
        self._hora = str(row['hora'])
        self._estado = row['estado']

    def to_json(self):
        return {
            "id_turno": self._id,
            "id_profesional": self._id_profesional,
            "id_cliente": self._id_cliente,
            "id_servicio": self._id_servicio,
            "fecha": self._fecha,
            "hora": self._hora,
            "estado": self._estado
        }

    @classmethod
    def get_all(cls):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM turno")
        rows = cur.fetchall()
        cur.close()
        return [cls(row).to_json() for row in rows]

    @classmethod
    def create(cls, data):
        cur = mysql.connection.cursor()
        
        # 1. Obtener la duración del servicio
        cur.execute("SELECT duracion_minutos FROM servicio WHERE id_servicio = %s", (data['id_servicio'],))
        servicio_data = cur.fetchone()
        if not servicio_data:
            cur.close()
            raise Exception("Servicio no encontrado")
        
        duracion = servicio_data['duracion_minutos'] 
        
        # 2. Parsear fecha y hora
        try:
            # Asume formato fecha YYYY-MM-DD y hora HH:MM
            fecha_obj = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            hora_inicio_dt = datetime.strptime(data['hora'], '%H:%M') 
        except ValueError:
            cur.close()
            raise Exception("Formato de fecha (YYYY-MM-DD) o hora (HH:MM) inválido")

        # Calculamos la hora de fin del turno
        hora_fin_dt = hora_inicio_dt + timedelta(minutes=duracion)
        
        h_inicio_turno = hora_inicio_dt.time()
        h_fin_turno = hora_fin_dt.time()

        # 3. VALIDAR DISPONIBILIDAD REAL
        # Python weekday(): 0=Lunes, 6=Domingo.
        dia_semana = fecha_obj.weekday() 

        # Verificamos si existe un rango de disponibilidad que cubra TODO el turno
        cur.execute("""
            SELECT id_disponibilidad 
            FROM disponibilidad 
            WHERE id_profesional = %s 
            AND dia_semana = %s
            AND hora_inicio <= %s 
            AND hora_fin >= %s
        """, (data['id_profesional'], dia_semana, h_inicio_turno, h_fin_turno))
        
        disp_encontrada = cur.fetchone()
        
        if not disp_encontrada:
            cur.close()
            raise Exception("El profesional no tiene disponibilidad configurada para ese día y horario.")

        # 4. Verificar superposición con otros turnos existentes
        cur.execute("""
            SELECT t.id_turno 
            FROM turno t
            JOIN servicio s ON t.id_servicio = s.id_servicio
            WHERE t.id_profesional = %s 
            AND t.fecha = %s
            AND t.estado != 'cancelado'
            AND (
                -- Se solapan si: (InicioA < FinB) y (InicioB < FinA)
                t.hora < %s 
                AND ADDTIME(t.hora, SEC_TO_TIME(s.duracion_minutos * 60)) > %s
            )
        """, (data['id_profesional'], data['fecha'], h_fin_turno, h_inicio_turno))
        
        if cur.fetchone():
            cur.close()
            raise Exception("El profesional ya tiene un turno ocupado en ese rango horario")

        # 5. Insertar
        cur.execute("""
            INSERT INTO turno (id_profesional, id_cliente, id_servicio, fecha, hora, estado) 
            VALUES (%s, %s, %s, %s, %s, 'pendiente')
        """, (data['id_profesional'], data['id_cliente'], data['id_servicio'], data['fecha'], data['hora']))
        
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Turno agendado exitosamente"}