from flask import Blueprint, render_template

rules_bp = Blueprint('rules', __name__)


@rules_bp.route('/rules')
def rules_page():
    return render_template('rules.html')
