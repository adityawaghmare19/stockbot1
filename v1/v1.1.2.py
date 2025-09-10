import yfinance as yf
import pandas as pd

# List of Indian stock tickers
tickers = ["HDFCBANK.NS", "^NSEI", "^NSEBANK", "ASIANPAINT.NS", "RELIANCE.NS"]

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

def run_bot_for_all_tickers(ticker_list):
    for ticker in ticker_list:
        try:
            df = get_stock_data(ticker)
            df = apply_ema_indicators(df)
            signal = generate_triple_ema_signal(df)
            print(f"{ticker}                 Signal: {signal}")
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

if __name__ == "__main__":
    run_bot_for_all_tickers(tickers)
