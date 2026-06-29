from functools import wraps

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from .models import Alert, AlertRule, Node, User, Zone

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@bp_admin.route('/')
@login_required
@admin_required
def index():
    return render_template(
        'admin.html',
        users=User.query.order_by(User.created_at.desc()).all(),
        zones=Zone.query.order_by(Zone.name.asc()).all(),
        nodes=Node.query.order_by(Node.node_code.asc()).all(),
        rules=AlertRule.query.order_by(AlertRule.id.desc()).all(),
        alerts=Alert.query.order_by(Alert.triggered_at.desc()).limit(20).all(),
    )
