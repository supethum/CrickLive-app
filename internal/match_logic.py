"""
match_logic.py  —  Web-parity scoring engine for CrickLive Python app.

Mirrors the scoring logic from the web app's LiveScoreInput.js recordBall()
function exactly: bye/leg-bye handling, ball display strings, settings-aware
delivery counting, dismissal text generation, and innings management.
"""
import copy

# ── Default match settings (mirrors web DEFAULT_MATCH_SETTINGS) ──────────────
DEFAULT_SETTINGS = {
    "total_overs": 20,
    "balls_per_over": 6,
    "wide_val": 1,
    "noball_val": 1,
    "bye_val": 1,
    "legbye_val": 1,
    "max_players": 11,
    "last_man_stand": False,
    "wide_counts_as_ball": False,
    "noball_counts_as_ball": True,
}

# ── Dismissal type sets (mirrors web constants) ───────────────────────────────
BOWLER_CREDIT_DISMISSAL_TYPES = {
    "bowled", "caught", "lbw", "stumped", "hit wicket",
}
WICKET_ALLOWED_ON_NOBALL_TYPES = {
    "run out", "hit the ball twice", "obstructing the field",
}
DONT_COUNT_BALL_DISMISSAL_TYPES = {
    "absent", "mankad", "timed out", "retired out", "retired hurt",
}


def _to_dismissal_key(value):
    return str(value or "").strip().lower()


def _get_dismissal_text(dismissal_type_key, bowler_name="", by_name=""):
    """Generate human-readable dismissal text matching web app format."""
    dtk = dismissal_type_key
    bowler = str(bowler_name or "").strip()
    by = str(by_name or "").strip()

    if dtk == "bowled":
        return f"b {bowler}" if bowler else "b"
    elif dtk == "caught":
        if bowler and by:
            if bowler.lower() == by.lower():
                return f"c & b {bowler}"
            return f"c {by} b {bowler}"
        elif bowler:
            return f"b {bowler} c"
        elif by:
            return f"c {by}"
        return "caught"
    elif dtk == "lbw":
        return f"lbw b {bowler}" if bowler else "lbw"
    elif dtk == "stumped":
        if bowler and by:
            return f"st {by} b {bowler}"
        elif bowler:
            return f"b {bowler} st"
        return "stumped"
    elif dtk == "run out":
        return f"run out ({by})" if by else "run out"
    elif dtk == "hit wicket":
        return f"hit wicket b {bowler}" if bowler else "hit wicket"
    elif dtk == "obstructing the field":
        return f"obstructing the field ({by})" if by else "obstructing the field"
    elif dtk == "mankad":
        return "mankad"
    elif dtk == "hit the ball twice":
        return "hit the ball twice"
    elif dtk == "timed out":
        return "timed out"
    elif dtk == "absent":
        return "absent"
    elif dtk == "retired out":
        return "retired out"
    elif dtk == "retired hurt":
        return "retired hurt"
    return dismissal_type_key or "Wicket"


def _get_ball_display(runs, is_wicket, is_wide, is_noball, is_reg_bye, is_reg_legbye):
    """Compute ball display string matching web app format exactly."""
    if is_wicket:
        if is_wide:
            suffix = "WD" if runs == 0 else f"{runs}WD"
        elif is_noball and is_reg_bye:
            suffix = "BN" if runs == 0 else f"{runs}BN"
        elif is_noball and is_reg_legbye:
            suffix = "LBN" if runs == 0 else f"{runs}LBN"
        elif is_noball:
            suffix = "NB" if runs == 0 else f"{runs}NB"
        elif is_reg_legbye:
            suffix = "LB" if runs == 0 else f"{runs}LB"
        elif is_reg_bye:
            suffix = "B" if runs == 0 else f"{runs}B"
        elif runs > 0:
            suffix = str(runs)
        else:
            suffix = ""
        return f"W+{suffix}" if suffix else "W"
    elif is_wide:
        return "WD" if runs == 0 else f"{runs}WD"
    elif is_noball and is_reg_bye:
        return f"N+{runs}B"
    elif is_noball and is_reg_legbye:
        return f"N+{runs}LB"
    elif is_noball:
        return "NB" if runs == 0 else f"{runs}NB"
    elif is_reg_legbye:
        return "LB" if runs == 0 else f"{runs}LB"
    elif is_reg_bye:
        return "B" if runs == 0 else f"{runs}B"
    else:
        return str(runs)


