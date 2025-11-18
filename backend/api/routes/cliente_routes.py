# api/routes/cliente_routes.py
from flask import Blueprint, jsonify, request
from ..models import Cliente, db, Negocio  # Importamos los modelos y la db

# Creamos un "Blueprint". Es como un mini-router para nuestros clientes.
clientes_bp = Blueprint('clientes_bp', __name__)

@clientes_bp.route('/login', methods=['GET'])
def get_login():
    try:
        # Consultamos la base de datos usando SQLAlchemy
        # Cliente.query.all() trae todos los registros de la tabla Cliente
        clientes = Cliente.query.all()
        
        # Usamos la función .serialize() que creamos en models.py
        # para convertir la lista de objetos Cliente a una lista de diccionarios
        lista_clientes = [cliente.serialize() for cliente in clientes]
        
        # Devolvemos la lista como JSON
        return jsonify(lista_clientes), 200 # 200 = OK
    except Exception as e:
        return jsonify({"error": f"Error al obtener clientes: {str(e)}"}), 500


# --- ENDPOINT 1: GET /api/clientes ---
# (Obtener todos los clientes)
@clientes_bp.route('/clientes', methods=['GET'])
def get_clientes():
    try:
        # Consultamos la base de datos usando SQLAlchemy
        # Cliente.query.all() trae todos los registros de la tabla Cliente
        clientes = Cliente.query.all()
        
        # Usamos la función .serialize() que creamos en models.py
        # para convertir la lista de objetos Cliente a una lista de diccionarios
        lista_clientes = [cliente.serialize() for cliente in clientes]
        
        # Devolvemos la lista como JSON
        return jsonify(lista_clientes), 200 # 200 = OK
    except Exception as e:
        return jsonify({"error": f"Error al obtener clientes: {str(e)}"}), 500

# --- ENDPOINT 2: POST /api/clientes ---
# (Crear un nuevo cliente)
@clientes_bp.route('/clientes', methods=['POST'])
def create_cliente():
    # request.json contiene el cuerpo (body) JSON que nos envía el cliente (ej. Postman)
    data = request.json
    
    # Validación simple: chequeamos que los campos necesarios estén
    if not data or 'nombre' not in data or 'id_negocio' not in data:
        return jsonify({"error": "Datos incompletos: 'nombre' y 'id_negocio' son requeridos"}), 400 # 400 = Bad Request

    # Validamos si el negocio existe
    negocio_id = data['id_negocio']
    if not Negocio.query.get(negocio_id):
        return jsonify({"error": f"El negocio con id {negocio_id} no existe"}), 404 # 404 = Not Found
        
    try:
        # Creamos la nueva instancia del objeto Cliente
        nuevo_cliente = Cliente(
            nombre=data['nombre'],
            telefono=data.get('telefono'), # .get() es seguro, devuelve None si no existe
            id_negocio=negocio_id
        )
        
        # Añadimos el nuevo cliente a la sesión de la base de datos
        db.session.add(nuevo_cliente)
        # Hacemos "commit" para guardar los cambios permanentemente
        db.session.commit()
        
        # Devolvemos el cliente recién creado (con su nuevo ID)
        return jsonify(nuevo_cliente.serialize()), 201 # 201 = Created
    except Exception as e:
        db.session.rollback() # Revertimos los cambios si algo falla
        return jsonify({"error": f"Error al crear el cliente: {str(e)}"}), 500
