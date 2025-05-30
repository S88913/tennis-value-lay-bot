# === BOT TENNIS: VALUE + LAY BET AVANZATO ===

import requests
import pandas as pd
from datetime import datetime
import pytz
import telegram

# === CONFIG ===
ODDS_API_KEY = "9d0de2745632deb584df9b2edd10176e"
BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID = "6146221712"

# === INIZIALIZZA BOT TELEGRAM ===
bot = telegram.Bot(token=BOT_TOKEN)

# === CONVERSIONE ORARIO IN FUSO ITALIANO ===
def convert_to_italian_time(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    italian_time = utc_time.astimezone(pytz.timezone("Europe/Rome"))
    return italian_time.strftime("%H:%M")

# === SCARICA MATCH TENNIS DI OGGI ===
def get_today_matches():
    url = f"https://api.the-odds-api.com/v4/sports/tennis/events/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
    response = requests.get(url)
    if response.status_code != 200:
        print("Errore nella richiesta:", response.status_code, response.text)
        return []
    return response.json()

# === ANALIZZA E FILTRA MATCH PER VALUE E LAY BET ===
def analyze_matches(matches):
    lay_signals = []
    value_signals = []

    for match in matches:
        try:
            if not match.get("bookmakers"):
                continue

            home = match['home_team']
            away = match['away_team']
            commence = match['commence_time']
            local_time = convert_to_italian_time(commence)

            for bookmaker in match['bookmakers']:
                if bookmaker['key'] != "bet365":
                    continue
                for market in bookmaker['markets']:
                    if market['key'] != "h2h":
                        continue
                    outcomes = market['outcomes']
                    if len(outcomes) != 2:
                        continue

                    p1, p2 = outcomes[0], outcomes[1]

                    # Ordina per quota
                    if p1['price'] < p2['price']:
                        fav, dog = p1, p2
                    else:
                        fav, dog = p2, p1

                    # === FILTRI LAY ===
                    if fav['price'] <= 1.60 and dog['price'] >= 2.40:
                        lay_signals.append({
                            "ora": local_time,
                            "match": f"{home} vs {away}",
                            "favorito": fav['name'],
                            "quota_fav": fav['price'],
                            "lay_su": dog['name'],
                            "quota_lay": dog['price']
                        })

                    # === FILTRI VALUE BET ===
                    if dog['price'] >= 2.00 and dog['price'] <= 3.80:
                        value_signals.append({
                            "ora": local_time,
                            "match": f"{home} vs {away}",
                            "value_su": dog['name'],
                            "quota_value": dog['price'],
                            "contro": fav['name'],
                            "quota_contrario": fav['price']
                        })

        except Exception as e:
            print("Errore nell'elaborazione:", e)
            continue

    return lay_signals, value_signals

# === INVIA MESSAGGI TELEGRAM ===
def send_signals(lay_signals, value_signals):
    if not lay_signals and not value_signals:
        bot.send_message(chat_id=CHAT_ID, text="⛔ Nessun segnale valido trovato oggi.")
        return

    # LAY BET
    for s in lay_signals:
        msg = (
            f"🚫 *LAY SICURO TENNIS*\n\n"
            f"🕒 Orario: *{s['ora']}*\n"
            f"🎾 Match: *{s['match']}*\n\n"
            f"✅ Favorito: *{s['favorito']}* (Quota {s['quota_fav']})\n"
            f"❌ Da bancare: *{s['lay_su']}* (Quota {s['quota_lay']})\n\n"
            f"💡 Strategia: Alta fiducia sul favorito\n"
            f"💰 Mercato: Betfair Exchange\n"
        )
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    # VALUE BET
    for s in value_signals:
        msg = (
            f"🔥 *VALUE BET TENNIS*\n\n"
            f"🕒 Orario: *{s['ora']}*\n"
            f"🎾 Match: *{s['match']}*\n\n"
            f"💰 Puntare su: *{s['value_su']}* (Quota {s['quota_value']})\n"
            f"⚠️ Contro: *{s['contro']}* (Quota {s['quota_contrario']})\n\n"
            f"📊 Quota interessante e sottovalutata\n"
            f"💸 Mercato: Betfair o Book classici\n"
        )
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

# === AVVIO BOT ===
def main():
    print("🟢 Avvio del bot tennis...")
    matches = get_today_matches()
    lay_signals, value_signals = analyze_matches(matches)
    send_signals(lay_signals, value_signals)
    print("✅ Completato.")

if __name__ == "__main__":
    main()
