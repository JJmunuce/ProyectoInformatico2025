from api import app, mysql
from flask import jsonify, request
from api.models.usuario import Usuario
from werkzeug.security import generate_password_hash
from api.utils import token_required

# --- Rutas para /api/usuarios (Lista y Crear) ---
@app.route('/api/usuarios', methods=['GET', 'POST'])
def handle_usuarios():
    
    # --- CREAR UN NUEVO USUARIO (Registro público) ---
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # CORRECCIÓN 1: Flexibilidad de nombres (acepta inglés y español)
        nombre = data.get('nombre')
        correo = data.get('correo') or data.get('email')
        raw_password = data.get('contraseña') or data.get('password')

        if not nombre or not correo or not raw_password:
            return jsonify({"error": "Faltan datos requeridos (nombre, correo, password)"}), 400
            
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
            if cur.fetchone():
                cur.close()
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409
            cur.close()

            # CORRECCIÓN 2: ENCRIPTAR LA CONTRASEÑA ANTES DE GUARDAR
            pwd_hash = generate_password_hash(str(raw_password))
            
            data_model = {
                'id_usuario': None,
                'nombre': nombre,
                'correo': correo,
                'contraseña': pwd_hash,  # Guardamos el HASH, no el texto plano
                'id_negocio': data.get('id_negocio') 
            }
            
            # Usamos el modelo para insertar
            # Nota: Asegúrate de que Usuario.create usa estos campos correctamente
            # Si Usuario.create hace el INSERT manual, pasamos el hash ahí.
            result = Usuario.create(data_model)
            return jsonify(result), 201

        except Exception as e:
            print(f"Error en registro: {e}")
            return jsonify({"error": str(e)}), 500

    # --- OBTENER USUARIOS (Protegido) ---
    elif request.method == 'GET':
        return get_usuarios_protegido()

# Función auxiliar para manejar el decorador en el GET
@token_required
def get_usuarios_protegido(current_user):
    try:
        # Solo devuelve usuarios del negocio del administrador
        if not current_user['id_negocio']:
            return jsonify([]), 200
        return jsonify(Usuario.get_all(current_user['id_negocio'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Rutas Individuales ---
@app.route('/api/usuarios/<int:id_usuario>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_usuario_by_id(current_user, id_usuario):
    try:
        cur = mysql.connection.cursor()
        # Seguridad: Solo acceder si pertenece al mismo negocio
        cur.execute("SELECT * FROM usuario WHERE id_usuario = %s AND id_negocio = %s", 
                    (id_usuario, current_user['id_negocio']))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario_obj = Usuario(row)

        if request.method == 'GET':
            return jsonify(usuario_obj.to_json()), 200

        if request.method == 'PUT':
            data = request.json
            nombre = data.get('nombre', row['nombre'])
            correo = data.get('correo', row['correo'])
            
            if correo != row['correo']:
                cur = mysql.connection.cursor()
                cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
                if cur.fetchone():
                    cur.close()
                    return jsonify({"error": "El correo ya está en uso"}), 409
                cur.close()

            cur = mysql.connection.cursor()
            # Si envían nueva contraseña, la encriptamos
            new_pass = data.get('contraseña') or data.get('password')
            if new_pass:
                pwd_hash = generate_password_hash(str(new_pass))
                cur.execute("UPDATE usuario SET nombre=%s, correo=%s, contraseña=%s WHERE id_usuario=%s", 
                            (nombre, correo, pwd_hash, id_usuario))
            else:
                cur.execute("UPDATE usuario SET nombre=%s, correo=%s WHERE id_usuario=%s", 
                            (nombre, correo, id_usuario))
            
            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200

        if request.method == 'DELETE':
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500