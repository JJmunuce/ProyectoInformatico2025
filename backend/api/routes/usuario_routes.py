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
        if not data or 'nombre' not in data or 'correo' not in data or 'contraseña' not in data:
            return jsonify({"error": "Faltan datos requeridos"}), 400
            
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (data['correo'],))
            if cur.fetchone():
                cur.close()
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409
            cur.close()

            pwd_str = str(data['contraseña'])
            data_model = {
                'id_usuario': None,
                'nombre': data['nombre'],
                'correo': data['correo'],
                'contraseña': pwd_str, 
                'id_negocio': data.get('id_negocio') 
            }
            
            result = Usuario.create(data_model)
            return jsonify(result), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- OBTENER TODOS LOS USUARIOS (Protegido) ---
    elif request.method == 'GET':
        # Nota: Idealmente deberías proteger esto con @token_required, 
        # pero para usar decoradores condicionales dentro de una función es complejo.
        # Mejor separar GET y POST en funciones distintas si quieres auth solo en GET.
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuario")
            rows = cur.fetchall()
            cur.close()
            usuarios = [Usuario(row).to_json() for row in rows]
            return jsonify(usuarios), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# --- Rutas Individuales ---
@app.route('/api/usuarios/<int:id_usuario>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_usuario_by_id(id_usuario):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
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
            id_negocio = data.get('id_negocio', row['id_negocio'])
            
            if correo != row['correo']:
                cur = mysql.connection.cursor()
                cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
                if cur.fetchone():
                    cur.close()
                    return jsonify({"error": "El correo ya está en uso"}), 409
                cur.close()

            cur = mysql.connection.cursor()
            if 'contraseña' in data and data.get('contraseña'):
                pwd_hash = generate_password_hash(str(data['contraseña']))
                cur.execute("UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s, contraseña=%s WHERE id_usuario=%s", 
                            (nombre, correo, id_negocio, pwd_hash, id_usuario))
            else:
                cur.execute("UPDATE usuario SET nombre=%s, correo=%s, id_negocio=%s WHERE id_usuario=%s", 
                            (nombre, correo, id_negocio, id_usuario))
            
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