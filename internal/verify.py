import sys
import os

# Ensure we can import from internal package regardless of where this script is run
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from internal.match_logic import Match
from internal.models import Team, Player

def test_noball_options():
    print("\n--- Testing No Ball Options ---")
    p1 = Player("Striker")
    p2 = Player("NonStriker")
    team_a = Team("Team A", [p1, p2])
    team_b = Team("Team B", [Player("Bowler")])
    match = Match(team_a, team_b)
    match.start_match()
    match.set_bowler("Bowler")

    # Case 1: No Ball + 4, Credit to Striker (Standard)
    print("1. NB + 4 (Striker)")
    match.record_ball(runs=4, is_noball=True, is_bye=False)
    # Expect: Total=5 (1NB+4), Striker=4, Extras=1(NB)
    if match.batting_team.total_runs == 5 and match.striker.runs_scored == 4 and match.batting_team.extras == 1:
        print("PASS")
    else:
        print(f"FAIL: T={match.batting_team.total_runs} S={match.striker.runs_scored} E={match.batting_team.extras}")

    # Case 2: No Ball + 2, Credit to Team (Extras)
    print("2. NB + 2 (Team/Extras)")
    match.record_ball(runs=2, is_noball=True, is_bye=True)
    # Expect: Total=5+3=8 (1NB+2Byes), Striker=4+0=4, Extras=1+3=4
    if match.batting_team.total_runs == 8 and match.striker.runs_scored == 4 and match.batting_team.extras == 4:
        print("PASS")
    else:
        print(f"FAIL: T={match.batting_team.total_runs} S={match.striker.runs_scored} E={match.batting_team.extras}")

def test_out_selection():
    print("\n--- Testing Out Selection ---")
    p1 = Player("Striker")
    p2 = Player("NonStriker")
    p3 = Player("NextMan")
    team_a = Team("Team A", [p1, p2, p3])
    team_b = Team("Team B", [Player("Bowler")])
    match = Match(team_a, team_b)
    match.start_match()
    match.set_bowler("Bowler")

    # Case 1: Out Non-Striker
    print("1. Out Non-Striker")
    match.record_ball(runs=0, is_wicket=True, dismissed_player_name="NonStriker", dismissal_type="Run Out")
    
    if match.non_striker is None and match.striker.name == "Striker" and len(match.batting_team.players)-1 > match.batting_team.wickets_lost :
        print("PASS: Non-Striker slot is empty")
    else:
        print(f"FAIL: NS={match.non_striker} S={match.striker}")

    # Case 2: New Batsman fills Non-Striker slot
    print("2. New Batsman fills slot")
    match.set_new_batsman("NextMan")
    if match.non_striker and match.non_striker.name == "NextMan":
        print("PASS: NextMan is Non-Striker")
    else:
        print(f"FAIL: NS={match.non_striker}")

def test_match_settings():
    print("\n--- Testing Match Settings ---")
    # Setup
    t1 = Team("Team A", [Player("P1"), Player("P2")])
    t2 = Team("Team B", [Player("P3"), Player("P4")])
    match = Match(t1, t2)
    match.start_match()
    match.set_bowler("P3")

    # Test Default (1 run)
    print("Testing Defaults...")
    match.record_ball(0, is_wide=True) 
    assert match.batting_team.extras == 1, f"Expected 1 extra, got {match.batting_team.extras}"
    assert match.current_over_runs == 1, f"Expected 1 run, got {match.current_over_runs}"
    
    # Test Edit Settings (2 runs)
    print("Testing Modified Settings...")
    match.wide_val = 2
    match.noball_val = 3
    
    match.record_ball(0, is_wide=True)
    # Previous 1 + New 2 = 3
    assert match.batting_team.extras == 3, f"Expected 3 extras, got {match.batting_team.extras}"
    
    match.record_ball(0, is_noball=True)
    # Previous 3 + New 3 = 6
    assert match.batting_team.extras == 6, f"Expected 6 extras, got {match.batting_team.extras}"
    
    # Test Dictionary Serialization
    data = match.to_dict()
    assert data['wide_val'] == 2
    assert data['noball_val'] == 3
    
    print("Match settings verification passed!")

