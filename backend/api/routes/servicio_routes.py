from flask import Blueprint, jsonify, request
from ..models import Servicio, db # Importamos el modelo Servicio

servicios_bp = Blueprint('servicios_bp', __name__)

# --- Rutas para /api/servicios (Lista y Crear) ---
@servicios_bp.route('/servicios', methods=['GET', 'POST'])
def handle_servicios():
    
    # --- CREAR UN NUEVO SERVICIO (POST) ---
    if request.method == 'POST':
        data = request.json
        
        # Validamos que los datos requeridos estén presentes
        if not data or 'nombre' not in data or 'duracion_minutos' not in data or 'id_profesional' not in data or 'id_negocio' not in data:
            return jsonify({"error": "'nombre', 'duracion_minutos', 'id_profesional' y 'id_negocio' son requeridos"}), 400
            
        try:
            nuevo_servicio = Servicio(
                nombre=data['nombre'],
                duracion_minutos=data['duracion_minutos'],
                id_profesional=data['id_profesional'],
                id_negocio=data['id_negocio']
            )
            db.session.add(nuevo_servicio)
            db.session.commit()
            return jsonify(nuevo_servicio.serialize()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS SERVICIOS (GET) ---
    if request.method == 'GET':
        try:
            # Opciones de filtrado (muy útiles para servicios)
            # Ej: /api/servicios?id_negocio=1
            # Ej: /api/servicios?id_profesional=5
            
            query = Servicio.query
            id_negocio = request.args.get('id_negocio')
            id_profesional = request.args.get('id_profesional')

            if id_negocio:
                query = query.filter_by(id_negocio=id_negocio)
            if id_profesional:
                query = query.filter_by(id_profesional=id_profesional)
                
            servicios = query.all()
            return jsonify([s.serialize() for s in servicios]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/servicios/<id> (Uno Específico) ---
@servicios_bp.route('/servicios/<int:id_servicio>', methods=['GET', 'PUT', 'DELETE'])
def handle_servicio_by_id(id_servicio):
    
    # Usamos get_or_404 para buscar el servicio
    servicio = Servicio.query.get_or_404(id_servicio, description="Servicio no encontrado")

    # --- OBTENER UN SERVICIO (GET por ID) ---
    if request.method == 'GET':
        return jsonify(servicio.serialize()), 200

    # --- ACTUALIZAR UN SERVICIO (PUT) ---
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        # Actualizamos los campos
        servicio.nombre = data.get('nombre', servicio.nombre)
        servicio.duracion_minutos = data.get('duracion_minutos', servicio.duracion_minutos)
        servicio.id_profesional = data.get('id_profesional', servicio.id_profesional)
        servicio.id_negocio = data.get('id_negocio', servicio.id_negocio)
        
        try:
            db.session.commit()
            return jsonify(servicio.serialize()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UN SERVICIO (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(servicio)
            db.session.commit()
            return jsonify({"mensaje": "Servicio eliminado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500