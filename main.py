import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import sqlite3
from datetime import datetime
import os
import re

class GliderLogbook:
    def __init__(self, root):
        self.root = root
        self.root.title("Glider Pilot Logbook")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.init_database()
        
        # Create GUI
        self.create_widgets()
        
        # Load data
        self.load_data()
        self.update_totals()
    
    def init_database(self):
        """Initialize SQLite database and create table if it doesn't exist"""
        self.conn = sqlite3.connect('glider_logbook.db')
        self.cursor = self.conn.cursor()
        
        # Check if table exists and if it has the old structure
        self.cursor.execute("PRAGMA table_info(flights)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        if 'cross_country_distance' not in columns:
            # Create new table with updated structure
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    aircraft_type TEXT NOT NULL,
                    aircraft_registration TEXT NOT NULL,
                    pilot_in_command TEXT NOT NULL,
                    instructor TEXT,
                    launch_method TEXT NOT NULL,
                    launch_site TEXT NOT NULL,
                    landing_site TEXT,
                    flight_duration TEXT,
                    max_altitude INTEGER,
                    cross_country_distance REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # If old table exists, migrate data
            if 'flights' in [table[0] for table in self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                self.cursor.execute('''
                    INSERT INTO flights_new (id, date, aircraft_type, aircraft_registration, pilot_in_command,
                                           instructor, launch_method, launch_site, landing_site, flight_duration,
                                           max_altitude, notes, created_at)
                    SELECT id, date, aircraft_type, aircraft_registration, pilot_in_command,
                           instructor, launch_method, launch_site, landing_site, flight_duration,
                           max_altitude, notes, created_at
                    FROM flights
                ''')
                self.cursor.execute('DROP TABLE flights')
            
            self.cursor.execute('ALTER TABLE flights_new RENAME TO flights')
        else:
            # Table already has correct structure
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    aircraft_type TEXT NOT NULL,
                    aircraft_registration TEXT NOT NULL,
                    pilot_in_command TEXT NOT NULL,
                    instructor TEXT,
                    launch_method TEXT NOT NULL,
                    launch_site TEXT NOT NULL,
                    landing_site TEXT,
                    flight_duration TEXT,
                    max_altitude INTEGER,
                    cross_country_distance REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        title_label = ttk.Label(main_frame, text="Glider Pilot Logbook", font=title_font)
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Search/Filter Frame
        search_frame = ttk.LabelFrame(main_frame, text="Search & Filter", padding="10")
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)
        
        self.create_search_widgets(search_frame)
        
        # Input Form
        form_frame = ttk.LabelFrame(main_frame, text="Flight Entry", padding="10")
        form_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Form fields
        self.create_form_fields(form_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Add Flight", command=self.add_flight).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Update Flight", command=self.update_flight).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Flight", command=self.delete_flight).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=(0, 5))
        
        # Treeview for displaying flights
        tree_frame = ttk.LabelFrame(main_frame, text="Flight Log", padding="10")
        tree_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.create_treeview(tree_frame)
        
        # Totals frame
        totals_frame = ttk.LabelFrame(main_frame, text="Totals", padding="10")
        totals_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.create_totals_widgets(totals_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_search_widgets(self, parent):
        """Create search and filter widgets"""
        # Search field
        ttk.Label(parent, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(parent, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        search_entry.bind('<KeyRelease>', lambda e: self.filter_data())
        
        # Filter category
        ttk.Label(parent, text="Filter by:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.filter_category_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(parent, textvariable=self.filter_category_var, width=15)
        filter_combo['values'] = ('All', 'Date', 'Aircraft Type', 'Registration', 'Pilot', 'Instructor', 'Launch Method', 'Launch Site', 'Landing Site')
        filter_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_data())
        
        # Clear search button
        ttk.Button(parent, text="Clear Search", command=self.clear_search).grid(row=0, column=4, padx=(5, 0), pady=2)
    
    def create_form_fields(self, parent):
        """Create form input fields"""
        # Row 0
        ttk.Label(parent, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(parent, textvariable=self.date_var, width=15).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        ttk.Label(parent, text="Aircraft Type:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.aircraft_type_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.aircraft_type_var, width=15).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Row 1
        ttk.Label(parent, text="Registration:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.registration_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.registration_var, width=15).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        ttk.Label(parent, text="Pilot in Command:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.pilot_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.pilot_var, width=15).grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Row 2
        ttk.Label(parent, text="Instructor:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.instructor_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.instructor_var, width=15).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        ttk.Label(parent, text="Launch Method:").grid(row=2, column=2, sticky=tk.W, pady=2)
        self.launch_method_var = tk.StringVar()
        launch_combo = ttk.Combobox(parent, textvariable=self.launch_method_var, width=12)
        launch_combo['values'] = ('Winch', 'Aerotow', 'Auto-tow', 'Bungee', 'Motor glider')
        launch_combo.grid(row=2, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Row 3
        ttk.Label(parent, text="Launch Site:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.launch_site_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.launch_site_var, width=15).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        ttk.Label(parent, text="Landing Site:").grid(row=3, column=2, sticky=tk.W, pady=2)
        self.landing_site_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.landing_site_var, width=15).grid(row=3, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Row 4
        ttk.Label(parent, text="Duration (H:MM):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar()
        duration_entry = ttk.Entry(parent, textvariable=self.duration_var, width=15)
        duration_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        ttk.Label(parent, text="Max Altitude (ft):").grid(row=4, column=2, sticky=tk.W, pady=2)
        self.altitude_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.altitude_var, width=15).grid(row=4, column=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Row 5
        ttk.Label(parent, text="Cross Country (km):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.distance_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.distance_var, width=15).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(5, 10), pady=2)
        
        # Row 6
        ttk.Label(parent, text="Notes:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=2)
        self.notes_var = tk.StringVar()
        notes_entry = tk.Text(parent, height=3, width=40)
        notes_entry.grid(row=6, column=1, columnspan=3, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.notes_text = notes_entry
        
        # Store selected flight ID for updates
        self.selected_flight_id = None
    
    def create_treeview(self, parent):
        """Create the treeview for displaying flight data"""
        columns = ('ID', 'Date', 'Aircraft', 'Registration', 'Pilot', 'Launch Method', 'Duration', 'Max Alt', 'Distance')
        
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Date', 'Duration']:
                self.tree.column(col, width=100)
            elif col in ['Max Alt', 'Distance']:
                self.tree.column(col, width=80)
            else:
                self.tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
    
    def create_totals_widgets(self, parent):
        """Create totals display widgets"""
        self.total_launches_var = tk.StringVar(value="Total Launches: 0")
        self.total_hours_var = tk.StringVar(value="Total Hours: 0:00")
        self.total_distance_var = tk.StringVar(value="Total Distance: 0.0 km")
        
        ttk.Label(parent, textvariable=self.total_launches_var).grid(row=0, column=0, padx=(0, 20), pady=2)
        ttk.Label(parent, textvariable=self.total_hours_var).grid(row=0, column=1, padx=(0, 20), pady=2)
        ttk.Label(parent, textvariable=self.total_distance_var).grid(row=0, column=2, pady=2)
    
    def validate_time_format(self, time_str):
        """Validate time format (H:MM or HH:MM)"""
        if not time_str:
            return True
        
        pattern = r'^(\d{1,2}):([0-5]\d)$'
        match = re.match(pattern, time_str)
        if not match:
            return False
        
        hours = int(match.group(1))
        minutes = int(match.group(2))
        
        return hours >= 0 and minutes >= 0 and minutes < 60
    
    def time_to_minutes(self, time_str):
        """Convert time string to minutes"""
        if not time_str:
            return 0
        
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        except:
            return 0
    
    def minutes_to_time(self, minutes):
        """Convert minutes to time string"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}:{mins:02d}"
    
    def load_data(self):
        """Load flight data from database into treeview"""
        self.filter_data()
    
    def filter_data(self):
        """Filter and display flight data based on search criteria"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Build query based on search criteria
        search_term = self.search_var.get().lower()
        filter_category = self.filter_category_var.get()
        
        base_query = '''
            SELECT id, date, aircraft_type, aircraft_registration, pilot_in_command, 
                   launch_method, flight_duration, max_altitude, cross_country_distance
            FROM flights
        '''
        
        params = []
        where_clause = ""
        
        if search_term:
            if filter_category == "All":
                where_clause = '''
                    WHERE LOWER(date) LIKE ? OR LOWER(aircraft_type) LIKE ? OR 
                          LOWER(aircraft_registration) LIKE ? OR LOWER(pilot_in_command) LIKE ? OR
                          LOWER(instructor) LIKE ? OR LOWER(launch_method) LIKE ? OR
                          LOWER(launch_site) LIKE ? OR LOWER(landing_site) LIKE ?
                '''
                params = [f'%{search_term}%'] * 8
            else:
                column_map = {
                    'Date': 'date',
                    'Aircraft Type': 'aircraft_type',
                    'Registration': 'aircraft_registration',
                    'Pilot': 'pilot_in_command',
                    'Instructor': 'instructor',
                    'Launch Method': 'launch_method',
                    'Launch Site': 'launch_site',
                    'Landing Site': 'landing_site'
                }
                if filter_category in column_map:
                    where_clause = f"WHERE LOWER({column_map[filter_category]}) LIKE ?"
                    params = [f'%{search_term}%']
        
        query = base_query + where_clause + " ORDER BY date DESC"
        
        # Execute query
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        # Insert data into treeview
        for row in rows:
            # Format the row data
            formatted_row = list(row)
            if formatted_row[8] is not None:  # Distance
                formatted_row[8] = f"{formatted_row[8]:.1f}"
            else:
                formatted_row[8] = ""
            
            self.tree.insert('', 'end', values=formatted_row)
        
        self.status_var.set(f"Showing {len(rows)} flights")
    
    def clear_search(self):
        """Clear search criteria and reload all data"""
        self.search_var.set("")
        self.filter_category_var.set("All")
        self.filter_data()
    
    def update_totals(self):
        """Update the totals display"""
        self.cursor.execute('''
            SELECT COUNT(*), 
                   SUM(CASE WHEN flight_duration != '' AND flight_duration IS NOT NULL THEN 1 ELSE 0 END) as duration_count,
                   SUM(CASE WHEN cross_country_distance IS NOT NULL THEN cross_country_distance ELSE 0 END) as total_distance
            FROM flights
        ''')
        
        result = self.cursor.fetchone()
        total_launches = result[0] if result[0] else 0
        total_distance = result[2] if result[2] else 0.0
        
        # Calculate total hours
        self.cursor.execute('SELECT flight_duration FROM flights WHERE flight_duration IS NOT NULL AND flight_duration != ""')
        durations = self.cursor.fetchall()
        
        total_minutes = 0
        for duration in durations:
            total_minutes += self.time_to_minutes(duration[0])
        
        total_hours_str = self.minutes_to_time(total_minutes)
        
        # Update display
        self.total_launches_var.set(f"Total Launches: {total_launches}")
        self.total_hours_var.set(f"Total Hours: {total_hours_str}")
        self.total_distance_var.set(f"Total Distance: {total_distance:.1f} km")
    
    def on_select(self, event):
        """Handle treeview selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            flight_id = item['values'][0]
            self.load_flight_details(flight_id)
    
    def load_flight_details(self, flight_id):
        """Load flight details into form for editing"""
        self.cursor.execute('SELECT * FROM flights WHERE id = ?', (flight_id,))
        flight = self.cursor.fetchone()
        
        if flight:
            self.selected_flight_id = flight_id
            
            # Map database columns to form variables
            self.date_var.set(flight[1])
            self.aircraft_type_var.set(flight[2])
            self.registration_var.set(flight[3])
            self.pilot_var.set(flight[4])
            self.instructor_var.set(flight[5] or '')
            self.launch_method_var.set(flight[6])
            self.launch_site_var.set(flight[7])
            self.landing_site_var.set(flight[8] or '')
            self.duration_var.set(flight[9] or '')
            self.altitude_var.set(flight[10] or '')
            self.distance_var.set(flight[11] or '')
            
            # Clear and set notes
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(1.0, flight[12] or '')
    
    def add_flight(self):
        """Add a new flight to the database"""
        if not self.validate_form():
            return
        
        try:
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            self.cursor.execute('''
                INSERT INTO flights (date, aircraft_type, aircraft_registration, pilot_in_command,
                                   instructor, launch_method, launch_site, landing_site, flight_duration,
                                   max_altitude, cross_country_distance, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.date_var.get(),
                self.aircraft_type_var.get(),
                self.registration_var.get(),
                self.pilot_var.get(),
                self.instructor_var.get() or None,
                self.launch_method_var.get(),
                self.launch_site_var.get(),
                self.landing_site_var.get() or None,
                self.duration_var.get() or None,
                int(self.altitude_var.get()) if self.altitude_var.get() else None,
                float(self.distance_var.get()) if self.distance_var.get() else None,
                notes or None
            ))
            
            self.conn.commit()
            self.filter_data()
            self.update_totals()
            self.clear_form()
            self.status_var.set("Flight added successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add flight: {str(e)}")
    
    def update_flight(self):
        """Update selected flight in the database"""
        if not self.selected_flight_id:
            messagebox.showwarning("Warning", "Please select a flight to update")
            return
        
        if not self.validate_form():
            return
        
        try:
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            self.cursor.execute('''
                UPDATE flights SET date=?, aircraft_type=?, aircraft_registration=?, pilot_in_command=?,
                                 instructor=?, launch_method=?, launch_site=?, landing_site=?, flight_duration=?,
                                 max_altitude=?, cross_country_distance=?, notes=?
                WHERE id=?
            ''', (
                self.date_var.get(),
                self.aircraft_type_var.get(),
                self.registration_var.get(),
                self.pilot_var.get(),
                self.instructor_var.get() or None,
                self.launch_method_var.get(),
                self.launch_site_var.get(),
                self.landing_site_var.get() or None,
                self.duration_var.get() or None,
                int(self.altitude_var.get()) if self.altitude_var.get() else None,
                float(self.distance_var.get()) if self.distance_var.get() else None,
                notes or None,
                self.selected_flight_id
            ))
            
            self.conn.commit()
            self.filter_data()
            self.update_totals()
            self.clear_form()
            self.status_var.set("Flight updated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update flight: {str(e)}")
    
    def delete_flight(self):
        """Delete selected flight from the database"""
        if not self.selected_flight_id:
            messagebox.showwarning("Warning", "Please select a flight to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this flight?"):
            try:
                self.cursor.execute('DELETE FROM flights WHERE id = ?', (self.selected_flight_id,))
                self.conn.commit()
                self.filter_data()
                self.update_totals()
                self.clear_form()
                self.status_var.set("Flight deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete flight: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.aircraft_type_var.set('')
        self.registration_var.set('')
        self.pilot_var.set('')
        self.instructor_var.set('')
        self.launch_method_var.set('')
        self.launch_site_var.set('')
        self.landing_site_var.set('')
        self.duration_var.set('')
        self.altitude_var.set('')
        self.distance_var.set('')
        self.notes_text.delete(1.0, tk.END)
        self.selected_flight_id = None
    
    def validate_form(self):
        """Validate form input"""
        if not self.date_var.get():
            messagebox.showerror("Error", "Date is required")
            return False
        
        if not self.aircraft_type_var.get():
            messagebox.showerror("Error", "Aircraft type is required")
            return False
        
        if not self.registration_var.get():
            messagebox.showerror("Error", "Aircraft registration is required")
            return False
        
        if not self.pilot_var.get():
            messagebox.showerror("Error", "Pilot in command is required")
            return False
        
        if not self.launch_method_var.get():
            messagebox.showerror("Error", "Launch method is required")
            return False
        
        if not self.launch_site_var.get():
            messagebox.showerror("Error", "Launch site is required")
            return False
        
        # Validate duration format
        if self.duration_var.get() and not self.validate_time_format(self.duration_var.get()):
            messagebox.showerror("Error", "Duration must be in H:MM format (e.g., 1:30)")
            return False
        
        # Validate altitude if provided
        if self.altitude_var.get():
            try:
                int(self.altitude_var.get())
            except ValueError:
                messagebox.showerror("Error", "Max altitude must be a number")
                return False
        
        # Validate distance if provided
        if self.distance_var.get():
            try:
                float(self.distance_var.get())
            except ValueError:
                messagebox.showerror("Error", "Cross country distance must be a number")
                return False
        
        return True
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = GliderLogbook(root)
    root.mainloop()

if __name__ == "__main__":
    main()