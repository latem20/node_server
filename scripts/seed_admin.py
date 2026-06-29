#!/usr/bin/env python3
"""Crea datos iniciales: admin, zona piloto, nodo de prueba y reglas de alerta."""

import os
import sys

from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

load_dotenv()

from app import create_app, db
from app.models import AlertRule, Node, User, Zone


def seed():
    app = create_app(os.environ.get('FLASK_ENV') or 'development')

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@agro.local').strip().lower()
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin1234')
    admin_name = os.getenv('ADMIN_NAME', 'Administrador')

    zone_name = os.getenv('DEFAULT_ZONE_NAME', 'Macetas piloto')
    zone_location = os.getenv('DEFAULT_ZONE_LOCATION', 'Riobamba - pruebas locales')
    node_code = os.getenv('DEFAULT_NODE_CODE', 'nodo_maceta_01')
    node_label = os.getenv('DEFAULT_NODE_LABEL', 'Maceta 01')

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                full_name=admin_name,
                role='admin',
                active=True,
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f'Usuario admin creado: {admin_email}')
        else:
            print(f'Usuario admin ya existe: {admin_email}')

        zone = Zone.query.filter_by(name=zone_name).first()
        if not zone:
            zone = Zone(
                name=zone_name,
                location=zone_location,
                description='Zona inicial para pruebas en macetas',
                active=True,
            )
            db.session.add(zone)
            db.session.flush()
            print(f'Zona creada: {zone_name}')
        else:
            print(f'Zona ya existe: {zone_name}')

        node = Node.query.filter_by(node_code=node_code).first()
        if not node:
            node = Node(
                zone_id=zone.id,
                node_code=node_code,
                label=node_label,
                active=True,
            )
            db.session.add(node)
            print(f'Nodo creado: {node_code}')
        else:
            print(f'Nodo ya existe: {node_code}')

        if admin not in zone.users:
            zone.users.append(admin)

        rules = [
            ('t_dht', '<', 5.0, 'critical', 'Riesgo de helada: temperatura muy baja'),
            ('h_gnd', '<', 30.0, 'warning', 'Suelo seco: considerar riego'),
        ]

        for variable, operator, threshold, severity, message in rules:
            exists = AlertRule.query.filter_by(
                zone_id=zone.id,
                variable=variable,
                operator=operator,
                threshold=threshold,
            ).first()
            if exists:
                continue
            db.session.add(
                AlertRule(
                    zone_id=zone.id,
                    variable=variable,
                    operator=operator,
                    threshold=threshold,
                    severity=severity,
                    message=message,
                    active=True,
                )
            )
            print(f'Regla creada: {variable} {operator} {threshold}')

        db.session.commit()
        print('')
        print('Instalación inicial completada.')
        print(f'Login: {admin_email}')
        print('Contraseña: la definida en ADMIN_PASSWORD dentro de .env')
        print(f'Nodo ESP32 de prueba: {node_code}')


if __name__ == '__main__':
    seed()
