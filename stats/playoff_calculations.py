from database.db_helpers import get_db_connection
from stats.stat_formulas import get_season_from_date

def get_playoff_bracket(season, eastern_standings, western_standings):

    conn = get_db_connection()
    cursor = conn.cursor()
    
    season_start_year = int(season.split('-')[0])
    playoff_start = f"{season_start_year + 1}-04-20"
    season_end = f"{season_start_year + 1}-06-30"
    
    cursor.execute("""
        SELECT 
            g.game_id,
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score
        FROM games g
        WHERE g.game_date >= ? AND g.game_date <= ?
        ORDER BY g.game_date
    """, (playoff_start, season_end))
    
    playoff_games = cursor.fetchall()
    conn.close()
    
    bracket = {
        'Eastern': _build_conference_bracket(eastern_standings, playoff_games, 'Eastern'),
        'Western': _build_conference_bracket(western_standings, playoff_games, 'Western'),
        'Finals': None
    }
    
    east_champ = bracket['Eastern'].get('conference_champion')
    west_champ = bracket['Western'].get('conference_champion')
    
    if east_champ and west_champ:
        bracket['Finals'] = _build_finals_series(east_champ, west_champ, playoff_games, 
                                                 eastern_standings, western_standings, season)
    
    return bracket

def _build_conference_bracket(standings, playoff_games, conference):
    """Build bracket for one conference"""
    if len(standings) < 10:
        return {}
    
    bracket = {
        'play_in': {
            '7v8': None,
            '9v10': None,
            'winner_9v10_vs_loser_7v8': None
        },
        'first_round': {},
        'conference_semis': {},
        'conference_finals': None,
        'conference_champion': None
    }
    
    # Play-in: 9v10
    seed_9 = standings[8]['team']
    seed_10 = standings[9]['team']
    bracket['play_in']['9v10'] = _get_series_result(seed_9, seed_10, playoff_games, best_of=1, team1_seed=9, team2_seed=10)
    
    # Play-in: 7v8 
    seed_7 = standings[6]['team']
    seed_8 = standings[7]['team']
    bracket['play_in']['7v8'] = _get_series_result(seed_7, seed_8, playoff_games, best_of=1, team1_seed=7, team2_seed=8)
    
    # Resultados play-in
    series_7v8 = bracket['play_in']['7v8']
    series_9v10 = bracket['play_in']['9v10']
    
    actual_7_seed = None
    actual_8_seed = None
    
    # 7th seed logic
    if series_7v8 and series_7v8['winner']:
        actual_7_seed = series_7v8['winner']
        loser_7v8 = series_7v8['loser']
        
        # 8th seed logic
        if series_9v10 and series_9v10['winner']:
            winner_9v10 = series_9v10['winner']
            
            winner_9v10_seed = 9 if series_9v10['team1_wins'] > series_9v10['team2_wins'] else 10
            loser_7v8_seed = 7 if loser_7v8 == seed_7 else 8
            
            bracket['play_in']['winner_9v10_vs_loser_7v8'] = _get_series_result(
                loser_7v8, winner_9v10, playoff_games, best_of=1, 
                team1_seed=loser_7v8_seed, team2_seed=winner_9v10_seed
            )
            
            if bracket['play_in']['winner_9v10_vs_loser_7v8'] and bracket['play_in']['winner_9v10_vs_loser_7v8']['winner']:
                actual_8_seed = bracket['play_in']['winner_9v10_vs_loser_7v8']['winner']
    
    # First Round
    matchups = [
        (standings[0]['team'], actual_8_seed if actual_8_seed else 'TBD', '1v8', 1, 8),
        (standings[3]['team'], standings[4]['team'], '4v5', 4, 5),
        (standings[2]['team'], standings[5]['team'], '3v6', 3, 6),
        (standings[1]['team'], actual_7_seed if actual_7_seed else 'TBD', '2v7', 2, 7)
    ]
    
    first_round_winners = []
    for high_seed, low_seed, matchup_name, high_seed_num, low_seed_num in matchups:
        series = _get_series_result(high_seed, low_seed, playoff_games, best_of=7, 
                                    team1_seed=high_seed_num, team2_seed=low_seed_num)
        bracket['first_round'][matchup_name] = series
        if series and series['winner']:
            winner_seed = series['team1_seed'] if series['winner'] == series['team1'] else series['team2_seed']
            first_round_winners.append((series['winner'], series, winner_seed))
    
    # Conference Semis & Finals
    if len(first_round_winners) >= 4:
        def get_sorted_matchup(team_a_data, team_b_data):
            team_a, _, seed_a = team_a_data
            team_b, _, seed_b = team_b_data
            if seed_a > seed_b:
                return team_b, team_a, seed_b, seed_a
            return team_a, team_b, seed_a, seed_b

        t1, t2, s1, s2 = get_sorted_matchup(first_round_winners[0], first_round_winners[1])
        series1 = _get_series_result(t1, t2, playoff_games, best_of=7, team1_seed=s1, team2_seed=s2)
        bracket['conference_semis']['upper'] = series1
        
        t1, t2, s1, s2 = get_sorted_matchup(first_round_winners[2], first_round_winners[3])
        series2 = _get_series_result(t1, t2, playoff_games, best_of=7, team1_seed=s1, team2_seed=s2)
        bracket['conference_semis']['lower'] = series2
        
        if series1 and series1['winner'] and series2 and series2['winner']:
            w1 = series1['winner']
            w1_seed = series1['team1_seed'] if w1 == series1['team1'] else series1['team2_seed']
            
            w2 = series2['winner']
            w2_seed = series2['team1_seed'] if w2 == series2['team1'] else series2['team2_seed']
            
            if w1_seed > w2_seed:
                t1, t2 = w2, w1
                s1, s2 = w2_seed, w1_seed
            else:
                t1, t2 = w1, w2
                s1, s2 = w1_seed, w2_seed
            
            conf_finals = _get_series_result(t1, t2, playoff_games, best_of=7,
                                             team1_seed=s1, team2_seed=s2)
            bracket['conference_finals'] = conf_finals
            
            if conf_finals and conf_finals['winner']:
                bracket['conference_champion'] = conf_finals['winner']
    
    return bracket

