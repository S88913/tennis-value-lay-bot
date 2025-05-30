# === MIGLIORATA VERSIONE CON RIEPILOGO E FILTRI ===

import requests
import pandas as pd
from datetime import datetime
import pytz
import time
import telegram

# Config
ODDS_API_KEY = "9d0de2745632deb584df9b2edd10176e"
BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID = "6146221712"

# Inizializza bot Telegram
bot = telegram.Bot(token=BOT_TOKEN)

# Funzione per convertire l’orario UTC in ora italiana
def convert_to_italian_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    italian_time = utc_time.astimezone(pytz.timezone("Europe/Rome"))
    return italian_time.strftime("%H:%M")

# Scarica partite di oggi
def get_today_matches():
    url = f"https://api.the-odds-api.com/v4/sports/tennis/events/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
    response = requests.get(url)
    if response.status_code != 200:
        print("Errore nella richiesta:", response.status_code, response.text)
        return []
    return response.json()

# Analizza e filtra i match
def analyze_matches(matches):
    segnali = []

    for match in matches:
        try:
            home = match['home_team']
            away = match['away_team']
            commence = match['commence_time']
            time_local = convert_to_italian_time(commence)

            # Quote disponibili?
            if not match.get("bookmakers"):
                continue

            for bookmaker in match['bookmakers']:
                if bookmaker['key'] == "bet365":
                    for market in bookmaker['markets']:
                        if market['key'] == "h2h":
                            outcomes = market['outcomes']
                            if len(outcomes) != 2:
                                continue

                            player1 = outcomes[0]
                            player2 = outcomes[1]

                            # Favorito e quota sfavorito
                            if player1['price'] < player2['price']:
                                favorito = player1
                                sfavorito = player2
                            else:
                                favorito = player2
                                sfavorito = player1

                            quota_favorito = favorito['price']
                            quota_sfavorito = sfavorito['price']

                            # FILTRI
                            if quota_favorito <= 1.50 and quota_sfavorito >= 2.50:
                                segnali.append({
                                    "ora": time_local,
                                    "match": f"{home} vs {away}",
                                    "favorito": favorito['name'],
                                    "quota": quota_favorito,
                                    "lay_su": sfavorito['name'],
                                    "quota_lay": quota_sfavorito
                                })
        except Exception as e:
            print("Errore durante l'analisi di un match:", e)
            continue

    return segnali

# Invia segnale Telegram
def send_signal(signals):
    if not signals:
        print("Nessun segnale valido trovato.")
        return

    for s in signals:
        messaggio = (
            f"🎾 *LAY SICURO TENNIS*\n\n"
            f"🕒 Orario: *{s['ora']}*\n"
            f"🆚 Match: *{s['match']}*\n\n"
            f"✅ Favorito: *{s['favorito']}* (Quota {s['quota']})\n"
            f"❌ Da bancare: *{s['lay_su']}* (Quota {s['quota_lay']})\n\n"
            f"⚠️ Alta discrepanza tra favorito e sfavorito\n"
        )
        bot.send_message(chat_id=CHAT_ID, text=messaggio, parse_mode=telegram.ParseMode.MARKDOWN)

# Main loop (eseguito solo una volta al giorno)
def main():
    print("🟢 Avvio del bot tennis...")
    matches = get_today_matches()
    signals = analyze_matches(matches)
    send_signal(signals)
    print("✅ Completato.")

if __name__ == "__main__":
    main()
