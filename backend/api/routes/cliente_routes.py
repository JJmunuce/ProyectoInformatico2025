from api import app
from flask import jsonify, request
from api.models.cliente import Cliente

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    try:
        return jsonify(Cliente.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
def create_cliente():
    try:
        data = request.json
        if not data or 'nombre' not in data or 'id_negocio' not in data:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        return jsonify(Cliente.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500