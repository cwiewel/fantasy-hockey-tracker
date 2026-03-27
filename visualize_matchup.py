"""
Fantasy Hockey Matchup Visualization Script
Creates graphs showing how matchup scores changed over time
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = "matchup_data.csv"

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def load_data(data_file=DATA_FILE):
    """Load matchup data from CSV"""
    try:
        df = pd.read_csv(data_file)
        # Handle mixed timestamp formats (both "2026-02-03 20:18:39" and "2026-02-03T23:28:38.908313")
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        return df
    except FileNotFoundError:
        print(f"ERROR: Could not find {data_file}")
        print("Please run collect_matchup_data.py first to collect data.")
        sys.exit(1)


def get_matchup_data(df, team_name, week=None):
    """
    Get data for a specific team's matchup
    
    Args:
        df: DataFrame with all matchup data
        team_name: Name of team (or part of name)
        week: Optional week number to filter by (None = current/latest week)
    
    Returns:
        DataFrame filtered to just that matchup
    """
    # If no week specified, use the most recent week in the data
    if week is None:
        week = df['week'].max()
    
    # Filter to the specified week
    week_data = df[df['week'] == week].copy()
    
    if week_data.empty:
        print(f"No data found for week {week}")
        return None
    
    # Find matchups where the team appears (could be team1 or team2)
    matchup_data = week_data[
        week_data['team1_name'].str.contains(team_name, case=False) |
        week_data['team2_name'].str.contains(team_name, case=False)
    ].copy()
    
    if matchup_data.empty:
        print(f"No matchup found for team: {team_name}")
        return None
    
    # Normalize data so our team is always "my_team"
    # This makes graphing easier
    normalized_rows = []
    
    for _, row in matchup_data.iterrows():
        if team_name.lower() in row['team1_name'].lower():
            # Our team is team1
            normalized_rows.append({
                'timestamp': row['timestamp'],
                'week': row['week'],
                'my_team': row['team1_name'],
                'my_current': row['team1_current_score'],
                'my_projected': row['team1_projected_score'],
                'opp_team': row['team2_name'],
                'opp_current': row['team2_current_score'],
                'opp_projected': row['team2_projected_score']
            })
        else:
            # Our team is team2
            normalized_rows.append({
                'timestamp': row['timestamp'],
                'week': row['week'],
                'my_team': row['team2_name'],
                'my_current': row['team2_current_score'],
                'my_projected': row['team2_projected_score'],
                'opp_team': row['team1_name'],
                'opp_current': row['team1_current_score'],
                'opp_projected': row['team1_projected_score']
            })
    
    return pd.DataFrame(normalized_rows).sort_values('timestamp')


def create_matchup_graph(matchup_df, week_start=None, week_end=None):
    """
    Create ESPN-style graph showing score progression
    
    Args:
        matchup_df: DataFrame with matchup data
        week_start: Optional datetime for week start (will be fetched if not provided)
        week_end: Optional datetime for week end (will be fetched if not provided)
    """
    if matchup_df is None or matchup_df.empty:
        return
    
    # Get team names for title
    my_team = matchup_df['my_team'].iloc[0]
    opp_team = matchup_df['opp_team'].iloc[0]
    week = matchup_df['week'].iloc[0]
    
    # Create figure with a nice size
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot current scores
    ax.plot(matchup_df['timestamp'], matchup_df['my_current'], 
            marker='o', linewidth=2, markersize=6,
            label=f'{my_team} (Current)', color='#2E7D32')
    
    ax.plot(matchup_df['timestamp'], matchup_df['opp_current'], 
            marker='o', linewidth=2, markersize=6,
            label=f'{opp_team} (Current)', color='#C62828')
    
    # Plot projected scores (dashed lines)
    ax.plot(matchup_df['timestamp'], matchup_df['my_projected'], 
            linestyle='--', linewidth=2,
            label=f'{my_team} (Projected)', color='#66BB6A', alpha=0.7)
    
    ax.plot(matchup_df['timestamp'], matchup_df['opp_projected'], 
            linestyle='--', linewidth=2,
            label=f'{opp_team} (Projected)', color='#EF5350', alpha=0.7)
    
    # Formatting
    ax.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Points', fontsize=12, fontweight='bold')
    ax.set_title(f'Week {week} Matchup: {my_team} vs {opp_team}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Set y-axis limits
    # Start at 0 (for beginning of week)
    # Max is dynamic based on highest value in data, with 10% padding
    max_current = max(matchup_df['my_current'].max(), matchup_df['opp_current'].max())
    max_projected = max(matchup_df['my_projected'].max(), matchup_df['opp_projected'].max())
    max_value = max(max_current, max_projected)
    
    # Add 10% padding to the top, minimum y-max of 100
    y_max = max(100, max_value * 1.1)
    
    ax.set_ylim(0, y_max)
    
    # Add grid for easier reading
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    
    # Format x-axis to show dates/times nicely
    import matplotlib.dates as mdates
    
    # Set x-axis to show day and time format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d\n%I:%M %p'))
    
    # Rotate labels for readability
    plt.xticks(rotation=45, ha='right')
    fig.autofmt_xdate()
    
    # Set x-axis limits to the official week boundaries
    if week_start and week_end:
        ax.set_xlim([week_start, week_end])
    else:
        # Fallback: use data range with padding
        from datetime import timedelta
        if len(matchup_df) == 1:
            center_time = matchup_df['timestamp'].iloc[0]
            ax.set_xlim([center_time - timedelta(days=3), center_time + timedelta(days=3)])
        else:
            time_range = matchup_df['timestamp'].max() - matchup_df['timestamp'].min()
            padding = max(timedelta(hours=12), time_range * 0.1)
            ax.set_xlim([
                matchup_df['timestamp'].min() - padding,
                matchup_df['timestamp'].max() + padding
            ])
    
    # Legend
    ax.legend(loc='best', framealpha=0.9, fontsize=10)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the figure
    filename = f"matchup_week_{week}_{my_team.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"✓ Graph saved as: {filename}")
    
    # Show the plot
    plt.show()


def print_matchup_summary(matchup_df):
    """Print a text summary of the matchup data"""
    if matchup_df is None or matchup_df.empty:
        return
    
    my_team = matchup_df['my_team'].iloc[0]
    opp_team = matchup_df['opp_team'].iloc[0]
    week = matchup_df['week'].iloc[0]
    
    print("=" * 70)
    print(f"Week {week} Matchup Summary: {my_team} vs {opp_team}")
    print("=" * 70)
    print()
    
    # Latest scores
    latest = matchup_df.iloc[-1]
    print(f"Latest Update: {latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Current Score:   {latest['my_current']:.1f} - {latest['opp_current']:.1f}")
    print(f"  Projected Score: {latest['my_projected']:.1f} - {latest['opp_projected']:.1f}")
    print()
    
    # Data points collected
    print(f"Data Points Collected: {len(matchup_df)}")
    print(f"Time Range: {matchup_df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} to "
          f"{matchup_df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Score changes
    if len(matchup_df) > 1:
        first = matchup_df.iloc[0]
        my_change = latest['my_current'] - first['my_current']
        opp_change = latest['opp_current'] - first['opp_current']
        
        print(f"Score Changes Since First Collection:")
        print(f"  {my_team}: {first['my_current']:.1f} → {latest['my_current']:.1f} "
              f"({my_change:+.1f})")
        print(f"  {opp_team}: {first['opp_current']:.1f} → {latest['opp_current']:.1f} "
              f"({opp_change:+.1f})")
        print()
    
    print("=" * 70)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Visualize fantasy hockey matchup data.")
    parser.add_argument(
        "--input",
        default=DATA_FILE,
        help=f"CSV file to read (default: {DATA_FILE})",
    )
    args = parser.parse_args()

    print("Fantasy Hockey Matchup Visualizer")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    df = load_data(args.input)
    print(f"✓ Loaded {len(df)} data points")
    print()
    
    # Get team name from user
    team_name = input("Enter your team name (or part of it): ").strip()
    
    if not team_name:
        team_name = "The Nose Goes"  # Default
        print(f"Using default: {team_name}")
    
    print()
    
    # Get matchup data
    print("Finding matchup data...")
    matchup_df = get_matchup_data(df, team_name)
    
    if matchup_df is None:
        return
    
    print(f"✓ Found {len(matchup_df)} data points for this matchup")
    print()
    
# Get week boundaries from CSV data
    week = matchup_df['week'].iloc[0]
    
    # Check if week_start and week_end columns exist in data
    if 'week_start' in matchup_df.columns and 'week_end' in matchup_df.columns:
        week_start_str = matchup_df['week_start'].iloc[0]
        week_end_str = matchup_df['week_end'].iloc[0]
        
        if pd.notna(week_start_str) and pd.notna(week_end_str):
            week_start = pd.to_datetime(week_start_str)
            week_end = pd.to_datetime(week_end_str) + pd.Timedelta(hours=23, minutes=59)
            print(f"✓ Week {week} runs from {week_start.strftime('%a %m/%d')} to {week_end.strftime('%a %m/%d')}")
        else:
            print("⚠ Week dates not available in data, using data-based boundaries")
            week_start = None
            week_end = None
    else:
        print("⚠ Week dates not in CSV (old data format), using data-based boundaries")
        week_start = None
        week_end = None
    
    print()    
    
    # Print summary
    print_matchup_summary(matchup_df)
    print()
    
    # Create graph
    print("Creating graph...")
    create_matchup_graph(matchup_df, week_start, week_end)
    print()
    
    print("Done!")


if __name__ == "__main__":
    main()