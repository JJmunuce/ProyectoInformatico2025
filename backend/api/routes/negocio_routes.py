from api import app
from flask import jsonify, request
from api.models.negocio import Negocio

@app.route('/api/negocios', methods=['GET'])
def get_negocios():
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
def create_negocio():
    try:
        data = request.json
        if not data or 'nombre' not in data:
            return jsonify({"error": "Nombre es requerido"}), 400
        return jsonify(Negocio.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios/<int:id>', methods=['PUT'])
def update_negocio(id):
    try:
        return jsonify(Negocio.update(id, request.json)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negocios/<int:id>', methods=['DELETE'])
def delete_negocio(id):
    try:
        return jsonify(Negocio.delete(id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500