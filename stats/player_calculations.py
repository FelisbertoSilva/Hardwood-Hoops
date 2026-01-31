from database.db_helpers import get_player_games
from stats.stat_formulas import (
    calculate_percentage, 
    calculate_efg, 
    calculate_ts,
    calculate_two_point_stats,
    calculate_per_36,
    get_season_from_date
)

def calculate_player_stats(player_name):
    games = get_player_games(player_name)

    if not games:
        return None

    # Encontrar jogo mais recente (lambda)
    sorted_games = sorted(games, key=lambda x: x['game_date'])
    latest_game = dict(sorted_games[-1])
    current_team = latest_game.get('team', 'N/A')
    real_player_name = latest_game.get('player', player_name)

    draft_year = latest_game.get('draft_year', 'N/A')
    draft_pick = latest_game.get('draft_pick', 'N/A')

    season_stats_regular = {}
    season_stats_playoff = {}
    game_logs = {}

    career_highs_reg = _initialize_career_highs()
    career_highs_playoff = _initialize_career_highs()
    
    for game in games:
        season = get_season_from_date(game['game_date'])
        team = game['team']
        key = f"{season}_{team}"
        
        # Playoff vs Regular season
        season_start_year = int(season.split('-')[0])
        playoff_start = f"{season_start_year + 1}-04-20"
        is_playoff = game['game_date'] >= playoff_start
        
        stats_dict = season_stats_playoff if is_playoff else season_stats_regular
        
        if key not in stats_dict:
            stats_dict[key] = _initialize_season_stats(season, team)
        
        if season not in game_logs:
            game_logs[season] = []
        
        _add_game_to_season(stats_dict[key], game)

        _add_game_to_logs(game_logs[season], game, team)

        highs_dict = career_highs_playoff if is_playoff else career_highs_reg
        _update_career_highs(highs_dict, game, team)
    
    stats_by_season = []
    career_totals = _initialize_career_totals()
    
    seasons_dict = {}
    for key, stats in season_stats_regular.items():
        season = stats['season']
        if season not in seasons_dict:
            seasons_dict[season] = []
        seasons_dict[season].append((key, stats))
    
    for season in sorted(seasons_dict.keys()):
        teams_in_season = seasons_dict[season]
        
        # TOT BBall Ref
        if len(teams_in_season) > 1:
            season_total_stats = _initialize_season_stats(season, f"{len(teams_in_season)}TM")
            
            for key, team_stats in teams_in_season:
                for stat_key in ['games', 'games_started', 'minutes', 'fg_made', 'fg_att', 
                                'tp_made', 'tp_att', 'ft_made', 'ft_att', 'rebounds', 
                                'assists', 'steals', 'blocks', 'turnovers', 'points']:
                    season_total_stats[stat_key] += team_stats[stat_key]
            
            tot_data = _calculate_season_data(season_total_stats, career_totals, count_career=False)
            stats_by_season.append(tot_data)
            
            for key, team_stats in teams_in_season:
                team_data = _calculate_season_data(team_stats, career_totals, count_career=False)
                stats_by_season.append(team_data)
            
            for stat_key in career_totals:
                if stat_key in season_total_stats:
                    career_totals[stat_key] += season_total_stats[stat_key]
        else:
            key, team_stats = teams_in_season[0]
            team_data = _calculate_season_data(team_stats, career_totals, count_career=True)
            stats_by_season.append(team_data)
    
    if career_totals['games'] > 0:
        career_averages = _calculate_career_averages(career_totals)
        career_per36 = _calculate_career_per36(career_totals)
        career_totals_display = _calculate_career_totals_display(career_totals)
    else:
        career_averages = None
        career_per36 = None
        career_totals_display = None
    
    playoff_stats_by_season = []
    playoff_career_totals = _initialize_career_totals()
    
    playoff_seasons_dict = {}
    for key, stats in season_stats_playoff.items():
        season = stats['season']
        if season not in playoff_seasons_dict:
            playoff_seasons_dict[season] = []
        playoff_seasons_dict[season].append((key, stats))
    
    for season in sorted(playoff_seasons_dict.keys()):
        teams_in_season = playoff_seasons_dict[season]
        
        if len(teams_in_season) > 1:
            season_total_stats = _initialize_season_stats(season, f"{len(teams_in_season)}TM")
            
            for key, team_stats in teams_in_season:
                for stat_key in ['games', 'games_started', 'minutes', 'fg_made', 'fg_att', 
                                'tp_made', 'tp_att', 'ft_made', 'ft_att', 'rebounds', 
                                'assists', 'steals', 'blocks', 'turnovers', 'points']:
                    season_total_stats[stat_key] += team_stats[stat_key]
            
            tot_data = _calculate_season_data(season_total_stats, playoff_career_totals, count_career=False)
            playoff_stats_by_season.append(tot_data)
            
            for key, team_stats in teams_in_season:
                team_data = _calculate_season_data(team_stats, playoff_career_totals, count_career=False)
                playoff_stats_by_season.append(team_data)
            
            for stat_key in playoff_career_totals:
                if stat_key in season_total_stats:
                    playoff_career_totals[stat_key] += season_total_stats[stat_key]
        else:
            key, team_stats = teams_in_season[0]
            team_data = _calculate_season_data(team_stats, playoff_career_totals, count_career=True)
            playoff_stats_by_season.append(team_data)
    
    if playoff_career_totals['games'] > 0:
        playoff_career_averages = _calculate_career_averages(playoff_career_totals)
        playoff_career_per36 = _calculate_career_per36(playoff_career_totals)
        playoff_career_totals_display = _calculate_career_totals_display(playoff_career_totals)
    else:
        playoff_career_averages = None
        playoff_career_per36 = None
        playoff_career_totals_display = None
    
    return {
        'player_name': real_player_name,
        'team': current_team,
        'draft_year': draft_year,
        'draft_pick': draft_pick, 
        'stats_by_season': stats_by_season,
        'career_averages': career_averages,
        'career_per36': career_per36,
        'career_totals': career_totals_display,
        'playoff_stats_by_season': playoff_stats_by_season,
        'playoff_career_averages': playoff_career_averages,
        'playoff_career_per36': playoff_career_per36,
        'playoff_career_totals': playoff_career_totals_display,
        'career_highs': career_highs_reg,
        'playoff_career_highs': career_highs_playoff,
        'game_logs': game_logs
    }

