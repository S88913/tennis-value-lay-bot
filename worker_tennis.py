import time
import subprocess
from datetime import datetime
import pytz
import os

def wait_until(hour, minute):
    """
    Aspetta fino all'ora (hour:minute) nel fuso Europe/Rome.
    Non esce mai; rimane in loop fino a che ora e minuto coincidono.
    """
    tz = pytz.timezone("Europe/Rome")
    while True:
        now = datetime.now(tz)
        if now.hour == hour and now.minute == minute:
            break
        # Stampo lo stato per debug sui log di Render
        print(f"⏳ Aspetto {hour:02}:{minute:02}... Ora: {now.strftime('%H:%M:%S')}")
        time.sleep(30)  # controllo ogni 30 secondi

def run_script(script_name):
    """
    Esegue lo script Python specificato, stampando un log prima e dopo.
    """
    print(f"▶️ Eseguo {script_name}...")
    subprocess.call(["python", script_name])
    print(f"✅ Completato {script_name}")

if __name__ == "__main__":
    print("🚀 Worker Tennis START (live 24/7)...")
    
    while True:
        # 1) Aspetta fino alle 05:00 (ora italiana)
        wait_until(5, 0)
        
        # 2) Genera CSV (tutti i match e calcoli)
        run_script("genera_csv.py")
        
        # 3) Attende 10 minuti per sicurezza (l’API OddsAPI possa aver aggiornato i dati in quell’intervallo)
        time.sleep(600)
        
        # 4) Esegue il bot che invia i segnali (con blocco notifiche su file locale)
        run_script("bot_tennis.py")
        
        # 5) Ora dorme fino al giorno successivo: riavvia ciclo while e aspetta di nuovo le 05:00
        print("😴 Worker dorme fino al giorno successivo...\n")
        # Attendi 23 ore e 50 minuti (più qualche margine): bastano 24h - 10 minuti
        time.sleep(23 * 3600 + 50 * 60)
