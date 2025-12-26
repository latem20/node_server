import os
import shutil
import time
from datetime import datetime

def clean_old_backups(backup_dir, days_to_keep=7):
    """Borra archivos que superen los 7 días de antigüedad."""
    now = time.time()
    cutoff = now - (days_to_keep * 86400)

    if not os.path.exists(backup_dir):
        return

    files = os.listdir(backup_dir)
    for file in files:
        file_path = os.path.join(backup_dir, file)
        if os.path.isfile(file_path) and file.startswith("sensors_backup_"):
            file_time = os.path.getmtime(file_path)
            if file_time < cutoff:
                try:
                    os.remove(file_path)
                    print(f"🗑️ Backup antiguo eliminado: {file}")
                except Exception as e:
                    print(f"⚠️ No se pudo borrar {file}: {e}")

def run_backup():
    # --- RUTAS FIJAS PARA DOCKER ---
    DB_PATH = '/usr/src/app/instance/sensors.db'
    BACKUP_DIR = '/usr/src/app/backups'
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"sensors_backup_{timestamp}.db"
    dest_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, dest_path)
            print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Backup creado: {backup_filename}")
            
            # Limpieza de archivos viejos
            clean_old_backups(BACKUP_DIR, days_to_keep=7)
            return True
        else:
            print(f"❌ Error: No se encontró la DB en {DB_PATH}")
            return False
    except Exception as e:
        print(f"❌ Error en el backup: {str(e)}")
        return False

if __name__ == "__main__":
    run_backup()