def _initialize_season_stats(season, team):
    return {
        'season': season,
        'team': team,
        'games': 0,
        'games_started': 0,
        'minutes': 0,
        'fg_made': 0,
        'fg_att': 0,
        'tp_made': 0,
        'tp_att': 0,
        'ft_made': 0,
        'ft_att': 0,
        'rebounds': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'turnovers': 0,
        'points': 0
    }

def _initialize_career_totals():
    return {
        'games': 0,
        'games_started': 0,
        'minutes': 0,
        'fg_made': 0,
        'fg_att': 0,
        'tp_made': 0,
        'tp_att': 0,
        'ft_made': 0,
        'ft_att': 0,
        'rebounds': 0,
        'assists': 0,
        'steals': 0,
        'blocks': 0,
        'turnovers': 0,
        'points': 0
    }

def _add_game_to_season(season_stats, game):
    season_stats['games'] += 1
    season_stats['games_started'] += game['started']
    season_stats['minutes'] += game['minutes']
    season_stats['fg_made'] += game['fg_made']
    season_stats['fg_att'] += game['fg_att']
    season_stats['tp_made'] += game['tp_made']
    season_stats['tp_att'] += game['tp_att']
    season_stats['ft_made'] += game['ft_made']
    season_stats['ft_att'] += game['ft_att']
    season_stats['rebounds'] += game['rebounds']
    season_stats['assists'] += game['assists']
    season_stats['steals'] += game['steals']
    season_stats['blocks'] += game['blocks']
    season_stats['turnovers'] += game['turnovers']
    season_stats['points'] += game['points']

