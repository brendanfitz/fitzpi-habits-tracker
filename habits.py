import tkinter as tk
from datetime import date
import json
import os

DATA_FILE = "habit_data.json"

HABITS = {
    "Vitamins": ["Morning", "Afternoon", "Night"],
    "Fiber": ["1", "2", "3"],
    "Stomach Breathing": ["Morning", "Afternoon", "Night"],
    "Hip Stretches": ["Gym", "Night"],
    "Dead Hangs": ["Morning", "Night"],
}

class HabitTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Daily Habit Tracker")
        master.geometry("1024x600")  # Fit to your touchscreen

        self.canvas = tk.Canvas(master)
        self.frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

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
                for col, time in enumerate(sub_items, start=1):
                    var = tk.BooleanVar(value=self.data.get("habits", {}).get(habit, {}).get(time, False))
                    chk = tk.Checkbutton(
                        self.frame,
                        text=time,
                        font=("Arial", 18),
                        variable=var,
                        command=self.save_data,
                        padx=20,
                        pady=10
                    )
                    chk.grid(row=row, column=col, padx=20, sticky="w")
                    self.check_vars[habit][time] = var
                row += 1
            else:
                var = tk.BooleanVar(value=self.data.get("habits", {}).get(habit, False))
                chk = tk.Checkbutton(
                    self.frame,
                    text=habit,
                    font=("Arial", 22),
                    variable=var,
                    command=self.save_data,
                    padx=20,
                    pady=15
                )
                chk.grid(row=row, column=0, columnspan=4, padx=30, pady=20, sticky="w")
                self.check_vars[habit] = var
                row += 1
    
        self.reset_button = tk.Button(
            self.frame,
            text="Reset Today",
            font=("Arial", 22),
            padx=30,
            pady=15,
            command=self.manual_reset
        )
        self.reset_button.grid(row=row, column=0, columnspan=4, pady=30)


    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"last_date": str(date.today()), "habits": {}}

    def save_data(self):
        habits_state = {}
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):  # Grouped checkboxes
                habits_state[habit] = {sub: v.get() for sub, v in var.items()}
            else:
                habits_state[habit] = var.get()

        self.data["habits"] = habits_state
        self.data["last_date"] = str(date.today())
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f)

    def check_date_and_reset(self):
        if self.data["last_date"] != str(date.today()):
            self.reset_habits()
            self.save_data()

    def manual_reset(self):
        self.reset_habits()
        self.save_data()

    def reset_habits(self):
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):
                for sub in var.values():
                    sub.set(False)
            else:
                var.set(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
