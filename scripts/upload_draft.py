import sqlite3
import re
import os

DB_NAME = "hh_stats.db"

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if os.path.exists(os.path.join(script_dir, DB_NAME)):
    DB_PATH = os.path.join(script_dir, DB_NAME)
elif os.path.exists(os.path.join(project_root, DB_NAME)):
    DB_PATH = os.path.join(project_root, DB_NAME)
else:
    DB_PATH = DB_NAME

NAME_FIXES = {
    "Walter Clayton Jr": "Walter Clayton",
}

DRAFTS = {
    2024: """
Round 1

 1. Chicago Bulls - Reed Sheppard
 2. Utah Jazz - Zaccharie Risacher
 3. Memphis Grizzlies - Alex Sarr
 4. LA Clippers (via HOU) - Stephon Castle
 5. Brooklyn Nets - Bub Carrington
 6. Milwaukee Bucks (via WAS) - Rob Dillingham
 7. Portland Trail Blazers - Matas Buzelis
 8. Brooklyn Nets (via ATL) - Zach Edey
 9. Brooklyn Nets (via TOR) - Ron Holland
 10. Orlando Magic - Donovan Clingan
 11. Oklahoma City Thunder (via DET) - Cody Williams
 12. Detroit Pistons (via SAC) - Tidjane Salaun
 13. Chicago Bulls (via LAL) - Kel'el Ware
 14. Milwaukee Bucks (via GSW) - Nikola Topic
 15. Utah Jazz (via IND) - Devin Carter
 16. New Orleans Pelicans (via MIA) - Kyshawn George
 17. Atlanta Hawks (via MIL) - Dalton Knecht
 18. Charlotte Hornets - Tristan Da Silva
 19. Houston Rockets (via MIN) - Jaylon Tyson
 20. Dallas Mavericks - Isaiah Collier
 21. Detroit Pistons (via DEN) - Kyle Filipowski
 22. Washington Wizards (via PHX) - Tyler Smith
 23. Utah Jazz (via SAS) - Jared McCain
 24. New York Knicks - Johnny Furphy
 25. Toronto Raptors (via OKC) - DaRon Holmes
 26. Philadelphia 76ers - Bronny James
 27. Cleveland Cavaliers (via BOS) - Ryan Dunn
 28. LA Lakers (via NOP) - Terrence Shannon
 29. LA Clippers - Yves Missi
 30. New York Knicks (via CLE) - Pacome Dadiet

Round 2

 31. Brooklyn Nets - Bobi Klintman
 32. Washington Wizards - JaKobe Walter
 33. Utah Jazz - AJ Johnson
 34. Chicago Bulls - Nikola Djurisic
 35. Washington Wizards (via HOU) - Jonathan Mogbo
 36. Portland Trail Blazers - Oso Ighodaro
 37. New York Knicks (via ATL) - Tyler Kolek
 38. Memphis Grizzlies - Baylor Scheierman
 39. Toronto Raptors - Jamal Shead
 40. Orlando Magic - Dillon Jones
 41. Detroit Pistons - Justin Edwards
 42. Sacramento Kings - Ajay Mitchell
 43. LA Lakers - Melvin Ajinca
 44. Portland Trail Blazers (via IND) - Ulrich Chomche
 45. Golden State Warriors - Juan Nunez
 46. Washington Wizards (via MIA) - Jaylen Wells
 47. LA Clippers (via MIL) - Adem Bona
 48. Charlotte Hornets - Pelle Larsson
 49. Atlanta Hawks (via MIN) - Tristen Newton
 50. Dallas Mavericks - Cam Christie
 51. Denver Nuggets - Trey Alexander
 52. Memphis Grizzlies (via PHX) - Antonio Reeves
 53. Milwaukee Bucks (via SAS) - Harrison Ingram
 54. New York Knicks - KJ Simpson
 55. New York Knicks (via OKC) - Quinten Post
 56. Philadelphia 76ers - Anton Watson
 57. New Orleans Pelicans (via BOS) - Jalen Bridges
 58. Detroit Pistons (via NOP) - Trentyn Flowers
 59. LA Clippers - Kevin McCullar Jr
 60. Utah Jazz (via CLE) - Enrique Freeman
""",

    2025: """
    
    Round 1

 1. Phoenix Suns - Cooper Flagg
 2. Utah Jazz - Dylan Harper
 3. Milwaukee Bucks - VJ Edgecombe
 4. Milwaukee Bucks (via CHI) - Ace Bailey
 5. Brooklyn Nets - Kon Knueppel
 6. Phoenix Suns (via DET) - Tre Johnson
 7. Chicago Bulls (via WAS) - Kasparas Jakucionis
 8. Miami Heat - Carter Bryant
 9. Portland Trail Blazers - Cedric Coward
 10. LA Lakers (via LAC) - Khaman Maluach
 11. Charlotte Hornets - Jeremiah Fears
 12. Atlanta Hawks (via SAS) - Noa Essengue
 13. Golden State Warriors - Collin Murray Boyles
 14. Sacramento Kings - Asa Newell
 15. Orlando Magic - Derik Queen (traded to BOS)
 16. Toronto Raptors - Thomas Sorber
 17. Memphis Grizzlies - Egor Demin
 18. New Orleans Pelicans (via PHI) - Yang Hansen (traded to MIN)
 19. Indiana Pacers - Walter Clayton Jr
 20. Portland Trail Blazers (via MIN) - Danny Wolf
 21. Milwaukee Bucks (via DAL) - Nique Clifford 
 22. Atlanta Hawks - Jase Richardson
 23. Portland Trail Blazers (via NOP) - Ryan Kalkbrenner
 24. LA Clippers (via BOS) - Nolan Traore
 25. Houston Rockets - Adou Thiero
 26. Utah Jazz (via CLE) - Liam McNeeley
 27. Washington Wizards (via OKC) - Joan Beringer
 28. Denver Nuggets - Noah Penda
 29. Memphis Grizzlies (via LAL) - Will Riley
 30. Miami Heat (via NYK) - Drake Powell


Round 2

 31. Brooklyn Nets - Rasheer Fleming
 32. Chicago Bulls (via DET) - Hugo González
 33. Utah Jazz - Ben Saraf
 34. Washington Wizards - Bogoljub Marković
 35. Washington Wizards (via CHI) - Maxime Raynaud
 36. Atlanta Hawks (via MIA) - Yanic Konan Niederhauser
 37. Houston Rockets (via LAC) - Tyrese Proctor
 38. Portland Trail Blazers - Micah Peavy
 39. Charlotte Hornets - Sion James
 40. Washington Wizards (via MIL) - Koby Brea
 41. Orlando Magic - Johni Broome
 42. Washington Wizards (via SAS) - Chaz Lanier
 43. Utah Jazz (via TOR) - Kam Jones
 44. Sacramento Kings - Brooks Barnhizer
 45. Memphis Grizzlies (via GSW) - Rocco Zikarsky
 46. Memphis Grizzlies - Javon Small
 47. Philadelphia 76ers - Eric Dixon
 48. Houston Rockets (via IND) - Alex Toohey
 49. Houston Rockets (via PHX) - Brice Williams
 50. Chicago Bulls (via ATL) - Mohamed Diawara
 51. New York Knicks (via DAL) - Ryan Nembhard
 52. Golden State Warriors (via MIN) - Alijah Martin
 53. New Orleans Pelicans - Payton Sandfort
 54. New York Knicks (via BOS) - Will Richard
 55. Houston Rockets - John Tonje
 56. Utah Jazz (via CLE) - Jamir Watkins
 57. Utah Jazz (via DEN) - Amari Williams
 58. Washington Wizards (via OKC) - Dink Pate
 59. LA Lakers - Lachlan Olbrich
 60. Miami Heat (via NYK) - Jahmai Mashack (traded to OKC)
    
"""
}

