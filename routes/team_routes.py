import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from flask import Blueprint, render_template, request
from database.db_helpers import get_all_players, get_total_games
from stats.standings_calculations import calculate_league_standings, get_available_seasons
from stats.playoff_calculations import get_playoff_bracket
from stats.team_calculations import (
    get_team_roster,
    get_team_season_records,
    get_team_games_by_season,
    get_game_boxscore,
    get_team_draft_picks,
    get_all_team_stats,
    get_available_seasons_for_teams,
    get_all_teams,
    get_franchise_names,
    get_primary_franchise_name,
    get_display_name_for_season
)

team_bp = Blueprint('team', __name__)

def _series_involves_franchise(series, franchise_names):
    """Helper to check if a franchise is in a series."""
    if not series:
        return False
    return series['team1'] in franchise_names or series['team2'] in franchise_names

def _get_playoff_results(bracket, conference, franchise_names):
    """Extract playoff results for a franchise from the bracket."""
    playoff_results = []
    if not conference:
        return playoff_results

    conf_bracket = bracket.get(conference, {})

    if conf_bracket.get('play_in'):
        for _, series in conf_bracket['play_in'].items():
            if _series_involves_franchise(series, franchise_names):
                result = _format_series_result_franchise(series, franchise_names, 'Play-In')
                if result:
                    playoff_results.append(result)

    if conf_bracket.get('first_round'):
        for _, series in conf_bracket['first_round'].items():
            if _series_involves_franchise(series, franchise_names):
                result = _format_series_result_franchise(series, franchise_names, 'First Round')
                if result:
                    playoff_results.append(result)

    if conf_bracket.get('conference_semis'):
        for _, series in conf_bracket['conference_semis'].items():
            if _series_involves_franchise(series, franchise_names):
                result = _format_series_result_franchise(series, franchise_names, 'Conf. Semifinals')
                if result:
                    playoff_results.append(result)

    if conf_bracket.get('conference_finals'):
        series = conf_bracket['conference_finals']
        if _series_involves_franchise(series, franchise_names):
            result = _format_series_result_franchise(series, franchise_names, 'Conf. Finals')
            if result:
                playoff_results.append(result)

    if bracket.get('Finals'):
        series = bracket['Finals']
        if _series_involves_franchise(series, franchise_names):
            result = _format_series_result_franchise(series, franchise_names, 'HH Finals')
            if result:
                playoff_results.append(result)
                
    return playoff_results

def get_team_season_history(team_name):
    available_seasons = get_available_seasons()
    history = {}

    franchise_names = get_franchise_names(team_name)

    for season in available_seasons:
        try:
            standings = calculate_league_standings(season)
            bracket = get_playoff_bracket(season, standings['Eastern'], standings['Western'])

            standing_pos = None
            conference = None
            
            # Find Standing and Conference
            for conf_name, conf_standings in [('Eastern', standings['Eastern']), ('Western', standings['Western'])]:
                for team in conf_standings:
                    if team['team'] in franchise_names:
                        standing_pos = team['seed']
                        conference = conf_name
                        break
                if standing_pos:
                    break

            if not standing_pos:
                continue

            playoff_results = _get_playoff_results(bracket, conference, franchise_names)

            history[season] = {
                'standing': standing_pos,
                'conference': conference,
                'playoff_results': playoff_results
            }
        except Exception as e:
            continue

    return history

def _format_series_result_franchise(series, franchise_names, round_name):
    """Format a playoff series result for display (franchise-aware)"""
    if not series or series['team1_wins'] == 0 and series['team2_wins'] == 0:
        return None

    is_team1 = series['team1'] in franchise_names
    team_wins = series['team1_wins'] if is_team1 else series['team2_wins']
    opp_wins = series['team2_wins'] if is_team1 else series['team1_wins']
    opponent = series['team2'] if is_team1 else series['team1']

    won = series['winner'] in franchise_names if series['winner'] else None

    return {
        'round': round_name,
        'opponent': opponent,
        'team_wins': team_wins,
        'opp_wins': opp_wins,
        'won': won,
        'complete': series.get('complete', False)
    }

