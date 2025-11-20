from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
# Habilitar CORS para todas las rutas
CORS(app)

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'proyecto'
app.config['MYSQL_PASSWORD'] = 'proyecto' 
app.config['MYSQL_DB'] = 'turnos'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecreto_dev_fallback')

mysql = MySQL(app)

# Importación de rutas 
import api.routes.negocio_routes
import api.routes.cliente_routes
import api.routes.servicio_routes
import api.routes.profesional_routes
import api.routes.usuario_routes
import api.routes.disponibilidad_routes
import api.routes.turno_routes
