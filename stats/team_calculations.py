import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_helpers import get_db_connection
from stats.stat_formulas import get_season_from_date
from stats.standings_calculations import get_available_seasons as get_available_seasons_for_teams

#Primero nome para Nome Atual (Em caso de futuras relocações)
FRANCHISE_MAP = {
    'Montreal Mastodons': 'Brooklyn Nets',
    'San Diego Caravels': 'San Antonio Spurs',
}

#Histórico de nomes
FRANCHISE_NAMES = {
    'Brooklyn Nets': ['Brooklyn Nets', 'Montreal Mastodons'],
    'San Antonio Spurs': ['San Antonio Spurs', 'San Diego Caravels'],
}

def get_franchise_names(team_name):

    primary = FRANCHISE_MAP.get(team_name, team_name)
    return FRANCHISE_NAMES.get(primary, [team_name])

def get_primary_franchise_name(team_name):
    return FRANCHISE_MAP.get(team_name, team_name)

def get_display_name_for_season(team_name, season):
    if season >= '2025-26':
        if team_name == 'Brooklyn Nets' or team_name == 'Montreal Mastodons':
            return 'Montreal Mastodons'
        if team_name == 'San Antonio Spurs' or team_name == 'San Diego Caravels':
            return 'San Diego Caravels'
    else:
        if team_name == 'Brooklyn Nets' or team_name == 'Montreal Mastodons':
            return 'Brooklyn Nets'
        if team_name == 'San Antonio Spurs' or team_name == 'San Diego Caravels':
            return 'San Antonio Spurs'
    return team_name


