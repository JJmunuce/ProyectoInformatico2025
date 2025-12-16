from api import app, mysql
from flask import jsonify, request
from api.models.profesional import Profesional
from api.utils import token_required

@app.route('/api/profesionales', methods=['GET'])
@token_required
def get_profesionales(current_user): # <--- Recibe el usuario
    try:
        id_servicio = request.args.get('id_servicio')
        if id_servicio:
            return jsonify(Profesional.get_by_servicio(id_servicio)), 200
            
        # Filtramos por el negocio del usuario logueado
        return jsonify(Profesional.get_all(current_user['id_negocio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales', methods=['POST'])
@token_required
def create_profesional(current_user): # <--- Recibe el usuario
    try:
        data = request.json or {}
        # Asignamos automáticamente el ID del negocio del token
        data['id_negocio'] = current_user['id_negocio']
        
        if 'nombre' not in data:
            return jsonify({"error": "Faltan datos: 'nombre' es requerido"}), 400
        return jsonify(Profesional.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales/<int:id_profesional>', methods=['DELETE'])
@token_required
def delete_profesional(current_user, id_profesional): # <--- Recibe el usuario
    try:
        cur = mysql.connection.cursor()
        # Seguridad: Solo borra si pertenece a tu negocio
        cur.execute("SELECT id_profesional FROM profesional WHERE id_profesional = %s AND id_negocio = %s", 
                    (id_profesional, current_user['id_negocio']))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Profesional no encontrado o no autorizado"}), 404
            
        cur.execute("DELETE FROM profesional WHERE id_profesional = %s", (id_profesional,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Profesional eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales/<int:id>/servicios', methods=['GET'])
def get_profesional_servicios(id):
    # Esta ruta suele ser pública para ver qué hace cada médico
    try:
        return jsonify(Profesional.get_services(id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales/<int:id>/servicios', methods=['POST'])
@token_required
def assign_service_to_profesional(current_user, id): # <--- Recibe el usuario
    try:
        data = request.json
        if 'id_servicio' not in data:
            return jsonify({"error": "Falta id_servicio"}), 400
        return jsonify(Profesional.assign_service(id, data['id_servicio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profesionales/<int:id>/servicios/<int:id_servicio>', methods=['DELETE'])
@token_required
def remove_service_from_profesional(current_user, id, id_servicio): # <--- Recibe el usuario
    try:
        return jsonify(Profesional.remove_service(id, id_servicio)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500