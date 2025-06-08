#!/usr/bin/env python3
import os
import requests
from telegram import Bot
from datetime import datetime
import pytz
import time
from dotenv import load_dotenv

# === CARICAMENTO CONFIG ===
load_dotenv()  # legge .env se presente
BOT_TOKEN       = os.getenv("BOT_TOKEN")
CHAT_ID         = os.getenv("CHAT_ID")
API_URL         = os.getenv("MATCHES_API_URL")
API_KEY         = os.getenv("MATCHES_API_KEY")
NOTIF_FILE      = "notificati.txt"

MIN_VALUE       = 1.70
MAX_LAY         = 3.00

bot = Bot(token=BOT_TOKEN)

def send(msg: str):
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

def load_notificati():
    if not os.path.exists(NOTIF_FILE):
        return set()
    with open(NOTIF_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def save_notificato(entry: str):
    with open(NOTIF_FILE, "a") as f:
        f.write(entry + "\n")

def fetch_matches():
    """Chiama la tua API privata e ritorna lista di match."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(API_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def main():
    tz         = pytz.timezone("Europe/Rome")
    today      = datetime.now(tz).date()
    s_today    = str(today)
    notificati = load_notificati()

    # if already sent today, exit
    if s_today in notificati:
        print("🔒 Segnali di oggi già inviati, esco.")
        return

    send("🎾 *Bot Tennis attivo…*")

    try:
        matches = fetch_matches()
    except Exception as e:
        send(f"❌ Errore API: {e}")
        return

    value_count, lay_count = 0, 0
    for m in matches:
        if m.get("date") != s_today:
            continue

        bt   = m.get("bet_type","")
        q1   = float(m.get("odds_1",0))
        p1   = m.get("player_1")
        p2   = m.get("player_2")
        tour = m.get("tournament")
        ep1  = float(m.get("est_prob_1",0))
        ip1  = float(m.get("imp_prob_1",0))

        if bt.startswith("value") and q1 >= MIN_VALUE:
            value_count += 1
            send(
                f"🟢 *VALUE BET*\n"
                f"🎾 {p1} vs {p2}\n"
                f"📍 {tour}\n"
                f"📆 Data: {s_today}\n"
                f"💰 Quota: *{q1}*\n"
                f"📊 Prob: *{ep1*100:.1f}%* | Implicita: *{ip1*100:.1f}%*"
            )
            time.sleep(1.5)

        elif bt.startswith("lay") and q1 <= MAX_LAY:
            lay_count += 1
            send(
                f"🔴 *LAY FAVORITO*\n"
                f"🎾 {p1} vs {p2}\n"
                f"📍 {tour}\n"
                f"📆 Data: {s_today}\n"
                f"💰 Quota Lay: *{q1}*\n"
                f"📊 Prob: *{ep1*100:.1f}%* | Implicita: *{ip1*100:.1f}%*"
            )
            time.sleep(1.5)

    # riepilogo
    if value_count or lay_count:
        send(f"✅ Oggi trovati: {value_count} Value, {lay_count} Lay")
    else:
        send("✅ Oggi non ci sono segnali validi.")

    save_notificato(s_today)

if __name__ == "__main__":
    main()
