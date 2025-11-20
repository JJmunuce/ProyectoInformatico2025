from api import app
from flask import jsonify, request
from api.models.profesional import Profesional

@app.route('/api/profesionales', methods=['GET'])
def get_profesionales():
    try:
        return jsonify(Profesional.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales', methods=['POST'])
def create_profesional():
    try:
        return jsonify(Profesional.create(request.json)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500