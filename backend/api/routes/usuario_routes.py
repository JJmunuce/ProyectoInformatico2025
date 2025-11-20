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
        if not data or 'nombre' not in data or 'correo' not in data or 'contraseña' not in data:
            return jsonify({"error": "Faltan datos: 'nombre', 'correo' y 'contraseña' son requeridos"}), 400
            
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (data['correo'],))
            if cur.fetchone():
                cur.close()
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409
            cur.close()

            # Convertir contraseña a string explícitamente para evitar errores de tipo
            pwd_str = str(data['contraseña'])

            data_model = {
                'id_usuario': None,
                'nombre': data['nombre'],
                'correo': data['correo'],
                'contraseña': pwd_str, 
                'id_negocio': data.get('id_negocio') 
            }
            
            # Crear usuario usando el modelo (el modelo se encarga del hash)
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
            usuarios = [Usuario(row).to_json() for row in rows]
            return jsonify(usuarios), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# --- Rutas para /api/usuarios/<id> (Operaciones Individuales) ---
@app.route('/api/usuarios/<int:id_usuario>', methods=['GET', 'PUT', 'DELETE'])
def handle_usuario_by_id(id_usuario):
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario_obj = Usuario(row)

        # --- GET ---
        if request.method == 'GET':
            return jsonify(usuario_obj.to_json()), 200

        # --- PUT ---
        if request.method == 'PUT':
            data = request.json
            nombre = data.get('nombre', row['nombre'])
            correo = data.get('correo', row['correo'])
            id_negocio = data.get('id_negocio', row['id_negocio'])
            
            if correo != row['correo']:
                cur = mysql.connection.cursor()
                cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
                if cur.fetchone():
                    cur.close()
                    return jsonify({"error": "El correo ya está en uso"}), 409
                cur.close()

            cur = mysql.connection.cursor()
            
            if 'contrasena' in data and data['contraseña']:
                # Convertir a string antes de hashear
                pwd_hash = generate_password_hash(str(data['contraseña']))
                cur.execute("""
                    UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s, contraseña=%s 
                    WHERE id_usuario=%s
                """, (nombre, correo, id_negocio, pwd_hash, id_usuario))
            else:
                cur.execute("""
                    UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s 
                    WHERE id_usuario=%s
                """, (nombre, correo, id_negocio, id_usuario))
            
            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200

        # --- DELETE ---
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
    data = request.get_json(silent=True)
    
    username = ""
    password = ""

    if data and 'username' in data and 'password' in data:
        username = data['username'] 
        # Aseguramos que la contraseña que llega sea string
        password = str(data['password']) 
    elif request.authorization:
        username = request.authorization.username
        password = str(request.authorization.password)
    else:
        return jsonify({"message": "Credenciales no proporcionadas"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if not user_data:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

        # --- DEBUG (Opcional, puedes borrarlo luego) ---
        print(f"DEBUG -> Hash en BD tipo: {type(user_data['contraseña'])}")
        
        # --- SOLUCIÓN 1: Bytes a String (DB) ---
        password_hash = user_data['contraseña']
        if isinstance(password_hash, bytes):
            password_hash = password_hash.decode('utf-8')

        # Verificar Contraseña
        if check_password_hash(password_hash, password):
            print("DEBUG -> ¡LOGIN EXITOSO!")
            usuario_obj = Usuario(user_data)
            resp_json = usuario_obj.to_json()
            
            # --- SOLUCIÓN 2: Clave Secreta Segura para JWT ---
            # Intentamos obtener la clave de la config, si falla usamos una por defecto
            secret_key = app.config.get('SECRET_KEY', 'clave_super_secreta_por_defecto')
            
            # Aseguramos que la clave sea un string (esto arregla el error del Token)
            if not isinstance(secret_key, str):
                secret_key = str(secret_key)

            # Generamos el token
            token = jwt.encode({
                'id_usuario': user_data['id_usuario'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
            }, secret_key, algorithm="HS256")
            
            # Compatibilidad PyJWT (si devuelve bytes, lo pasamos a str)
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            resp_json['token'] = token
            
            return jsonify(resp_json), 200
        else:
            return jsonify({"message": "Usuario o contraseña incorrectos"}), 401

    except Exception as ex:
        print("ERROR CRÍTICO LOGIN:", ex)
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error interno del servidor: ' + str(ex)}), 500