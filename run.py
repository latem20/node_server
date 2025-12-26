import os
from app import create_app

# 1. Obtener el entorno de configuración
config_name = os.environ.get('FLASK_ENV') or 'development'

# 2. Crear la aplicación
app = create_app(config_name)

# 3. Bloque para ejecución directa
if __name__ == '__main__':
    # Obtenemos el puerto
    port = int(os.environ.get('SERVER_PORT') or 8000)
    
    # --- LA LÍNEA CLAVE ES ESTA ---
    # host='0.0.0.0' permite acceso desde otros dispositivos (como el ESP32)
    # debug=True activa el reinicio automático al detectar cambios en archivos .py
    app.run(host='0.0.0.0', port=port, debug=True)