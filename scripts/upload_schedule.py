import sqlite3
import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DB_PATH = os.path.join(project_root, "hh_stats.db")

SCHEDULE_TEXT = """
1 Nov -  Milwaukee Bucks vs  Philadelphia 76ers
1 Nov -  Denver Nuggets vs  San Diego Caravels
1 Nov -  Dallas Mavericks vs  Phoenix Suns
2 Nov -  New York Knicks vs  Boston Celtics
2 Nov -  Washington Wizards vs  Toronto Raptors
2 Nov -  Milwaukee Bucks vs  Montreal Mastodons
2 Nov -  Indiana Pacers vs  Orlando Magic
2 Nov -  Philadelphia 76ers vs  Detroit Pistons
2 Nov -  New Orleans Pelicans vs  Cleveland Cavaliers
2 Nov -  Charlotte Hornets vs  Chicago Bulls
2 Nov -  Miami Heat vs  Memphis Grizzlies
2 Nov -  Sacramento Kings vs  Houston Rockets
2 Nov -  Portland Trailblazers vs  Minnesota Timberwolves
2 Nov -  Los Angeles Lakers vs  Denver Nuggets
2 Nov -  Dallas Mavericks vs  Utah Jazz
2 Nov -  Atlanta Hawks vs  Golden State Warriors
2 Nov -  Los Angeles Clippers vs  Oklahoma City Thunder
3 Nov -  Indiana Pacers vs  Miami Heat
3 Nov -  Phoenix Suns vs  Los Angeles Lakers
4 Nov -  Detroit Pistons vs  Boston Celtics
4 Nov -  Montreal Mastodons vs  Toronto Raptors
4 Nov -  Milwaukee Bucks vs  New York Knicks
4 Nov -  Charlotte Hornets vs  Philadelphia 76ers
4 Nov -  Memphis Grizzlies vs  Orlando Magic
4 Nov -  Washington Wizards vs  Chicago Bulls
4 Nov -  Sacramento Kings vs  New Orleans Pelicans
4 Nov -  Cleveland Cavaliers vs  San Diego Caravels
4 Nov -  Portland Trailblazers vs  Denver Nuggets
4 Nov -  Atlanta Hawks vs  Los Angeles Clippers
4 Nov -  Utah Jazz vs  Golden State Warriors
4 Nov -  Minnesota Timberwolves vs  Oklahoma City Thunder
5 Nov -  Chicago Bulls vs  Montreal Mastodons
5 Nov -  Orlando Magic vs  Washington Wizards
5 Nov -  Boston Celtics vs  Charlotte Hornets
5 Nov -  Toronto Raptors vs  Detroit Pistons
5 Nov -  Philadelphia 76ers vs  Indiana Pacers
5 Nov -  Miami Heat vs  Milwaukee Bucks
5 Nov -  Cleveland Cavaliers vs  Memphis Grizzlies
5 Nov -  New Orleans Pelicans vs  Houston Rockets
5 Nov -  San Diego Caravels vs  Dallas Mavericks
5 Nov -  Phoenix Suns vs  Utah Jazz
5 Nov -  Minnesota Timberwolves vs  Los Angeles Clippers
5 Nov -  Atlanta Hawks vs  Portland Trailblazers
6 Nov -  Golden State Warriors vs  New York Knicks
6 Nov -  Sacramento Kings vs  Phoenix Suns
6 Nov -  Denver Nuggets vs  Los Angeles Lakers
7 Nov -  Cleveland Cavaliers vs  Toronto Raptors
7 Nov -  Utah Jazz vs  Charlotte Hornets
7 Nov -  Montreal Mastodons vs  Miami Heat
7 Nov -  San Diego Caravels vs  Chicago Bulls
7 Nov -  Los Angeles Clippers vs  Minnesota Timberwolves
8 Nov -  Los Angeles Lakers vs  Atlanta Hawks
8 Nov -  Golden State Warriors vs  Milwaukee Bucks
8 Nov -  Oklahoma City Thunder vs  Memphis Grizzlies
8 Nov -  Orlando Magic vs  Houston Rockets
8 Nov -  Detroit Pistons vs  Sacramento Kings
9 Nov -  Memphis Grizzlies vs  Boston Celtics
9 Nov -  Utah Jazz vs  Montreal Mastodons
9 Nov -  Dallas Mavericks vs  Philadelphia 76ers
9 Nov -  Los Angeles Clippers vs  Washington Wizards
9 Nov -  San Diego Caravels vs  Charlotte Hornets
9 Nov -  Oklahoma City Thunder vs  Cleveland Cavaliers
9 Nov -  Miami Heat vs  Indiana Pacers
9 Nov -  Golden State Warriors vs  Chicago Bulls
9 Nov -  Orlando Magic vs  New Orleans Pelicans
9 Nov -  Los Angeles Lakers vs  Minnesota Timberwolves
9 Nov -  Sacramento Kings vs  Denver Nuggets
9 Nov -  New York Knicks vs  Portland Trailblazers
10 Nov -  Los Angeles Clippers vs  Atlanta Hawks
10 Nov -  Houston Rockets vs  Miami Heat
10 Nov -  Detroit Pistons vs  Phoenix Suns
11 Nov -  San Diego Caravels vs  Boston Celtics
11 Nov -  Utah Jazz vs  Toronto Raptors
11 Nov -  Los Angeles Lakers vs  Philadelphia 76ers
11 Nov -  Oklahoma City Thunder vs  Washington Wizards
11 Nov -  Dallas Mavericks vs  Charlotte Hornets
11 Nov -  Memphis Grizzlies vs  Cleveland Cavaliers
11 Nov -  Montreal Mastodons vs  Indiana Pacers
11 Nov -  New York Knicks vs  Golden State Warriors
11 Nov -  Denver Nuggets vs  Sacramento Kings
11 Nov -  Detroit Pistons vs  Portland Trailblazers
12 Nov -  Houston Rockets vs  Montreal Mastodons
12 Nov -  San Diego Caravels vs  Washington Wizards
12 Nov -  Memphis Grizzlies vs  Atlanta Hawks
12 Nov -  Charlotte Hornets vs  Miami Heat
12 Nov -  Utah Jazz vs  Chicago Bulls
12 Nov -  Indiana Pacers vs  Milwaukee Bucks
12 Nov -  Dallas Mavericks vs  New Orleans Pelicans
12 Nov -  Golden State Warriors vs  Phoenix Suns
13 Nov -  New York Knicks vs  Sacramento Kings
13 Nov -  Houston Rockets vs  Boston Celtics
13 Nov -  Oklahoma City Thunder vs  Toronto Raptors
13 Nov -  Los Angeles Clippers vs  Philadelphia 76ers
13 Nov -  Cleveland Cavaliers vs  Orlando Magic
13 Nov -  Minnesota Timberwolves vs  Denver Nuggets
14 Nov -  Los Angeles Lakers vs  Memphis Grizzlies
14 Nov -  New York Knicks vs  Utah Jazz
14 Nov -  Chicago Bulls vs  Golden State Warriors
15 Nov -  Oklahoma City Thunder vs  Montreal Mastodons
15 Nov -  Toronto Raptors vs  Philadelphia 76ers
15 Nov -  Charlotte Hornets vs  Orlando Magic
15 Nov -  New Orleans Pelicans vs  Miami Heat
15 Nov -  Boston Celtics vs  Detroit Pistons
15 Nov -  Washington Wizards vs  Cleveland Cavaliers
15 Nov -  Denver Nuggets vs  Dallas Mavericks
15 Nov -  Atlanta Hawks vs  San Diego Caravels
15 Nov -  Houston Rockets vs  Minnesota Timberwolves
15 Nov -  Milwaukee Bucks vs  Los Angeles Clippers
15 Nov -  Utah Jazz vs  Sacramento Kings
16 Nov -  Oklahoma City Thunder vs  Boston Celtics
16 Nov -  Philadelphia 76ers vs  Toronto Raptors
16 Nov -  Indiana Pacers vs  Charlotte Hornets
16 Nov -  Denver Nuggets vs  New Orleans Pelicans
16 Nov -  Memphis Grizzlies vs  Phoenix Suns
16 Nov -  New York Knicks vs  Los Angeles Lakers
16 Nov -  Milwaukee Bucks vs  Golden State Warriors
16 Nov -  Chicago Bulls vs  Portland Trailblazers
17 Nov -  Atlanta Hawks vs  Dallas Mavericks
17 Nov -  Houston Rockets vs  San Diego Caravels
17 Nov -  Washington Wizards vs  Minnesota Timberwolves
18 Nov -  Toronto Raptors vs  Boston Celtics
18 Nov -  Philadelphia 76ers vs  Miami Heat
18 Nov -  Orlando Magic vs  Cleveland Cavaliers
18 Nov -  Charlotte Hornets vs  Indiana Pacers
18 Nov -  Atlanta Hawks vs  New Orleans Pelicans
18 Nov -  Detroit Pistons vs  Houston Rockets
18 Nov -  New York Knicks vs  Denver Nuggets
18 Nov -  Utah Jazz vs  Phoenix Suns
18 Nov -  Los Angeles Clippers vs  Los Angeles Lakers
18 Nov -  Milwaukee Bucks vs  Sacramento Kings
18 Nov -  Golden State Warriors vs  Portland Trailblazers
18 Nov -  Chicago Bulls vs  Oklahoma City Thunder
19 Nov -  Washington Wizards vs  Montreal Mastodons
19 Nov -  Cleveland Cavaliers vs  Philadelphia 76ers
19 Nov -  New Orleans Pelicans vs  Orlando Magic
19 Nov -  Detroit Pistons vs  Dallas Mavericks
19 Nov -  Phoenix Suns vs  San Diego Caravels
19 Nov -  Charlotte Hornets vs  Minnesota Timberwolves
19 Nov -  Memphis Grizzlies vs  Utah Jazz
20 Nov -  Washington Wizards vs  Boston Celtics
20 Nov -  Miami Heat vs  Toronto Raptors
20 Nov -  Portland Trailblazers vs  New York Knicks
20 Nov -  Houston Rockets vs  Indiana Pacers
20 Nov -  Memphis Grizzlies vs  Denver Nuggets
20 Nov -  Golden State Warriors vs  Los Angeles Clippers
20 Nov -  Chicago Bulls vs  Los Angeles Lakers
20 Nov -  Sacramento Kings vs  Oklahoma City Thunder
21 Nov -  New Orleans Pelicans vs  Philadelphia 76ers
21 Nov -  Milwaukee Bucks vs  Utah Jazz
21 Nov -  Montreal Mastodons vs  Golden State Warriors
21 Nov -  San Diego Caravels vs  Sacramento Kings
22 Nov -  Denver Nuggets vs  Washington Wizards
22 Nov -  Boston Celtics vs  Cleveland Cavaliers
22 Nov -  Portland Trailblazers vs  Memphis Grizzlies
22 Nov -  Houston Rockets vs  Dallas Mavericks
22 Nov -  Toronto Raptors vs  Phoenix Suns
22 Nov -  Utah Jazz vs  Oklahoma City Thunder
23 Nov -  New York Knicks vs  Charlotte Hornets
23 Nov -  Boston Celtics vs  Atlanta Hawks
23 Nov -  Washington Wizards vs  Orlando Magic
23 Nov -  Portland Trailblazers vs  Miami Heat
23 Nov -  Denver Nuggets vs  Detroit Pistons
23 Nov -  Philadelphia 76ers vs  Milwaukee Bucks
23 Nov -  Minnesota Timberwolves vs  New Orleans Pelicans
23 Nov -  Phoenix Suns vs  Houston Rockets
23 Nov -  Toronto Raptors vs  Los Angeles Clippers
23 Nov -  San Diego Caravels vs  Golden State Warriors
23 Nov -  Montreal Mastodons vs  Sacramento Kings
24 Nov -  Cleveland Cavaliers vs  Indiana Pacers
24 Nov -  Oklahoma City Thunder vs  Los Angeles Lakers
25 Nov -  Charlotte Hornets vs  Boston Celtics
25 Nov -  Portland Trailblazers vs  Orlando Magic
25 Nov -  Dallas Mavericks vs  Miami Heat
25 Nov -  Atlanta Hawks vs  Indiana Pacers
25 Nov -  Houston Rockets vs  Memphis Grizzlies
25 Nov -  Chicago Bulls vs  San Diego Caravels
25 Nov -  Milwaukee Bucks vs  Minnesota Timberwolves
25 Nov -  Los Angeles Clippers vs  Denver Nuggets
25 Nov -  Golden State Warriors vs  Utah Jazz
25 Nov -  Montreal Mastodons vs  Phoenix Suns
25 Nov -  Toronto Raptors vs  Sacramento Kings
25 Nov -  New Orleans Pelicans vs  Oklahoma City Thunder
26 Nov -  Toronto Raptors vs  Golden State Warriors
26 Nov -  Philadelphia 76ers vs  New York Knicks
26 Nov -  Washington Wizards vs  Charlotte Hornets
26 Nov -  Miami Heat vs  Orlando Magic
26 Nov -  Minnesota Timberwolves vs  Cleveland Cavaliers
26 Nov -  Detroit Pistons vs  Milwaukee Bucks
26 Nov -  Chicago Bulls vs  Houston Rockets
26 Nov -  Memphis Grizzlies vs  Dallas Mavericks
27 Nov -  Portland Trailblazers vs  Atlanta Hawks
27 Nov -  Washington Wizards vs  Detroit Pistons
27 Nov -  Indiana Pacers vs  Los Angeles Clippers
27 Nov -  Montreal Mastodons vs  Los Angeles Lakers
28 Nov -  Orlando Magic vs  Boston Celtics
28 Nov -  Dallas Mavericks vs  Toronto Raptors
28 Nov -  New York Knicks vs  Miami Heat
28 Nov -  Montreal Mastodons vs  Denver Nuggets
28 Nov -  New Orleans Pelicans vs  Golden State Warriors
29 Nov -  Portland Trailblazers vs  Philadelphia 76ers
29 Nov -  Orlando Magic vs  Chicago Bulls
29 Nov -  Dallas Mavericks vs  Milwaukee Bucks
29 Nov -  Atlanta Hawks vs  Houston Rockets
29 Nov -  Los Angeles Lakers vs  San Diego Caravels
29 Nov -  Los Angeles Clippers vs  Minnesota Timberwolves
29 Nov -  Indiana Pacers vs  Utah Jazz
29 Nov -  Charlotte Hornets vs  Sacramento Kings
30 Nov -  Philadelphia 76ers vs  Boston Celtics
30 Nov -  Memphis Grizzlies vs  Toronto Raptors
30 Nov -  Detroit Pistons vs  Montreal Mastodons
30 Nov -  Chicago Bulls vs  New York Knicks
30 Nov -  Portland Trailblazers vs  Washington Wizards
30 Nov -  Miami Heat vs  Atlanta Hawks
30 Nov -  Los Angeles Clippers vs  Cleveland Cavaliers
30 Nov -  New Orleans Pelicans vs  Denver Nuggets
30 Nov -  Indiana Pacers vs  Phoenix Suns
30 Nov -  Sacramento Kings vs  Golden State Warriors
30 Nov -  Charlotte Hornets vs  Oklahoma City Thunder
1 Dec -  San Diego Caravels vs  Dallas Mavericks
1 Dec -  Los Angeles Lakers vs  Utah Jazz
2 Dec -  Chicago Bulls vs  Boston Celtics
2 Dec -  Milwaukee Bucks vs  Washington Wizards
2 Dec -  Toronto Raptors vs  Atlanta Hawks
2 Dec -  New York Knicks vs  Detroit Pistons
2 Dec -  Orlando Magic vs  Memphis Grizzlies
2 Dec -  Philadelphia 76ers vs  New Orleans Pelicans
2 Dec -  Denver Nuggets vs  Phoenix Suns
2 Dec -  Minnesota Timberwolves vs  Los Angeles Lakers
2 Dec -  Charlotte Hornets vs  Golden State Warriors
2 Dec -  Miami Heat vs  Sacramento Kings
2 Dec -  Indiana Pacers vs  Portland Trailblazers
2 Dec -  Cleveland Cavaliers vs  Oklahoma City Thunder
3 Dec -  Toronto Raptors vs  Montreal Mastodons
3 Dec -  Detroit Pistons vs  Chicago Bulls
3 Dec -  Orlando Magic vs  Milwaukee Bucks
3 Dec -  Memphis Grizzlies vs  Houston Rockets
3 Dec -  New Orleans Pelicans vs  Dallas Mavericks
3 Dec -  Philadelphia 76ers vs  San Diego Caravels
3 Dec -  Miami Heat vs  Denver Nuggets
3 Dec -  Cleveland Cavaliers vs  Los Angeles Clippers
4 Dec -  Boston Celtics vs  New York Knicks
4 Dec -  Atlanta Hawks vs  Phoenix Suns
4 Dec -  Charlotte Hornets vs  Los Angeles Lakers
4 Dec -  Minnesota Timberwolves vs  Sacramento Kings
4 Dec -  Utah Jazz vs  Portland Trailblazers
4 Dec -  Indiana Pacers vs  Oklahoma City Thunder
5 Dec -  San Diego Caravels vs  Orlando Magic
5 Dec -  Dallas Mavericks vs  Chicago Bulls
5 Dec -  Minnesota Timberwolves vs  Utah Jazz
5 Dec -  Miami Heat vs  Los Angeles Clippers
6 Dec -  Toronto Raptors vs  Washington Wizards
6 Dec -  Dallas Mavericks vs  Indiana Pacers
6 Dec -  Los Angeles Lakers vs  Milwaukee Bucks
6 Dec -  New Orleans Pelicans vs  Memphis Grizzlies
6 Dec -  Boston Celtics vs  Houston Rockets
6 Dec -  Atlanta Hawks vs  Denver Nuggets
6 Dec -  Portland Trailblazers vs  Phoenix Suns
6 Dec -  Cleveland Cavaliers vs  Sacramento Kings
6 Dec -  New York Knicks vs  Oklahoma City Thunder
7 Dec -  Los Angeles Lakers vs  Toronto Raptors
7 Dec -  Milwaukee Bucks vs  Philadelphia 76ers
7 Dec -  Montreal Mastodons vs  Charlotte Hornets
7 Dec -  Chicago Bulls vs  Orlando Magic
7 Dec -  Boston Celtics vs  New Orleans Pelicans
7 Dec -  Miami Heat vs  San Diego Caravels
7 Dec -  Atlanta Hawks vs  Utah Jazz
7 Dec -  New York Knicks vs  Los Angeles Clippers
7 Dec -  Phoenix Suns vs  Golden State Warriors
7 Dec -  Minnesota Timberwolves vs  Portland Trailblazers
8 Dec -  Washington Wizards vs  Indiana Pacers
8 Dec -  Houston Rockets vs  Sacramento Kings
9 Dec -  Charlotte Hornets vs  Philadelphia 76ers
9 Dec -  Denver Nuggets vs  Miami Heat
9 Dec -  Montreal Mastodons vs  Cleveland Cavaliers
9 Dec -  Los Angeles Lakers vs  Chicago Bulls
9 Dec -  Dallas Mavericks vs  Memphis Grizzlies
9 Dec -  Boston Celtics vs  San Diego Caravels
9 Dec -  Oklahoma City Thunder vs  Utah Jazz
9 Dec -  New York Knicks vs  Phoenix Suns
9 Dec -  Detroit Pistons vs  Golden State Warriors
9 Dec -  New Orleans Pelicans vs  Portland Trailblazers
10 Dec -  San Diego Caravels vs  Atlanta Hawks
10 Dec -  Philadelphia 76ers vs  Montreal Mastodons
10 Dec -  Chicago Bulls vs  Washington Wizards
10 Dec -  Toronto Raptors vs  Charlotte Hornets
10 Dec -  Denver Nuggets vs  Orlando Magic
10 Dec -  Memphis Grizzlies vs  Indiana Pacers
10 Dec -  Cleveland Cavaliers vs  Milwaukee Bucks
10 Dec -  Boston Celtics vs  Dallas Mavericks
10 Dec -  Los Angeles Lakers vs  Minnesota Timberwolves
10 Dec -  Phoenix Suns vs  Los Angeles Clippers
10 Dec -  Sacramento Kings vs  Oklahoma City Thunder
11 Dec -  Washington Wizards vs  Miami Heat
11 Dec -  Detroit Pistons vs  Los Angeles Clippers
11 Dec -  New Orleans Pelicans vs  Sacramento Kings
11 Dec -  Houston Rockets vs  Portland Trailblazers
12 Dec -  Milwaukee Bucks vs  New York Knicks
12 Dec -  Minnesota Timberwolves vs  Philadelphia 76ers
12 Dec -  Los Angeles Lakers vs  Dallas Mavericks
12 Dec -  Detroit Pistons vs  Utah Jazz
12 Dec -  New Orleans Pelicans vs  Phoenix Suns
13 Dec -  Montreal Mastodons vs  Washington Wizards
13 Dec -  Denver Nuggets vs  Charlotte Hornets
13 Dec -  Atlanta Hawks vs  Cleveland Cavaliers
13 Dec -  Miami Heat vs  Chicago Bulls
13 Dec -  Los Angeles Clippers vs  San Diego Caravels
13 Dec -  Sacramento Kings vs  Minnesota Timberwolves
13 Dec -  Golden State Warriors vs  Oklahoma City Thunder
14 Dec -  Indiana Pacers vs  Boston Celtics
14 Dec -  Chicago Bulls vs  Toronto Raptors
14 Dec -  Charlotte Hornets vs  Montreal Mastodons
14 Dec -  Orlando Magic vs  New York Knicks
14 Dec -  Atlanta Hawks vs  Philadelphia 76ers
14 Dec -  Sacramento Kings vs  Detroit Pistons
14 Dec -  Miami Heat vs  Milwaukee Bucks
14 Dec -  Los Angeles Lakers vs  Memphis Grizzlies
14 Dec -  Los Angeles Clippers vs  New Orleans Pelicans
14 Dec -  Phoenix Suns vs  Dallas Mavericks
14 Dec -  Portland Trailblazers vs  Utah Jazz
14 Dec -  Houston Rockets vs  Golden State Warriors
15 Dec -  Denver Nuggets vs  Cleveland Cavaliers
15 Dec -  San Diego Caravels vs  Minnesota Timberwolves
15 Dec -  Houston Rockets vs  Oklahoma City Thunder
16 Dec -  Milwaukee Bucks vs  Boston Celtics
16 Dec -  Golden State Warriors vs  Toronto Raptors
16 Dec -  Denver Nuggets vs  Montreal Mastodons
16 Dec -  Miami Heat vs  Philadelphia 76ers
16 Dec -  New York Knicks vs  Atlanta Hawks
16 Dec -  Chicago Bulls vs  Detroit Pistons
16 Dec -  Utah Jazz vs  Indiana Pacers
16 Dec -  Phoenix Suns vs  Memphis Grizzlies
16 Dec -  Orlando Magic vs  Dallas Mavericks
16 Dec -  Washington Wizards vs  Los Angeles Lakers
16 Dec -  Oklahoma City Thunder vs  Portland Trailblazers
17 Dec -  Indiana Pacers vs  New York Knicks
17 Dec -  Detroit Pistons vs  Charlotte Hornets
17 Dec -  Miami Heat vs  Cleveland Cavaliers
17 Dec -  Boston Celtics vs  Chicago Bulls
17 Dec -  Utah Jazz vs  Milwaukee Bucks
17 Dec -  Phoenix Suns vs  New Orleans Pelicans
17 Dec -  Sacramento Kings vs  San Diego Caravels
17 Dec -  Houston Rockets vs  Los Angeles Clippers
18 Dec -  Philadelphia 76ers vs  Toronto Raptors
18 Dec -  Golden State Warriors vs  Montreal Mastodons
18 Dec -  Denver Nuggets vs  Atlanta Hawks
18 Dec -  Minnesota Timberwolves vs  Dallas Mavericks
18 Dec -  Houston Rockets vs  Los Angeles Lakers
18 Dec -  Washington Wizards vs  Portland Trailblazers
19 Dec -  Golden State Warriors vs  Boston Celtics
19 Dec -  Sacramento Kings vs  Charlotte Hornets
19 Dec -  Toronto Raptors vs  Orlando Magic
19 Dec -  Detroit Pistons vs  Memphis Grizzlies
19 Dec -  Washington Wizards vs  Oklahoma City Thunder
20 Dec -  Los Angeles Clippers vs  Montreal Mastodons
20 Dec -  Atlanta Hawks vs  Miami Heat
20 Dec -  Portland Trailblazers vs  Detroit Pistons
20 Dec -  Utah Jazz vs  Cleveland Cavaliers
20 Dec -  Charlotte Hornets vs  Chicago Bulls
20 Dec -  San Diego Caravels vs  Milwaukee Bucks
20 Dec -  Oklahoma City Thunder vs  Phoenix Suns
20 Dec -  Dallas Mavericks vs  Los Angeles Lakers
21 Dec -  Utah Jazz vs  Boston Celtics
21 Dec -  San Diego Caravels vs  New York Knicks
21 Dec -  Golden State Warriors vs  Philadelphia 76ers
21 Dec -  Montreal Mastodons vs  Orlando Magic
21 Dec -  Los Angeles Clippers vs  Indiana Pacers
21 Dec -  Portland Trailblazers vs  Memphis Grizzlies
21 Dec -  Toronto Raptors vs  Houston Rockets
21 Dec -  New Orleans Pelicans vs  Minnesota Timberwolves
21 Dec -  Washington Wizards vs  Denver Nuggets
22 Dec -  Cleveland Cavaliers vs  Chicago Bulls
22 Dec -  Dallas Mavericks vs  Sacramento Kings
23 Dec -  New Orleans Pelicans vs  Milwaukee Bucks
23 Dec -  Utah Jazz vs  New York Knicks
23 Dec -  Los Angeles Clippers vs  Charlotte Hornets
23 Dec -  Philadelphia 76ers vs  Atlanta Hawks
23 Dec -  Los Angeles Lakers vs  Orlando Magic
23 Dec -  Montreal Mastodons vs  Miami Heat
23 Dec -  Golden State Warriors vs  Detroit Pistons
23 Dec -  Indiana Pacers vs  Cleveland Cavaliers
23 Dec -  Chicago Bulls vs  Memphis Grizzlies
23 Dec -  Toronto Raptors vs  San Diego Caravels
23 Dec -  Portland Trailblazers vs  Minnesota Timberwolves
23 Dec -  Houston Rockets vs  Denver Nuggets
23 Dec -  Washington Wizards vs  Phoenix Suns
23 Dec -  Dallas Mavericks vs  Oklahoma City Thunder
25 Dec -  Los Angeles Lakers vs  Miami Heat
25 Dec -  San Diego Caravels vs  Detroit Pistons
26 Dec -  Montreal Mastodons vs  New York Knicks
26 Dec -  Los Angeles Lakers vs  Washington Wizards
26 Dec -  Milwaukee Bucks vs  Orlando Magic
26 Dec -  Chicago Bulls vs  Cleveland Cavaliers
26 Dec -  Indiana Pacers vs  Dallas Mavericks
26 Dec -  Phoenix Suns vs  Minnesota Timberwolves
26 Dec -  Memphis Grizzlies vs  Utah Jazz
26 Dec -  Denver Nuggets vs  Golden State Warriors
26 Dec -  Portland Trailblazers vs  Sacramento Kings
26 Dec -  Boston Celtics vs  Oklahoma City Thunder
27 Dec -  Cleveland Cavaliers vs  Montreal Mastodons
27 Dec -  Charlotte Hornets vs  Atlanta Hawks
27 Dec -  Milwaukee Bucks vs  Miami Heat
27 Dec -  Toronto Raptors vs  Detroit Pistons
27 Dec -  Utah Jazz vs  Houston Rockets
27 Dec -  Indiana Pacers vs  San Diego Caravels
27 Dec -  Philadelphia 76ers vs  Denver Nuggets
27 Dec -  Sacramento Kings vs  Los Angeles Clippers
28 Dec -  Atlanta Hawks vs  Toronto Raptors
28 Dec -  Phoenix Suns vs  Washington Wizards
28 Dec -  Chicago Bulls vs  Charlotte Hornets
28 Dec -  New York Knicks vs  Orlando Magic
28 Dec -  Houston Rockets vs  New Orleans Pelicans
28 Dec -  Oklahoma City Thunder vs  Minnesota Timberwolves
28 Dec -  Memphis Grizzlies vs  Los Angeles Lakers
28 Dec -  Boston Celtics vs  Golden State Warriors
28 Dec -  Philadelphia 76ers vs  Portland Trailblazers
29 Dec -  Miami Heat vs  Detroit Pistons
29 Dec -  New Orleans Pelicans vs  San Diego Caravels
29 Dec -  Oklahoma City Thunder vs  Denver Nuggets
30 Dec -  Atlanta Hawks vs  Montreal Mastodons
30 Dec -  Miami Heat vs  Washington Wizards
30 Dec -  Phoenix Suns vs  Charlotte Hornets
30 Dec -  Minnesota Timberwolves vs  Orlando Magic
30 Dec -  Toronto Raptors vs  Indiana Pacers
30 Dec -  New York Knicks vs  Milwaukee Bucks
30 Dec -  Golden State Warriors vs  Dallas Mavericks
30 Dec -  Boston Celtics vs  Sacramento Kings
30 Dec -  Memphis Grizzlies vs  Portland Trailblazers
31 Dec -  Detroit Pistons vs  Cleveland Cavaliers
31 Dec -  Phoenix Suns vs  Chicago Bulls
31 Dec -  Dallas Mavericks vs  New Orleans Pelicans
31 Dec -  Golden State Warriors vs  Houston Rockets
31 Dec -  San Diego Caravels vs  Denver Nuggets
31 Dec -  Philadelphia 76ers vs  Utah Jazz
31 Dec -  Boston Celtics vs  Los Angeles Clippers
31 Dec -  Memphis Grizzlies vs  Oklahoma City Thunder
1 Jan -  Minnesota Timberwolves vs  Miami Heat
1 Jan -  Utah Jazz vs  Los Angeles Lakers
1 Jan -  Los Angeles Clippers vs  Portland Trailblazers
2 Jan -  Phoenix Suns vs  New York Knicks
2 Jan -  Oklahoma City Thunder vs  Indiana Pacers
2 Jan -  Milwaukee Bucks vs  Chicago Bulls
2 Jan -  Boston Celtics vs  Denver Nuggets
3 Jan -  Houston Rockets vs  Washington Wizards
3 Jan -  Toronto Raptors vs  Atlanta Hawks
3 Jan -  Orlando Magic vs  Detroit Pistons
3 Jan -  Golden State Warriors vs  Memphis Grizzlies
3 Jan -  Portland Trailblazers vs  Dallas Mavericks
3 Jan -  Los Angeles Lakers vs  Utah Jazz
3 Jan -  Philadelphia 76ers vs  Sacramento Kings
4 Jan -  Charlotte Hornets vs  Boston Celtics
4 Jan -  Orlando Magic vs  Toronto Raptors
4 Jan -  Oklahoma City Thunder vs  Chicago Bulls
4 Jan -  Cleveland Cavaliers vs  Milwaukee Bucks
4 Jan -  Miami Heat vs  New Orleans Pelicans
4 Jan -  Portland Trailblazers vs  San Diego Caravels
4 Jan -  Dallas Mavericks vs  Minnesota Timberwolves
4 Jan -  Indiana Pacers vs  Denver Nuggets
4 Jan -  Philadelphia 76ers vs  Phoenix Suns
5 Jan -  Houston Rockets vs  Cleveland Cavaliers
5 Jan -  Indiana Pacers vs  Golden State Warriors
6 Jan -  Atlanta Hawks vs  Boston Celtics
6 Jan -  Houston Rockets vs  Toronto Raptors
6 Jan -  Orlando Magic vs  Montreal Mastodons
6 Jan -  Washington Wizards vs  New York Knicks
6 Jan -  Oklahoma City Thunder vs  Detroit Pistons
6 Jan -  Chicago Bulls vs  Milwaukee Bucks
6 Jan -  Utah Jazz vs  Memphis Grizzlies
6 Jan -  Portland Trailblazers vs  New Orleans Pelicans
6 Jan -  Minnesota Timberwolves vs  San Diego Caravels
6 Jan -  Dallas Mavericks vs  Denver Nuggets
6 Jan -  Miami Heat vs  Phoenix Suns
6 Jan -  Philadelphia 76ers vs  Los Angeles Lakers
6 Jan -  Los Angeles Clippers vs  Sacramento Kings
7 Jan -  New Orleans Pelicans vs  Atlanta Hawks
7 Jan -  Boston Celtics vs  Washington Wizards
7 Jan -  Charlotte Hornets vs  Orlando Magic
7 Jan -  Utah Jazz vs  Detroit Pistons
7 Jan -  Milwaukee Bucks vs  Cleveland Cavaliers
7 Jan -  Memphis Grizzlies vs  Chicago Bulls
7 Jan -  Minnesota Timberwolves vs  Dallas Mavericks
7 Jan -  San Diego Caravels vs  Phoenix Suns
7 Jan -  Los Angeles Lakers vs  Los Angeles Clippers
8 Jan -  Montreal Mastodons vs  Toronto Raptors
8 Jan -  Oklahoma City Thunder vs  New York Knicks
8 Jan -  Denver Nuggets vs  Houston Rockets
8 Jan -  Indiana Pacers vs  Sacramento Kings
8 Jan -  Miami Heat vs  Portland Trailblazers
9 Jan -  Dallas Mavericks vs  Boston Celtics
9 Jan -  Oklahoma City Thunder vs  Philadelphia 76ers
9 Jan -  Utah Jazz vs  Washington Wizards
9 Jan -  Toronto Raptors vs  Chicago Bulls
9 Jan -  Indiana Pacers vs  Los Angeles Lakers
10 Jan -  Houston Rockets vs  Charlotte Hornets
10 Jan -  Boston Celtics vs  Atlanta Hawks
10 Jan -  New York Knicks vs  Cleveland Cavaliers
10 Jan -  Minnesota Timberwolves vs  Milwaukee Bucks
10 Jan -  Sacramento Kings vs  Memphis Grizzlies
10 Jan -  Detroit Pistons vs  New Orleans Pelicans
10 Jan -  Montreal Mastodons vs  San Diego Caravels
10 Jan -  Phoenix Suns vs  Denver Nuggets
10 Jan -  Orlando Magic vs  Los Angeles Clippers
11 Jan -  Charlotte Hornets vs  Toronto Raptors
11 Jan -  Dallas Mavericks vs  New York Knicks
11 Jan -  Utah Jazz vs  Philadelphia 76ers
11 Jan -  Atlanta Hawks vs  Washington Wizards
11 Jan -  Milwaukee Bucks vs  Indiana Pacers
11 Jan -  Sacramento Kings vs  Houston Rockets
11 Jan -  Chicago Bulls vs  Minnesota Timberwolves
11 Jan -  Miami Heat vs  Golden State Warriors
11 Jan -  Los Angeles Lakers vs  Portland Trailblazers
11 Jan -  Orlando Magic vs  Oklahoma City Thunder
12 Jan -  Detroit Pistons vs  San Diego Caravels
12 Jan -  Los Angeles Clippers vs  Phoenix Suns
12 Jan -  Cleveland Cavaliers vs  Los Angeles Lakers
13 Jan -  Atlanta Hawks vs  New York Knicks
13 Jan -  Boston Celtics vs  Philadelphia 76ers
13 Jan -  Milwaukee Bucks vs  Charlotte Hornets
13 Jan -  Washington Wizards vs  Indiana Pacers
13 Jan -  Montreal Mastodons vs  Memphis Grizzlies
13 Jan -  Sacramento Kings vs  New Orleans Pelicans
13 Jan -  Denver Nuggets vs  Minnesota Timberwolves
13 Jan -  Orlando Magic vs  Portland Trailblazers
13 Jan -  Miami Heat vs  Oklahoma City Thunder
14 Jan -  Washington Wizards vs  Atlanta Hawks
14 Jan -  Charlotte Hornets vs  Detroit Pistons
14 Jan -  Indiana Pacers vs  Chicago Bulls
14 Jan -  Denver Nuggets vs  Milwaukee Bucks
14 Jan -  New Orleans Pelicans vs  Houston Rockets
14 Jan -  Montreal Mastodons vs  Dallas Mavericks
14 Jan -  Memphis Grizzlies vs  San Diego Caravels
14 Jan -  Miami Heat vs  Utah Jazz
14 Jan -  Cleveland Cavaliers vs  Phoenix Suns
14 Jan -  Oklahoma City Thunder vs  Los Angeles Clippers
14 Jan -  Los Angeles Lakers vs  Golden State Warriors
15 Jan -  New York Knicks vs  Toronto Raptors
15 Jan -  Orlando Magic vs  Sacramento Kings
15 Jan -  Cleveland Cavaliers vs  Portland Trailblazers
16 Jan -  Indiana Pacers vs  Montreal Mastodons
16 Jan -  Minnesota Timberwolves vs  New York Knicks
16 Jan -  Philadelphia 76ers vs  Washington Wizards
16 Jan -  New Orleans Pelicans vs  Charlotte Hornets
16 Jan -  Houston Rockets vs  Atlanta Hawks
16 Jan -  Boston Celtics vs  Detroit Pistons
16 Jan -  Denver Nuggets vs  Chicago Bulls
16 Jan -  San Diego Caravels vs  Memphis Grizzlies
16 Jan -  Milwaukee Bucks vs  Dallas Mavericks
16 Jan -  Utah Jazz vs  Los Angeles Clippers
16 Jan -  Miami Heat vs  Los Angeles Lakers
16 Jan -  Oklahoma City Thunder vs  Golden State Warriors
17 Jan -  Washington Wizards vs  Orlando Magic
17 Jan -  Toronto Raptors vs  Utah Jazz
17 Jan -  Phoenix Suns vs  Sacramento Kings
18 Jan -  Minnesota Timberwolves vs  Boston Celtics
18 Jan -  Montreal Mastodons vs  Philadelphia 76ers
18 Jan -  Detroit Pistons vs  Atlanta Hawks
18 Jan -  Orlando Magic vs  Miami Heat
18 Jan -  Charlotte Hornets vs  Indiana Pacers
18 Jan -  New York Knicks vs  Chicago Bulls
18 Jan -  Memphis Grizzlies vs  New Orleans Pelicans
18 Jan -  Dallas Mavericks vs  Houston Rockets
18 Jan -  Milwaukee Bucks vs  San Diego Caravels
18 Jan -  Cleveland Cavaliers vs  Denver Nuggets
18 Jan -  Phoenix Suns vs  Los Angeles Clippers
18 Jan -  Toronto Raptors vs  Portland Trailblazers
19 Jan -  Detroit Pistons vs  New York Knicks
19 Jan -  Los Angeles Lakers vs  Sacramento Kings
20 Jan -  Orlando Magic vs  Charlotte Hornets
20 Jan -  Milwaukee Bucks vs  Atlanta Hawks
20 Jan -  San Diego Caravels vs  Miami Heat
20 Jan -  Houston Rockets vs  Chicago Bulls
20 Jan -  Indiana Pacers vs  Minnesota Timberwolves
20 Jan -  Utah Jazz vs  Denver Nuggets
20 Jan -  Los Angeles Lakers vs  Phoenix Suns
20 Jan -  Dallas Mavericks vs  Los Angeles Clippers
20 Jan -  Cleveland Cavaliers vs  Golden State Warriors
20 Jan -  Toronto Raptors vs  Oklahoma City Thunder
20 Jan -  Montreal Mastodons vs  Boston Celtics
20 Jan -  Memphis Grizzlies vs  Philadelphia 76ers
20 Jan -  New Orleans Pelicans vs  Washington Wizards
21 Jan -  Boston Celtics vs  Montreal Mastodons
21 Jan -  New Orleans Pelicans vs  New York Knicks
21 Jan -  Sacramento Kings vs  Orlando Magic
21 Jan -  Chicago Bulls vs  Indiana Pacers
21 Jan -  Charlotte Hornets vs  Milwaukee Bucks
21 Jan -  Cleveland Cavaliers vs  Utah Jazz
22 Jan -  Memphis Grizzlies vs  Washington Wizards
22 Jan -  Sacramento Kings vs  Miami Heat
22 Jan -  Houston Rockets vs  Detroit Pistons
22 Jan -  Denver Nuggets vs  San Diego Caravels
22 Jan -  Philadelphia 76ers vs  Minnesota Timberwolves
22 Jan -  Oklahoma City Thunder vs  Phoenix Suns
22 Jan -  Golden State Warriors vs  Los Angeles Clippers
22 Jan -  Toronto Raptors vs  Los Angeles Lakers
22 Jan -  Dallas Mavericks vs  Portland Trailblazers
23 Jan -  New Orleans Pelicans vs  Boston Celtics
23 Jan -  Indiana Pacers vs  Atlanta Hawks
23 Jan -  Houston Rockets vs  Milwaukee Bucks
23 Jan -  Toronto Raptors vs  Denver Nuggets
23 Jan -  Montreal Mastodons vs  Utah Jazz
23 Jan -  Los Angeles Clippers vs  Golden State Warriors
24 Jan -  Sacramento Kings vs  Philadelphia 76ers
24 Jan -  Phoenix Suns vs  Orlando Magic
24 Jan -  Memphis Grizzlies vs  Miami Heat
24 Jan -  Indiana Pacers vs  Cleveland Cavaliers
24 Jan -  Charlotte Hornets vs  San Diego Caravels
24 Jan -  Detroit Pistons vs  Minnesota Timberwolves
25 Jan -  Chicago Bulls vs  Toronto Raptors
25 Jan -  Sacramento Kings vs  New York Knicks
25 Jan -  Cleveland Cavaliers vs  Atlanta Hawks
25 Jan -  Milwaukee Bucks vs  Detroit Pistons
25 Jan -  Minnesota Timberwolves vs  Memphis Grizzlies
25 Jan -  San Diego Caravels vs  New Orleans Pelicans
25 Jan -  Charlotte Hornets vs  Houston Rockets
25 Jan -  Oklahoma City Thunder vs  Utah Jazz
25 Jan -  Montreal Mastodons vs  Los Angeles Clippers
25 Jan -  Dallas Mavericks vs  Golden State Warriors
25 Jan -  Denver Nuggets vs  Portland Trailblazers
26 Jan -  Orlando Magic vs  Philadelphia 76ers
26 Jan -  Phoenix Suns vs  Miami Heat
26 Jan -  Dallas Mavericks vs  Oklahoma City Thunder
27 Jan -  Sacramento Kings vs  Boston Celtics
27 Jan -  Orlando Magic vs  New York Knicks
27 Jan -  Miami Heat vs  Charlotte Hornets
27 Jan -  Phoenix Suns vs  Atlanta Hawks
27 Jan -  Memphis Grizzlies vs  Detroit Pistons
27 Jan -  Cleveland Cavaliers vs  Indiana Pacers
27 Jan -  Washington Wizards vs  Chicago Bulls
27 Jan -  Toronto Raptors vs  Milwaukee Bucks
27 Jan -  Utah Jazz vs  New Orleans Pelicans
27 Jan -  Minnesota Timberwolves vs  Houston Rockets
27 Jan -  Los Angeles Clippers vs  Denver Nuggets
27 Jan -  Golden State Warriors vs  Los Angeles Lakers
27 Jan -  Montreal Mastodons vs  Portland Trailblazers
28 Jan -  New York Knicks vs  Philadelphia 76ers
28 Jan -  Charlotte Hornets vs  Washington Wizards
28 Jan -  Atlanta Hawks vs  Chicago Bulls
28 Jan -  New Orleans Pelicans vs  Memphis Grizzlies
28 Jan -  Utah Jazz vs  Dallas Mavericks
28 Jan -  Minnesota Timberwolves vs  San Diego Caravels
28 Jan -  Denver Nuggets vs  Los Angeles Clippers
28 Jan -  Portland Trailblazers vs  Golden State Warriors
28 Jan -  Montreal Mastodons vs  Oklahoma City Thunder
29 Jan -  Sacramento Kings vs  Toronto Raptors
29 Jan -  Philadelphia 76ers vs  Orlando Magic
29 Jan -  Los Angeles Lakers vs  Detroit Pistons
29 Jan -  Phoenix Suns vs  Cleveland Cavaliers
29 Jan -  Boston Celtics vs  Milwaukee Bucks
29 Jan -  Miami Heat vs  Houston Rockets
30 Jan -  Cleveland Cavaliers vs  Charlotte Hornets
30 Jan -  New York Knicks vs  Atlanta Hawks
30 Jan -  Los Angeles Clippers vs  Miami Heat
30 Jan -  Houston Rockets vs  Memphis Grizzlies
30 Jan -  Milwaukee Bucks vs  New Orleans Pelicans
30 Jan -  Boston Celtics vs  Minnesota Timberwolves
30 Jan -  San Diego Caravels vs  Utah Jazz
30 Jan -  Portland Trailblazers vs  Oklahoma City Thunder
31 Jan -  Detroit Pistons vs  Montreal Mastodons
31 Jan -  Los Angeles Lakers vs  New York Knicks
31 Jan -  Phoenix Suns vs  Philadelphia 76ers
31 Jan -  Indiana Pacers vs  Washington Wizards
31 Jan -  Chicago Bulls vs  Dallas Mavericks
31 Jan -  Denver Nuggets vs  Sacramento Kings
1 Feb -  Phoenix Suns vs  Boston Celtics
1 Feb -  Washington Wizards vs  Toronto Raptors
1 Feb -  Atlanta Hawks vs  Charlotte Hornets
1 Feb -  Los Angeles Clippers vs  Orlando Magic
1 Feb -  Minnesota Timberwolves vs  Detroit Pistons
1 Feb -  Montreal Mastodons vs  Cleveland Cavaliers
1 Feb -  Los Angeles Lakers vs  Indiana Pacers
1 Feb -  Dallas Mavericks vs  Memphis Grizzlies
1 Feb -  Chicago Bulls vs  New Orleans Pelicans
1 Feb -  Milwaukee Bucks vs  Houston Rockets
1 Feb -  Denver Nuggets vs  Utah Jazz
1 Feb -  San Diego Caravels vs  Portland Trailblazers
1 Feb -  Golden State Warriors vs  Oklahoma City Thunder
2 Feb -  Cleveland Cavaliers vs  Miami Heat
2 Feb -  San Diego Caravels vs  Golden State Warriors
3 Feb -  Los Angeles Clippers vs  Boston Celtics
3 Feb -  New York Knicks vs  Toronto Raptors
3 Feb -  Detroit Pistons vs  Philadelphia 76ers
3 Feb -  Los Angeles Lakers vs  Charlotte Hornets
3 Feb -  Orlando Magic vs  Atlanta Hawks
3 Feb -  Oklahoma City Thunder vs  Houston Rockets
3 Feb -  Sacramento Kings vs  Utah Jazz
3 Feb -  Minnesota Timberwolves vs  Portland Trailblazers
4 Feb -  Miami Heat vs  Montreal Mastodons
4 Feb -  Atlanta Hawks vs  Washington Wizards
4 Feb -  Boston Celtics vs  Orlando Magic
4 Feb -  Philadelphia 76ers vs  Cleveland Cavaliers
4 Feb -  Detroit Pistons vs  Indiana Pacers
4 Feb -  Memphis Grizzlies vs  Milwaukee Bucks
4 Feb -  Los Angeles Lakers vs  New Orleans Pelicans
4 Feb -  Oklahoma City Thunder vs  Dallas Mavericks
4 Feb -  Portland Trailblazers vs  Denver Nuggets
4 Feb -  Chicago Bulls vs  Phoenix Suns
4 Feb -  Minnesota Timberwolves vs  Golden State Warriors
5 Feb -  Los Angeles Clippers vs  Toronto Raptors
5 Feb -  Houston Rockets vs  New York Knicks
5 Feb -  Utah Jazz vs  Sacramento Kings
6 Feb -  New Orleans Pelicans vs  Montreal Mastodons
6 Feb -  Houston Rockets vs  Philadelphia 76ers
6 Feb -  Orlando Magic vs  Washington Wizards
6 Feb -  Oklahoma City Thunder vs  Charlotte Hornets
6 Feb -  Boston Celtics vs  Miami Heat
6 Feb -  Chicago Bulls vs  Utah Jazz
6 Feb -  Minnesota Timberwolves vs  Phoenix Suns
6 Feb -  Denver Nuggets vs  Golden State Warriors
7 Feb -  Los Angeles Clippers vs  New York Knicks
7 Feb -  Detroit Pistons vs  Atlanta Hawks
7 Feb -  Milwaukee Bucks vs  Cleveland Cavaliers
7 Feb -  Los Angeles Lakers vs  Dallas Mavericks
7 Feb -  Memphis Grizzlies vs  Sacramento Kings
8 Feb -  San Diego Caravels vs  Toronto Raptors
8 Feb -  New York Knicks vs  Montreal Mastodons
8 Feb -  Golden State Warriors vs  Washington Wizards
8 Feb -  Philadelphia 76ers vs  Charlotte Hornets
8 Feb -  Los Angeles Clippers vs  Detroit Pistons
8 Feb -  Portland Trailblazers vs  Indiana Pacers
8 Feb -  Orlando Magic vs  Milwaukee Bucks
8 Feb -  Oklahoma City Thunder vs  New Orleans Pelicans
8 Feb -  Los Angeles Lakers vs  Houston Rockets
8 Feb -  Cleveland Cavaliers vs  Minnesota Timberwolves
8 Feb -  Chicago Bulls vs  Denver Nuggets
8 Feb -  Memphis Grizzlies vs  Phoenix Suns
9 Feb -  Miami Heat vs  Dallas Mavericks
9 Feb -  Chicago Bulls vs  Sacramento Kings
10 Feb -  Portland Trailblazers vs  Boston Celtics
10 Feb -  San Diego Caravels vs  Montreal Mastodons
10 Feb -  Cleveland Cavaliers vs  Washington Wizards
10 Feb -  Toronto Raptors vs  Charlotte Hornets
10 Feb -  Detroit Pistons vs  Orlando Magic
10 Feb -  Golden State Warriors vs  Indiana Pacers
10 Feb -  New York Knicks vs  New Orleans Pelicans
10 Feb -  Utah Jazz vs  Minnesota Timberwolves
10 Feb -  Dallas Mavericks vs  Denver Nuggets
10 Feb -  Sacramento Kings vs  Phoenix Suns
10 Feb -  Memphis Grizzlies vs  Los Angeles Clippers
10 Feb -  Atlanta Hawks vs  Oklahoma City Thunder
11 Feb -  Golden State Warriors vs  Cleveland Cavaliers
11 Feb -  Charlotte Hornets vs  Milwaukee Bucks
11 Feb -  Utah Jazz vs  Houston Rockets
11 Feb -  New Orleans Pelicans vs  Minnesota Timberwolves
11 Feb -  Memphis Grizzlies vs  Los Angeles Lakers
12 Feb -  Orlando Magic vs  Boston Celtics
12 Feb -  Portland Trailblazers vs  Toronto Raptors
12 Feb -  Milwaukee Bucks vs  Montreal Mastodons
12 Feb -  Philadelphia 76ers vs  Washington Wizards
12 Feb -  Detroit Pistons vs  Miami Heat
12 Feb -  San Diego Caravels vs  Indiana Pacers
12 Feb -  New York Knicks vs  Houston Rockets
12 Feb -  Chicago Bulls vs  Los Angeles Clippers
12 Feb -  Atlanta Hawks vs  Sacramento Kings
12 Feb -  Denver Nuggets vs  Oklahoma City Thunder
13 Feb -  Portland Trailblazers vs  Charlotte Hornets
13 Feb -  Washington Wizards vs  New Orleans Pelicans
13 Feb -  New York Knicks vs  Dallas Mavericks
13 Feb -  Toronto Raptors vs  Minnesota Timberwolves
13 Feb -  Utah Jazz vs  Los Angeles Lakers
13 Feb -  Memphis Grizzlies vs  Golden State Warriors
14 Feb -  Orlando Magic vs  Miami Heat
14 Feb -  Montreal Mastodons vs  Detroit Pistons
14 Feb -  San Diego Caravels vs  Cleveland Cavaliers
14 Feb -  Sacramento Kings vs  Chicago Bulls
14 Feb -  Oklahoma City Thunder vs  Milwaukee Bucks
14 Feb -  Houston Rockets vs  Los Angeles Clippers
15 Feb -  Cleveland Cavaliers vs  Boston Celtics
15 Feb -  Toronto Raptors vs  New York Knicks
15 Feb -  San Diego Caravels vs  Philadelphia 76ers
15 Feb -  Montreal Mastodons vs  Charlotte Hornets
15 Feb -  Miami Heat vs  Orlando Magic
15 Feb -  Milwaukee Bucks vs  Indiana Pacers
15 Feb -  Sacramento Kings vs  Memphis Grizzlies
15 Feb -  Portland Trailblazers vs  New Orleans Pelicans
15 Feb -  Washington Wizards vs  Dallas Mavericks
15 Feb -  Oklahoma City Thunder vs  Minnesota Timberwolves
15 Feb -  Phoenix Suns vs  Denver Nuggets
15 Feb -  Atlanta Hawks vs  Los Angeles Lakers
15 Feb -  Los Angeles Clippers vs  Golden State Warriors
16 Feb -  Philadelphia 76ers vs  Chicago Bulls
16 Feb -  Houston Rockets vs  Phoenix Suns
21 Feb -  Minnesota Timberwolves vs  Washington Wizards
21 Feb -  Atlanta Hawks vs  Detroit Pistons
21 Feb -  Orlando Magic vs  Cleveland Cavaliers
21 Feb -  New Orleans Pelicans vs  Indiana Pacers
21 Feb -  Montreal Mastodons vs  Milwaukee Bucks
21 Feb -  Toronto Raptors vs  Memphis Grizzlies
21 Feb -  Los Angeles Clippers vs  Dallas Mavericks
21 Feb -  Oklahoma City Thunder vs  San Diego Caravels
21 Feb -  Charlotte Hornets vs  Denver Nuggets
21 Feb -  Boston Celtics vs  Utah Jazz
21 Feb -  Portland Trailblazers vs  Los Angeles Lakers
21 Feb -  Golden State Warriors vs  Sacramento Kings
22 Feb -  Orlando Magic vs  Montreal Mastodons
22 Feb -  Miami Heat vs  New York Knicks
22 Feb -  Cleveland Cavaliers vs  Philadelphia 76ers
22 Feb -  Oklahoma City Thunder vs  Atlanta Hawks
22 Feb -  Minnesota Timberwolves vs  Chicago Bulls
22 Feb -  San Diego Caravels vs  New Orleans Pelicans
22 Feb -  Los Angeles Clippers vs  Houston Rockets
22 Feb -  Boston Celtics vs  Phoenix Suns
22 Feb -  Charlotte Hornets vs  Portland Trailblazers
23 Feb -  Indiana Pacers vs  Detroit Pistons
23 Feb -  Memphis Grizzlies vs  Dallas Mavericks
23 Feb -  Sacramento Kings vs  Los Angeles Lakers
24 Feb -  Montreal Mastodons vs  New York Knicks
24 Feb -  Oklahoma City Thunder vs  Orlando Magic
24 Feb -  Washington Wizards vs  Cleveland Cavaliers
24 Feb -  Atlanta Hawks vs  Indiana Pacers
24 Feb -  Detroit Pistons vs  Chicago Bulls
24 Feb -  Philadelphia 76ers vs  Milwaukee Bucks
24 Feb -  San Diego Caravels vs  Memphis Grizzlies
24 Feb -  Golden State Warriors vs  Houston Rockets
24 Feb -  Denver Nuggets vs  Minnesota Timberwolves
24 Feb -  Los Angeles Lakers vs  Los Angeles Clippers
24 Feb -  Boston Celtics vs  Portland Trailblazers
25 Feb -  Chicago Bulls vs  Philadelphia 76ers
25 Feb -  New York Knicks vs  Washington Wizards
25 Feb -  Milwaukee Bucks vs  Atlanta Hawks
25 Feb -  Oklahoma City Thunder vs  Miami Heat
25 Feb -  Toronto Raptors vs  Dallas Mavericks
25 Feb -  Golden State Warriors vs  San Diego Caravels
25 Feb -  New Orleans Pelicans vs  Utah Jazz
25 Feb -  Charlotte Hornets vs  Phoenix Suns
26 Feb -  Indiana Pacers vs  Montreal Mastodons
26 Feb -  Houston Rockets vs  Orlando Magic
26 Feb -  Cleveland Cavaliers vs  Detroit Pistons
26 Feb -  Memphis Grizzlies vs  Minnesota Timberwolves
26 Feb -  Boston Celtics vs  Los Angeles Lakers
26 Feb -  New Orleans Pelicans vs  Portland Trailblazers
27 Feb -  Montreal Mastodons vs  Atlanta Hawks
27 Feb -  Toronto Raptors vs  Miami Heat
27 Feb -  Detroit Pistons vs  Cleveland Cavaliers
27 Feb -  Washington Wizards vs  Memphis Grizzlies
27 Feb -  Phoenix Suns vs  Houston Rockets
27 Feb -  Philadelphia 76ers vs  Dallas Mavericks
27 Feb -  New York Knicks vs  San Diego Caravels
27 Feb -  Milwaukee Bucks vs  Denver Nuggets
27 Feb -  Charlotte Hornets vs  Los Angeles Clippers
27 Feb -  Utah Jazz vs  Golden State Warriors
27 Feb -  Portland Trailblazers vs  Sacramento Kings
28 Feb -  Orlando Magic vs  Los Angeles Lakers
28 Feb -  New Orleans Pelicans vs  Oklahoma City Thunder
1 Mar -  Miami Heat vs  Boston Celtics
1 Mar -  Atlanta Hawks vs  Toronto Raptors
1 Mar -  Indiana Pacers vs  Washington Wizards
1 Mar -  Sacramento Kings vs  Cleveland Cavaliers
1 Mar -  New York Knicks vs  Memphis Grizzlies
1 Mar -  Philadelphia 76ers vs  Houston Rockets
1 Mar -  Montreal Mastodons vs  Minnesota Timberwolves
1 Mar -  Detroit Pistons vs  Denver Nuggets
1 Mar -  Charlotte Hornets vs  Utah Jazz
1 Mar -  Milwaukee Bucks vs  Phoenix Suns
1 Mar -  New Orleans Pelicans vs  Los Angeles Clippers
1 Mar -  Orlando Magic vs  Golden State Warriors
1 Mar -  Los Angeles Lakers vs  Portland Trailblazers
2 Mar -  Cleveland Cavaliers vs  Chicago Bulls
2 Mar -  Dallas Mavericks vs  San Diego Caravels
3 Mar -  Indiana Pacers vs  Boston Celtics
3 Mar -  Chicago Bulls vs  New York Knicks
3 Mar -  Washington Wizards vs  Philadelphia 76ers
3 Mar -  Sacramento Kings vs  Atlanta Hawks
3 Mar -  Denver Nuggets vs  Houston Rockets
3 Mar -  Charlotte Hornets vs  Dallas Mavericks
3 Mar -  Los Angeles Clippers vs  Utah Jazz
3 Mar -  Orlando Magic vs  Phoenix Suns
3 Mar -  Los Angeles Lakers vs  Golden State Warriors
3 Mar -  Detroit Pistons vs  Oklahoma City Thunder
4 Mar -  Toronto Raptors vs  Montreal Mastodons
4 Mar -  Atlanta Hawks vs  Miami Heat
4 Mar -  New York Knicks vs  Milwaukee Bucks
4 Mar -  Charlotte Hornets vs  New Orleans Pelicans
4 Mar -  Portland Trailblazers vs  San Diego Caravels
4 Mar -  Orlando Magic vs  Denver Nuggets
4 Mar -  Detroit Pistons vs  Los Angeles Lakers
5 Mar -  Boston Celtics vs  Toronto Raptors
5 Mar -  Indiana Pacers vs  Philadelphia 76ers
5 Mar -  Sacramento Kings vs  Washington Wizards
5 Mar -  Chicago Bulls vs  Cleveland Cavaliers
5 Mar -  Portland Trailblazers vs  Houston Rockets
5 Mar -  Phoenix Suns vs  Dallas Mavericks
5 Mar -  Golden State Warriors vs  Minnesota Timberwolves
5 Mar -  Memphis Grizzlies vs  Los Angeles Clippers
5 Mar -  Utah Jazz vs  Oklahoma City Thunder
6 Mar -  Sacramento Kings vs  Montreal Mastodons
6 Mar -  Miami Heat vs  Charlotte Hornets
6 Mar -  Phoenix Suns vs  New Orleans Pelicans
6 Mar -  Memphis Grizzlies vs  Denver Nuggets
6 Mar -  Orlando Magic vs  Utah Jazz
6 Mar -  San Diego Caravels vs  Los Angeles Lakers
7 Mar -  Boston Celtics vs  Washington Wizards
7 Mar -  Golden State Warriors vs  Atlanta Hawks
7 Mar -  Toronto Raptors vs  Cleveland Cavaliers
7 Mar -  New York Knicks vs  Indiana Pacers
7 Mar -  Montreal Mastodons vs  Chicago Bulls
7 Mar -  Portland Trailblazers vs  Dallas Mavericks
7 Mar -  Houston Rockets vs  Minnesota Timberwolves
7 Mar -  San Diego Caravels vs  Los Angeles Clippers
8 Mar -  Philadelphia 76ers vs  Boston Celtics
8 Mar -  Cleveland Cavaliers vs  Toronto Raptors
8 Mar -  Golden State Warriors vs  Charlotte Hornets
8 Mar -  Washington Wizards vs  Miami Heat
8 Mar -  Chicago Bulls vs  Detroit Pistons
8 Mar -  Sacramento Kings vs  Milwaukee Bucks
8 Mar -  Los Angeles Lakers vs  New Orleans Pelicans
8 Mar -  Indiana Pacers vs  Houston Rockets
8 Mar -  Minnesota Timberwolves vs  Utah Jazz
8 Mar -  Memphis Grizzlies vs  Oklahoma City Thunder
9 Mar -  Denver Nuggets vs  Philadelphia 76ers
9 Mar -  San Diego Caravels vs  Phoenix Suns
9 Mar -  Dallas Mavericks vs  Portland Trailblazers
10 Mar -  Milwaukee Bucks vs  Boston Celtics
10 Mar -  Denver Nuggets vs  Toronto Raptors
10 Mar -  Cleveland Cavaliers vs  Orlando Magic
10 Mar -  Golden State Warriors vs  Miami Heat
10 Mar -  Los Angeles Clippers vs  Chicago Bulls
10 Mar -  Indiana Pacers vs  New Orleans Pelicans
10 Mar -  Los Angeles Lakers vs  San Diego Caravels
10 Mar -  Memphis Grizzlies vs  Sacramento Kings
10 Mar -  Minnesota Timberwolves vs  Oklahoma City Thunder
11 Mar -  Detroit Pistons vs  Washington Wizards
11 Mar -  New York Knicks vs  Charlotte Hornets
11 Mar -  Chicago Bulls vs  Atlanta Hawks
11 Mar -  Golden State Warriors vs  Orlando Magic
11 Mar -  Los Angeles Clippers vs  Milwaukee Bucks
11 Mar -  Dallas Mavericks vs  Utah Jazz
11 Mar -  Minnesota Timberwolves vs  Phoenix Suns
12 Mar -  Denver Nuggets vs  Boston Celtics
12 Mar -  Indiana Pacers vs  Toronto Raptors
12 Mar -  Cleveland Cavaliers vs  Miami Heat
12 Mar -  Charlotte Hornets vs  Detroit Pistons
12 Mar -  Philadelphia 76ers vs  Memphis Grizzlies
12 Mar -  Montreal Mastodons vs  New Orleans Pelicans
12 Mar -  Houston Rockets vs  San Diego Caravels
12 Mar -  Oklahoma City Thunder vs  Los Angeles Lakers
12 Mar -  Dallas Mavericks vs  Sacramento Kings
12 Mar -  Phoenix Suns vs  Portland Trailblazers
13 Mar -  Denver Nuggets vs  New York Knicks
13 Mar -  Orlando Magic vs  Indiana Pacers
13 Mar -  Atlanta Hawks vs  Milwaukee Bucks
13 Mar -  Montreal Mastodons vs  Houston Rockets
13 Mar -  Minnesota Timberwolves vs  Los Angeles Clippers
14 Mar -  Toronto Raptors vs  Philadelphia 76ers
14 Mar -  Washington Wizards vs  Charlotte Hornets
14 Mar -  Utah Jazz vs  Miami Heat
14 Mar -  Portland Trailblazers vs  Chicago Bulls
14 Mar -  Boston Celtics vs  Memphis Grizzlies
14 Mar -  Cleveland Cavaliers vs  Dallas Mavericks
14 Mar -  New Orleans Pelicans vs  San Diego Caravels
14 Mar -  Los Angeles Lakers vs  Sacramento Kings
14 Mar -  Phoenix Suns vs  Oklahoma City Thunder
15 Mar -  Detroit Pistons vs  Toronto Raptors
15 Mar -  Portland Trailblazers vs  Montreal Mastodons
15 Mar -  Atlanta Hawks vs  New York Knicks
15 Mar -  Charlotte Hornets vs  Washington Wizards
15 Mar -  Utah Jazz vs  Orlando Magic
15 Mar -  Denver Nuggets vs  Indiana Pacers
15 Mar -  Chicago Bulls vs  Milwaukee Bucks
15 Mar -  Dallas Mavericks vs  Houston Rockets
15 Mar -  Minnesota Timberwolves vs  Los Angeles Lakers
16 Mar -  Boston Celtics vs  Miami Heat
16 Mar -  Minnesota Timberwolves vs  Golden State Warriors
16 Mar -  Philadelphia 76ers vs  Oklahoma City Thunder
17 Mar -  Milwaukee Bucks vs  Toronto Raptors
17 Mar -  Los Angeles Lakers vs  Montreal Mastodons
17 Mar -  Detroit Pistons vs  New York Knicks
17 Mar -  Dallas Mavericks vs  Washington Wizards
17 Mar -  Utah Jazz vs  Atlanta Hawks
17 Mar -  Boston Celtics vs  Orlando Magic
17 Mar -  Portland Trailblazers vs  Cleveland Cavaliers
17 Mar -  Sacramento Kings vs  Indiana Pacers
17 Mar -  Denver Nuggets vs  Memphis Grizzlies
17 Mar -  San Diego Caravels vs  Houston Rockets
17 Mar -  Golden State Warriors vs  Phoenix Suns
17 Mar -  Philadelphia 76ers vs  Los Angeles Clippers
18 Mar -  Detroit Pistons vs  Charlotte Hornets
18 Mar -  Miami Heat vs  Chicago Bulls
18 Mar -  Portland Trailblazers vs  Milwaukee Bucks
18 Mar -  Denver Nuggets vs  New Orleans Pelicans
18 Mar -  Phoenix Suns vs  San Diego Caravels
19 Mar -  Dallas Mavericks vs  Montreal Mastodons
19 Mar -  Miami Heat vs  New York Knicks
19 Mar -  Chicago Bulls vs  Washington Wizards
19 Mar -  Orlando Magic vs  Atlanta Hawks
19 Mar -  Los Angeles Lakers vs  Cleveland Cavaliers
19 Mar -  Boston Celtics vs  Indiana Pacers
19 Mar -  Utah Jazz vs  Memphis Grizzlies
19 Mar -  Sacramento Kings vs  Minnesota Timberwolves
19 Mar -  Philadelphia 76ers vs  Golden State Warriors
20 Mar -  Los Angeles Lakers vs  Boston Celtics
20 Mar -  Atlanta Hawks vs  Detroit Pistons
20 Mar -  Los Angeles Clippers vs  Houston Rockets
20 Mar -  Milwaukee Bucks vs  Portland Trailblazers
21 Mar -  Toronto Raptors vs  New York Knicks
21 Mar -  Montreal Mastodons vs  Washington Wizards
21 Mar -  Orlando Magic vs  Charlotte Hornets
21 Mar -  Indiana Pacers vs  Memphis Grizzlies
21 Mar -  Los Angeles Clippers vs  New Orleans Pelicans
21 Mar -  Houston Rockets vs  Dallas Mavericks
21 Mar -  Golden State Warriors vs  San Diego Caravels
21 Mar -  Miami Heat vs  Minnesota Timberwolves
21 Mar -  Phoenix Suns vs  Utah Jazz
21 Mar -  Oklahoma City Thunder vs  Sacramento Kings
22 Mar -  Toronto Raptors vs  Boston Celtics
22 Mar -  Atlanta Hawks vs  Philadelphia 76ers
22 Mar -  New York Knicks vs  Orlando Magic
22 Mar -  Miami Heat vs  Detroit Pistons
22 Mar -  Charlotte Hornets vs  Cleveland Cavaliers
22 Mar -  Chicago Bulls vs  Indiana Pacers
22 Mar -  San Diego Caravels vs  Denver Nuggets
22 Mar -  Sacramento Kings vs  Los Angeles Lakers
22 Mar -  Milwaukee Bucks vs  Oklahoma City Thunder
23 Mar -  Minnesota Timberwolves vs  Montreal Mastodons
23 Mar -  Los Angeles Clippers vs  Memphis Grizzlies
23 Mar -  Houston Rockets vs  New Orleans Pelicans
23 Mar -  Golden State Warriors vs  Dallas Mavericks
23 Mar -  Washington Wizards vs  Utah Jazz
23 Mar -  Portland Trailblazers vs  Phoenix Suns
24 Mar -  Minnesota Timberwolves vs  Toronto Raptors
24 Mar -  Memphis Grizzlies vs  New York Knicks
24 Mar -  Orlando Magic vs  Philadelphia 76ers
24 Mar -  Charlotte Hornets vs  Miami Heat
24 Mar -  Boston Celtics vs  Cleveland Cavaliers
24 Mar -  Detroit Pistons vs  Indiana Pacers
24 Mar -  New Orleans Pelicans vs  Chicago Bulls
24 Mar -  Oklahoma City Thunder vs  Denver Nuggets
24 Mar -  Milwaukee Bucks vs  Los Angeles Lakers
24 Mar -  San Diego Caravels vs  Portland Trailblazers
25 Mar -  Dallas Mavericks vs  Atlanta Hawks
25 Mar -  Sacramento Kings vs  Utah Jazz
25 Mar -  Denver Nuggets vs  Phoenix Suns
25 Mar -  Washington Wizards vs  Los Angeles Clippers
26 Mar -  Philadelphia 76ers vs  Indiana Pacers
26 Mar -  Toronto Raptors vs  Milwaukee Bucks
26 Mar -  Charlotte Hornets vs  Memphis Grizzlies
26 Mar -  Cleveland Cavaliers vs  Houston Rockets
26 Mar -  New York Knicks vs  Minnesota Timberwolves
26 Mar -  New Orleans Pelicans vs  Los Angeles Lakers
26 Mar -  Golden State Warriors vs  Sacramento Kings
26 Mar -  Los Angeles Clippers vs  Portland Trailblazers
26 Mar -  San Diego Caravels vs  Oklahoma City Thunder
26 Mar -  Chicago Bulls vs  Boston Celtics
26 Mar -  Atlanta Hawks vs  Orlando Magic
26 Mar -  Montreal Mastodons vs  Detroit Pistons
27 Mar -  Phoenix Suns vs  Montreal Mastodons
27 Mar -  Indiana Pacers vs  Miami Heat
27 Mar -  New Orleans Pelicans vs  Utah Jazz
27 Mar -  Washington Wizards vs  Golden State Warriors
28 Mar -  Atlanta Hawks vs  Charlotte Hornets
28 Mar -  Dallas Mavericks vs  Detroit Pistons
28 Mar -  Orlando Magic vs  Chicago Bulls
28 Mar -  Phoenix Suns vs  Milwaukee Bucks
28 Mar -  Oklahoma City Thunder vs  Memphis Grizzlies
28 Mar -  San Diego Caravels vs  Los Angeles Clippers
28 Mar -  Washington Wizards vs  Sacramento Kings
29 Mar -  Miami Heat vs  Toronto Raptors
29 Mar -  Memphis Grizzlies vs  Montreal Mastodons
29 Mar -  Boston Celtics vs  New York Knicks
29 Mar -  Detroit Pistons vs  Philadelphia 76ers
29 Mar -  Indiana Pacers vs  Atlanta Hawks
29 Mar -  Dallas Mavericks vs  Cleveland Cavaliers
29 Mar -  Oklahoma City Thunder vs  Houston Rockets
29 Mar -  Orlando Magic vs  Minnesota Timberwolves
29 Mar -  Utah Jazz vs  Denver Nuggets
29 Mar -  New Orleans Pelicans vs  Golden State Warriors
29 Mar -  Sacramento Kings vs  Portland Trailblazers
30 Mar -  Phoenix Suns vs  Indiana Pacers
30 Mar -  San Diego Caravels vs  Los Angeles Lakers
31 Mar -  Phoenix Suns vs  Toronto Raptors
31 Mar -  Philadelphia 76ers vs  New York Knicks
31 Mar -  Chicago Bulls vs  Charlotte Hornets
31 Mar -  Montreal Mastodons vs  Atlanta Hawks
31 Mar -  Dallas Mavericks vs  Orlando Magic
31 Mar -  Milwaukee Bucks vs  Detroit Pistons
31 Mar -  Memphis Grizzlies vs  New Orleans Pelicans
31 Mar -  Washington Wizards vs  Houston Rockets
31 Mar -  Minnesota Timberwolves vs  Denver Nuggets
31 Mar -  Utah Jazz vs  Los Angeles Clippers
31 Mar -  Sacramento Kings vs  Golden State Warriors
31 Mar -  Los Angeles Lakers vs  Oklahoma City Thunder
1 Apr -  Miami Heat vs  Cleveland Cavaliers
1 Apr -  Boston Celtics vs  Chicago Bulls
1 Apr -  Indiana Pacers vs  Milwaukee Bucks
1 Apr -  Washington Wizards vs  San Diego Caravels
1 Apr -  Utah Jazz vs  Portland Trailblazers
2 Apr -  New Orleans Pelicans vs  Toronto Raptors
2 Apr -  Miami Heat vs  Montreal Mastodons
2 Apr -  New York Knicks vs  Philadelphia 76ers
2 Apr -  Cleveland Cavaliers vs  Charlotte Hornets
2 Apr -  Phoenix Suns vs  Detroit Pistons
2 Apr -  Atlanta Hawks vs  Memphis Grizzlies
2 Apr -  Denver Nuggets vs  Dallas Mavericks
2 Apr -  Golden State Warriors vs  Minnesota Timberwolves
2 Apr -  Houston Rockets vs  Los Angeles Lakers
2 Apr -  Los Angeles Clippers vs  Sacramento Kings
2 Apr -  Portland Trailblazers vs  Oklahoma City Thunder
4 Apr -  Boston Celtics vs  Toronto Raptors
4 Apr -  Atlanta Hawks vs  Montreal Mastodons
4 Apr -  New York Knicks vs  Washington Wizards
4 Apr -  Minnesota Timberwolves vs  Charlotte Hornets
4 Apr -  Milwaukee Bucks vs  Miami Heat
4 Apr -  New Orleans Pelicans vs  Detroit Pistons
4 Apr -  Philadelphia 76ers vs  Cleveland Cavaliers
4 Apr -  Indiana Pacers vs  Chicago Bulls
4 Apr -  Golden State Warriors vs  Memphis Grizzlies
4 Apr -  Sacramento Kings vs  Dallas Mavericks
4 Apr -  San Diego Caravels vs  Utah Jazz
4 Apr -  Denver Nuggets vs  Los Angeles Clippers
4 Apr -  Houston Rockets vs  Oklahoma City Thunder
5 Apr -  Washington Wizards vs  Boston Celtics
5 Apr -  Cleveland Cavaliers vs  New York Knicks
5 Apr -  Chicago Bulls vs  Philadelphia 76ers
5 Apr -  Minnesota Timberwolves vs  Atlanta Hawks
5 Apr -  Milwaukee Bucks vs  Orlando Magic
5 Apr -  Toronto Raptors vs  Indiana Pacers
5 Apr -  Golden State Warriors vs  New Orleans Pelicans
5 Apr -  Sacramento Kings vs  San Diego Caravels
5 Apr -  Los Angeles Clippers vs  Phoenix Suns
5 Apr -  Houston Rockets vs  Portland Trailblazers
6 Apr -  Charlotte Hornets vs  Montreal Mastodons
6 Apr -  Detroit Pistons vs  Miami Heat
6 Apr -  Los Angeles Lakers vs  Denver Nuggets
7 Apr -  Utah Jazz vs  Minnesota Timberwolves
7 Apr -  Los Angeles Lakers vs  Phoenix Suns
7 Apr -  Sacramento Kings vs  Los Angeles Clippers
7 Apr -  Houston Rockets vs  Golden State Warriors
7 Apr -  Oklahoma City Thunder vs  Portland Trailblazers
7 Apr -  Indiana Pacers vs  New York Knicks
7 Apr -  Boston Celtics vs  Philadelphia 76ers
7 Apr -  Washington Wizards vs  Atlanta Hawks
7 Apr -  Detroit Pistons vs  Orlando Magic
7 Apr -  Milwaukee Bucks vs  Memphis Grizzlies
7 Apr -  Toronto Raptors vs  New Orleans Pelicans
7 Apr -  Dallas Mavericks vs  San Diego Caravels
8 Apr -  Cleveland Cavaliers vs  Montreal Mastodons
8 Apr -  Miami Heat vs  Washington Wizards
8 Apr -  Philadelphia 76ers vs  Chicago Bulls
8 Apr -  New Orleans Pelicans vs  Dallas Mavericks
8 Apr -  Golden State Warriors vs  Denver Nuggets
8 Apr -  Portland Trailblazers vs  Utah Jazz
9 Apr -  New York Knicks vs  Boston Celtics
9 Apr -  Charlotte Hornets vs  Toronto Raptors
9 Apr -  Indiana Pacers vs  Detroit Pistons
9 Apr -  Montreal Mastodons vs  Milwaukee Bucks
9 Apr -  Memphis Grizzlies vs  San Diego Caravels
9 Apr -  Atlanta Hawks vs  Minnesota Timberwolves
9 Apr -  Los Angeles Clippers vs  Los Angeles Lakers
9 Apr -  Houston Rockets vs  Sacramento Kings
9 Apr -  Phoenix Suns vs  Oklahoma City Thunder
10 Apr -  Washington Wizards vs  Philadelphia 76ers
10 Apr -  Atlanta Hawks vs  Orlando Magic
10 Apr -  Toronto Raptors vs  Miami Heat
10 Apr -  New York Knicks vs  Indiana Pacers
10 Apr -  Cleveland Cavaliers vs  New Orleans Pelicans
10 Apr -  Houston Rockets vs  Utah Jazz
10 Apr -  Dallas Mavericks vs  Los Angeles Clippers
10 Apr -  Denver Nuggets vs  Portland Trailblazers
11 Apr -  Montreal Mastodons vs  Chicago Bulls
11 Apr -  Minnesota Timberwolves vs  Memphis Grizzlies
11 Apr -  Oklahoma City Thunder vs  San Diego Caravels
11 Apr -  Golden State Warriors vs  Los Angeles Lakers
11 Apr -  Phoenix Suns vs  Sacramento Kings
12 Apr -  Philadelphia 76ers vs  Montreal Mastodons
12 Apr -  Memphis Grizzlies vs  Charlotte Hornets
12 Apr -  Chicago Bulls vs  Atlanta Hawks
12 Apr -  Toronto Raptors vs  Orlando Magic
12 Apr -  Cleveland Cavaliers vs  Detroit Pistons
12 Apr -  Boston Celtics vs  Indiana Pacers
12 Apr -  Washington Wizards vs  Milwaukee Bucks
12 Apr -  Oklahoma City Thunder vs  New Orleans Pelicans
12 Apr -  Minnesota Timberwolves vs  Houston Rockets
12 Apr -  Denver Nuggets vs  Utah Jazz
12 Apr -  Portland Trailblazers vs  Los Angeles Clippers
12 Apr -  Dallas Mavericks vs  Golden State Warriors
13 Apr -  New York Knicks vs  Cleveland Cavaliers
13 Apr -  Orlando Magic vs  San Diego Caravels
13 Apr -  Dallas Mavericks vs  Phoenix Suns
14 Apr -  Montreal Mastodons vs  Boston Celtics
14 Apr -  Detroit Pistons vs  Toronto Raptors
14 Apr -  Washington Wizards vs  New York Knicks
14 Apr -  Charlotte Hornets vs  Atlanta Hawks
14 Apr -  Philadelphia 76ers vs  Miami Heat
14 Apr -  Minnesota Timberwolves vs  Indiana Pacers
14 Apr -  Milwaukee Bucks vs  Chicago Bulls
14 Apr -  Utah Jazz vs  New Orleans Pelicans
14 Apr -  Portland Trailblazers vs  Los Angeles Lakers
14 Apr -  Phoenix Suns vs  Golden State Warriors
14 Apr -  Los Angeles Clippers vs  Oklahoma City Thunder
15 Apr -  Indiana Pacers vs  Charlotte Hornets
15 Apr -  Philadelphia 76ers vs  Orlando Magic
15 Apr -  Atlanta Hawks vs  Milwaukee Bucks
15 Apr -  Memphis Grizzlies vs  Houston Rockets
15 Apr -  Sacramento Kings vs  Denver Nuggets
15 Apr -  Golden State Warriors vs  Portland Trailblazers
16 Apr -  Boston Celtics vs  Montreal Mastodons
16 Apr -  Cleveland Cavaliers vs  Washington Wizards
16 Apr -  Chicago Bulls vs  Miami Heat
16 Apr -  New York Knicks vs  Detroit Pistons
16 Apr -  Utah Jazz vs  Dallas Mavericks
16 Apr -  San Diego Caravels vs  Minnesota Timberwolves
16 Apr -  Oklahoma City Thunder vs  Los Angeles Clippers
16 Apr -  Phoenix Suns vs  Los Angeles Lakers
16 Apr -  New Orleans Pelicans vs  Sacramento Kings
17 Apr -  Cleveland Cavaliers vs  Boston Celtics
17 Apr -  Indiana Pacers vs  Toronto Raptors
17 Apr -  Charlotte Hornets vs  New York Knicks
17 Apr -  Chicago Bulls vs  Orlando Magic
17 Apr -  Detroit Pistons vs  Milwaukee Bucks
17 Apr -  Utah Jazz vs  San Diego Caravels
17 Apr -  Houston Rockets vs  Denver Nuggets
17 Apr -  New Orleans Pelicans vs  Phoenix Suns
17 Apr -  Portland Trailblazers vs  Golden State Warriors
18 Apr -  Montreal Mastodons vs  Philadelphia 76ers
18 Apr -  Milwaukee Bucks vs  Washington Wizards
18 Apr -  Miami Heat vs  Atlanta Hawks
18 Apr -  Los Angeles Clippers vs  Memphis Grizzlies
18 Apr -  Oklahoma City Thunder vs  Sacramento Kings
19 Apr -  Miami Heat vs  Boston Celtics
19 Apr -  New York Knicks vs  Montreal Mastodons
19 Apr -  Philadelphia 76ers vs  Charlotte Hornets
19 Apr -  Washington Wizards vs  Detroit Pistons
19 Apr -  Atlanta Hawks vs  Cleveland Cavaliers
19 Apr -  Orlando Magic vs  Indiana Pacers
19 Apr -  Toronto Raptors vs  Chicago Bulls
19 Apr -  San Diego Caravels vs  Houston Rockets
19 Apr -  Los Angeles Clippers vs  Dallas Mavericks
19 Apr -  Memphis Grizzlies vs  Minnesota Timberwolves
19 Apr -  Golden State Warriors vs  Utah Jazz
19 Apr -  New Orleans Pelicans vs  Los Angeles Lakers
19 Apr -  Phoenix Suns vs  Portland Trailblazers
19 Apr -  Denver Nuggets vs  Oklahoma City Thunder
"""

