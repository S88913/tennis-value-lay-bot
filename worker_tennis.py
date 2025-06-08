#!/usr/bin/env python3
import time
import subprocess
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Carica le variabili da .env
load_dotenv()

def wait_until(hour: int, minute: int):
    tz = pytz.timezone("Europe/Rome")
    while True:
        now = datetime.now(tz)
        if now.hour == hour and now.minute == minute:
            break
        print(f"⏳ Aspetto {hour:02}:{minute:02} (ora locale: {now.strftime('%H:%M:%S')})")
        time.sleep(30)

def run_script(script: str):
    print(f"▶️ Eseguo {script} ...")
    subprocess.call(["python", script])
    print(f"✅ Completato {script}")

if __name__ == "__main__":
    print("🚀 Worker Tennis START (live 24/7).")

    # — RUN IMMEDIATO PER TEST — 
    run_script("bot_tennis.py")
    print("🏃 Esecuzione immediata completata, ora passo a loop giornaliero...\n")

    while True:
        # 1) Aspetta le 05:00 ora italiana
        wait_until(5, 0)

        # 2) Esegui di nuovo il bot alle 05:00
        run_script("bot_tennis.py")

        # 3) Dorme fino al giorno successivo
        print("😴 Dormo fino al giorno successivo...\n")
        time.sleep(23 * 3600 + 50 * 60)
