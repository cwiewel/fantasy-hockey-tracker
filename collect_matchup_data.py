"""
Fantasy Hockey Matchup Data Collection Script
Collects current and projected scores for ALL matchups in the league
"""

from yfpy.query import YahooFantasySportsQuery
from pathlib import Path
from datetime import datetime
import csv
import os

# Load .env file automatically if present (local dev + GitHub Actions)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(os.path.dirname(os.path.abspath(__file__))) / '.env')
except ImportError:
    pass

# ============================================================================
# CONFIGURATION
# ============================================================================

# Yahoo API credentials - loaded from .env file
# Copy .env.template to .env and fill in your credentials
CLIENT_ID = os.getenv('YAHOO_CLIENT_ID') or os.getenv('YAHOO_CONSUMER_KEY')
CLIENT_SECRET = os.getenv('YAHOO_CLIENT_SECRET') or os.getenv('YAHOO_CONSUMER_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError(
        "Yahoo API credentials not found. "
        "Copy .env.template to .env and set YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET."
    )

# League settings
LEAGUE_ID = "30102"
GAME_CODE = "nhl"
GAME_ID = 465

# Data file location — can be overridden with DATA_FILE env var on remote servers
DATA_FILE = os.getenv('DATA_FILE', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matchup_data.csv'))

# ============================================================================
# MAIN SCRIPT
# ============================================================================

def get_all_matchups_data(yahoo_query, current_week):
    """
    Fetch matchup data for ALL matchups in the league
    
    Returns:
        tuple: (list of dicts with matchup data, week_start, week_end)
    """
    # Get scoreboard for current week
    scoreboard = yahoo_query.get_league_scoreboard_by_week(current_week)
    
    # Get week start/end dates from the first matchup
    # All matchups have the same week dates
    week_start = None
    week_end = None
    
    if scoreboard.matchups and len(scoreboard.matchups) > 0:
        first_matchup = scoreboard.matchups[0]
        week_start = getattr(first_matchup, 'week_start', None)
        week_end = getattr(first_matchup, 'week_end', None)
    
    all_matchups = []
    
    # Process each matchup
    for matchup in scoreboard.matchups:
        team1 = matchup.teams[0]
        team2 = matchup.teams[1]

        # Get live projected points (real-time updates during games)
        team1_projected = float(team1.team_projected_points.total)  # default
        team2_projected = float(team2.team_projected_points.total)  # default
        
        # Try to get live projections from internal data structure
        if hasattr(team1, '_extracted_data'):
            live_proj = team1._extracted_data.get('team_live_projected_points')
            if live_proj and 'total' in live_proj:
                team1_projected = float(live_proj['total'])
        
        if hasattr(team2, '_extracted_data'):
            live_proj = team2._extracted_data.get('team_live_projected_points')
            if live_proj and 'total' in live_proj:
                team2_projected = float(live_proj['total'])
        
        matchup_data = {
            'timestamp': datetime.now().isoformat(),
            'week': current_week,
            'week_start': str(week_start) if week_start else None,
            'week_end': str(week_end) if week_end else None,
            'team1_name': str(team1.name).replace("b'", "").replace("'", ""),
            'team1_current_score': float(team1.team_points.total),
            'team1_projected_score': team1_projected,
            'team2_name': str(team2.name).replace("b'", "").replace("'", ""),
            'team2_current_score': float(team2.team_points.total),
            'team2_projected_score': team2_projected
        }   
        
        all_matchups.append(matchup_data)
    
    return all_matchups, week_start, week_end


def save_to_csv(matchups_data):
    """
    Save all matchup data to CSV file
    Creates file with headers if it doesn't exist
    Appends data if it does exist
    """
    # Define CSV columns
    fieldnames = [
        'timestamp',
        'week',
        'week_start',
        'week_end',
        'team1_name',
        'team1_current_score',
        'team1_projected_score',
        'team2_name',
        'team2_current_score',
        'team2_projected_score'
    ]
    
    # Check if file exists
    file_exists = os.path.isfile(DATA_FILE)
    
    # Open file in append mode
    with open(DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if this is a new file
        if not file_exists:
            writer.writeheader()
            print(f"Created new data file: {DATA_FILE}")
        
        # Write all matchup data
        for matchup in matchups_data:
            writer.writerow(matchup)
        
        print(f"Saved {len(matchups_data)} matchups to {DATA_FILE}")


def main():
    """
    Main function to collect and save matchup data
    """
    print("=" * 60)
    print("Fantasy Hockey League Matchup Data Collection")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize Yahoo Fantasy query
    print("Connecting to Yahoo Fantasy API...")
    yahoo_query = YahooFantasySportsQuery(
        league_id=LEAGUE_ID,
        game_code=GAME_CODE,
        game_id=GAME_ID,
        yahoo_consumer_key=CLIENT_ID,
        yahoo_consumer_secret=CLIENT_SECRET,
        env_file_location=Path(os.path.dirname(os.path.abspath(__file__))),
        save_token_data_to_env_file=True,  # Save tokens for reuse
        browser_callback=True
    )
    print("✓ Connected!")
    print()
    
    # Get current week
    league_info = yahoo_query.get_league_info()
    current_week = league_info.current_week
    print(f"Current Week: {current_week}")
    print()
    
    # Fetch all matchup data
    print("Fetching matchup data for all teams...")
    matchups_data, week_start, week_end = get_all_matchups_data(yahoo_query, current_week)
    
    if week_start and week_end:
        print(f"Week {current_week} runs from {week_start} to {week_end}")
    
    print(f"✓ Retrieved {len(matchups_data)} matchups!")
    print()
    
    # Display the data
    print("-" * 60)
    print("Current Matchups:")
    print("-" * 60)
    for matchup in matchups_data:
        print(f"{matchup['team1_name']} vs {matchup['team2_name']}")
        print(f"  Current:   {matchup['team1_current_score']} - {matchup['team2_current_score']}")
        print(f"  Projected: {matchup['team1_projected_score']} - {matchup['team2_projected_score']}")
        print()
    print("-" * 60)
    print()
    
    # Save to CSV
    print("Saving data...")
    save_to_csv(matchups_data)
    print()
    
    print("=" * 60)
    print("✓ Data collection complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()