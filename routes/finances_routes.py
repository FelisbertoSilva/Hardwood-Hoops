import sys
import os
import sqlite3
from flask import Blueprint, render_template, request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

finances_bp = Blueprint('finances', __name__)

# Salários 2025/26 season
SALARY_CAP = 154647000  
HARD_CAP = 216505800  

TEAMS = [
    'Atlanta Hawks', 'Boston Celtics', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
    'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers',
    'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks',
    'Minnesota Timberwolves', 'Montreal Mastodons', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
    'Portland Trailblazers', 'Sacramento Kings', 'San Diego Caravels',
    'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
]


def get_db_connection():
    """Create a database connection"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_team_contracts(team_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, rating, birds,
               ct1, ct2, ct3, ct4, ct5,
               ct1c, ct2c, ct3c, ct4c, ct5c
        FROM players
        WHERE team = ?
        ORDER BY
            CASE WHEN birds > 0 THEN 0 ELSE 1 END,
            rating DESC,
            ct1 DESC
    """, (team_name,))

    players = cursor.fetchall()
    conn.close()

    result = []
    for player in players:
        contracts = []
        has_contract = False
        for i in range(5):
            ct_val = player[3 + i]   
            ctc_val = player[8 + i]   

            contracts.append((ct_val, ctc_val)) #Não mexer


            if ct_val:
                has_contract = True

        if has_contract:
            result.append({
                'name': player[0],
                'rating': player[1],
                'birds': player[2],
                'contracts': contracts
            })

    return result


def calculate_team_totals(players):
    totals = [0, 0, 0, 0, 0]

    for player in players:
        for i, (amount, code) in enumerate(player['contracts']):
            if amount:
                totals[i] += amount

    return totals


def format_salary(amount):
    if amount is None or amount == 0:
        return ""
    return f"${amount:,.0f}"


def format_salary_diff(amount, cap):
    diff = cap - amount
    if diff >= 0:
        return f"${diff:,.0f}"
    else:
        return f"-${abs(diff):,.0f}"


@finances_bp.route('/finances')
@finances_bp.route('/finances/<team_name>')
def finances_page(team_name=None):

    if not team_name:
        team_name = 'Atlanta Hawks'

    players = get_team_contracts(team_name)
    totals = calculate_team_totals(players)

    salary_cap_diff = SALARY_CAP - totals[0] if totals[0] else SALARY_CAP
    hard_cap_diff = HARD_CAP - totals[0] if totals[0] else HARD_CAP

    return render_template('finances.html',
                           team_name=team_name,
                           teams=TEAMS,
                           players=players,
                           totals=totals,
                           salary_cap=SALARY_CAP,
                           hard_cap=HARD_CAP,
                           salary_cap_diff=salary_cap_diff,
                           hard_cap_diff=hard_cap_diff,
                           format_salary=format_salary,
                           format_salary_diff=format_salary_diff)