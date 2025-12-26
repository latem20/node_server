from . import db
from datetime import datetime

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), nullable=False, index=True)
    # Columna JSON para guardar N variables sin límites
    payload = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "data": self.payload,
            "timestamp": self.timestamp.isoformat()
        }