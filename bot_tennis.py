import pandas as pd
from telegram import Bot
from datetime import datetime
import os
import pytz
import time

# === CONFIG ===
BOT_TOKEN   = "7359337286:AAFmojWUP9eCKcDLNj5YFb0h_LjJuhjf5uE"
CHAT_ID     = "6146221712"
CSV_FILE    = "tennis_bets_2025.csv"
NOTIF_FILE  = "notificati.txt"

bot = Bot(token=BOT_TOKEN)

def send(msg):
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def load_notificati():
    """
    Ritorna un insieme di date già notificate (una riga = una data).
    - Se il file NON esiste, restituisce insieme vuoto.
    """
    if not os.path.exists(NOTIF_FILE):
        return set()
    with open(NOTIF_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_notificato(entry):
    """
    Salva nel file NOTIF_FILE l'entry fornita (di solito la data odierna).
    Ogni chiamata aggiunge una riga.
    """
    with open(NOTIF_FILE, "a") as f:
        f.write(entry + "\n")

def main():
    # Calcola la data di oggi (fuso Europe/Rome)
    today = datetime.now(pytz.timezone("Europe/Rome")).date()

    # Carica il set di date già notificate
    notificati = load_notificati()

    # Se oggi è già stato notificato, esci subito
    if str(today) in notificati:
        print("📛 Segnali di oggi già inviati, esco.")
        return

    # Inizio invio segnali
    send("🎾 *Bot Tennis attivo...*")

    # Provo a leggere il CSV e filtrare i match di oggi
    try:
        df = pd.read_csv(CSV_FILE)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df[df["date"] == today]
    except Exception as e:
        send(f"❌ Errore lettura file: {e}")
        return

    value_count = 0
    lay_count   = 0
    messaggi    = []

    # Scorri ogni riga (match) e costruisci i messaggi value/lay
    for _, row in df.iterrows():
        tipo  = row['bet_type']
        quota = row['odds_1']
        msg   = ""

        if tipo.startswith("value") and quota >= 1.70:
            value_count += 1
            msg = (
                f"🟢 *VALUE BET*\n"
                f"🎾 {row['player_1']} vs {row['player_2']}\n"
                f"📍 {row['tournament']}\n"
                f"📆 Data: {row['date']}\n"
                f"💰 Quota: *{quota}*\n"
                f"📊 Prob: *{round(row['est_prob_1']*100,1)}%* | Implicita: *{round(row['imp_prob_1']*100,1)}%*"
            )
        elif tipo.startswith("lay") and quota <= 3.00:
            lay_count += 1
            msg = (
                f"🔴 *LAY FAVORITO*\n"
                f"🎾 {row['player_1']} vs {row['player_2']}\n"
                f"📍 {row['tournament']}\n"
                f"📆 Data: {row['date']}\n"
                f"💰 Quota Lay: *{quota}*\n"
                f"📊 Prob: *{round(row['est_prob_1']*100,1)}%* | Implicita: *{round(row['imp_prob_1']*100,1)}%*"
            )

        if msg:
            messaggi.append(msg)

    # Invia tutti i messaggi raccolti
    for m in messaggi:
        send(m)
        time.sleep(1.5)  # piccolo ritardo per non inchiodare Telegram

    # Invia riepilogo se c’è almeno un segnale
    send(f"✅ Oggi trovati: {value_count} Value, {lay_count} Lay")

    # Registra che oggi abbiamo già notificato (salva la data)
    save_notificato(str(today))

if __name__ == "__main__":
    main()
