import re
import json
import os

raw_text = """GAME 4
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC
Oklahoma City Thunder

@

Cleveland Cavaliers

Video Placeholder

Min
FGA
3PT
FTA
Tov
Blk
Stl
Reb
Ast
Pts
Jakob Poeltl		
44
1/8
0/0
2/2
3
1
2
14
3
4
Chet Holmgren		
25
2/6
1/1
3/3
1
2
0
1
2
8
Jalen Williams		
40
11/23
2/7
2/2
1
1
1
7
3
26
Shai G Alexander		
36
11/21
4/9
4/4
3
1
0
3
5
30
Keon Ellis		
37
5/10
5/8
0/0
3
1
4
2
0
15
Desmond Bane		
15
3/4
1/2
4/4
1
0
1
0
3
11
Dorian F Smith		
18
0/2
0/2
2/3
2
0
1
5
1
2
Luguentz Dort		
7
1/4
0/1
0/0
0
0
2
2
0
2
Naji Marshall		
4
2/3
1/1
0/0
0
0
0
1
1
5
Jaylin Williams		
1
0/1
0/1
0/0
0
0
0
1
0
0
Isaiah Joe		
3
0/0
0/0
0/0
0
0
0
0
0
0
Guerschon Yabusele		
10
1/2
1/1
0/0
3
1
1
2
0
3
Totals			
37/84
15/33
17/18
17
7
12
38
18
106
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FGA
3PT
FTA
Tov
Blk
Stl
Reb
Ast
Pts
Mitchell Robinson		
37
5/10
0/0
1/2
3
0
0
6
0
11
Evan Mobley		
43
5/12
1/3
3/4
3
2
5
13
6
14
Kevin Durant		
46
12/30
5/13
2/3
2
2
1
10
4
31
Alex Caruso		
36
0/1
0/1
3/3
1
0
4
1
3
3
Donovan Mitchell		
39
9/19
4/10
1/1
3
1
2
4
2
23
Myles Turner		
15
2/3
1/2
0/0
1
2
0
2
1
5
Dean Wade		
11
1/4
0/3
1/1
3
0
0
0
0
3
Gary Payton II		
8
1/1
1/1
1/1
0
1
0
1
0
4
Andre Drummond		
5
0/0
0/0
0/0
0
1
0
2
0
0
Totals			
35/80
12/33
12/15
16
9
12
39
16
94
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC"""

game_date = "2026-05-17"

raw_text = re.sub(r'[ \t]+', '\t', raw_text)

game_pattern = re.compile(
    r'([^\n]+?)\s*\n+@\s*\n+([^\n]+?)\s*\n'
)

player_stats_pattern = re.compile(
    r'([^\n]+)\t*\n(\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)'
)

totals_stats_pattern = re.compile(
    r'Totals\s+\n(\d+/\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)'
)

games_json = []

for match in game_pattern.finditer(raw_text):
    away_team, home_team = match.groups()
    away_team = away_team.strip().replace('\t', ' ')
    home_team = home_team.strip().replace('\t', ' ')
    
    game_start = match.end()
    next_match = game_pattern.search(raw_text, game_start)
    game_end = next_match.start() if next_match else len(raw_text)
    full_game_text = raw_text[game_start:game_end]
    
    sections = re.split(r'Min\nFG', full_game_text)

    if len(sections) < 3:
        continue
        
    away_text = sections[1]
    home_text = sections[2]

    def parse_team_stats(text_block, team_name):
        team_players = []
        
        def parse_val(v):
            if '/' in v:
                parts = v.split('/')
                return int(parts[0]), int(parts[1])
            return int(v)
        
        for p in player_stats_pattern.finditer(text_block):
            stats = {}
            stats["player"] = p.group(1).strip().replace('\t', ' ')
            stats["team"] = team_name
            stats["min"] = parse_val(p.group(2))
            stats["fg_made"], stats["fg_att"] = parse_val(p.group(3))
            stats["tp_made"], stats["tp_att"] = parse_val(p.group(4))
            stats["ft_made"], stats["ft_att"] = parse_val(p.group(5))
            stats["to"] = parse_val(p.group(6))
            stats["blk"] = parse_val(p.group(7))
            stats["stl"] = parse_val(p.group(8))
            stats["reb"] = parse_val(p.group(9))
            stats["ast"] = parse_val(p.group(10))
            stats["pts"] = parse_val(p.group(11))
            team_players.append(stats)
        
        totals_match = totals_stats_pattern.search(text_block)
        if totals_match:
            stats = {}
            stats["team_name"] = team_name
            stats["fg_made"], stats["fg_att"] = parse_val(totals_match.group(1))
            stats["tp_made"], stats["tp_att"] = parse_val(totals_match.group(2))
            stats["ft_made"], stats["ft_att"] = parse_val(totals_match.group(3))
            stats["to"] = parse_val(totals_match.group(4))
            stats["blk"] = parse_val(totals_match.group(5))
            stats["stl"] = parse_val(totals_match.group(6))
            stats["reb"] = parse_val(totals_match.group(7))
            stats["ast"] = parse_val(totals_match.group(8))
            stats["pts"] = sum(player["pts"] for player in team_players)  # Calcular pontos da equipa
            team_players.append(stats)
            
        return team_players

    away_stats = parse_team_stats(away_text, away_team)
    home_stats = parse_team_stats(home_text, home_team)
    

    away_score = away_stats[-1]["pts"] if away_stats and "team_name" in away_stats[-1] else 0
    home_score = home_stats[-1]["pts"] if home_stats and "team_name" in home_stats[-1] else 0
    
    all_players = away_stats + home_stats

    games_json.append({
        "game_date": game_date,
        "away_team": away_team,
        "away_score": away_score,
        "home_team": home_team,
        "home_score": home_score,
        "players": all_players
    })

script_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(script_dir)
game_data_path = os.path.join(project_root, "game_data")

os.makedirs(game_data_path, exist_ok=True)

output_path = os.path.join(game_data_path, f"{game_date}.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(games_json, f, indent=2)

print(f"Saved {len(games_json)} games to {output_path}")