import sqlite3
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DB_PATH = os.path.join(project_root, "hh_stats.db")


def get_season_from_date(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    if date.month >= 7:
        return date.year + 1
    return date.year


def get_next_trade_group_id(cursor):
    cursor.execute("SELECT MAX(trade_group_id) FROM transactions")
    result = cursor.fetchone()[0]
    return (result or 0) + 1


def format_pick_name(pick_col, original_team):
    """Example: [("1Y26", "Los Angeles Lakers")]) '"""
    round_num = "1st" if pick_col[0] == "1" else "2nd"
    year = "20" + pick_col[2:4]

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

    abbrev = team_abbrevs.get(original_team, original_team[:3].upper())
    return f"{year} {round_num} ({abbrev})"


def sign_player(player_name, team, date, years=None, value=None):
    """
    Como usar
        sign_player("LeBron James", "Los Angeles Lakers", "2024-07-15", years=2, value=100000000)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    season = get_season_from_date(date)

    cursor.execute("""
        INSERT INTO transactions (transaction_type, transaction_date, season, player_name, from_team, to_team, contract_years, contract_value)
        VALUES ('SIGNING', ?, ?, ?, NULL, ?, ?, ?)
    """, (date, season, player_name, team, years, value))

    conn.commit()
    conn.close()
    print(f"Signed {player_name} to {team}")


def release_player(player_name, team, date):
    """
    Como usar
        release_player("Player", "Team", "XXXX-MM-DD")
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    season = get_season_from_date(date)

    cursor.execute("""
        INSERT INTO transactions (transaction_type, transaction_date, season, player_name, from_team, to_team)
        VALUES ('RELEASE', ?, ?, ?, ?, NULL)
    """, (date, season, player_name, team))

    conn.commit()
    conn.close()
    print(f"Released {player_name} from {team}")


def trade(date, *team_packages):
    """

    Como usar (2 equipas):
        trade("2024-02-08",
            ("New York Knicks", ["Player A", "Player B"]),
            ("Dallas Mavericks", ["Player C"])
        )

    Como usar (3 equipas):
        trade("2024-02-08",
            ("Team A", ["Player 1"]),
            ("Team B", ["Player 2", "Player 3"]),
            ("Team C", ["Player 4"])
        )

    Com picks - (pick_column, original_team):
        trade("2024-02-08",
            ("New York Knicks", ["Player A"], [("1Y26", "Los Angeles Lakers")]),
            ("Dallas Mavericks", ["Player C"], [("2Y27", "Dallas Mavericks")])
        )

    Pick columns: 1Y26, 2Y26, 1Y27, 2Y27, 1Y28, 2Y28, 1Y29, 2Y29

    """
    if len(team_packages) < 2:
        print("Error: Trade requires at least 2 teams")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    season = get_season_from_date(date)
    trade_group_id = get_next_trade_group_id(cursor)

    teams = [pkg[0] for pkg in team_packages]

    for i, package in enumerate(team_packages):
        from_team = package[0]
        players = package[1] if len(package) > 1 else []
        picks = package[2] if len(package) > 2 else []

        if len(teams) == 2:
            to_team = teams[1] if i == 0 else teams[0]
        else:
            to_team = teams[(i + 1) % len(teams)]

        for player in players:
            cursor.execute("""
                INSERT INTO transactions (transaction_type, transaction_date, season, player_name, from_team, to_team, trade_group_id)
                VALUES ('TRADE', ?, ?, ?, ?, ?, ?)
            """, (date, season, player, from_team, to_team, trade_group_id))

            cursor.execute("""
                UPDATE players SET team = ? WHERE name = ?
            """, (to_team, player))

        for pick_col, original_team in picks:
            cursor.execute(f"""
                UPDATE draft_picks
                SET "{pick_col}" = ?
                WHERE team = ?
            """, (to_team, original_team))

            pick_name = format_pick_name(pick_col, original_team)
            cursor.execute("""
                INSERT INTO transactions (transaction_type, transaction_date, season, player_name, from_team, to_team, trade_group_id)
                VALUES ('TRADE', ?, ?, ?, ?, ?, ?)
            """, (date, season, pick_name, from_team, to_team, trade_group_id))

    conn.commit()
    conn.close()

    print(f"Trade completed (ID: {trade_group_id})")
    for package in team_packages:
        from_team = package[0]
        players = package[1] if len(package) > 1 else []
        picks = package[2] if len(package) > 2 else []

        if len(teams) == 2:
            to_team = teams[1] if from_team == teams[0] else teams[0]
        else:
            to_team = teams[(teams.index(from_team) + 1) % len(teams)]

        for player in players:
            print(f"  {player}: {from_team} -> {to_team}")
        for pick_col, original_team in picks:
            pick_name = format_pick_name(pick_col, original_team)
            print(f"  {pick_name}: {from_team} -> {to_team}")


def show_transactions(season=None, team=None, player=None):
    """
    Como usar:
        show_transactions()                      # All transactions
        show_transactions(season=2025)           # Filter by season
        show_transactions(team="Boston Celtics") # Filter by team
        show_transactions(player="LeBron")       # Filter by player name
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if season:
        query += " AND season = ?"
        params.append(season)
    if team:
        query += " AND (from_team LIKE ? OR to_team LIKE ?)"
        params.extend([f"%{team}%", f"%{team}%"])
    if player:
        query += " AND player_name LIKE ?"
        params.append(f"%{player}%")

    query += " ORDER BY transaction_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        print("No transactions found.")
        return

    print(f"\n{'='*80}")
    print(f"{'ID':<4} {'Type':<8} {'Date':<12} {'Player':<20} {'From':<15} {'To':<15}")
    print(f"{'='*80}")

    for row in rows:
        trans_id, trans_type, date, season, player_name, from_team, to_team, trade_group, years, value = row
        from_display = (from_team or "FA")[:15]
        to_display = (to_team or "Released")[:15]
        print(f"{trans_id:<4} {trans_type:<8} {date:<12} {player_name:<20} {from_display:<15} {to_display:<15}")

    print(f"{'='*80}\n")
    conn.close()


if __name__ == "__main__":

    # WRITE HERE
    # ================================================

    trade("2025-12-28",
        ("Oklahoma City Thunder", ["Desmond Bane", "Dorian F Smith", "Jordan Hawkins", "Kris Murray"], [("1Y29", "Orlando Magic"), ("1Y28", "Oklahoma City Thunder")]),
        ("Milwaukee Bucks", ["Devin Booker", "Amir Coffey"])
    )

    # ================================================
