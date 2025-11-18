from flask import Blueprint, jsonify, request
from ..models import Profesional, db # <-- Cambiamos la importación

profesionales_bp = Blueprint('profesionales_bp', __name__)

# --- Rutas para /api/profesionales (Lista y Crear) ---

@profesionales_bp.route('/profesionales', methods=['POST'])
def create_profesional():
    data = request.json
    # Cambiamos las validaciones
    if not data or 'nombre' not in data or 'id_negocio' not in data:
        return jsonify({"error": "'nombre' y 'id_negocio' son requeridos"}), 400
        
    try:
        # Usamos el modelo Profesional
        nuevo_profesional = Profesional(
            nombre=data['nombre'],
            id_negocio=data['id_negocio']
        )
        db.session.add(nuevo_profesional)
        db.session.commit()
        return jsonify(nuevo_profesional.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@profesionales_bp.route('/profesionales', methods=['GET'])
def get_profesionales():
    try:
        # Opcional: filtrar por negocio
        id_negocio = request.args.get('id_negocio')
        if id_negocio:
            profesionales = Profesional.query.filter_by(id_negocio=id_negocio).all()
        else:
            profesionales = Profesional.query.all()
            
        return jsonify([p.serialize() for p in profesionales]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Rutas para /api/profesionales/<id> (Uno Específico) ---

@profesionales_bp.route('/profesionales/<int:id_profesional>', methods=['GET', 'PUT', 'DELETE'])
def handle_profesional_by_id(id_profesional):
    
    # Usamos get_or_404 con el modelo Profesional
    profesional = Profesional.query.get_or_404(id_profesional, description="Profesional no encontrado")

    # --- OBTENER UN PROFESIONAL (GET por ID) ---
    if request.method == 'GET':
        return jsonify(profesional.serialize()), 200

    # --- ACTUALIZAR UN PROFESIONAL (PUT) ---
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        profesional.nombre = data.get('nombre', profesional.nombre)
        profesional.id_negocio = data.get('id_negocio', profesional.id_negocio)
        
        try:
            db.session.commit()
            return jsonify(profesional.serialize()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UN PROFESIONAL (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(profesional)
            db.session.commit()
            return jsonify({"mensaje": "Profesional eliminado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
