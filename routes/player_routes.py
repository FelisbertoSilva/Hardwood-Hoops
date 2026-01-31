import sys
import os
import json
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, render_template, abort
from database.db_helpers import get_all_players, get_player_info
from stats.player_calculations import calculate_player_stats
from stats.records_calculations import get_award_winners

player_bp = Blueprint('player', __name__)

name_corrections = {
    "AJ Green": "AJ Green",
    "Alperen Sengun": "Alperen Sengun",
    "Brandon Boston": "Brandon Boston",
    "Olivier M Prosper": "Olivier-Maxence Prosper",
    "Andre Jackson Jr": "Andre Jackson Jr.",
    "Bruce Brown Jr": "Bruce Brown",
    "DayRon Sharpe": "Day'Ron Sharpe",
    "DeAndre Hunter": "De'Andre Hunter",
    "Derrick Jones Jr": "Derrick Jones Jr.",
    "Dorian F Smith": "Dorian Finney-Smith",
    "Gary Trent Jr": "Gary Trent Jr.",
    "Herb Jones": "Herbert Jones",
    "Jabari Smith Jr": "Jabari Smith Jr.",
    "Jaime Jaquez Jr": "Jaime Jaquez Jr.",
    "JaKobe Walter": "Ja'Kobe Walter",
    "Jaren Jackson Jr": "Jaren Jackson Jr.",
    "Jeremiah R Earl": "Jeremiah Robinson-Earl",
    "Karl Anthony Towns": "Karl-Anthony Towns",
    "Kelly Oubre Jr": "Kelly Oubre Jr.",
    "Kentavious C Pope": "Kentavious Caldwell-Pope",
    "Kevin Porter Jr": "Kevin Porter Jr.",
    "Michael Porter Jr": "Michael Porter Jr.",
    "Nick Smith Jr": "Nick Smith Jr.",
    "Nickeil A Walker": "Nickeil Alexander-Walker",
    "PJ Washington": "P.J. Washington",
    "Scottie Pippen Jr": "Scotty Pippen Jr.",
    "Shai G Alexander": "Shai Gilgeous-Alexander",
    "TJ McConnell": "T.J. McConnell",
    "Talen H Tucker": "Talen Horton-Tucker",
    "Tim Hardaway Jr": "Tim Hardaway Jr.",
    "Trayce J Davis": "Trayce Jackson-Davis",
    "Wendell Carter Jr": "Wendell Carter Jr.",
    "Nikola Jovic": "Nikola Jović",
    "DeAaron Fox": "De'Aaron Fox",
    "JaeSean Tate": "Jae'Sean Tate",
    "Craig Porter": "Craig Porter Jr.",
    "Sandro Mamu": "Sandro Mamukelashvili",
    "Marvin Bagley": "Marvin Bagley III",
    "Dante Exum": "Danté Exum",
    "Jalen H Schifino": "Jalen Hood-Schifino",
    "Luka Doncic": "Luka Dončić",
    "Nikola Jokic": "Nikola Jokić",
    "DeAnthony Melton": "De'Anthony Melton",
    "Karlo Matkovic": "Karlo Matković",
    "Jimmy Butler": "Jimmy Butler III",
    "Dom Barlow": "Dominick Barlow",
    "Terrence Shannon": "Terrence Shannon Jr.",
    "Bogdan Bogdanovic": "Bogdan Bogdanović",
    "Lonnie Walker": "Lonnie Walker IV",
    "Kristaps Porzingis": "Kristaps Porziņģis",
    "Robert Williams": "Robert Williams III",
    "Vince Williams Jr": "Vince Williams Jr.",
    "Moussa Diabate": "Moussa Diabaté",
    "Larry Nance Jr": "Larry Nance Jr.",
    "Pacome Dadiet": "Pacôme Dadiet",
    "Nikola Vucevic": "Nikola Vučević",
    "Jusuf Nurkic": "Jusuf Nurkić",
    "Dennis Schroder": "Dennis Schröder",
    "Jonas Valanciunas": "Jonas Valančiūnas",
    "Tidjane Salaun": "Tidjane Salaün",
    "Kasparas Jakucionis": "Kasparas Jakučionis",
    "Ron Holland": "Ronald Holland II"
}

