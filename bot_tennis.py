=== MIGLIORATA VERSIONE CON RIEPILOGO E FILTRI ===

import pandas as pd import requests from datetime import datetime import pytz

=== CONFIG ===

BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE" CHAT_ID = "6146221712" CSV_FILE = "tennis_bets_2025.csv"

def send_telegram_message(message): url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"} try: requests.post(url, data=data) except Exception as e: print("Errore invio messaggio:", e)

def carica_dati(): try: df = pd.read_csv(CSV_FILE) df["date"] = pd.to_datetime(df["date"]) oggi = pd.Timestamp.now(tz="Europe/Rome").date() df = df[df["date"].dt.date == oggi] return df except Exception as e: send_telegram_message(f"Errore lettura file: {e}") return pd.DataFrame()

def format_orario(): ora = datetime.now(pytz.timezone("Europe/Rome")).strftime("%d/%m/%Y %H:%M") return ora

def invia_segnali(): df = carica_dati() if df.empty: return

count_value = 0
count_lay = 0
orari_set = set()

for _, row in df.iterrows():
    match_date = pd.to_datetime(row["date"])
    orario_match = match_date.strftime("%d/%m %H:%M")
    orari_set.add(orario_match)

    torneo = row["tournament"]
    p1 = row["player_1"]
    p2 = row["player_2"]
    quota1 = row["odds_1"]
    quota2 = row["odds_2"]
    est_prob_1 = row["est_prob_1"]
    imp_prob_1 = row["imp_prob_1"]
    est_prob_2 = row["est_prob_2"]
    imp_prob_2 = row["imp_prob_2"]
    bet_type = row["bet_type"]

    if bet_type.startswith("value"):
        count_value += 1
        quota = quota1 if "Value Player" in bet_type else quota2
        prob_stimata = est_prob_1 if "Value Player" in bet_type else est_prob_2
        prob_implicita = imp_prob_1 if "Value Player" in bet_type else imp_prob_2
        value_player = p1 if "Value Player" in bet_type else p2
        msg = (
            f"🟢 *VALUE BET*\n"
            f"🎾 {p1} vs {p2}\n"
            f"📍 Torneo: {torneo}\n"
            f"📆 Data: {orario_match}\n"
            f"💰 Quota {value_player}: *{quota}*\n"
            f"📊 Prob. stimata: *{round(prob_stimata*100,1)}%* | Implicita: *{round(prob_implicita*100,1)}%*"
        )
        send_telegram_message(msg)

    elif bet_type.startswith("lay"):
        quota = quota1 if "Lay Favorite" in bet_type else quota2
        prob_stimata = est_prob_1 if "Lay Favorite" in bet_type else est_prob_2
        prob_implicita = imp_prob_1 if "Lay Favorite" in bet_type else imp_prob_2
        if prob_stimata < 0.60 and 1.30 <= quota <= 1.60 and (prob_implicita - prob_stimata) > 0.15:
            count_lay += 1
            lay_player = p1 if "Lay Favorite" in bet_type else p2
            msg = (
                f"🔴 *LAY FAVORITO*\n"
                f"🎾 {p1} vs {p2}\n"
                f"📍 Torneo: {torneo}\n"
                f"📆 Data: {orario_match}\n"
                f"💰 Quota {lay_player}: *{quota}*\n"
                f"📊 Prob. stimata: *{round(prob_stimata*100,1)}%* | Implicita: *{round(prob_implicita*100,1)}%*"
            )
            send_telegram_message(msg)

# Riepilogo finale
riepilogo = (
    f"📋 *RIEPILOGO GIORNALIERO*\n"
    f"🟢 Value Bet inviate: *{count_value}*\n"
    f"🔴 Lay Bet inviate: *{count_lay}*\n"
    f"📅 Match previsti oggi: *{len(orari_set)}* orari diversi\n"
    f"🕒 Orario attuale: {format_orario()}"
)
send_telegram_message(riepilogo)

if name == "main": print("🎾 Bot Tennis attivo...") invia_segnali()