def clean_data(raw_name):
    name = re.sub(r'\s*\(traded.*?\)', '', raw_name).strip()
    name = NAME_FIXES.get(name, name)
    return name

def parse_draft_text(text):
    picks = []
    pattern = re.compile(r'^\s*(\d+)\.\s*([^-]+)\s*-\s+(.+)$', re.MULTILINE)

    for match in pattern.finditer(text):
        pick_num = int(match.group(1))
        raw_name = match.group(3)
        
        name = clean_data(raw_name)
        picks.append((pick_num, name))
    
    return picks

def save_draft_data(year, picks):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated = 0
    created = 0

    print(f"\nProcessing {year} Draft Data...")

    for pick, name in picks:
        cursor.execute("SELECT player_id FROM players WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            cursor.execute("""
                UPDATE players 
                SET draft_year = ?, draft_pick = ? 
                WHERE name = ?
            """, (year, pick, name))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO players (name, draft_year, draft_pick)
                VALUES (?, ?, ?)
            """, (name, year, pick))
            created += 1
            print(f"  [NEW] Created Player: #{pick} {name}")

    conn.commit()
    conn.close()

    print(f"  -> Finished {year}: {updated} Updated, {created} Created.")
    return updated, created

if __name__ == "__main__":
    print(f"Starting Draft Import for DB: {DB_PATH}")
    
    total_updated = 0
    total_created = 0

    for year, text in DRAFTS.items():
        if not text.strip() or "PASTE" in text:
            print(f"\nSkipping {year} (No data provided)")
            continue
            
        picks = parse_draft_text(text)
        if picks:
            up, cr = save_draft_data(year, picks)
            total_updated += up
            total_created += cr
        else:
            print(f"\nWarning: Could not parse any picks for {year}")

    print(f"Total Profiles Updated: {total_updated}")
    print(f"Total New Profiles Created: {total_created}")