def get_player_contracts(player_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ct1, ct2, ct3, ct4, ct5,
               ct1c, ct2c, ct3c, ct4c, ct5c
        FROM players
        WHERE name = ?
    """, (player_name,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    contract_years = ['2025/26', '2026/27', '2027/28', '2028/29', '2029/30']
    contracts = []

    for i in range(5):
        ct_val = row[i]        
        ctc_val = row[5 + i]   

        # Só aparecer anos com contrato
        if ct_val:
            contracts.append({
                'year': contract_years[i],
                'amount': ct_val,
                'code': ctc_val
            })

    return contracts if contracts else None

def get_player_map():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, '..', 'player_id_map.json')
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"DEBUG Error: {e}")
    return {}

@player_bp.route('/player/<player_name>')
def player_page(player_name):
    player_stats = calculate_player_stats(player_name)

    if not player_stats:
        corrected_name = name_corrections.get(player_name)
        if corrected_name:
             player_stats = calculate_player_stats(corrected_name)

    # If no stats, check if player exists in players table (hasn't played yet)
    if not player_stats:
        lookup_name = name_corrections.get(player_name, player_name)
        player_info = get_player_info(lookup_name)

        if player_info:
            # Player exists but has no game stats - create empty stats structure
            player_stats = {
                'player_name': player_info['name'],
                'team': player_info['team'] or 'N/A',
                'draft_year': player_info['draft_year'],
                'draft_pick': player_info['draft_pick'],
                'stats_by_season': [],
                'career_averages': None,
                'career_per36': None,
                'career_totals': None,
                'playoff_stats_by_season': [],
                'playoff_career_averages': None,
                'playoff_career_per36': None,
                'playoff_career_totals': None,
                'career_highs': {
                    'points': None, 'rebounds': None, 'assists': None,
                    'steals': None, 'blocks': None, 'three_pointers': None,
                    'free_throws': None, 'field_goals': None
                },
                'playoff_career_highs': {
                    'points': None, 'rebounds': None, 'assists': None,
                    'steals': None, 'blocks': None, 'three_pointers': None,
                    'free_throws': None, 'field_goals': None
                },
                'game_logs': {}
            }
        else:
            return render_template('error.html', message=f"Player '{player_name}' not found"), 404

    map_lookup_name = name_corrections.get(player_name, player_name)
    
    player_map = get_player_map()
    
    target_player_id = None
    player_metadata = {} 
    
    if str(player_name).isdigit():
        target_player_id = int(player_name)
        for map_name, map_data in player_map.items():
            if map_data.get('id') == target_player_id:
                player_metadata = map_data
                break
        
    elif map_lookup_name in player_map:
        player_metadata = player_map[map_lookup_name]
        target_player_id = player_metadata.get('id')

    if 'player' not in player_stats:
        player_stats['player'] = {}
        
    player_stats['player']['id'] = target_player_id
    
    player_stats['player']['birthdate'] = player_metadata.get('birthdate')
    player_stats['player']['draft'] = player_metadata.get('draft', {})

    db_year = player_stats.get('draft_year')
    db_pick = player_stats.get('draft_pick')

    if db_year and db_year != 'N/A':
        player_stats['player']['draft_year'] = db_year
        player_stats['player']['draft_pick'] = db_pick
        
        try:
            pick_num = int(db_pick)
            round_num = 1 if pick_num <= 30 else 2
            player_stats['player']['draft_formatted'] = f"{db_year} R{round_num} | Pick {pick_num}"
        except:
            player_stats['player']['draft_formatted'] = f"{db_year} | Pick {db_pick}"

    else:
        player_stats['player']['draft'] = player_metadata.get('draft', {})

    team_val = player_stats.get('team')
    if not team_val or team_val == 'N/A':
        try:
            all_logs = []
            for season_logs in player_stats.get('game_logs', {}).values():
                all_logs.extend(season_logs)
            if all_logs:
                all_logs.sort(key=lambda x: x['date'])
                team_val = all_logs[-1]['team']
        except Exception:
            pass
    player_stats['player']['team'] = team_val if team_val else 'N/A'

    all_awards = get_award_winners()
    awards_summary = {}
    
    check_names = {player_name, map_lookup_name}

    award_labels = {
        'mvp': 'MVP', 'dpoy': 'Defensive Player of the Year', 'roy': 'Rookie of the Year',
        'smoy': 'Sixth Man of the Year', 'mip': 'Most Improved Player',
        'all_hh_1st': 'All-HH 1st Team', 'all_hh_2nd': 'All-HH 2nd Team', 'all_hh_3rd': 'All-HH 3rd Team',
        'all_defensive_1st': 'All-Defensive 1st Team', 'all_defensive_2nd': 'All-Defensive 2nd Team',
        'all_rookie_1st': 'All-Rookie 1st Team', 'all_rookie_2nd': 'All-Rookie 2nd Team',
        'all_star': 'All-Star', 'finals_mvp': 'Finals MVP'
    }

    for award_key, winners_list in all_awards.items():
        if award_key in award_labels:
            label = award_labels[award_key]
            for winner in winners_list:
                if winner['player_name'] in check_names:
                    if label not in awards_summary:
                        awards_summary[label] = []
                    awards_summary[label].append(winner['season'])

    player_stats['player']['awards_summary'] = awards_summary

    if 'player_name' not in player_stats:
        player_stats['player_name'] = player_name

    contracts = get_player_contracts(player_name)
    if not contracts and map_lookup_name != player_name:
        contracts = get_player_contracts(map_lookup_name)

    player_stats['contracts'] = contracts

    return render_template('player.html', **player_stats)