def _add_game_to_logs(game_log_list, game, team):
    game_log_list.append({
        'game_id': game['game_id'],
        'date': game['game_date'],
        'team': game['team'],
        'opponent': game['away_team'] if game['home_team'] == team else game['home_team'],
        'location': 'vs' if game['home_team'] == team else '@',
        'team_score': game['home_score'] if game['home_team'] == team else game['away_score'],
        'opp_score': game['away_score'] if game['home_team'] == team else game['home_score'],
        'started': game['started'],
        'minutes': game['minutes'],
        'fg_made': game['fg_made'],
        'fg_att': game['fg_att'],
        'tp_made': game['tp_made'],
        'tp_att': game['tp_att'],
        'ft_made': game['ft_made'],
        'ft_att': game['ft_att'],
        'rebounds': game['rebounds'],
        'assists': game['assists'],
        'steals': game['steals'],
        'blocks': game['blocks'],
        'turnovers': game['turnovers'],
        'points': game['points']
    })

def _calculate_season_data(stats, career_totals, count_career=True):
    g = stats['games']
    
    if count_career:
        for key in career_totals:
            if key in stats:
                career_totals[key] += stats[key]
    
    two_p_made, two_p_att = calculate_two_point_stats(
        stats['fg_made'], stats['fg_att'],
        stats['tp_made'], stats['tp_att']
    )
    
    mpg = stats['minutes'] / g
    
    averages = _build_stat_dict(
        stats['season'], stats['team'], g, stats['games_started'],
        stats['minutes'] / g,
        stats['fg_made'] / g,
        stats['fg_att'] / g,
        calculate_percentage(stats['fg_made'], stats['fg_att']),
        stats['tp_made'] / g,
        stats['tp_att'] / g,
        calculate_percentage(stats['tp_made'], stats['tp_att']),
        two_p_made / g,
        two_p_att / g,
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(stats['fg_made'], stats['tp_made'], stats['fg_att']),
        stats['ft_made'] / g,
        stats['ft_att'] / g,
        calculate_percentage(stats['ft_made'], stats['ft_att']),
        calculate_ts(stats["points"] / g, stats["fg_att"] / g, stats["ft_att"] / g),
        stats['rebounds'] / g,
        stats['assists'] / g,
        stats['steals'] / g,
        stats['blocks'] / g,
        stats['turnovers'] / g,
        stats['points'] / g,
        round_values=True
    )
    
    per36 = _build_stat_dict(
        stats['season'], stats['team'], g, stats['games_started'],
        mpg,
        calculate_per_36(stats['fg_made'] / g, mpg),
        calculate_per_36(stats['fg_att'] / g, mpg),
        calculate_percentage(stats['fg_made'], stats['fg_att']),
        calculate_per_36(stats['tp_made'] / g, mpg),
        calculate_per_36(stats['tp_att'] / g, mpg),
        calculate_percentage(stats['tp_made'], stats['tp_att']),
        calculate_per_36(two_p_made / g, mpg),
        calculate_per_36(two_p_att / g, mpg),
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(stats['fg_made'], stats['tp_made'], stats['fg_att']),
        calculate_per_36(stats['ft_made'] / g, mpg),
        calculate_per_36(stats['ft_att'] / g, mpg),
        calculate_percentage(stats['ft_made'], stats['ft_att']),
        calculate_ts(stats["points"] / g, stats["fg_att"] / g, stats["ft_att"] / g),
        calculate_per_36(stats['rebounds'] / g, mpg),
        calculate_per_36(stats['assists'] / g, mpg),
        calculate_per_36(stats['steals'] / g, mpg),
        calculate_per_36(stats['blocks'] / g, mpg),
        calculate_per_36(stats['turnovers'] / g, mpg),
        calculate_per_36(stats['points'] / g, mpg),
        round_values=False
    )
    
    totals = _build_stat_dict(
        stats['season'], stats['team'], g, stats['games_started'],
        stats['minutes'],
        stats['fg_made'],
        stats['fg_att'],
        calculate_percentage(stats['fg_made'], stats['fg_att']),
        stats['tp_made'],
        stats['tp_att'],
        calculate_percentage(stats['tp_made'], stats['tp_att']),
        two_p_made,
        two_p_att,
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(stats['fg_made'], stats['tp_made'], stats['fg_att']),
        stats['ft_made'],
        stats['ft_att'],
        calculate_percentage(stats['ft_made'], stats['ft_att']),
        calculate_ts(stats["points"], stats["fg_att"], stats["ft_att"]),
        stats['rebounds'],
        stats['assists'],
        stats['steals'],
        stats['blocks'],
        stats['turnovers'],
        stats['points'],
        round_values=False 
    )
    
    return {
        'averages': averages,
        'per36': per36,
        'totals': totals
    }

