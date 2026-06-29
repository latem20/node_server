from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

user_zones = db.Table(
    'user_zones',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('zone_id', db.Integer, db.ForeignKey('zones.id'), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, default='viewer')
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    zones = db.relationship('Zone', secondary=user_zones, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def can_access_zone(self, zone_id):
        if self.is_admin:
            return True
        return any(zone.id == zone_id for zone in self.zones)


class Zone(db.Model):
    __tablename__ = 'zones'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    nodes = db.relationship('Node', backref='zone', lazy='dynamic')


class Node(db.Model):
    __tablename__ = 'nodes'

    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False, index=True)
    node_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    label = db.Column(db.String(120))
    active = db.Column(db.Boolean, default=True, nullable=False)
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    readings = db.relationship('SensorReading', backref='node', lazy='dynamic')


class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(50), nullable=False, index=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), index=True)
    payload = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    synced = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'node_id': self.node_id,
            'data': self.payload,
            'timestamp': self.timestamp.isoformat(),
        }


class AlertRule(db.Model):
    __tablename__ = 'alert_rules'

    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False, index=True)
    variable = db.Column(db.String(50), nullable=False)
    operator = db.Column(db.String(10), nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), default='warning')
    message = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    zone = db.relationship('Zone', backref=db.backref('alert_rules', lazy='dynamic'))


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False, index=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    rule = db.relationship('AlertRule', backref=db.backref('alerts', lazy='dynamic'))
    node = db.relationship('Node', backref=db.backref('alerts', lazy='dynamic'))


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(80), nullable=False)
    entity = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('audit_entries', lazy='dynamic'))
