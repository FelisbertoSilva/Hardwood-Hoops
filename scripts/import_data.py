import re
import json
import os

raw_text = """SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Detroit Pistons
107
@
84
Cleveland Cavaliers
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Giannis Antetokounmpo		
45
13/24
1/1
4/5
3
2
2
16
5
31
Kevin Durant		
42
13/23
2/9
3/3
2
1
3
7
6
31
Duncan Robinson		
42
4/12
2/8
1/1
1
4
0
6
0
11
Derrick White		
41
1/4
1/2
1/1
2
0
1
4
8
4
James Harden		
44
8/12
6/8
1/2
3
0
1
2
8
23
Josh Okogie		
7
1/1
1/1
1/1
0
0
0
0
0
4
Jay Huff		
12
1/2
0/1
1/1
0
0
2
1
0
3
Steven Adams		
7
0/0
0/0
0/1
0
0
0
0
0
0
Javonte Green		
0
0/0
0/0
0/0
0
0
0
0
0
0
Marvin Bagley		
0
0/0
0/0
0/0
0
0
0
0
0
0
Jaden Hardy		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
41/78
13/30
12/15
11
7
9
36
27
107
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Mitchell Robinson		
34
1/7
0/0
1/2
2
1
2
8
2
3
Evan Mobley		
43
9/30
3/12
3/4
4
1
1
12
4
24
Mikal Bridges		
42
8/16
6/12
2/3
3
0
1
5
1
24
Alex Caruso		
23
0/3
0/2
1/1
1
1
1
2
1
1
Donovan Mitchell		
45
4/9
1/6
2/2
4
0
3
4
4
11
Ayo Dosunmu		
27
5/7
1/2
1/1
0
2
0
4
3
12
Wendell Carter Jr		
24
4/6
0/0
1/1
1
2
0
2
1
9
Jake LaRavia		
1
0/0
0/0
0/0
0
0
0
0
0
0
Caris LeVert		
1
0/0
0/0
0/0
0
0
0
0
0
0
Dean Wade		
0
0/0
0/0
0/0
0
0
0
0
0
0
Nae'Qwan Tomlin		
0
0/0
0/0
0/0
0
0
0
0
0
0
Craig Porter		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
31/78
11/34
11/14
15
7
8
37
16
84
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Phoenix Suns
89
@
91
Chicago Bulls
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Kelly Olynyk		
32
1/1
0/0
3/5
3
3
2
10
1
5
Michael Porter Jr		
38
4/13
1/6
3/3
0
0
2
11
2
12
Cooper Flagg		
38
7/20
1/3
8/9
2
2
1
15
5
23
Aaron Nesmith		
32
4/19
3/14
8/10
5
0
1
5
2
19
Andrew Nembhard		
38
5/17
0/7
2/4
3
0
1
1
3
12
Zach LaVine		
25
3/9
0/1
3/3
2
0
0
1
0
9
Jusuf Nurkic		
15
1/1
0/0
1/1
1
2
1
6
0
3
Bilal Coulibaly		
20
1/3
1/2
3/3
1
1
3
5
1
6
Jalen Smith		
2
0/0
0/0
0/0
0
0
0
0
0
0
Julian Strawther		
0
0/0
0/0
0/0
0
0
0
0
0
0
Tre Johnson		
0
0/0
0/0
0/0
0
0
0
0
0
0
Cody Williams		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
26/83
6/33
31/38
17
8
11
54
14
89
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Kel'el Ware		
39
3/10
0/5
5/6
4
2
1
19
0
11
Patrick Williams		
35
3/10
1/7
3/6
2
0
2
8
2
10
Kevin Huerter		
41
5/17
1/6
2/5
3
3
3
13
6
13
Reed Sheppard		
32
4/11
2/4
2/3
2
0
0
3
0
12
Kasparas Jakucionis		
40
7/18
4/7
3/4
2
1
2
2
4
21
Jaime Jaquez Jr		
15
0/3
0/1
0/0
0
0
0
2
1
0
Jaylon Tyson		
26
6/12
3/5
4/5
3
2
3
4
0
19
Luka Garza		
8
2/4
0/0
1/1
2
0
0
3
1
5
Tyler Smith		
1
0/0
0/0
0/0
0
0
0
0
0
0
Max Christie		
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
Sidy Cissoko		
0
0/0
0/0
0/0
0
0
0
0
0
0
Nikola Djurisic		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
30/85
11/35
20/30
18
8
11
54
14
91
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Dallas Mavericks
110
@
85
New Orleans Pelicans
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Onyeka Okongwu		
40
5/16
4/9
3/3
4
1
3
12
3
17
Lauri Markkanen		
35
7/13
3/6
0/1
4
0
0
7
1
17
Trey Murphy III		
32
10/18
6/14
3/3
1
0
2
7
1
29
Keon Ellis		
32
4/9
4/7
1/1
1
1
1
3
3
13
Luka Doncic		
34
9/15
2/5
0/1
0
2
2
6
6
20
Daniel Gafford		
14
4/5
0/0
0/0
2
0
1
5
0
8
Saddiq Bey		
17
1/3
1/2
0/0
2
0
0
3
0
3
Tyus Jones		
9
1/4
1/3
0/0
0
1
0
2
2
3
Dalton Knecht		
6
0/1
0/0
0/0
1
0
0
4
1
0
Cam Spencer		
16
0/0
0/0
0/0
0
2
1
0
3
0
Dwight Powell		
2
0/0
0/0
0/0
0
0
0
0
0
0
Isaiah Collier		
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
Totals			
41/84
21/46
7/9
15
7
10
49
20
110
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Jarrett Allen		
19
5/10
0/1
1/1
1
0
0
2
2
11
Ausar Thompson		
41
3/8
0/0
0/2
1
2
5
13
2
6
Sam Hauser		
35
3/9
3/9
3/4
4
2
1
6
0
12
Deni Avdija		
42
5/22
1/10
7/7
4
0
1
6
7
18
Dyson Daniels		
33
8/17
0/3
4/6
1
1
1
3
2
20
Brandin Podziemski		
13
2/5
0/1
4/6
2
0
0
1
0
8
Luke Kornet		
26
0/1
0/0
0/1
1
1
1
9
0
0
Kyshawn George		
16
1/6
0/3
4/4
2
0
0
1
1
6
JaKobe Walter		
9
0/2
0/0
1/1
0
0
0
0
0
1
Leonard Miller		
6
1/2
1/1
0/0
0
0
0
0
0
3
Totals			
28/82
5/28
24/32
16
6
9
41
14
85
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Golden State Warriors
106
@
114
Houston Rockets
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Joel Embiid		
42
4/17
0/3
6/8
1
1
3
12
2
14
Draymond Green		
41
10/13
7/8
2/6
5
2
3
12
2
29
Klay Thompson		
42
8/20
7/17
4/9
4
0
1
4
3
27
Brandon Ingram		
41
6/13
2/4
4/4
3
1
2
3
2
18
Ja Morant		
38
4/13
1/5
2/2
1
2
1
2
6
11
Robert Williams		
9
0/0
0/0
0/0
0
0
0
3
1
0
Gui Santos		
10
1/2
0/1
0/0
0
0
0
2
2
2
Collin Murray Boyles		
14
1/4
0/0
2/2
0
2
1
3
1
4
Yang Hansen		
3
0/0
0/0
1/1
0
0
0
0
0
1
Oshae Brissett		
0
0/0
0/0
0/0
0
0
0
0
0
0
Alijah Martin		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
34/82
17/38
21/32
14
8
11
41
19
106
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Alperen Sengun		
40
9/23
0/6
3/5
2
2
1
11
3
21
Amen Thompson		
36
6/15
1/2
9/9
4
2
2
11
4
22
Peyton Watson		
28
7/11
2/3
0/0
1
1
3
8
2
16
Nickeil A Walker		
35
7/14
5/8
3/3
3
0
3
1
5
22
Ryan Rollins		
39
6/12
4/5
1/1
6
1
1
4
2
17
Mike Conley		
14
0/1
0/1
1/1
0
0
0
0
1
1
Goga Bitadze		
10
0/0
0/0
1/1
0
0
0
0
1
1
Jonathan Mogbo		
14
2/2
1/1
0/0
0
2
0
2
1
5
Kyle Kuzma		
22
2/3
1/2
4/4
2
0
0
2
1
9
Kentavious C Pope		
2
0/0
0/0
0/0
0
0
0
0
0
0
Tyrese Proctor		
0
0/0
0/0
0/0
0
0
0
0
0
0
Cam Christie		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
39/81
14/28
22/24
18
8
10
39
20
114
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


San Diego Caravels
98
@
105
Denver Nuggets
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Bam Adebayo		
40
9/16
0/3
6/6
2
2
2
8
4
24
Victor Wembanyama		
42
8/20
2/9
7/7
1
1
2
10
2
25
Tobias Harris		
38
2/4
1/2
2/3
3
0
0
5
3
7
Payton Pritchard		
41
2/11
1/7
4/4
3
1
0
6
2
9
Cade Cunningham		
38
8/15
2/5
3/4
4
2
2
3
7
21
Tim Hardaway Jr		
12
0/5
0/4
2/2
0
0
0
2
0
2
Dennis Schroder		
13
1/2
1/2
2/2
0
0
0
1
1
5
Neemias Queta		
10
0/2
0/0
2/2
0
2
0
1
0
2
Tre Jones		
6
1/2
1/2
0/0
1
0
2
0
0
3
Jonathan Isaac		
0
0/0
0/0
0/0
0
0
0
0
0
0
Buddy Hield		
0
0/0
0/0
0/0
0
0
0
0
0
0
Ryan Dunn		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
31/77
8/34
28/30
14
8
8
36
19
98
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Kevin Love		
37
2/6
2/3
1/2
1
0
1
13
3
7
Pascal Siakam		
44
11/26
0/7
4/7
1
3
1
10
7
26
Norman Powell		
31
5/11
2/6
0/0
3
0
3
5
1
12
CJ McCollum		
39
9/15
6/10
2/2
3
0
2
4
1
26
Jamal Murray		
39
11/22
2/9
5/5
2
1
2
5
4
29
Ben Simmons		
9
0/0
0/0
0/0
0
0
0
1
2
0
Pat Connaughton		
10
0/0
0/0
0/1
2
0
0
0
0
0
Kyle Lowry		
16
0/0
0/0
1/1
1
1
0
3
2
1
Jalen Pickett		
5
0/0
0/0
0/0
0
0
0
0
1
0
Hunter Tyson		
10
1/1
1/1
1/1
0
0
0
0
0
4
Noah Penda		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
39/81
13/36
14/19
13
5
9
41
21
105
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Philadelphia 76ers
101
@
90
Utah Jazz
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Nikola Vucevic		
31
5/10
3/3
7/7
3
4
2
6
1
20
LeBron James		
33
6/17
1/7
3/5
0
0
4
4
4
16
Jaylen Brown		
36
8/12
0/1
4/4
4
1
2
6
3
20
Coby White		
42
6/15
2/6
4/5
1
0
2
7
6
18
Miles McBride		
40
5/14
4/10
2/3
2
0
0
7
3
16
Josh Hart		
26
3/7
1/5
0/0
3
1
0
8
0
7
Quinten Post		
15
1/2
0/0
0/0
2
2
2
3
1
2
Brook Lopez		
8
0/1
0/0
0/3
0
1
1
2
0
0
Christian Koloko		
9
0/2
0/1
2/2
0
0
0
0
1
2
Bronny James		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
34/80
11/33
22/29
15
9
13
43
19
101
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Taylor Hendricks		
30
1/9
0/5
1/2
1
4
3
7
0
3
Jeremy Sochan		
42
6/9
1/1
4/5
3
0
1
7
2
17
Zaccharie Risacher		
33
2/11
1/4
2/3
3
1
0
5
1
7
Keyonte George		
29
5/10
1/3
2/4
1
0
0
2
4
13
Dylan Harper		
39
6/13
1/3
4/4
4
0
3
7
4
17
Jared McCain		
14
6/12
2/6
0/0
0
0
0
3
0
14
Zeke Nnaji		
12
3/5
0/1
1/2
1
0
2
0
0
7
AJ Johnson		
15
2/5
1/1
0/0
3
0
0
0
1
5
Brice Sensabaugh		
8
0/1
0/0
2/2
1
0
0
2
0
2
Liam McNeeley		
18
2/4
1/1
0/0
3
1
0
6
3
5
Totals			
33/79
8/25
16/22
20
6
9
39
15
90
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Boston Celtics
96
@
105
Los Angeles Clippers
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Karl Anthony Towns		
35
4/5
1/2
4/4
4
1
1
7
3
13
Derik Queen		
45
12/27
2/6
3/3
1
0
2
6
4
29
Jordan Poole		
40
2/6
1/5
3/3
1
3
2
4
3
8
DeAnthony Melton		
36
3/10
3/8
3/3
2
0
3
5
2
12
Anthony Black		
40
12/29
2/10
3/3
5
0
1
2
2
29
Tyler Herro		
12
1/2
1/2
1/1
1
0
1
1
1
4
Precious Achiuwa		
18
0/3
0/0
1/1
1
1
1
3
1
1
Paul Reed		
11
0/0
0/0
0/0
1
0
1
5
1
0
DayRon Sharpe		
2
0/0
0/0
0/0
0
1
0
2
0
0
AJ Green		
1
0/0
0/0
0/0
0
0
0
0
0
0
Jordan Walsh		
0
0/0
0/0
0/0
0
0
0
0
0
0
Jose Alvarado		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
34/82
10/33
18/18
16
6
12
35
17
96
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Adem Bona		
35
6/13
1/1
1/2
3
3
1
6
2
14
Alex Sarr		
42
22/33
5/8
2/2
3
2
3
8
3
51
Jaylen Wells		
44
4/11
1/5
4/4
4
1
2
13
5
13
Stephon Castle		
27
4/9
0/1
2/2
0
0
0
1
5
10
Kobe Bufkin		
32
6/13
1/4
0/0
3
0
1
6
0
13
Aaron Holiday		
18
0/1
0/1
0/1
2
1
2
1
2
0
Ziaire Williams		
12
0/1
0/1
2/2
1
0
0
2
0
2
Dom Barlow		
13
0/0
0/0
1/1
0
0
0
0
0
1
Nolan Traore		
8
0/0
0/0
0/0
0
0
0
0
0
0
Seth Curry		
9
0/0
0/0
1/1
1
0
1
0
0
1
Totals			
42/81
8/21
13/15
17
7
10
37
17
105
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
SPACINGSPACINGSPAC	SPACINGSPA	SPACINGSPA	SPACINGSPA	SPACINGSPACINGSPAC


Memphis Grizzlies
82
@
90
Oklahoma City Thunder
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Ivica Zubac		
40
7/13
0/1
2/3
3
1
1
8
4
16
Jaren Jackson Jr		
46
9/21
3/7
2/3
0
3
2
7
4
23
Herbert Jones		
41
6/19
2/7
1/1
1
3
2
10
3
15
Bruce Brown		
33
3/6
1/2
2/2
2
0
2
2
0
9
Egor Demin		
40
5/14
1/7
3/3
4
1
1
1
1
14
Justin Champagnie		
14
0/2
0/0
0/0
4
0
0
2
1
0
Will Riley		
18
2/2
1/1
0/0
2
0
1
4
1
5
Baylor Scheierman		
8
0/1
0/1
0/0
1
0
0
1
0
0
Andre Jackson Jr		
0
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
32/78
8/26
10/12
17
8
9
35
14
82
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC
Min
FG
3PT
FT
TO
Blk
Stl
Reb
Ast
Pts
Rudy Gobert		
41
5/8
0/0
0/2
4
3
2
10
0
10
Chet Holmgren		
37
3/9
2/4
2/4
3
1
2
6
1
10
Devin Booker		
43
11/13
4/4
1/1
2
2
3
8
4
27
Shai G Alexander		
43
8/25
1/5
9/9
3
2
1
7
9
26
Kris Dunn		
42
3/10
2/5
5/7
3
0
2
3
2
13
Jalen Williams		
15
1/5
1/1
0/0
0
0
1
2
3
3
Isaiah Joe		
7
0/0
0/0
0/0
0
0
0
1
0
0
Jaylen Clark		
5
0/1
0/0
0/0
0
0
0
0
0
0
Ricky Council IV		
5
0/0
0/0
1/1
0
0
1
0
0
1
Duop Reath		
2
0/0
0/0
0/0
0
0
0
0
0
0
Totals			
31/71
10/19
18/24
15
8
12
37
19
90
SPACINGSPACINGSPACING	S	SPAC	SPACIN	SPACIN	SPACIN	SPAC	SPAC	SPAC	SPAC	SPAC	SPAC"""

