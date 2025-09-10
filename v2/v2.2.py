import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
import schedule
import time

# ======== CONFIGURATION ========
tickers = ["HDFCBANK.NS", "^NSEI", "^NSEBANK", "ASIANPAINT.NS", "RELIANCE.NS"]
LOG_FILE = "stock_signals_log.txt"

# Email config
EMAIL_SENDER = "nuggagamer2020@gmail.com"
EMAIL_RECEIVER = "narendra.waghmare62@gmail.com"
EMAIL_PASSWORD = "fbze oopu bdao defv"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# ===============================


def get_stock_data(ticker, period="3mo", interval="1h"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    df.dropna(inplace=True)
    return df

def apply_ema_indicators(df):
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['EMA55'] = df['Close'].ewm(span=55, adjust=False).mean()
    return df

def generate_triple_ema_signal(df):
    ema9 = df['EMA9'].iloc[-1]
    ema21 = df['EMA21'].iloc[-1]
    ema55 = df['EMA55'].iloc[-1]

    if ema9 > ema21 and ema9 > ema55:
        return "BUY STOCK"
    elif ema9 < ema21 and ema9 < ema55:
        return "SELL STOCK"
    else:
        return "HOLD"

def log_signal_to_text(ticker, signal, df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    close = df['Close'].iloc[-1]
    log_line = f"[{now}] Ticker: {ticker} | Signal: {signal} | PRICE: {close:.2f}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)

# ✅ NEW: Send one email with all signals
def send_email_alert(all_signals):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[Stock Alert] EMA Signals Summary - {now}"

    body_lines = [f"📈 EMA Signal Summary - {now}\n"]
    for stock in all_signals:
        line = f"{stock['ticker']} ------→ {stock['signal']} ====> ₹{stock['price']:.2f}"
        body_lines.append(line)

    body = "\n".join(body_lines)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Summary email sent successfully.")
    except Exception as e:
        print(f"⚠️ Failed to send summary email: {e}")

# 🔄 MODIFIED: Run bot for all tickers and collect signals
def run_bot_for_all_tickers(ticker_list):
    all_signals = []

    for ticker in ticker_list:
        try:
            df = get_stock_data(ticker)
            df = apply_ema_indicators(df)
            signal = generate_triple_ema_signal(df)
            close_price = df['Close'].iloc[-1]

            print(f"{ticker}                Signal: {signal}")
            log_signal_to_text(ticker, signal, df)

            all_signals.append({
                "ticker": ticker,
                "signal": signal,
                "price": close_price
            })

        except Exception as e:
            print(f"⚠️ Error processing {ticker}: {e}")

    # ✅ Send email after all stocks are processed
    send_email_alert(all_signals)

# Scheduler setup
schedule.every(10).minutes.do(run_bot_for_all_tickers, ticker_list=tickers)

if __name__ == "__main__":
    run_bot_for_all_tickers(tickers)
    while True:
        schedule.run_pending()
        time.sleep(1)
