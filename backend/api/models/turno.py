from api import mysql
from datetime import datetime, timedelta

class Turno:
    def __init__(self, row):
        self._id = row['id_turno']
        self._id_profesional = row['id_profesional']
        self._id_cliente = row['id_cliente']
        self._id_servicio = row['id_servicio']
        self._fecha = str(row['fecha']) # Convertir Date a string
        self._hora = str(row['hora'])   # Convertir Time a string
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
        
        # 1. Obtener la duración del servicio que se intenta agendar
        cur.execute("SELECT duracion_minutos FROM servicio WHERE id_servicio = %s", (data['id_servicio'],))
        servicio_data = cur.fetchone()
        if not servicio_data:
            raise Exception("Servicio no encontrado")
        
        duracion = servicio_data['duracion_minutos'] 
        
        
        hora_inicio_nueva = datetime.strptime(data['hora'], '%H:%M')
        hora_fin_nueva = hora_inicio_nueva + timedelta(minutes=duracion)
        
        # 2. Verificar superposición
        # Buscamos turnos del mismo profesional en la misma fecha
        # que terminen DESPUÉS de que empiece el nuevo Y empiecen ANTES de que termine el nuevo
        cur.execute("""
            SELECT t.id_turno 
            FROM turno t
            JOIN servicio s ON t.id_servicio = s.id_servicio
            WHERE t.id_profesional = %s 
            AND t.fecha = %s
            AND t.estado != 'cancelado'
            AND (
                ADDTIME(t.hora, SEC_TO_TIME(s.duracion_minutos * 60)) > %s 
                AND t.hora < %s
            )
        """, (data['id_profesional'], data['fecha'], hora_inicio_nueva.time(), hora_fin_nueva.time()))
        
        if cur.fetchone():
            cur.close()
            raise Exception("El profesional ya tiene un turno ocupado en ese rango horario")

        # Insertar si no hay conflicto
        cur.execute("""
            INSERT INTO turno (id_profesional, id_cliente, id_servicio, fecha, hora, estado) 
            VALUES (%s, %s, %s, %s, %s, 'pendiente')
        """, (data['id_profesional'], data['id_cliente'], data['id_servicio'], data['fecha'], data['hora']))
        
        mysql.connection.commit()
        cur.close()
        return {"mensaje": "Turno agendado exitosamente"}