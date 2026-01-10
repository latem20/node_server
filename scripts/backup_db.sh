#!/bin/bash
# 1. Directorio de destino DENTRO del contenedor
BACKUP_DIR="/usr/src/app/backups"

# 2. MANTENEMOS el Timestamp para identificar cada backup por fecha/hora
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 3. Ruta a la base de datos DENTRO del contenedor
DB_PATH="/usr/src/app/instance/sensors.db"

# Crear carpeta si no existe
mkdir -p $BACKUP_DIR

# Hacer copia de seguridad
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/backup_$TIMESTAMP.db'"

# Borrar backups más viejos de 3 días (ajustado según tu código)
find $BACKUP_DIR -type f -name "*.db" -mtime +3 -delete

echo "Backup completado: backup_$TIMESTAMP.db"