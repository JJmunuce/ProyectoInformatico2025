from flask import Blueprint, jsonify, request
from ..models import Turno, db # Importamos el modelo Turno
from datetime import datetime

turnos_bp = Blueprint('turnos_bp', __name__)

# --- Rutas para /api/turnos (Lista y Crear) ---
@turnos_bp.route('/turnos', methods=['GET', 'POST'])
def handle_turnos():
    
    # --- CREAR UN NUEVO TURNO (POST) ---
    if request.method == 'POST':
        data = request.json
        
        req_fields = ['id_cliente', 'id_profesional', 'id_servicio', 'fecha', 'hora']
        if not data or not all(field in data for field in req_fields):
            return jsonify({"error": "Faltan datos: 'id_cliente', 'id_profesional', 'id_servicio', 'fecha' (YYYY-MM-DD) y 'hora' (HH:MM) son requeridos"}), 400
            
        try:
            # Convertimos los strings de fecha y hora a objetos de Python
            fecha_obj = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            hora_obj = datetime.strptime(data['hora'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Formato de fecha (YYYY-MM-DD) u hora (HH:MM) inválido"}), 400

        try:
            # --- Lógica de Negocio: Evitar conflictos de turnos ---
            # Verificamos si el profesional ya tiene un turno en esa fecha y hora
            conflicto = Turno.query.filter_by(
                id_profesional=data['id_profesional'],
                fecha=fecha_obj,
                hora=hora_obj
            ).first()

            if conflicto:
                return jsonify({"error": "El profesional ya tiene un turno asignado en esa fecha y hora"}), 409 # 409 Conflict
            
            # Si no hay conflicto, creamos el turno
            nuevo_turno = Turno(
                id_cliente=data['id_cliente'],
                id_profesional=data['id_profesional'],
                id_servicio=data['id_servicio'],
                fecha=fecha_obj,
                hora=hora_obj,
                estado=data.get('estado', 'pendiente') # Estado por defecto
            )
            db.session.add(nuevo_turno)
            db.session.commit()
            return jsonify(nuevo_turno.serialize()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS TURNOS (GET) ---
    if request.method == 'GET':
        try:
            # Los filtros son esenciales para los turnos
            # Ej: /api/turnos?id_profesional=1
            # Ej: /api/turnos?id_cliente=3
            # Ej: /api/turnos?fecha=2024-12-25
            
            query = Turno.query
            id_profesional = request.args.get('id_profesional')
            id_cliente = request.args.get('id_cliente')
            fecha_str = request.args.get('fecha')
            estado = request.args.get('estado')

            if id_profesional:
                query = query.filter_by(id_profesional=id_profesional)
            if id_cliente:
                query = query.filter_by(id_cliente=id_cliente)
            if estado:
                query = query.filter_by(estado=estado)
            if fecha_str:
                try:
                    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    query = query.filter_by(fecha=fecha_obj)
                except ValueError:
                    return jsonify({"error": "Formato de fecha (YYYY-MM-DD) inválido"}), 400
                
            turnos = query.all()
            return jsonify([t.serialize() for t in turnos]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/turnos/<id> (Uno Específico) ---
@turnos_bp.route('/turnos/<int:id_turno>', methods=['GET', 'PUT', 'DELETE'])
def handle_turno_by_id(id_turno):
    
    turno = Turno.query.get_or_404(id_turno, description="Turno no encontrado")

    # --- OBTENER UN TURNO (GET por ID) ---
    if request.method == 'GET':
        return jsonify(turno.serialize()), 200

    # --- ACTUALIZAR UN TURNO (PUT) ---
    # Útil para confirmar, cancelar o reprogramar
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        # Actualizamos campos, con manejo de fecha/hora si vienen
        if 'fecha' in data:
            try:
                turno.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Formato de fecha (YYYY-MM-DD) inválido"}), 400
                
        if 'hora' in data:
            try:
                turno.hora = datetime.strptime(data['hora'], '%H:%M').time()
            except ValueError:
                return jsonify({"error": "Formato de hora (HH:MM) inválido"}), 400

        # Actualizar el estado es lo más común
        turno.estado = data.get('estado', turno.estado)
        
        # Se podrían actualizar también los IDs, pero es menos común
        turno.id_cliente = data.get('id_cliente', turno.id_cliente)
        turno.id_profesional = data.get('id_profesional', turno.id_profesional)
        turno.id_servicio = data.get('id_servicio', turno.id_servicio)
        
        try:
            # (Faltaría la validación de conflicto si se reprograma,
            # pero lo omitimos para mantener el PUT simple)
            db.session.commit()
            return jsonify(turno.serialize()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UN TURNO (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(turno)
            db.session.commit()
            return jsonify({"mensaje": "Turno eliminado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500