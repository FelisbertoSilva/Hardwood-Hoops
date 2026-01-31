from functools import cmp_to_key
from itertools import groupby
from database.db_helpers import get_db_connection
from database.team_config import (
    get_team_conference, 
    get_team_division, 
    get_conference_teams, 
    get_division_teams
)
from stats.stat_formulas import calculate_percentage, get_season_from_date

def get_available_seasons():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT game_date FROM games ORDER BY game_date DESC")
    dates = cursor.fetchall()
    conn.close()
    
    seasons = set()
    for date_row in dates:
        season = get_season_from_date(date_row['game_date'])
        seasons.add(season)
    return sorted(list(seasons), reverse=True)

def calculate_league_standings(season=None):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cursor = conn.cursor()
    
    if season is None:
        available_seasons = get_available_seasons()
        season = available_seasons[0] if available_seasons else "2024-25"
    
    season_start_year = int(season.split('-')[0])
    season_start, season_end = f"{season_start_year}-07-01", f"{season_start_year + 1}-06-30"
    playoff_start = f"{season_start_year + 1}-04-20"

    cursor.execute("""
        SELECT 
            ts.team_name,
            COUNT(*) as gp,
            SUM(ts.win) as wins,
            SUM(CASE WHEN ts.team_name = g.home_team THEN g.home_score ELSE g.away_score END) as pts_for,
            SUM(CASE WHEN ts.team_name = g.home_team THEN g.away_score ELSE g.home_score END) as pts_against
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE g.game_date >= ? AND g.game_date < ?
        GROUP BY ts.team_name
    """, (season_start, playoff_start))
    teams_data = cursor.fetchall()

    cursor.execute("""
        SELECT g.*, ts_home.win as home_win 
        FROM games g
        JOIN team_stats ts_home ON g.game_id = ts_home.game_id AND g.home_team = ts_home.team_name
        WHERE g.game_date >= ? AND g.game_date < ?
    """, (season_start, playoff_start))
    all_games = cursor.fetchall()
    conn.close()

    standings_dict = {}
    for row in teams_data:
        name = row['team_name']
        conf_wins, conf_loss = _calculate_conference_record(name, all_games)
        div_wins, div_loss = _calculate_division_record(name, all_games)
        home_w, home_l, road_w, road_l = _calculate_home_road_records(name, all_games)
        last10_w, last10_l = _calculate_last10_detailed(name, all_games)
        div_wins, div_loss = _calculate_division_record(name, all_games)
        
        standings_dict[name] = {
            'team': name,
            'wins': row['wins'],
            'losses': row['gp'] - row['wins'],
            'win_pct': row['wins'] / row['gp'] if row['gp'] > 0 else 0,
            'conf_wins': conf_wins, 'conf_losses': conf_loss,
            'conf_pct': conf_wins / (conf_wins + conf_loss) if (conf_wins + conf_loss) > 0 else 0,
            'div_wins': div_wins, 'div_losses': div_loss,
            'div_pct': div_wins / (div_wins + div_loss) if (div_wins + div_loss) > 0 else 0,
            'net_points': row['pts_for'] - row['pts_against'],
            'is_div_leader': False,
            'home_wins': home_w, 'home_losses': home_l,
            'road_wins': road_w, 'road_losses': road_l,
            'last10_wins': last10_w, 'last10_losses': last10_l,
            'last10': _calculate_last10_record(name, all_games),
            'streak': _calculate_streak(name, all_games)
        }

    for div in ['Atlantic', 'Central', 'Southeast', 'Northwest', 'Pacific', 'Southwest']:
        div_teams = [standings_dict[t] for t in get_division_teams(div) if t in standings_dict]
        if div_teams:
            leader = max(div_teams, key=lambda x: (x['win_pct'], x['wins']))
            standings_dict[leader['team']]['is_div_leader'] = True

    playoff_eligible = _identify_playoff_eligible(standings_dict)

    east_teams = [v for k, v in standings_dict.items() if get_team_conference(k) == 'Eastern']
    west_teams = [v for k, v in standings_dict.items() if get_team_conference(k) == 'Western']

    sorted_east = _resolve_group_ties(east_teams, all_games, playoff_eligible)
    sorted_west = _resolve_group_ties(west_teams, all_games, playoff_eligible)

    _add_seed_and_gb(sorted_east)
    _add_seed_and_gb(sorted_west)

    clinch_indicators = _calculate_clinch_indicators(sorted_east, sorted_west)
    
    for team in sorted_east + sorted_west:
        team["clinch"] = clinch_indicators.get(team["team"], "")

    return {"Eastern": sorted_east, "Western": sorted_west}

