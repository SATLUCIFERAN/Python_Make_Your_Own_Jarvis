import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

class JarvisScheduler:
    def __init__(self, data_dir):
        self.db_path = Path(data_dir) / "jarvis_intelligence.db"
        self._init_db()

    def _init_db(self):
        """Creates the database and table if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create table with all columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                date TEXT,
                start_time TEXT,
                stop_time TEXT,
                task TEXT,
                notified INTEGER DEFAULT 0,
                reminder_minutes INTEGER DEFAULT 15
            )
        ''')
        
        # Check if old table exists without new columns - if so, migrate
        cursor.execute("PRAGMA table_info(schedule)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'notified' not in columns:
            print("[DB Migration] Adding 'notified' column...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN notified INTEGER DEFAULT 0")
        
        if 'reminder_minutes' not in columns:
            print("[DB Migration] Adding 'reminder_minutes' column...")
            cursor.execute("ALTER TABLE schedule ADD COLUMN reminder_minutes INTEGER DEFAULT 15")
        
        conn.commit()
        conn.close()
        print("[DB] Database initialized successfully")

    def save_event(self, date, start_time, stop_time, task, reminder_minutes=15):
        """C - Create: Inserts a new appointment into the SQLite database."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO schedule (timestamp, date, start_time, stop_time, task, notified, reminder_minutes)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            ''', (timestamp, date, start_time, stop_time, task, reminder_minutes))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def get_all_events(self):
        """R - Read: Retrieves all events from SQLite sorted by date."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT id, date, start_time, stop_time, task, notified, reminder_minutes FROM schedule ORDER BY date ASC, start_time ASC')
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Read Error: {e}")
            return []

    def get_upcoming_events(self, minutes_ahead=60):
        """Get events that are coming up within the specified minutes."""
        try:
            now = datetime.now()
            future_time = now + timedelta(minutes=minutes_ahead)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, date, start_time, stop_time, task, notified, reminder_minutes 
                FROM schedule 
                WHERE notified = 0
                ORDER BY date ASC, start_time ASC
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            upcoming = []
            for row in rows:
                event_id, date_str, start_time, stop_time, task, notified, reminder_mins = row
                
                # Parse event datetime
                try:
                    event_datetime = datetime.strptime(f"{date_str} {start_time}", "%m/%d/%y %H:%M")
                except:
                    # Try alternative format
                    try:
                        event_datetime = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
                    except:
                        continue
                
                # FIXED: Check if event is in the future (hasn't started yet)
                # Alert as long as the event hasn't started, regardless of reminder time
                if now <= event_datetime:
                    minutes_until = int((event_datetime - now).total_seconds() / 60)
                    
                    # Only alert if event is within the lookahead window
                    if minutes_until <= minutes_ahead:
                        upcoming.append({
                            'id': event_id,
                            'date': date_str,
                            'start_time': start_time,
                            'stop_time': stop_time,
                            'task': task,
                            'minutes_until': minutes_until,
                            'reminder_minutes': reminder_mins
                        })
            
            return upcoming
        except Exception as e:
            print(f"Get Upcoming Error: {e}")
            return []

    def mark_as_notified(self, event_id):
        """Mark an event as notified so we don't alert again."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("UPDATE schedule SET notified = 1 WHERE id = ?", (event_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Mark Notified Error: {e}")
            return False

    def delete_event_by_name(self, task_name):
        """D - Delete: Removes entries matching a specific keyword (Voice Optimized)."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedule WHERE task LIKE ?", (f'%{task_name}%',))
            rows_affected = conn.total_changes
            conn.commit()
            conn.close()
            return rows_affected > 0
        except Exception as e:
            print(f"Delete Error: {e}")
            return False

    def update_event_by_name(self, old_name, new_task):
        """U - Update: Replaces an old task description with a new one."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("UPDATE schedule SET task = ? WHERE task LIKE ?", (new_task, f'%{old_name}%'))
            rows_affected = conn.total_changes
            conn.commit()
            conn.close()
            return rows_affected > 0
        except Exception as e:
            print(f"Update Error: {e}")
            return False

    def reset_all_notifications(self):
        """Reset all notified flags (useful for testing)."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("UPDATE schedule SET notified = 0")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Reset Error: {e}")
            return False


class ScheduleMonitor:
    """Background thread that monitors schedules and triggers notifications."""
    
    def __init__(self, scheduler, notification_callback):
        self.scheduler = scheduler
        self.notification_callback = notification_callback
        self.running = False
        self.thread = None
        self.check_interval = 10  # Check every 10 seconds for faster response
    
    def start(self):
        """Start the monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("[Schedule Monitor] Started - Checking every 10 seconds")
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Check for upcoming events (next 60 minutes)
                upcoming = self.scheduler.get_upcoming_events(minutes_ahead=60)
                
                for event in upcoming:
                    minutes = event['minutes_until']
                    reminder = event['reminder_minutes']
                    
                    # Trigger notification if:
                    # 1. Event is starting now (0-1 minutes), OR
                    # 2. We're at the reminder time
                    should_notify = False
                    
                    if minutes <= 1:
                        # Event is starting now/very soon - always notify
                        should_notify = True
                    elif minutes <= reminder:
                        # We're within the reminder window
                        should_notify = True
                    
                    if should_notify:
                        # Trigger notification callback
                        self.notification_callback(event)
                        
                        # Mark as notified
                        self.scheduler.mark_as_notified(event['id'])
                        
                        print(f"[Monitor] Notified: {event['task']} in {event['minutes_until']} minutes")
                
            except Exception as e:
                print(f"[Monitor Error]: {e}")
            
            # Wait before next check
            time.sleep(self.check_interval)


