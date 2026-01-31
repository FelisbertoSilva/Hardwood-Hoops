import sqlite3
import json
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

DB_PATH = os.path.join(project_root, "hh_stats.db")
GAME_DATA_FOLDER = os.path.join(project_root, "game_data")

PLAYER_NAME_MAP = {
    "Kelly Oubre Jr": "Kelly Oubre",
    "Jabari Smith Jr": "Jabari Smith",
    "Bruce Brown Jr": "Bruce Brown",
    "Ronald Holland II": "Ron Holland",
    "Wendell Carter Jr": "Wendell Carter",
    "Jaime Jaquez Jr": "Jaime Jaquez",
    "Nicolas Claxton": "Nic Claxton",
    "Herbert Jones": "Herb Jones",
    "Dereck Lively II": "Dereck Lively",
    "DeAndre Ayton": "Deandre Ayton",
    "Kevin Porter Jr": "Kevin Porter",
    "Trey Murphy III": "Trey Murphy",
    "Nick Smith Jr": "Nick Smith",
    "DayRon Sharpe": "Dayron Sharpe",
    "Caris Levert": "Caris LeVert"
}

def get_season_from_date(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    if date.month >= 7:
        season = date.year + 1
    else:
        season = date.year
    return season

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela Jogadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            team TEXT,
            rating INTEGER,
            born TEXT,
            draft_pick INTEGER,
            draft_year INTEGER,
            birds INTEGER,
            ct1 INTEGER,
            ct1c INTEGER,
            ct2 INTEGER,
            ct2c INTEGER,
            ct3 INTEGER,
            ct3c INTEGER,
            ct4 INTEGER,
            ct4c INTEGER,
            ct5 INTEGER,
            ct5c INTEGER,
            IR INTEGER DEFAULT 0
        )
    """)
    #Update
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN IR INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Jogos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            season INTEGER NOT NULL,
            away_team TEXT NOT NULL,
            away_score INTEGER NOT NULL,
            home_team TEXT NOT NULL,
            home_score INTEGER NOT NULL,
            UNIQUE(game_date, away_team, home_team)
        )
    """)
    
    # Stat_Jogadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            season INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            team TEXT NOT NULL,
            started INTEGER NOT NULL,
            minutes INTEGER NOT NULL,
            fg_made INTEGER NOT NULL,
            fg_att INTEGER NOT NULL,
            tp_made INTEGER NOT NULL,
            tp_att INTEGER NOT NULL,
            ft_made INTEGER NOT NULL,
            ft_att INTEGER NOT NULL,
            turnovers INTEGER NOT NULL,
            blocks INTEGER NOT NULL,
            steals INTEGER NOT NULL,
            rebounds INTEGER NOT NULL,
            assists INTEGER NOT NULL,
            points INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)

    # Stat_Equipa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_stats (
            team_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            season INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            fg_made INTEGER NOT NULL,
            fg_att INTEGER NOT NULL,
            tp_made INTEGER NOT NULL,
            tp_att INTEGER NOT NULL,
            ft_made INTEGER NOT NULL,
            ft_att INTEGER NOT NULL,
            turnovers INTEGER NOT NULL,
            blocks INTEGER NOT NULL,
            steals INTEGER NOT NULL,
            rebounds INTEGER NOT NULL,
            assists INTEGER NOT NULL,
            points INTEGER NOT NULL,
            points_against INTEGER NOT NULL,
            win INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
    """)

    # Calendário
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            away_team TEXT NOT NULL,
            home_team TEXT NOT NULL,
            UNIQUE(month, day, away_team, home_team)
        )
    """)

    # Movimentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            season INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            from_team TEXT,
            to_team TEXT,
            trade_group_id INTEGER,
            contract_years INTEGER,
            contract_value INTEGER
        )
    """)

    # Draft
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS draft_picks (
            pick_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team TEXT NOT NULL UNIQUE,
            "1Y26" TEXT,
            "1Y26C" TEXT,
            "2Y26" TEXT,
            "2Y26C" TEXT,
            "1Y27" TEXT,
            "1Y27C" TEXT,
            "2Y27" TEXT,
            "2Y27C" TEXT,
            "1Y28" TEXT,
            "1Y28C" TEXT,
            "2Y28" TEXT,
            "2Y28C" TEXT,
            "1Y29" TEXT,
            "1Y29C" TEXT,
            "2Y29" TEXT,
            "2Y29C" TEXT
        )
    """)

    # Preencher Draft_Picks
    nba_teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Charlotte Hornets', 'Chicago Bulls',
        'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
        'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 'Los Angeles Clippers',
        'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks',
        'Minnesota Timberwolves', 'Montreal Mastodons', 'New Orleans Pelicans', 'New York Knicks',
        'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trailblazers', 'Sacramento Kings', 'San Diego Caravels',
        'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
    ]

    for team in nba_teams:
        try:
            cursor.execute("""
                INSERT INTO draft_picks (
                    team, "1Y26", "1Y26C", "2Y26", "2Y26C",
                    "1Y27", "1Y27C", "2Y27", "2Y27C",
                    "1Y28", "1Y28C", "2Y28", "2Y28C",
                    "1Y29", "1Y29C", "2Y29", "2Y29C"
                ) VALUES (?, ?, NULL, ?, NULL, ?, NULL, ?, NULL, ?, NULL, ?, NULL, ?, NULL, ?, NULL)
            """, (team, team, team, team, team, team, team, team, team))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


