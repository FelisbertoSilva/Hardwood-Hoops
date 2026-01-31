import sys
import os
import sqlite3
from flask import Blueprint, render_template

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

draft_bp = Blueprint('draft', __name__)

TEAM_ABBREVS = {
    'Atlanta Hawks': 'ATL',
    'Boston Celtics': 'BOS',
    'Charlotte Hornets': 'CHA',
    'Chicago Bulls': 'CHI',
    'Cleveland Cavaliers': 'CLE',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'Montreal Mastodons': 'MTL',
    'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHX',
    'Portland Trailblazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Diego Caravels': 'SDC',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS'
}

TEAM_COLORS = {
    'Atlanta Hawks': '#E03A3E',
    'Boston Celtics': '#007A33',
    'Charlotte Hornets': '#1D1160',
    'Chicago Bulls': '#CE1141',
    'Cleveland Cavaliers': '#860038',
    'Dallas Mavericks': '#00538C',
    'Denver Nuggets': '#0E2240',
    'Detroit Pistons': '#C8102E',
    'Golden State Warriors': '#1D428A',
    'Houston Rockets': '#CE1141',
    'Indiana Pacers': '#002D62',
    'Los Angeles Clippers': '#C8102E',
    'Los Angeles Lakers': '#552583',
    'Memphis Grizzlies': '#5D76A9',
    'Miami Heat': '#98002E',
    'Milwaukee Bucks': '#00471B',
    'Minnesota Timberwolves': '#0C2340',
    'Montreal Mastodons': '#4A90D9',
    'New Orleans Pelicans': '#0C2340',
    'New York Knicks': '#006BB6',
    'Oklahoma City Thunder': '#007AC1',
    'Orlando Magic': '#0077C0',
    'Philadelphia 76ers': '#006BB6',
    'Phoenix Suns': '#1D1160',
    'Portland Trailblazers': '#E03A3E',
    'Sacramento Kings': '#5A2D81',
    'San Diego Caravels': '#00A7E1',
    'Toronto Raptors': '#CE1141',
    'Utah Jazz': '#002B5C',
    'Washington Wizards': '#002B5C'
}


def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_draft_picks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team,
               "1Y26", "1Y26C", "2Y26", "2Y26C",
               "1Y27", "1Y27C", "2Y27", "2Y27C",
               "1Y28", "1Y28C", "2Y28", "2Y28C",
               "1Y29", "1Y29C", "2Y29", "2Y29C"
        FROM draft_picks
        ORDER BY team
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            'team': row['team'],
            'picks': {
                '1Y26': {'owner': row['1Y26'], 'condition': row['1Y26C']},
                '2Y26': {'owner': row['2Y26'], 'condition': row['2Y26C']},
                '1Y27': {'owner': row['1Y27'], 'condition': row['1Y27C']},
                '2Y27': {'owner': row['2Y27'], 'condition': row['2Y27C']},
                '1Y28': {'owner': row['1Y28'], 'condition': row['1Y28C']},
                '2Y28': {'owner': row['2Y28'], 'condition': row['2Y28C']},
                '1Y29': {'owner': row['1Y29'], 'condition': row['1Y29C']},
                '2Y29': {'owner': row['2Y29'], 'condition': row['2Y29C']},
            }
        })

    return result


def get_abbrev(team_name):
    return TEAM_ABBREVS.get(team_name, team_name[:3].upper() if team_name else '')


def get_color(team_name):
    return TEAM_COLORS.get(team_name, '#888888')


@draft_bp.route('/draft-rights')
def draft_rights_page():
    draft_data = get_all_draft_picks()

    return render_template('draft_rights.html',
                           draft_data=draft_data,
                           get_abbrev=get_abbrev,
                           get_color=get_color,
                           team_abbrevs=TEAM_ABBREVS)
