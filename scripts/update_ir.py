from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import sqlite3
import time
import os
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DB_PATH = os.path.join(project_root, "hh_stats.db")
GAME_DATA_FOLDER = os.path.join(project_root, "game_data")

# Map: NBA API Name -> Database Name
NAME_MAP = {
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
    "Day'Ron Sharpe": "Dayron Sharpe",
    "DayRon Sharpe": "Dayron Sharpe",
    "Caris LeVert": "Caris LeVert",
    "Luka Doncic": "Luka Dončić",
    "Nikola Jokic": "Nikola Jokić",
    "Bogdan Bogdanovic": "Bogdan Bogdanović",
    "Kristaps Porzingis": "Kristaps Porziņģis",
    "Nikola Vucevic": "Nikola Vučević",
    "Jusuf Nurkic": "Jusuf Nurkić",
    "Jonas Valanciunas": "Jonas Valančiūnas",
    "Dennis Schroder": "Dennis Schröder",
    "Dante Exum": "Danté Exum",
    "Karlo Matkovic": "Karlo Matković",
    "Moussa Diabate": "Moussa Diabaté",
    "Pacome Dadiet": "Pacôme Dadiet",
    "Tidjane Salaun": "Tidjane Salaün",
    "Kasparas Jakucionis": "Kasparas Jakučionis",
    "Nikola Jovic": "Nikola Jović",
    "Alperen Sengun": "Alperen Sengun",
}

def get_reference_date():
    """Get reference date from most recent game_data file + 1 day."""
    if not os.path.exists(GAME_DATA_FOLDER):
        return datetime.today().strftime('%Y-%m-%d')

    json_files = [f for f in os.listdir(GAME_DATA_FOLDER) if f.endswith('.json')]
    if not json_files:
        return datetime.today().strftime('%Y-%m-%d')

    dates = []
    for f in json_files:
        try:
            date_str = f.replace('.json', '')
            dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
        except ValueError:
            continue

    if not dates:
        return datetime.today().strftime('%Y-%m-%d')

    most_recent = max(dates)
    reference = most_recent + timedelta(days=1)
    return reference.strftime('%Y-%m-%d')


def get_db_player_names():
    """Fetch all player names currently in the SQLite database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return set()
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM players")
        names = {row[0] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
        names = set()
    finally:
        conn.close()
    
    return names


def find_DNPs(player_id, season_start, season_end, season, min_gap_days=29):
    """Find gaps in a player's game log indicating injury."""
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        df = gamelog.get_data_frames()[0]
    except:
        df = pd.DataFrame()

    if df.empty:
        today = pd.to_datetime(datetime.today().date())
        return pd.DataFrame([(
            pd.to_datetime(season_start),
            today,
            (today - pd.to_datetime(season_start)).days
        )], columns=['PREV_GAME_DATE', 'GAME_DATE', 'GAP'])

    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE')
    all_dates = list(df['GAME_DATE'])
    gaps = []
    previous_date = pd.to_datetime(season_start)
    today = pd.to_datetime(datetime.today().date())

    for current_date in all_dates:
        gap = (current_date - previous_date).days
        if gap >= min_gap_days:
            gap_end = min(current_date, today)
            gaps.append((previous_date, gap_end, (gap_end - previous_date).days))
        previous_date = current_date

    if (today - previous_date).days >= min_gap_days:
        gaps.append((previous_date, today, (today - previous_date).days))

    return pd.DataFrame(gaps, columns=['PREV_GAME_DATE', 'GAME_DATE', 'GAP'])


def get_injured_players(season, season_start, season_end, reference_date, min_gap_days=29):
    """Get list of players currently on IR based on game log gaps, filtered by DB existence."""
    reference_date = pd.to_datetime(reference_date)
    today = pd.to_datetime(datetime.today().date())
    season_end_dt = pd.to_datetime(season_end)

    all_players = players.get_players()
    active_players = [p for p in all_players if p['is_active']]

    db_names = get_db_player_names()
    print(f"Found {len(db_names)} players in database to check against.")

    injured_players = []

    for player in active_players:
        player_id = player['id']
        api_name = player['full_name']
        
        mapped_name = NAME_MAP.get(api_name, api_name)
        
        if mapped_name not in db_names and api_name not in db_names:
            continue

        print(f"Processing {api_name}...")

        gaps = find_DNPs(player_id, season_start, season_end, season, min_gap_days)

        if not gaps.empty:
            gaps = gaps.copy()
            gaps['GAME_DATE'] = gaps['GAME_DATE'].apply(
                lambda x: min(today, season_end_dt) if x == 'unknown' else pd.to_datetime(x)
            )
            gaps = gaps[(gaps['PREV_GAME_DATE'] <= reference_date) &
                        (gaps['GAME_DATE'] >= reference_date)]

            if not gaps.empty:
                injured_players.append(mapped_name)

        time.sleep(0.6)

    return injured_players


def update_ir_status(injured_players):
    """Update IR column in players table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Reset
    cursor.execute("UPDATE players SET IR = 0")
    print("Reset all players IR status to 0.")

    updated_count = 0
    not_found = []

    for db_name in injured_players:
        cursor.execute("UPDATE players SET IR = 1 WHERE name = ?", (db_name,))

        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found.append(db_name)

    conn.commit()
    conn.close()

    return updated_count, not_found


def main():
    season = '2025-26'
    season_start = '2025-10-21'
    season_end = '2026-04-12'
    min_gap_days = 29
    reference_date = get_reference_date()

    print(f"Reference date: {reference_date}\n")

    injured_players = get_injured_players(
        season, season_start, season_end, reference_date, min_gap_days
    )

    updated_count, not_found = update_ir_status(injured_players)

    print(f"\nIR Update Complete:")
    print(f"  - Players marked as injured: {updated_count}")
    
    if not_found:
        print(f"  - Players identified as injured but not matched in DB: {len(not_found)}")
        for name in not_found:
            print(f"    - {name}")


if __name__ == "__main__":
    main()