import requests
import pandas as pd
from datetime import datetime
import pytz

# === CONFIG ===
API_KEY = "9d0de2745632deb584df9b2edd10176e"  # OddsAPI gratuita
OUTPUT_FILE = "tennis_bets_2025.csv"
MIN_VALUE_ODDS = 1.70
MAX_LAY_ODDS = 3.00

def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/tennis/events/?regions=eu&markets=h2h&oddsFormat=decimal&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("Errore API:", e)
        return []

def calc_estimated_prob(elo1, elo2):
    return 1 / (1 + 10 ** ((elo2 - elo1) / 400))

def build_csv():
    today = datetime.now(pytz.timezone("Europe/Rome")).date()
    matches = get_matches()
    rows = []

    for match in matches:
        try:
            date = match["commence_time"][:10]
            if date != str(today):
                continue

            teams = match.get("teams", [])
            if len(teams) != 2:
                continue

            p1, p2 = teams
            odds_data = match["bookmakers"][0]["markets"][0]["outcomes"]
            o1 = odds_data[0]
            o2 = odds_data[1]
            q1 = float(o1["price"])
            q2 = float(o2["price"])
            ip1 = round(1 / q1, 4)
            ip2 = round(1 / q2, 4)
            elo1 = 1900
            elo2 = 1800
            ep1 = round(calc_estimated_prob(elo1, elo2), 4)
            ep2 = round(1 - ep1, 4)
            vd1 = round(ep1 - ip1, 4)
            vd2 = round(ep2 - ip2, 4)

            bet_type = ""
            if q1 >= MIN_VALUE_ODDS and vd1 >= 0.05:
                bet_type = f"value_{p1}"
            elif q1 <= MAX_LAY_ODDS and vd1 <= -0.10:
                bet_type = f"lay_{p1}"

            if bet_type:
                rows.append([
                    date, match["sport_title"], p1, p2, elo1, elo2,
                    q1, q2, ip1, ip2, ep1, ep2, vd1, vd2, bet_type
                ])
        except Exception as e:
            print("Errore parsing:", e)

    df = pd.DataFrame(rows, columns=[
        "date", "tournament", "player_1", "player_2", "elo_1", "elo_2",
        "odds_1", "odds_2", "imp_prob_1", "imp_prob_2",
        "est_prob_1", "est_prob_2", "value_diff_1", "value_diff_2", "bet_type"
    ])
    df.to_csv(OUTPUT_FILE, index=False)
    print("✅ File generato con", len(df), "segnali")

if __name__ == "__main__":
    build_csv()
