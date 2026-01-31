from database.db_helpers import get_db_connection
from stats.stat_formulas import get_season_from_date
from stats.home_calculations import get_latest_game_date


def convert_season_to_db_format(season_str):

    if isinstance(season_str, int):
        return season_str
    if '-' in str(season_str):
        start_year = int(season_str.split('-')[0])
        return start_year + 1
    return int(season_str)

# ELO RATING
BASE_ELO = 1500  # Elo Inicial
K_FACTOR_BASE = 32  # K-Factor
ROSTER_WEIGHT = 0.5  # Peso rating dos jogadores
GAME_WEIGHT = 0.5  # Peso dos resultados

# Peso dos 8 melhores jogadores
PLAYER_POSITION_WEIGHTS = {
    1: 1.00,  
    2: 0.85,  
    3: 0.72,   
    4: 0.60,  
    5: 0.50,   
    6: 0.42,  
    7: 0.35, 
    8: 0.30, 
}

TOTAL_WEIGHT = sum(PLAYER_POSITION_WEIGHTS.values())


def get_all_teams_for_season(season):
    conn = get_db_connection()
    cursor = conn.cursor()

    db_season = convert_season_to_db_format(season)

    cursor.execute("""
        SELECT DISTINCT team_name
        FROM team_stats
        WHERE season = ?
        ORDER BY team_name
    """, (db_season,))

    teams = [row['team_name'] for row in cursor.fetchall()]
    conn.close()

    return teams


