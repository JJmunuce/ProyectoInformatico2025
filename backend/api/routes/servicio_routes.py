from api import app
from flask import jsonify, request
from api.models.servicio import Servicio

@app.route('/api/servicios', methods=['GET'])
def get_servicios():
    try:
        return jsonify(Servicio.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/servicios', methods=['POST'])
def create_servicio():
    try:
        return jsonify(Servicio.create(request.json)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500