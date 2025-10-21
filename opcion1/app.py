import mysql.connector
from flask import Flask, request, jsonify

# ----------------------------------------------------------------------------
# 1. FLASK APP INITIALIZATION
# ----------------------------------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------------------------------
# 2. DATABASE CONFIGURATION
# IMPORTANT: Replace these placeholders with your actual MySQL credentials.
# ----------------------------------------------------------------------------
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_database_name' # Ensure 'profesionales' table exists here
}

def get_db_connection():
    """Establishes a connection to the database and returns the connection object."""
    try:
        # We use a global variable 'db' to match your original snippet's variable name.
        db = mysql.connector.connect(**DATABASE_CONFIG)
        return db
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# ----------------------------------------------------------------------------
# 3. API ROUTES (CRUD OPERATIONS for 'profesionales')
# ----------------------------------------------------------------------------

@app.route('/api/profesionales', methods=['GET'])
def get_profesionales():
    """Retrieves all professionals from the database."""
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesionales")
        profesionales = cursor.fetchall()
        return jsonify(profesionales)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.route('/api/profesionales', methods=['POST'])
def add_profesional():
    """Adds a new professional to the database."""
    data = request.get_json()
    # Basic input validation
    if not data or 'nombre' not in data or 'especialidad' not in data:
        return jsonify({"mensaje": "Datos incompletos (requiere 'nombre' y 'especialidad')"}), 400

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = db.cursor()
        query = "INSERT INTO profesionales (nombre, especialidad) VALUES (%s, %s)"
        cursor.execute(query, (data['nombre'], data['especialidad']))
        db.commit()
        return jsonify({"mensaje": "Profesional agregado", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": f"Database insertion failed: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.route('/api/profesionales/<int:id>', methods=['PUT'])
def update_profesional(id):
    """Updates an existing professional by ID."""
    data = request.get_json()
    if not data or 'nombre' not in data or 'especialidad' not in data:
        return jsonify({"mensaje": "Datos incompletos (requiere 'nombre' y 'especialidad')"}), 400

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = db.cursor()
        query = "UPDATE profesionales SET nombre=%s, especialidad=%s WHERE id=%s"
        cursor.execute(query, (data['nombre'], data['especialidad'], id))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"mensaje": f"No se encontró profesional con ID {id}"}), 404

        return jsonify({"mensaje": f"Profesional con ID {id} actualizado"})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": f"Database update failed: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.route('/api/profesionales/<int:id>', methods=['DELETE'])
def delete_profesional(id):
    """Deletes a professional by ID."""
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM profesionales WHERE id=%s", (id,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"mensaje": f"No se encontró profesional con ID {id}"}), 404

        return jsonify({"mensaje": f"Profesional con ID {id} eliminado"})
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": f"Database deletion failed: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# ----------------------------------------------------------------------------
# 4. RUNNING THE APPLICATION
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    # You can change the port if needed, e.g., app.run(debug=True, port=5001)
    # Note: 'debug=True' should be removed in production environments.
    app.run(debug=True)
