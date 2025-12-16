from api import app, mysql
from flask import jsonify, request
from api.models.disponibilidad import Disponibilidad
from api.utils import token_required

@app.route('/api/disponibilidades', methods=['GET'])
@token_required
def get_disponibilidades(current_user): # <--- AHORA RECIBE EL USUARIO
    try:
        # Si el frontend pide los horarios de un profesional específico
        id_profesional = request.args.get('id_profesional')
        if id_profesional:
            return jsonify(Disponibilidad.get_by_profesional(id_profesional)), 200
        
        # Si no, devuelve todos los del negocio (para que el calendario filtre rápido)
        return jsonify(Disponibilidad.get_all_by_negocio(current_user['id_negocio'])), 200
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
def create_disponibilidad(current_user): # <--- CORREGIDO: RECIBE current_user
    try:
        data = request.json
        
        # VALIDACIÓN DE SEGURIDAD: 
        # Verificar que el profesional al que le asignas horario PERTENECE a tu negocio
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_profesional FROM profesional WHERE id_profesional = %s AND id_negocio = %s", 
                    (data['id_profesional'], current_user['id_negocio']))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "No tienes permiso sobre este profesional"}), 403
        cur.close()

        required = ['id_profesional', 'dia_semana', 'hora_inicio', 'hora_fin']
        if not all(k in data for k in required):
            return jsonify({"error": "Faltan datos obligatorios"}), 400
            
        return jsonify(Disponibilidad.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades/<int:id>', methods=['PUT'])
@token_required
def update_disponibilidad(current_user, id): # <--- CORREGIDO
    try:
        # Aquí podrías agregar validación de propiedad si quisieras ser estricto
        result = Disponibilidad.update(id, request.json)
        if result:
            return jsonify(result), 200
        return jsonify({"error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disponibilidades/<int:id>', methods=['DELETE'])
@token_required
def delete_disponibilidad(current_user, id): # <--- CORREGIDO
    try:
        # Podrías validar que la disponibilidad pertenezca a tu negocio antes de borrar
        if Disponibilidad.delete(id):
            return jsonify({"mensaje": "Eliminada exitosamente"}), 200
        return jsonify({"error": "No encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500