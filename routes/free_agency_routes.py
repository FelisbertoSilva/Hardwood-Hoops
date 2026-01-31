import sys
import os
import sqlite3
from flask import Blueprint, render_template

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

free_agency_bp = Blueprint('free_agency', __name__)


def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_current_free_agents():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, rating
        FROM players
        WHERE (team IS NULL OR team = '')
        AND name NOT LIKE '%(%'
        ORDER BY rating DESC NULLS LAST, name ASC
    """)

    players = cursor.fetchall()
    conn.close()

    result = []
    for player in players:
        result.append({
            'name': player['name'],
            'rating': player['rating']
        })

    return result


def get_upcoming_free_agents():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Upcoming free agents: players with only 1 year left (no ct2)
    cursor.execute("""
        SELECT name, team, rating, ct1
        FROM players
        WHERE ct1 > 0 AND (ct2 IS NULL OR ct2 = 0)
        AND team IS NOT NULL AND team != ''
        AND name NOT LIKE '%(%'
        ORDER BY rating DESC NULLS LAST, ct1 DESC
    """)
    upcoming_players = cursor.fetchall()

    # Players with options: have 2+ years, and ct2c indicates an option
    cursor.execute("""
        SELECT name, team, rating, ct2, ct2c
        FROM players
        WHERE ct1 > 0 AND ct2 > 0 AND ct2c IN (1, 2)
        AND team IS NOT NULL AND team != ''
        AND name NOT LIKE '%(%'
        ORDER BY rating DESC NULLS LAST, ct2 DESC
    """)
    option_players = cursor.fetchall()

    conn.close()

    upcoming = []
    player_options = []  # ct2c = 2
    team_options = []    # ct2c = 1

    for player in upcoming_players:
        upcoming.append({
            'name': player['name'],
            'team': player['team'],
            'rating': player['rating'],
            'salary': player['ct1']
        })

    for player in option_players:
        player_data = {
            'name': player['name'],
            'team': player['team'],
            'rating': player['rating'],
            'salary': player['ct2']
        }

        if player['ct2c'] == 1:
            team_options.append(player_data)
        elif player['ct2c'] == 2:
            player_options.append(player_data)

    return {
        'upcoming': upcoming,
        'player_options': player_options,
        'team_options': team_options
    }


def format_salary(amount):
    if amount is None or amount == 0:
        return ""
    return f"${amount:,.0f}"


@free_agency_bp.route('/free-agency')
def free_agency_page():

    current_free_agents = get_current_free_agents()
    upcoming_data = get_upcoming_free_agents()

    return render_template('free_agency.html',
                           current_free_agents=current_free_agents,
                           upcoming_free_agents=upcoming_data['upcoming'],
                           player_options=upcoming_data['player_options'],
                           team_options=upcoming_data['team_options'],
                           format_salary=format_salary)
