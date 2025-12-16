from api import app
from flask import jsonify, request
from api.models.negocio import Negocio
from api.utils import token_required

@app.route('/api/negocios', methods=['GET'])
def get_negocios():
    # Esta suele ser pública o para superadmin
    try:
        return jsonify(Negocio.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios/<int:id>', methods=['GET'])
def get_negocio(id):
    try:
        negocio = Negocio.get_by_id(id)
        if negocio:
            return jsonify(negocio), 200
        return jsonify({"error": "No encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios', methods=['POST'])
@token_required
def create_negocio(current_user): # <---
    try:
        data = request.json
        if not data or 'nombre' not in data:
            return jsonify({"error": "Nombre es requerido"}), 400
        return jsonify(Negocio.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios/<int:id>', methods=['PUT'])
@token_required
def update_negocio(current_user, id): # <---
    try:
        return jsonify(Negocio.update(id, request.json)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios/<int:id>', methods=['DELETE'])
@token_required
def delete_negocio(current_user, id): # <---
    try:
        return jsonify(Negocio.delete(id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500