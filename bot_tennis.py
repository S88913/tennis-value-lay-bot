=== MIGLIORATA VERSIONE CON RIEPILOGO E FILTRI ===

import pandas as pd import requests from datetime import datetime import pytz import os

=== CONFIGURAZIONE ===

BOT_TOKEN = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE" CHAT_ID = "6146221712" CSV_FILE = "tennis_bets_2025.csv" FILE_NOTIFICATI = "notificati.txt"

=== FUNZIONI UTILI ===

def send_telegram_message(message): url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"} try: response = requests.post(url, data=data) response.raise_for_status() except Exception as e: print("Errore invio Telegram:", e)

def convert_to_italian_time(utc_date): try: dt = datetime.strptime(utc_date, "%Y-%m-%d") dt = pytz.utc.localize(dt) dt_italy = dt.astimezone(pytz.timezone("Europe/Rome")) return dt_italy.strftime("%d/%m") except: return utc_date

def carica_notificati(): if not os.path.exists(FILE_NOTIFICATI): return set() with open(FILE_NOTIFICATI, "r") as f: return set(line.strip() for line in f if line.strip())

def salva_notificato(match_id): with open(FILE_NOTIFICATI, "a") as f: f.write(f"{match_id}\n")

=== MAIN ===

def main(): print("\U0001F3BE Bot Tennis attivo...")

notificati = carica_notificati()
count_value, count_lay = 0, 0
orari = []

try:
    df = pd.read_csv(CSV_FILE)
except Exception as e:
    send_telegram_message(f"Errore lettura file: {e}")
    return

for _, row in df.iterrows():
    try:
        date = row['date']
        tournament = row['tournament']
        p1 = row['player_1']
        p2 = row['player_2']
        odds_1 = float(row['odds_1'])
        odds_2 = float(row['odds_2'])
        est_prob_1 = float(row['est_prob_1'])
        est_prob_2 = float(row['est_prob_2'])
        imp_prob_1 = float(row['imp_prob_1'])
        imp_prob_2 = float(row['imp_prob_2'])
        bet_type = row['bet_type']
        match_id = f"{date}_{p1}_vs_{p2}_{bet_type}"

        if match_id in notificati:
            continue

        giorno = convert_to_italian_time(date)

        # VALUE BET
        if "value_" in bet_type:
            quota = odds_1 if "Value Player" in bet_type else odds_2
            stima = est_prob_1 if "Value Player" in bet_type else est_prob_2
            implicita = imp_prob_1 if "Value Player" in bet_type else imp_prob_2
            if 1.40 <= quota <= 3.00:
                messaggio = (
                    f"\U0001F7E2 *VALUE BET*\n"
                    f"\U0001F3BE {p1} vs {p2}\n"
                    f"\U0001F4CD Torneo: {tournament}\n"
                    f"\U0001F4C6 Data: {giorno}\n"
                    f"\U0001F4B0 Quota {p1 if 'Value Player' in bet_type else p2}: *{quota}*\n"
                    f"\U0001F4CA Prob. stimata: *{round(stima*100,1)}%* | Implicita: *{round(implicita*100,1)}%*"
                )
                send_telegram_message(messaggio)
                salva_notificato(match_id)
                count_value += 1
                orari.append(giorno)

        # LAY BET
        elif "lay_" in bet_type:
            favorito = p1 if "Lay Favorite" in bet_type else p2
            quota = odds_1 if favorito == p1 else odds_2
            stima = est_prob_1 if favorito == p1 else est_prob_2
            implicita = imp_prob_1 if favorito == p1 else imp_prob_2
            if stima < 0.60 and quota < 1.60 and (implicita - stima) > 0.15:
                messaggio = (
                    f"\U0001F534 *LAY FAVORITO*\n"
                    f"\U0001F3BE {p1} vs {p2}\n"
                    f"\U0001F4CD Torneo: {tournament}\n"
                    f"\U0001F4C6 Data: {giorno}\n"
                    f"\U0001F4B0 Quota {favorito}: *{quota}*\n"
                    f"\U0001F4CA Prob. stimata: *{round(stima*100,1)}%* | Implicita: *{round(implicita*100,1)}%*"
                )
                send_telegram_message(messaggio)
                salva_notificato(match_id)
                count_lay += 1
                orari.append(giorno)

    except Exception as e:
        print("Errore riga:", e)
        continue

# RIEPILOGO
riepilogo = (
    f"\n\U0001F4CB *Riepilogo giornaliero*\n"
    f"✅ Value Bet: {count_value}\n"
    f"❌ Lay Bet: {count_lay}\n"
    f"⏰ Match del giorno: {', '.join(sorted(set(orari)))}"
)
send_telegram_message(riepilogo)

if name == "main": main()