def test_edit_teams():
    print("\n--- Testing Edit Teams ---")
    # Setup
    p1 = Player("OldPlayer1")
    t1 = Team("OldTeamA", [p1, Player("P2")])
    t2 = Team("Team B", [Player("P3"), Player("P4")])
    match = Match(t1, t2)
    match.start_match() # Sets striker to p1
    
    print(f"Original: {match.batting_team.name}, Striker: {match.striker.name}")
    assert match.batting_team.name == "OldTeamA"
    assert match.striker.name == "OldPlayer1"
    
    # Edit Names
    print("Editing names...")
    match.batting_team.name = "NewTeamA"
    p1.name = "NewPlayer1"
    
    # Verify References
    print(f"New: {match.batting_team.name}, Striker: {match.striker.name}")
    assert match.batting_team.name == "NewTeamA"
    assert match.striker.name == "NewPlayer1"
    assert match.team_a.players[0].name == "NewPlayer1"
    
    # Verify Serialization
    data = match.to_dict()
    assert data['batting_team_name'] == "NewTeamA"
    assert data['striker_name'] == "NewPlayer1"
    
    print("Edit Teams logic verified!")

def test_extras_logic():
    print("\n--- Testing Extras Logic ---")
    p1 = Player("P1")
    p2 = Player("P2")
    t1 = Team("A", [p1, p2])
    b1 = Player("B1")
    t2 = Team("B", [b1])
    
    m = Match(t1, t2)
    m.start_match()
    m.set_bowler("B1")
    
    # 1. Test Default/Bye Logic (simulating "Default" + 2 runs)
    print("Testing Default (Byes) + 2 runs...")
    m.record_ball(2, is_bye=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "b2" or last_ball == "2" 
    assert m.batting_team.extras == 2
    assert m.batting_team.total_runs == 2
    assert m.balls_in_current_over == 1
    
    # 2. Test Wide + 1 run (simulating "Wide" + 1 run)
    print("Testing Wide + 1 run...")
    m.record_ball(1, is_wide=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "2wb"
    assert m.batting_team.total_runs == 4 # Prev 2 + 1(wide) + 1(run)
    assert m.balls_in_current_over == 1
    
    # 3. Test NoBall + 4 runs (simulating "No Ball" + 4 runs)
    print("Testing NoBall + 4 runs...")
    m.record_ball(4, is_noball=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "NB4"
    assert m.batting_team.total_runs == 9 # Prev 4 + 1(nb) + 4(runs)
    assert m.balls_in_current_over == 1
    
    print("Extras logic verification passed")

def test_noball_standalone():
    print("\n--- Testing No Ball Standalone ---")
    # Setup
    p1 = Player("Striker")
    p2 = Player("NonStriker")
    team_a = Team("Team A", [p1, p2])
    team_b = Team("Team B", [Player("Bowler")])
    match = Match(team_a, team_b)
    match.start_match()
    match.set_bowler("Bowler")

    # Record No Ball with 4 runs
    print(f"Initial Striker Runs: {match.striker.runs_scored}")
    print(f"Initial Striker Fours: {match.striker.fours}")
    print("Recording No Ball + 4 runs...")

    match.record_ball(runs=4, is_noball=True)

    # Check results
    print(f"Striker Runs: {match.striker.runs_scored}")
    print(f"Striker Fours: {match.striker.fours}")
    print(f"Total Score: {match.batting_team.total_runs}")
    print(f"Extras: {match.batting_team.extras}")
    print(f"This Over: {match.current_over_balls}")

    if match.striker.runs_scored == 4 and match.striker.fours == 1:
        print("SUCCESS: Runs credited to striker correctly.")
    else:
        print("FAILURE: Runs NOT credited to striker correctly.")

def test_wide_logic():
    print("\n--- Testing Wide Logic ---")
    p1 = Player("P1")
    p2 = Player("P2")
    t1 = Team("A", [p1, p2])
    
    b1 = Player("B1")
    t2 = Team("B", [b1])
    
    m = Match(t1, t2)
    m.start_match()
    m.set_bowler("B1")
    
    print("Testing 0 runs wide (expect 'wb')...")
    m.record_ball(0, is_wide=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "wb"
    assert m.batting_team.total_runs == 1
    
    print("Testing 1 run wide (expect '2wb')...")
    m.record_ball(1, is_wide=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "2wb"
    assert m.batting_team.total_runs == 1 + 2 # 3 total
    
    print("Testing 4 runs wide (expect '5wb')...")
    m.record_ball(4, is_wide=True)
    last_ball = m.current_over_balls[-1]
    print(f"Result: {last_ball}")
    assert last_ball == "5wb"
    
    print("Wide logic tests passed")

if __name__ == "__main__":
    print("====================================")
    print("RUNNING ALL CRICKLIVE VERIFICATIONS")
    print("====================================")
    
    try:
        test_noball_options()
        test_out_selection()
        test_match_settings()
        test_edit_teams()
        test_extras_logic()
        test_noball_standalone()
        test_wide_logic()
        print("\n\nALL TESTS COMPLETED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
