import uuid


class Player:
    def __init__(self, name, role="all_rounder"):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role

        # Batting stats
        self.runs_scored = 0
        self.balls_faced = 0
        self.fours = 0
        self.sixes = 0
        self.dot_balls = 0
        self.is_out = False
        self.how_out = None
        self.dismissal_text = None
        self.dismissal_type = None
        self.by_player = None
        self.dismissed_by = None

        # Bowling stats
        self.overs_bowled = 0.0
        self.balls_bowled_count = 0
        self.runs_conceded = 0
        self.wickets_taken = 0
        self.maidens = 0

    @property
    def strike_rate(self):
        if self.balls_faced == 0:
            return 0.0
        return round((self.runs_scored / self.balls_faced) * 100, 2)

    @property
    def economy_rate(self):
        if self.overs_bowled == 0:
            return 0.0
        return round(self.runs_conceded / self.overs_bowled, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "runs_scored": self.runs_scored,
            "balls_faced": self.balls_faced,
            "fours": self.fours,
            "sixes": self.sixes,
            "dot_balls": self.dot_balls,
            "is_out": self.is_out,
            "how_out": self.how_out,
            "dismissal_text": self.dismissal_text,
            "dismissal_type": self.dismissal_type,
            "by_player": self.by_player,
            "dismissed_by": self.dismissed_by,
            "overs_bowled": self.overs_bowled,
            "balls_bowled_count": self.balls_bowled_count,
            "runs_conceded": self.runs_conceded,
            "wickets_taken": self.wickets_taken,
            "maidens": self.maidens,
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data.get("name", ""), data.get("role", "all_rounder"))
        p.id = data.get("id", p.id)
        p.runs_scored = data.get("runs_scored", 0)
        p.balls_faced = data.get("balls_faced", 0)
        p.fours = data.get("fours", 0)
        p.sixes = data.get("sixes", 0)
        p.dot_balls = data.get("dot_balls", 0)
        p.is_out = data.get("is_out", False)
        p.how_out = data.get("how_out", None)
        p.dismissal_text = data.get("dismissal_text", None)
        p.dismissal_type = data.get("dismissal_type", None)
        p.by_player = data.get("by_player", None)
        p.dismissed_by = data.get("dismissed_by", None)
        p.overs_bowled = data.get("overs_bowled", 0.0)
        p.balls_bowled_count = data.get("balls_bowled_count", 0)
        p.runs_conceded = data.get("runs_conceded", 0)
        p.wickets_taken = data.get("wickets_taken", 0)
        p.maidens = data.get("maidens", 0)
        return p


class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players
        self.total_runs = 0
        self.wickets_lost = 0
        self.overs_played = 0
        self.extras = 0

    def get_player(self, player_name):
        for p in self.players:
            if p.name.lower() == player_name.lower():
                return p
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "total_runs": self.total_runs,
            "wickets_lost": self.wickets_lost,
            "overs_played": self.overs_played,
            "extras": self.extras,
            "players": [p.to_dict() for p in self.players],
        }

    @classmethod
    def from_dict(cls, data):
        players = [Player.from_dict(p) for p in data.get("players", [])]
        team = cls(data.get("name", ""), players)
        team.total_runs = data.get("total_runs", 0)
        team.wickets_lost = data.get("wickets_lost", 0)
        team.overs_played = data.get("overs_played", 0)
        team.extras = data.get("extras", 0)
        return team