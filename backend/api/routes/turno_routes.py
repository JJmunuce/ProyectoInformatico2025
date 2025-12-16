from api import app, mysql
from flask import jsonify, request
from api.models.turno import Turno
from api.utils import token_required

@app.route('/api/turnos', methods=['GET'])
@token_required
def get_turnos(current_user): # <--- Recibe current_user
    try:
        # Pasa el id_negocio al modelo para filtrar
        return jsonify(Turno.get_all(current_user['id_negocio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/turnos', methods=['POST'])
@token_required
def create_turno(current_user): # <--- Recibe current_user
    try:
        data = request.json or {}
        # Aquí podrías agregar validaciones extra si quisieras asegurar 
        # que el cliente/profesional pertenecen al negocio, 
        # pero la validación principal está en el filtrado de listas.
        return jsonify(Turno.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/turnos/<int:id_turno>', methods=['DELETE'])
@token_required
def delete_turno(current_user, id_turno): # <--- Recibe current_user
    try:
        cur = mysql.connection.cursor()
        
        # Seguridad: Verificar que el turno pertenezca a un profesional de MI negocio
        cur.execute("""
            SELECT t.id_turno 
            FROM turno t
            JOIN profesional p ON t.id_profesional = p.id_profesional
            WHERE t.id_turno = %s AND p.id_negocio = %s
        """, (id_turno, current_user['id_negocio']))
        
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Turno no encontrado o no autorizado"}), 404
            
        # Borrado lógico (recomendado) o físico
        # Opción A: Borrado físico (DELETE)
        cur.execute("DELETE FROM turno WHERE id_turno = %s", (id_turno,))
        
        # Opción B: Cancelación (UPDATE) - Descomentar si prefieres esto
        # cur.execute("UPDATE turno SET estado = 'cancelado' WHERE id_turno = %s", (id_turno,))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Turno eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500