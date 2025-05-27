
import os
import pandas as pd
from datetime import datetime
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_FILE = "tennis_bets_2025.csv"
FILE_NOTIFICATI = "notificati.txt"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Errore invio messaggio:", e)

def carica_notificati():
    if not os.path.exists(FILE_NOTIFICATI):
        return set()
    with open(FILE_NOTIFICATI, "r") as f:
        return set(line.strip() for line in f if line.strip())

def salva_notificato(match_id):
    with open(FILE_NOTIFICATI, "a") as f:
        f.write(f"{match_id}\n")

def filtra_e_notifica():
    try:
        df = pd.read_csv(CSV_FILE)
        notificati = carica_notificati()
        oggi = datetime.utcnow().date()

        for _, row in df.iterrows():
            match_date = pd.to_datetime(row["date"]).date()
            match_id = f"{row['player_1']}_vs_{row['player_2']}_{match_date}"

            if match_date != oggi or match_id in notificati or row["bet_type"] == "none":
                continue

            if "value" in row["bet_type"]:
                emoji = "🟢"
                tipo = "VALUE BET"
                giocatore = row["bet_type"].split("_", 1)[1]
            elif "lay" in row["bet_type"]:
                emoji = "🔴"
                tipo = "LAY FAVORITO"
                giocatore = row["bet_type"].split("_", 1)[1]
            else:
                continue

            messaggio = (
                f"{emoji} *{tipo}*\n"
                f"🎾 {row['player_1']} vs {row['player_2']}\n"
                f"📍 Torneo: {row['tournament']}\n"
                f"📆 Data: {match_date.strftime('%d/%m/%Y')}\n"
                f"📈 Elo: {int(row['elo_1'])} vs {int(row['elo_2'])}\n"
                f"💰 Quota {giocatore}: *{row['odds_1'] if giocatore == row['player_1'] else row['odds_2']}*\n"
                f"📊 Prob. stimata: *{row['est_prob_1'] if giocatore == row['player_1'] else row['est_prob_2']:.0%}* | "
                f"Implicita: *{row['imp_prob_1'] if giocatore == row['player_1'] else row['imp_prob_2']:.0%}*"
            )

            send_telegram_message(messaggio)
            salva_notificato(match_id)

    except Exception as e:
        print("❌ Errore generale:", e)

if __name__ == "__main__":
    filtra_e_notifica()