def _build_stat_dict(season, team, g, gs, mp, fg, fga, fg_pct, tp, tpa, tp_pct,
                     two_p, two_pa, two_p_pct, efg, ft, fta, ft_pct, ts, rb, ast,
                     stl, blk, tov, pts, round_values=True):
    """Build a standardized stat dictionary"""
    if round_values:
        return {
            'season': season, 'team': team, 'g': g, 'gs': gs,
            'mp': round(mp, 1), 'fg': round(fg, 1), 'fga': round(fga, 1), 'fg_pct': fg_pct,
            'tp': round(tp, 1), 'tpa': round(tpa, 1), 'tp_pct': tp_pct,
            'two_p': round(two_p, 1), 'two_pa': round(two_pa, 1), 'two_p_pct': two_p_pct,
            'efg': efg, 'ft': round(ft, 1), 'fta': round(fta, 1), 'ft_pct': ft_pct,
            'ts': ts, 'rb': round(rb, 1), 'ast': round(ast, 1), 'stl': round(stl, 1),
            'blk': round(blk, 1), 'tov': round(tov, 1), 'pts': round(pts, 1)
        }
    else:
        return {
            'season': season, 'team': team, 'g': g, 'gs': gs,
            'mp': mp, 'fg': fg, 'fga': fga, 'fg_pct': fg_pct,
            'tp': tp, 'tpa': tpa, 'tp_pct': tp_pct,
            'two_p': two_p, 'two_pa': two_pa, 'two_p_pct': two_p_pct,
            'efg': efg, 'ft': ft, 'fta': fta, 'ft_pct': ft_pct,
            'ts': ts, 'rb': rb, 'ast': ast, 'stl': stl,
            'blk': blk, 'tov': tov, 'pts': pts
        }

def _calculate_career_averages(career_totals):
    g = career_totals['games']
    two_p_made, two_p_att = calculate_two_point_stats(
        career_totals['fg_made'], career_totals['fg_att'],
        career_totals['tp_made'], career_totals['tp_att']
    )
    
    return _build_stat_dict(
        'Career', '', g, career_totals['games_started'],
        career_totals['minutes'] / g,
        career_totals['fg_made'] / g,
        career_totals['fg_att'] / g,
        calculate_percentage(career_totals['fg_made'], career_totals['fg_att']),
        career_totals['tp_made'] / g,
        career_totals['tp_att'] / g,
        calculate_percentage(career_totals['tp_made'], career_totals['tp_att']),
        two_p_made / g,
        two_p_att / g,
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(career_totals['fg_made'], career_totals['tp_made'], career_totals['fg_att']),
        career_totals['ft_made'] / g,
        career_totals['ft_att'] / g,
        calculate_percentage(career_totals['ft_made'], career_totals['ft_att']),
        calculate_ts(career_totals['points'] / g, career_totals['fg_att'] / g, career_totals['ft_att'] / g),
        career_totals['rebounds'] / g,
        career_totals['assists'] / g,
        career_totals['steals'] / g,
        career_totals['blocks'] / g,
        career_totals['turnovers'] / g,
        career_totals['points'] / g,
        round_values=True
    )

