from flask import Blueprint, render_template, request
from stats.stats_calculations import (
    get_stats_leaders, 
    get_tonight_leaders,
    get_team_season_leaders,
    get_team_tonight_leaders,
    get_all_player_stats,
    get_available_seasons_for_players
)

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
def stats():

    # Jogadores
    season_leaders = get_stats_leaders()
    tonight_leaders = get_tonight_leaders()
    
    # Equipas
    season_team_leaders = get_team_season_leaders()
    tonight_team_leaders = get_team_tonight_leaders()
    
    return render_template('stats.html', 
                         leaders=season_leaders, 
                         tonight_leaders=tonight_leaders,
                         season_team_leaders=season_team_leaders,
                         tonight_team_leaders=tonight_team_leaders)

@stats_bp.route('/stats/players')
@stats_bp.route('/stats/players/<season>')
def all_player_stats(season=None):

    season_type = request.args.get('season_type', 'regular')
    per_mode = request.args.get('per_mode', 'per_game')
    season_segment = request.args.get('season_segment', 'all')
    sort_by = request.args.get('sort_by', 'pts')
    sort_order = request.args.get('sort_order', 'desc')

    available_seasons = get_available_seasons_for_players()

    if not season and available_seasons:
        season = available_seasons[0]

    player_stats = get_all_player_stats(
        season=season,
        season_type=season_type,
        per_mode=per_mode,
        season_segment=season_segment,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return render_template('player_stats.html',
                         player_stats=player_stats,
                         current_season=season,
                         available_seasons=available_seasons,
                         season_type=season_type,
                         per_mode=per_mode,
                         season_segment=season_segment,
                         sort_by=sort_by,
                         sort_order=sort_order)