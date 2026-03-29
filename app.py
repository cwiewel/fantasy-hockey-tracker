"""
Fantasy Hockey Matchup Tracker - Streamlit Web App
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_URL = "https://raw.githubusercontent.com/cwiewel/fantasy-hockey-tracker/main/matchup_data.csv"

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes, then re-fetch
def load_data():
    """Load matchup data directly from GitHub."""
    import urllib.request
    import ssl
    import io
    # Use certifi certificates; fall back to unverified if unavailable
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    with urllib.request.urlopen(DATA_URL, context=ctx) as response:
        data = response.read().decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    # Timestamps from GitHub Actions are UTC; convert to EST for display.
    # Early rows collected locally are already in EST — those predate GitHub Actions
    # and are week 18/19 data. Week 22+ is all UTC from Actions.
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    utc_mask = df['week'] >= 22
    df.loc[utc_mask, 'timestamp'] = (
        df.loc[utc_mask, 'timestamp']
        .dt.tz_localize('UTC')
        .dt.tz_convert('America/New_York')
        .dt.tz_localize(None)
    )
    return df


def get_all_teams(df, week):
    """Get sorted list of all team names for the given week."""
    week_data = df[df['week'] == week]
    teams = set(week_data['team1_name'].tolist() + week_data['team2_name'].tolist())
    return sorted(teams)


def get_matchup_data(df, team_name, week):
    """Get normalized matchup data for a specific team and week."""
    week_data = df[df['week'] == week].copy()

    matchup_data = week_data[
        week_data['team1_name'].str.contains(team_name, case=False, regex=False) |
        week_data['team2_name'].str.contains(team_name, case=False, regex=False)
    ].copy()

    if matchup_data.empty:
        return None

    normalized_rows = []
    for _, row in matchup_data.iterrows():
        if team_name.lower() in row['team1_name'].lower():
            normalized_rows.append({
                'timestamp': row['timestamp'],
                'week': row['week'],
                'my_team': row['team1_name'],
                'my_current': row['team1_current_score'],
                'my_projected': row['team1_projected_score'],
                'opp_team': row['team2_name'],
                'opp_current': row['team2_current_score'],
                'opp_projected': row['team2_projected_score'],
            })
        else:
            normalized_rows.append({
                'timestamp': row['timestamp'],
                'week': row['week'],
                'my_team': row['team2_name'],
                'my_current': row['team2_current_score'],
                'my_projected': row['team2_projected_score'],
                'opp_team': row['team1_name'],
                'opp_current': row['team1_current_score'],
                'opp_projected': row['team1_projected_score'],
            })

    return pd.DataFrame(normalized_rows).sort_values('timestamp')


# ============================================================================
# GRAPH
# ============================================================================

def create_matchup_graph(matchup_df, week_start=None, week_end=None):
    """Create ESPN-style score progression graph."""
    my_team = matchup_df['my_team'].iloc[0]
    opp_team = matchup_df['opp_team'].iloc[0]
    week = matchup_df['week'].iloc[0]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(matchup_df['timestamp'], matchup_df['my_current'],
            marker='o', linewidth=2, markersize=5,
            label=f'{my_team} (Current)', color='#2E7D32')

    ax.plot(matchup_df['timestamp'], matchup_df['opp_current'],
            marker='o', linewidth=2, markersize=5,
            label=f'{opp_team} (Current)', color='#C62828')

    ax.plot(matchup_df['timestamp'], matchup_df['my_projected'],
            linestyle='--', linewidth=2,
            label=f'{my_team} (Projected)', color='#66BB6A', alpha=0.7)

    ax.plot(matchup_df['timestamp'], matchup_df['opp_projected'],
            linestyle='--', linewidth=2,
            label=f'{opp_team} (Projected)', color='#EF5350', alpha=0.7)

    ax.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax.set_ylabel('Points', fontsize=11, fontweight='bold')
    ax.set_title(f'Week {week}: {my_team} vs {opp_team}', fontsize=13, fontweight='bold', pad=15)

    max_value = max(
        matchup_df['my_current'].max(), matchup_df['opp_current'].max(),
        matchup_df['my_projected'].max(), matchup_df['opp_projected'].max()
    )
    ax.set_ylim(0, max(100, max_value * 1.1))

    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d\n%I:%M %p'))
    fig.autofmt_xdate()

    if week_start and week_end:
        ax.set_xlim([week_start, week_end])
    else:
        if len(matchup_df) == 1:
            center = matchup_df['timestamp'].iloc[0]
            ax.set_xlim([center - timedelta(days=3), center + timedelta(days=3)])
        else:
            time_range = matchup_df['timestamp'].max() - matchup_df['timestamp'].min()
            padding = max(timedelta(hours=12), time_range * 0.1)
            ax.set_xlim([
                matchup_df['timestamp'].min() - padding,
                matchup_df['timestamp'].max() + padding
            ])

    ax.legend(loc='best', framealpha=0.9, fontsize=10)
    plt.tight_layout()
    return fig


# ============================================================================
# APP LAYOUT
# ============================================================================

st.set_page_config(page_title="Fantasy Hockey Tracker", page_icon="🏒", layout="wide")

st.title("🏒 Fantasy Hockey Matchup Tracker")
st.caption("Score progression throughout the week — updated every 30 minutes during games.")

# Load data
with st.spinner("Loading data..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.stop()

# Week selector
available_weeks = sorted(df['week'].unique(), reverse=True)
selected_week = st.selectbox(
    "Week",
    options=available_weeks,
    format_func=lambda w: f"Week {w}"
)

# Team selector
teams = get_all_teams(df, selected_week)
selected_team = st.selectbox("Select a team", options=teams)

# Get week boundaries
week_data = df[df['week'] == selected_week]
week_start = None
week_end = None
if 'week_start' in week_data.columns and 'week_end' in week_data.columns:
    ws = week_data['week_start'].iloc[0]
    we = week_data['week_end'].iloc[0]
    if pd.notna(ws) and pd.notna(we):
        week_start = pd.to_datetime(ws)
        week_end = pd.to_datetime(we) + pd.Timedelta(hours=23, minutes=59)

# Get matchup data and render
matchup_df = get_matchup_data(df, selected_team, selected_week)

if matchup_df is None or matchup_df.empty:
    st.warning("No data found for this team/week.")
else:
    latest = matchup_df.iloc[-1]
    my_team = matchup_df['my_team'].iloc[0]
    opp_team = matchup_df['opp_team'].iloc[0]

    # Score summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{my_team}", f"{latest['my_current']:.1f}", "Current")
    col2.metric(f"{opp_team}", f"{latest['opp_current']:.1f}", "Current")
    col3.metric(f"{my_team}", f"{latest['my_projected']:.1f}", "Projected")
    col4.metric(f"{opp_team}", f"{latest['opp_projected']:.1f}", "Projected")

    st.divider()

    # Graph
    fig = create_matchup_graph(matchup_df, week_start, week_end)
    st.pyplot(fig)
    plt.close(fig)

    # Data freshness
    last_update = matchup_df['timestamp'].max()
    st.caption(f"Last data point: {last_update.strftime('%a %b %d, %I:%M %p')} · {len(matchup_df)} data points collected")
