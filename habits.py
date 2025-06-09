import tkinter as tk
from datetime import date, datetime
import json
import os

DATA_FILE = "habit_data.json"

HABITS = {
    "Vitamins": ["Morning", "Afternoon", "Night"],
    "Fiber": ["1", "2", "3"],
    "Breathing": ["Morning"],
    "Stretches": ["Dead Hangs", "Hips", "Core"],
}

class HabitTrackerApp:
    def __init__(self, master):
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
                for col, sub_item in enumerate(sub_items, start=1):
                    var = tk.BooleanVar(value=self.data.get("habits", {}).get(habit, {}).get(sub_item, False))
                    chk = tk.Checkbutton(
                        self.frame,
                        text=sub_item,
                        font=("Arial", 18),
                        variable=var,
                        command=self.save_data,
                        padx=20,
                        pady=10
                    )
                    chk.grid(row=row, column=col, padx=20, sticky="w")
                    self.check_vars[habit][sub_item] = var

                    def make_callback(h=habit, i=sub_item, v=var, c=chk):
                        return lambda: self.update_checkbutton_color(h, i, v, c)

                    chk.config(command=make_callback())
                    self.update_checkbutton_color(habit, sub_item, var, chk)

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

        # Evenly distribute rows
        for i in range(row):
            self.frame.grid_rowconfigure(i, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Reset button
        self.reset_button = tk.Button(
            self.bottom_frame,
            text="Reset Today",
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
            relief="ridge"
        )
        self.date_label.pack(side="right", padx=20, pady=10)

    def get_formatted_date(self):
        return datetime.now().strftime("%b %d, %y")  # e.g., Jun 08, 25

    def update_date_label(self):
        self.date_label.config(text=self.get_formatted_date())

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"last_date": str(date.today()),
                         "habits": {habit: {sub_item: False for sub_item in sub_items}
                                    for habit, sub_items in HABITS.items()}}

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
            self.update_date_label()

    def manual_reset(self):
        self.reset_habits()
        self.save_data()
        self.update_date_label()

    def reset_habits(self):
        for habit, var in self.check_vars.items():
            if isinstance(var, dict):
                for sub in var.values():
                    sub.set(False)
            else:
                var.set(False)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width, height=event.height)

    def update_checkbutton_color(self, habit, sub_item, var, chk):
        if var.get():
            chk.config(bg="#b9f6ca")  # Light green
        else:
            chk.config(bg="#ff8a80")  # Light red

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()