import sys
import requests
from datetime import datetime

API_KEY = "468e87fed64a9b9701b2dd2e9a9f23c9"  # paste your key here
BASE_URL = "http://api.openweathermap.org/data/2.5"

# ANSI colors
R = "\033[91m"  # red
G = "\033[92m"  # green
Y = "\033[93m"  # yellow
B = "\033[94m"  # blue
C = "\033[96m"  # cyan
W = "\033[97m"  # white
DIM = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

WEATHER_ICONS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "fog": "🌫️",
    "haze": "🌫️",
    "smoke": "🌫️",
    "dust": "🌪️",
    "tornado": "🌪️",
}

def get_icon(condition):
    condition = condition.lower()
    for key in WEATHER_ICONS:
        if key in condition:
            return WEATHER_ICONS[key]
    return "🌡️"

def temp_color(temp):
    if temp <= 10:   return B
    if temp <= 20:   return C
    if temp <= 30:   return G
    if temp <= 38:   return Y
    return R

def wind_desc(speed):
    if speed < 5:    return "Calm"
    if speed < 15:   return "Light breeze"
    if speed < 30:   return "Moderate wind"
    if speed < 50:   return "Strong wind"
    return "Storm warning ⚠️"

def humidity_bar(humidity):
    filled = int(humidity / 10)
    bar = "█" * filled + "░" * (10 - filled)
    color = G if humidity < 60 else Y if humidity < 80 else R
    return f"{color}{bar}{RESET} {humidity}%"

def visibility_desc(vis_m):
    vis_km = vis_m / 1000
    if vis_km >= 10:  return f"{G}Excellent ({vis_km:.1f} km){RESET}"
    if vis_km >= 5:   return f"{Y}Good ({vis_km:.1f} km){RESET}"
    if vis_km >= 2:   return f"{Y}Moderate ({vis_km:.1f} km){RESET}"
    return f"{R}Poor ({vis_km:.1f} km){RESET}"

def fetch_current(city):
    url = f"{BASE_URL}/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 401:
            print(f"\n  {R}❌ Invalid API key. Check your key in the script.{RESET}\n")
            sys.exit(1)
        if r.status_code == 404:
            print(f"\n  {R}❌ City '{city}' not found. Try again.{RESET}\n")
            sys.exit(1)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        print(f"\n  {R}❌ No internet connection.{RESET}\n")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\n  {R}❌ Request timed out. Try again.{RESET}\n")
        sys.exit(1)

def fetch_forecast(city):
    url = f"{BASE_URL}/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "cnt": 24}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None

def display_current(data):
    city     = data['name']
    country  = data['sys']['country']
    temp     = data['main']['temp']
    feels    = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind_spd = data['wind']['speed'] * 3.6  # m/s to km/h
    wind_dir = data['wind'].get('deg', 0)
    vis      = data.get('visibility', 10000)
    condition= data['weather'][0]['main']
    desc     = data['weather'][0]['description'].title()
    sunrise  = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
    sunset   = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
    icon     = get_icon(condition)
    tc       = temp_color(temp)
    now      = datetime.now().strftime('%A, %d %B %Y · %H:%M')

    print(f"\n  {DIM}{'─' * 50}{RESET}")
    print(f"  {BOLD}{W}  {icon}  {city}, {country}{RESET}  {DIM}· {now}{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}")
    print(f"\n  {tc}{BOLD}  {temp:.1f}°C{RESET}  {DIM}feels like {feels:.1f}°C{RESET}")
    print(f"  {DIM}  ↑ {temp_max:.1f}°C   ↓ {temp_min:.1f}°C{RESET}")
    print(f"\n  {W}  {desc}{RESET}\n")
    print(f"  {DIM}💧 Humidity   {RESET}{humidity_bar(humidity)}")
    print(f"  {DIM}💨 Wind       {RESET}{W}{wind_spd:.1f} km/h{RESET}  {DIM}{wind_desc(wind_spd)}{RESET}")
    print(f"  {DIM}🔵 Pressure   {RESET}{W}{pressure} hPa{RESET}")
    print(f"  {DIM}👁️  Visibility {RESET}{visibility_desc(vis)}")
    print(f"  {DIM}🌅 Sunrise    {RESET}{Y}{sunrise}{RESET}   {DIM}🌇 Sunset  {RESET}{Y}{sunset}{RESET}")
    print(f"\n  {DIM}{'─' * 50}{RESET}\n")

def display_forecast(data):
    if not data:
        return

    print(f"  {BOLD}{W}📅 5-Day Forecast{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}")

    seen_days = []
    for item in data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        day = dt.strftime('%A')
        if day not in seen_days and dt.hour in range(11, 14):
            seen_days.append(day)
            temp    = item['main']['temp']
            t_min   = item['main']['temp_min']
            t_max   = item['main']['temp_max']
            cond    = item['weather'][0]['main']
            desc    = item['weather'][0]['description'].title()
            icon    = get_icon(cond)
            tc      = temp_color(temp)
            date_str= dt.strftime('%d %b')
            print(f"  {W}{day:<12}{RESET} {date_str}  {icon}  {tc}{temp:.1f}°C{RESET}  "
                  f"{DIM}↑{t_max:.1f} ↓{t_min:.1f}  {desc}{RESET}")

        if len(seen_days) == 5:
            break

    print(f"  {DIM}{'─' * 50}{RESET}\n")

def main():
    if len(sys.argv) < 2:
        print(f"\n  {Y}🌤️  Weather CLI{RESET}")
        print(f"  {DIM}usage: python weather.py <city>{RESET}")
        print(f"  {DIM}examples:{RESET}")
        print(f"  {DIM}  python weather.py Bhilai{RESET}")
        print(f"  {DIM}  python weather.py \"New Delhi\"{RESET}")
        print(f"  {DIM}  python weather.py London{RESET}\n")
        return

    city = " ".join(sys.argv[1:])
    print(f"\n  {DIM}Fetching weather for {W}{city}{RESET}{DIM}...{RESET}")

    current = fetch_current(city)
    display_current(current)

    forecast = fetch_forecast(city)
    display_forecast(forecast)

if __name__ == "__main__":
    main()