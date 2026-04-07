"""
storage.py  —  JSON-based persistence for CrickLive Python app.

Replaces the old DB-sync approach.  All match state (both teams with full
player stats, innings summaries, match settings) is saved to match_data.json
next to the CrickLive package root.
"""
import json
import os

# Resolve to  CrickLive/match_data.json  regardless of cwd
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(_BASE_DIR, "match_data.json")
LIVE_SNAPSHOT_FILE = os.path.join(_BASE_DIR, "match_live_snapshot.json")


def _safe_overs_decimal(team_obj, balls_in_current_over, balls_per_over):
    try:
        bpo = int(balls_per_over)
    except (TypeError, ValueError):
        bpo = 6
    if bpo <= 0:
        bpo = 6
    return team_obj.overs_played + (balls_in_current_over / bpo)


def _current_innings_runs(match_obj):
    start_total = getattr(match_obj, "current_innings_start_total", 0)
    runs = match_obj.batting_team.total_runs - start_total
    return runs if runs >= 0 else match_obj.batting_team.total_runs


def _innings_scores_map(match_obj, total_innings):
    scores = {1: 0, 2: 0, 3: 0, 4: 0}
    for entry in getattr(match_obj, "innings_summaries", []):
        inning_no = int(entry.get("inning", 0) or 0)
        if inning_no < 1 or inning_no > 4:
            continue
        scores[inning_no] = int(entry.get("runs", 0) or 0)

    current_innings = int(getattr(match_obj, "current_innings", 1) or 1)
    if 1 <= current_innings <= 4:
        scores[current_innings] = _current_innings_runs(match_obj)

    if total_innings == 2:
        scores[3] = 0
        scores[4] = 0

    return scores


def _player_snapshot(player_obj):
    if not player_obj:
        return None
    return {
        "name": player_obj.name,
        "runs": player_obj.runs_scored,
        "fours": player_obj.fours,
        "sixes": player_obj.sixes,
        "dot_balls": getattr(player_obj, "dot_balls", 0),
        "strike_rate": player_obj.strike_rate,
    }


def _build_live_snapshot(match_obj):
    total_innings = int(match_obj.settings.get("match_innings", 2) or 2)
    total_innings = 4 if total_innings == 4 else 2

    balls_per_over = int(match_obj.settings.get("balls_per_over", 6) or 6)
    innings_runs = _current_innings_runs(match_obj)
    innings_scores = _innings_scores_map(match_obj, total_innings)
    overs_decimal = _safe_overs_decimal(match_obj.batting_team, match_obj.balls_in_current_over, balls_per_over)
    crr = (innings_runs / overs_decimal) if overs_decimal > 0 else 0.0

    target_display = (match_obj.target + 1) if match_obj.target is not None else None

    base = {
        "match_type_innings": total_innings,
        "current_innings": match_obj.current_innings,
        "current_team": match_obj.batting_team.name,
        "current_batting_team_name": match_obj.batting_team.name,
        "current_bowling_team_name": match_obj.bowling_team.name,
        "current_team_score": innings_runs,
        "current_team_wickets": match_obj.batting_team.wickets_lost,
        "current_over_count": f"{match_obj.batting_team.overs_played}.{match_obj.balls_in_current_over}",
        "current_over_balls": list(match_obj.current_over_balls),
        "last_over_balls": list(match_obj.last_over),
        "striker": _player_snapshot(match_obj.striker),
        "non_striker": _player_snapshot(match_obj.non_striker),
        "bowler": {
            "name": match_obj.current_bowler.name if match_obj.current_bowler else None,
            "overs_bowled": match_obj.current_bowler.overs_bowled if match_obj.current_bowler else 0.0,
            "runs_conceded": match_obj.current_bowler.runs_conceded if match_obj.current_bowler else 0,
            "wickets_taken": match_obj.current_bowler.wickets_taken if match_obj.current_bowler else 0,
        },
        "target": target_display,
    }

    if total_innings == 2:
        base.update({
            "inning_1_score": innings_scores[1],
            "crr": round(crr, 2),
        })
    else:
        base.update({
            "current_inning_score": innings_runs,
            "crr": round(crr, 2),
            "inning_1_score": innings_scores[1],
            "inning_2_score": innings_scores[2],
            "inning_3_score": innings_scores[3],
            "inning_4_score": innings_scores[4],
        })

    return base


def save_match_data(match_obj):
    """Persist complete match state to JSON file."""
    data = match_obj.to_dict()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    live_snapshot = _build_live_snapshot(match_obj)
    with open(LIVE_SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(live_snapshot, f, indent=4, ensure_ascii=False)


def load_match_data():
    """Load match state from JSON. Returns dict or None if missing/corrupt."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def match_data_exists():
    """Return True when a saved match file is present."""
    return os.path.exists(DATA_FILE)


def reset_match_data():
    """Delete saved match files (use when starting a fresh match)."""
    for file_path in (DATA_FILE, LIVE_SNAPSHOT_FILE):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error clearing match data file {file_path}: {e}")