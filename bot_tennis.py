
import requests
from datetime import datetime
import pytz
import os

# === CONFIG ===
BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID = "6146221712"
ODDS_API_KEY = "9d0de2745632deb584df9b2edd10176e"
ELO_PLAYERS = {
    "Value Player": 1700,
    "Opponent A": 1550,
    "Lay Favorite": 1480,
    "Underdog B": 1650
}

# === PARAMETRI PERSONALIZZABILI ===
MIN_VALUE_THRESHOLD = 0.12
MIN_LAY_OVERVALUATION = 0.10
TOURNAMENT_FILTER = ["ATP", "Masters", "Grand Slam"]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("✅ Inviato:", message.splitlines()[0])
    except Exception as e:
        print("❌ Errore invio:", e)

def calcola_prob_elo(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def calcola_prob_implicita(odds):
    return 1 / odds if odds > 0 else 0

def main():
    print("🚀 Bot Tennis attivo...")

    url = "https://api.the-odds-api.com/v4/sports/tennis/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("❌ Errore nella richiesta OddsAPI:", response.status_code)
        return

    data = response.json()
    for match in data:
        home = match.get("home_team")
        away = match.get("away_team")
        commence = datetime.strptime(match.get("commence_time"), "%Y-%m-%dT%H:%M:%SZ")
        commence = pytz.utc.localize(commence).astimezone(pytz.timezone("Europe/Rome"))
        orario_str = commence.strftime("%d/%m/%Y ore %H:%M")

        torneo = match.get("sport_title", "Tennis")
        if not any(t in torneo for t in TOURNAMENT_FILTER):
            continue

        elo_home = ELO_PLAYERS.get(home)
        elo_away = ELO_PLAYERS.get(away)
        if not elo_home or not elo_away:
            continue

        prob_home = calcola_prob_elo(elo_home, elo_away)
        prob_away = calcola_prob_elo(elo_away, elo_home)

        for book in match["bookmakers"]:
            if book["key"] != "pinnacle":
                continue
            for market in book["markets"]:
                if market["key"] != "h2h":
                    continue
                outcomes = market["outcomes"]
                odds = {o["name"]: o["price"] for o in outcomes}

                # VALUE BET
                for player in [home, away]:
                    prob_stimata = prob_home if player == home else prob_away
                    quota = odds.get(player)
                    if not quota:
                        continue
                    prob_implicita = calcola_prob_implicita(quota)
                    value = prob_stimata - prob_implicita
                    if value >= MIN_VALUE_THRESHOLD:
                        messaggio = (
                            f"🟢 *VALUE BET*
"
                            f"🎾 {home} vs {away}
"
                            f"📍 Torneo: {torneo}
"
                            f"📆 Data: {orario_str}
"
                            f"📈 Elo: {elo_home} vs {elo_away}
"
                            f"💰 Quota {player}: *{quota}*
"
                            f"📊 Prob. stimata: *{round(prob_stimata*100)}%* | Implicita: *{round(prob_implicita*100)}%*"
                        )
                        send_telegram_message(messaggio)

                # LAY BET
                for player in [home, away]:
                    prob_stimata = prob_home if player == home else prob_away
                    quota = odds.get(player)
                    if not quota:
                        continue
                    prob_implicita = calcola_prob_implicita(quota)
                    sovrastima = prob_implicita - prob_stimata
                    if sovrastima >= MIN_LAY_OVERVALUATION:
                        messaggio = (
                            f"🔴 *LAY FAVORITO*
"
                            f"🎾 {home} vs {away}
"
                            f"📍 Torneo: {torneo}
"
                            f"📆 Data: {orario_str}
"
                            f"📈 Elo: {elo_home} vs {elo_away}
"
                            f"💰 Quota {player}: *{quota}*
"
                            f"📊 Prob. stimata: *{round(prob_stimata*100)}%* | Implicita: *{round(prob_implicita*100)}%*"
                        )
                        send_telegram_message(messaggio)

if __name__ == "__main__":
    main()
