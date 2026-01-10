import os
from app import create_app
from app.routes import sincronizar_pendientes

# Forzamos entorno de producción para la tarea cron
app = create_app('production')

def force_sync():
    """Ejecuta la sincronización de datos pendientes sin esperar al ESP32."""
    with app.app_context():
        print(f"🔄 [{os.getpid()}] Iniciando sincronización forzada...")
        try:
            sincronizar_pendientes()
            print("✅ Proceso de sincronización finalizado.")
        except Exception as e:
            print(f"❌ Error en sincronización forzada: {e}")

if __name__ == "__main__":
    force_sync()