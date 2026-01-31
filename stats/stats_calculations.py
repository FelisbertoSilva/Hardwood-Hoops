from database.db_helpers import get_db_connection
from stats.stat_formulas import get_season_from_date
from stats.standings_calculations import get_available_seasons as get_available_seasons_for_players

def get_stats_leaders(season=None):

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT season FROM player_stats ORDER BY season DESC LIMIT 1")
    result = cursor.fetchone()
    season = result['season'] if result else None
    
    if season is None:
        return {
            'points_per_game': [],
            'rebounds_per_game': [],
            'assists_per_game': [],
            'blocks_per_game': [],
            'steals_per_game': [],
            'field_goal_percentage': [],
            'three_pointers_made': [],
            'three_point_percentage': [],
            'free_throw_percentage': []
        }
    
    cursor.execute("""
        SELECT COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        ORDER BY games_played DESC
        LIMIT 1
    """, (season,))
    
    max_games_result = cursor.fetchone()
    max_games = max_games_result['games_played'] if max_games_result else 0
    if max_games < 20:
        min_games = 0  
    else:
        min_games = int(max_games * 0.70)
    
    leaders = {}
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(AVG(points), 1) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['points_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(AVG(rebounds), 1) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['rebounds_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(AVG(assists), 1) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['assists_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(AVG(blocks), 1) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['blocks_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(AVG(steals), 1) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['steals_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(100.0 * SUM(fg_made) / NULLIF(SUM(fg_att), 0), 1) as value,
               COUNT(*) as games_played,
               SUM(fg_att) as total_attempts
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ? AND total_attempts >= 50
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['field_goal_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               SUM(tp_made) as value,
               COUNT(*) as games_played
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ?
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['three_pointers_made'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(100.0 * SUM(tp_made) / NULLIF(SUM(tp_att), 0), 1) as value,
               COUNT(*) as games_played,
               SUM(tp_att) as total_attempts
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ? AND total_attempts >= 25
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['three_point_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT player_name, team, 
               ROUND(100.0 * SUM(ft_made) / NULLIF(SUM(ft_att), 0), 1) as value,
               COUNT(*) as games_played,
               SUM(ft_att) as total_attempts
        FROM player_stats
        WHERE season = ? AND minutes > 0
        GROUP BY player_name
        HAVING games_played >= ? AND total_attempts >= 20
        ORDER BY value DESC
        LIMIT 5
    """, (season, min_games))
    leaders['free_throw_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return leaders


def get_tonight_leaders():

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT game_date 
        FROM games 
        ORDER BY game_date DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        return {
            'points_per_game': [],
            'rebounds_per_game': [],
            'assists_per_game': [],
            'blocks_per_game': [],
            'steals_per_game': [],
            'field_goal_percentage': [],
            'three_pointers_made': [],
            'three_point_percentage': [],
            'free_throw_percentage': []
        }
    
    latest_date = result['game_date']
    
    leaders = {}
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.points as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.points DESC
        LIMIT 5
    """, (latest_date,))
    leaders['points_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.rebounds as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.rebounds DESC
        LIMIT 5
    """, (latest_date,))
    leaders['rebounds_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.assists as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.assists DESC
        LIMIT 5
    """, (latest_date,))
    leaders['assists_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.blocks as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.blocks DESC
        LIMIT 5
    """, (latest_date,))
    leaders['blocks_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.steals as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.steals DESC
        LIMIT 5
    """, (latest_date,))
    leaders['steals_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, 
               ROUND(100.0 * ps.fg_made / NULLIF(ps.fg_att, 0), 1) as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0 AND ps.fg_att >= 5
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['field_goal_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, ps.tp_made as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0
        ORDER BY ps.tp_made DESC
        LIMIT 5
    """, (latest_date,))
    leaders['three_pointers_made'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, 
               ROUND(100.0 * ps.tp_made / NULLIF(ps.tp_att, 0), 1) as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0 AND ps.tp_att >= 3
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['three_point_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ps.player_name, ps.team, 
               ROUND(100.0 * ps.ft_made / NULLIF(ps.ft_att, 0), 1) as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE g.game_date = ? AND ps.minutes > 0 AND ps.ft_att >= 3
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['free_throw_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return leaders


def get_team_season_leaders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT season FROM team_stats ORDER BY season DESC LIMIT 1")
    result = cursor.fetchone()
    season = result['season'] if result else None
    
    if season is None:
        return {
            'points_per_game': [],
            'rebounds_per_game': [],
            'assists_per_game': [],
            'blocks_per_game': [],
            'steals_per_game': [],
            'field_goal_percentage': [],
            'three_pointers_made': [],
            'three_point_percentage': [],
            'free_throw_percentage': []
        }
    
    leaders = {}
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(AVG(points), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['points_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(AVG(rebounds), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['rebounds_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(AVG(assists), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['assists_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(AVG(blocks), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['blocks_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(AVG(steals), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['steals_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(100.0 * SUM(fg_made) / NULLIF(SUM(fg_att), 0), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['field_goal_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               SUM(tp_made) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['three_pointers_made'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(100.0 * SUM(tp_made) / NULLIF(SUM(tp_att), 0), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['three_point_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT team_name, 
               ROUND(100.0 * SUM(ft_made) / NULLIF(SUM(ft_att), 0), 1) as value,
               COUNT(*) as games_played
        FROM team_stats
        WHERE season = ?
        GROUP BY team_name
        ORDER BY value DESC
        LIMIT 5
    """, (season,))
    leaders['free_throw_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return leaders


def get_team_tonight_leaders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT game_date 
        FROM games 
        ORDER BY game_date DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        return {
            'points_per_game': [],
            'rebounds_per_game': [],
            'assists_per_game': [],
            'blocks_per_game': [],
            'steals_per_game': [],
            'field_goal_percentage': [],
            'three_pointers_made': [],
            'three_point_percentage': [],
            'free_throw_percentage': []
        }
    
    latest_date = result['game_date']
    
    leaders = {}
    
    cursor.execute("""
        SELECT ts.team_name, ts.points as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.points DESC
        LIMIT 5
    """, (latest_date,))
    leaders['points_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, ts.rebounds as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.rebounds DESC
        LIMIT 5
    """, (latest_date,))
    leaders['rebounds_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, ts.assists as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.assists DESC
        LIMIT 5
    """, (latest_date,))
    leaders['assists_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, ts.blocks as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.blocks DESC
        LIMIT 5
    """, (latest_date,))
    leaders['blocks_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, ts.steals as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.steals DESC
        LIMIT 5
    """, (latest_date,))
    leaders['steals_per_game'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, 
               ROUND(100.0 * ts.fg_made / NULLIF(ts.fg_att, 0), 1) as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['field_goal_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, ts.tp_made as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY ts.tp_made DESC
        LIMIT 5
    """, (latest_date,))
    leaders['three_pointers_made'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, 
               ROUND(100.0 * ts.tp_made / NULLIF(ts.tp_att, 0), 1) as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['three_point_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT ts.team_name, 
               ROUND(100.0 * ts.ft_made / NULLIF(ts.ft_att, 0), 1) as value
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date = ?
        ORDER BY value DESC
        LIMIT 5
    """, (latest_date,))
    leaders['free_throw_percentage'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return leaders


def get_all_player_stats(season=None, season_type='regular', per_mode='per_game', season_segment='all', sort_by='pts', sort_order='desc'):
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
    

    rank_limit_clause = ""
    
    if season_segment == 'last5':
        rank_limit_clause = "WHERE rn <= 5"
    elif season_segment == 'last10':
        rank_limit_clause = "WHERE rn <= 10"
    
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
    
    query = f"""
        WITH BaseStats AS (
            SELECT 
                ps.*,
                g.game_date,
                ROW_NUMBER() OVER (PARTITION BY ps.player_name ORDER BY g.game_date DESC) as rn
            FROM player_stats ps
            JOIN games g ON ps.game_id = g.game_id
            WHERE g.game_date >= ?
            AND g.game_date <= ?
            {date_filter}
            {segment_filter}
        )
        SELECT 
            player_name,
            -- Select the team from the most recent game (where rank is 1)
            MAX(CASE WHEN rn = 1 THEN team END) as team,
            COUNT(DISTINCT game_id) as games_played,
            SUM(minutes) as total_minutes,
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
            SUM(blocks) as total_blk
        FROM BaseStats
        {rank_limit_clause}
        GROUP BY player_name
        ORDER BY total_points DESC, player_name ASC
    """
    
    cursor.execute(query, (season_start, season_end))
    players = cursor.fetchall()
    conn.close()
    
    player_stats = []
    for player in players:
        games = player['games_played']
        if games == 0:
            continue
        
        if per_mode == 'per_game':
            min_avg = round(player['total_minutes'] / games, 1)
            pts = round(player['total_points'] / games, 1)
            fgm = round(player['total_fg_made'] / games, 1)
            fga = round(player['total_fg_att'] / games, 1)
            tpm = round(player['total_3pm'] / games, 1)
            tpa = round(player['total_3pa'] / games, 1)
            ftm = round(player['total_ftm'] / games, 1)
            fta = round(player['total_fta'] / games, 1)
            reb = round(player['total_reb'] / games, 1)
            ast = round(player['total_ast'] / games, 1)
            tov = round(player['total_tov'] / games, 1)
            stl = round(player['total_stl'] / games, 1)
            blk = round(player['total_blk'] / games, 1)
        else:  
            min_avg = player['total_minutes']
            pts = player['total_points']
            fgm = player['total_fg_made']
            fga = player['total_fg_att']
            tpm = player['total_3pm']
            tpa = player['total_3pa']
            ftm = player['total_ftm']
            fta = player['total_fta']
            reb = player['total_reb']
            ast = player['total_ast']
            tov = player['total_tov']
            stl = player['total_stl']
            blk = player['total_blk']
        
        fg_pct = round((player['total_fg_made'] / player['total_fg_att'] * 100), 1) if player['total_fg_att'] > 0 else 0
        tp_pct = round((player['total_3pm'] / player['total_3pa'] * 100), 1) if player['total_3pa'] > 0 else 0
        ft_pct = round((player['total_ftm'] / player['total_fta'] * 100), 1) if player['total_fta'] > 0 else 0
        
        player_stats.append({
            'player_name': player['player_name'],
            'team': player['team'],
            'gp': games,
            'min': min_avg,
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
            'blk': blk
        })
    
    sort_key_map = {
        'pts': 'pts',
        'ast': 'ast',
        'reb': 'reb',
        'stl': 'stl',
        'blk': 'blk',
        'gp': 'gp',
        'min': 'min',
        'fgm': 'fgm',
        'fga': 'fga',
        'fg_pct': 'fg_pct',
        'tpm': 'tpm',
        'tpa': 'tpa',
        'tp_pct': 'tp_pct',
        'ftm': 'ftm',
        'fta': 'fta',
        'ft_pct': 'ft_pct',
        'tov': 'tov',
        'player_name': 'player_name',
        'team': 'team'
    }

    sort_key = sort_key_map.get(sort_by, 'pts')
    reverse_sort = sort_order == 'desc'

    if sort_key in ['player_name', 'team']:
        reverse_sort = sort_order == 'desc'
        player_stats.sort(key=lambda x: (x[sort_key] or '').lower(), reverse=reverse_sort)
    else:
        player_stats.sort(key=lambda x: (-x[sort_key] if reverse_sort else x[sort_key], x['player_name']))

    return player_stats