def _resolve_group_ties(teams, all_games, playoff_eligible):
    teams.sort(key=lambda x: (x['win_pct'], x['wins']), reverse=True)
    
    final_standings = []
    for _, group in groupby(teams, key=lambda x: (x['win_pct'], x['wins'])):
        tied_list = list(group)
        if len(tied_list) > 1:
            resolved = _break_tie_recursive(tied_list, all_games, playoff_eligible)
            final_standings.extend(resolved)
        else:
            final_standings.extend(tied_list)
    return final_standings

def _break_tie_recursive(tied_teams, all_games, playoff_eligible):
    if len(tied_teams) <= 1:
        return tied_teams

    is_multi = len(tied_teams) > 2
    team_names = [t['team'] for t in tied_teams]

    def h2h_val(t): return _calculate_h2h_pct(t['team'], team_names, all_games)
    def div_leader_val(t): return 1 if t['is_div_leader'] else 0
    def div_pct_val(t): 
        divs = {get_team_division(name) for name in team_names}
        return t['div_pct'] if len(divs) == 1 else 0
    def conf_pct_val(t): return t['conf_pct']
    def v_playoff_own(t): return _record_vs_playoff(t['team'], all_games, playoff_eligible, True)
    def v_playoff_opp(t): return _record_vs_playoff(t['team'], all_games, playoff_eligible, False)
    def net_pts_val(t): return t['net_points']

    if not is_multi:
        steps = [h2h_val, div_leader_val, div_pct_val, conf_pct_val, v_playoff_own, v_playoff_opp, net_pts_val]
    else:
        steps = [div_leader_val, h2h_val, div_pct_val, conf_pct_val, v_playoff_own, v_playoff_opp, net_pts_val]

    for step_func in steps:
        tied_teams.sort(key=step_func, reverse=True)
        new_groups = []
        for _, g in groupby(tied_teams, key=step_func):
            new_groups.append(list(g))
        
        if len(new_groups) > 1:
            result = []
            for sub_group in new_groups:
                result.extend(_break_tie_recursive(sub_group, all_games, playoff_eligible))
            return result

    return tied_teams


def _calculate_h2h_pct(team_name, tied_names, all_games):
    wins, total = 0, 0
    for g in all_games:
        if g['home_team'] == team_name and g['away_team'] in tied_names:
            total += 1
            if g['home_win']: wins += 1
        elif g['away_team'] == team_name and g['home_team'] in tied_names:
            total += 1
            if not g['home_win']: wins += 1
    return wins / total if total > 0 else 0

def _record_vs_playoff(team_name, all_games, playoff_eligible, own_conf=True):
    team_conf = get_team_conference(team_name)
    targets = [t for t in playoff_eligible if (get_team_conference(t) == team_conf) == own_conf]
    wins, total = 0, 0
    for g in all_games:
        if g['home_team'] == team_name and g['away_team'] in targets:
            total += 1
            if g['home_win']: wins += 1
        elif g['away_team'] == team_name and g['home_team'] in targets:
            total += 1
            if not g['home_win']: wins += 1
    return wins / total if total > 0 else 0

def _identify_playoff_eligible(standings_dict):
    """Returns set of team names currently in top 10, prioritizing wins on equal pct."""
    east = [v for k, v in standings_dict.items() if get_team_conference(k) == 'Eastern']
    west = [v for k, v in standings_dict.items() if get_team_conference(k) == 'Western']
    
    east.sort(key=lambda x: (x['win_pct'], x['wins']), reverse=True)
    west.sort(key=lambda x: (x['win_pct'], x['wins']), reverse=True)
    
    return {t['team'] for t in east[:10]} | {t['team'] for t in west[:10]}

def _calculate_conference_record(team_name, all_games):
    conf = get_team_conference(team_name)
    conf_teams = get_conference_teams(conf)
    w, l = 0, 0
    for g in all_games:
        if g['home_team'] == team_name and g['away_team'] in conf_teams:
            if g['home_win']: w += 1
            else: l += 1
        elif g['away_team'] == team_name and g['home_team'] in conf_teams:
            if not g['home_win']: w += 1
            else: l += 1
    return (w, l)

def _calculate_division_record(team_name, all_games):
    div = get_team_division(team_name)
    div_teams = get_division_teams(div)
    w, l = 0, 0
    for g in all_games:
        if g['home_team'] == team_name and g['away_team'] in div_teams:
            if g['home_win']: w += 1
            else: l += 1
        elif g['away_team'] == team_name and g['home_team'] in div_teams:
            if not g['home_win']: w += 1
            else: l += 1
    return (w, l)

def _calculate_last10_record(team_name, all_games):
    results = []
    for g in all_games:
        if g['home_team'] == team_name: results.append(True if g['home_win'] else False)
        elif g['away_team'] == team_name: results.append(True if not g['home_win'] else False)
    last_10 = results[-10:]
    w = sum(last_10)
    return f"{w}-{len(last_10)-w}"