def _get_series_result(team1, team2, playoff_games, best_of=7, team1_seed=None, team2_seed=None):

    if not team1 or not team2:
        return None
    
    series_games = []
    for game in playoff_games:
        if (game['home_team'] == team1 and game['away_team'] == team2) or \
           (game['home_team'] == team2 and game['away_team'] == team1):
            series_games.append(game)
    
    if not series_games:
        return {
            'team1': team1, 'team2': team2,
            'team1_seed': team1_seed, 'team2_seed': team2_seed,
            'team1_wins': 0, 'team2_wins': 0,
            'games': [], 'winner': None, 'loser': None,
            'complete': False
        }
    
    team1_wins = 0
    team2_wins = 0
    games_details = []
    
    for game in series_games:
        if game['home_team'] == team1:
            if game['home_score'] > game['away_score']:
                team1_wins += 1
                winner = team1
            else:
                team2_wins += 1
                winner = team2
        else:
            if game['home_score'] > game['away_score']:
                team2_wins += 1
                winner = team2
            else:
                team1_wins += 1
                winner = team1
        
        games_details.append({
            'game_id': game['game_id'],
            'date': game['game_date'],
            'home': game['home_team'],
            'away': game['away_team'],
            'home_score': game['home_score'],
            'away_score': game['away_score'],
            'winner': winner
        })
    
    wins_needed = (best_of + 1) // 2
    series_winner = None
    series_loser = None
    complete = False
    
    if team1_wins >= wins_needed:
        series_winner = team1
        series_loser = team2
        complete = True
    elif team2_wins >= wins_needed:
        series_winner = team2
        series_loser = team1
        complete = True
    
    return {
        'team1': team1, 'team2': team2,
        'team1_seed': team1_seed, 'team2_seed': team2_seed,
        'team1_wins': team1_wins, 'team2_wins': team2_wins,
        'games': games_details,
        'winner': series_winner, 'loser': series_loser,
        'complete': complete
    }

def _calculate_finals_mvp(winner, loser, season):

    conn = get_db_connection()
    conn.row_factory = None
    cursor = conn.cursor()
    
    # Datas dos jogos de playoff
    season_start_year = int(season.split('-')[0])
    playoff_start = f"{season_start_year + 1}-04-20"
    season_end = f"{season_start_year + 1}-06-30"
    
    query = """
        SELECT 
            p.player_name, 
            p.team,
            SUM(p.points) as total_points
        FROM player_stats p 
        JOIN games g ON p.game_id = g.game_id
        WHERE 
            g.game_date >= ? AND g.game_date <= ?
            AND (
                (g.home_team = ? AND g.away_team = ?) 
                OR 
                (g.home_team = ? AND g.away_team = ?)
            )
        GROUP BY p.player_name, p.team
    """
    
    cursor.execute(query, (playoff_start, season_end, winner, loser, loser, winner))
    players = cursor.fetchall()
    conn.close()

    mvp_list = []
    for row in players:
        name = row[0]
        team = row[1]
        points = row[2] if row[2] else 0
        
        final_score = points * 2 if team == winner else points
        
        mvp_list.append({'name': name, 'score': final_score, 'raw_points': points})

    if not mvp_list:
        return None

    mvp_list.sort(key=lambda x: x['score'], reverse=True)
    return mvp_list[0]

def _build_finals_series(east_champ, west_champ, playoff_games, east_standings, west_standings, season):
    east_record = next((team for team in east_standings if team['team'] == east_champ), None)
    west_record = next((team for team in west_standings if team['team'] == west_champ), None)
    
    higher_seed = east_champ
    lower_seed = west_champ
    
    if east_record and west_record:
        if east_record['wins'] > west_record['wins']:
            higher_seed = east_champ
            lower_seed = west_champ
        elif west_record['wins'] > east_record['wins']:
            higher_seed = west_champ
            lower_seed = east_champ
        else:
            if east_record['win_pct'] >= west_record['win_pct']:
                higher_seed = east_champ
                lower_seed = west_champ
            else:
                higher_seed = west_champ
                lower_seed = east_champ
    
    series = _get_series_result(higher_seed, lower_seed, playoff_games, best_of=7)
    
    if series:
        series['home_court_team'] = higher_seed
        
        if series.get('winner'):
            series['mvp'] = _calculate_finals_mvp(series['winner'], series['loser'], season)
    
    return series