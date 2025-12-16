from api import app, mysql
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
        # Permitir reservar sin token/secret (clientes)
        return jsonify(Turno.create(request.json)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/turnos/<int:id_turno>', methods=['DELETE'])
def delete_turno(id_turno):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_turno FROM turno WHERE id_turno = %s", (id_turno,))
        t = cur.fetchone()
        if not t:
            cur.close()
            return jsonify({"error": "Turno no encontrado"}), 404
        cur.execute("DELETE FROM turno WHERE id_turno = %s", (id_turno,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Turno eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500