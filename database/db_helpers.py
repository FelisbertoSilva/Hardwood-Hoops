import sqlite3
from datetime import datetime

DB_PATH = "hh_stats.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_players():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT player_name 
        FROM player_stats 
        ORDER BY player_name
    """)
    players = cursor.fetchall()
    conn.close()
    
    return players

def get_all_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT team_name 
        FROM team_stats 
        ORDER BY team_name
    """)
    teams = cursor.fetchall()
    conn.close()
    
    return teams

def get_total_games():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM games")
    total_games = cursor.fetchone()['count']
    conn.close()
    
    return total_games

def get_player_info(player_name):
    """Get basic player info from the players table (for players with no game stats)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, team, draft_year, draft_pick
        FROM players
        WHERE name = ?
    """, (player_name,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'name': row['name'],
            'team': row['team'],
            'draft_year': row['draft_year'],
            'draft_pick': row['draft_pick']
        }
    return None

def get_player_games(player_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            g.game_id,
            ps.team,
            ps.started,
            ps.minutes,
            ps.fg_made,
            ps.fg_att,
            ps.tp_made,
            ps.tp_att,
            ps.ft_made,
            ps.ft_att,
            ps.rebounds,
            ps.assists,
            ps.steals,
            ps.blocks,
            ps.turnovers,
            ps.points,
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score,
            -- Select Draft Info
            p.draft_year,
            p.draft_pick
        FROM player_stats ps
        JOIN games g ON ps.game_id = g.game_id
        -- FIXED: Changed p.player_name to p.name
        LEFT JOIN players p ON ps.player_name = p.name
        WHERE ps.player_name = ?
        ORDER BY g.game_date
    """, (player_name,))
    
    games = cursor.fetchall()
    conn.close()
    
    return games

def get_team_games(team_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as games_played,
            SUM(win) as wins
        FROM team_stats
        WHERE team_name = ?
    """, (team_name,))
    
    record = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            g.game_date,
            g.away_team,
            g.away_score,
            g.home_team,
            g.home_score,
            ts.win
        FROM team_stats ts
        JOIN games g ON ts.game_id = g.game_id
        WHERE ts.team_name = ?
        ORDER BY g.game_date DESC
    """, (team_name,))
    
    games = cursor.fetchall()
    conn.close()
    
    return record, games