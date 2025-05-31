import pandas as pd import requests from datetime import datetime import pytz import os

=== CONFIG ===

BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE" CHAT_ID = "6146221712" CSV_FILE = "tennis_bets_2025.csv" NOTIFICATI_FILE = "notificati.txt"

=== FUNZIONI ===

def send_telegram_message(msg): url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"} try: requests.post(url, data=payload) except Exception as e: print("Errore Telegram:", e)

def carica_notificati(): if not os.path.exists(NOTIFICATI_FILE): return set() with open(NOTIFICATI_FILE, "r") as f: return set(line.strip() for line in f.readlines())

def salva_notificato(id_partita): with open(NOTIFICATI_FILE, "a") as f: f.write(id_partita + "\n")

def formatta_data_italiana(data_str): try: data = datetime.strptime(data_str, "%Y-%m-%d") data = pytz.utc.localize(data) return data.astimezone(pytz.timezone("Europe/Rome")).strftime("%d/%m %H:%M") except: return data_str

def main(): print("\U0001F3BE Bot Tennis attivo...") notificati = carica_notificati() try: df = pd.read_csv(CSV_FILE) except Exception as e: print("Errore lettura file:", e) return

for _, row in df.iterrows():
    id_unico = f"{row['date']}_{row['player_1']}_vs_{row['player_2']}_{row['bet_type']}"
    if id_unico in notificati:
        continue

    torneo = row['tournament']
    data_match = formatta_data_italiana(row['date'])
    quota_1 = row['odds_1']
    quota_2 = row['odds_2']
    prob_stimata_1 = row['est_prob_1']
    prob_stimata_2 = row['est_prob_2']
    prob_implicita_1 = row['imp_prob_1']
    prob_implicita_2 = row['imp_prob_2']

    if "value" in row['bet_type']:
        player = row['player_1']
        msg = (
            f"🟢 *VALUE BET*\n"
            f"🎾 {row['player_1']} vs {row['player_2']}\n"
            f"📍 Torneo: {torneo}\n"
            f"📆 Data: {data_match}\n"
            f"💰 Quota {player}: {quota_1}\n"
            f"📊 Prob. stimata: {round(prob_stimata_1*100,1)}% | Implicita: {round(prob_implicita_1*100,1)}%"
        )
    elif "lay" in row['bet_type']:
        player = row['player_1']
        msg = (
            f"🔴 *LAY FAVORITO*\n"
            f"🎾 {row['player_1']} vs {row['player_2']}\n"
            f"📍 Torneo: {torneo}\n"
            f"📆 Data: {data_match}\n"
            f"💰 Quota {player}: {quota_1}\n"
            f"📊 Prob. stimata: {round(prob_stimata_1*100,1)}% | Implicita: {round(prob_implicita_1*100,1)}%"
        )
    else:
        continue

    send_telegram_message(msg)
    salva_notificato(id_unico)

if name == "main": main()

