import time
import subprocess
from datetime import datetime
import pytz

def wait_until(hour, minute):
    tz = pytz.timezone("Europe/Rome")
    while True:
        now = datetime.now(tz)
        if now.hour == hour and now.minute == minute:
            break
        print(f"⏳ Aspetto {hour:02}:{minute:02}... Ora: {now.strftime('%H:%M:%S')}")
        time.sleep(30)

def run_script(script):
    print(f"▶️ Eseguo {script}...")
    subprocess.call(["python", script])
    print(f"✅ Completato {script}")

if __name__ == "__main__":
    print("🚀 Worker Tennis avviato...")
    
    # Aspetta le 05:00 ora italiana
    wait_until(5, 0)
    run_script("genera_csv.py")
    
    # Aspetta altri 10 minuti
    time.sleep(600)
    
    # Esegui il bot Telegram
    run_script("bot_tennis.py")
    
    print("😴 Fine. Worker dorme fino al prossimo restart.")
