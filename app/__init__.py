import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_map 

# Inicializa la extensión de la base de datos
db = SQLAlchemy()

def create_app(config_name='development'):
    """Función de fábrica para crear la aplicación Flask."""
    
    # 1. Inicializar la instancia de Flask
    app = Flask(__name__, instance_relative_config=True) 
    
    # 2. Cargar Configuración
    # Usa la configuración definida en config.py basada en el entorno (development/production)
    app.config.from_object(config_map[config_name])
    
    # 3. Inicializar Extensiones
    db.init_app(app)
    
    # 4. Asegurar que los directorios existan
    # Aseguramos que 'instance' y 'logs' existan dentro del contenedor
    if not os.path.isdir(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.isdir(os.path.join(os.getcwd(), 'logs')):
        os.makedirs(os.path.join(os.getcwd(), 'logs'))

    # 5. Configurar Logging
    setup_logging(app)
    
    # 6. Registrar Blueprints (Rutas y Funcionalidad)
    from . import routes
    app.register_blueprint(routes.bp_api)
    app.register_blueprint(routes.bp_dashboard)
    
    # 7. Registrar Modelos
    from . import models # Esto asegura que los modelos de SQLAlchemy se carguen
    
    # 8. Creación Inicial de la Base de Datos
    with app.app_context():
        # Crea las tablas si no existen (solo se debe hacer una vez o en desarrollo)
        db.create_all() 
    
    return app

def setup_logging(app):
    """Configura el sistema de logging de la aplicación."""
    # Usaremos el manejador de archivos rotativo para el log
    if not app.debug:
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE_PATH'], 
            maxBytes=10240, # 10 KB de límite por archivo de log
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Sensor Server Startup')