def get_all_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT team FROM (
            SELECT home_team AS team FROM games
            UNION
            SELECT away_team AS team FROM games
        ) ORDER BY team
    """)
    all_teams = [row['team'] for row in cursor.fetchall()]
    conn.close()

    consolidated = set()
    for team in all_teams:
        primary = get_primary_franchise_name(team)
        consolidated.add(primary)

    return sorted(list(consolidated))


def get_team_roster(team_name, season=None, season_type='regular'):

    franchise_names = get_franchise_names(team_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?' for _ in franchise_names])

    if not season:
        cursor.execute(f"""
            SELECT MAX(g.game_date) as latest_date
            FROM player_stats ps
            JOIN games g ON ps.game_id = g.game_id
            WHERE ps.team IN ({placeholders})
        """, franchise_names)

        result = cursor.fetchone()
        if not result or not result['latest_date']:
            conn.close()
            return [], None

        season = get_season_from_date(result['latest_date'])

    season_start_year = int(season.split('-')[0])
    season_end_year = season_start_year + 1
    season_start = f"{season_start_year}-07-01"
    season_end = f"{season_end_year}-06-30"
    playoff_start = f"{season_end_year}-04-20"

    if season_type == 'playoffs':
        date_start = playoff_start
        date_end = season_end
    else:
        date_start = season_start
        date_end = playoff_start

    cursor.execute(f"""
        WITH PlayerLastGame AS (
            SELECT
                ps.player_name,
                ps.team as last_team
            FROM player_stats ps
            JOIN games g ON ps.game_id = g.game_id
            WHERE g.game_date >= ? AND g.game_date <= ?
            AND g.game_date = (
                SELECT MAX(g2.game_date)
                FROM player_stats ps2
                JOIN games g2 ON ps2.game_id = g2.game_id
                WHERE ps2.player_name = ps.player_name
                AND g2.game_date >= ? AND g2.game_date <= ?
            )
        )
        SELECT
            ps.player_name,
            COUNT(*) as games_played,
            SUM(ps.started) as games_started,
            ROUND(AVG(ps.minutes), 1) as mpg,
            ROUND(AVG(ps.points), 1) as ppg,
            ROUND(AVG(ps.rebounds), 1) as rpg,
            ROUND(AVG(ps.assists), 1) as apg
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        JOIN PlayerLastGame plg ON ps.player_name = plg.player_name
        WHERE ps.team IN ({placeholders})
        AND g.game_date >= ?
        AND g.game_date <= ?
        AND plg.last_team IN ({placeholders})
        GROUP BY ps.player_name
        ORDER BY AVG(ps.points) DESC
    """, [season_start, season_end, season_start, season_end] +
         franchise_names + [date_start, date_end] + franchise_names)

    roster = cursor.fetchall()
    conn.close()

    return roster, season

def get_team_season_records(team_name):
    franchise_names = get_franchise_names(team_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?' for _ in franchise_names])

    cursor.execute(f"""
        SELECT
            g.game_date,
            ts.win
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE ts.team_name IN ({placeholders})
        ORDER BY g.game_date DESC
    """, franchise_names)

    games = cursor.fetchall()
    conn.close()

    season_records = {}
    for game in games:
        season = get_season_from_date(game['game_date'])
        if season not in season_records:
            season_records[season] = {'wins': 0, 'losses': 0, 'games': 0}

        season_records[season]['games'] += 1
        if game['win'] == 1:
            season_records[season]['wins'] += 1
        else:
            season_records[season]['losses'] += 1

    records_list = []
    for season, record in season_records.items():
        records_list.append({
            'season': season,
            'wins': record['wins'],
            'losses': record['losses'],
            'games': record['games'],
            'win_pct': round(record['wins'] / record['games'], 3) if record['games'] > 0 else 0
        })

    records_list.sort(key=lambda x: x['season'], reverse=True)
    return records_list

def get_team_games_by_season(team_name, season):
    franchise_names = get_franchise_names(team_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join(['?' for _ in franchise_names])

    season_start_year = int(season.split('-')[0])
    season_end_year = season_start_year + 1
    season_start = f"{season_start_year}-07-01"
    season_end = f"{season_end_year}-06-30"

    cursor.execute(f"""
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
        WHERE ts.team_name IN ({placeholders})
        AND g.game_date >= ?
        AND g.game_date <= ?
        ORDER BY g.game_date DESC
    """, franchise_names + [season_start, season_end])

    games = cursor.fetchall()
    conn.close()

    return games

def get_game_boxscore(game_id, team_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            game_date,
            away_team,
            away_score,
            home_team,
            home_score
        FROM games
        WHERE game_id = ?
    """, (game_id,))
    
    game_info = cursor.fetchone()
    
    if not game_info:
        conn.close()
        return None

    current_game_date = game_info['game_date']
    current_season = get_season_from_date(current_game_date)
    
    season_start_year = int(current_season.split('-')[0])
    season_start_date = f"{season_start_year}-07-01"

    def get_record_at_date(team, date, start_date):
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN ts.win = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN ts.win = 0 THEN 1 ELSE 0 END) as losses
            FROM team_stats ts
            JOIN games g ON ts.game_id = g.game_id
            WHERE ts.team_name = ?
            AND g.game_date >= ?
            AND g.game_date <= ?
        """, (team, start_date, date))
        result = cursor.fetchone()
        if result and result['wins'] is not None:
            return f"{result['wins']}-{result['losses']}"
        return "0-0"

    away_record = get_record_at_date(game_info['away_team'], current_game_date, season_start_date)
    home_record = get_record_at_date(game_info['home_team'], current_game_date, season_start_date)

    cursor.execute("""
        SELECT 
            stat_id, 
            player_name,
            started,
            minutes,
            fg_made,
            fg_att,
            tp_made,
            tp_att,
            ft_made,
            ft_att,
            rebounds,
            assists,
            steals,
            blocks,
            turnovers,
            points
        FROM player_stats
        WHERE game_id = ? AND team = ?
        ORDER BY started DESC, stat_id ASC
    """, (game_id, team_name))
    
    players = cursor.fetchall()
    
    opponent = game_info['away_team'] if game_info['home_team'] == team_name else game_info['home_team']
    
    cursor.execute("""
        SELECT 
            stat_id,
            player_name,
            started,
            minutes,
            fg_made,
            fg_att,
            tp_made,
            tp_att,
            ft_made,
            ft_att,
            rebounds,
            assists,
            steals,
            blocks,
            turnovers,
            points
        FROM player_stats
        WHERE game_id = ? AND team = ?
        ORDER BY started DESC, stat_id ASC
    """, (game_id, opponent))
    
    opponent_players = cursor.fetchall()
    
    cursor.execute("""
        SELECT 
            team_name,
            fg_made,
            fg_att,
            tp_made,
            tp_att,
            ft_made,
            ft_att,
            rebounds,
            assists,
            steals,
            blocks,
            turnovers,
            points
        FROM team_stats
        WHERE game_id = ?
    """, (game_id,))
    
    team_totals = cursor.fetchall()
    conn.close()
    
    team_total = None
    opponent_total = None
    for total in team_totals:
        if total['team_name'] == team_name:
            team_total = total
        else:
            opponent_total = total
    
    return {
        'game_info': game_info,
        'team_name': team_name,
        'opponent': opponent,
        'team_players': players,
        'opponent_players': opponent_players,
        'team_total': team_total,
        'opponent_total': opponent_total,
        'home_record': home_record,
        'away_record': away_record
    }

def get_team_draft_picks(team_name):
    primary_name = get_primary_franchise_name(team_name)

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

    owned_picks = []

    pick_columns = [
        ('1Y26', '1Y26C', 2026, 1),
        ('2Y26', '2Y26C', 2026, 2),
        ('1Y27', '1Y27C', 2027, 1),
        ('2Y27', '2Y27C', 2027, 2),
        ('1Y28', '1Y28C', 2028, 1),
        ('2Y28', '2Y28C', 2028, 2),
        ('1Y29', '1Y29C', 2029, 1),
        ('2Y29', '2Y29C', 2029, 2),
    ]

    for row in rows:
        original_team = row['team']

        for owner_col, condition_col, year, round_num in pick_columns:
            owner = row[owner_col]
            condition = row[condition_col]

            if owner == primary_name:
                owned_picks.append({
                    'year': year,
                    'round': round_num,
                    'original_team': original_team,
                    'condition': condition,
                    'is_own_pick': original_team == primary_name
                })

    owned_picks.sort(key=lambda x: (x['year'], x['round'], not x['is_own_pick'], x['original_team']))

    return owned_picks

def get_all_team_stats(season=None, season_type='regular', per_mode='per_game', season_segment='all'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not season:
        cursor.execute("SELECT MAX(game_date) as latest_date FROM games")
        result = cursor.fetchone()
        if result and result['latest_date']:
            season = get_season_from_date(result['latest_date'])
        else:
            conn.close()
            return []
    
    season_start_year = int(season.split('-')[0])
    season_end_year = season_start_year + 1
    season_start = f"{season_start_year}-07-01"
    season_end = f"{season_end_year}-06-30"
    
    if season_type == 'playoffs':
        playoff_start = f"{season_end_year}-04-20"
        date_filter = f"AND g.game_date >= '{playoff_start}'"
    else:
        playoff_start = f"{season_end_year}-04-20"
        date_filter = f"AND g.game_date < '{playoff_start}'"
    
    limit_clause = ""
    is_ranked_query = False
    
    if season_segment == 'last5':
        limit_clause = "WHERE rn <= 5"
        is_ranked_query = True
    elif season_segment == 'last10':
        limit_clause = "WHERE rn <= 10"
        is_ranked_query = True
    
    segment_filter = ""
    if season_segment == 'pre_allstar':
        allstar_date = f"{season_end_year}-02-18"
        segment_filter = f"AND g.game_date < '{allstar_date}'"
    elif season_segment == 'post_allstar':
        allstar_date = f"{season_end_year}-02-18"
        segment_filter = f"AND g.game_date >= '{allstar_date}'"
    elif season_segment in ['nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may']:
        month_map = {
            'nov': (11, season_start_year),
            'dec': (12, season_start_year),
            'jan': (1, season_end_year),
            'feb': (2, season_end_year),
            'mar': (3, season_end_year),
            'apr': (4, season_end_year),
            'may': (5, season_end_year)
        }
        month_num, year = month_map[season_segment]
        segment_filter = f"AND strftime('%Y-%m', g.game_date) = '{year}-{month_num:02d}'"
    
    if is_ranked_query:
        query = f"""
            WITH RankedGames AS (
                SELECT 
                    ts.*,
                    g.game_date,
                    g.home_team,
                    g.away_team,
                    g.home_score,
                    g.away_score,
                    ROW_NUMBER() OVER (PARTITION BY ts.team_name ORDER BY g.game_date DESC) as rn
                FROM team_stats ts
                JOIN games g ON ts.game_id = g.game_id
                WHERE g.game_date >= ?
                AND g.game_date <= ?
                {date_filter}
            )
            SELECT 
                team_name,
                COUNT(DISTINCT game_id) as games_played,
                SUM(win) as wins,
                SUM(CASE WHEN win = 0 THEN 1 ELSE 0 END) as losses,
                SUM(points) as total_points,
                SUM(fg_made) as total_fg_made,
                SUM(fg_att) as total_fg_att,
                SUM(tp_made) as total_3pm,
                SUM(tp_att) as total_3pa,
                SUM(ft_made) as total_ftm,
                SUM(ft_att) as total_fta,
                SUM(rebounds) as total_reb,
                SUM(assists) as total_ast,
                SUM(turnovers) as total_tov,
                SUM(steals) as total_stl,
                SUM(blocks) as total_blk,
                SUM(CASE 
                    WHEN team_name = home_team THEN (home_score - away_score) 
                    ELSE (away_score - home_score) 
                END) as total_plus_minus
            FROM RankedGames
            {limit_clause}
            GROUP BY team_name
            ORDER BY wins DESC, team_name ASC
        """
    else:
        query = f"""
            SELECT 
                ts.team_name,
                COUNT(DISTINCT ts.game_id) as games_played,
                SUM(ts.win) as wins,
                SUM(CASE WHEN ts.win = 0 THEN 1 ELSE 0 END) as losses,
                SUM(ts.points) as total_points,
                SUM(ts.fg_made) as total_fg_made,
                SUM(ts.fg_att) as total_fg_att,
                SUM(ts.tp_made) as total_3pm,
                SUM(ts.tp_att) as total_3pa,
                SUM(ts.ft_made) as total_ftm,
                SUM(ts.ft_att) as total_fta,
                SUM(ts.rebounds) as total_reb,
                SUM(ts.assists) as total_ast,
                SUM(ts.turnovers) as total_tov,
                SUM(ts.steals) as total_stl,
                SUM(ts.blocks) as total_blk,
                SUM(CASE 
                    WHEN ts.team_name = g.home_team THEN (g.home_score - g.away_score) 
                    ELSE (g.away_score - g.home_score) 
                END) as total_plus_minus
            FROM team_stats ts
            JOIN games g ON ts.game_id = g.game_id
            WHERE g.game_date >= ?
            AND g.game_date <= ?
            {date_filter}
            {segment_filter}
            GROUP BY ts.team_name
            ORDER BY wins DESC, ts.team_name ASC
        """
    
    cursor.execute(query, (season_start, season_end))
    teams = cursor.fetchall()
    conn.close()
    
    team_stats = []
    for team in teams:
        games = team['games_played']
        if games == 0:
            continue
        
        wins = team['wins']
        losses = team['losses']
        win_pct = round(wins / games, 3) if games > 0 else 0
        
        if per_mode == 'per_game':
            pts = round(team['total_points'] / games, 1)
            fgm = round(team['total_fg_made'] / games, 1)
            fga = round(team['total_fg_att'] / games, 1)
            tpm = round(team['total_3pm'] / games, 1)
            tpa = round(team['total_3pa'] / games, 1)
            ftm = round(team['total_ftm'] / games, 1)
            fta = round(team['total_fta'] / games, 1)
            reb = round(team['total_reb'] / games, 1)
            ast = round(team['total_ast'] / games, 1)
            tov = round(team['total_tov'] / games, 1)
            stl = round(team['total_stl'] / games, 1)
            blk = round(team['total_blk'] / games, 1)
            plus_minus = round(team['total_plus_minus'] / games, 1)
        else:
            pts = team['total_points']
            fgm = team['total_fg_made']
            fga = team['total_fg_att']
            tpm = team['total_3pm']
            tpa = team['total_3pa']
            ftm = team['total_ftm']
            fta = team['total_fta']
            reb = team['total_reb']
            ast = team['total_ast']
            tov = team['total_tov']
            stl = team['total_stl']
            blk = team['total_blk']
            plus_minus = team['total_plus_minus']
        
        fg_pct = round((team['total_fg_made'] / team['total_fg_att'] * 100), 1) if team['total_fg_att'] > 0 else 0
        tp_pct = round((team['total_3pm'] / team['total_3pa'] * 100), 1) if team['total_3pa'] > 0 else 0
        ft_pct = round((team['total_ftm'] / team['total_fta'] * 100), 1) if team['total_fta'] > 0 else 0
        
        team_stats.append({
            'team_name': team['team_name'],
            'gp': games,
            'wins': wins,
            'losses': losses,
            'win_pct': win_pct,
            'pts': pts,
            'fgm': fgm,
            'fga': fga,
            'fg_pct': fg_pct,
            'tpm': tpm,
            'tpa': tpa,
            'tp_pct': tp_pct,
            'ftm': ftm,
            'fta': fta,
            'ft_pct': ft_pct,
            'reb': reb,
            'ast': ast,
            'tov': tov,
            'stl': stl,
            'blk': blk,
            'plus_minus': plus_minus
        })
    
    team_stats.sort(key=lambda x: (-x['win_pct'], x['team_name']))
    return team_stats