import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# === CONFIGURAZIONE ===
TOKEN = '7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE'
CHAT_ID = '6146221712'
CSV_PATH = 'tennis_bets_2025.csv'
LOG_FILE = 'notificati.txt'
TIMEZONE = 'Europe/Rome'

# === FUNZIONI ===

def invia_messaggio(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    requests.post(url, data=data)

def leggi_notificati():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def salva_notificato(match_id):
    with open(LOG_FILE, 'a') as f:
        f.write(match_id + '\n')

def formatta_valore(row):
    return (
        f"🟢 *VALUE BET*\n"
        f"🎾 {row['player_1']} vs {row['player_2']}\n"
        f"📍 Torneo: {row['tournament']}\n"
        f"📆 Data: {row['date']} {row.get('time', '13:00')}\n"
        f"💰 Quota {row['player_1']}: *{row['odds_1']}*\n"
        f"📊 Prob. stimata: *{float(row['est_prob_1'])*100:.1f}%* | Implicita: *{float(row['imp_prob_1'])*100:.1f}%*"
    )

def formatta_lay(row):
    return (
        f"🔴 *LAY FAVORITO*\n"
        f"🎾 {row['player_1']} vs {row['player_2']}\n"
        f"📍 Torneo: {row['tournament']}\n"
        f"📆 Data: {row['date']} {row.get('time', '13:00')}\n"
        f"💰 Quota {row['player_1']}: *{row['odds_1']}*\n"
        f"📊 Prob. stimata: *{float(row['est_prob_1'])*100:.1f}%* | Implicita: *{float(row['imp_prob_1'])*100:.1f}%*"
    )

def oggi_iso():
    oggi = datetime.now(pytz.timezone(TIMEZONE))
    return oggi.strftime('%Y-%m-%d')

# === AVVIO ===
invia_messaggio("🎾 Bot Tennis attivo...")

try:
    df = pd.read_csv(CSV_PATH)
    df = df[df['date'] == oggi_iso()]
    notificati = leggi_notificati()

    for _, row in df.iterrows():
        match_id = f"{row['date']}_{row['player_1']}_vs_{row['player_2']}"
        if match_id in notificati:
            continue

        if row['bet_type'].startswith('value'):
            messaggio = formatta_valore(row)
        elif row['bet_type'].startswith('lay'):
            messaggio = formatta_lay(row)
        else:
            continue

        invia_messaggio(messaggio)
        salva_notificato(match_id)

except Exception as e:
    invia_messaggio(f"❌ Errore: {str(e)}")
