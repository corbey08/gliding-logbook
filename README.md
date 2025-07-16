# Glider Pilot Logbook

A comprehensive desktop application for glider pilots to track and manage their flight logs. Built with Python and Tkinter, featuring a clean interface and robust data management.

## Features

### Flight Management
- **Add, Edit, Delete**: Complete CRUD operations for flight records
- **Comprehensive Data**: Track date, aircraft details, pilots, launch methods, duration, altitude, and cross-country distance
- **Notes**: Add detailed notes for each flight
- **Data Validation**: Ensures data integrity with proper format validation

### Search & Filter
- **Real-time Search**: Search across all flight data as you type
- **Category Filtering**: Filter by specific categories (Date, Aircraft Type, Registration, Pilot, etc.)
- **Clear Filters**: Easy reset of search criteria

### Statistics & Totals
- **Total Launches**: Count of all recorded flights
- **Total Hours**: Sum of all flight durations in H:MM format
- **Total Distance**: Sum of all cross-country distances in kilometers
- **Auto-updating**: Totals refresh automatically when data changes

### Data Management
- **SQLite Database**: Reliable local storage with automatic backup
- **Database Migration**: Seamless upgrades from older versions
- **Data Persistence**: All data stored locally on your computer

## Requirements

- Python 3.6 or higher
- Standard Python libraries (included with Python):
  - `tkinter` - GUI framework
  - `sqlite3` - Database management
  - `datetime` - Date/time handling
  - `os` - File system operations
  - `re` - Regular expressions for validation

## Installation

1. **Clone or download** this repository
2. **Ensure Python 3.6+** is installed on your system
3. **Run the application**:
   ```bash
   python glider_logbook.py
   ```

No additional dependencies need to be installed as the application uses only Python standard library modules.

## Usage

### Adding a Flight
1. Fill in the required fields (marked as required in validation):
   - Date
   - Aircraft Type
   - Aircraft Registration
   - Pilot in Command
   - Launch Method
   - Launch Site
2. Optionally add:
   - Instructor name
   - Landing site
   - Flight duration (H:MM format, e.g., "1:30")
   - Maximum altitude (feet)
   - Cross-country distance (kilometers)
   - Notes
3. Click "Add Flight"

### Editing a Flight
1. Select a flight from the list by clicking on it
2. The form will populate with the flight's data
3. Make your changes
4. Click "Update Flight"

### Searching and Filtering
1. Use the search box to find flights containing specific text
2. Select a category from the dropdown to search within specific fields
3. Use "Clear Search" to reset filters and show all flights

### Time Format
- Enter flight duration as **H:MM** (e.g., "1:30" for 1 hour 30 minutes)
- The application validates the format and will show an error for invalid entries

### Data Export
The application stores data in a SQLite database file (`glider_logbook.db`) in the same directory as the program. This file can be:
- Backed up for safety
- Opened with SQLite database tools for advanced queries
- Moved between computers to transfer your logbook

## Database Structure

The application uses a SQLite database with the following fields:
- **id**: Unique identifier (auto-generated)
- **date**: Flight date
- **aircraft_type**: Type of glider
- **aircraft_registration**: Aircraft registration/tail number
- **pilot_in_command**: Primary pilot name
- **instructor**: Instructor name (optional)
- **launch_method**: Method of launch (Winch, Aerotow, etc.)
- **launch_site**: Departure location
- **landing_site**: Landing location (optional)
- **flight_duration**: Duration in H:MM format
- **max_altitude**: Maximum altitude reached (feet)
- **cross_country_distance**: Distance flown (kilometers)
- **notes**: Additional notes
- **created_at**: Record creation timestamp

## File Structure

```
glider_logbook/
├── main.py                    # Main application file
├── glider_logbook.db          # SQLite database (created on first run)
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Backup and Data Safety

- The SQLite database file is created in the same directory as the program
- **Recommended**: Regularly backup the `glider_logbook.db` file
- The application includes database migration for updates
- Data is stored locally for privacy and offline access

## Troubleshooting

### Application won't start
- Ensure Python 3.6+ is installed
- Check that tkinter is available: `python -c "import tkinter"`
- On Linux, you may need to install tkinter: `sudo apt-get install python3-tk`

### Database errors
- Ensure the application has write permissions in its directory
- If the database becomes corrupted, delete `glider_logbook.db` to start fresh
- Check that the database file isn't opened in another program

### Time format errors
- Use H:MM format (e.g., "1:30", not "1.5" or "90 minutes")
- Hours can be 1-2 digits, minutes must be 2 digits (00-59)

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs or suggest features via GitHub issues
- Submit pull requests with improvements
- Share feedback and usage experiences

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python's standard library for maximum compatibility
- Designed for the gliding community to support safe flight logging
- Inspired by traditional paper logbooks used by glider pilots

---

**Happy Flying!** ✈️

For support or questions, please open an issue in the GitHub repository.
