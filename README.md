# fitzpi-habits-tracker

To run your Tkinter app on a touchscreen, the best approach is to create a desktop shortcut that launches your script in fullscreen mode. This makes it easy to start with a single tap.

**Steps:**


1. **Create a desktop shortcut** (`.desktop` file) in `~/Desktop/fitzpi-habits.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=Habit Tracker
Exec=python3 /path/to/habits.py
Icon=utilities-terminal
Terminal=false
```
Replace `/path/to/habits.py` with the actual path.

2. **Make the shortcut executable:**
```bash
chmod +x ~/Desktop/fitzpi-habits.desktop
```

Now you can launch your app in fullscreen with a single tap on the touchscreen.