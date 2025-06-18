import tkinter as tk
from datetime import date, datetime
import calendar
import json
import os
import csv
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

CSV_PATH = os.getenv("HABITS_CSV_PATH")
DATA_FILE = "habit_data.json"

def load_habits_from_csv(csv_path):
    habits = {}
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            habit = row['Habits'].strip()
            subitem = row['SubItems'].strip()
            days = [d.strip() for d in row.get('Days', '').split('-') if d.strip()]
            if habit not in habits:
                habits[habit] = []
            if subitem:
                habits[habit].append({'name': subitem, 'days': days})
    return habits

def is_today_in_days(days):
    if not days:
        return True  # Show every day if no days specified
    today = calendar.day_abbr[date.today().weekday()]
    return today in days


HABITS = load_habits_from_csv(CSV_PATH)

class HabitTrackerApp:
    def __init__(self, master):
        self.check_vars, self.data = {}, {}
        self.date_label, self.reset_button = None, None

        self.master = master
        master.title("Daily Habit Tracker")
        master.geometry("1024x600") # Fit to the touchscreen
        # master.attributes('-fullscreen', True)  # Optional fullscreen

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.frame = tk.Frame(self.canvas, borderwidth=4, relief="ridge")
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(side="bottom", fill="x")

        self.window_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.load_data()
        self.create_widgets()
        self.check_date_and_reset()

    def create_widgets(self):
        self.check_vars = {}

        row = 0
        for habit, sub_items in HABITS.items():
            if sub_items:
                lbl = tk.Label(self.frame, text=habit, font=("Arial", 22, "bold"), anchor="w")
                lbl.grid(row=row, column=0, padx=30, pady=20, sticky="w")

                self.check_vars[habit] = {}
                for col, sub_item_dict in enumerate(sub_items, start=1):
                    sub_item = sub_item_dict['name']
                    days = sub_item_dict.get('days', [])
                    if not is_today_in_days(days):
                        continue

                    var = tk.BooleanVar(value=self.data.get("habits", {}).get(habit, {}).get(sub_item, False))
                    chk = tk.Checkbutton(
                        self.frame,
                        text=sub_item,
                        font=("Arial", 18),
                        variable=var,
                        command=self.save_data,
                        padx=20,
                        pady=10,
                        borderwidth=4,
                        relief="ridge"
                    )
                    chk.grid(row=row, column=col, padx=20, sticky="w")
                    self.check_vars[habit][sub_item] = var

                    def make_callback(h=habit, si=sub_item, v=var, c=chk):
                        return lambda: self.update_checkbutton_color(h, si, v, c)

                    chk.config(command=make_callback())
                    self.update_checkbutton_color(habit, sub_item, var, chk)

                row += 1
            else:
                raise ValueError('Habits without Sub Items Not Configured')

        # Evenly distribute rows
        for i in range(row):
            self.frame.grid_rowconfigure(i, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Reset button
        self.reset_button = tk.Button(
            self.bottom_frame,
            text="Reset",
            font=("Arial", 28, "bold"),
            padx=30,
            pady=15,
            command=self.manual_reset,
            bg = "#1976D2",  # Background color
            fg = "white",  # Text color
            activebackground = "#1565C0",  # Color when pressed
            activeforeground = "white"
        )
        self.reset_button.pack(side="left", padx=20, pady=10)

        # Date label
        self.date_label = tk.Label(
            self.bottom_frame,
            text=self.get_formatted_date(),
            font=("Arial", 28, "bold"),
            anchor="e",
            bg="#1976D2",      # Background color
            fg="white",         # Text color
            padx=30,  # Inner horizontal padding (inside label)
            pady=10,  # Inner vertical padding (inside label)
            borderwidth=4,
            relief="raised"
        )
        self.date_label.pack(side="right", padx=20, pady=10)

    @staticmethod
    def get_formatted_date():
        return datetime.now().strftime("%b %d, %y")  # e.g., Jun 08, 25

    def update_date_label(self):
        self.date_label.config(text=self.get_formatted_date())

    def load_data(self):
        self.data = {"last_date": str(date.today()),
                     "habits": {habit: {sub_item['name']: False for sub_item in sub_items}
                                for habit, sub_items in HABITS.items()}}
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    # Read last record from file (newline-delimited JSON)
                    lines = f.readlines()
                    if lines:
                        self.data = json.loads(lines[-1])
            except Exception:
                pass

    def save_data(self):
        habits_state = {}
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):
                habits_state[habit] = {sub: v.get() for sub, v in var.items()}
            else:
                habits_state[habit] = var.get()

        record = {
            "habits": habits_state,
            "last_date": str(date.today()),
            "timestamp": datetime.now().isoformat()
        }
        with open(DATA_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")
        self.data = record  # Update current state

    def check_date_and_reset(self):
        if self.data["last_date"] != str(date.today()):
            self.reset_habits()
            self.save_data()
            self.update_date_label()

    def manual_reset(self):
        self.reset_habits()
        self.save_data()
        self.update_date_label()
        for widget in self.frame.winfo_children():
            widget.destroy()
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()
        self.create_widgets()

    def reset_habits(self):
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):
                for sub in var.values():
                    sub.set(False)
            else:
                var.set(False)
        self.update_all_checkbutton_colors()

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width, height=event.height)

    @staticmethod
    def update_checkbutton_color(habit, sub_item, var, chk):
        if var.get():
            chk.config(bg="#b9f6ca", activebackground='#b9f6ca')  # Light green
        else:
            chk.config(bg="#ff8a80", activebackground='#ff8a80')  # Light red

    def update_all_checkbutton_colors(self):
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):
                for sub_item, v in var.items():
                    # Find the Checkbutton widget for this var
                    for widget in self.frame.grid_slaves():
                        if isinstance(widget, tk.Checkbutton) and widget.cget("text") == sub_item:
                            self.update_checkbutton_color(habit, sub_item, v, widget)
            else:
                for widget in self.frame.grid_slaves():
                    if isinstance(widget, tk.Checkbutton) and widget.cget("text") == habit:
                        self.update_checkbutton_color(habit, None, var, widget)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()