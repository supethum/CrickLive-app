# CrickLive - Cricket Live Scoring Application

A Python-based desktop cricket scoring application with a graphical user interface for live match management and comprehensive statistics tracking.

## Features

- **Live Cricket Scoring**: Ball-by-ball scoring with real-time updates
- **Team Management**: Create and manage multiple teams with player rosters
- **Match Configuration**: Customizable match settings (overs, players, rules)
- **Comprehensive Statistics**: 
  - Batting stats (runs, balls faced, strike rate, boundaries)
  - Bowling stats (overs, runs conceded, wickets, economy rate)
  - Fielding and dismissal tracking
- **Data Persistence**: Automatic save/load functionality with JSON storage
- **User-Friendly Interface**: Intuitive Tkinter-based GUI
- **Multiple Dismissal Types**: Support for all standard cricket dismissals
- **Extras Handling**: Wide balls, no-balls, byes, and leg-byes

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- No additional external dependencies required

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cricketlive.git
   cd cricketlive
   ```

2. Run the application:
   ```bash
   python main.py
   ```
   
   Or on Windows, simply double-click `CrickLive.bat`

## Quick Start

1. **Launch the Application**: Run `python main.py` or double-click `CrickLive.bat`
2. **Setup Match**: Configure teams, players, and match settings
3. **Start Scoring**: Begin ball-by-ball scoring with the intuitive interface
4. **View Statistics**: Monitor live stats and match progress
5. **Save Data**: Match data is automatically saved to `match_data.json`

## Project Structure

```
cricketlive/
|
|--- main.py                 # Main entry point
|--- CrickLive.bat          # Windows launcher script
|--- match_data.json        # Match data storage
|--- match_live_snapshot.json # Live match snapshot
|--- .gitignore            # Git ignore file
|
|--- internal/             # Application modules
|    |--- gui.py           # GUI entry point
|    |--- gui_setup.py     # Match setup interface
|    |--- gui_scorer.py    # Live scoring interface
|    |--- gui_constants.py # UI constants and styles
|    |--- match_logic.py   # Core scoring engine
|    |--- models.py        # Data models (Player, Team, Match)
|    |--- storage.py       # Data persistence layer
|    |--- verify.py        # Data validation
|    |--- api_client.py    # API integration (future)
|    |--- logo.png         # Application logo
```

## Match Rules Supported

- **Limited Overs**: T20, ODI, and custom over formats
- **Standard Cricket Rules**: All conventional dismissal types
- **Extras**: Wide balls, no-balls, byes, leg-byes
- **Customizable Settings**: 
  - Runs per wide/no-ball
  - Whether extras count as balls
  - Maximum players per team
  - Last man standing option

## Data Models

### Player
- Unique ID generation
- Batting statistics (runs, balls, strike rate, boundaries)
- Bowling statistics (overs, wickets, economy, maidens)
- Dismissal tracking

### Match
- Innings management
- Ball-by-ball history
- Live score updates
- Settings configuration

## Usage Examples

### Starting a New Match
```python
# Launch via GUI - no code required
python main.py
```

### Match Data Format
```json
{
  "match_settings": {
    "total_overs": 20,
    "balls_per_over": 6,
    "wide_val": 2,
    "noball_val": 3
  },
  "team_a": {
    "name": "Team A",
    "players": [...]
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the existing documentation
- Review the code comments for detailed explanations

## Future Enhancements

- Web interface integration
- Cloud sync for match data
- Tournament management
- Advanced analytics dashboard
- Mobile companion app
- Live streaming integration

---

**CrickLive** - Making cricket scoring simple and professional!
