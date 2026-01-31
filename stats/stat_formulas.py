def calculate_percentage(made, attempted):
    if attempted == 0:
        return 0.0
    return round((made / attempted) * 100, 1)

def calculate_efg(fg_made, tp_made, fg_att):
    if fg_att == 0:
        return 0.0
    return round(((fg_made + 0.5 * tp_made) / fg_att) * 100, 1)

def calculate_ts(points, fg_att, ft_att):
    denominator = 2 * (fg_att + 0.44 * ft_att)
    if denominator == 0:
        return 0.0
    return round((points / denominator) * 100, 1)


def calculate_two_point_stats(fg_made, fg_att, tp_made, tp_att):
    two_p_made = fg_made - tp_made
    two_p_att = fg_att - tp_att
    return two_p_made, two_p_att

def calculate_per_36(stat_per_game, minutes_per_game):
    if minutes_per_game == 0:
        return 0.0
    multiplier = 36 / minutes_per_game
    return round(stat_per_game * multiplier, 1)

def get_season_from_date(date_str):
    from datetime import datetime
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    if date.month >= 7:
        season_start = date.year
    else:
        season_start = date.year - 1
    
    season_end = str(season_start + 1)[-2:]
    return f"{season_start}-{season_end}"

def is_playoff_game(date_str):
    from datetime import datetime
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    if date.month == 4 and date.day >= 20:
        return True
    if date.month in [5, 6]:
        return True
    
    return False

def get_playoff_start_date(season):
    season_start_year = int(season.split('-')[0])
    season_end_year = season_start_year + 1
    return f"{season_end_year}-04-20"