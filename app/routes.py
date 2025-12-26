from flask import Blueprint, jsonify, request, render_template, current_app
from . import db
from .models import SensorReading
import os

bp_api = Blueprint('api', __name__, url_prefix='/api')
bp_dashboard = Blueprint('dashboard', __name__)

@bp_api.route('/sensor-data', methods=['POST'])
def receive_data():
    # 1. Verificar la API KEY
    api_key = request.headers.get('X-API-KEY')
    if api_key != os.getenv('SENSOR_API_KEY'):
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    if not data or 'sensor_id' not in data:
        return jsonify({"error": "Falta sensor_id"}), 400

    s_id = data.pop('sensor_id') 
    
    try:
        new_reading = SensorReading(sensor_id=s_id, payload=data)
        db.session.add(new_reading)
        db.session.commit()
        return jsonify({"status": "recibido", "sensor": s_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- RUTA ÚNICA PARA OBTENER DATOS ---
@bp_api.route('/readings')
def get_readings():
    """Retorna las últimas 200 lecturas para alimentar la gráfica y tabla."""
    # Aumentamos el límite a 200 para que el selector 'Últimos 50/100' funcione
    readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(200).all()
    
    output = []
    for r in readings:
        output.append({
            "timestamp": r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_id": r.sensor_id,
            "payload": r.payload 
        })
    return jsonify(output)

@bp_dashboard.route('/')
def index():
    # Carga inicial para el renderizado del template
    readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(50).all()
    return render_template('index.html', readings=readings)