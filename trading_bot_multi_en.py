#!/usr/bin/env python3
"""
Multi-Asset Trading Bot with Alpaca Paper Trading
Supports multiple symbols (stocks, crypto, ETFs) simultaneously.
"""

import time
import requests
import os
from datetime import datetime

# ===================== CONFIGURATION =====================
# Alpaca Paper Trading API keys (read from environment variables)
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

# List of assets to trade
SYMBOLS = [
    {"symbol": "BTCUSD", "coin_id": "bitcoin"},
    {"symbol": "ETHUSD", "coin_id": "ethereum"},
    {"symbol": "AAPL",   "coin_id": None},   # Stock (needs a different data source)
]

SHORT_MA_PERIOD = 1
LONG_MA_PERIOD = 5
CHECK_INTERVAL = 60
POSITION_SIZE = 0.05

# ===================== ALPACA API HELPERS =====================

def alpaca_headers():
    """Return headers for Alpaca API requests."""
    return {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

def get_account():
    """Fetch account information from Alpaca."""
    url = f"{BASE_URL}/v2/account"
    resp = requests.get(url, headers=alpaca_headers())
    resp.raise_for_status()
    return resp.json()

def submit_order(symbol, side, qty):
    """Submit a market order to Alpaca Paper Trading."""
    url = f"{BASE_URL}/v2/orders"
    data = {
        "symbol": symbol,
        "qty": str(qty),
        "side": side,
        "type": "market",
        "time_in_force": "day"
    }
    try:
        resp = requests.post(url, headers=alpaca_headers(), json=data)
        resp.raise_for_status()
        order = resp.json()
        print(f"✅ {side.upper()} {symbol} | Qty: {qty:.6f} | ID: {order.get('id', 'N/A')}")
        return order
    except Exception as e:
        print(f"❌ Order failed for {symbol}: {e}")
        return None

def get_positions():
    """Get current open positions."""
    url = f"{BASE_URL}/v2/positions"
    resp = requests.get(url, headers=alpaca_headers())
    return resp.json() if resp.status_code == 200 else []

def close_all_positions(symbol=None):
    """Close all positions or a specific position if a symbol is provided."""
    url = f"{BASE_URL}/v2/positions"
    if symbol:
        url += f"/{symbol}"
    try:
        resp = requests.delete(url, headers=alpaca_headers())
        if resp.status_code == 200:
            print(f"✅ Closed position for {symbol if symbol else 'all'}")
        else:
            print(f"⚠️ Could not close: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# ===================== PRICE HELPERS =====================

def get_crypto_price(coin_id):
    """Fetch current price of a cryptocurrency from CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()[coin_id]['usd']
    except Exception:
        return None

def get_stock_price(symbol):
    """Fetch current stock price from Alpaca."""
    url = f"{BASE_URL}/v2/stocks/{symbol}/trades/latest"
    try:
        r = requests.get(url, headers=alpaca_headers(), timeout=10)
        r.raise_for_status()
        return float(r.json()['trade']['p'])
    except Exception:
        return None

def get_historical_crypto(coin_id, days=30):
    """Fetch historical prices for a cryptocurrency from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/{}/market_chart".format(coin_id)
    params = {'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return [p[1] for p in r.json()['prices']]
    except Exception:
        return None

def get_historical_stock(symbol, days=30):
    """Fetch historical stock prices from Alpaca (bars)."""
    url = f"{BASE_URL}/v2/stocks/{symbol}/bars"
    params = {'timeframe': '1Day', 'limit': days}
    try:
        r = requests.get(url, headers=alpaca_headers(), params=params, timeout=10)
        r.raise_for_status()
        return [float(bar['c']) for bar in r.json()['bars']]
    except Exception:
        return None

def calculate_moving_average(prices, period):
    """Calculate simple moving average for a given period."""
    if not prices or len(prices) < period:
        return None
    return sum(prices[-period:]) / period

# ===================== MAIN LOOP =====================

def main():
    print("=" * 60)
    print("🚀 Multi-Asset Trading Bot (Alpaca Paper Trading)")
    print(f"📊 MA {SHORT_MA_PERIOD} / {LONG_MA_PERIOD}")
    print(f"💵 Position size: {POSITION_SIZE * 100}%")
    print("=" * 60)

    # Test connection
    if not API_KEY or not SECRET_KEY:
        print("❌ ERROR: API_KEY and SECRET_KEY must be set as environment variables.")
        return

    try:
        account = get_account()
        print(f"💰 Buying Power: ${float(account.get('buying_power', 0)):,.2f}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    last_signals = {s['symbol']: None for s in SYMBOLS}
    print("\n🟢 Bot is running... Press Ctrl+C to stop.\n")

    while True:
        try:
            for asset in SYMBOLS:
                symbol = asset['symbol']
                coin_id = asset['coin_id']

                # Fetch data based on asset type
                if coin_id:
                    prices = get_historical_crypto(coin_id, 30)
                    price = get_crypto_price(coin_id)
                else:
                    prices = get_historical_stock(symbol, 30)
                    price = get_stock_price(symbol)

                if not prices or not price:
                    continue

                short_ma = calculate_moving_average(prices, SHORT_MA_PERIOD)
                long_ma = calculate_moving_average(prices, LONG_MA_PERIOD)

                if short_ma is None or long_ma is None:
                    continue

                # Detect crossover signal
                signal = None
                prev_short = calculate_moving_average(prices[:-1], SHORT_MA_PERIOD)
                prev_long = calculate_moving_average(prices[:-1], LONG_MA_PERIOD)

                if prev_short and prev_long:
                    if prev_short <= prev_long and short_ma > long_ma:
                        signal = "buy"
                    elif prev_short >= prev_long and short_ma < long_ma:
                        signal = "sell"

                # Display current status
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {symbol}: ${price:,.2f} | MA{SHORT_MA_PERIOD}: {short_ma:.2f} | MA{LONG_MA_PERIOD}: {long_ma:.2f}")

                # Execute signal if new
                if signal and signal != last_signals[symbol]:
                    print(f"🚨 SIGNAL: {signal.upper()} {symbol} at ${price:,.2f}")

                    account = get_account()
                    buying_power = float(account.get('buying_power', 0))
                    positions = get_positions()
                    has_position = any(p['symbol'] == symbol for p in positions)

                    if signal == "buy" and not has_position:
                        # Allocate position across all symbols
                        trade_amount = buying_power * POSITION_SIZE / len(SYMBOLS)
                        qty = round(trade_amount / price, 6)
                        if qty > 0:
                            submit_order(symbol, "buy", qty)
                            last_signals[symbol] = signal
                    elif signal == "sell" and has_position:
                        close_all_positions(symbol)
                        last_signals[symbol] = signal

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
