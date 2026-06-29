# Servidor de sensores IoT (Flask + SQLite)

## Requisitos

- Python **3.11 o 3.12** recomendado (3.14 funciona con SQLAlchemy >= 2.0.40)
- Si `pip install` falla con pandas: ya fue eliminado del proyecto (no se usa)

## Instalación rápida (Windows / PC de desarrollo)

```powershell
cd "IOT\codigo inicial\node_server"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\seed_admin.py
python run.py
```

Abre en el navegador:

- Login: http://localhost:8000/auth/login
- Dashboard: http://localhost:8000/
- Admin: http://localhost:8000/admin/

Credenciales por defecto (`.env`):

- Email: `admin@agro.local`
- Contraseña: `admin1234`

## Probar envío de sensor (PowerShell)

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/sensor-data" -Method POST `
  -Headers @{"X-API-KEY"="mi_clave_secreta_123"; "Content-Type"="application/json"} `
  -Body '{"sensor_id":"nodo_maceta_01","t_dht":3.5,"h_dht":70,"h_gnd":25,"light":900}'
```

Si `t_dht` es menor a 5, se creará una alerta de helada.

## Endpoints

| Ruta | Auth | Uso |
|------|------|-----|
| `POST /api/sensor-data` | API key | ESP32 envía lecturas |
| `GET /api/readings` | Login | Dashboard consulta JSON |
| `GET /` | Login | Dashboard web |
| `GET /admin/` | Admin | Panel administración |
| `GET/POST /auth/login` | Público | Inicio de sesión |

## Base de datos

Archivo SQLite: `instance/sensors.db`

Tablas: `users`, `zones`, `nodes`, `sensor_readings`, `alert_rules`, `alerts`, `audit_log`, `user_zones`.

Ver diseño en `../../esquema-base-datos.md`.
