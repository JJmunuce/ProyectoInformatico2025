from flask import Blueprint, jsonify, request
from ..models import Disponibilidad, db
from datetime import datetime

disponibilidades_bp = Blueprint('disponibilidades_bp', __name__)

# --- Rutas para /api/disponibilidades (Lista y Crear) ---
@disponibilidades_bp.route('/disponibilidades', methods=['GET', 'POST'])
def handle_disponibilidades():
    
    # --- CREAR UNA NUEVA DISPONIBILIDAD (POST) ---
    if request.method == 'POST':
        data = request.json
        
        req_fields = ['id_profesional', 'dia_semana', 'hora_inicio', 'hora_fin']
        if not data or not all(field in data for field in req_fields):
            return jsonify({"error": "Faltan datos: 'id_profesional', 'dia_semana', 'hora_inicio' (HH:MM) y 'hora_fin' (HH:MM) son requeridos"}), 400
            
        try:
            # Convertimos los strings de hora a objetos time
            hora_inicio_obj = datetime.strptime(data['hora_inicio'], '%H:%M').time()
            hora_fin_obj = datetime.strptime(data['hora_fin'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Formato de hora (HH:MM) inválido"}), 400

        # Lógica de negocio: Validar que hora_inicio sea menor que hora_fin
        if hora_inicio_obj >= hora_fin_obj:
            return jsonify({"error": "La 'hora_inicio' debe ser anterior a la 'hora_fin'"}), 400

        try:
            # TODO Opcional: Validar que esta nueva disponibilidad no se solape
            # con otra existente para el mismo profesional y día.
            
            nueva_disponibilidad = Disponibilidad(
                id_profesional=data['id_profesional'],
                dia_semana=data['dia_semana'], # Ej: "Lunes", "Martes", o 0-6
                hora_inicio=hora_inicio_obj,
                hora_fin=hora_fin_obj
            )
            db.session.add(nueva_disponibilidad)
            db.session.commit()
            return jsonify(nueva_disponibilidad.serialize()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODAS LAS DISPONIBILIDADES (GET) ---
    if request.method == 'GET':
        try:
            # El filtro por profesional es el más importante aquí
            # Ej: /api/disponibilidades?id_profesional=1
            
            query = Disponibilidad.query
            id_profesional = request.args.get('id_profesional')

            if id_profesional:
                query = query.filter_by(id_profesional=id_profesional)
            
            # También se podría filtrar por dia_semana
            dia_semana = request.args.get('dia_semana')
            if dia_semana:
                query = query.filter_by(dia_semana=dia_semana)
                
            disponibilidades = query.all()
            return jsonify([d.serialize() for d in disponibilidades]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/disponibilidades/<id> (Una Específica) ---
@disponibilidades_bp.route('/disponibilidades/<int:id_disponibilidad>', methods=['GET', 'PUT', 'DELETE'])
def handle_disponibilidad_by_id(id_disponibilidad):
    
    disponibilidad = Disponibilidad.query.get_or_404(id_disponibilidad, description="Disponibilidad no encontrada")

    # --- OBTENER UNA DISPONIBILIDAD (GET por ID) ---
    if request.method == 'GET':
        return jsonify(disponibilidad.serialize()), 200

    # --- ACTUALIZAR UNA DISPONIBILIDAD (PUT) ---
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        # Actualizamos campos
        disponibilidad.id_profesional = data.get('id_profesional', disponibilidad.id_profesional)
        disponibilidad.dia_semana = data.get('dia_semana', disponibilidad.dia_semana)

        try:
            if 'hora_inicio' in data:
                disponibilidad.hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
            if 'hora_fin' in data:
                disponibilidad.hora_fin = datetime.strptime(data['hora_fin'], '%H:%M').time()
            
            # Validar de nuevo si se actualizaron las horas
            if disponibilidad.hora_inicio >= disponibilidad.hora_fin:
                db.session.rollback() # Deshacer cambios si son inválidos
                return jsonify({"error": "La 'hora_inicio' debe ser anterior a la 'hora_fin'"}), 400

            db.session.commit()
            return jsonify(disponibilidad.serialize()), 200
            
        except ValueError:
            return jsonify({"error": "Formato de hora (HH:MM) inválido"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UNA DISPONIBILIDAD (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(disponibilidad)
            db.session.commit()
            return jsonify({"mensaje": "Disponibilidad eliminada exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500