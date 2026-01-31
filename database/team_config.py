"""
HH Configuração de eEquipas

"""

CONFERENCES = {
    'Eastern': {
        'Atlantic': [
            'Boston Celtics',
            'Brooklyn Nets',
            'Montreal Mastodons',  # Brooklyn Nets antes de 2025-26
            'New York Knicks',
            'Philadelphia 76ers',
            'Toronto Raptors'
        ],
        'Central': [
            'Chicago Bulls',
            'Cleveland Cavaliers',
            'Detroit Pistons',
            'Indiana Pacers',
            'Milwaukee Bucks'
        ],
        'Southeast': [
            'Atlanta Hawks',
            'Charlotte Hornets',
            'Miami Heat',
            'Orlando Magic',
            'Washington Wizards'
        ]
    },
    'Western': {
        'Northwest': [
            'Denver Nuggets',
            'Minnesota Timberwolves',
            'Oklahoma City Thunder',
            'Portland Trailblazers',
            'Utah Jazz'
        ],
        'Pacific': [
            'Golden State Warriors',
            'Los Angeles Clippers',
            'Los Angeles Lakers',
            'Phoenix Suns',
            'Sacramento Kings'
        ],
        'Southwest': [
            'Dallas Mavericks',
            'Houston Rockets',
            'Memphis Grizzlies',
            'New Orleans Pelicans',
            'San Antonio Spurs',
            'San Diego Caravels'  # Antonio Spurs antes de 2025-26
        ]
    }
}

def get_team_conference(team_name):
    for conference, divisions in CONFERENCES.items():
        for division, teams in divisions.items():
            if team_name in teams:
                return conference
    return None

def get_team_division(team_name):
    for conference, divisions in CONFERENCES.items():
        for division, teams in divisions.items():
            if team_name in teams:
                return division
    return None

def get_conference_teams(conference):
    if conference not in CONFERENCES:
        return []
    
    teams = []
    for division, team_list in CONFERENCES[conference].items():
        teams.extend(team_list)
    return teams

def get_division_teams(division):
    """Get all teams in a division"""
    for conference, divisions in CONFERENCES.items():
        if division in divisions:
            return divisions[division]
    return []