from api import app
from flask import jsonify, request
from api.models.turno import Turno

@app.route('/api/turnos', methods=['GET'])
def get_turnos():
    try:
        return jsonify(Turno.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/turnos', methods=['POST'])
def create_turno():
    try:
        return jsonify(Turno.create(request.json)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500