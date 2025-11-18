# api/routes/negocio_routes.py
from flask import Blueprint, jsonify, request
from ..models import Negocio, db # Importamos Negocio y db

negocios_bp = Blueprint('negocios_bp', __name__)


# --- Rutas para /api/negocios (Lista y Crear) ---
@negocios_bp.route('/negocios', methods=['GET', 'POST'])
def handle_negocios():
    
    # --- CREAR UN NUEVO NEGOCIO (POST) ---
    if request.method == 'POST':
        data = request.json
        if not data or 'nombre' not in data:
            return jsonify({"error": "'nombre' es requerido"}), 400
            
        try:
            nuevo_negocio = Negocio(
                nombre=data['nombre'],
                direccion=data.get('direccion'),
                telefono=data.get('telefono')
            )
            db.session.add(nuevo_negocio)
            db.session.commit()
            return jsonify(nuevo_negocio.serialize()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS NEGOCIOS (GET) ---
    if request.method == 'GET':
        try:
            negocios = Negocio.query.all()
            return jsonify([negocio.serialize() for negocio in negocios]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/negocios/<id> (Uno Específico) ---
@negocios_bp.route('/negocios/<int:id_negocio>', methods=['GET', 'PUT', 'DELETE'])
def handle_negocio_by_id(id_negocio):
    
    # Primero, buscamos el negocio en la DB
    negocio = Negocio.query.get(id_negocio)
    
    # Si no existe, para cualquier método, devolvemos 404
    if not negocio:
        return jsonify({"error": "Negocio no encontrado"}), 404

    # --- OBTENER UN NEGOCIO (GET por ID) ---
    if request.method == 'GET':
        return jsonify(negocio.serialize()), 200

    # --- ACTUALIZAR UN NEGOCIO (PUT) ---
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        # Actualizamos los campos
        # Usamos data.get() para actualizar solo lo que viene en el JSON
        negocio.nombre = data.get('nombre', negocio.nombre)
        negocio.direccion = data.get('direccion', negocio.direccion)
        negocio.telefono = data.get('telefono', negocio.telefono)
        
        try:
            db.session.commit()
            return jsonify(negocio.serialize()), 200 # 200 = OK
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UN NEGOCIO (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(negocio)
            db.session.commit()
            return jsonify({"mensaje": "Negocio eliminado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500