from flask import Blueprint, render_template
from database.db_helpers import get_all_players, get_total_games
from stats.home_calculations import (
    get_latest_games,
    get_champions_history,
    get_transactions,
    get_power_rankings,
    get_injury_report,
    get_upcoming_games
)

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    latest_games = get_latest_games()
    champions = get_champions_history()
    transactions = get_transactions()
    power_rankings = get_power_rankings()
    injuries = get_injury_report()
    upcoming_games = get_upcoming_games()
    
    return render_template('home.html',
                         latest_games=latest_games,
                         champions=champions,
                         transactions=transactions,
                         power_rankings=power_rankings,
                         injuries=injuries,
                         upcoming_games=upcoming_games)