"""Compute technical indicators per split (train/val/test) to prevent lookahead leakage.

Splits: train 2020-01-01..2022-12-31, val 2023-01-01..2023-12-31, test 2024-01-01..2024-12-31
Indicators: RSI(14), MACD(12/26/9), Bollinger Bands(20), EMA(50), volume z-score(20)
"""
import argparse
import os
import numpy as np
import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

SPLITS = [
    ("train", "2020-01-01", "2022-12-31"),
    ("val",   "2023-01-01", "2023-12-31"),
    ("test",  "2024-01-01", "2024-12-31"),
]

ASSETS = ["btc", "eth", "sol"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # RSI(14)
    df["rsi"] = RSIIndicator(close=close, window=14, fillna=True).rsi()

    # MACD (12/26/9) — diff, signal, histogram
    macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9, fillna=True)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    # Bollinger Bands(20): width = (upper - lower) / middle
    bb = BollingerBands(close=close, window=20, window_dev=2, fillna=True)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"].replace(0, np.nan)

    # EMA(50) and normalised distance
    ema50 = EMAIndicator(close=close, window=50, fillna=True).ema_indicator()
    df["ema50"] = ema50
    df["ema50_dist"] = (close - ema50) / ema50.replace(0, np.nan)

    # Volume z-score over 20-period rolling window
    vol_mean = volume.rolling(20, min_periods=1).mean()
    vol_std = volume.rolling(20, min_periods=1).std().replace(0, np.nan)
    df["vol_zscore"] = (volume - vol_mean) / vol_std

    return df


def process_asset(asset: str) -> None:
    raw_path = os.path.join(RAW_DIR, f"{asset}_ohlcv_2020_2024.csv")
    if not os.path.exists(raw_path):
        print(f"  raw file not found: {raw_path} — run download_data.py first")
        return

    df = pd.read_csv(raw_path, index_col="date", parse_dates=True)
    df.columns = [c.lower() for c in df.columns]

    chunks = []
    for split_name, start, end in SPLITS:
        chunk = df[(df.index >= start) & (df.index <= end)].copy()
        if chunk.empty:
            print(f"  warning: no data for {asset} {split_name} split")
            continue

        chunk = add_indicators(chunk)
        chunk["split"] = split_name
        chunks.append(chunk)

    result = pd.concat(chunks)
    result = result.dropna()

    out_path = os.path.join(PROCESSED_DIR, f"{asset}_features.csv")
    result.to_csv(out_path)
    print(f"  {asset}: {len(result)} rows → {out_path} (NaNs after dropna: {result.isna().sum().sum()})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", nargs="+", default=ASSETS, choices=ASSETS)
    args = parser.parse_args()

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    for asset in args.assets:
        print(f"Processing {asset}...")
        process_asset(asset)


if __name__ == "__main__":
    main()
