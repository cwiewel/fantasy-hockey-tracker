"""
Fantasy Hockey Matchup Tracker - Streamlit Web App
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

def get_all_matchup_pairs(df, week):
    """Get list of (team1, team2) pairs for all matchups in a given week."""
    week_data = df[df['week'] == week]
    pairs = week_data[['team1_name', 'team2_name']].drop_duplicates()
    return [(row['team1_name'], row['team2_name']) for _, row in pairs.iterrows()]


def create_matchup_graph(matchup_df, week_start=None, week_end=None, compact=False):
    """Create interactive Plotly score progression graph.

    compact=True produces a smaller chart for the dashboard grid.
    """
    my_team = matchup_df['my_team'].iloc[0]
    opp_team = matchup_df['opp_team'].iloc[0]
    week = matchup_df['week'].iloc[0]

    hover_fmt = '%{x|%a %b %d, %I:%M %p}<br>Score: %{y:.1f}<extra></extra>'

    fig = go.Figure()

    # Current scores — solid lines
    fig.add_trace(go.Scatter(
        x=matchup_df['timestamp'], y=matchup_df['my_current'],
        mode='lines+markers',
        name=f'{my_team}',
        line=dict(color='#2E7D32', width=3 if not compact else 2),
        marker=dict(size=7 if not compact else 4),
        hovertemplate=f'<b>{my_team}</b><br>{hover_fmt}',
    ))
    fig.add_trace(go.Scatter(
        x=matchup_df['timestamp'], y=matchup_df['opp_current'],
        mode='lines+markers',
        name=f'{opp_team}',
        line=dict(color='#C62828', width=3 if not compact else 2),
        marker=dict(size=7 if not compact else 4),
        hovertemplate=f'<b>{opp_team}</b><br>{hover_fmt}',
    ))

    # Projected scores — dashed lines
    fig.add_trace(go.Scatter(
        x=matchup_df['timestamp'], y=matchup_df['my_projected'],
        mode='lines',
        name=f'{my_team} (Projected)',
        line=dict(color='#66BB6A', width=2 if not compact else 1.5, dash='dash'),
        opacity=0.7,
        hovertemplate=f'<b>{my_team} Projected</b><br>{hover_fmt}',
    ))
    fig.add_trace(go.Scatter(
        x=matchup_df['timestamp'], y=matchup_df['opp_projected'],
        mode='lines',
        name=f'{opp_team} (Projected)',
        line=dict(color='#EF5350', width=2 if not compact else 1.5, dash='dash'),
        opacity=0.7,
        hovertemplate=f'<b>{opp_team} Projected</b><br>{hover_fmt}',
    ))

    # X-axis range
    if week_start and week_end:
        x_range = [week_start, week_end]
    elif len(matchup_df) == 1:
        center = matchup_df['timestamp'].iloc[0]
        x_range = [center - timedelta(days=3), center + timedelta(days=3)]
    else:
        time_range = matchup_df['timestamp'].max() - matchup_df['timestamp'].min()
        padding = max(timedelta(hours=12), time_range * 0.1)
        x_range = [
            matchup_df['timestamp'].min() - padding,
            matchup_df['timestamp'].max() + padding,
        ]

    max_value = max(
        matchup_df['my_current'].max(), matchup_df['opp_current'].max(),
        matchup_df['my_projected'].max(), matchup_df['opp_projected'].max()
    )

    fig.update_layout(
        title=dict(text=f'Week {week}: {my_team} vs {opp_team}', font=dict(size=18 if not compact else 13)),
        xaxis=dict(
            title='Time' if not compact else None,
            range=x_range,
            tickformat='%a %m/%d\n%I %p' if not compact else '%a %m/%d',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.08)',
        ),
        yaxis=dict(
            title='Points' if not compact else None,
            range=[0, max(100, max_value * 1.1)],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.08)',
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        showlegend=not compact,
        hovermode='x unified',
        plot_bgcolor='white',
        height=500 if not compact else 300,
        margin=dict(l=40, r=20, t=50, b=30) if compact else None,
    )

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

# Week selector (shared across tabs)
available_weeks = sorted(df['week'].unique(), reverse=True)
selected_week = st.selectbox(
    "Week",
    options=available_weeks,
    format_func=lambda w: f"Week {w}"
)

# Get week boundaries (shared across tabs)
week_data = df[df['week'] == selected_week]
week_start = None
week_end = None
if 'week_start' in week_data.columns and 'week_end' in week_data.columns:
    ws = week_data['week_start'].iloc[0]
    we = week_data['week_end'].iloc[0]
    if pd.notna(ws) and pd.notna(we):
        week_start = pd.to_datetime(ws)
        week_end = pd.to_datetime(we) + pd.Timedelta(hours=23, minutes=59)

tab_dashboard, tab_single = st.tabs(["League Dashboard", "Single Matchup"])

# ==========================================================================
# TAB 1: LEAGUE DASHBOARD — all matchups in a grid
# ==========================================================================
with tab_dashboard:
    matchup_pairs = get_all_matchup_pairs(df, selected_week)

    if not matchup_pairs:
        st.warning("No matchups found for this week.")
    else:
        # 2-column grid
        for i in range(0, len(matchup_pairs), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(matchup_pairs):
                    break
                team1, team2 = matchup_pairs[idx]
                m_df = get_matchup_data(df, team1, selected_week)
                if m_df is None or m_df.empty:
                    col.warning(f"No data: {team1} vs {team2}")
                    continue
                latest = m_df.iloc[-1]
                with col:
                    # Compact score line
                    st.markdown(
                        f"**{latest['my_current']:.1f}** {latest['my_team']}  vs  "
                        f"**{latest['opp_current']:.1f}** {latest['opp_team']}"
                    )
                    fig = create_matchup_graph(m_df, week_start, week_end, compact=True)
                    st.plotly_chart(fig, use_container_width=True, key=f"dash_{idx}")

        # Data freshness
        last_ts = df[df['week'] == selected_week]['timestamp'].max()
        st.caption(f"Last data point: {last_ts.strftime('%a %b %d, %I:%M %p')}")

# ==========================================================================
# TAB 2: SINGLE MATCHUP — detailed view (existing behavior)
# ==========================================================================
with tab_single:
    teams = get_all_teams(df, selected_week)
    selected_team = st.selectbox("Select a team", options=teams, key="single_team")

    matchup_df = get_matchup_data(df, selected_team, selected_week)

    if matchup_df is None or matchup_df.empty:
        st.warning("No data found for this team/week.")
    else:
        latest = matchup_df.iloc[-1]
        my_team = matchup_df['my_team'].iloc[0]
        opp_team = matchup_df['opp_team'].iloc[0]

        # Score summary — show change since last data point
        def score_delta(col):
            if len(matchup_df) >= 2:
                return round(matchup_df[col].iloc[-1] - matchup_df[col].iloc[-2], 1)
            return "—"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"{my_team}", f"{latest['my_current']:.1f}", score_delta('my_current'))
        col2.metric(f"{opp_team}", f"{latest['opp_current']:.1f}", score_delta('opp_current'))
        col3.metric(f"{my_team} (Proj)", f"{latest['my_projected']:.1f}", score_delta('my_projected'))
        col4.metric(f"{opp_team} (Proj)", f"{latest['opp_projected']:.1f}", score_delta('opp_projected'))

        st.divider()

        fig = create_matchup_graph(matchup_df, week_start, week_end)
        st.plotly_chart(fig, use_container_width=True)

        last_update = matchup_df['timestamp'].max()
        st.caption(f"Last data point: {last_update.strftime('%a %b %d, %I:%M %p')} · {len(matchup_df)} data points collected")
