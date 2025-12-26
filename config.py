import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Clase base de configuración que obtiene valores del entorno."""
    
    # 1. Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-dificil'
    # Forzamos una ruta absoluta en el directorio /data
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'sensors.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 3. Logging y Rutas
    # Define la ruta del archivo de logs dentro del contenedor
    LOG_FILE_PATH = os.path.join(basedir, 'logs', 'app.log')
    
    # 4. Configuración de la API
    # Puede ser útil para limitar datos en el dashboard
    MAX_SENSOR_READINGS = 1000 
    
class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuración para el entorno de producción."""
    DEBUG = False
    FLASK_ENV = 'production'
    # Considerar rutas de logs más seguras o rotación
    
# Mapeo para cargar la configuración basada en el entorno
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}