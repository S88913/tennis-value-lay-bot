import pandas as pd
import requests
import pytz
from datetime import datetime
from telegram import Bot
import os

# === CONFIG ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = "tennis_bets_2025.csv"
TIMEZONE = "Europe/Rome"
MIN_VALUE_ODDS = 1.70
MAX_LAY_ODDS = 3.00

bot = Bot(token=TOKEN)

def invia_messaggio(messaggio):
    bot.send_message(chat_id=CHAT_ID, text=messaggio, parse_mode='Markdown')

def leggi_file():
    try:
        df = pd.read_csv(CSV_PATH)
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize('UTC').dt.tz_convert(TIMEZONE)
        oggi = datetime.now(pytz.timezone(TIMEZONE)).date()
        df = df[df['date'].dt.date == oggi]
        return df
    except Exception as e:
        invia_messaggio(f"❌ Errore lettura file: {e}")
        return pd.DataFrame()

def crea_messaggi(df):
    messaggi = []

    for _, row in df.iterrows():
        match_data = row['date'].strftime("%d/%m %H:%M")
        torneo = row['tournament']
        p1 = row['player_1']
        p2 = row['player_2']
        q1 = row['odds_1']
        q2 = row['odds_2']
        ep1 = round(row['est_prob_1'] * 100, 1)
        ep2 = round(row['est_prob_2'] * 100, 1)
        ip1 = round(row['imp_prob_1'] * 100, 1)
        ip2 = round(row['imp_prob_2'] * 100, 1)
        tipo = row['bet_type']

        if tipo.startswith("value") and q1 >= MIN_VALUE_ODDS:
            msg = (
                f"🟢 *VALUE BET*\n"
                f"🎾 {p1} vs {p2}\n"
                f"📍 Torneo: {torneo}\n"
                f"📆 Data: {match_data}\n"
                f"💰 Quota {p1}: *{q1}*\n"
                f"📊 Prob. stimata: *{ep1}%* | Implicita: *{ip1}%*"
            )
            messaggi.append(msg)

        elif tipo.startswith("lay") and q1 <= MAX_LAY_ODDS:
            msg = (
                f"🔴 *LAY FAVORITO*\n"
                f"🎾 {p1} vs {p2}\n"
                f"📍 Torneo: {torneo}\n"
                f"📆 Data: {match_data}\n"
                f"💰 Quota Lay {p1}: *{q1}*\n"
                f"📊 Prob. stimata: *{ep1}%* | Implicita: *{ip1}%*"
            )
            messaggi.append(msg)

    return messaggi

def main():
    df = leggi_file()
    if df.empty:
        return
    messaggi = crea_messaggi(df)
    if not messaggi:
        invia_messaggio("ℹ️ Nessun segnale valido oggi.")
    for m in messaggi:
        invia_messaggio(m)

if __name__ == "__main__":
    print("🚀 Bot Tennis attivo...")
    main()
