import tkinter as tk
from tkinter import ttk, messagebox
from internal.models import Player
from internal.storage import save_match_data
from internal.gui_constants import (
    COLORS, FONT_SML, FONT_BOLD, ModernButton, ModernEntry, 
    get_acronym, get_icons_dict, create_popup_window, create_btn_grid
)

class CricketScorerApp:
    def __init__(self, root, match, show_inning_setup_on_start=False):
        self.match = match
        self.root = root
        self.root.configure(bg=COLORS["bg_body"])
        
        self.match.gui_callback = self.show_2nd_inning_setup
        self.auto_save_enabled = True
        
        self.icons = get_icons_dict()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        app_width = int(screen_width)
        app_height = int(screen_height * 0.35) 
        
        self.root.geometry(f"{app_width}x{app_height}+0+0")
        self.root.title(f"{match.team_a.name} vs {match.team_b.name}")

        self.main_container = tk.Frame(root, bg=COLORS["bg_body"])
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.main_container.columnconfigure(0, weight=3) 
        self.main_container.columnconfigure(1, weight=3) 
        self.main_container.columnconfigure(2, weight=4) 
        self.main_container.rowconfigure(0, weight=1)

        self.panel_score = tk.Frame(self.main_container, bg=COLORS["bg_panel"])
        self.panel_score.grid(row=0, column=0, sticky="nsew", padx=5)
        
        self.panel_pitch = tk.Frame(self.main_container, bg=COLORS["bg_panel"])
        self.panel_pitch.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.panel_controls = tk.Frame(self.main_container, bg=COLORS["bg_panel"])
        self.panel_controls.grid(row=0, column=2, sticky="nsew", padx=5)
        
        self.setup_scoreboard_panel()
        self.setup_pitch_panel()
        self.setup_controls_panel()
        
        self.refresh_ui()

        if show_inning_setup_on_start and not self.match.match_over:
            self.root.after(150, self.show_start_next_inning_popup)

    def auto_save(self):
        if self.auto_save_enabled:
            save_match_data(self.match)

    def setup_scoreboard_panel(self):
        for widget in self.panel_score.winfo_children():
            widget.destroy()

        container = tk.Frame(self.panel_score, bg=COLORS["bg_card"], padx=20, pady=20)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        inner_frame = tk.Frame(container, bg=COLORS["bg_card"])
        inner_frame.pack(expand=True, fill="x")

        self.lbl_batting_team = tk.Label(inner_frame, text="TEAM NAME",
                                         font=("Segoe UI", 18, "bold"), bg=COLORS["bg_card"], fg=COLORS["primary"])
        self.lbl_batting_team.pack(anchor="center", pady=(0, 5))
        
        self.lbl_total_score = tk.Label(inner_frame, text="0/0",
                                        font=("Segoe UI", 56, "bold"), bg=COLORS["bg_card"], fg=COLORS["text_white"])
        self.lbl_total_score.pack(anchor="center", pady=0)
        
        stats_frame = tk.Frame(inner_frame, bg=COLORS["bg_card"])
        stats_frame.pack(anchor="center", pady=(15, 0), fill="x")
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        def create_stat_label(parent, text, col):
            lbl = tk.Label(parent, text=text, font=("Segoe UI", 12, "bold"), bg=COLORS["bg_card"], fg=COLORS["text_gray"])
            lbl.grid(row=0, column=col, sticky="ew")
            return lbl

        self.lbl_overs_display = create_stat_label(stats_frame, "OV: 0.0", 0)
        self.lbl_crr = create_stat_label(stats_frame, "CRR: 0.0", 1)
        self.lbl_target_display = create_stat_label(stats_frame, "1st INN", 2)
        
        self.lbl_overs_display.config(fg="white")
        self.lbl_crr.config(fg=COLORS["accent"])
        self.lbl_target_display.config(fg=COLORS["warning"])

    def setup_pitch_panel(self):
        container = tk.Frame(self.panel_pitch, bg=COLORS["bg_panel"])
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Batting HeadRow
        row_bat_head = tk.Frame(container, bg=COLORS["bg_panel"])
        row_bat_head.pack(fill="x", pady=(0, 5))
        
        self.lbl_batting_header = tk.Label(row_bat_head, text="BATTING", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_panel"], fg=COLORS["text_muted"], anchor="w")
        self.lbl_batting_header.pack(side="left")
        
        ModernButton(row_bat_head, text="⇄ Swap Batters", bg=COLORS["bg_input"], fg=COLORS["text_gray"],
                     font=("Segoe UI", 8), corner_radius=6, padx=6, pady=2,
                     command=self.change_batsmen).pack(side="right")

        row_s = tk.Frame(container, bg=COLORS["bg_panel"])
        row_s.pack(fill="x", pady=(5, 2))
        tk.Label(row_s, image=self.icons["bat"], bg=COLORS["bg_panel"]).pack(side="left")
        
        self.lbl_striker_name = tk.Label(row_s, text="Striker", font=("Segoe UI", 14, "bold"), bg=COLORS["bg_panel"], fg=COLORS["accent"])
        self.lbl_striker_name.pack(side="left", padx=5)
        
        self.lbl_striker_stats = tk.Label(row_s, text="4s:0 6s:0", font=("Segoe UI", 10), bg=COLORS["bg_panel"], fg=COLORS["text_gray"])
        self.lbl_striker_stats.pack(side="right", padx=10)

        self.lbl_striker_runs = tk.Label(row_s, text="0(0)", font=("Segoe UI", 14), bg=COLORS["bg_panel"], fg=COLORS["text_white"])
        self.lbl_striker_runs.pack(side="right")

        row_ns = tk.Frame(container, bg=COLORS["bg_panel"])
        row_ns.pack(fill="x", pady=(2, 5))
        tk.Label(row_ns, image=self.icons["bat"], bg=COLORS["bg_panel"]).pack(side="left")
        
        self.lbl_non_name = tk.Label(row_ns, text="Non-Striker", font=("Segoe UI", 11), bg=COLORS["bg_panel"], fg=COLORS["text_gray"])
        self.lbl_non_name.pack(side="left", padx=5)

        self.lbl_non_stats = tk.Label(row_ns, text="4s:0 6s:0", font=("Segoe UI", 10), bg=COLORS["bg_panel"], fg=COLORS["text_muted"])
        self.lbl_non_stats.pack(side="right", padx=10)

        self.lbl_non_runs = tk.Label(row_ns, text="0(0)", font=("Segoe UI", 11), bg=COLORS["bg_panel"], fg=COLORS["text_gray"])
        self.lbl_non_runs.pack(side="right")
        
        tk.Frame(container, height=1, bg=COLORS["border"]).pack(fill="x", pady=10)

        # Bowling Head Row
        row_bowl_head = tk.Frame(container, bg=COLORS["bg_panel"])
        row_bowl_head.pack(fill="x", pady=(0, 5))

        self.lbl_bowling_header = tk.Label(row_bowl_head, text="BOWLING", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_panel"], fg=COLORS["text_muted"], anchor="w")
        self.lbl_bowling_header.pack(side="left")
        
        ModernButton(row_bowl_head, text="⇄ Swap Bowler", bg=COLORS["bg_input"], fg=COLORS["text_gray"],
                     font=("Segoe UI", 8), corner_radius=6, padx=6, pady=2,
                     command=self.ask_new_bowler).pack(side="right")

        row_b = tk.Frame(container, bg=COLORS["bg_panel"])
        row_b.pack(fill="x", pady=5)
        tk.Label(row_b, image=self.icons["ball"], bg=COLORS["bg_panel"]).pack(side="left")
        
        self.lbl_bowler_name = tk.Label(row_b, text="Bowler", font=("Segoe UI", 12, "bold"), bg=COLORS["bg_panel"], fg=COLORS["warning"])
        self.lbl_bowler_name.pack(side="left", padx=5)
        
        self.lbl_bowler_figures = tk.Label(row_b, text="0-0 (0.0)", font=("Segoe UI", 12), bg=COLORS["bg_panel"], fg=COLORS["text_white"])
        self.lbl_bowler_figures.pack(side="right")

        self.lbl_current_over = tk.Label(container, text="This Over: -", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_panel"], fg=COLORS["text_gray"])
        self.lbl_current_over.pack(anchor="w", padx=(30, 0), pady=(2, 5))

        self.btn_scorecard = ModernButton(container, text="Full Scorecard", 
                                        bg="#27272A", fg="#A1A1AA", hover="#3F3F46", 
                                        font=("Segoe UI", 10, "bold"), 
                                        command=self.show_summary_popup)
        self.btn_scorecard.pack(side="bottom", pady=0)

    def setup_controls_panel(self):
        container = tk.Frame(self.panel_controls, bg=COLORS["bg_panel"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        grid_frame = tk.Frame(container, bg=COLORS["bg_panel"])
        grid_frame.pack(fill="both", expand=True)
        
        for i in range(4): grid_frame.columnconfigure(i, weight=1)
        for i in range(4): grid_frame.rowconfigure(i, weight=1)
        
        btn_runs_style = {"bg": "#3F3F46", "fg": "white", "hover": "#52525B"} 
        
        vals = [0, 1, 2, 3]
        for i, val in enumerate(vals):
            txt = "•" if val == 0 else str(val)
            ModernButton(grid_frame, text=txt, 
                        bg=btn_runs_style["bg"], hover=btn_runs_style["hover"], fg=btn_runs_style["fg"],
                        command=lambda v=val: self.process_ball(v),
                        font=("Segoe UI", 16, "bold"), corner_radius=12).grid(row=0, column=i, sticky="nsew", padx=4, pady=4)

        ModernButton(grid_frame, text="FOUR", bg="#6366F1", hover="#4F46E5", fg="white",
                    command=lambda: self.process_ball(4),
                    font=("Segoe UI", 16, "bold"), corner_radius=12).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)

        ModernButton(grid_frame, text="SIX", bg="#EC4899", hover="#DB2777", fg="white",
                    command=lambda: self.process_ball(6),
                    font=("Segoe UI", 16, "bold"), corner_radius=12).grid(row=1, column=2, columnspan=2, sticky="nsew", padx=4, pady=4)

        btn_extra_style = {"bg": "#F59E0B", "hover": "#D97706", "fg": "black"}
        btn_out_style = {"bg": "#EF4444", "hover": "#DC2626", "fg": "white"}

        ModernButton(grid_frame, text="WD", bg=btn_extra_style["bg"], hover=btn_extra_style["hover"], fg=btn_extra_style["fg"],
                    command=self.handle_wide,
                    font=("Segoe UI", 11, "bold"), corner_radius=8).grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        
        ModernButton(grid_frame, text="NB", bg=btn_extra_style["bg"], hover=btn_extra_style["hover"], fg=btn_extra_style["fg"],
                    command=self.handle_noball,
                    font=("Segoe UI", 11, "bold"), corner_radius=8).grid(row=2, column=1, sticky="nsew", padx=4, pady=4)
        
        ModernButton(grid_frame, text="EXT", bg=btn_extra_style["bg"], hover=btn_extra_style["hover"], fg=btn_extra_style["fg"],
                    command=self.handle_extra,
                    font=("Segoe UI", 11, "bold"), corner_radius=8).grid(row=2, column=2, sticky="nsew", padx=4, pady=4)
        
        ModernButton(grid_frame, text="OUT", bg=btn_out_style["bg"], hover=btn_out_style["hover"], fg=btn_out_style["fg"],
                    command=lambda: self.process_ball(0, is_wicket=True),
                    font=("Segoe UI", 12, "bold"), corner_radius=8).grid(row=2, column=3, sticky="nsew", padx=4, pady=4)

        action_frame = tk.Frame(grid_frame, bg=COLORS["bg_panel"])
        action_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=4)
        
        ModernButton(action_frame, text="↺ Undo", bg="#27272A", hover="#3F3F46", fg="#A1A1AA",
                    command=self.undo_last_action,
                    font=("Segoe UI", 10), corner_radius=8).pack(side="left", fill="both", expand=True, padx=2)

        ModernButton(action_frame, text="⚙ Settings", bg="#27272A", hover="#3F3F46", fg="#A1A1AA",
                    command=self.edit_match_settings,
                    font=("Segoe UI", 10), corner_radius=8).pack(side="left", fill="both", expand=True, padx=2)

        ModernButton(action_frame, text="👥 Teams", bg="#27272A", hover="#3F3F46", fg="#A1A1AA",
                    command=self.edit_teams_details,
                    font=("Segoe UI", 10), corner_radius=8).pack(side="left", fill="both", expand=True, padx=2)

        ModernButton(action_frame, text="☄ Overthrow", bg="#27272A", hover="#3F3F46", fg="#A1A1AA",
                    command=self.handle_overthrow,
                    font=("Segoe UI", 10), corner_radius=8).pack(side="left", fill="both", expand=True, padx=2)

        ModernButton(action_frame, text="⏭ End Inning", bg="#27272A", hover="#3F3F46", fg="#A1A1AA",
                command=self.request_end_inning,
                font=("Segoe UI", 10), corner_radius=8).pack(side="left", fill="both", expand=True, padx=2)

    def handle_extra(self):
        top, frame = create_popup_window(self.root, 400, 360, "EXTRAS")
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab: Byes
        tab_bye = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_bye, text="BYES")
        tk.Label(tab_bye, text="Select Bye Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        bye_var = tk.StringVar(value="1b")
        bye_opts = [{"label": f"{i}B", "value": f"{i}b"} for i in range(1, 8)]
        create_btn_grid(tab_bye, bye_opts, bye_var, cols=4)
        
        hint_bye = tk.Label(tab_bye, text="", bg=COLORS["bg_card"], fg=COLORS["accent"], font=FONT_BOLD, pady=5)
        hint_bye.pack(fill="x", padx=40, pady=10)
        def upd_bye(*a): 
            val = bye_var.get().replace('b','')
            hint_bye.config(text=f"Total Bye Runs: {val}")
        bye_var.trace_add("write", upd_bye)
        upd_bye()

        # Tab: Leg Byes
        tab_legbye = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_legbye, text="LEG BYES")
        tk.Label(tab_legbye, text="Select Leg Bye Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        lb_var = tk.StringVar(value="1lb")
        lb_opts = [{"label": f"{i}LB", "value": f"{i}lb"} for i in range(1, 8)]
        create_btn_grid(tab_legbye, lb_opts, lb_var, cols=4)
        
        hint_lb = tk.Label(tab_legbye, text="", bg=COLORS["bg_card"], fg=COLORS["accent"], font=FONT_BOLD, pady=5)
        hint_lb.pack(fill="x", padx=40, pady=10)
        def upd_lb(*a): 
            val = lb_var.get().replace('lb','')
            hint_lb.config(text=f"Total Leg Bye Runs: {val}")
        lb_var.trace_add("write", upd_lb)
        upd_lb()
        
        def confirm():
            active_tab = notebook.index(notebook.select())
            if active_tab == 0:
                r = int(bye_var.get().replace('b',''))
                self.process_ball(r, is_bye=True)
            else:
                r = int(lb_var.get().replace('lb',''))
                self.process_ball(r, is_leg_bye=True)
            top.destroy()
                
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=15, fill="x", padx=40)
        ModernButton(button_frame, text="OK", bg=COLORS["primary"], command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def edit_match_settings(self):
        top, frame = create_popup_window(self.root, 400, 620, "MATCH SETTINGS")
        container = tk.Frame(frame, bg=COLORS["bg_panel"])
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        def add_field(label_text, value):
            row = tk.Frame(container, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, bg=COLORS["bg_panel"], fg="gray", width=16, anchor="w").pack(side="left")
            entry = ModernEntry(row)
            entry.insert(0, str(value))
            entry.pack(side="right", expand=True, fill="x")
            return entry

        def add_toggle(label_text, default_val):
            row = tk.Frame(container, bg=COLORS["bg_panel"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label_text, bg=COLORS["bg_panel"], fg="gray", width=16, anchor="w").pack(side="left")
            t_var = tk.StringVar(value="ON" if default_val else "OFF")
            cb = ttk.Combobox(row, textvariable=t_var, values=["ON", "OFF"], state="readonly", font=FONT_SML)
            cb.pack(side="right", expand=True, fill="x")
            return t_var
            
        e_overs = add_field("Total Overs:", self.match.settings.get("total_overs", 20))
        e_balls = add_field("Balls/Over:", self.match.settings.get("balls_per_over", 6))
        e_wide = add_field("Wide Runs:", self.match.settings.get("wide_val", 1))
        e_noball = add_field("No Ball Runs:", self.match.settings.get("noball_val", 1))
        e_max_players = add_field("Max Players:", self.match.settings.get("max_players", 11))

        row_inning = tk.Frame(container, bg=COLORS["bg_panel"])
        row_inning.pack(fill="x", pady=5)
        tk.Label(row_inning, text="Match Innings:", bg=COLORS["bg_panel"], fg="gray", width=16, anchor="w").pack(side="left")
        inning_var = tk.StringVar(value=str(self.match.settings.get("match_innings", 2)))
        cb_inning = ttk.Combobox(row_inning, textvariable=inning_var, values=["2", "4"], state="readonly", font=FONT_SML)
        cb_inning.pack(side="right", expand=True, fill="x")

        e_wb_count = add_toggle("Wide as Ball:", self.match.settings.get("wide_counts_as_ball", False))
        e_nb_count = add_toggle("NoBall as Ball:", self.match.settings.get("noball_counts_as_ball", True))
        e_last_man = add_toggle("Last Man Stands:", self.match.settings.get("last_man_stand", False))
        
        cb_inning.configure(state="readonly")
        
        def save():
            try:
                self.match.settings.update({
                    "total_overs": int(e_overs.get()),
                    "balls_per_over": int(e_balls.get()),
                    "wide_val": int(e_wide.get()),
                    "noball_val": int(e_noball.get()),
                    "max_players": int(e_max_players.get()),
                    "match_innings": int(inning_var.get()),
                    "wide_counts_as_ball": e_wb_count.get() == "ON",
                    "noball_counts_as_ball": e_nb_count.get() == "ON",
                    "last_man_stand": e_last_man.get() == "ON",
                })
                self.refresh_ui()
                self.auto_save()
                messagebox.showinfo("Success", "Settings updated and saved to JSON.", parent=top)
                top.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input values", parent=top)

        btn_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        btn_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(btn_frame, text="SUBMIT AND SAVE", bg=COLORS["accent"], command=save).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(btn_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def edit_teams_details(self):
        top, frame = create_popup_window(self.root, 500, 650, "EDIT TEAMS DETAILS")
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        def create_team_tab(team):
            tab = tk.Frame(notebook, bg=COLORS["bg_body"])
            notebook.add(tab, text=team.name)
            
            tk.Label(tab, text="Team Name:", bg=COLORS["bg_body"], fg="gray").pack(anchor="w", padx=10, pady=(10, 0))
            name_var = tk.StringVar(value=team.name)
            name_entry = ModernEntry(tab)
            name_entry.entry.config(textvariable=name_var)
            name_entry.pack(fill="x", padx=10, pady=(0, 10))
            
            tk.Label(tab, text="Players:", bg=COLORS["bg_body"], fg="gray").pack(anchor="w", padx=10)
            
            container = tk.Frame(tab, bg=COLORS["bg_body"])
            container.pack(fill="both", expand=True, padx=10, pady=5)
            
            canvas = tk.Canvas(container, bg=COLORS["bg_body"], highlightthickness=0)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_body"])
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=420)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            player_rows = []

            def delete_player(row_data):
                row_data["frame"].destroy()
                row_data["deleted"] = True
                
            def add_player_row(player=None):
                row = tk.Frame(scrollable_frame, bg=COLORS["bg_body"])
                row.pack(fill="x", pady=2)
                
                var = tk.StringVar(value=player.name if player else "")
                entry = ModernEntry(row)
                entry.entry.config(textvariable=var)
                entry.pack(side="left", fill="x", expand=True)
                
                btn_del = tk.Button(row, text="✕", bg=COLORS["bg_body"], fg="red", relief="flat", command=lambda: delete_player(row_data))
                btn_del.pack(side="right", padx=5)
                
                row_data = {"player": player, "var": var, "frame": row, "deleted": False}
                player_rows.append(row_data)

            for p in team.players: add_player_row(p)
            btn_add = ModernButton(tab, text="+ Add Player", bg=COLORS["bg_input"], fg=COLORS["accent"], command=lambda: add_player_row(None))
            btn_add.pack(fill="x", padx=10, pady=10)
                
            return name_var, player_rows

        name_var_a, rows_a = create_team_tab(self.match.team_a)
        name_var_b, rows_b = create_team_tab(self.match.team_b)
        
        def save():
            def update_team(team, name_var, rows):
                team.name = name_var.get().strip() or team.name
                new_players = []
                for r in rows:
                    if r["deleted"]: continue
                    name = r["var"].get().strip()
                    if not name: continue
                    if r["player"]:
                        r["player"].name = name
                        new_players.append(r["player"])
                    else:
                        new_players.append(Player(name))
                team.players = new_players
            
            update_team(self.match.team_a, name_var_a, rows_a)
            update_team(self.match.team_b, name_var_b, rows_b)
            self.refresh_ui()
            self.auto_save()
            messagebox.showinfo("Success", "Teams updated!")
            top.destroy()
            
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(button_frame, text="SUBMIT AND SAVE", bg=COLORS["accent"], command=save).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def handle_wide(self):
        top, frame = create_popup_window(self.root, 400, 300, "WIDE BALL")
        tk.Label(frame, text="Select Wide Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        
        wide_var = tk.StringVar(value="wd")
        options = [{"label": "WD", "value": "wd"}] + [{"label": f"{i}WD", "value": f"{i}wd"} for i in range(1, 7)]
        create_btn_grid(frame, options, wide_var, cols=4)
        
        hint_lbl = tk.Label(frame, text="", bg=COLORS["bg_card"], fg=COLORS["accent"], font=FONT_BOLD, pady=5)
        hint_lbl.pack(fill="x", padx=40, pady=10)
        
        def update_hint(*args):
            v = wide_var.get()
            extra = 0 if v == "wd" else int(v.replace("wd", ""))
            rule_val = self.match.settings.get("wide_val", 1)
            hint_lbl.config(text=f"{extra} (Extra Runs) + {rule_val} (Wide Runs) = {extra+rule_val} Total Runs")
            
        wide_var.trace_add("write", update_hint)
        update_hint()
        
        def confirm():
            v = wide_var.get()
            extra = 0 if v == "wd" else int(v.replace("wd", ""))
            self.process_ball(extra, is_wide=True)
            top.destroy()
                
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(button_frame, text="OK", bg=COLORS["primary"], command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def handle_overthrow(self):
        top, frame = create_popup_window(self.root, 500, 550, "OVERTHROW")
        
        canvas = tk.Canvas(frame, bg=COLORS["bg_panel"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_panel"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Did batsman complete runs?", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(5, 2))
        base_var = tk.StringVar(value="0")
        base_opts = [{"label": str(i), "value": str(i)} for i in range(7)]
        create_btn_grid(scrollable_frame, base_opts, base_var, cols=7)
        
        tk.Label(scrollable_frame, text="Overthrow runs?", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(15, 2))
        over_var = tk.StringVar(value="4")
        over_opts = [{"label": str(i), "value": str(i)} for i in range(1, 7)]
        create_btn_grid(scrollable_frame, over_opts, over_var, cols=6)
        
        tk.Label(scrollable_frame, text="Is that Bye or Leg Bye? (Optional)", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(15, 2))
        extra_var = tk.StringVar(value="none")
        extra_opts = [{"label": "NONE", "value": "none"}, {"label": "BYES", "value": "bye"}, {"label": "LEG BYES", "value": "legbye"}]
        create_btn_grid(scrollable_frame, extra_opts, extra_var, cols=3)
        
        tk.Label(scrollable_frame, text="Is that No Ball or Wide? (Optional)", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(15, 2))
        ball_var = tk.StringVar(value="none")
        ball_opts = [{"label": "NONE", "value": "none"}, {"label": "NO BALL", "value": "noball"}, {"label": "WIDE", "value": "wide"}]
        create_btn_grid(scrollable_frame, ball_opts, ball_var, cols=3)
        
        def confirm():
            base = int(base_var.get())
            over = int(over_var.get())
            total = base + over
            ev = extra_var.get()
            bv = ball_var.get()
            
            is_bye = (ev == "bye")
            is_lbye = (ev == "legbye")
            is_nb = (bv == "noball")
            is_wd = (bv == "wide")
            
            self.process_ball(total, is_wide=is_wd, is_noball=is_nb, is_bye=is_bye, is_leg_bye=is_lbye)
            top.destroy()
                
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=15, fill="x", padx=40)
        ModernButton(button_frame, text="OK", bg=COLORS["primary"], command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def handle_noball(self):
        top, frame = create_popup_window(self.root, 400, 420, "NO BALL")
        
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        hint_lbl = tk.Label(frame, text="", bg=COLORS["bg_card"], fg=COLORS["accent"], font=FONT_BOLD, pady=5)
        hint_lbl.pack(fill="x", padx=40, pady=10)

        # Tab: NB
        tab_nb = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_nb, text="NB")
        tk.Label(tab_nb, text="Select No Ball Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        nb_var = tk.StringVar(value="nb")
        nb_opts = [{"label": "NB", "value": "nb"}] + [{"label": f"{i}NB", "value": f"{i}nb"} for i in range(1, 8)]
        create_btn_grid(tab_nb, nb_opts, nb_var, cols=4)
        
        def upd_nb(*a):
            v = nb_var.get()
            extra = 0 if v == "nb" else int(v.replace("nb", ""))
            rval = self.match.settings.get("noball_val", 1)
            hint_lbl.config(text=f"{extra} (Off Bat) + {rval} (No Ball Runs) = {extra+rval} Total")
        nb_var.trace_add("write", upd_nb)

        # Tab: Byes
        tab_bye = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_bye, text="BYES")
        tk.Label(tab_bye, text="Select Bye + No Ball Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        bnb_var = tk.StringVar(value="1b+nb")
        bnb_opts = [{"label": f"{i}B+NB", "value": f"{i}b+nb"} for i in range(1, 8)]
        create_btn_grid(tab_bye, bnb_opts, bnb_var, cols=4)
        
        def upd_bye(*a):
            v = bnb_var.get()
            extra = int(v.replace("b+nb", ""))
            rval = self.match.settings.get("noball_val", 1)
            hint_lbl.config(text=f"{extra} (Byes) + {rval} (No Ball Runs) = {extra+rval} Total")
        bnb_var.trace_add("write", upd_bye)

        # Tab: Leg Byes
        tab_lb = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_lb, text="LEGBYES")
        tk.Label(tab_lb, text="Select Leg Bye + No Ball Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        lnb_var = tk.StringVar(value="1lb+nb")
        lnb_opts = [{"label": f"{i}LB+NB", "value": f"{i}lb+nb"} for i in range(1, 8)]
        create_btn_grid(tab_lb, lnb_opts, lnb_var, cols=4)
        
        def upd_lb(*a):
            v = lnb_var.get()
            extra = int(v.replace("lb+nb", ""))
            rval = self.match.settings.get("noball_val", 1)
            hint_lbl.config(text=f"{extra} (Leg Byes) + {rval} (No Ball Runs) = {extra+rval} Total")
        lnb_var.trace_add("write", upd_lb)

        def on_tab_change(event):
            idx = notebook.index(notebook.select())
            if idx == 0: upd_nb()
            elif idx == 1: upd_bye()
            elif idx == 2: upd_lb()
        notebook.bind("<<NotebookTabChanged>>", on_tab_change)
        upd_nb()
        
        def confirm():
            idx = notebook.index(notebook.select())
            if idx == 0:
                v = nb_var.get()
                extra = 0 if v == "nb" else int(v.replace("nb", ""))
                self.process_ball(extra, is_noball=True)
            elif idx == 1:
                v = bnb_var.get()
                extra = int(v.replace("b+nb", ""))
                self.process_ball(extra, is_noball=True, is_bye=True)
            elif idx == 2:
                v = lnb_var.get()
                extra = int(v.replace("lb+nb", ""))
                self.process_ball(extra, is_noball=True, is_leg_bye=True)
            top.destroy()
                
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=15, fill="x", padx=40)
        ModernButton(button_frame, text="OK", bg=COLORS["primary"], command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def undo_last_action(self):
        if self.match.undo():
            self.refresh_ui()
            self.auto_save()
        else:
            messagebox.showinfo("Undo", "Nothing to undo!")

    def process_ball(self, runs, is_wicket=False, is_wide=False, is_noball=False, is_bye=False, is_leg_bye=False):
        if self.match.match_over: return
        if not self.match.current_bowler:
            if not self.ask_new_bowler(): return

        self.match.snapshot()

        if is_wicket:
            d_info = self.ask_dismissal_type()
            if not d_info["type"]: 
                self.match.undo()
                return 
            
            self.match.record_ball(runs, is_wicket, is_wide, is_noball, is_bye, is_leg_bye,
                                 dismissal_type=d_info["type"],
                                 dismissed_player_name=d_info["player"],
                                 dismissed_by_name=d_info["by_player"])
            self.refresh_ui()
            if (self.match.striker is None or self.match.non_striker is None) and not self.match.match_over:
                 self.ask_next_batsman()
        else:
            self.match.record_ball(runs, is_wicket=is_wicket, is_wide=is_wide, is_noball=is_noball,
                                   is_bye=is_bye, is_leg_bye=is_leg_bye)
        
        self.refresh_ui()
        self.auto_save()
        
        if self.match.inning_complete_pending and not self.match.match_over:
            self._handle_innings_transition("Innings completed.")
        
        if self.match.current_bowler is None and not self.match.match_over and not self.match.inning_complete_pending:
            self.ask_new_bowler()
            
        if self.match.match_over:
             messagebox.showinfo("Game Over", f"Winner: {self.match.winner}")
             self.auto_save()
             self.refresh_ui()

    def _total_innings(self):
        try:
            innings = int(self.match.settings.get("match_innings", 2))
        except (TypeError, ValueError):
            innings = 2
        return 4 if innings == 4 else 2

    def _ordinal(self, value):
        if 10 <= (value % 100) <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
        return f"{value}{suffix}"

    def _handle_innings_transition(self, notice_text):
        messagebox.showinfo("Innings Over", notice_text)
        self.match.switch_innings()
        self.refresh_ui()
        self.auto_save()
        self.show_start_next_inning_popup()

    def show_start_next_inning_popup(self):
        top, frame = create_popup_window(self.root, 380, 260, "START NEXT INNING")
        should_start = {"value": False}

        inning_text = self._ordinal(self.match.current_innings).upper()
        tk.Label(
            frame,
            text=f"{inning_text} INNING READY",
            bg=COLORS["bg_panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 4))

        tk.Label(
            frame,
            text=f"Batting Team: {self.match.batting_team.name}",
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            font=FONT_SML
        ).pack(pady=(0, 4))

        tk.Label(
            frame,
            text=f"Bowling Team: {self.match.bowling_team.name}",
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            font=FONT_SML
        ).pack(pady=(0, 15))

        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)

        def on_start():
            should_start["value"] = True
            top.destroy()

        ModernButton(button_frame, text="START", bg=COLORS["accent"], fg="black", command=on_start).pack(
            side="left", fill="x", expand=True
        )
        self.root.wait_window(top)

        if should_start["value"]:
            self.show_2nd_inning_setup()

    def request_end_inning(self):
        if self.match.match_over:
            return

        top, frame = create_popup_window(self.root, 430, 260, "END INNING")

        content = tk.Frame(frame, bg=COLORS["bg_panel"])
        content.pack(fill="both", expand=True, padx=20, pady=5)

        tk.Label(
            content,
            text="Warning: ending innings now cannot be auto-recovered.",
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

        def confirm_end():
            self.match.snapshot()
            ended = self.match.force_end_innings()
            top.destroy()
            if not ended:
                return

            self.refresh_ui()
            self.auto_save()

            if self.match.inning_complete_pending and not self.match.match_over:
                self._handle_innings_transition("Innings ended by user.")
            elif self.match.match_over:
                messagebox.showinfo("Game Over", f"Winner: {self.match.winner}")
                self.refresh_ui()
                self.auto_save()

        ModernButton(button_frame, text="CONFIRM", bg="#DC2626", fg="white", command=confirm_end).pack(
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

    def ask_dismissal_type(self):
        top, frame = create_popup_window(self.root, 480, 550, "WICKET TYPE")
        
        canvas = tk.Canvas(frame, bg=COLORS["bg_panel"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg_panel"])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable, text="Dismissal Type:", bg=COLORS["bg_panel"], fg="gray", font=FONT_BOLD).pack(pady=(10, 5))
        
        notebook = ttk.Notebook(scrollable)
        notebook.pack(fill="x", expand=True, padx=10, pady=5)
        
        tab_common = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_common, text="COMMON")
        
        tab_rare = tk.Frame(notebook, bg=COLORS["bg_panel"])
        notebook.add(tab_rare, text="RARE")
        
        type_var = tk.StringVar(value="Bowled")
        common_opts = [{"label": "Bowled", "value": "Bowled"}, {"label": "Caught", "value": "Caught"}, 
                       {"label": "LBW", "value": "LBW"}, {"label": "Run Out", "value": "Run Out"}, 
                       {"label": "Stumped", "value": "Stumped"}]
        rare_opts = [{"label": "Hit Wicket", "value": "Hit Wicket"}, {"label": "Retired Hurt", "value": "Retired Hurt"},
                     {"label": "Retired Out", "value": "Retired Out"}, {"label": "Obstructing", "value": "Obstructing the field"},
                     {"label": "Hit Ball Twice", "value": "Hit the Ball Twice"}, {"label": "Timed Out", "value": "Timed Out"},
                     {"label": "Absent", "value": "Absent"}, {"label": "Mankad", "value": "Mankad"}]
                     
        create_btn_grid(tab_common, common_opts, type_var, cols=2)
        create_btn_grid(tab_rare, rare_opts, type_var, cols=2)
        
        details_frame = tk.Frame(scrollable, bg=COLORS["bg_panel"])
        details_frame.pack(fill="x", pady=10)
        tk.Label(details_frame, text="Who is out?", bg=COLORS["bg_panel"], fg="gray").pack(pady=(5,2))
        
        s_name = self.match.striker.name if self.match.striker else "Striker"
        ns_name = self.match.non_striker.name if self.match.non_striker else "Non-Striker"
        player_var = tk.StringVar(value=s_name)
        
        whos_out_opts = [{"label": f"STRIKER\n{s_name}", "value": s_name}]
        if self.match.non_striker:
            whos_out_opts.append({"label": f"NON-STRIKER\n{ns_name}", "value": ns_name})
        create_btn_grid(details_frame, whos_out_opts, player_var, cols=2)
        
        f_by_row = tk.Frame(scrollable, bg=COLORS["bg_panel"])
        f_by_row.pack(fill="x", padx=10, pady=10)
        tk.Label(f_by_row, text="Fielder/Assist (opt):", bg=COLORS["bg_panel"], fg="gray").pack(side="left")
        
        fielders = [""] + [p.name for p in self.match.bowling_team.players]
        combo_by_var = tk.StringVar(value="")
        cb_by = ttk.Combobox(f_by_row, textvariable=combo_by_var, values=fielders, state="readonly", font=FONT_SML)
        cb_by.pack(side="left", padx=10, fill="x", expand=True)

        result = {"type": None, "player": None, "by_player": None}
        def on_done():
            result["type"] = type_var.get()
            result["player"] = player_var.get()
            result["by_player"] = combo_by_var.get()
            top.destroy()
            
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=10, fill="x", padx=40)
        ModernButton(button_frame, text="NEXT / CONFIRM", bg=COLORS["danger"], command=on_done).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        self.root.wait_window(top)
        return result

    def ask_next_batsman(self):
        bat_t = self.match.batting_team
        c_non = self.match.non_striker
        avail = [p.name for p in bat_t.players if not p.is_out and (c_non is None or p.name != c_non.name)]
        if not avail: return

        top, frame = create_popup_window(self.root, 280, 220, "NEXT BATSMAN")
        selected = tk.StringVar(value=avail[0])
        cb = ttk.Combobox(frame, textvariable=selected, values=avail, state="readonly", font=FONT_SML)
        cb.pack(pady=15, fill="x", padx=30)
        
        def on_conf():
            self.match.set_new_batsman(selected.get())
            top.destroy()
            self.refresh_ui()
            self.auto_save()
            
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(button_frame, text="SEND IN", bg=COLORS["accent"], fg="black", command=on_conf).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))
        self.root.wait_window(top)

    def ask_new_bowler(self):
        bowl_t = self.match.bowling_team
        players = [p.name for p in bowl_t.players]
        top, frame = create_popup_window(self.root, 280, 220, "SELECT BOWLER")
        selected = tk.StringVar(value=players[0])
        cb = ttk.Combobox(frame, textvariable=selected, values=players, state="readonly", font=FONT_SML)
        cb.pack(pady=15, fill="x", padx=30)
        
        def confirm():
            self.match.set_bowler(selected.get())
            top.destroy()
            self.refresh_ui()
            self.auto_save()
            
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(button_frame, text="CONFIRM", bg=COLORS["primary"], command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))
        self.root.wait_window(top)
        return True

    def change_batsmen(self, title="CHANGE BATSMEN"):
        batting_team = self.match.batting_team
        available = [p.name for p in batting_team.players if not p.is_out]
        if len(available) < 2: return

        top, frame = create_popup_window(self.root, 300, 280, title)
        s_var = tk.StringVar(value=available[0])
        ns_var = tk.StringVar(value=available[1] if len(available)>1 else available[0])

        for lbl, var in [("Striker", s_var), ("Non-Striker", ns_var)]:
            tk.Label(frame, text=lbl, bg=COLORS["bg_panel"], fg=COLORS["text_gray"]).pack(pady=(10,0))
            cb = ttk.Combobox(frame, textvariable=var, values=available, state="readonly", font=FONT_SML)
            cb.pack(fill="x", padx=30)
        
        def confirm():
            if s_var.get() == ns_var.get():
                messagebox.showerror("Error", "Same player selected twice!")
                return
            self.match.set_striker(s_var.get())
            self.match.set_non_striker(ns_var.get())
            top.destroy(); self.refresh_ui(); self.auto_save()
            
        button_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        button_frame.pack(side="bottom", pady=20, fill="x", padx=40)
        ModernButton(button_frame, text="UPDATE", bg=COLORS["accent"], fg="black", command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ModernButton(button_frame, text="CANCEL", bg=COLORS["bg_input"], fg="gray", command=top.destroy).pack(side="right", fill="x", expand=True, padx=(5, 0))
        self.root.wait_window(top)

    def show_summary_popup(self):
        top = tk.Toplevel(self.root)
        top.title("Scorecard")
        top.configure(bg=COLORS["bg_body"])
        w = int(self.root.winfo_screenwidth() * 0.5)
        h = int(self.root.winfo_screenheight() * 0.6)
        top.geometry(f"{w}x{h}")
        
        container = tk.Frame(top, bg=COLORS["bg_body"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        status_frame = tk.Frame(container, bg=COLORS["bg_card"], pady=10, padx=10)
        status_frame.pack(fill="x", pady=(0, 10))
        tk.Label(status_frame, text="CURRENT MATCH STATUS", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_card"], fg=COLORS["text_gray"]).pack()
        
        s, ns = self.match.striker, self.match.non_striker
        s_txt = f"{s.name}: {s.runs_scored}({s.balls_faced})" if s else "No Striker"
        ns_txt = f"{ns.name}: {ns.runs_scored}({ns.balls_faced})" if ns else "No Non-Striker"
        tk.Label(status_frame, text=f"🏏 {s_txt}   |   {ns_txt}", font=("Segoe UI", 12, "bold"), bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=2)
        
        b = self.match.current_bowler
        b_txt = f"{b.name}: {b.wickets_taken}-{b.runs_conceded} ({b.overs_bowled})" if b else "No Bowler"
        tk.Label(status_frame, text=f"⚾ {b_txt}", font=("Segoe UI", 11), bg=COLORS["bg_card"], fg=COLORS["warning"]).pack(pady=2)
        
        tk.Label(container, text=f"{self.match.batting_team.name}", font=FONT_BOLD, bg=COLORS["bg_body"], fg=COLORS["accent"]).pack(pady=5)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["bg_card"], foreground="white", fieldbackground=COLORS["bg_card"], borderwidth=0)
        style.configure("Treeview.Heading", background=COLORS["bg_panel"], foreground="white", relief="flat")
        
        cols = ("Name", "R", "B", "4s", "6s")
        tree = ttk.Treeview(container, columns=cols, show="headings", height=8)
        tree.column("Name", width=100); tree.heading("Name", text="Name")
        for c in cols[1:]: 
            tree.column(c, width=30, anchor="center")
            tree.heading(c, text=c)
        tree.pack(fill="x", pady=5)
        
        for p in self.match.batting_team.players:
            if p.balls_faced > 0 or p.is_out or p == s or p == ns:
                disp = f"{p.name}*" if not p.is_out and (p==s or p==ns) else (f"{p.name} (out)" if p.is_out else p.name)
                tree.insert("", "end", values=(disp, p.runs_scored, p.balls_faced, p.fours, p.sixes))

        tk.Label(container, text=f"{self.match.bowling_team.name}", font=FONT_BOLD, bg=COLORS["bg_body"], fg=COLORS["warning"]).pack(pady=10)
        b_cols = ("Name", "O", "R", "W")
        btree = ttk.Treeview(container, columns=b_cols, show="headings", height=5)
        btree.column("Name", width=100); btree.heading("Name", text="Name")
        for c in b_cols[1:]: 
            btree.column(c, width=40, anchor="center")
            btree.heading(c, text=c)
        btree.pack(fill="x", pady=5)
        
        for p in self.match.bowling_team.players:
            if p.balls_bowled_count > 0:
                btree.insert("", "end", values=(p.name, p.overs_bowled, p.runs_conceded, p.wickets_taken))
        
        ModernButton(container, text="CLOSE", bg=COLORS["bg_input"], command=top.destroy).pack(pady=15, fill="x", padx=50)

    def show_2nd_inning_setup(self):
        inning_text = self._ordinal(self.match.current_innings).upper()
        self.change_batsmen(title=f"SELECT {inning_text} INNING OPENERS")
        self.ask_new_bowler()

    def refresh_ui(self):
        try:
            batting = self.match.batting_team
            bowling = self.match.bowling_team
            innings_start_total = getattr(self.match, "current_innings_start_total", 0)
            innings_runs = batting.total_runs - innings_start_total
            if innings_runs < 0:
                innings_runs = batting.total_runs
            
            self.lbl_batting_team.config(text=get_acronym(batting.name))
            if hasattr(self, 'lbl_batting_header'):
                self.lbl_batting_header.config(text=f"BATTING: {get_acronym(batting.name)}")
            if hasattr(self, 'lbl_bowling_header'):
                self.lbl_bowling_header.config(text=f"BOWLING: {get_acronym(bowling.name)}")
                
            self.lbl_total_score.config(text=f"{innings_runs}/{batting.wickets_lost}")
            self.lbl_overs_display.config(text=f"OV: {batting.overs_played}.{self.match.balls_in_current_over}")
            
            total_overs_decimal = batting.overs_played + (self.match.balls_in_current_over / self.match.settings.get("balls_per_over", 6))
            crr = innings_runs / total_overs_decimal if total_overs_decimal > 0 else 0
            self.lbl_crr.config(text=f"CRR: {crr:.2f}")

            total_innings = self._total_innings()
            current_innings = self.match.current_innings

            if total_innings == 4 and current_innings == 2:
                self.lbl_target_display.config(text="2ND INNINGS", fg=COLORS["warning"])
            elif total_innings == 4 and current_innings == 3:
                self.lbl_target_display.config(text=f"INN1+INN3: {batting.total_runs}", fg=COLORS["warning"])
            elif self.match.target is not None:
                needed = (self.match.target + 1) - batting.total_runs
                if needed > 0:
                    self.lbl_target_display.config(text=f"TARGET: {self.match.target+1} • NEED: {needed}", fg=COLORS["warning"])
                else:
                    self.lbl_target_display.config(text="WINNER!", fg=COLORS["accent"])
            else:
                label = f"{self._ordinal(current_innings).upper()} INNINGS"
                self.lbl_target_display.config(text=label, fg=COLORS["warning"])

            s, ns, b = self.match.striker, self.match.non_striker, self.match.current_bowler

            if s:
                self.lbl_striker_name.config(text=f"{s.name}*")
                self.lbl_striker_runs.config(text=f"{s.runs_scored}({s.balls_faced})")
                self.lbl_striker_stats.config(text=f"4s: {s.fours}  6s: {s.sixes}")
            else:
                self.lbl_striker_name.config(text="Wicket")
                self.lbl_striker_runs.config(text="--")
                self.lbl_striker_stats.config(text="4s: -  6s: -")

            if ns:
                self.lbl_non_name.config(text=ns.name)
                self.lbl_non_runs.config(text=f"{ns.runs_scored}({ns.balls_faced})")
                self.lbl_non_stats.config(text=f"4s: {ns.fours}  6s: {ns.sixes}")
            else:
                self.lbl_non_name.config(text="--")
                self.lbl_non_runs.config(text="--")
                self.lbl_non_stats.config(text="4s: -  6s: -")
                
            if b:
                self.lbl_bowler_name.config(text=b.name)
                self.lbl_bowler_figures.config(text=f"{b.wickets_taken}-{b.runs_conceded} ({b.overs_bowled})")
            else:
                self.lbl_bowler_name.config(text="No Bowler")
                self.lbl_bowler_figures.config(text="--")

            over_display = "This Over: " + " ".join(self.match.current_over_balls) if self.match.current_over_balls else "This Over: -"
            self.lbl_current_over.config(text=over_display)
            self.btn_scorecard.config(text=f"Full Scorecard: {batting.name} vs {bowling.name}")
        except tk.TclError:
            pass
