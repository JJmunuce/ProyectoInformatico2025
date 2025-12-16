from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
CORS(app)

# Configuración MySQL (Recomendación: usar variables de entorno)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'proyecto')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'proyecto')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'turnos')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Clave secreta
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_super_secreta_desarrollo')
app.config['ADMIN_SECRET'] = os.environ.get('ADMIN_SECRET', 'dev_admin_secret')

mysql = MySQL(app)

# Importación de rutas 
import api.routes.negocio_routes
import api.routes.cliente_routes
import api.routes.servicio_routes
import api.routes.profesional_routes
import api.routes.usuario_routes
import api.routes.disponibilidad_routes
import api.routes.turno_routes
import api.routes.auth_routes # <--- Nueva ruta de autenticación