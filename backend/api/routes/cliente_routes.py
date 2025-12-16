from api import app, mysql
from flask import jsonify, request
from api.models.cliente import Cliente
from api.utils import token_required

@app.route('/api/clientes', methods=['GET'])
@token_required
def get_clientes(current_user): # <---
    try:
        return jsonify(Cliente.get_all(current_user['id_negocio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
@token_required
def create_cliente(current_user): # <---
    try:
        data = request.json or {}
        data['id_negocio'] = current_user['id_negocio']
        
        if 'nombre' not in data or 'dni' not in data:
            return jsonify({"error": "Faltan nombre y dni"}), 400

        return jsonify(Cliente.create(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
@token_required
def delete_cliente(current_user, id_cliente): # <---
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_cliente FROM cliente WHERE id_cliente = %s AND id_negocio = %s", 
                    (id_cliente, current_user['id_negocio']))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Cliente no encontrado o no autorizado"}), 404
        cur.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Cliente eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500