"""
Mock Data Generator for Fantasy Hockey Tracker
Generates realistic fake matchup data for testing visualization and automation.

Usage:
    python3 generate_mock_data.py                     # Normal week, all scenarios
    python3 generate_mock_data.py --scenario comeback  # Specific scenario
    python3 generate_mock_data.py --week 99            # Custom week number
    python3 generate_mock_data.py --output my_test.csv # Custom output file

Scenarios:
    normal    - Close, competitive matchup (default)
    comeback  - Team trails all week then surges at the end
    blowout   - One team dominates from the start
    flip      - Projected winner changes multiple times
"""

import csv
import random
import argparse
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURATION
# ============================================================================

# Real team names from the league (makes test data feel authentic)
TEAM_NAMES = [
    "The Nose Goes",
    "Pucker McPuckface",
    "More Like HelleSUCK Am I Right",
    "Eichel Tower",
    "Eichel on Ice",
    "Broke My Leg Pavelskiing",
    "Poke Checks",
    "Return Of The Mack",
    "The Big Sticks",
    "Weast Coast Bruins",
    "youre on your own sid",
    "ericas Optimal Team",
]

# NHL game windows (hour ranges when scores typically jump)
# Format: (start_hour, end_hour) in 24h time
WEEKDAY_GAME_WINDOW = (19, 23)   # 7 PM - 11 PM
WEEKEND_GAME_WINDOW = (13, 23)   # 1 PM - 11 PM

# Typical final score range for this league (from real data)
SCORE_RANGE = (140, 320)

# How often we'd collect data in real usage (every 2 hours)
COLLECTION_INTERVAL_HOURS = 2

# ============================================================================
# CORE SIMULATION LOGIC
# ============================================================================

def is_game_window(dt):
    """Returns True if this datetime falls during typical NHL game hours."""
    weekday = dt.weekday()  # 0=Monday, 6=Sunday
    hour = dt.hour
    if weekday >= 5:  # Weekend
        start, end = WEEKEND_GAME_WINDOW
    else:             # Weekday
        start, end = WEEKDAY_GAME_WINDOW
    return start <= hour < end


def generate_timestamps(week_start, week_end, interval_hours):
    """
    Generate a list of collection timestamps across a full week.
    Mimics the intelligent scheduler: more frequent during game windows.
    """
    timestamps = []
    current = week_start.replace(hour=10, minute=0, second=0, microsecond=0)

    while current <= week_end:
        timestamps.append(current)
        if is_game_window(current):
            # Collect every hour during games
            current += timedelta(hours=1)
        else:
            # Collect every 4 hours off-peak, skip overnight (midnight-9am)
            next_time = current + timedelta(hours=interval_hours)
            if next_time.hour < 9 and next_time.day > current.day:
                # Jump to 10am next day instead of collecting overnight
                next_time = next_time.replace(hour=10, minute=0)
            current = next_time

    return timestamps


def simulate_scores(scenario, final_score_team1, final_score_team2, timestamps):
    """
    Simulate how scores accumulate over the week for a given scenario.

    Returns two lists: (team1_currents, team2_currents)
    Scores only go up (can't un-score fantasy points).
    """
    n = len(timestamps)
    week_start = timestamps[0]
    week_end = timestamps[-1]
    total_seconds = (week_end - week_start).total_seconds()

    team1_scores = []
    team2_scores = []

    for i, ts in enumerate(timestamps):
        elapsed = (ts - week_start).total_seconds()
        progress = elapsed / total_seconds  # 0.0 at start, 1.0 at end

        if scenario == "blowout":
            # Team 1 scores heavily early, team 2 stays behind all week
            t1_progress = _accelerated(progress, bias=0.7)
            t2_progress = _decelerated(progress, bias=0.4)

        elif scenario == "comeback":
            # Team 2 leads most of the week, team 1 surges in last 2 days
            t1_progress = _comeback_curve(progress)
            t2_progress = _early_burst(progress)

        elif scenario == "flip":
            # Both teams trade the lead — projections flip multiple times
            t1_progress = _flip_curve(progress, phase=0)
            t2_progress = _flip_curve(progress, phase=0.5)

        else:  # normal
            # Both teams score steadily with slight random variation
            t1_progress = _steady(progress)
            t2_progress = _steady(progress)

        # Apply progress to final scores, add small noise, clamp to [0, final]
        t1 = round(min(final_score_team1, max(0, final_score_team1 * t1_progress + random.uniform(-3, 3))), 1)
        t2 = round(min(final_score_team2, max(0, final_score_team2 * t2_progress + random.uniform(-3, 3))), 1)

        # Scores can never decrease
        if team1_scores:
            t1 = max(t1, team1_scores[-1])
            t2 = max(t2, team2_scores[-1])

        team1_scores.append(t1)
        team2_scores.append(t2)

    return team1_scores, team2_scores


def simulate_projections(team1_currents, team2_currents, final1, final2, timestamps):
    """
    Simulate projected scores. Projections start near the season-average
    final score and converge toward actual as the week progresses.

    A projection roughly means: current_score + (expected remaining points).
    As the week ends, remaining points → 0, so projection → current score.
    """
    week_start = timestamps[0]
    week_end = timestamps[-1]
    total_seconds = (week_end - week_start).total_seconds()

    team1_projs = []
    team2_projs = []

    for i, ts in enumerate(timestamps):
        elapsed = (ts - week_start).total_seconds()
        progress = elapsed / total_seconds
        remaining = 1.0 - progress  # fraction of week left

        # Projected = current + (fraction remaining * expected total)
        # Add noise that shrinks as week progresses (projections get more certain)
        noise_scale = remaining * 15

        t1_proj = team1_currents[i] + (remaining * final1) + random.uniform(-noise_scale, noise_scale)
        t2_proj = team2_currents[i] + (remaining * final2) + random.uniform(-noise_scale, noise_scale)

        # Projections can't be lower than current score
        t1_proj = max(t1_proj, team1_currents[i])
        t2_proj = max(t2_proj, team2_currents[i])

        team1_projs.append(round(t1_proj, 2))
        team2_projs.append(round(t2_proj, 2))

    return team1_projs, team2_projs


