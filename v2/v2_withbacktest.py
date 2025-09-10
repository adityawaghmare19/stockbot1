import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Tickers from Indian market
tickers = ["HDFCBANK.NS", "^NSEI", "^NSEBANK", "ASIANPAINT.NS", "RELIANCE.NS"]

# Log file name
LOG_FILE = "stock_signals_log.csv"

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Datetime", "Ticker", "Signal", "Close", "EMA9", "EMA21", "EMA55"]).to_csv(LOG_FILE, index=False)

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

def log_signal(ticker, signal, df):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    close = df['Close'].iloc[-1]
    ema9 = df['EMA9'].iloc[-1]
    ema21 = df['EMA21'].iloc[-1]
    ema55 = df['EMA55'].iloc[-1]

    log_df = pd.DataFrame([{
        "Datetime": now,
        "Ticker": ticker,
        "Signal": signal,
        "Close": close,
        "EMA9": ema9,
        "EMA21": ema21,
        "EMA55": ema55
    }])

    log_df.to_csv(LOG_FILE, mode='a', header=False, index=False)

def run_bot_for_all_tickers(ticker_list):
    for ticker in ticker_list:
        try:
            df = get_stock_data(ticker)
            df = apply_ema_indicators(df)
            signal = generate_triple_ema_signal(df)
            print(f"{ticker} Signal: {signal}")
            log_signal(ticker, signal, df)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

# ------------------------
# 🧪 Backtesting function
# ------------------------
def backtest_triple_ema(ticker, period="6mo", interval="1d"):
    df = get_stock_data(ticker, period=period, interval=interval)
    df = apply_ema_indicators(df)

    df['Signal'] = "HOLD"

    for i in range(len(df)):
        if df['EMA9'].iloc[i] > df['EMA21'].iloc[i] and df['EMA9'].iloc[i] > df['EMA55'].iloc[i]:
            df.at[df.index[i], 'Signal'] = "BUY"
        elif df['EMA9'].iloc[i] < df['EMA21'].iloc[i] and df['EMA9'].iloc[i] < df['EMA55'].iloc[i]:
            df.at[df.index[i], 'Signal'] = "SELL"

    signal_counts = df['Signal'].value_counts()
    print(f"\n📊 Backtest Results for {ticker}:")
    print(signal_counts)

    # Save to CSV
    backtest_file = f"backtest_{ticker.replace('.', '_')}.csv"
    df[['Close', 'EMA9', 'EMA21', 'EMA55', 'Signal']].to_csv(backtest_file)
    print(f"Backtest data saved to {backtest_file}")


if __name__ == "__main__":
    run_bot_for_all_tickers(tickers)

    # Run backtest for each stock
    for ticker in tickers:
        backtest_triple_ema(ticker)