def parse_schedule():
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 
        'June': 6, 'July': 7, 'August': 8, 'September': 9, 
        'October': 10, 'November': 11, 'December': 12
    }
    
    games = []
    lines = [line.strip() for line in SCHEDULE_TEXT.split('\n') if line.strip()]
    
    for line in lines:
        match = re.match(r'(\d+)\s+([A-Za-z]+)\s*-\s*(.+?)\s+vs\s+(.+)', line)
        
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            away_team = match.group(3).strip()
            home_team = match.group(4).strip()
            
            month = month_map.get(month_str)
            if month:
                games.append((month, day, away_team, home_team))
            else:
                print(f"Warning: Unknown month '{month_str}' in line: {line}")
        else:
            print(f"Warning: Could not parse line: {line}")
    
    return games

def upload_schedule():
    print(f"Database path: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run create_db.py first to create the database!")
        return
    
    games = parse_schedule()
    
    if not games:
        print("ERROR: No games found in schedule text!")
        return
    
    print(f"Parsed {len(games)} games from schedule")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for game in games:
        try:
            cursor.execute("""
                INSERT INTO schedule (month, day, away_team, home_team)
                VALUES (?, ?, ?, ?)
            """, game)
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM schedule")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT month, day, away_team, home_team FROM schedule ORDER BY month, day LIMIT 5")
    sample = cursor.fetchall()
    
    conn.close()

if __name__ == "__main__":
    upload_schedule()