from api import app, mysql
from flask import jsonify, request
from api.models.servicio import Servicio
from api.utils import token_required

@app.route('/api/servicios', methods=['GET'])
@token_required
def get_servicios(current_user): # <---
    try:
        return jsonify(Servicio.get_all(current_user['id_negocio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/servicios', methods=['POST'])
@token_required
def create_servicio(current_user): # <---
    try:
        data = request.json or {}
        data['id_negocio'] = current_user['id_negocio']
        if 'nombre' not in data or 'duracion_minutos' not in data:
            return jsonify({"error": "Faltan datos obligatorios"}), 400
        return jsonify(Servicio.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/servicios/<int:id_servicio>', methods=['DELETE'])
@token_required
def delete_servicio(current_user, id_servicio): # <---
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_servicio FROM servicio WHERE id_servicio = %s AND id_negocio = %s", 
                    (id_servicio, current_user['id_negocio']))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Servicio no encontrado o no autorizado"}), 404
        cur.execute("DELETE FROM servicio WHERE id_servicio = %s", (id_servicio,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Servicio eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500