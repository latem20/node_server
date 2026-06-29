from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import current_user, login_required

from . import db
from .models import SensorReading
from .services import evaluate_alert_rules, readings_query_for_user, resolve_node
import os
import requests
from datetime import datetime
import pytz

bp_api = Blueprint('api', __name__, url_prefix='/api')
bp_dashboard = Blueprint('dashboard', __name__)


@bp_api.route('/sensor-data', methods=['POST'])
def receive_data():
    api_key = request.headers.get('X-API-KEY')
    if api_key != os.getenv('SENSOR_API_KEY'):
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    if not data or 'sensor_id' not in data:
        return jsonify({"error": "Falta sensor_id"}), 400

    s_id = data.get('sensor_id')

    local_payload = data.copy()
    local_payload.pop('sensor_id', None)

    try:
        node = resolve_node(s_id)
        new_reading = SensorReading(
            sensor_id=s_id,
            node_id=node.id if node else None,
            payload=local_payload,
            synced=False,
        )
        db.session.add(new_reading)
        db.session.commit()

        evaluate_alert_rules(new_reading)
        sincronizar_pendientes()

        return jsonify({"status": "recibido y procesando sincronización", "sensor": s_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def sincronizar_pendientes():
    """Busca registros no sincronizados e intenta enviarlos a Supabase."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return

    pendientes = SensorReading.query.filter_by(synced=False).order_by(SensorReading.timestamp.asc()).all()

    if not pendientes:
        return

    endpoint = f"{url}/rest/v1/lecturas_sensores"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    for lectura in pendientes:
        payload_nube = {
            "sensor_id": lectura.sensor_id,
            "temp_internal": lectura.payload.get('t_int'),
            "temp_ds18b20": lectura.payload.get('t_ds18'),
            "temp_dht11": lectura.payload.get('t_dht'),
            "hum_dht11": lectura.payload.get('h_dht'),
            "light_lvl": lectura.payload.get('light'),
            "ppmco_mq9": lectura.payload.get('co'),
            "ppmco2_mq135": lectura.payload.get('co2'),
            "hpa_bmp180": lectura.payload.get('pres'),
            "temp_bmp180": lectura.payload.get('t_bmp'),
            "alt_bmp180": lectura.payload.get('alt'),
            "hum_gnd": lectura.payload.get('h_gnd'),
        }

        try:
            response = requests.post(endpoint, json=payload_nube, headers=headers, timeout=3)

            if response.status_code in [200, 201]:
                lectura.synced = True
                db.session.commit()
                current_app.logger.info(f"Sincronizado id {lectura.id} a la nube")
            else:
                current_app.logger.error(
                    f"Fallo en id {lectura.id}: {response.status_code} - {response.text}"
                )
                break
        except Exception as e:
            current_app.logger.warning(f"Sin conexión a la nube. Acumulando datos... ({e})")
            break


@bp_api.route('/readings')
@login_required
def get_readings():
    is_render = os.getenv('RENDER') is not None
    ecuador_tz = pytz.timezone('America/Guayaquil')

    if is_render:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        endpoint = f"{url}/rest/v1/lecturas_sensores"
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

        try:
            params = {"select": "*", "order": "created_at.desc", "limit": "100"}
            response = requests.get(endpoint, headers=headers, params=params, timeout=5)
            supabase_data = response.json()

            output = []
            for r in supabase_data:
                raw_date = r.get('created_at')
                dt_utc = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                dt_ecuador = dt_utc.astimezone(ecuador_tz)

                output.append({
                    "timestamp": dt_ecuador.strftime('%Y-%m-%d %H:%M:%S'),
                    "sensor_id": r.get('sensor_id'),
                    "payload": {
                        "t_int": r.get('temp_internal'),
                        "t_ds18": r.get('temp_ds18b20'),
                        "t_dht": r.get('temp_dht11'),
                        "h_dht": r.get('hum_dht11'),
                        "co": r.get('ppmco_mq9'),
                        "co2": r.get('ppmco2_mq135'),
                        "light": r.get('light_lvl'),
                        "pres": r.get('hpa_bmp180'),
                        "t_bmp": r.get('temp_bmp180'),
                        "alt": r.get('alt_bmp180'),
                        "h_gnd": r.get('hum_gnd'),
                    },
                })
            return jsonify(output)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    readings = readings_query_for_user(current_user).limit(200).all()
    output = []
    for r in readings:
        dt_utc = r.timestamp.replace(tzinfo=pytz.utc) if r.timestamp.tzinfo is None else r.timestamp
        dt_ecuador = dt_utc.astimezone(ecuador_tz)
        output.append({
            "timestamp": dt_ecuador.strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_id": r.sensor_id,
            "payload": r.payload,
        })
    return jsonify(output)


@bp_dashboard.route('/')
@login_required
def index():
    readings = readings_query_for_user(current_user).limit(50).all()
    ecuador_tz = pytz.timezone('America/Guayaquil')

    for r in readings:
        if r.timestamp.tzinfo is None:
            r.timestamp = r.timestamp.replace(tzinfo=pytz.utc).astimezone(ecuador_tz)
        else:
            r.timestamp = r.timestamp.astimezone(ecuador_tz)

    return render_template('index.html', readings=readings)
