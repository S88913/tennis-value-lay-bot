import requests
import pandas as pd
from datetime import datetime
import pytz
import os

# === CONFIG ===
ODDS_API_KEY = os.getenv("ODDS_API_KEY") or "9d0de2745632deb584df9b2edd10176e"  # usa la tua oppure quella free
REGIONS = "eu"  # Europa
MARKETS = "h2h"  # Testa a testa
SPORT = "tennis"

# === UTILS ===
def get_today_iso_date():
    tz = pytz.timezone("Europe/Rome")
    return datetime.now(tz).strftime("%Y-%m-%d")

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?regions={REGIONS}&markets={MARKETS}&apiKey={ODDS_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Errore API OddsAPI: {response.status_code} - {response.text}")
    return response.json()

def parse_matches(data):
    matches = []
    for match in data:
        try:
            if not match.get("bookmakers"):
                continue
            bookmaker = match["bookmakers"][0]
            markets = bookmaker["markets"][0]
            outcomes = markets["outcomes"]

            player_1 = outcomes[0]["name"]
            odds_1 = outcomes[0]["price"]
            player_2 = outcomes[1]["name"]
            odds_2 = outcomes[1]["price"]

            imp_prob_1 = 1 / odds_1
            imp_prob_2 = 1 / odds_2

            # Placeholder ELO logic (fake prob): favorisce la quota più bassa leggermente
            est_prob_1 = imp_prob_1 + 0.1 if imp_prob_1 < imp_prob_2 else imp_prob_1 - 0.1
            est_prob_2 = 1 - est_prob_1

            value_diff_1 = est_prob_1 - imp_prob_1
            value_diff_2 = est_prob_2 - imp_prob_2

            bet_type = ""
            if odds_1 >= 1.70 and value_diff_1 > 0.05:
                bet_type = f"value_{player_1}"
            elif odds_1 <= 3.00 and value_diff_1 < -0.08:
                bet_type = f"lay_{player_1}"

            matches.append({
                "date": get_today_iso_date(),
                "tournament": match.get("league", {}).get("name", ""),
                "player_1": player_1,
                "player_2": player_2,
                "odds_1": odds_1,
                "odds_2": odds_2,
                "imp_prob_1": round(imp_prob_1, 3),
                "imp_prob_2": round(imp_prob_2, 3),
                "est_prob_1": round(est_prob_1, 3),
                "est_prob_2": round(est_prob_2, 3),
                "value_diff_1": round(value_diff_1, 3),
                "value_diff_2": round(value_diff_2, 3),
                "bet_type": bet_type
            })
        except Exception as e:
            print(f"Errore parsing match: {e}")
            continue
    return matches

if __name__ == "__main__":
    print("📥 Scarico quote da OddsAPI...")
    try:
        odds_data = fetch_odds()
        print(f"✅ Ricevuti {len(odds_data)} match")
        matches = parse_matches(odds_data)
        df = pd.DataFrame(matches)
        df.to_csv("tennis_bets_2025.csv", index=False)
        print("💾 File 'tennis_bets_2025.csv' aggiornato con success! ✅")
    except Exception as e:
        print(f"❌ Errore: {e}")
