import pandas as pd
from telegram import Bot
from datetime import datetime
import os
import pytz

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_FILE = "tennis_bets_2025.csv"
NOTIF_FILE = "notificati.txt"

bot = Bot(token=BOT_TOKEN)

def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def load_notificati():
    if not os.path.exists(NOTIF_FILE):
        return set()
    with open(NOTIF_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_notificato(id_match):
    with open(NOTIF_FILE, "a") as f:
        f.write(id_match + "\n")

def main():
    send("🎾 *Bot Tennis attivo...*")
    try:
        df = pd.read_csv(CSV_FILE)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        today = datetime.now(pytz.timezone("Europe/Rome")).date()
        df = df[df["date"] == today]
    except Exception as e:
        send(f"❌ Errore lettura file: {e}")
        return

    notificati = load_notificati()
    value_count = 0
    lay_count = 0

    for _, row in df.iterrows():
        match_id = f"{row['player_1']}_{row['player_2']}_{row['date']}"
        if match_id in notificati:
            continue

        tipo = row['bet_type']
        quota = row['odds_1']
        msg = ""

        if tipo.startswith("value") and quota >= 1.70:
            value_count += 1
            msg = (
                f"🟢 *VALUE BET*\n"
                f"🎾 {row['player_1']} vs {row['player_2']}\n"
                f"📍 {row['tournament']}\n"
                f"📆 Data: {row['date']}\n"
                f"💰 Quota: *{quota}*\n"
                f"📊 Prob: *{round(row['est_prob_1']*100,1)}%* | Implicita: *{round(row['imp_prob_1']*100,1)}%*"
            )
        elif tipo.startswith("lay") and quota <= 3.00:
            lay_count += 1
            msg = (
                f"🔴 *LAY FAVORITO*\n"
                f"🎾 {row['player_1']} vs {row['player_2']}\n"
                f"📍 {row['tournament']}\n"
                f"📆 Data: {row['date']}\n"
                f"💰 Quota Lay: *{quota}*\n"
                f"📊 Prob: *{round(row['est_prob_1']*100,1)}%* | Implicita: *{round(row['imp_prob_1']*100,1)}%*"
            )

        if msg:
            send(msg)
            save_notificato(match_id)

    send(f"✅ Oggi trovati: *{value_count} Value*, *{lay_count} Lay*")

if __name__ == "__main__":
    main()