class ScheduleGUI:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("Jarvis Command Center: Scheduler")
        self.root.geometry("420x750")
        self.root.configure(padx=20, pady=20)
        self.last_saved_entry = None

        tk.Label(self.root, text="Select Date:", font=("Arial", 10, "bold")).pack(anchor="w")
        now = datetime.now()
        self.cal = Calendar(self.root, selectmode='day', year=now.year, month=now.month, day=now.day)
        self.cal.pack(pady=10, fill="x")

        time_container = tk.Frame(self.root)
        time_container.pack(fill="x", pady=10)

        # Start Time Pickers
        start_frame = tk.Frame(time_container)
        start_frame.pack(side="left", expand=True)
        tk.Label(start_frame, text="Start Time:", font=("Arial", 9, "bold")).pack()
        self.start_h = tk.StringVar(value="09")
        self.start_m = tk.StringVar(value="00")
        s_pickers = tk.Frame(start_frame); s_pickers.pack()
        ttk.Spinbox(s_pickers, from_=0, to=23, width=3, textvariable=self.start_h, format="%02.0f").pack(side="left")
        tk.Label(s_pickers, text=":").pack(side="left")
        ttk.Spinbox(s_pickers, from_=0, to=59, width=3, textvariable=self.start_m, format="%02.0f").pack(side="left")

        # Stop Time Pickers
        stop_frame = tk.Frame(time_container)
        stop_frame.pack(side="right", expand=True)
        tk.Label(stop_frame, text="Stop Time:", font=("Arial", 9, "bold")).pack()
        self.stop_h = tk.StringVar(value="10")
        self.stop_m = tk.StringVar(value="00")
        e_pickers = tk.Frame(stop_frame); e_pickers.pack()
        ttk.Spinbox(e_pickers, from_=0, to=23, width=3, textvariable=self.stop_h, format="%02.0f").pack(side="left")
        tk.Label(e_pickers, text=":").pack(side="left")
        ttk.Spinbox(e_pickers, from_=0, to=59, width=3, textvariable=self.stop_m, format="%02.0f").pack(side="left")

        tk.Label(self.root, text="Appointment / Task:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 0))
        self.task_entry = tk.Entry(self.root, font=("Arial", 11))
        self.task_entry.pack(pady=5, fill="x")

        # Reminder Settings
        tk.Label(self.root, text="Reminder Time:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        reminder_frame = tk.Frame(self.root)
        reminder_frame.pack(fill="x", pady=5)
        
        self.reminder_var = tk.StringVar(value="15")
        reminder_options = [
            ("5 minutes before", "5"),
            ("15 minutes before", "15"),
            ("30 minutes before", "30"),
            ("1 hour before", "60")
        ]
        
        for text, value in reminder_options:
            tk.Radiobutton(reminder_frame, text=text, variable=self.reminder_var, 
                          value=value, font=("Arial", 9)).pack(anchor="w", padx=20)

        self.save_btn = tk.Button(self.root, text="CONFIRM LOGS", command=self.save,
                                  bg="#2c3e50", fg="white", font=("Arial", 10, "bold"), height=2)
        self.save_btn.pack(pady=20, fill="x")

    def save(self):
        date_str = self.cal.get_date()
        start_str = f"{self.start_h.get()}:{self.start_m.get()}"
        stop_str = f"{self.stop_h.get()}:{self.stop_m.get()}"
        task_str = self.task_entry.get()
        reminder_mins = int(self.reminder_var.get())

        if not task_str:
            messagebox.showwarning("Input Error", "Please describe the task.")
            return

        if self.engine.save_event(date_str, start_str, stop_str, task_str, reminder_mins):
            self.last_saved_entry = {
                "date": date_str, 
                "start": start_str, 
                "stop": stop_str, 
                "task": task_str,
                "reminder": reminder_mins
            }
            messagebox.showinfo("Success", f"Entry recorded with {reminder_mins} minute reminder.")
            self.root.destroy()

    def run(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.mainloop()
        return self.last_saved_entry


class ListViewerGUI:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("Jarvis: Personal Schedule Archive")
        self.root.geometry("950x500") 
        self.root.configure(bg="#1e1e1e")

        # High-Tech Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2d2d2d", foreground="white", 
                       fieldbackground="#2d2d2d", rowheight=35, font=("Arial", 10))
        style.configure("Treeview.Heading", background="#4a4a4a", foreground="white", 
                       font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#0078d7')])

        # Table Setup
        columns = ('date', 'start', 'stop', 'task', 'status', 'reminder')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        
        # Column Widths
        self.tree.column('date', width=120, anchor="center")
        self.tree.column('start', width=80, anchor="center")
        self.tree.column('stop', width=80, anchor="center")
        self.tree.column('task', width=400, anchor="w")
        self.tree.column('status', width=100, anchor="center")
        self.tree.column('reminder', width=100, anchor="center")

        self.tree.heading('date', text='DATE')
        self.tree.heading('start', text='START')
        self.tree.heading('stop', text='STOP')
        self.tree.heading('task', text='TASK DESCRIPTION')
        self.tree.heading('status', text='STATUS')
        self.tree.heading('reminder', text='REMINDER')

        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        events = self.engine.get_all_events()
        now = datetime.now()
        
        for event in events:
            event_id, date_str, start_time, stop_time, task, notified, reminder_mins = event
            
            # Determine status
            try:
                event_datetime = datetime.strptime(f"{date_str} {start_time}", "%m/%d/%y %H:%M")
            except:
                try:
                    event_datetime = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
                except:
                    event_datetime = now
            
            if event_datetime < now:
                status = "✓ Past"
            elif notified:
                status = "🔔 Notified"
            else:
                status = "⏰ Pending"
            
            reminder_text = f"{reminder_mins} min"
            
            self.tree.insert('', tk.END, values=(date_str, start_time, stop_time, task, status, reminder_text))
            
        self.tree.pack(expand=True, fill='both', padx=20, pady=(20, 10))
        scrollbar.pack(side='right', fill='y')

        # Interactive Hint
        tk.Label(self.root, text="Jarvis is actively monitoring your schedule and will alert you before events.", 
                 bg="#1e1e1e", fg="#5dade2", font=("Arial", 9, "italic")).pack(pady=10)

    def run(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.mainloop()