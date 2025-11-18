from flask import Blueprint, jsonify, request
from ..models import Usuario, db
from werkzeug.security import generate_password_hash, check_password_hash
# (Necesitarás instalar werkzeug: pip install werkzeug)

usuarios_bp = Blueprint('usuarios_bp', __name__)


# --- Rutas para /api/usuarios (Lista y Crear) ---
@usuarios_bp.route('/usuarios', methods=['GET', 'POST'])
def handle_usuarios():
    
    # --- CREAR UN NUEVO USUARIO (POST) ---
    if request.method == 'POST':
        data = request.json
        if not data or 'nombre' not in data or 'correo' not in data or 'contrasena' not in data or 'id_negocio' not in data:
            return jsonify({"error": "'nombre', 'correo', 'contrasena' y 'id_negocio' son requeridos"}), 400
            
        # Revisar si el correo ya existe
        if Usuario.query.filter_by(correo=data['correo']).first():
            return jsonify({"error": "El correo electrónico ya está en uso"}), 409 # 409 Conflict
            
        try:
            # Hashear la contraseña ANTES de guardarla
            hashed_password = generate_password_hash(data['contrasena'])
            
            nuevo_usuario = Usuario(
                nombre=data['nombre'],
                correo=data['correo'],
                contrasena_hash=hashed_password, # Guardamos el hash, no la contraseña
                id_negocio=data['id_negocio']
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Devolvemos el usuario serializado (el modelo NO debe serializar la contraseña)
            return jsonify(nuevo_usuario.serialize()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS USUARIOS (GET) ---
    if request.method == 'GET':
        try:
            usuarios = Usuario.query.all()
            return jsonify([usuario.serialize() for usuario in usuarios]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/usuarios/<id> (Uno Específico) ---
@usuarios_bp.route('/usuarios/<int:id_usuario>', methods=['GET', 'PUT', 'DELETE'])
def handle_usuario_by_id(id_usuario):
    
    # Usamos get_or_404 para buscar al usuario o devolver 404 si no existe
    usuario = Usuario.query.get_or_404(id_usuario, description="Usuario no encontrado")

    # --- OBTENER UN USUARIO (GET por ID) ---
    if request.method == 'GET':
        return jsonify(usuario.serialize()), 200

    # --- ACTUALIZAR UN USUARIO (PUT) ---
    if request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos para actualizar"}), 400
        
        # Actualizamos los campos
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.id_negocio = data.get('id_negocio', usuario.id_negocio)
        
        # Manejo especial para el correo (verificar duplicados)
        if 'correo' in data and data['correo'] != usuario.correo:
            if Usuario.query.filter_by(correo=data['correo']).first():
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409
            usuario.correo = data['correo']
            
        # Manejo especial para la contraseña
        if 'contrasena' in data:
            usuario.contrasena_hash = generate_password_hash(data['contrasena'])
            
        try:
            db.session.commit()
            return jsonify(usuario.serialize()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # --- BORRAR UN USUARIO (DELETE) ---
    if request.method == 'DELETE':
        try:
            db.session.delete(usuario)
            db.session.commit()
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


# --- Ruta de Autenticación (Login) ---
@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'correo' not in data or 'contrasena' not in data:
        return jsonify({"error": "Faltan 'correo' o 'contrasena'"}), 400
        
    usuario = Usuario.query.filter_by(correo=data['correo']).first()
    
    # Verificamos si el usuario existe Y si la contraseña es correcta
    if not usuario or not check_password_hash(usuario.contrasena_hash, data['contrasena']):
        return jsonify({"error": "Credenciales inválidas"}), 401 # 401 Unauthorized
        
    # En un caso real, aquí generarías un Token (JWT)
    # Por ahora, solo confirmamos el éxito
    
    return jsonify({
        "mensaje": "Login exitoso",
        "usuario": usuario.serialize()
    }), 200
