from datetime import datetime

from . import db
from .models import Alert, AlertRule, Node, SensorReading


def resolve_node(sensor_id):
    """Vincula una lectura al nodo registrado y actualiza last_seen."""
    node = Node.query.filter_by(node_code=sensor_id, active=True).first()
    if node:
        node.last_seen = datetime.utcnow()
    return node


def evaluate_alert_rules(reading):
    """Evalúa reglas activas de la zona del nodo tras guardar una lectura."""
    if not reading.node_id:
        return []

    node = Node.query.get(reading.node_id)
    if not node:
        return []

    rules = AlertRule.query.filter_by(zone_id=node.zone_id, active=True).all()
    triggered = []

    for rule in rules:
        value = reading.payload.get(rule.variable)
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if not _matches_rule(value, rule.operator, rule.threshold):
            continue

        alert = Alert(
            rule_id=rule.id,
            node_id=node.id,
            value=value,
        )
        db.session.add(alert)
        triggered.append(alert)

    if triggered:
        db.session.commit()

    return triggered


def _matches_rule(value, operator, threshold):
    if operator == '<':
        return value < threshold
    if operator == '<=':
        return value <= threshold
    if operator == '>':
        return value > threshold
    if operator == '>=':
        return value >= threshold
    if operator == '==':
        return value == threshold
    return False


def readings_query_for_user(user):
    """Filtra lecturas según rol y zonas asignadas."""
    query = SensorReading.query.order_by(SensorReading.timestamp.desc())

    if user.is_admin:
        return query

    zone_ids = [zone.id for zone in user.zones]
    if not zone_ids:
        return query.filter(SensorReading.id == -1)

    node_ids = [
        node.id
        for node in Node.query.filter(Node.zone_id.in_(zone_ids), Node.active.is_(True)).all()
    ]
    if not node_ids:
        return query.filter(SensorReading.id == -1)

    return query.filter(SensorReading.node_id.in_(node_ids))