def _calculate_career_per36(career_totals):
    g = career_totals['games']
    mpg = career_totals['minutes'] / g
    two_p_made, two_p_att = calculate_two_point_stats(
        career_totals['fg_made'], career_totals['fg_att'],
        career_totals['tp_made'], career_totals['tp_att']
    )
    
    return _build_stat_dict(
        'Career', '', g, career_totals['games_started'],
        mpg,
        calculate_per_36(career_totals['fg_made'] / g, mpg),
        calculate_per_36(career_totals['fg_att'] / g, mpg),
        calculate_percentage(career_totals['fg_made'], career_totals['fg_att']),
        calculate_per_36(career_totals['tp_made'] / g, mpg),
        calculate_per_36(career_totals['tp_att'] / g, mpg),
        calculate_percentage(career_totals['tp_made'], career_totals['tp_att']),
        calculate_per_36(two_p_made / g, mpg),
        calculate_per_36(two_p_att / g, mpg),
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(career_totals['fg_made'], career_totals['tp_made'], career_totals['fg_att']),
        calculate_per_36(career_totals['ft_made'] / g, mpg),
        calculate_per_36(career_totals['ft_att'] / g, mpg),
        calculate_percentage(career_totals['ft_made'], career_totals['ft_att']),
        calculate_ts(career_totals['points'] / g, career_totals['fg_att'] / g, career_totals['ft_att'] / g),
        calculate_per_36(career_totals['rebounds'] / g, mpg),
        calculate_per_36(career_totals['assists'] / g, mpg),
        calculate_per_36(career_totals['steals'] / g, mpg),
        calculate_per_36(career_totals['blocks'] / g, mpg),
        calculate_per_36(career_totals['turnovers'] / g, mpg),
        calculate_per_36(career_totals['points'] / g, mpg),
        round_values=False
    )

def _calculate_career_totals_display(career_totals):
    two_p_made, two_p_att = calculate_two_point_stats(
        career_totals['fg_made'], career_totals['fg_att'],
        career_totals['tp_made'], career_totals['tp_att']
    )
    
    return _build_stat_dict(
        'Career', '', career_totals['games'], career_totals['games_started'],
        career_totals['minutes'],
        career_totals['fg_made'],
        career_totals['fg_att'],
        calculate_percentage(career_totals['fg_made'], career_totals['fg_att']),
        career_totals['tp_made'],
        career_totals['tp_att'],
        calculate_percentage(career_totals['tp_made'], career_totals['tp_att']),
        two_p_made,
        two_p_att,
        calculate_percentage(two_p_made, two_p_att),
        calculate_efg(career_totals['fg_made'], career_totals['tp_made'], career_totals['fg_att']),
        career_totals['ft_made'],
        career_totals['ft_att'],
        calculate_percentage(career_totals['ft_made'], career_totals['ft_att']),
        calculate_ts(career_totals['points'], career_totals['fg_att'], career_totals['ft_att']),
        career_totals['rebounds'],
        career_totals['assists'],
        career_totals['steals'],
        career_totals['blocks'],
        career_totals['turnovers'],
        career_totals['points'],
        round_values=False
    )


def _initialize_career_highs():
    return {
        'points': None,
        'rebounds': None,
        'assists': None,
        'steals': None,
        'blocks': None,
        'three_pointers': None,
        'free_throws': None,
        'field_goals': None
    }


def _update_career_highs(highs_dict, game, team):
    if game['home_team'] == team:
        opponent = game['away_team']
    else:
        opponent = game['home_team']

    game_date = game['game_date']

    stat_mappings = [
        ('points', 'points'),
        ('rebounds', 'rebounds'),
        ('assists', 'assists'),
        ('steals', 'steals'),
        ('blocks', 'blocks'),
        ('three_pointers', 'tp_made'),
        ('free_throws', 'ft_made'),
        ('field_goals', 'fg_made')
    ]

    for high_key, game_key in stat_mappings:
        value = game[game_key]
        if highs_dict[high_key] is None or value > highs_dict[high_key]['value']:
            highs_dict[high_key] = {
                'value': value,
                'opponent': opponent,
                'date': game_date,
                'team': team
            }