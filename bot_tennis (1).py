
import pandas as pd
import requests
from datetime import datetime
import pytz
import os

BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID = "6146221712"
CSV_FILE = "tennis_bets_2025.csv"
NOTIFICATI_FILE = "notificati.txt"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Errore invio messaggio:", e)

def load_notificati():
    if not os.path.exists(NOTIFICATI_FILE):
        return set()
    with open(NOTIFICATI_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_notificato(id_partita):
    with open(NOTIFICATI_FILE, "a") as f:
        f.write(f"{id_partita}\n")

def converti_orario_locale(data_str):
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M")
        dt_utc = pytz.utc.localize(dt)
        dt_local = dt_utc.astimezone(pytz.timezone("Europe/Rome"))
        return dt_local.strftime("%d/%m %H:%M")
    except Exception:
        return data_str

def main():
    print("🎾 Bot Tennis attivo...")
    notificati = load_notificati()

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print("Errore lettura file:", e)
        return

    for _, row in df.iterrows():
        try:
            player_1 = row['player_1']
            player_2 = row['player_2']
            torneo = row['tournament']
            data_match = row['date'] + " 11:00"
            quota_1 = row['odds_1']
            imp_prob_1 = row['imp_prob_1']
            est_prob_1 = row['est_prob_1']
            value_diff_1 = row['value_diff_1']
            tipo_bet = row['bet_type']

            id_match = f"{player_1}_{player_2}_{data_match}_{tipo_bet}"
            if id_match in notificati:
                continue

            if tipo_bet.startswith("value"):
                messaggio = (
                    f"🟢 *VALUE BET*\n"
                    f"🎾 {player_1} vs {player_2}\n"
                    f"📍 Torneo: {torneo}\n"
                    f"📆 Data: {converti_orario_locale(data_match)}\n"
                    f"💰 Quota {player_1}: *{quota_1}*\n"
                    f"📊 Prob. stimata: *{round(est_prob_1*100,1)}%* | Implicita: *{round(imp_prob_1*100,1)}%*"
                )
                send_telegram_message(messaggio)
                save_notificato(id_match)

            elif tipo_bet.startswith("lay"):
                messaggio = (
                    f"🔴 *LAY FAVORITO*\n"
                    f"🎾 {player_1} vs {player_2}\n"
                    f"📍 Torneo: {torneo}\n"
                    f"📆 Data: {converti_orario_locale(data_match)}\n"
                    f"💰 Quota {player_1}: *{quota_1}*\n"
                    f"📊 Prob. stimata: *{round(est_prob_1*100,1)}%* | Implicita: *{round(imp_prob_1*100,1)}%*"
                )
                send_telegram_message(messaggio)
                save_notificato(id_match)
        except Exception as e:
            print("Errore riga:", e)
            continue

if __name__ == "__main__":
    main()
