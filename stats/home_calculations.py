from database.db_helpers import get_db_connection
from datetime import datetime, timedelta
from stats.standings_calculations import calculate_league_standings
from stats.playoff_calculations import get_playoff_bracket
from stats.stat_formulas import get_season_from_date

def get_latest_game_date():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT MAX(game_date) as latest_date
        FROM games
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return result['latest_date'] if result else None

def get_games_by_date(game_date):
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
        WHERE g.game_date = ?
        ORDER BY g.game_id
    """, (game_date,))
    
    games = cursor.fetchall()
    conn.close()
    
    return games

def get_latest_games():
    latest_date = get_latest_game_date()
    
    if not latest_date:
        return []
    
    return get_games_by_date(latest_date)

def get_champions_history():
    return []

def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_type, transaction_date, player_name, from_team, to_team, trade_group_id
        FROM transactions
        ORDER BY transaction_date DESC, transaction_id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()

    transactions = []
    seen_trade_groups = set()

    for row in rows:
        trans_type = row['transaction_type']
        player = row['player_name']
        from_team = row['from_team']
        to_team = row['to_team']
        trade_group_id = row['trade_group_id']

        # 1 por trade_id
        if trans_type == 'TRADE' and trade_group_id:
            if trade_group_id in seen_trade_groups:
                continue
            seen_trade_groups.add(trade_group_id)

            cursor.execute("""
                SELECT DISTINCT from_team, to_team FROM transactions
                WHERE trade_group_id = ?
            """, (trade_group_id,))
            trade_teams = cursor.fetchall()
            teams_in_trade = set()
            for t in trade_teams:
                teams_in_trade.add(t['from_team'])
                teams_in_trade.add(t['to_team'])
            teams_list = list(teams_in_trade)

            cursor.execute("""
                SELECT t.player_name, t.to_team, p.rating
                FROM transactions t
                LEFT JOIN players p ON t.player_name = p.name
                WHERE t.trade_group_id = ? AND p.rating IS NOT NULL
                ORDER BY p.rating DESC
                LIMIT 1
            """, (trade_group_id,))
            best_player = cursor.fetchone()

            if best_player:
                player_name = best_player['player_name']
                destination_team = best_player['to_team']
            else:
                cursor.execute("""
                    SELECT player_name, to_team FROM transactions
                    WHERE trade_group_id = ? AND player_name NOT LIKE '%1st%' AND player_name NOT LIKE '%2nd%'
                    LIMIT 1
                """, (trade_group_id,))
                first_player = cursor.fetchone()
                player_name = first_player['player_name'] if first_player else "Players"
                destination_team = first_player['to_team'] if first_player else teams_list[0] if teams_list else ''

            team_abbrevs = {
                "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Charlotte Hornets": "CHA",
                "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL",
                "Denver Nuggets": "DEN", "Detroit Pistons": "DET", "Golden State Warriors": "GSW",
                "Houston Rockets": "HOU", "Indiana Pacers": "IND", "Los Angeles Clippers": "LAC",
                "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA",
                "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "Montreal Mastodons": "MTL",
                "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
                "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
                "Portland Trailblazers": "POR", "Sacramento Kings": "SAC", "San Diego Caravels": "SDC",
                "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
            }
            dest_abbrev = team_abbrevs.get(destination_team, destination_team[:3].upper() if destination_team else "")

            transactions.append({
                'type': 'TRADE',
                'player': f"{player_name} to {dest_abbrev}",
                'team1': teams_list[0] if len(teams_list) > 0 else '',
                'team2': teams_list[1] if len(teams_list) > 1 else ''
            })
        elif trans_type == 'SIGNING':
            transactions.append({
                'type': 'SIGNING',
                'player': player,
                'team1': to_team,
                'team2': None
            })
        elif trans_type == 'RELEASE':
            transactions.append({
                'type': 'RELEASE',
                'player': player,
                'team1': from_team,
                'team2': None
            })
        else:
            transactions.append({
                'type': trans_type,
                'player': player,
                'team1': from_team or to_team,
                'team2': None
            })

        if len(transactions) >= 10:
            break

    conn.close()
    return transactions

def get_power_rankings():
    """
    Get current power rankings based on ELO system.
    Combines roster strength (top 8 players) with game performance.
    """
    from stats.elo_calculations import calculate_power_rankings
    return calculate_power_rankings()

def get_injury_report():
    """
    Get current injury report from players with IR=1
    Returns list of dicts with player_name and team
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, team
        FROM players
        WHERE IR = 1
        ORDER BY team, name
    """)

    injured_players = cursor.fetchall()
    conn.close()

    return [{'player_name': p['name'], 'team': p['team']} for p in injured_players]

def get_upcoming_games():
    
    latest_date_str = get_latest_game_date()
    if not latest_date_str:
        return []

    latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
    season = get_season_from_date(latest_date_str)
    season_start_year = int(season.split('-')[0])
    playoff_start_date = datetime.strptime(f"{season_start_year + 1}-04-20", '%Y-%m-%d')
    
    #Playoffs
    if latest_date >= playoff_start_date:
        standings = calculate_league_standings()
        bracket = get_playoff_bracket(season, standings['Eastern'], standings['Western'])
        
        upcoming_playoff_games = []

        def add_active_series(series_data, round_name, is_play_in=False, is_qualifier=False):
            """
            Checks if a series is active. If so, calculates the next matchup.
            """
            if not series_data or series_data.get('complete'):
                return

            t1 = series_data['team1'] 
            t2 = series_data['team2']
            t1_wins = series_data['team1_wins']
            t2_wins = series_data['team2_wins']
            
            if is_play_in:
                if is_qualifier:

                    is_team1_home = False 
                else:
                    is_team1_home = True
            else:
                next_game_num = t1_wins + t2_wins + 1
                is_team1_home = next_game_num in [1, 2, 5, 7]

            if is_team1_home:
                upcoming_playoff_games.append({
                    'away_team': t2,
                    'home_team': t1,
                    'away_record': f"{t2_wins}-{t1_wins}", 
                    'home_record': f"{t1_wins}-{t2_wins}",
                    'round': round_name
                })
            else:
                upcoming_playoff_games.append({
                    'away_team': t1,
                    'home_team': t2,
                    'away_record': f"{t1_wins}-{t2_wins}",
                    'home_record': f"{t2_wins}-{t1_wins}",
                    'round': round_name
                })

        for conf in ['Eastern', 'Western']:
            if not bracket.get(conf) or not bracket[conf].get('play_in'):
                continue
                
            p_data = bracket[conf]['play_in']
            
            add_active_series(p_data.get('7v8'), f'{conf} Play-In (7v8)', is_play_in=True)
            add_active_series(p_data.get('9v10'), f'{conf} Play-In (9v10)', is_play_in=True)
            add_active_series(p_data.get('winner_9v10_vs_loser_7v8'), f'{conf} Play-In Qualifier', is_play_in=True, is_qualifier=True)

        matchup_order = ['1v8', '4v5', '3v6', '2v7']
        for conf in ['Eastern', 'Western']:
            if not bracket.get(conf) or not bracket[conf].get('first_round'):
                continue
                
            fr_data = bracket[conf]['first_round']
            for key in matchup_order:
                add_active_series(fr_data.get(key), f'{conf} First Round')
            
        for conf in ['Eastern', 'Western']:
            if not bracket.get(conf) or not bracket[conf].get('conference_semis'):
                continue

            cs_data = bracket[conf]['conference_semis']
            add_active_series(cs_data.get('upper'), f'{conf} Semifinals')
            add_active_series(cs_data.get('lower'), f'{conf} Semifinals')
                
        for conf in ['Eastern', 'Western']:
            if bracket.get(conf):
                add_active_series(bracket[conf].get('conference_finals'), f'{conf} Conference Finals')

        add_active_series(bracket.get('Finals'), 'NBA Finals')

        return upcoming_playoff_games

    else:
        next_day = latest_date + timedelta(days=1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT away_team, home_team
                FROM schedule
                WHERE month = ? AND day = ?
                ORDER BY away_team
            """, (next_day.month, next_day.day))
            
            scheduled_games = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching schedule: {e}")
            conn.close()
            return []
            
        conn.close()
        
        standings = calculate_league_standings()
        records = {}
        for team in standings['Eastern'] + standings['Western']:
            records[team['team']] = f"{team['wins']}-{team['losses']}"
            
        return [{
            'away_team': g['away_team'],
            'home_team': g['home_team'],
            'away_record': records.get(g['away_team'], '0-0'),
            'home_record': records.get(g['home_team'], '0-0'),
            'round': None
        } for g in scheduled_games]