# Hardwood Hoops

A fantasy basketball league management and statistics website for tracking, managing, and analyzing a basketball simulation league. It's based on it's ProBoards version (https://hardwoodhoops.boards.net/).

**Note:There was use of AI when creating the parsers in order to be able to data scrape the information from ProBoards posts and from NBA Live 08 crypted data, which is mostly the import and update files in scripts.**

## About

Hardwood Hoops is a comprehensive platform for league members to view league statistics, team information, player data, financial details, draft information, and other league-related analytics. The website purpose is to bring an experience similar to what NBA.com offers to a simulation league.

This project was mostly used to revisit my SQL skills while being able to create a database infrastructure from the ground up that we could extract a multitude of statistics from just a few simple stats.

## Tech Stack

### Backend
- **Python 3** - Core language
- **Flask** - Web framework
- **SQLite3** - Database

### Frontend
- **HTML/Jinja2** - Templating
- **CSS** - Styling
- **JavaScript** - Client-side interactivity

### Data
- **JSON** - Game data files

## Features

- **Player Statistics** - Points, rebounds, assists, steals, blocks, turnovers, shooting percentages
- **Team Management** - Rosters, season records, playoff performance, division standings
- **Contract Management** - 5-year contract tracking with salary cap calculations
- **Draft Tracking** - Multi-year draft pick ownership with conditions
- **Awards System** - MVP, DPOY, Rookie of the Year, All-Star selections, All-Defensive, All-Rookie teams
- **Playoff Brackets** - Championship tracking and playoff series results
- **Power Rankings** - Dynamic league rankings
- **Injury Reports** - Player injury tracking
- **Financial Management** - Salary cap compliance monitoring
- **League History** - Champions history and record keeping

## Project Structure

```
HH Reference/
├── app.py                 # Flask application entry point
├── hh_stats.db            # SQLite database
├── routes/                # Flask blueprints
├── database/              # Database utilities
├── scripts/               # Data import scripts
├── stats/                 # Statistical calculations
├── templates/             # HTML templates
├── static/                # CSS, JS, and images
└── game_data/             # JSON game data files
```

## Running the Application
First run create_db.py, then import/upload all the data necessary for your league, and then run create_db.py again to upload the database.
If you sim daily, just import_data, update_ir and create_db.py to update the files for that day.
If you wanna see our page would look, just run app.py.
It's as simple as that, or you can visit BoxToData.com to visit my personal portfolio.

*This was constructed with league data up until December 31st 2025 and has been on pause since*
