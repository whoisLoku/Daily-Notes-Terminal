import customtkinter as ctk
import json
from datetime import datetime, timedelta
import os
import locale
import random
import requests

# ====== CONSTANTS AND CONFIGURATION ======
try:
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "English_United States.1252")


# Terminal style colors
TERM_BG = "#0C0C0C"
TERM_TEXT = "#FFFFFF" 
TERM_PROMPT = "#00B8D4"
TERM_HEADER = "#FF5733"
TERM_ERROR = "#FF0000"
TERM_SUCCESS = "#33FF33"

# Tag colors for priority levels
TAG_COLORS = {
    "low": "#33FF33",      # Gray-blue
    "mid": "#ff9800",      # Orange
    "important": "#f44336", # Bright red
    "birthday": "#FFEB3B", # Yellow
    "special_day": "#f49536" # Orange
}

# Text colors for different priority levels
TEXT_COLORS = {
    "low": "#FFFFFF",     # White
    "mid": "#FFFFFF",     # White
    "important": "#FFFFFF", # White
    "birthday": "#FFFFFF", # White
    "special_day": "#FFFFFF" # White
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def weather_with_emoji(description):
    desc = description.lower()
    if "clear" in desc or "sunny" in desc:
        return "☀️ Sunny"
    elif "cloud" in desc:
        return "☁️ Cloudy"
    elif "rain" in desc:
        return "🌧️ Rainy"
    elif "snow" in desc:
        return "❄️ Snowy"
    elif "storm" in desc or "thunder" in desc:
        return "⛈️ Stormy"
    else:
        return description.capitalize()

def get_weather():
    import requests
    from datetime import datetime, timedelta

    api_key = "" # Your OpenWeatherMap API key
    city = "" # Your city name
    url_current = f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=en&units=metric&appid={api_key}"
    url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=en&units=metric&appid={api_key}"

    try:
        # Current weather
        response_current = requests.get(url_current)
        response_current.raise_for_status()
        data_current = response_current.json()

        temp_c = data_current['main']['temp']
        temp_f = round(temp_c * 9/5 + 32)
        feels_like_c = data_current['main']['feels_like']
        feels_like_f = round(feels_like_c * 9/5 + 32)
        desc = data_current['weather'][0]['description'].capitalize()
        humidity = data_current['main']['humidity']

        # Tomorrow's forecast
        response_forecast = requests.get(url_forecast)
        response_forecast.raise_for_status()
        data_forecast = response_forecast.json()

        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d 12:00:00")

        forecast_item = next((item for item in data_forecast['list'] if item['dt_txt'] == tomorrow_str), None)
        if forecast_item:
            forecast_temp = round(forecast_item['main']['temp'])
            forecast_desc = forecast_item['weather'][0]['description'].capitalize()
            forecast_text = f"TOMORROW'S WEATHER FORECAST: {weather_with_emoji(forecast_desc)}, {forecast_temp}°C"
        else:
            forecast_text = "Tomorrow's forecast not available"

        weather_text = weather_with_emoji(desc)
        return f"{weather_with_emoji(desc)}, {round(temp_c)}°C ({temp_f}°F) (Feels like: {round(feels_like_c)}°C ({feels_like_f}°F)), Humidity: %{humidity}"

    except Exception as e:
        print("Error fetching weather data:", e)
        return "🌐 Weather data not available"


# You can add more motivational messages and general knowledge facts as needed
def get_special_message(): 
    messages = [
        "🌟 A new day, new opportunities!", 
        "💪 You can achieve great things today!",
        "🎯 Focus on your goals!",
        "✨ Take good care of yourself!",
        "🌈 Stay positive!"
    ]

    general_knowledge = [
        "🌍 The Earth revolves around the Sun in about 365.25 days.",
        "⚡ Electricity travels at nearly 300,000 km per second.",
        "🦅 Eagles can spot their prey from about 3 km away.",
        "📜 The first written laws were established by Babylonian King Hammurabi."
    ]

    # Choose one motivational message and one general knowledge fact randomly
    motivational = random.choice(messages)
    knowledge = random.choice(general_knowledge)

    return f"{motivational}\nDID YOU KNOW? {knowledge}"


def get_full_date_string():
    return datetime.now().strftime("%A, %B %d, %Y")

print(get_full_date_string())

def load_notes_and_upcoming():
    try:
        with open('notes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        today = datetime.now().strftime("%d-%m")
        notes = []
        upcoming = []
        
        # Today's Notes
        if today in data:
            notes = [(item["text"], item.get("tag", "low")) for item in data[today]]
            
         # Upcoming Events
        for date_str, items in data.items():
            try:
                day, month = map(int, date_str.split('-'))
                current_year = datetime.now().year
                date_obj = datetime(current_year, month, day)
                
                if date_obj < datetime.now():
                    date_obj = datetime(current_year + 1, month, day)
                
                days_diff = (date_obj - datetime.now()).days
                if date_str != today and 0 < days_diff <= 30:
                    for item in items:
                        upcoming.append((date_obj, item["text"], item.get("tag", "low")))
            except ValueError:
                continue
                
        upcoming.sort(key=lambda x: x[0])
        
        return notes, upcoming
    except FileNotFoundError:
        print("Error: notes.json not found")
        return [], []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return [], []


class TerminalPopup(ctk.CTk):
    def __init__(self, notes, upcoming, special_message, full_date_str, weather):
        super().__init__()
        self.geometry("960x720")  # Set the size of the window
        self.title("TERMINAL://LNCLT")  ## You can change the title as needed
        self.wm_attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=TERM_BG)
        
        # Store reference to ascii_art for refresh
        self.tips_text = "\nType 'help' to see available commands. Press Enter to execute command.\n"
        
        # ASCII Art Header
        ascii_art = """
  _____ _____ ____  __  __ ___ _   _    _    _     
 |_   _| ____|  _ \|  \/  |_ _| \ | |  / \  | |    
   | | |  _| | |_) | |\/| || ||  \| | / _ \ | |    
   | | | |___|  _ <| |  | || || |\  |/ ___ \| |___ 
   |_| |_____|_| \_\_|  |_|___|_| \_/_/   \_\_____|
                                    
        """

        # Main Terminal Frame
        self.terminal = ctk.CTkTextbox(
            self,
            fg_color=TERM_BG,
            text_color=TERM_TEXT,
            font=("Courier", 14),
            activate_scrollbars=True
        )
        self.terminal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Command Input Frame
        input_frame = ctk.CTkFrame(self, fg_color=TERM_BG)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        prompt_label = ctk.CTkLabel(
            input_frame,
            text="LNCLT>",
            font=("Courier", 14, "bold"),
            text_color=TERM_PROMPT
        )
        prompt_label.pack(side="left", padx=(0, 10))
        
        self.command_input = ctk.CTkEntry(
            input_frame,
            fg_color=TERM_BG,
            text_color=TERM_TEXT,
            font=("Courier", 14),
            border_color=TERM_PROMPT
        )
        self.command_input.pack(side="left", fill="x", expand=True)
        self.command_input.bind("<Return>", self.process_command)
        
        # Initialize terminal content
        self.print_header(ascii_art)
        self.print_system_info(full_date_str, weather, special_message)
        self.print_notes(notes)
        self.print_upcoming(upcoming)
        
        self.command_input.focus()
        
    def print_header(self, ascii_art):
        self.terminal.insert("end", ascii_art + "\n", "header")
        self.terminal.insert("end", "="*50, "separator")
        self.terminal.insert("end", self.tips_text, "tips")
        self.terminal.insert("end", "\n", "separator")
        self.terminal.tag_config("header", foreground=TERM_HEADER)
        self.terminal.tag_config("separator", foreground=TERM_PROMPT)
        self.terminal.tag_config("tips", foreground=TERM_PROMPT)
        
    def print_system_info(self, date_str, weather, special_msg):
        self.terminal.insert("end", f"\nSYSTEM DATE: {date_str}\n", "info")
        self.terminal.insert("end", f"WEATHER STATUS: {weather}\n", "info")
        self.terminal.insert("end", f"SPECIAL MESSAGE: {special_msg}\n", "info")
        self.terminal.insert("end", "="*50 + "\n\n", "separator")
        self.terminal.tag_config("info", foreground=TERM_SUCCESS)
        
    def print_notes(self, notes):
        self.terminal.insert("end", "TODAY'S TASKS:\n", "section")
        if notes:
            for text, tag in notes:
                # Insert tag with its color
                self.terminal.insert("end", "[", f"bracket_{tag}")
                self.terminal.insert("end", tag.upper(), f"tag_{tag}")
                self.terminal.insert("end", "] ", f"bracket_{tag}")
                # Insert text with its color
                self.terminal.insert("end", f"{text}\n", f"text_{tag}")
                
                # Configure colors
                self.terminal.tag_config(f"bracket_{tag}", foreground=TAG_COLORS.get(tag, TERM_TEXT))
                self.terminal.tag_config(f"tag_{tag}", foreground=TAG_COLORS.get(tag, TERM_TEXT))
                self.terminal.tag_config(f"text_{tag}", foreground=TEXT_COLORS.get(tag, TERM_TEXT))
        else:
            self.terminal.insert("end", "No tasks found for today.\n", "normal")
        self.terminal.insert("end", "\n")
        self.terminal.tag_config("section", foreground=TERM_HEADER)
        
    def print_upcoming(self, upcoming):
        if upcoming:
            self.terminal.insert("end", "UPCOMING EVENTS:\n", "section")
            for date_obj, text, tag in upcoming:
                days_left = (date_obj - datetime.now()).days
                date_str = date_obj.strftime("%d %B")
                
                # Insert date and tag with their colors
                self.terminal.insert("end", f"[{date_str}] ", "date")
                self.terminal.insert("end", "[", f"bracket_{tag}")
                self.terminal.insert("end", tag.upper(), f"tag_{tag}")
                self.terminal.insert("end", "] ", f"bracket_{tag}")
                # Insert text with its color
                self.terminal.insert("end", f"{text}\n", f"text_{tag}")
                
                # Configure colors
                self.terminal.tag_config("date", foreground=TERM_PROMPT)
                self.terminal.tag_config(f"bracket_{tag}", foreground=TAG_COLORS.get(tag, TERM_TEXT))
                self.terminal.tag_config(f"tag_{tag}", foreground=TAG_COLORS.get(tag, TERM_TEXT))
                self.terminal.tag_config(f"text_{tag}", foreground=TEXT_COLORS.get(tag, TERM_TEXT))
                
    def process_command(self, event):
        command = self.command_input.get().strip().lower()
        self.command_input.delete(0, 'end')
        
        self.terminal.insert("end", f"\nLNCLT> {command}\n", "prompt")
        
        if command == "clear":
            self.terminal.delete(1.0, "end")
            self.refresh_display()
        elif command == "help":
            self.show_help()
        elif command == "exit":
            self.destroy()
        elif command == "time":
            self.terminal.insert("end", f"Current time: {datetime.now().strftime('%H:%M:%S')}\n", "info")
        else:
            self.terminal.insert("end", "Unknown command. Type 'help' for available commands.\n", "error")
            
            
        self.terminal.see("end")
        
    def refresh_display(self):
        """Refresh the entire display with current data"""
        notes, upcoming = load_notes_and_upcoming()
        special_msg = get_special_message()
        full_date = get_full_date_string()
        weather = get_weather()
        
        self.print_header(self.ascii_art)
        self.print_system_info(full_date, weather, special_msg)
        self.print_notes(notes)
        self.print_upcoming(upcoming)
        
    def show_help(self):
        help_text = """
            Available commands:
            - help: Show this help message
            - clear: Clear terminal
            - exit: Close the application
            - time: Show current time
            """
        self.terminal.insert("end", help_text, "help")
        self.terminal.tag_config("help", foreground=TERM_SUCCESS)


if __name__ == "__main__":
    notes, upcoming = load_notes_and_upcoming()
    special_msg = get_special_message()
    full_date = get_full_date_string()
    weather = get_weather()

    app = TerminalPopup(notes, upcoming, special_msg, full_date, weather)
    app.mainloop()