def get_game_leaders(game_id, team_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    leaders = {}
    categories = [('points', 'points'), ('rebounds', 'rebounds'), ('assists', 'assists')]
    
    for key, col in categories:
        query = f"""
            SELECT player_name, {col} as value
            FROM player_stats
            WHERE game_id = ? AND team = ?
            ORDER BY {col} DESC, minutes ASC, player_name ASC
            LIMIT 1
        """
        cursor.execute(query, (game_id, team_name))
        result = cursor.fetchone()
        
        if result:
            leaders[key] = {'player': result['player_name'], 'value': result['value']}
        else:
            leaders[key] = {'player': 'N/A', 'value': 0}
            
    conn.close()
    return leaders


@team_bp.route('/teams')
def teams():
    """Display list of all teams"""
    teams = get_all_teams()
    return render_template('teams.html', teams=teams)

@team_bp.route('/team/<team_name>')
def team_page(team_name):
    primary_name = get_primary_franchise_name(team_name)
    franchise_names = get_franchise_names(team_name)

    roster_season = request.args.get('roster_season')
    season_type = request.args.get('season_type', 'regular')

    season_records = get_team_season_records(team_name)
    draft_picks = get_team_draft_picks(team_name)

    if not season_records:
        return render_template('error.html', message=f"Team '{team_name}' not found")

    available_seasons = [r['season'] for r in season_records]

    roster, current_roster_season = get_team_roster(team_name, roster_season, season_type)

    if not roster_season:
        roster_season = current_roster_season

    total_wins = sum(r['wins'] for r in season_records)
    total_losses = sum(r['losses'] for r in season_records)

    season_history = get_team_season_history(team_name)

    current_display_name = get_display_name_for_season(team_name, available_seasons[0] if available_seasons else '2024-25')

    return render_template('team.html',
                           team_name=primary_name,
                           display_name=current_display_name,
                           franchise_names=franchise_names,
                           roster=roster,
                           season_records=season_records,
                           draft_picks=draft_picks,
                           total_wins=total_wins,
                           total_losses=total_losses,
                           season_history=season_history,
                           available_seasons=available_seasons,
                           current_roster_season=roster_season,
                           season_type=season_type,
                           get_display_name_for_season=get_display_name_for_season)

@team_bp.route('/team/<team_name>/season/<season>')
def team_season(team_name, season):
    primary_name = get_primary_franchise_name(team_name)
    franchise_names = get_franchise_names(team_name)
    display_name = get_display_name_for_season(team_name, season)

    games = get_team_games_by_season(team_name, season)

    if not games:
        return render_template('error.html', message=f"No games found for {team_name} in {season}")

    wins = sum(1 for game in games if game['win'] == 1)
    losses = len(games) - wins

    standing_pos = None
    conference = None
    playoff_results = []

    try:
        standings = calculate_league_standings(season)
        bracket = get_playoff_bracket(season, standings['Eastern'], standings['Western'])

        for conf_name, conf_standings in [('Eastern', standings['Eastern']), ('Western', standings['Western'])]:
            for team in conf_standings:
                if team['team'] in franchise_names:
                    standing_pos = team['seed']
                    conference = conf_name
                    break
            if standing_pos:
                break
        
        playoff_results = _get_playoff_results(bracket, conference, franchise_names)

    except Exception:
        pass

    return render_template('team_season.html',
                           team_name=primary_name,
                           display_name=display_name,
                           season=season,
                           games=games,
                           wins=wins,
                           losses=losses,
                           standing=standing_pos,
                           playoff_results=playoff_results)

def get_game_mvp(game_id, winning_team):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM player_stats WHERE game_id = ?", (game_id,))
    players = cursor.fetchall()
    conn.close()
    
    mvp_list = []
    for p in players:
        gms = (
            (p['points'] * 1.0) +
            (p['rebounds'] * 0.5) +
            (p['assists'] * 1.2) +
            (p['steals'] * 1.0) +
            (p['blocks'] * 0.8) -
            (p['turnovers'] * 1.2) -
            (p['fg_att'] * 0.4) -
            (p['ft_att'] * 0.2) +
            (p['tp_made'] * 0.5) +
            (p['minutes'] * 0.05)
        )
        
        if p['team'] == winning_team:
            gms *= 1.20
            
        mvp_list.append({
            'name': p['player_name'],
            'gms': round(gms, 2),
            'minutes': p['minutes']
        })
    
    if not mvp_list:
        return None

    mvp_list.sort(key=lambda x: (-x['gms'], x['minutes'], x['name']))
    
    return mvp_list[0]

@team_bp.route('/game/<int:game_id>/team/<team_name>')
def game_boxscore(game_id, team_name):
    boxscore = get_game_boxscore(game_id, team_name)
    
    if not boxscore:
        return render_template('error.html', message=f"Game not found")
    
    return render_template('game_boxscore.html', **boxscore)

@team_bp.route('/league')
@team_bp.route('/league/<season>')
def league_standings(season=None):    
    available_seasons = get_available_seasons()
    
    if season is None and available_seasons:
        season = available_seasons[0]
    
    standings = calculate_league_standings(season)
    playoff_bracket = get_playoff_bracket(season, standings['Eastern'], standings['Western'])
    
    return render_template('league.html', 
                           eastern=standings['Eastern'],
                           western=standings['Western'],
                           playoff_bracket=playoff_bracket,
                           current_season=season,
                           available_seasons=available_seasons)

@team_bp.route('/league/<season>/series/<team1>/<team2>')
def playoff_series(season, team1, team2):

    standings = calculate_league_standings(season)
    playoff_bracket = get_playoff_bracket(season, standings['Eastern'], standings['Western'])
    
    series = None
    for conf_name, conf_bracket in [('Eastern', playoff_bracket['Eastern']), ('Western', playoff_bracket['Western'])]:
        if conf_bracket.get('play_in'):
            for key, s in conf_bracket['play_in'].items():
                if s and ((s['team1'] == team1 and s['team2'] == team2) or (s['team1'] == team2 and s['team2'] == team1)):
                    series = s
                    break
        
        if not series and conf_bracket.get('first_round'):
            for key, s in conf_bracket['first_round'].items():
                if s and ((s['team1'] == team1 and s['team2'] == team2) or (s['team1'] == team2 and s['team2'] == team1)):
                    series = s
                    break
        
        if not series and conf_bracket.get('conference_semis'):
            for key, s in conf_bracket['conference_semis'].items():
                if s and ((s['team1'] == team1 and s['team2'] == team2) or (s['team1'] == team2 and s['team2'] == team1)):
                    series = s
                    break
        
        if not series and conf_bracket.get('conference_finals'):
            s = conf_bracket['conference_finals']
            if s and ((s['team1'] == team1 and s['team2'] == team2) or (s['team1'] == team2 and s['team2'] == team1)):
                series = s
                break

    if not series and playoff_bracket.get('Finals'):
        s = playoff_bracket['Finals']
        if s and ((s['team1'] == team1 and s['team2'] == team2) or (s['team1'] == team2 and s['team2'] == team1)):
            series = s

    if not series:
        return render_template('error.html', message=f"Series not found")

    if 'games' in series:
        for game in series['games']:
            g_id = game.get('game_id')
            if g_id:
                game['away_leaders'] = get_game_leaders(g_id, game['away'])
                game['home_leaders'] = get_game_leaders(g_id, game['home'])
                winner = game.get('winner')
                game['mvp'] = get_game_mvp(g_id, winner)
    
    return render_template('playoff_series.html',
                           season=season,
                           series=series)

@team_bp.route('/stats/teams')
@team_bp.route('/stats/teams/<season>')
def team_stats_page(season=None):

    season_type = request.args.get('season_type', 'regular')
    per_mode = request.args.get('per_mode', 'per_game')
    season_segment = request.args.get('season_segment', 'all')
    
    available_seasons = get_available_seasons_for_teams()
    
    if not season and available_seasons:
        season = available_seasons[0]
    
    team_stats = get_all_team_stats(
        season=season,
        season_type=season_type,
        per_mode=per_mode,
        season_segment=season_segment
    )
    
    return render_template('team_stats.html',
                           team_stats=team_stats,
                           current_season=season,
                           available_seasons=available_seasons,
                           season_type=season_type,
                           per_mode=per_mode,
                           season_segment=season_segment)