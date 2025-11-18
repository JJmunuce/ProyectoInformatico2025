from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SECRET_KEY'] = 'app_123'

import api.routes.Login
import api.routes.cliente_routes
import api.routes.negocio_routes
import api.routes.profesional_routes
import api.routes.usuario_routes
import api.routes.servicio_routes
import api.routes.turno_routes