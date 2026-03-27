from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
import os

# Yahoo API credentials - loaded from .env file
CLIENT_ID = os.getenv('YAHOO_CLIENT_ID') or os.getenv('YAHOO_CONSUMER_KEY')
CLIENT_SECRET = os.getenv('YAHOO_CLIENT_SECRET') or os.getenv('YAHOO_CONSUMER_SECRET')

# Initialize query
yahoo_query = YahooFantasySportsQuery(
    league_id="30102",
    game_code="nhl",
    game_id=465,
    yahoo_consumer_key=CLIENT_ID,
    yahoo_consumer_secret=CLIENT_SECRET,
    env_file_location=Path("."),
    browser_callback=True
)

# Get league info to find current week
league_info = yahoo_query.get_league_info()
current_week = league_info.current_week

print(f"Current Week: {current_week}")

# Get current week's scoreboard (all matchups)
scoreboard = yahoo_query.get_league_scoreboard_by_week(current_week)
print(f"\n📊 Week {scoreboard.week} Matchups:")

for matchup in scoreboard.matchups:
    team1 = matchup.teams[0]
    team2 = matchup.teams[1]
    
    print(f"\n{team1.name} vs {team2.name}")
    print(f"  Current: {team1.team_points.total} - {team2.team_points.total}")
    print(f"  Projected: {team1.team_projected_points.total} - {team2.team_projected_points.total}")