def insert_game_data(json_file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        games_data = json.load(f)
    
    games_inserted = 0
    games_skipped = 0
    
    for game in games_data:
        try:
            season = get_season_from_date(game['game_date'])
            
            cursor.execute("""
                INSERT INTO games (game_date, season, away_team, away_score, home_team, home_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (game['game_date'], season, game['away_team'], game['away_score'], game['home_team'], game['home_score']))
            
            game_id = cursor.lastrowid
            team_player_counts = {}
            
            for p in game['players']:
                if 'team_name' in p:
                    is_away = (p['team_name'] == game['away_team'])
                    points_against = game['home_score'] if is_away else game['away_score']
                    win = 1 if (is_away and game['away_score'] > game['home_score']) or \
                               (not is_away and game['home_score'] > game['away_score']) else 0
                    
                    cursor.execute("""
                        INSERT INTO team_stats (
                            game_id, season, team_name, fg_made, fg_att, tp_made, tp_att,
                            ft_made, ft_att, turnovers, blocks, steals, rebounds, assists, points, points_against, win
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (game_id, season, p['team_name'], p['fg_made'], p['fg_att'],
                          p['tp_made'], p['tp_att'], p['ft_made'], p['ft_att'],
                          p['to'], p['blk'], p['stl'], p['reb'],
                          p['ast'], p['pts'], points_against, win))
                
                else:
                    raw_name = p['player']
                    team = p['team']

                    # Mapa de nomes
                    final_player_name = PLAYER_NAME_MAP.get(raw_name, raw_name)

                    cursor.execute("SELECT player_id FROM players WHERE name = ?", (final_player_name,))
                    result = cursor.fetchone()
                    
                    if result is None:
                        cursor.execute("INSERT INTO players (name, team) VALUES (?, ?)", (final_player_name, team))
                        actual_player_id = cursor.lastrowid
                    else:
                        actual_player_id = result[0]
                    
                    # 5 inicial
                    if team not in team_player_counts:
                        team_player_counts[team] = 0
                    team_player_counts[team] += 1
                    started = 1 if team_player_counts[team] <= 5 else 0
                    
                    cursor.execute("""
                        INSERT INTO player_stats (
                            game_id, player_id, season, player_name, team, started, minutes, fg_made, fg_att, tp_made, tp_att,
                            ft_made, ft_att, turnovers, blocks, steals, rebounds, assists, points
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        game_id, actual_player_id, season, final_player_name, team, started, p['min'],
                        p['fg_made'], p['fg_att'], p['tp_made'], p['tp_att'],
                        p['ft_made'], p['ft_att'], p['to'], p['blk'],
                        p['stl'], p['reb'], p['ast'], p['pts']
                    ))
            
            games_inserted += 1
            
        except sqlite3.IntegrityError:
            games_skipped += 1
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Processed {os.path.basename(json_file_path)}: {games_inserted} games inserted, {games_skipped} skipped.")

def update_database_from_folder():
    if not os.path.exists(GAME_DATA_FOLDER):
        print(f"Error")
        return
    
    json_files = [f for f in os.listdir(GAME_DATA_FOLDER) if f.endswith('.json')]
    if not json_files:
        print(f"JSON missing")
        return
    
    print(f"Found {len(json_files)} JSON file\n")
    
    for json_file in sorted(json_files):
        insert_game_data(os.path.join(GAME_DATA_FOLDER, json_file))

def main():
    try:
        create_database()
        update_database_from_folder()
        print("\nSuccess")
    except Exception as e:
        print(f"\nFailure")

if __name__ == "__main__":
    main()