game_date = "2025-12-31"

# Cleanup de espaços
raw_text = re.sub(r'[ \t]+', '\t', raw_text)

# Encontrar inicio do jogo
game_pattern = re.compile(
    r'([^\n]+)\n(\d+)\n@\n(\d+)\n([^\n]+)\n'
)

# Stats de jogadores
player_stats_pattern = re.compile(
    r'([^\n]+)\t*\n(\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)'
)

# Stats da equipa
totals_stats_pattern = re.compile(
    r'Totals\s+\n(\d+/\d+)\n(\d+/\d+)\n(\d+/\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)\n(\d+)'
)

games_json = []

for match in game_pattern.finditer(raw_text):
    away_team, away_score, home_score, home_team = match.groups()
    away_team = away_team.strip().replace('\t', ' ')
    home_team = home_team.strip().replace('\t', ' ')
    
    # Isolar block de cada jogo
    game_start = match.end()
    next_match = game_pattern.search(raw_text, game_start)
    game_end = next_match.start() if next_match else len(raw_text)
    full_game_text = raw_text[game_start:game_end]
    
    # Dividir casa vs fora
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
            stats["pts"] = parse_val(totals_match.group(9))
            team_players.append(stats)
            
        return team_players

    away_stats = parse_team_stats(away_text, away_team)
    home_stats = parse_team_stats(home_text, home_team)
    
    all_players = away_stats + home_stats

    games_json.append({
        "game_date": game_date,
        "away_team": away_team,
        "away_score": int(away_score),
        "home_team": home_team,
        "home_score": int(home_score),
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