def _calculate_streak(team_name, all_games):
    results = []
    for g in all_games:
        if g['home_team'] == team_name: results.append(True if g['home_win'] else False)
        elif g['away_team'] == team_name: results.append(True if not g['home_win'] else False)
    if not results: return "N/A"
    curr = results[-1]
    count = 0
    for r in reversed(results):
        if r == curr: count += 1
        else: break
    return f"{'W' if curr else 'L'}{count}"

def _add_seed_and_gb(standings):
    if not standings: return
    leader_w, leader_l = standings[0]['wins'], standings[0]['losses']
    for i, team in enumerate(standings):
        team['seed'] = i + 1
        gb = ((leader_w - team['wins']) + (team['losses'] - leader_l)) / 2
        team['gb'] = "-" if gb == 0 else (f"{gb:.1f}" if gb % 1 != 0 else str(int(gb)))
def _calculate_clinch_indicators(east_teams, west_teams):
    season_complete = all(team['wins'] + team['losses'] >= 82 for team in east_teams + west_teams)
    
    if season_complete:
        return {} 
    
    clinch_status = {}
    
    for conf_name, teams in [('Eastern', east_teams), ('Western', west_teams)]:
        sorted_teams = sorted(teams, key=lambda x: x['seed'])
        
        for i, team in enumerate(sorted_teams):
            team_name = team['team']
            seed = team['seed']
            wins = team['wins']
            losses = team['losses']
            games_remaining = 82 - (wins + losses)
            
            status = []
            
            if team['is_div_leader']:
                division = get_team_division(team_name)
                div_teams = [t for t in teams if get_team_division(t['team']) == division and t['team'] != team_name]
                
                if div_teams:
                    second_place = max(div_teams, key=lambda x: x['wins'])
                    max_possible_wins = second_place['wins'] + (82 - second_place['wins'] - second_place['losses'])
                    
                    if wins > max_possible_wins:
                        div_abbrev = {
                            'Atlantic': 'a', 'Central': 'c', 'Southeast': 'se',
                            'Northwest': 'nw', 'Pacific': 'p', 'Southwest': 'sw'
                        }.get(division, '')
                        if div_abbrev:
                            status.append(div_abbrev)
            
            # Conference clinch 
            if seed == 1:
                second_place = sorted_teams[1] if len(sorted_teams) > 1 else None
                if second_place:
                    max_possible_wins = second_place['wins'] + (82 - second_place['wins'] - second_place['losses'])
                    if wins > max_possible_wins:
                        status.append('e' if conf_name == 'Eastern' else 'w')
            
            # Playoff clinch
            if seed <= 6:
                seventh_place = sorted_teams[6] if len(sorted_teams) > 6 else None
                if seventh_place:
                    max_possible_wins = seventh_place['wins'] + (82 - seventh_place['wins'] - seventh_place['losses'])
                    if wins > max_possible_wins:
                        if 'x' not in status:
                            status.append('x')
            
            # Play-in clinch
            if seed <= 10:
                eleventh_place = sorted_teams[10] if len(sorted_teams) > 10 else None
                if eleventh_place:
                    max_possible_wins = eleventh_place['wins'] + (82 - eleventh_place['wins'] - eleventh_place['losses'])
                    if wins > max_possible_wins and 'x' not in status:
                        status.append('pi')
            
            # Eliminado
            if seed > 10:
                tenth_place = sorted_teams[9]  
                min_wins_needed = tenth_place['wins'] + 1
                max_possible_wins = wins + games_remaining
                
                if max_possible_wins < min_wins_needed:
                    status.append('o')
            
            if status:
                clinch_status[team_name] = '-'.join(status)
    
    return clinch_status

def _calculate_home_road_records(team_name, all_games):
    home_wins, home_losses = 0, 0
    road_wins, road_losses = 0, 0
    
    for g in all_games:
        if g['home_team'] == team_name:
            if g['home_win']:
                home_wins += 1
            else:
                home_losses += 1
        elif g['away_team'] == team_name:
            if not g['home_win']:
                road_wins += 1
            else:
                road_losses += 1
    
    return (home_wins, home_losses, road_wins, road_losses)

def _calculate_last10_detailed(team_name, all_games):
    results = []
    for g in all_games:
        if g['home_team'] == team_name:
            results.append(True if g['home_win'] else False)
        elif g['away_team'] == team_name:
            results.append(True if not g['home_win'] else False)
    
    last_10 = results[-10:]
    wins = sum(last_10)
    losses = len(last_10) - wins
    return (wins, losses)