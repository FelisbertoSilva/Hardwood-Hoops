from flask import Blueprint, render_template
from stats.records_calculations import get_all_records

records_bp = Blueprint('records', __name__)


@records_bp.route('/records')
def records_page():

    records = get_all_records()

    return render_template('records.html',
                           awards=records['awards'],
                           single_game=records['single_game'],
                           career=records['career'],
                           playoff_single_game=records['playoff_single_game'],
                           playoff_career=records['playoff_career'],
                           team_season=records['team_season'],
                           team_streaks=records['team_streaks'])
