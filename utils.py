# =====================================================================
# 🛠️ utils.py - الدوال المشتركة بين جميع الملفات
# =====================================================================

import requests
import math
import logging

# ============================================================
# 📡 دوال جلب البيانات من MEXC API
# ============================================================

def get_mexc_candles(symbol, interval="Min15", limit=200):
    """جلب بيانات الشموع من MEXC API"""
    url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('success') and 'data' in res_data:
                raw_candles = res_data['data']
                return {
                    "closes": [float(x) for x in raw_candles.get('close', [])],
                    "highs": [float(x) for x in raw_candles.get('high', [])],
                    "lows": [float(x) for x in raw_candles.get('low', [])],
                    "opens": [float(x) for x in raw_candles.get('open', [])],
                    "volumes": [float(x) for x in raw_candles.get('vol', [])]
                }
        return None
    except Exception as e:
        logging.error(f"MEXC API Error: {e}")
        return None


# ============================================================
# 📊 دوال المؤشرات الفنية
# ============================================================

def rma(src, length):
    """حساب RMA (المتوسط المتحرك الموزون)"""
    alpha = 1.0 / length
    rma_values = []
    if len(src) >= length:
        sum_init = sum(src[:length]) / length
        rma_values = [0.0] * (length - 1) + [sum_init]
        for i in range(length, len(src)):
            val = alpha * src[i] + (1 - alpha) * rma_values[-1]
            rma_values.append(val)
    else:
        rma_values = [src[0]] * len(src)
    return rma_values


def calculate_rsi_7(src, length=7):
    """حساب RSI (7)"""
    if len(src) < length + 1:
        return [50.0] * len(src)
    deltas = [src[i] - src[i-1] for i in range(1, len(src))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gains = rma(gains, length)
    avg_losses = rma(losses, length)
    rsi_vals = [50.0] * length
    for i in range(len(avg_gains)):
        if avg_losses[i] == 0:
            rsi_vals.append(100.0)
        else:
            rsi_vals.append(100.0 - (100.0 / (1 + avg_gains[i] / avg_losses[i])))
    return rsi_vals


def ema(data, period):
    """حساب EMA"""
    alpha = 2.0 / (period + 1)
    res = [data[0]]
    for x in data[1:]:
        res.append(alpha * x + (1 - alpha) * res[-1])
    return res


def calculate_macd_histogram(src):
    """حساب MACD Histogram"""
    if len(src) < 35:
        return [0.0] * len(src)
    f_ema = ema(src, 12)
    s_ema = ema(src, 26)
    macd_line = [f - s for f, s in zip(f_ema, s_ema)]
    sig_line = ema(macd_line, 9)
    return [m - s for m, s in zip(macd_line, sig_line)]


def stdev_pinescript(src, length):
    """حساب الانحراف المعياري (PineScript style)"""
    stdev_values = []
    for i in range(len(src)):
        if i < length - 1:
            stdev_values.append(0.0)
        else:
            window = src[i - length + 1:i + 1]
            mean = sum(window) / length
            variance = sum((x - mean) ** 2 for x in window) / length
            stdev_values.append(math.sqrt(variance))
    return stdev_values


def calculate_bollinger_bands(closes, length=20, mult=2):
    """حساب Bollinger Bands"""
    if len(closes) < length:
        return [closes[-1]] * len(closes), [closes[-1]] * len(closes), [closes[-1]] * len(closes)
    basis = [sum(closes[i-length+1:i+1])/length for i in range(length-1, len(closes))]
    basis = [closes[0]] * (length-1) + basis
    dev = stdev_pinescript(closes, length)
    upper = [b + (mult * d) for b, d in zip(basis, dev)]
    lower = [b - (mult * d) for b, d in zip(basis, dev)]
    return upper, basis, lower


def calculate_vwap(data):
    """حساب VWAP"""
    closes, highs, lows, volumes = data["closes"], data["highs"], data["lows"], data["volumes"]
    vwap_values, cum_pv, cum_vol = [], 0.0, 0.0
    for i in range(len(closes)):
        typical_price = (highs[i] + lows[i] + closes[i]) / 3.0
        cum_pv += typical_price * volumes[i]
        cum_vol += volumes[i]
        vwap_values.append(cum_pv / cum_vol if cum_vol != 0 else closes[i])
    return vwap_values


def calculate_adx_14(data):
    """حساب ADX (14)"""
    highs, lows, closes = data["highs"], data["lows"], data["closes"]
    if len(closes) < 20:
        return 15.0
    tr = [highs[0] - lows[0]]
    plus_dm, minus_dm = [0.0], [0.0]
    for i in range(1, len(closes)):
        tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        up, down = highs[i] - highs[i-1], lows[i-1] - lows[i]
        plus_dm.append(up if up > down and up > 0 else 0.0)
        minus_dm.append(down if down > up and down > 0 else 0.0)
    tr_smooth = rma(tr, 14)
    plus_di = [100 * x / y if y != 0 else 0 for x, y in zip(rma(plus_dm, 14), tr_smooth)]
    minus_di = [100 * x / y if y != 0 else 0 for x, y in zip(rma(minus_dm, 14), tr_smooth)]
    dx = [100 * abs(p - m) / (p + m) if (p + m) != 0 else 0 for p, m in zip(plus_di, minus_di)]
    return rma(dx, 14)[-1]


def calculate_atr_14(data):
    """حساب ATR (14)"""
    highs, lows, closes = data["highs"], data["lows"], data["closes"]
    if len(closes) < 15:
        return 0.1
    tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(closes))]
    return sum(tr[-14:]) / 14


