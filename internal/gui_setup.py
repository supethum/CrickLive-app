import tkinter as tk
from tkinter import ttk, messagebox
from internal.models import Player, Team
from internal.match_logic import Match
from internal.storage import load_match_data, match_data_exists, save_match_data, reset_match_data
from internal.gui_constants import COLORS, FONT_SML, ModernButton, ModernEntry, ModernText, create_popup_window
from internal.gui_scorer import CricketScorerApp

class SetupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Match Setup")
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        target_w, target_h = 450, 750
        w = min(target_w, max(380, screen_width - 40))
        h = min(target_h, max(620, screen_height - 80))
        x = max(0, int((screen_width - w) / 2))
        y = max(0, int((screen_height - h) / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=COLORS["bg_body"])
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=COLORS["bg_body"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["bg_panel"], foreground="white", padding=[10, 8], font=FONT_SML)
        style.map("TNotebook.Tab", background=[("selected", COLORS["primary"])])
        style.configure("TFrame", background=COLORS["bg_body"])

        header = tk.Frame(root, bg=COLORS["bg_body"])
        header.pack(fill="x", pady=12)
        tk.Label(header, text="NEW MATCH", font=("Segoe UI", 20, "bold"), bg=COLORS["bg_body"], fg="white").pack()
        self.header = header

        if match_data_exists():
            self.btn_resume = ModernButton(self.header, text="RESUME SAVED MATCH", bg=COLORS["warning"], fg="black", command=self.resume_match)
            self.btn_resume.pack(pady=10)
        else:
            self.btn_resume = None
        self.btn_start_next_inning = None

        self.temp_settings = {
            "total_overs": 20,
            "balls_per_over": 6,
            "wide_val": 1,
            "noball_val": 1,
            "max_players": 11,
            "match_innings": 2,
            "wide_counts_as_ball": False,
            "noball_counts_as_ball": True,
            "last_man_stand": False
        }

        # Basic Info
        info_frame = tk.Frame(root, bg=COLORS["bg_body"], padx=25)
        info_frame.pack(fill="x")

        tk.Label(info_frame, text="Team A Name:", bg=COLORS["bg_body"], fg="gray").grid(row=0, column=0, sticky="w", pady=5)
        self.team_a_name = tk.StringVar(value="Team A")
        ModernEntry(info_frame).entry.configure(textvariable=self.team_a_name)
        info_frame.winfo_children()[-1].grid(row=0, column=1, sticky="ew", padx=10)

        tk.Label(info_frame, text="Team B Name:", bg=COLORS["bg_body"], fg="gray").grid(row=1, column=0, sticky="w", pady=5)
        self.team_b_name = tk.StringVar(value="Team B")
        ModernEntry(info_frame).entry.configure(textvariable=self.team_b_name)
        info_frame.winfo_children()[-1].grid(row=1, column=1, sticky="ew", padx=10)
        
        info_frame.columnconfigure(1, weight=1)

        self.team_a_name.trace_add("write", self.update_toss_options)
        self.team_b_name.trace_add("write", self.update_toss_options)

        # Players Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=8, padx=20, expand=True, fill="both")
        
        self.text_p1 = self.create_player_tab("Team A Players")
        self.text_p2 = self.create_player_tab("Team B Players")
        self.tab1 = self.text_p1.master
        self.tab2 = self.text_p2.master

        self.text_p1.insert("1.0", "\n".join([f"Player A{i+1}" for i in range(11)]))
        self.text_p2.insert("1.0", "\n".join([f"Player B{i+1}" for i in range(11)]))

        # Settings
        self.settings_frame = tk.Frame(root, bg=COLORS["bg_body"], padx=25)
        self.settings_frame.pack(fill="x", pady=5)
        
        tk.Label(self.settings_frame, text="Toss Won & Batting:", bg=COLORS["bg_body"], fg="gray").pack(anchor="w")
        self.toss_var = tk.StringVar(value="Team A")
        self.cb_toss = ttk.Combobox(self.settings_frame, textvariable=self.toss_var, values=["Team A", "Team B"], state="readonly")
        self.cb_toss.pack(fill="x", pady=(5, 10))

        # Actions
        actions_grid = tk.Frame(root, bg=COLORS["bg_body"])
        actions_grid.pack(pady=(0, 16), fill="x", padx=25)
        actions_grid.columnconfigure(0, weight=1)
        actions_grid.columnconfigure(1, weight=1)

        self.btn_select_bowler = ModernButton(actions_grid, text="1. Select First Bowler", bg=COLORS["bg_input"], command=self.select_bowler_setup)
        self.btn_select_bowler.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=4)

        self.btn_select_batting = ModernButton(actions_grid, text="2. Select Opening Batters", bg=COLORS["bg_input"], command=self.select_batting_pair_setup)
        self.btn_select_batting.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=4)

        self.btn_start_match = ModernButton(actions_grid, text="START MATCH", bg=COLORS["accent"], fg="black", command=self.start_match)
        self.btn_start_match.config(state="disabled", bg=COLORS["bg_input"], fg="gray")
        self.btn_start_match.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=4)

        self.btn_save_players = ModernButton(actions_grid, text="SAVE PLAYER DETAILS", bg=COLORS["primary"], fg="white", command=self.save_player_details)
        self.btn_save_players.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=4)

        ModernButton(actions_grid, text="⚙ SETTINGS", bg=COLORS["bg_input"], command=self.open_settings).grid(
            row=2, column=0, sticky="ew", padx=(0, 5), pady=4
        )
        ModernButton(actions_grid, text="↺ RESET ALL", bg="#DC2626", fg="white", command=self.reset_all).grid(
            row=2, column=1, sticky="ew", padx=(5, 0), pady=4
        )
        
        self.bowler_selected = None
        self.batting_pair_selected = None

    def update_toss_options(self, *args):
        a = self.team_a_name.get() or "Team A"
        b = self.team_b_name.get() or "Team B"
        self.notebook.tab(self.tab1, text=f"{a} Players")
        self.notebook.tab(self.tab2, text=f"{b} Players")
        self.cb_toss.config(values=[a, b])
        if self.toss_var.get() not in [a, b]:
            self.toss_var.set(a)

    def resume_match(self):
        data = load_match_data()
        if not data:
            messagebox.showerror("Error", "Could not load saved match data.")
            return
        match = Match.from_dict(data)

        pending_inning_setup = self._is_inning_setup_pending(match)

        self.root.destroy()
        new_root = tk.Tk()
        app = CricketScorerApp(new_root, match, show_inning_setup_on_start=pending_inning_setup)
        new_root.mainloop()

    def _ordinal(self, value):
        if 10 <= (value % 100) <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
        return f"{value}{suffix}"

    def _match_total_innings(self, match):
        try:
            innings = int(match.settings.get("match_innings", 2))
        except (TypeError, ValueError):
            innings = 2
        return 4 if innings == 4 else 2

    def _is_inning_setup_pending(self, match):
        inning_start = (
            match.batting_team.overs_played == 0
            and match.balls_in_current_over == 0
            and len(match.current_over_balls) == 0
        )

        return (
            not match.match_over
            and match.current_innings > 1
            and inning_start
            and (match.striker is None or match.non_striker is None or match.current_bowler is None)
        )

    def _refresh_next_inning_button(self):
        if not self.btn_start_next_inning or not self.btn_start_next_inning.winfo_exists():
            return

        data = load_match_data()
        if not data:
            self.btn_start_next_inning.grid_remove()
            return

        try:
            match = Match.from_dict(data)
        except Exception:
            self.btn_start_next_inning.grid_remove()
            return

        if self._is_inning_setup_pending(match):
            self.btn_start_next_inning.config(text=f"START {self._ordinal(match.current_innings).upper()} INNING")
            self.btn_start_next_inning.grid()
            return

        next_inning = match.current_innings + 1
        if match.match_over or next_inning > self._match_total_innings(match):
            self.btn_start_next_inning.grid_remove()
            return

        self.btn_start_next_inning.config(text=f"START {self._ordinal(next_inning).upper()} INNING")
        self.btn_start_next_inning.grid()

    def start_next_inning_from_saved(self):
        data = load_match_data()
        if not data:
            messagebox.showerror("Error", "No saved match data found.", parent=self.root)
            return

        match = Match.from_dict(data)
        total_innings = self._match_total_innings(match)
        pending_inning_setup = self._is_inning_setup_pending(match)

        if match.match_over:
            messagebox.showinfo("Match Complete", "No next inning is available.", parent=self.root)
            self._refresh_next_inning_button()
            return

        if not pending_inning_setup:
            if match.current_innings >= total_innings:
                messagebox.showinfo("Match Complete", "No next inning is available.", parent=self.root)
                self._refresh_next_inning_button()
                return
            match.switch_innings()

        save_match_data(match)

        self._ensure_resume_button()
        self._refresh_next_inning_button()

        self.root.destroy()
        new_root = tk.Tk()
        app = CricketScorerApp(new_root, match, show_inning_setup_on_start=True)
        new_root.mainloop()

    def create_player_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        text = ModernText(frame, height=10)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        return text

    def _ensure_resume_button(self):
        if self.btn_resume and self.btn_resume.winfo_exists():
            if not self.btn_resume.winfo_ismapped():
                self.btn_resume.pack(pady=10)
            return

        self.btn_resume = ModernButton(self.header, text="RESUME SAVED MATCH", bg=COLORS["warning"], fg="black", command=self.resume_match)
        self.btn_resume.pack(pady=10)

    def _build_match_from_inputs(self):
        name_a = self.team_a_name.get() or "Team A"
        name_b = self.team_b_name.get() or "Team B"

        def get_names(widget):
            return [n.strip() for n in widget.get("1.0", "end-1c").split('\n') if n.strip()]

        players_a = get_names(self.text_p1)
        players_b = get_names(self.text_p2)

        if not players_a or not players_b:
            messagebox.showwarning("Missing Players", "Please add players for both teams before saving.", parent=self.root)
            return None

        pa = [Player(n) for n in players_a]
        pb = [Player(n) for n in players_b]
        
        team_a = Team(name_a, pa)
        team_b = Team(name_b, pb)
        
        batting_choice = self.toss_var.get()
        
        if batting_choice == name_b:
            match = Match(team_b, team_a)
        else:
            match = Match(team_a, team_b)

        match.settings.update({
            "total_overs": self.temp_settings.get("total_overs", 20),
            "balls_per_over": self.temp_settings.get("balls_per_over", 6),
            "wide_val": self.temp_settings.get("wide_val", 1),
            "noball_val": self.temp_settings.get("noball_val", 1),
            "max_players": self.temp_settings.get("max_players", 11),
            "match_innings": self.temp_settings.get("match_innings", 2),
            "wide_counts_as_ball": self.temp_settings.get("wide_counts_as_ball", False),
            "noball_counts_as_ball": self.temp_settings.get("noball_counts_as_ball", True),
            "last_man_stand": self.temp_settings.get("last_man_stand", False)
        })

        match.start_match()

        if self.bowler_selected:
            match.set_bowler(self.bowler_selected)
        if self.batting_pair_selected:
            match.set_striker(self.batting_pair_selected['striker'])
            match.set_non_striker(self.batting_pair_selected['non_striker'])

        return match

    def start_match(self):
        match = self._build_match_from_inputs()
        if not match:
            return

        save_match_data(match)

        self.root.destroy()
        new_root = tk.Tk()
        app = CricketScorerApp(new_root, match)
        new_root.mainloop()

    def save_player_details(self):
        match = self._build_match_from_inputs()
        if not match:
            return

        save_match_data(match)
        self._ensure_resume_button()
        self._refresh_next_inning_button()
        messagebox.showinfo("Saved", "Player details and match setup saved to JSON.", parent=self.root)

    def reset_all(self):
        top, frame = create_popup_window(self.root, 430, 260, "RESET ALL")

        content = tk.Frame(frame, bg=COLORS["bg_panel"])
        content.pack(fill="both", expand=True, padx=20, pady=5)

        tk.Label(
            content,
            text="Warning: this will erase all form data and saved JSON details.",
            bg=COLORS["bg_panel"],
            fg=COLORS["warning"],
            wraplength=360,
            justify="center",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 8))

        countdown_var = tk.StringVar(value="Confirm options will appear in 5 seconds...")
        tk.Label(
            content,
            textvariable=countdown_var,
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            font=FONT_SML
        ).pack(pady=(0, 12))

        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])

        def confirm_reset():
            self._perform_reset_all()
            top.destroy()

        ModernButton(button_frame, text="CONFIRM", bg="#DC2626", fg="white", command=confirm_reset).pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(
            side="right", fill="x", expand=True, padx=(5, 0)
        )

        def tick(seconds_left):
            if not top.winfo_exists():
                return
            if seconds_left > 0:
                countdown_var.set(f"Confirm options will appear in {seconds_left} seconds...")
                top.after(1000, lambda: tick(seconds_left - 1))
            else:
                countdown_var.set("You can now confirm or cancel.")
                button_frame.pack(side="bottom", pady=20, fill="x", padx=40)

        tick(5)

    def _perform_reset_all(self):
        reset_match_data()
        
        self.team_a_name.set("Team A")
        self.team_b_name.set("Team B")
        self.text_p1.delete("1.0", "end")
        self.text_p2.delete("1.0", "end")
        self.text_p1.insert("1.0", "\n".join([f"Player A{i+1}" for i in range(11)]))
        self.text_p2.insert("1.0", "\n".join([f"Player B{i+1}" for i in range(11)]))
        
        self.toss_var.set("Team A")
        self.bowler_selected = None
        self.batting_pair_selected = None
        self.btn_select_bowler.config(text="1. Select First Bowler", bg=COLORS["bg_input"], fg="white")
        self.btn_select_batting.config(text="2. Select Opening Batters", bg=COLORS["bg_input"], fg="white")
        self.btn_start_match.config(state="disabled", bg=COLORS["bg_input"], fg="gray")
        
        if self.btn_resume and self.btn_resume.winfo_exists():
            self.btn_resume.pack_forget()
        if self.btn_start_next_inning and self.btn_start_next_inning.winfo_exists():
            self.btn_start_next_inning.grid_remove()
        
        messagebox.showinfo("Reset", "All forms and saved match data erased!", parent=self.root)

    def open_settings(self):
        top, frame = create_popup_window(self.root, 400, 600, "MATCH SETTINGS")
        container = tk.Frame(frame, bg=COLORS["bg_panel"])
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        def add_field(label_text, value):
            row = tk.Frame(container, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, bg=COLORS["bg_panel"], fg="gray", width=20, anchor="w").pack(side="left")
            entry = ModernEntry(row)
            entry.insert(0, str(value))
            entry.pack(side="right", expand=True, fill="x")
            return entry
            
        def add_toggle(label_text, default_val):
            row = tk.Frame(container, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, bg=COLORS["bg_panel"], fg="gray", width=20, anchor="w").pack(side="left")
            t_var = tk.StringVar(value="ON" if default_val else "OFF")
            cb = ttk.Combobox(row, textvariable=t_var, values=["ON", "OFF"], state="readonly", font=FONT_SML)
            cb.pack(side="right", expand=True, fill="x")
            return t_var
            
        e_overs = add_field("Total Overs:", self.temp_settings.get("total_overs", 20))
        e_balls = add_field("Balls/Over:", self.temp_settings.get("balls_per_over", 6))
        e_wide = add_field("Wide Runs:", self.temp_settings.get("wide_val", 1))
        e_noball = add_field("No Ball Runs:", self.temp_settings.get("noball_val", 1))
        e_max_players = add_field("Max Players:", self.temp_settings.get("max_players", 11))
        
        row_inning = tk.Frame(container, bg=COLORS["bg_panel"])
        row_inning.pack(fill="x", pady=5)
        tk.Label(row_inning, text="Match Innings:", bg=COLORS["bg_panel"], fg="gray", width=20, anchor="w").pack(side="left")
        inning_var = tk.StringVar(value=str(self.temp_settings.get("match_innings", 2)))
        cb_inning = ttk.Combobox(row_inning, textvariable=inning_var, values=["2", "4"], state="readonly", font=FONT_SML)
        cb_inning.pack(side="right", expand=True, fill="x")
        
        e_wb_count = add_toggle("Wide Count as Ball:", self.temp_settings.get("wide_counts_as_ball", False))
        e_nb_count = add_toggle("No Ball Count as Ball:", self.temp_settings.get("noball_counts_as_ball", True))
        e_last_man = add_toggle("Last Man Stands:", self.temp_settings.get("last_man_stand", False))
        
        def save():
            try:
                self.temp_settings.update({
                    "total_overs": int(e_overs.get()),
                    "balls_per_over": int(e_balls.get()),
                    "wide_val": int(e_wide.get()),
                    "noball_val": int(e_noball.get()),
                    "max_players": int(e_max_players.get()),
                    "match_innings": int(inning_var.get()),
                    "wide_counts_as_ball": e_wb_count.get() == "ON",
                    "noball_counts_as_ball": e_nb_count.get() == "ON",
                    "last_man_stand": e_last_man.get() == "ON"
                })
                self.temp_settings.pop("target", None)
                    
                messagebox.showinfo("Success", "Settings saved for the new match!", parent=top)
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values", parent=top)

        btn_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        btn_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(btn_frame, text="SAVE", bg=COLORS["accent"], command=save).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(btn_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def select_bowler_setup(self):
        name_a = self.team_a_name.get() or "Team A"
        batting_choice = self.toss_var.get()
        
        if batting_choice == name_a:
            player_names = [n.strip() for n in self.text_p2.get("1.0", "end-1c").split('\n') if n.strip()]
        else:
            player_names = [n.strip() for n in self.text_p1.get("1.0", "end-1c").split('\n') if n.strip()]
        
        if not player_names: 
            messagebox.showwarning("No Players", "Please add players to the teams first.")
            return
        
        self.open_selector("Select First Bowler", player_names, self.set_bowler)

    def select_batting_pair_setup(self):
        name_a = self.team_a_name.get() or "Team A"
        batting_choice = self.toss_var.get()
        
        if batting_choice == name_a:
            player_names = [n.strip() for n in self.text_p1.get("1.0", "end-1c").split('\n') if n.strip()]
        else:
            player_names = [n.strip() for n in self.text_p2.get("1.0", "end-1c").split('\n') if n.strip()]
            
        if len(player_names) < 2: 
             messagebox.showwarning("No Players", "Need at least 2 players to bat.")
             return
        
        self.open_pair_selector("Select Openers", player_names, self.set_batters)

    def set_bowler(self, name):
        self.bowler_selected = name
        self.btn_select_bowler.config(text=f"Bowler: {name}", bg=COLORS["primary"], fg="white")
        self.check_start()

    def set_batters(self, s, ns):
        self.batting_pair_selected = {'striker': s, 'non_striker': ns}
        self.btn_select_batting.config(text=f"Batters: {s} & {ns}", bg=COLORS["primary"], fg="white")
        self.check_start()

    def check_start(self):
        if self.bowler_selected and self.batting_pair_selected:
            self.btn_start_match.config(state="normal", bg=COLORS["accent"], fg="black")

    def open_selector(self, title, items, callback):
        top = tk.Toplevel(self.root)
        top.geometry("300x250")
        top.configure(bg=COLORS["bg_body"])
        
        tk.Label(top, text=title, bg=COLORS["bg_body"], fg="white", font=("Segoe UI", 11)).pack(pady=10)
        
        sv = tk.StringVar(value=items[0])
        opt = tk.OptionMenu(top, sv, *items)
        opt.config(bg=COLORS["bg_input"], fg="white", highlightthickness=0)
        opt.pack(pady=10, fill="x", padx=30)
        
        def conf():
            callback(sv.get())
            top.destroy()
            
        ModernButton(top, text="CONFIRM", bg=COLORS["primary"], command=conf).pack(pady=20)

    def open_pair_selector(self, title, items, callback):
        top = tk.Toplevel(self.root)
        top.geometry("300x300")
        top.configure(bg=COLORS["bg_body"])
        
        tk.Label(top, text=title, bg=COLORS["bg_body"], fg="white", font=("Segoe UI", 11)).pack(pady=10)
        
        s = tk.StringVar(value=items[0])
        ns = tk.StringVar(value=items[1])
        
        tk.Label(top, text="Striker", bg=COLORS["bg_body"], fg="gray").pack()
        tk.OptionMenu(top, s, *items).pack(fill="x", padx=30)
        
        tk.Label(top, text="Non-Striker", bg=COLORS["bg_body"], fg="gray").pack()
        tk.OptionMenu(top, ns, *items).pack(fill="x", padx=30)
        
        def conf():
            if s.get() == ns.get(): return
            callback(s.get(), ns.get())
            top.destroy()
            
        ModernButton(top, text="CONFIRM", bg=COLORS["primary"], command=conf).pack(pady=20)
