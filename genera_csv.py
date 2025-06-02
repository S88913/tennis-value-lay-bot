
import requests
import pandas as pd
from datetime import datetime
import pytz

# === CONFIG ===
API_KEY = "9d0de2745632deb584df9b2edd10176e"  # OddsAPI gratuita
BASE_URL = "https://api.the-odds-api.com/v4/sports/tennis/events"
REGION = "eu"
MARKET = "h2h"
CSV_FILE = "tennis_bets_2025.csv"

# === FUNZIONI DI SUPPORTO ===
def calcola_probabilità(quota):
    return round(1 / quota, 4) if quota else 0

def stima_probabilità_elo(elo1, elo2):
    diff = elo1 - elo2
    prob1 = 1 / (1 + 10 ** (-diff / 400))
    return round(prob1, 2), round(1 - prob1, 2)

def tipo_scommessa(value_diff1, value_diff2, player1):
    if value_diff1 > 0.05:
        return f"value_{player1}"
    elif value_diff1 < -0.08:
        return f"lay_{player1}"
    return ""

# === GENERA FILE ===
def genera_file():
    print("📡 Recupero dati da OddsAPI...")
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        print("❌ Errore API OddsAPI:", response.status_code, response.text)
        return

    events = response.json()
    print(f"✅ {len(events)} eventi trovati")

    dati = []
    oggi = datetime.now(pytz.timezone("Europe/Rome")).date()

    for event in events:
        try:
            nome1, nome2 = event['participants'][0], event['participants'][1]
            commence_time = datetime.fromisoformat(event['commence_time'].replace("Z", "+00:00"))
            data_match = commence_time.astimezone(pytz.timezone("Europe/Rome")).date()

            if data_match != oggi:
                continue

            bookmaker = event['bookmakers'][0]
            outcomes = bookmaker['markets'][0]['outcomes']

            quota1 = next(o['price'] for o in outcomes if o['name'] == nome1)
            quota2 = next(o['price'] for o in outcomes if o['name'] == nome2)

            imp1 = calcola_probabilità(quota1)
            imp2 = calcola_probabilità(quota2)

            # Valori ELO fittizi per testing
            elo1, elo2 = 1800, 1750

            est1, est2 = stima_probabilità_elo(elo1, elo2)
            value1 = est1 - imp1
            value2 = est2 - imp2

            bet = tipo_scommessa(value1, value2, nome1)
            if bet == "":
                continue

            genere = "WTA" if any(n in nome1 for n in ["Swiatek", "Sabalenka", "Gauff", "Svitolina"]) else "ATP"
            torneo = f"{genere} French Open"

            dati.append({
                "date": str(data_match),
                "tournament": torneo,
                "player_1": nome1,
                "player_2": nome2,
                "elo_1": elo1,
                "elo_2": elo2,
                "odds_1": quota1,
                "odds_2": quota2,
                "imp_prob_1": imp1,
                "imp_prob_2": imp2,
                "est_prob_1": est1,
                "est_prob_2": est2,
                "value_diff_1": value1,
                "value_diff_2": value2,
                "bet_type": bet
            })

        except Exception as e:
            print(f"⚠️ Errore evento: {e}")
            continue

    if not dati:
        print("🚫 Nessun segnale valido oggi.")
        return

    df = pd.DataFrame(dati)
    df.to_csv(CSV_FILE, index=False)
    print(f"📁 File salvato: {CSV_FILE}")

if __name__ == "__main__":
    genera_file()
