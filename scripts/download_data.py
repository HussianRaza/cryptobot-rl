"""Download daily OHLCV data for BTC, ETH, SOL via yfinance (default) or CCXT."""
import argparse
import os
import sys
import pandas as pd

ASSETS = {
    "btc": "BTC-USD",
    "eth": "ETH-USD",
    "sol": "SOL-USD",
}

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def download_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    df.index = pd.to_datetime(df.index)
    df.columns = [c.lower() for c in df.columns]
    return df[["open", "high", "low", "close", "volume"]]


def download_ccxt(symbol: str, start: str, end: str) -> pd.DataFrame:
    import ccxt
    exchange = ccxt.binance({"enableRateLimit": True})
    since = exchange.parse8601(f"{start}T00:00:00Z")
    ohlcv = []
    while True:
        batch = exchange.fetch_ohlcv(symbol, "1d", since=since, limit=1000)
        if not batch:
            break
        ohlcv.extend(batch)
        since = batch[-1][0] + 86400000
        if batch[-1][0] >= exchange.parse8601(f"{end}T00:00:00Z"):
            break
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("date")[["open", "high", "low", "close", "volume"]]
    df = df[df.index < end]
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", nargs="+", default=["btc", "eth", "sol"],
                        choices=list(ASSETS.keys()))
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--source", default="yfinance", choices=["yfinance", "ccxt"])
    args = parser.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)

    for asset in args.assets:
        out_path = os.path.join(RAW_DIR, f"{asset}_ohlcv_2020_2024.csv")
        if os.path.exists(out_path):
            print(f"{asset}: already exists at {out_path}, skipping")
            continue

        print(f"Downloading {asset} ({args.start} → {args.end}) via {args.source}...")
        if args.source == "yfinance":
            df = download_yfinance(ASSETS[asset], args.start, args.end)
        else:
            symbol_map = {"btc": "BTC/USDT", "eth": "ETH/USDT", "sol": "SOL/USDT"}
            df = download_ccxt(symbol_map[asset], args.start, args.end)

        df.index.name = "date"
        df.to_csv(out_path)
        print(f"  saved {len(df)} rows → {out_path}")


if __name__ == "__main__":
    main()
