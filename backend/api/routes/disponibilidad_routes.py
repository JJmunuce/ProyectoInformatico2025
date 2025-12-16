from api import app
from flask import jsonify, request
from api.models.disponibilidad import Disponibilidad
from api.utils import token_required

@app.route('/api/disponibilidades', methods=['GET'])
def get_disponibilidades():
    try:
        id_profesional = request.args.get('id_profesional')
        if id_profesional:
            return jsonify(Disponibilidad.get_by_profesional(id_profesional)), 200
        return jsonify(Disponibilidad.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades/<int:id>', methods=['GET'])
def get_disponibilidad(id):
    try:
        disp = Disponibilidad.get_by_id(id)
        if disp:
            return jsonify(disp), 200
        return jsonify({"error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades', methods=['POST'])
@token_required
def create_disponibilidad(current_user): # <---
    try:
        data = request.json
        required = ['id_profesional', 'dia_semana', 'hora_inicio', 'hora_fin']
        if not all(k in data for k in required):
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        return jsonify(Disponibilidad.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades/<int:id>', methods=['PUT'])
@token_required
def update_disponibilidad(current_user, id): # <---
    try:
        result = Disponibilidad.update(id, request.json)
        if result:
            return jsonify(result), 200
        return jsonify({"error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades/<int:id>', methods=['DELETE'])
@token_required
def delete_disponibilidad(current_user, id): # <---
    try:
        if Disponibilidad.delete(id):
            return jsonify({"mensaje": "Eliminada exitosamente"}), 200
        return jsonify({"error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500