def calculate_stochastic(highs, lows, closes, length=14, smooth_k=3):
    """حساب Stochastic (14,3)"""
    if len(closes) < length + smooth_k:
        return [50.0] * len(closes)
    stoch_raw = []
    for i in range(len(closes)):
        if i < length - 1:
            stoch_raw.append(50.0)
            continue
        window_high = max(highs[i-length+1:i+1])
        window_low = min(lows[i-length+1:i+1])
        denom = (window_high - window_low)
        fast_k = ((closes[i] - window_low) / denom * 100) if denom != 0 else 50.0
        stoch_raw.append(fast_k)
    smooth_values = [sum(stoch_raw[i-smooth_k+1:i+1])/smooth_k for i in range(smooth_k-1, len(stoch_raw))]
    return [50.0] * (smooth_k-1) + smooth_values


def calculate_vpt_supertrend_v5_corrected(data, vpt_len=10, st_period=100, st_mult=2.5):
    """حساب VPT Supertrend (معدل)"""
    closes, highs, lows, opens, volumes = data["closes"], data["highs"], data["lows"], data["opens"], data["volumes"]
    n = len(closes)
    if n < st_period + 50:
        return [0.0] * n, [1] * n

    spreadvol = []
    for i in range(n):
        hilow = (highs[i] - lows[i]) * 100
        openclose = (closes[i] - opens[i]) * 100
        vol = volumes[i] / (1 if hilow == 0 else hilow)
        spreadvol.append(openclose * vol)

    cum_spreadvol = []
    current_cum = 0.0
    for sv in spreadvol:
        current_cum += sv
        cum_spreadvol.append(current_cum)

    v = [sv + csv for sv, csv in zip(spreadvol, cum_spreadvol)]
    window_len, v_len = 28, 14

    smooth = []
    for i in range(n):
        start = max(0, i - v_len + 1)
        smooth.append(sum(v[start:i+1]) / len(v[start:i+1]))

    v_minus_smooth = [vi - sm for vi, sm in zip(v, smooth)]
    v_spread = stdev_pinescript(v_minus_smooth, window_len)
    price_spread = stdev_pinescript([h - l for h, l in zip(highs, lows)], window_len)

    shadow, out = [], []
    for i in range(n):
        v_sp = 1 if v_spread[i] == 0 else v_spread[i]
        sh_val = (v_minus_smooth[i] / v_sp) * price_spread[i]
        shadow.append(sh_val)
        out.append(highs[i] + sh_val if sh_val > 0 else lows[i] + sh_val)

    alpha_vpt = 2.0 / (vpt_len + 1)
    vpt = [out[0]]
    for i in range(1, n):
        vpt.append(alpha_vpt * out[i] + (1 - alpha_vpt) * vpt[-1])

    tr_values = [highs[0] - lows[0]]
    for i in range(1, n):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        tr_values.append(tr)

    atr_val_st = rma(tr_values, st_period)
    up_trend, down_trend, trend, st_line = [0.0] * n, [0.0] * n, [1] * n, [0.0] * n

    for i in range(1, n):
        up_lev = vpt[i] - (st_mult * atr_val_st[i])
        dn_lev = vpt[i] + (st_mult * atr_val_st[i])

        up_trend[i] = max(up_lev, up_trend[i-1]) if closes[i-1] > up_trend[i-1] else up_lev
        down_trend[i] = min(dn_lev, down_trend[i-1]) if closes[i-1] < down_trend[i-1] else dn_lev

        if closes[i] > down_trend[i-1]:
            trend[i] = 1
        elif closes[i] < up_trend[i-1]:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

        st_line[i] = up_trend[i] if trend[i] == 1 else down_trend[i]

    return st_line, trend
