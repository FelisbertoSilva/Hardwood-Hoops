from database.db_helpers import get_db_connection
from stats.stat_formulas import get_season_from_date
from stats.standings_calculations import calculate_league_standings
from stats.playoff_calculations import get_playoff_bracket


def calculate_gms(points, rebounds, assists, steals, blocks, turnovers, fg_att, ft_att, tp_made, minutes): #MVP
    return (
        (points * 1.0) +
        (rebounds * 0.5) +
        (assists * 1.4) +
        (steals * 1.0) +
        (blocks * 0.8) -
        (turnovers * 1.2) -
        (fg_att * 0.4) -
        (ft_att * 0.2) +
        (tp_made * 0.5) +
        (minutes * 0.05)
    )


def calculate_dps(steals, blocks, rebounds, opponent_points, player_won): #DPOY
    base_dps = (steals * 1.0) + (blocks * 1.5) + (rebounds * 0.25)

    if opponent_points > 0:
        opponent_factor = 100 / opponent_points
    else:
        opponent_factor = 1.0

    win_multiplier = 1.5 if player_won else 1.0

    return base_dps * opponent_factor * win_multiplier


def get_award_winners():
    conn = get_db_connection()
    cursor = conn.cursor()

    awards = {
        'mvp': [],
        'dpoy': [],
        'roy': [],
        'smoy': [],
        'mip': [],
        'all_hh_1st': [],
        'all_hh_2nd': [],
        'all_hh_3rd': [],
        'all_defensive_1st': [],
        'all_defensive_2nd': [],
        'all_rookie_1st': [],
        'all_rookie_2nd': [],
        'all_star': [],       
        'finals_mvp': []       
    }

    #Mapa Conferencias
    east_teams = set()
    west_teams = set()

    divisions = {
        'Atlantic': ['Boston Celtics', 'Brooklyn Nets', 'Montreal Mastodons', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors'],
        'Central': ['Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks'],
        'Southeast': ['Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards'],
        'Northwest': ['Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trailblazers', 'Utah Jazz'],
        'Pacific': ['Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings'],
        'Southwest': ['Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans', 'San Antonio Spurs', 'San Diego Caravels']
    }

    for team in divisions['Atlantic'] + divisions['Central'] + divisions['Southeast']:
        east_teams.add(team)
    
    for team in divisions['Northwest'] + divisions['Pacific'] + divisions['Southwest']:
        west_teams.add(team)

    # Min. Jogos
    player_season_gms = {}
    player_season_games = {}

    cursor.execute("""
        SELECT DISTINCT
            CASE
                WHEN CAST(strftime('%m', game_date) AS INTEGER) >= 7
                THEN CAST(strftime('%Y', game_date) AS INTEGER)
                ELSE CAST(strftime('%Y', game_date) AS INTEGER) - 1
            END as season_year
        FROM games
        ORDER BY season_year ASC
    """)
    seasons = [row['season_year'] for row in cursor.fetchall()]

    for season_start_year in seasons:
        season_end_year = season_start_year + 1
        season_start = f"{season_start_year}-07-01"
        playoff_start = f"{season_end_year}-04-20"
        all_star_cutoff = f"{season_end_year}-02-18"
        season_display = f"{season_start_year}-{str(season_end_year)[-2:]}"

        # 82 Game Check
        cursor.execute("""
            SELECT COUNT(*) as games_played
            FROM player_stats ps
            JOIN games g ON ps.game_id = g.game_id
            WHERE g.game_date >= ? AND g.game_date < ? AND ps.minutes > 0
            GROUP BY ps.player_name
            ORDER BY games_played DESC
            LIMIT 1
        """, (season_start, playoff_start))
        
        max_res = cursor.fetchone()
        if not max_res or max_res['games_played'] < 82:
            continue

        cursor.execute("""
            SELECT
                ps.player_name, ps.team,
                ps.points, ps.rebounds, ps.assists, ps.steals, ps.blocks,
                ps.turnovers, ps.fg_att, ps.ft_att, ps.tp_made, ps.minutes,
                ps.started,
                g.game_date,
                CASE WHEN (ps.team = g.home_team AND g.home_score > g.away_score) OR (ps.team = g.away_team AND g.away_score > g.home_score) THEN 1 ELSE 0 END as player_won,
                CASE WHEN ps.team = g.home_team THEN g.away_score ELSE g.home_score END as opponent_points
            FROM player_stats ps
            JOIN games g ON ps.game_id = g.game_id
            WHERE g.game_date >= ? AND g.game_date < ? AND ps.minutes > 0
            ORDER BY g.game_date ASC
        """, (season_start, playoff_start))

        players_stats = cursor.fetchall()

        player_gms = {}
        player_dps = {}
        player_as_gms = {} 
        player_teams = {}
        player_last_as_team = {}
        player_last_as_date = {}
        player_starts = {}
        player_bench = {}
        player_games = {}

        for p in players_stats:
            name = p['player_name']
            
            gms = calculate_gms(p['points'], p['rebounds'], p['assists'], p['steals'], p['blocks'], p['turnovers'], p['fg_att'], p['ft_att'], p['tp_made'], p['minutes'])
            dps = calculate_dps(p['steals'], p['blocks'], p['rebounds'], p['opponent_points'], p['player_won'] == 1)
            if p['player_won'] == 1: gms *= 1.5

            if name not in player_gms:
                player_gms[name] = 0; player_dps[name] = 0; player_as_gms[name] = 0
                player_teams[name] = p['team']; player_starts[name] = 0
                player_bench[name] = 0; player_games[name] = 0
                player_last_as_date[name] = "0000-00-00"

            player_gms[name] += gms
            player_dps[name] += dps
            player_teams[name] = p['team']
            player_games[name] += 1
            if p['started'] == 1: player_starts[name] += 1
            else: player_bench[name] += 1

            if p['game_date'] < all_star_cutoff:
                player_as_gms[name] += gms
                if p['game_date'] >= player_last_as_date[name]:
                    player_last_as_date[name] = p['game_date']
                    player_last_as_team[name] = p['team']

        for name, gms in player_gms.items():
            if name not in player_season_gms: player_season_gms[name] = {}
            player_season_gms[name][season_start_year] = gms
            if name not in player_season_games: player_season_games[name] = {}
            player_season_games[name][season_start_year] = player_games[name]

        #Prémios
        def format_award(p_name, p_team, score_val=0):
            return {'season': season_display, 'player_name': p_name, 'team': p_team, 'score': round(score_val, 2)}

        # MVP
        if player_gms:
            mvp = max(player_gms, key=player_gms.get)
            awards['mvp'].append({'season': season_display, 'player_name': mvp, 'team': player_teams[mvp], 'total_gms': round(player_gms[mvp], 2)})

        # DPOY
        if player_dps:
            dpoy = max(player_dps, key=player_dps.get)
            awards['dpoy'].append({'season': season_display, 'player_name': dpoy, 'team': player_teams[dpoy], 'total_dps': round(player_dps[dpoy], 2)})

        # 6MOY
        cands_6man = {n: g for n, g in player_gms.items() if player_bench.get(n,0) > player_starts.get(n,0)}
        if cands_6man:
            smoy = max(cands_6man, key=cands_6man.get)
            awards['smoy'].append(format_award(smoy, player_teams[smoy], cands_6man[smoy]))

        # ROY
        cursor.execute("SELECT player_name, MIN(game_date) as fd FROM player_stats ps JOIN games g ON ps.game_id=g.game_id GROUP BY player_name")
        first_games = cursor.fetchall()
        rookies = set()
        for row in first_games:
            y = int(row['fd'][:4]); m = int(row['fd'][5:7])
            if (y if m>=7 else y-1) == season_start_year: rookies.add(row['player_name'])
        
        rookie_stats = {n: g for n, g in player_gms.items() if n in rookies}
        if rookie_stats:
            if season_start_year == 2023:
                vic = {n: g for n, g in rookie_stats.items() if 'Victor' in n}
                roy = max(vic, key=vic.get) if vic else max(rookie_stats, key=rookie_stats.get)
            else:
                roy = max(rookie_stats, key=rookie_stats.get)
            awards['roy'].append(format_award(roy, player_teams[roy], rookie_stats[roy]))

        # MIP
        prev_yr = season_start_year - 1
        mip_cands = {}
        for n, gms in player_gms.items():
            if n in rookies or player_games[n] < 65: continue
            prev_g = player_season_gms.get(n, {}).get(prev_yr, 0)
            prev_gp = player_season_games.get(n, {}).get(prev_yr, 0)
            if prev_gp >= 65:
                mip_cands[n] = (gms/player_games[n]) - (prev_g/prev_gp)
        if mip_cands:
            mip = max(mip_cands, key=mip_cands.get)
            awards['mip'].append({'season': season_display, 'player_name': mip, 'team': player_teams[mip], 'improvement': round(mip_cands[mip], 2)})

        # HH_Teams
        sorted_gms = sorted(player_gms.items(), key=lambda x: x[1], reverse=True)
        awards['all_hh_1st'].extend([format_award(n, player_teams[n], s) for n, s in sorted_gms[0:5]])
        awards['all_hh_2nd'].extend([format_award(n, player_teams[n], s) for n, s in sorted_gms[5:10]])
        awards['all_hh_3rd'].extend([format_award(n, player_teams[n], s) for n, s in sorted_gms[10:15]])

        sorted_dps = sorted(player_dps.items(), key=lambda x: x[1], reverse=True)
        awards['all_defensive_1st'].extend([format_award(n, player_teams[n], s) for n, s in sorted_dps[0:5]])
        awards['all_defensive_2nd'].extend([format_award(n, player_teams[n], s) for n, s in sorted_dps[5:10]])

        # All-Rookie (2024+)
        if season_start_year >= 2024:
            sorted_rookies = sorted(rookie_stats.items(), key=lambda x: x[1], reverse=True)
            awards['all_rookie_1st'].extend([format_award(n, player_teams[n], s) for n, s in sorted_rookies[0:5]])
            awards['all_rookie_2nd'].extend([format_award(n, player_teams[n], s) for n, s in sorted_rookies[5:10]])

        as_candidates = [
            (name, score) for name, score in player_as_gms.items() 
            if score > 0 and name in player_last_as_team
        ]
        
        as_candidates.sort(key=lambda x: x[1], reverse=True)

        east_roster = []
        west_roster = []

        for name, score in as_candidates:
            team_at_break = player_last_as_team[name]
            
            if team_at_break in east_teams:
                if len(east_roster) < 12:
                    east_roster.append(format_award(name, team_at_break, score))
            elif team_at_break in west_teams:
                if len(west_roster) < 12:
                    west_roster.append(format_award(name, team_at_break, score))
            
            if len(east_roster) == 12 and len(west_roster) == 12:
                break

        awards['all_star'].extend(east_roster)
        awards['all_star'].extend(west_roster)

        #FINALS MVP
        try:
            standings = calculate_league_standings(season_display)
            bracket = get_playoff_bracket(season_display, standings['Eastern'], standings['Western'])

            if bracket and 'Finals' in bracket:
                finals = bracket['Finals']
                if finals and finals.get('mvp'):
                    mvp_data = finals['mvp']
                    mvp_name = mvp_data.get('name') if isinstance(mvp_data, dict) else mvp_data
                    mvp_team = finals.get('winner', '')
                    if mvp_name:
                        awards['finals_mvp'].append({
                            'player_name': mvp_name,
                            'team': mvp_team,
                            'season': season_display,
                            'score': 0
                        })
        except Exception:
            pass

    conn.close()
    
    for k in awards:
        awards[k].reverse()
        
    return awards


def get_single_game_player_records(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor()

    records = {}

    reg_season_filter = """
        AND NOT (
            (CAST(strftime('%m', g.game_date) AS INTEGER) = 4 AND CAST(strftime('%d', g.game_date) AS INTEGER) >= 20)
            OR CAST(strftime('%m', g.game_date) AS INTEGER) IN (5, 6)
        )
    """

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.points as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.points DESC
        LIMIT ?
    """, (limit,))
    records['points'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.rebounds as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.rebounds DESC
        LIMIT ?
    """, (limit,))
    records['rebounds'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.assists as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.assists DESC
        LIMIT ?
    """, (limit,))
    records['assists'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.steals as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.steals DESC
        LIMIT ?
    """, (limit,))
    records['steals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.blocks as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.blocks DESC
        LIMIT ?
    """, (limit,))
    records['blocks'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.tp_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.tp_made DESC
        LIMIT ?
    """, (limit,))
    records['three_pointers'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.ft_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.ft_made DESC
        LIMIT ?
    """, (limit,))
    records['free_throws'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.fg_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.fg_made DESC
        LIMIT ?
    """, (limit,))
    records['field_goals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.minutes as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        ORDER BY ps.minutes DESC
        LIMIT ?
    """, (limit,))
    records['minutes'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records


def get_career_player_records(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor()

    records = {}

    # Regular season
    reg_season_filter = """
        AND NOT (
            (CAST(strftime('%m', g.game_date) AS INTEGER) = 4 AND CAST(strftime('%d', g.game_date) AS INTEGER) >= 20)
            OR CAST(strftime('%m', g.game_date) AS INTEGER) IN (5, 6)
        )
    """

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.points) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['points'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.rebounds) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['rebounds'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.assists) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['assists'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.steals) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['steals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.blocks) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['blocks'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.tp_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['three_pointers'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.ft_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['free_throws'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.fg_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['field_goals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            COUNT(*) as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['games_played'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.minutes) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {reg_season_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['minutes'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records


def get_team_season_records(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor()

    records = {}

    cursor.execute("""
        SELECT
            ts.team_name,
            SUM(ts.win) as wins,
            COUNT(*) - SUM(ts.win) as losses,
            COUNT(*) as games_played,
            ts.season
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE (
            -- Regular season: before April 20 of the ending year
            CAST(strftime('%m', g.game_date) AS INTEGER) < 4
            OR (CAST(strftime('%m', g.game_date) AS INTEGER) = 4 AND CAST(strftime('%d', g.game_date) AS INTEGER) < 20)
            OR CAST(strftime('%m', g.game_date) AS INTEGER) >= 7
        )
        GROUP BY ts.team_name, ts.season
        ORDER BY wins DESC
        LIMIT ?
    """, (limit,))
    records['most_wins'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT
            ts.team_name,
            ts.points as value,
            g.game_date,
            CASE
                WHEN ts.team_name = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent,
            CASE
                WHEN ts.team_name = g.home_team THEN g.away_score
                ELSE g.home_score
            END as opponent_score
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        ORDER BY ts.points DESC
        LIMIT ?
    """, (limit,))
    records['most_points_game'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records


def get_team_streak_records(limit=10):
    """
    Get team streak records:
    - Longest winning streaks
    - Longest losing streaks
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ts.team_name,
            g.game_date,
            ts.win
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        ORDER BY ts.team_name, g.game_date
    """)

    games = cursor.fetchall()
    conn.close()

    win_streaks = []
    loss_streaks = []

    if not games:
        return {'win_streaks': [], 'loss_streaks': []}

    current_team = None
    current_streak = 0
    streak_type = None  
    streak_start = None
    streak_end = None

    for game in games:
        team = game['team_name']
        date = game['game_date']
        won = game['win'] == 1

        if team != current_team:
            if current_team and current_streak > 0:
                if streak_type == 'win':
                    win_streaks.append({
                        'team_name': current_team,
                        'streak': current_streak,
                        'start_date': streak_start,
                        'end_date': streak_end
                    })
                else:
                    loss_streaks.append({
                        'team_name': current_team,
                        'streak': current_streak,
                        'start_date': streak_start,
                        'end_date': streak_end
                    })

            current_team = team
            current_streak = 1
            streak_type = 'win' if won else 'loss'
            streak_start = date
            streak_end = date
        else:
            current_game_type = 'win' if won else 'loss'

            if current_game_type == streak_type:
                current_streak += 1
                streak_end = date
            else:
                if streak_type == 'win':
                    win_streaks.append({
                        'team_name': current_team,
                        'streak': current_streak,
                        'start_date': streak_start,
                        'end_date': streak_end
                    })
                else:
                    loss_streaks.append({
                        'team_name': current_team,
                        'streak': current_streak,
                        'start_date': streak_start,
                        'end_date': streak_end
                    })

                current_streak = 1
                streak_type = current_game_type
                streak_start = date
                streak_end = date

    if current_team and current_streak > 0:
        if streak_type == 'win':
            win_streaks.append({
                'team_name': current_team,
                'streak': current_streak,
                'start_date': streak_start,
                'end_date': streak_end
            })
        else:
            loss_streaks.append({
                'team_name': current_team,
                'streak': current_streak,
                'start_date': streak_start,
                'end_date': streak_end
            })

    win_streaks.sort(key=lambda x: x['streak'], reverse=True)
    loss_streaks.sort(key=lambda x: x['streak'], reverse=True)

    return {
        'win_streaks': win_streaks[:limit],
        'loss_streaks': loss_streaks[:limit]
    }


def get_playoff_single_game_player_records(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()

    records = {}

    playoff_filter = """
        AND (
            (CAST(strftime('%m', g.game_date) AS INTEGER) = 4 AND CAST(strftime('%d', g.game_date) AS INTEGER) >= 20)
            OR CAST(strftime('%m', g.game_date) AS INTEGER) IN (5, 6)
        )
    """

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.points as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.points DESC
        LIMIT ?
    """, (limit,))
    records['points'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.rebounds as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.rebounds DESC
        LIMIT ?
    """, (limit,))
    records['rebounds'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.assists as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.assists DESC
        LIMIT ?
    """, (limit,))
    records['assists'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.steals as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.steals DESC
        LIMIT ?
    """, (limit,))
    records['steals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.blocks as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.blocks DESC
        LIMIT ?
    """, (limit,))
    records['blocks'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.tp_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.tp_made DESC
        LIMIT ?
    """, (limit,))
    records['three_pointers'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.ft_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.ft_made DESC
        LIMIT ?
    """, (limit,))
    records['free_throws'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            ps.team,
            ps.fg_made as value,
            g.game_date,
            CASE
                WHEN ps.team = g.home_team THEN g.away_team
                ELSE g.home_team
            END as opponent
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        ORDER BY ps.fg_made DESC
        LIMIT ?
    """, (limit,))
    records['field_goals'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records


def get_playoff_career_player_records(limit=10):

    conn = get_db_connection()
    cursor = conn.cursor()

    records = {}

    playoff_filter = """
        AND (
            (CAST(strftime('%m', g.game_date) AS INTEGER) = 4 AND CAST(strftime('%d', g.game_date) AS INTEGER) >= 20)
            OR CAST(strftime('%m', g.game_date) AS INTEGER) IN (5, 6)
        )
    """

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.points) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['points'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.rebounds) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['rebounds'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.assists) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['assists'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.steals) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['steals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.blocks) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['blocks'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.tp_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['three_pointers'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.ft_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['free_throws'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            SUM(ps.fg_made) as value,
            COUNT(*) as games_played
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['field_goals'] = [dict(row) for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT
            ps.player_name,
            COUNT(*) as value
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        WHERE ps.minutes > 0
        {playoff_filter}
        GROUP BY ps.player_name
        ORDER BY value DESC
        LIMIT ?
    """, (limit,))
    records['games_played'] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records


def get_all_records():

    return {
        'awards': get_award_winners(),
        'single_game': get_single_game_player_records(),
        'career': get_career_player_records(),
        'playoff_single_game': get_playoff_single_game_player_records(),
        'playoff_career': get_playoff_career_player_records(),
        'team_season': get_team_season_records(),
        'team_streaks': get_team_streak_records()
    }
