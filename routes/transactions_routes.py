import sys
import os
import sqlite3
from flask import Blueprint, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

transactions_bp = Blueprint('transactions', __name__)


def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "hh_stats.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_available_seasons():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT season FROM transactions ORDER BY season DESC")
    seasons = [row['season'] for row in cursor.fetchall()]
    conn.close()
    return seasons if seasons else [2025]


def get_trades(season):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_id, transaction_date, player_name, from_team, to_team, trade_group_id
        FROM transactions
        WHERE transaction_type = 'TRADE' AND season = ?
        ORDER BY transaction_date DESC, trade_group_id
    """, (season,))

    rows = cursor.fetchall()
    conn.close()

    # Juntar trocas por ID
    trades = {}
    for row in rows:
        group_id = row['trade_group_id']
        if group_id not in trades:
            trades[group_id] = {
                'date': row['transaction_date'],
                'players': []
            }
        trades[group_id]['players'].append({
            'player_name': row['player_name'],
            'from_team': row['from_team'],
            'to_team': row['to_team']
        })

    return list(trades.values())


def get_offseason_signings(season):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Off-season vs Regular Season
    year = season - 1
    start_date = f"{year}-07-01"
    end_date = f"{year}-10-31"

    cursor.execute("""
        SELECT transaction_date, player_name, to_team, contract_years, contract_value
        FROM transactions
        WHERE transaction_type = 'SIGNING'
        AND season = ?
        AND transaction_date >= ? AND transaction_date <= ?
        ORDER BY transaction_date DESC
    """, (season, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [{
        'date': row['transaction_date'],
        'player_name': row['player_name'],
        'team': row['to_team'],
        'years': row['contract_years'],
        'value': row['contract_value']
    } for row in rows]


def get_regular_season_signings(season):
    conn = get_db_connection()
    cursor = conn.cursor()

    year = season - 1
    start_date = f"{year}-11-01"
    end_date = f"{season}-06-30"

    cursor.execute("""
        SELECT transaction_date, player_name, to_team, contract_years, contract_value
        FROM transactions
        WHERE transaction_type = 'SIGNING'
        AND season = ?
        AND (transaction_date >= ? OR transaction_date <= ?)
        ORDER BY transaction_date DESC
    """, (season, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [{
        'date': row['transaction_date'],
        'player_name': row['player_name'],
        'team': row['to_team'],
        'years': row['contract_years'],
        'value': row['contract_value']
    } for row in rows]


def get_releases(season):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transaction_date, player_name, from_team
        FROM transactions
        WHERE transaction_type = 'RELEASE' AND season = ?
        ORDER BY transaction_date DESC
    """, (season,))

    rows = cursor.fetchall()
    conn.close()

    return [{
        'date': row['transaction_date'],
        'player_name': row['player_name'],
        'team': row['from_team']
    } for row in rows]


def format_salary(amount):
    if amount is None or amount == 0:
        return ""
    return f"${amount:,.0f}"


def format_contract(years, value):
    if not years and not value:
        return ""
    parts = []
    if years:
        parts.append(f"{years}yr" if years == 1 else f"{years}yrs")
    if value:
        if value >= 1000000:
            parts.append(f"${value / 1000000:.1f}M")
        else:
            parts.append(f"${value:,.0f}")
    return " / ".join(parts)


@transactions_bp.route('/transactions')
def transactions_page():

    available_seasons = get_available_seasons()

    season = request.args.get('season', type=int)
    if season is None or season not in available_seasons:
        season = available_seasons[0] if available_seasons else 2025

    trades = get_trades(season)
    offseason_signings = get_offseason_signings(season)
    regular_season_signings = get_regular_season_signings(season)
    releases = get_releases(season)

    return render_template('transactions.html',
                           season=season,
                           available_seasons=available_seasons,
                           trades=trades,
                           offseason_signings=offseason_signings,
                           regular_season_signings=regular_season_signings,
                           releases=releases,
                           format_contract=format_contract)