# ============================================================================
# CURVE SHAPES (control how scores accumulate over time)
# ============================================================================

def _steady(progress):
    """Roughly linear accumulation with slight S-curve."""
    return progress ** 0.9


def _accelerated(progress, bias=0.7):
    """Scores heavily early in the week."""
    return min(1.0, progress ** (1 - bias))


def _decelerated(progress, bias=0.4):
    """Scores slowly, picks up late."""
    return progress ** (1 + bias)


def _comeback_curve(progress):
    """Flat early, then rapid gain in final 30% of week."""
    if progress < 0.7:
        return progress * 0.5
    else:
        catch_up = (progress - 0.7) / 0.3  # 0 to 1 in final 30%
        return 0.35 + catch_up * 0.65


def _early_burst(progress):
    """Scores fast early, then slows down."""
    if progress < 0.4:
        return progress * 1.5
    else:
        return 0.6 + (progress - 0.4) * 0.67


def _flip_curve(progress, phase=0):
    """Oscillating progress — creates lead changes."""
    import math
    base = progress
    oscillation = 0.12 * math.sin(progress * math.pi * 3 + phase * math.pi)
    return max(0, min(1, base + oscillation))


# ============================================================================
# DATA ASSEMBLY & OUTPUT
# ============================================================================

def generate_mock_week(
    scenario="normal",
    week_number=99,
    week_start_date="2026-03-02",
    team1_name=None,
    team2_name=None,
    seed=None,
):
    """
    Generate a full week of mock matchup data for one matchup.

    Args:
        scenario:        "normal", "comeback", "blowout", or "flip"
        week_number:     Week number to embed in the data
        week_start_date: ISO date string "YYYY-MM-DD"
        team1_name:      Override team 1 name (random if None)
        team2_name:      Override team 2 name (random if None)
        seed:            Random seed for reproducibility

    Returns:
        List of dicts matching the CSV schema used by collect_matchup_data.py
    """
    if seed is not None:
        random.seed(seed)

    week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
    week_end = week_start + timedelta(days=6, hours=23, minutes=59)

    # Pick team names
    available = TEAM_NAMES.copy()
    if team1_name is None:
        team1_name = random.choice(available)
    available = [t for t in available if t != team1_name]
    if team2_name is None:
        team2_name = random.choice(available)

    # Pick realistic final scores
    final1 = round(random.uniform(*SCORE_RANGE), 1)
    final2 = round(random.uniform(*SCORE_RANGE), 1)

    # Generate timestamps
    timestamps = generate_timestamps(week_start, week_end, COLLECTION_INTERVAL_HOURS)

    # Simulate score progression
    t1_currents, t2_currents = simulate_scores(scenario, final1, final2, timestamps)
    t1_projs, t2_projs = simulate_projections(t1_currents, t2_currents, final1, final2, timestamps)

    # Assemble rows
    rows = []
    for i, ts in enumerate(timestamps):
        rows.append({
            "timestamp": ts.isoformat(),
            "week": week_number,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "team1_name": team1_name,
            "team1_current_score": t1_currents[i],
            "team1_projected_score": t1_projs[i],
            "team2_name": team2_name,
            "team2_current_score": t2_currents[i],
            "team2_projected_score": t2_projs[i],
        })

    return rows


def save_mock_data(rows, output_file):
    """Write mock data rows to a CSV file in the same format as real data."""
    fieldnames = [
        "timestamp", "week", "week_start", "week_end",
        "team1_name", "team1_current_score", "team1_projected_score",
        "team2_name", "team2_current_score", "team2_projected_score",
    ]
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {output_file}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate mock fantasy hockey matchup data for testing.")
    parser.add_argument(
        "--scenario",
        choices=["normal", "comeback", "blowout", "flip"],
        default="normal",
        help="Score progression scenario to simulate (default: normal)",
    )
    parser.add_argument(
        "--week",
        type=int,
        default=99,
        help="Week number to embed in the data (default: 99)",
    )
    parser.add_argument(
        "--start-date",
        default="2026-03-02",
        help="Week start date in YYYY-MM-DD format (default: 2026-03-02)",
    )
    parser.add_argument(
        "--output",
        default="mock_matchup_data.csv",
        help="Output CSV filename (default: mock_matchup_data.csv)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output",
    )
    args = parser.parse_args()

    print(f"Generating '{args.scenario}' scenario for week {args.week}...")
    rows = generate_mock_week(
        scenario=args.scenario,
        week_number=args.week,
        week_start_date=args.start_date,
        seed=args.seed,
    )

    save_mock_data(rows, args.output)

    # Print a quick summary so you can sanity-check the output
    first = rows[0]
    last = rows[-1]
    print()
    print(f"  Matchup:  {first['team1_name']}  vs  {first['team2_name']}")
    print(f"  Week:     {first['week_start']} → {first['week_end']}")
    print(f"  Points:   {len(rows)} data points collected")
    print()
    print(f"  Start:  {first['team1_name']} {first['team1_current_score']} - {first['team2_current_score']} {first['team2_name']}")
    print(f"  End:    {last['team1_name']} {last['team1_current_score']} - {last['team2_current_score']} {last['team2_name']}")
    print()
    print(f"To visualize: rename {args.output} to matchup_data.csv, then run python3 visualize_matchup.py")


if __name__ == "__main__":
    main()