def get_team_roster_rating(team_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, rating
        FROM players
        WHERE team = ? AND rating IS NOT NULL
        ORDER BY rating DESC
        LIMIT 8
    """, (team_name,))

    players = cursor.fetchall()
    conn.close()

    if not players:
        return BASE_ELO 

    weighted_sum = 0
    actual_weight = 0

    for i, player in enumerate(players, start=1):
        weight = PLAYER_POSITION_WEIGHTS.get(i, 0.25)
        weighted_sum += player['rating'] * weight
        actual_weight += weight

    if actual_weight == 0:
        return BASE_ELO
    avg_rating = weighted_sum / actual_weight

    # Cade ponto = 15 ELO
    roster_elo = BASE_ELO + (avg_rating - 75) * 15

    return roster_elo


def calculate_expected_score(team_elo, opponent_elo):

    return 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))


def calculate_k_factor(games_played, season_progress):

    # K-Factor diminui para metade durante o ano
    season_modifier = 1 - (season_progress * 0.5)

    games_modifier = 1.0
    if games_played < 10:
        games_modifier = 1.2
    elif games_played < 20:
        games_modifier = 1.1

    return K_FACTOR_BASE * season_modifier * games_modifier


def calculate_game_elo_change(winner_elo, loser_elo, k_factor, margin_of_victory=None):

    expected_winner = calculate_expected_score(winner_elo, loser_elo)
    expected_loser = 1 - expected_winner

    base_change = k_factor * (1 - expected_winner)

    if margin_of_victory is not None:
        mov_multiplier = min(1.5, 1 + (margin_of_victory / 40))
        base_change *= mov_multiplier

    return base_change


def get_team_game_history(team_name, season):
    """
    Get all games for a team in a season, ordered chronologically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    db_season = convert_season_to_db_format(season)

    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score,
            ts.win
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE ts.team_name = ? AND ts.season = ?
        ORDER BY g.game_date
    """, (team_name, db_season))

    games = cursor.fetchall()
    conn.close()

    return games


def calculate_season_game_elo(season):
    """
    Calculate ELO ratings for all teams based on their game history for a season.

    Process:
    1. Initialize all teams with their roster-based ELO
    2. Process games chronologically
    3. Update ELO after each game

    Returns dict: {team_name: final_game_elo}
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    db_season = convert_season_to_db_format(season)

    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score
        FROM games g
        WHERE g.season = ?
        ORDER BY g.game_date
    """, (db_season,))

    all_games = cursor.fetchall()
    conn.close()

    if not all_games:
        return {}

    teams = get_all_teams_for_season(season)

    game_elos = {}
    games_played = {}

    for team in teams:
        roster_elo = get_team_roster_rating(team)
        game_elos[team] = roster_elo  
        games_played[team] = 0

    total_season_games = len(all_games)

    # Ir por ordem de jogos
    for game_index, game in enumerate(all_games):
        away_team = game['away_team']
        home_team = game['home_team']
        away_score = game['away_score']
        home_score = game['home_score']

        if away_score > home_score:
            winner = away_team
            loser = home_team
            margin = away_score - home_score
        else:
            winner = home_team
            loser = away_team
            margin = home_score - away_score

        if winner not in game_elos or loser not in game_elos:
            continue

        season_progress = game_index / max(1, total_season_games - 1) if total_season_games > 1 else 0

        winner_elo = game_elos[winner]
        loser_elo = game_elos[loser]

        k_winner = calculate_k_factor(games_played.get(winner, 0), season_progress)
        k_loser = calculate_k_factor(games_played.get(loser, 0), season_progress)
        k_factor = (k_winner + k_loser) / 2

        # Mudança
        elo_change = calculate_game_elo_change(winner_elo, loser_elo, k_factor, margin)

        # Elo update
        game_elos[winner] += elo_change
        game_elos[loser] -= elo_change
        games_played[winner] = games_played.get(winner, 0) + 1
        games_played[loser] = games_played.get(loser, 0) + 1

    return game_elos


def calculate_power_rankings():

    latest_date = get_latest_game_date()
    if not latest_date:
        return []

    season = get_season_from_date(latest_date)

    teams = get_all_teams_for_season(season)

    if not teams:
        return []

    roster_elos = {}
    for team in teams:
        roster_elos[team] = get_team_roster_rating(team)

    game_elos = calculate_season_game_elo(season)

    rankings = []

    for team in teams:
        roster_elo = roster_elos.get(team, BASE_ELO)
        game_elo = game_elos.get(team, roster_elo) 

        combined_elo = (ROSTER_WEIGHT * roster_elo) + (GAME_WEIGHT * game_elo)

        rankings.append({
            'name': team,
            'elo': round(combined_elo),
            'roster_elo': round(roster_elo),
            'game_elo': round(game_elo),
        })

    rankings.sort(key=lambda x: x['elo'], reverse=True)

    for i, team in enumerate(rankings, start=1):
        team['rank'] = i

    return rankings


def get_team_elo_history(team_name, season=None):

    if season is None:
        latest_date = get_latest_game_date()
        if not latest_date:
            return []
        season = get_season_from_date(latest_date)

    db_season = convert_season_to_db_format(season)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            g.game_id,
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score
        FROM games g
        WHERE g.season = ?
        ORDER BY g.game_date
    """, (db_season,))

    all_games = cursor.fetchall()
    conn.close()

    if not all_games:
        return []

    teams = get_all_teams_for_season(season)
    game_elos = {team: get_team_roster_rating(team) for team in teams}
    games_played = {team: 0 for team in teams}

    history = []
    total_season_games = len(all_games)

    if team_name in game_elos:
        history.append({
            'date': 'Pre-season',
            'elo': round(game_elos[team_name])
        })

    for game_index, game in enumerate(all_games):
        away_team = game['away_team']
        home_team = game['home_team']
        away_score = game['away_score']
        home_score = game['home_score']

        if away_score > home_score:
            winner = away_team
            loser = home_team
            margin = away_score - home_score
        else:
            winner = home_team
            loser = away_team
            margin = home_score - away_score

        if winner not in game_elos or loser not in game_elos:
            continue

        season_progress = game_index / max(1, total_season_games - 1) if total_season_games > 1 else 0

        winner_elo = game_elos[winner]
        loser_elo = game_elos[loser]

        k_winner = calculate_k_factor(games_played.get(winner, 0), season_progress)
        k_loser = calculate_k_factor(games_played.get(loser, 0), season_progress)
        k_factor = (k_winner + k_loser) / 2

        elo_change = calculate_game_elo_change(winner_elo, loser_elo, k_factor, margin)

        game_elos[winner] += elo_change
        game_elos[loser] -= elo_change

        games_played[winner] = games_played.get(winner, 0) + 1
        games_played[loser] = games_played.get(loser, 0) + 1

        if team_name == winner or team_name == loser:
            history.append({
                'date': game['game_date'],
                'elo': round(game_elos[team_name])
            })

    return history
