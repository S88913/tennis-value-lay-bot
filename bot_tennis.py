
import os
import requests
import pandas as pd
from datetime import datetime
from pytz import timezone

# === CONFIG ===
TELEGRAM_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID = "6146221712"
ODDS_API_KEY = "9d0de2745632deb584df9b2edd10176e"
CSV_PATH = "atp_matches_2024.csv"
XLSX_PATH_2024 = "2024 (1).xlsx"
XLSX_PATH_2025 = "2025 (3).xlsx"

# === FUNZIONI TELEGRAM ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Errore Telegram:", e)

# === FUNZIONI UTILI ===
def get_matches_today():
    url = "https://api.the-odds-api.com/v4/sports/tennis/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        res = requests.get(url, params=params)
        return res.json()
    except Exception as e:
        print("Errore chiamata OddsAPI:", e)
        return []

def convert_to_rome_time(utc_dt_str):
    try:
        utc_dt = datetime.fromisoformat(utc_dt_str.replace("Z", "+00:00"))
        rome = timezone("Europe/Rome")
        return utc_dt.astimezone(rome).strftime("%d/%m %H:%M")
    except:
        return "?"

# === MAIN ===
def main():
    send_telegram_message("🎾 Bot Tennis attivo...")

    # Leggo i dati storici (semplificato)
    try:
        df_csv = pd.read_csv(CSV_PATH)
        df_24 = pd.read_excel(XLSX_PATH_2024)
        df_25 = pd.read_excel(XLSX_PATH_2025)
    except Exception as e:
        send_telegram_message(f"Errore lettura file: {e}")
        return

    matches = get_matches_today()
    if not matches:
        send_telegram_message("❌ Nessun match trovato oggi.")
        return

    segnali = []
    for match in matches:
        try:
            teams = match['bookmakers'][0]['markets'][0]['outcomes']
            if len(teams) < 2:
                continue
            p1 = teams[0]
            p2 = teams[1]
            quota_p1 = float(p1['price'])
            quota_p2 = float(p2['price'])

            implicita_p1 = round(100 / quota_p1, 1)
            implicita_p2 = round(100 / quota_p2, 1)

            # Simulazione probabilità stimata semplificata
            prob_stimata_p1 = implicita_p1 + 10
            prob_stimata_p2 = implicita_p2 - 10

            orario = convert_to_rome_time(match['commence_time'])
            torneo = match['sport_title']

            if prob_stimata_p1 > implicita_p1 + 5:
                segnali.append(f"🟢 *VALUE BET*\n🎾 {p1['name']} vs {p2['name']}\n📍 Torneo: {torneo}\n📆 Data: {orario}\n💰 Quota {p1['name']}: *{quota_p1}*\n📊 Prob. stimata: *{prob_stimata_p1}%* | Implicita: *{implicita_p1}%*")

            if implicita_p1 > prob_stimata_p1 + 10:
                segnali.append(f"🔴 *LAY FAVORITO*\n🎾 {p1['name']} vs {p2['name']}\n📍 Torneo: {torneo}\n📆 Data: {orario}\n💰 Quota {p1['name']}: *{quota_p1}*\n📊 Prob. stimata: *{prob_stimata_p1}%* | Implicita: *{implicita_p1}%*")

        except Exception as e:
            print("Errore elaborazione match:", e)
            continue

    if segnali:
        for segnale in segnali:
            send_telegram_message(segnale)
    else:
        send_telegram_message("❌ Nessun segnale rilevante oggi.")

if __name__ == "__main__":
    main()
