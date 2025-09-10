import yfinance as yf
import pandas as pd
from datetime import datetime

# Tickers from Indian market
tickers = ["HDFCBANK.NS", "^NSEI", "^NSEBANK", "ASIANPAINT.NS", "RELIANCE.NS"]

# Log file name (text format)
LOG_FILE = "stock_signals_log.txt"


#fetching the stock data
def get_stock_data(ticker, period="3mo", interval="1h"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    df.dropna(inplace=True)
    return df

#applying the ema indicators
def apply_ema_indicators(df):
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['EMA55'] = df['Close'].ewm(span=55, adjust=False).mean()
    return df


#basic logic for buy sell and hold
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

# for logging the stocks 
def log_signal_to_text(ticker, signal, df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    close = df['Close'].iloc[-1]
    ema9 = df['EMA9'].iloc[-1]
    ema21 = df['EMA21'].iloc[-1]
    ema55 = df['EMA55'].iloc[-1]

    log_line = f"[{now}] Ticker: {ticker} | Signal: {signal} | PRICE : {close:.2f} \n"
    log_line =f"\n"

    with open(LOG_FILE, "a") as f:
        f.write(log_line)


# for using multipe stocks 
def run_bot_for_all_tickers(ticker_list):
    for ticker in ticker_list:
        try:
            df = get_stock_data(ticker)
            df = apply_ema_indicators(df)
            signal = generate_triple_ema_signal(df)
            print(f"{ticker}                Signal: {signal}")
            log_signal_to_text(ticker, signal, df)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")



# to run the bot every 10 minutes
import schedule
import time

schedule.every(10).minutes.do(run_bot_for_all_tickers, ticker_list=tickers)

while True:
    schedule.run_pending()
    time.sleep(1)
            

if __name__ == "__main__":
    run_bot_for_all_tickers(tickers)