# ── Match class ───────────────────────────────────────────────────────────────
class Match:
    def __init__(self, team_a, team_b, settings=None):
        self.team_a = team_a
        self.team_b = team_b
        self.settings = {**DEFAULT_SETTINGS, **(settings or {})}

        self.current_innings = 1
        self.batting_team = self.team_a
        self.bowling_team = self.team_b

        self.striker = None
        self.non_striker = None
        self.current_bowler = None

        self.balls_in_current_over = 0
        self.current_over_runs = 0
        self.current_over_balls = []
        self.last_over = []

        self.match_over = False
        self.winner = None
        self.target = None
        self.innings_summaries = []
        self.history = []
        self.current_innings_start_total = self.batting_team.total_runs

        # Set by GUI to respond to inning transitions
        self.gui_callback = None
        self.inning_complete_pending = False

    # ── Startup ──────────────────────────────────────────────────────────────
    def start_match(self):
        available = [p for p in self.batting_team.players if not p.is_out]
        if len(available) >= 2:
            self.striker = available[0]
            self.non_striker = available[1]

    def _total_innings(self):
        try:
            innings = int(self.settings.get("match_innings", 2))
        except (TypeError, ValueError):
            innings = 2
        return 4 if innings == 4 else 2

    def _is_final_innings(self):
        return self.current_innings >= self._total_innings()

    def _finalize_match_from_totals(self):
        if self.target is not None:
            if self.batting_team.total_runs > self.target:
                self.winner = self.batting_team.name
            elif self.batting_team.total_runs == self.target:
                self.winner = "TIE"
            else:
                self.winner = self.bowling_team.name
        else:
            if self.team_a.total_runs > self.team_b.total_runs:
                self.winner = self.team_a.name
            elif self.team_b.total_runs > self.team_a.total_runs:
                self.winner = self.team_b.name
            else:
                self.winner = "TIE"
        self.match_over = True

    def force_end_innings(self):
        """Force-complete current innings (used by GUI End Inning action)."""
        if self.match_over:
            return False
        if self._is_final_innings():
            self._finalize_match_from_totals()
        else:
            self.inning_complete_pending = True
        return True

    # ── Player setters ────────────────────────────────────────────────────────
    def set_bowler(self, name):
        p = self.bowling_team.get_player(name)
        if p:
            self.current_bowler = p
            return True
        return False

    def set_striker(self, name):
        p = self.batting_team.get_player(name)
        if p:
            self.striker = p
            return True
        return False

    def set_non_striker(self, name):
        p = self.batting_team.get_player(name)
        if p:
            self.non_striker = p
            return True
        return False

    def set_new_batsman(self, name):
        p = self.batting_team.get_player(name)
        if p:
            if self.striker is None:
                self.striker = p
            elif self.non_striker is None:
                self.non_striker = p
            else:
                self.striker = p
            return True
        return False

    # ── Core scoring: record_ball ─────────────────────────────────────────────
    def record_ball(self, runs, is_wicket=False, is_wide=False, is_noball=False,
                    is_bye=False, is_leg_bye=False, dismissal_type=None,
                    dismissed_player_name=None, dismissed_by_name=None,
                    dont_count_ball=False):
        if self.match_over:
            return

        s = self.settings
        balls_per_over        = int(s.get("balls_per_over", 6))
        wide_val              = int(s.get("wide_val", 1))
        noball_val            = int(s.get("noball_val", 1))
        wide_counts_as_ball   = bool(s.get("wide_counts_as_ball", False))
        noball_counts_as_ball = bool(s.get("noball_counts_as_ball", True))

        dtk = _to_dismissal_key(dismissal_type)
        bowler_gets_wicket_credit = (
            not dtk or dtk in BOWLER_CREDIT_DISMISSAL_TYPES
        )

        is_reg_bye    = is_bye and not is_noball
        is_reg_legbye = is_leg_bye and not is_noball

        # ── Extras and team totals ────────────────────────────────────────────
        extras = 0
        if is_wide:
            extras += wide_val
            self.batting_team.extras += wide_val
        elif is_noball:
            extras += noball_val
            self.batting_team.extras += noball_val

        if is_reg_bye:
            self.batting_team.extras += runs
        elif is_reg_legbye:
            self.batting_team.extras += runs

        total_ball_runs = runs + extras
        self.batting_team.total_runs += total_ball_runs
        self.current_over_runs += total_ball_runs

        # ── Ball display ──────────────────────────────────────────────────────
        self.current_over_balls.append(
            _get_ball_display(runs, is_wicket, is_wide, is_noball,
                              is_reg_bye, is_reg_legbye)
        )

        # ── Striker batting stats ─────────────────────────────────────────────
        if self.striker and not is_wide and not dont_count_ball:
            self.striker.balls_faced += 1
            if runs == 0 and not is_noball and not is_reg_bye and not is_reg_legbye:
                self.striker.dot_balls += 1
        if self.striker and not is_wide and not is_reg_bye and not is_reg_legbye:
            self.striker.runs_scored += runs
            if runs == 4:
                self.striker.fours += 1
            if runs == 6:
                self.striker.sixes += 1

        # ── Delivery counting ─────────────────────────────────────────────────
        delivery_counts = not dont_count_ball and (
            (not is_wide and not is_noball)
            or (is_wide and wide_counts_as_ball)
            or (is_noball and noball_counts_as_ball)
        )

        # ── Bowler stats ──────────────────────────────────────────────────────
        if self.current_bowler:
            if not is_reg_bye and not is_reg_legbye:
                self.current_bowler.runs_conceded += (runs + extras)
            else:
                self.current_bowler.runs_conceded += extras

            if delivery_counts:
                self.current_bowler.balls_bowled_count += 1
                ovs = self.current_bowler.balls_bowled_count // balls_per_over
                rem = self.current_bowler.balls_bowled_count % balls_per_over
                self.current_bowler.overs_bowled = float(f"{ovs}.{rem}")

            if is_wicket and not is_noball and bowler_gets_wicket_credit:
                self.current_bowler.wickets_taken += 1

        # ── Wicket processing ─────────────────────────────────────────────────
        if is_wicket and (not is_noball or dtk in WICKET_ALLOWED_ON_NOBALL_TYPES):
            is_retired_hurt = dtk == "retired hurt"
            if not is_retired_hurt:
                self.batting_team.wickets_lost += 1

            out = self.striker
            if (dismissed_player_name and self.non_striker and
                    dismissed_player_name.lower() == self.non_striker.name.lower()):
                out = self.non_striker

            if out:
                bowler_name = self.current_bowler.name if self.current_bowler else ""
                by_name = str(dismissed_by_name or "").strip()
                d_text = _get_dismissal_text(dtk, bowler_name, by_name)

                out.is_out = True
                out.how_out = d_text
                out.dismissal_text = d_text
                out.dismissal_type = dismissal_type or "Wicket"
                out.by_player = by_name or None
                out.dismissed_by = by_name or None

                if out is self.striker:
                    self.striker = None
                else:
                    self.non_striker = None

        # ── Ball count for over ───────────────────────────────────────────────
        if delivery_counts:
            self.balls_in_current_over += 1

        # ── Strike rotation ───────────────────────────────────────────────────
        if runs % 2 != 0 and self.striker and self.non_striker:
            self.striker, self.non_striker = self.non_striker, self.striker

        # ── End of over ───────────────────────────────────────────────────────
        if self.balls_in_current_over == balls_per_over:
            self.batting_team.overs_played += 1
            self.balls_in_current_over = 0
            self.current_over_runs = 0
            self.last_over = list(self.current_over_balls)
            self.current_over_balls = []
            if self.striker and self.non_striker:
                self.striker, self.non_striker = self.non_striker, self.striker
            self.current_bowler = None

        # ── Check match status ────────────────────────────────────────────────
        self._check_match_status()

    # ── Match status ──────────────────────────────────────────────────────────
    def _check_match_status(self):
        s = self.settings
        max_players    = int(s.get("max_players", 11))
        last_man_stand = bool(s.get("last_man_stand", False))
        total_overs    = int(s.get("total_overs", 20))

        all_out_threshold = max_players if last_man_stand else max(1, max_players - 1)

        # In a chasing innings, immediate win when target crossed
        if self._is_final_innings() and self.target is not None:
            if self.batting_team.total_runs > self.target:
                self.match_over = True
                self.winner = self.batting_team.name
                return

        # All-out or overs complete
        if (self.batting_team.wickets_lost >= all_out_threshold or
                self.batting_team.overs_played >= total_overs):
            if not self._is_final_innings():
                self.inning_complete_pending = True
            else:
                self._finalize_match_from_totals()

    # ── Innings switch ────────────────────────────────────────────────────────
    def switch_innings(self):
        """Move to next innings and prepare new batting side."""
        completed_innings_runs = self.batting_team.total_runs - self.current_innings_start_total
        self.innings_summaries.append({
            "inning": self.current_innings,
            "team": self.batting_team.name,
            "runs": completed_innings_runs,
            "aggregate_runs": self.batting_team.total_runs,
            "wickets": self.batting_team.wickets_lost,
            "overs": self.batting_team.overs_played,
            "extras": self.batting_team.extras,
        })

        total_innings = self._total_innings()
        completed_inning = self.current_innings
        self.current_innings += 1
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team

        # In 2 innings, chase starts in inning 2.
        # In 4 innings, chase starts in inning 4 (after inning 3 is complete).
        if total_innings == 2 and completed_inning == 1:
            self.target = self.bowling_team.total_runs
        elif total_innings == 4 and completed_inning == 3:
            self.target = self.bowling_team.total_runs
        else:
            self.target = None

        self.current_innings_start_total = self.batting_team.total_runs
        self.batting_team.wickets_lost = 0
        self.batting_team.overs_played = 0
        self.batting_team.extras = 0

        self.balls_in_current_over = 0
        self.current_over_runs = 0
        self.current_over_balls = []
        self.last_over = []
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.inning_complete_pending = False

    # ── Undo / Redo ───────────────────────────────────────────────────────────
    def snapshot(self):
        state = {k: v for k, v in self.__dict__.items()
                 if k not in ("history", "gui_callback")}
        self.history.append(copy.deepcopy(state))

    def undo(self):
        if not self.history:
            return False
        state = self.history.pop()
        for key, value in state.items():
            setattr(self, key, value)
        # Re-link object references after deepcopy restore
        if self.striker:
            self.striker = self.batting_team.get_player(self.striker.name)
        if self.non_striker:
            self.non_striker = self.batting_team.get_player(self.non_striker.name)
        if self.current_bowler:
            self.current_bowler = self.bowling_team.get_player(self.current_bowler.name)
        return True

    # ── Serialisation ─────────────────────────────────────────────────────────
    def to_dict(self):
        """Full match state for JSON persistence."""
        return {
            "match_settings": self.settings,
            "team_a": self.team_a.to_dict(),
            "team_b": self.team_b.to_dict(),
            "batting_team_name": self.batting_team.name,
            "current_innings": self.current_innings,
            "target": self.target,
            "balls_in_current_over": self.balls_in_current_over,
            "current_over_balls": self.current_over_balls,
            "last_over": self.last_over,
            "striker_name": self.striker.name if self.striker else "",
            "non_striker_name": self.non_striker.name if self.non_striker else "",
            "current_bowler_name": self.current_bowler.name if self.current_bowler else "",
            "match_over": self.match_over,
            "winner": self.winner,
            "innings_summaries": self.innings_summaries,
            "current_innings_start_total": self.current_innings_start_total,
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a Match from a JSON state dict."""
        from internal.models import Team
        settings = data.get("match_settings", {})
        team_a = Team.from_dict(data["team_a"])
        team_b = Team.from_dict(data["team_b"])

        match = cls(team_a, team_b, settings)
        match.current_innings = data.get("current_innings", 1)
        match.target = data.get("target", None)
        match.balls_in_current_over = data.get("balls_in_current_over", 0)
        match.current_over_balls = data.get("current_over_balls", [])
        match.last_over = data.get("last_over", [])
        match.match_over = data.get("match_over", False)
        match.winner = data.get("winner", None)
        match.innings_summaries = data.get("innings_summaries", [])

        batting_name = data.get("batting_team_name", team_a.name)
        if batting_name == team_b.name:
            match.batting_team = team_b
            match.bowling_team = team_a
        else:
            match.batting_team = team_a
            match.bowling_team = team_b

        if "current_innings_start_total" in data:
            match.current_innings_start_total = data.get("current_innings_start_total", match.batting_team.total_runs)
        else:
            innings_summaries = data.get("innings_summaries", [])
            previous_team_runs = 0
            for inning_data in innings_summaries:
                if inning_data.get("team") != match.batting_team.name:
                    continue
                if inning_data.get("inning", 0) >= match.current_innings:
                    continue
                previous_team_runs += int(inning_data.get("runs", 0))

            match.current_innings_start_total = previous_team_runs

        sn = data.get("striker_name", "")
        nsn = data.get("non_striker_name", "")
        bn = data.get("current_bowler_name", "")
        if sn:
            match.striker = match.batting_team.get_player(sn)
        if nsn:
            match.non_striker = match.batting_team.get_player(nsn)
        if bn:
            match.current_bowler = match.bowling_team.get_player(bn)

        return match