#!/usr/bin/env python3
import time
import subprocess
from datetime import datetime
import pytz

def wait_until(hour: int, minute: int):
    tz = pytz.timezone("Europe/Rome")
    while True:
        now = datetime.now(tz)
        if now.hour == hour and now.minute == minute:
            return
        print(f"⏳ Aspetto {hour:02}:{minute:02}… (ora {now.strftime('%H:%M:%S')})")
        time.sleep(30)

def run_script(script: str):
    print(f"▶️ Eseguo {script}…")
    subprocess.call(["python", script])
    print(f"✅ Completato {script}")

if __name__ == "__main__":
    print("🚀 Worker Tennis START (live 24/7)")

    while True:
        wait_until(5, 0)               # alle 05:00 ora italiana
        run_script("bot_tennis.py")    # fetch, filter e invio segnali
        print("😴 Worker dorme fino al giorno successivo…")
        time.sleep(23*3600 + 50*60)     # ~23h50m di pausa
