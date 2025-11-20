from api import app, mysql
from flask import jsonify, request
from api.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

# --- Rutas para /api/usuarios (Lista y Crear) ---
@app.route('/api/usuarios', methods=['GET', 'POST'])
def handle_usuarios():
    
    # --- CREAR UN NUEVO USUARIO (POST) ---
    if request.method == 'POST':
        data = request.json
        # Validación básica de campos obligatorios
        if not data or 'nombre' not in data or 'correo' not in data or 'contraseña' not in data:
            return jsonify({"error": "Faltan datos: 'nombre', 'correo' y 'contraseña' son requeridos"}), 400
            
        # Validar si el correo ya existe
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (data['correo'],))
            if cur.fetchone():
                cur.close()
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409
            cur.close()

            # Preparar datos para el modelo (mapeando 'contrasena' del front a 'contraseña' del modelo)
            # Nota: id_negocio puede ser None si es un cliente, usamos .get()
            data_model = {
                'id_usuario': None,
                'nombre': data['nombre'],
                'correo': data['correo'],
                'contraseña': data['contraseña'], # Se pasa cruda, el modelo la hashea
                'id_negocio': data.get('id_negocio') 
            }
            
            # Crear usuario usando el modelo
            result = Usuario.create(data_model)
            return jsonify(result), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS USUARIOS (GET) ---
    elif request.method == 'GET':
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuario")
            rows = cur.fetchall()
            cur.close()
            # Convertir filas a lista de diccionarios usando el modelo
            usuarios = [Usuario(row).to_json() for row in rows]
            return jsonify(usuarios), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/usuarios/<id> (Operaciones Individuales) ---
@app.route('/api/usuarios/<int:id_usuario>', methods=['GET', 'PUT', 'DELETE'])
def handle_usuario_by_id(id_usuario):
    
    try:
        # Verificar existencia del usuario
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario_obj = Usuario(row)

        # --- OBTENER UN USUARIO (GET) ---
        if request.method == 'GET':
            return jsonify(usuario_obj.to_json()), 200

        # --- ACTUALIZAR UN USUARIO (PUT) ---
        if request.method == 'PUT':
            data = request.json
            
            # Usar datos nuevos o mantener los actuales si no se envían
            nombre = data.get('nombre', row['nombre'])
            correo = data.get('correo', row['correo'])
            id_negocio = data.get('id_negocio', row['id_negocio'])
            
            # Validar correo duplicado solo si cambió
            if correo != row['correo']:
                cur = mysql.connection.cursor()
                cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
                if cur.fetchone():
                    cur.close()
                    return jsonify({"error": "El correo ya está en uso"}), 409
                cur.close()

            cur = mysql.connection.cursor()
            
            # Si envían contraseña nueva, hay que hashearla
            if 'contrasena' in data and data['contraseña']:
                pwd_hash = generate_password_hash(data['contraseña'])
                cur.execute("""
                    UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s, contraseña=%s 
                    WHERE id_usuario=%s
                """, (nombre, correo, id_negocio, pwd_hash, id_usuario))
            else:
                # Si no hay contraseña nueva, actualizamos el resto
                cur.execute("""
                    UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s 
                    WHERE id_usuario=%s
                """, (nombre, correo, id_negocio, id_usuario))
            
            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200

        # --- BORRAR UN USUARIO (DELETE) ---
        if request.method == 'DELETE':
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Ruta de Autenticación (Login) ---
@app.route('/login', methods=['POST'])
def login():
    # Intentar obtener JSON del cuerpo
    data = request.get_json(silent=True)
    
    username = ""
    password = ""

    # Soporte para JSON body (Recomendado)
    if data and 'username' in data and 'password' in data:
        username = data['username'] # El frontend envía el email en este campo
        password = data['password']
    # Fallback para Basic Auth (Header)
    elif request.authorization:
        username = request.authorization.username
        password = request.authorization.password
    else:
        return jsonify({"message": "Credenciales no proporcionadas"}), 400

    try:
        cur = mysql.connection.cursor()
        # Buscamos el usuario por correo
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if not user_data:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

        # Verificar la contraseña
        if check_password_hash(user_data['contraseña'], password):
            # Crear objeto usuario para estandarizar la respuesta
            usuario_obj = Usuario(user_data)
            resp_json = usuario_obj.to_json()
            
            # Generar Token JWT
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Asegurar que el token sea string (compatibilidad versiones PyJWT)
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            resp_json['token'] = token
            
            return jsonify(resp_json), 200
        else:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

    except Exception as ex:
        return jsonify({'message': 'Error interno del servidor: ' + str(ex)}), 500