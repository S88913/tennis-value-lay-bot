import requests
import pandas as pd
from datetime import datetime
import pytz
import os

# === CONFIG ===
API_KEY    = "9d0de2745632deb584df9b2edd10176e"
BASE_URL   = "https://api.the-odds-api.com/v4/sports/tennis/events"
REGION     = "eu"
MARKET     = "h2h"
CSV_FILE   = "tennis_bets_2025.csv"

def calcola_probabilità(quota):
    return round(1/quota, 4) if quota else 0

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

def genera_file():
    print("📡 Recupero dati OddsAPI...")
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }
    r = requests.get(BASE_URL, params=params)
    if r.status_code != 200:
        print(f"❌ Errore API: {r.status_code} - {r.text}")
        return
    events = r.json()
    print(f"✅ {len(events)} eventi trovati")

    dati = []
    oggi = datetime.now(pytz.timezone("Europe/Rome")).date()

    for ev in events:
        try:
            n1, n2 = ev["participants"][0], ev["participants"][1]
            ct = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00"))
            data_match = ct.astimezone(pytz.timezone("Europe/Rome")).date()
            if data_match != oggi:
                continue

            bookmaker = ev["bookmakers"][0]
            outcomes  = bookmaker["markets"][0]["outcomes"]
            quota1    = next(o["price"] for o in outcomes if o["name"] == n1)
            quota2    = next(o["price"] for o in outcomes if o["name"] == n2)
            imp1      = calcola_probabilità(quota1)
            imp2      = calcola_probabilità(quota2)

            # ELO falsi per esempio (15/06: da sostituire con ELO reali)
            elo1, elo2 = 1800, 1750
            est1, est2 = stima_probabilità_elo(elo1, elo2)
            val1       = est1 - imp1
            val2       = est2 - imp2

            bet = tipo_scommessa(val1, val2, n1)
            if bet == "":
                continue

            # Decide torneo in base al nome del giocatore (ATP/WTA semplificato)
            genere  = "WTA" if any(x in n1 for x in ["Swiatek","Sabalenka","Gauff","Svitolina"]) else "ATP"
            torneo  = f"{genere} French Open"

            dati.append({
                "date": str(data_match),
                "tournament": torneo,
                "player_1": n1,
                "player_2": n2,
                "elo_1": elo1,
                "elo_2": elo2,
                "odds_1": quota1,
                "odds_2": quota2,
                "imp_prob_1": imp1,
                "imp_prob_2": imp2,
                "est_prob_1": est1,
                "est_prob_2": est2,
                "value_diff_1": val1,
                "value_diff_2": val2,
                "bet_type": bet
            })
        except Exception as e:
            print(f"⚠️ Errore parsing evento: {e}")
            continue

    if not dati:
        print("🚫 Nessun segnale valido oggi.")
        # Sovrascrivi comunque per chiarezza (file vuoto)
        pd.DataFrame(dati).to_csv(CSV_FILE, index=False)
        return

    df = pd.DataFrame(dati)
    df.to_csv(CSV_FILE, index=False)
    print(f"📁 {CSV_FILE} creato con {len(df)} righe.")

if __name__ == "__main__":
    genera_file()
