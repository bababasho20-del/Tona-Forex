# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 INDICATORS.PY - دوال المؤشرات الفنية
📌 يحتوي على جميع المؤشرات الفنية المستخدمة في الاستراتيجية والتحليل
═══════════════════════════════════════════════════════════════════════════════════
"""

import math
from typing import List, Dict, Any, Optional

from constants import logger


# ====================================================================================
# 📊 المؤشرات الأساسية
# ====================================================================================

def stdev_population(src, length):
    """
    حساب الانحراف المعياري للسكان (Population Standard Deviation)
    """
    if not src or length <= 0:
        return []
    
    stdev_values = []
    for i in range(len(src)):
        if i < length - 1:
            stdev_values.append(0.0)
        else:
            window = src[i - length + 1:i + 1]
            clean_window = [x for x in window if x is not None and not math.isnan(x) and not math.isinf(x)]
            if len(clean_window) < 2:
                stdev_values.append(0.0)
                continue
            
            mean = sum(clean_window) / len(clean_window)
            variance = sum((x - mean) ** 2 for x in clean_window) / len(clean_window)
            stdev_values.append(math.sqrt(variance) if variance >= 0 else 0.0)
    
    return stdev_values


def rma(src, length):
    """
    RMA (Wilder's Moving Average)
    """
    if not src or length <= 0:
        return []
    
    if len(src) >= length:
        alpha = 1.0 / length
        rma_values = [sum(src[:length]) / length]
        
        for i in range(length, len(src)):
            rma_values.append(alpha * src[i] + (1 - alpha) * rma_values[-1])
        
        return rma_values
    
    return [sum(src) / len(src)] * len(src) if src else []


def calculate_vpt_correct(closes, volumes):
    """
    حساب VPT بنفس طريقة TradingView بالضبط
    """
    if not closes or not volumes or len(closes) < 2:
        return [0.0] * len(closes) if closes else []
    
    vpt_values = [0.0]
    cum_vpt = 0.0
    
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        if closes[i] != 0:
            vpt_value = volumes[i] * change / closes[i]
            cum_vpt += vpt_value
        vpt_values.append(cum_vpt)
    
    return vpt_values


def calculate_atr_rma(highs, lows, closes, length=14):
    """حساب ATR باستخدام RMA"""
    if len(closes) < length:
        return [0.001] * len(closes)
    
    tr = [0.0]
    for i in range(1, len(closes)):
        tr.append(max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        ))
    
    atr = [0.0] * len(closes)
    atr[length-1] = sum(tr[:length]) / length
    
    alpha = 1.0 / length
    for i in range(length, len(tr)):
        atr[i] = alpha * tr[i] + (1 - alpha) * atr[i-1]
    
    return atr


# ====================================================================================
# 📈 SuperTrend + VPT (الاستراتيجية الأساسية)
# ====================================================================================

def calculate_supertrend_vpt_correct(data, st_mult=1.0, st_period=100, vpt_len=10):
    """
    SuperTrend + VPT - يستخدم للاستراتيجية فقط
    """
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    volumes = data["volumes"]
    n = len(closes)
    
    if n < st_period + 10:
        return [0.0] * n, [1] * n, [0.0] * n
    
    v = calculate_vpt_correct(closes, volumes)
    
    hl_spread = [highs[i] - lows[i] for i in range(n)]
    price_spread = stdev_population(hl_spread, 28)
    
    v_len = 14
    smooth = []
    for i in range(n):
        start = max(0, i - v_len + 1)
        window = v[start:i+1]
        smooth.append(sum(window) / len(window) if window else 0.0)
    
    v_diff = [v[i] - smooth[i] for i in range(n)]
    v_spread = stdev_population(v_diff, 28)
    
    shadow = []
    out = []
    for i in range(n):
        vsp = v_spread[i] if v_spread[i] != 0 else 1.0
        sh = ((v[i] - smooth[i]) / vsp) * price_spread[i]
        shadow.append(sh)
        out.append(highs[i] + sh if sh > 0 else lows[i] + sh)
    
    alpha = 2.0 / (vpt_len + 1)
    vpt_ema = [out[0]]
    for i in range(1, n):
        vpt_ema.append(alpha * out[i] + (1 - alpha) * vpt_ema[-1])
    
    st_src = [(highs[i] + lows[i]) / 2 for i in range(n)]
    
    atr_val = calculate_atr_rma(highs, lows, closes, st_period)
    
    up_trend = [0.0] * n
    down_trend = [0.0] * n
    trend = [1] * n
    st_line = [0.0] * n
    
    for i in range(n):
        if i == 0:
            up_lev = st_src[i] - (st_mult * atr_val[i])
            dn_lev = st_src[i] + (st_mult * atr_val[i])
            up_trend[i] = up_lev
            down_trend[i] = dn_lev
            trend[i] = 1
            st_line[i] = up_lev
        else:
            up_lev = st_src[i] - (st_mult * atr_val[i])
            dn_lev = st_src[i] + (st_mult * atr_val[i])
            
            if st_src[i-1] > up_trend[i-1]:
                up_trend[i] = max(up_lev, up_trend[i-1])
            else:
                up_trend[i] = up_lev
            
            if st_src[i-1] < down_trend[i-1]:
                down_trend[i] = min(dn_lev, down_trend[i-1])
            else:
                down_trend[i] = dn_lev
            
            if st_src[i] > down_trend[i-1]:
                trend[i] = 1
            elif st_src[i] < up_trend[i-1]:
                trend[i] = -1
            else:
                trend[i] = trend[i-1]
            
            st_line[i] = up_trend[i] if trend[i] == 1 else down_trend[i]
    
    return st_line, trend, vpt_ema


def calculate_vpt_supertrend_v11(data, vpt_len=10, st_period=100, st_mult=2.5):
    """
    الدالة القديمة - تم الاحتفاظ بها للتوافق مع الكود القديم
    """
    closes, highs, lows, opens, volumes = data["closes"], data["highs"], data["lows"], data["opens"], data["volumes"]
    n = len(closes)
    
    if n < max(st_period + 50, vpt_len + 20, 10):
        return [0.0] * n, [1] * n
    
    def clean_floats(arr):
        return [0.0 if (x is None or math.isnan(x) or math.isinf(x)) else float(x) for x in arr]
    
    closes, highs, lows, opens, volumes = clean_floats(closes), clean_floats(highs), clean_floats(lows), clean_floats(opens), clean_floats(volumes)
    
    spreadvol = []
    for i in range(n):
        hilow = (highs[i] - lows[i]) * 100 or 0.0001
        openclose = (closes[i] - opens[i]) * 100
        spreadvol.append(openclose * (volumes[i] / hilow))
    
    cum_spreadvol = []
    current_cum = 0.0
    for sv in spreadvol:
        current_cum += sv
        cum_spreadvol.append(current_cum)
    
    v = [sv + csv for sv, csv in zip(spreadvol, cum_spreadvol)]
    
    v_len = 14
    smooth = []
    for i in range(n):
        start = max(0, i - v_len + 1)
        window = v[start:i+1]
        smooth.append(sum(window) / len(window) if window else 0.0)
    
    window_len = 28
    v_diff = [v_i - s_i for v_i, s_i in zip(v, smooth)]
    v_spread = stdev_population(v_diff, window_len)
    price_spread = stdev_population([h - l for h, l in zip(highs, lows)], window_len)
    
    shadow, out = [], []
    for i in range(n):
        v_sp = v_spread[i] if v_spread[i] != 0 else 0.0001
        if math.isnan(v_sp) or math.isinf(v_sp) or v_sp == 0:
            v_sp = 0.0001
        sh_val = ((v[i] - smooth[i]) / v_sp) * price_spread[i]
        shadow.append(sh_val)
        out.append(highs[i] + sh_val if sh_val > 0 else lows[i] + sh_val)
    
    alpha_vpt = 2.0 / (vpt_len + 1)
    vpt = [out[0]]
    for i in range(1, n):
        vpt.append(alpha_vpt * out[i] + (1 - alpha_vpt) * vpt[-1])
    
    st_src = [(highs[i] + lows[i]) / 2 for i in range(n)]
    
    tr_values = [highs[0] - lows[0]]
    for i in range(1, n):
        tr_values.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
    
    atr_val_st = rma(tr_values, st_period)
    if not atr_val_st or len(atr_val_st) < n:
        atr_val_st = [0.001] * n
    
    atr_val_st = [0.0001 if (math.isnan(x) or math.isinf(x)) else x for x in atr_val_st]
    
    up_trend, down_trend, trend, st_line = [0.0] * n, [0.0] * n, [1] * n, [0.0] * n
    
    for i in range(n):
        if i == 0:
            up_lev = st_src[i] - (st_mult * atr_val_st[i])
            dn_lev = st_src[i] + (st_mult * atr_val_st[i])
            up_trend[i] = up_lev
            down_trend[i] = dn_lev
            trend[i] = 1
            st_line[i] = up_lev
        else:
            up_lev = st_src[i] - (st_mult * atr_val_st[i])
            dn_lev = st_src[i] + (st_mult * atr_val_st[i])
            
            up_trend[i] = max(up_lev, up_trend[i-1]) if st_src[i-1] > up_trend[i-1] else up_lev
            down_trend[i] = min(dn_lev, down_trend[i-1]) if st_src[i-1] < down_trend[i-1] else dn_lev
            
            if st_src[i] > down_trend[i-1]:
                trend[i] = 1
            elif st_src[i] < up_trend[i-1]:
                trend[i] = -1
            else:
                trend[i] = trend[i-1]
            
            st_line[i] = up_trend[i] if trend[i] == 1 else down_trend[i]
    
    return st_line, trend


# ====================================================================================
# 📊 المؤشرات الفنية الأخرى
# ====================================================================================

def calculate_rsi_7(src, length=7):
    """حساب RSI"""
    if not src or len(src) < 2:
        return [50.0] * len(src) if src else []
    deltas = [src[i] - src[i-1] for i in range(1, len(src))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gains = rma(gains, length)
    avg_losses = rma(losses, length)
    rsi_vals = [50.0] * (len(src) - len(avg_gains))
    for i in range(len(avg_gains)):
        if avg_losses[i] == 0:
            rsi_vals.append(100.0)
        else:
            rsi_vals.append(100.0 - (100.0 / (1 + avg_gains[i] / avg_losses[i])))
    return rsi_vals


def calculate_macd_histogram(src):
    """حساب MACD Histogram"""
    if not src or len(src) < 35:
        return [0.0] * len(src) if src else []
    def ema(data, period):
        alpha = 2.0 / (period + 1)
        res = [data[0]]
        for x in data[1:]:
            res.append(alpha * x + (1 - alpha) * res[-1])
        return res
    f_ema = ema(src, 12)
    s_ema = ema(src, 26)
    macd_line = [f - s for f, s in zip(f_ema, s_ema)]
    sig_line = ema(macd_line, 9)
    return [m - s for m, s in zip(macd_line, sig_line)]


def calculate_adx_14(data):
    """حساب ADX (14)"""
    highs, lows, closes = data["highs"], data["lows"], data["closes"]
    if not closes or len(closes) < 20:
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
    adx_result = rma(dx, 14)
    return adx_result[-1] if adx_result else 15.0


def calculate_atr_14(data):
    """حساب ATR (14)"""
    highs, lows, closes = data["highs"], data["lows"], data["closes"]
    if not closes or len(closes) < 15:
        return 0.1
    tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(closes))]
    return sum(tr[-14:]) / 14


def calculate_bollinger_bands(closes, length=20, mult=2):
    """حساب Bollinger Bands"""
    if not closes or len(closes) < 2:
        return [closes[-1]] * len(closes) if closes else [0], [0], [0]
    if len(closes) < length:
        actual_length = len(closes)
        basis = [sum(closes) / actual_length] * len(closes)
        dev = stdev_population(closes, actual_length)
    else:
        basis = []
        for i in range(len(closes)):
            if i < length - 1:
                basis.append(sum(closes[:i+1]) / (i+1))
            else:
                basis.append(sum(closes[i-length+1:i+1]) / length)
        dev = stdev_population(closes, length)
    min_len = min(len(basis), len(dev))
    basis = basis[:min_len]
    dev = dev[:min_len]
    return [b + (mult * d) for b, d in zip(basis, dev)], basis, [b - (mult * d) for b, d in zip(basis, dev)]


def calculate_stochastic(highs, lows, closes, length=14, smooth_k=3):
    """حساب Stochastic"""
    if not closes or not highs or not lows or len(closes) < length + smooth_k:
        return [50.0] * len(closes) if closes else []
    stoch_raw = []
    for i in range(len(closes)):
        if i < length - 1:
            stoch_raw.append(50.0)
            continue
        window_high = max(highs[i-length+1:i+1])
        window_low = min(lows[i-length+1:i+1])
        denom = (window_high - window_low)
        stoch_raw.append(((closes[i] - window_low) / denom * 100) if denom != 0 else 50.0)
    smooth_values = []
    for i in range(len(stoch_raw)):
        if i < smooth_k - 1:
            smooth_values.append(50.0)
        else:
            smooth_values.append(sum(stoch_raw[i-smooth_k+1:i+1]) / smooth_k)
    return smooth_values


def calculate_vwap(data):
    """حساب VWAP"""
    closes, highs, lows, volumes = data["closes"], data["highs"], data["lows"], data["volumes"]
    if not closes or not volumes:
        return closes if closes else []
    vwap_values, cum_pv, cum_vol = [], 0.0, 0.0
    for i in range(len(closes)):
        typical_price = (highs[i] + lows[i] + closes[i]) / 3.0
        cum_pv += typical_price * volumes[i]
        cum_vol += volumes[i]
        vwap_values.append(cum_pv / cum_vol if cum_vol != 0 else closes[i])
    return vwap_values


# ====================================================================================
# 💪 حساب قوة الإشارة (signal_strength)
# ====================================================================================

def calculate_signal_strength(close_price, open_price, high_price, low_price, st_line_prev, atr_val, adx_val, vol_ratio):
    """
    حساب قوة الإشارة (signal_strength) كما في استراتيجية TradingView.
    
    المعادلات:
    - breakout_score = min(1, abs(close - st_line[1]) / (atr * 3))
    - candle_score   = min(1, abs(close - open) / (high - low))  (مع التحقق من المقام)
    - vol_score      = max(0, min(1, (vol_ratio - 1) / 3))
    - adx_score      = max(0, min(1, (adx - 20) / 30))
    - signal_strength = breakout_score * 0.30 + adx_score * 0.30 + vol_score * 0.20 + candle_score * 0.20
    
    المدخلات:
        close_price   : float - سعر الإغلاق
        open_price    : float - سعر الافتتاح
        high_price    : float - أعلى سعر
        low_price     : float - أدنى سعر
        st_line_prev  : float - قيمة st_line من الشمعة السابقة [1]
        atr_val       : float - قيمة ATR
        adx_val       : float - قيمة ADX
        vol_ratio     : float - نسبة الحجم (current_volume / avg_volume)
    
    المخرج:
        float - signal_strength بين 0 و 1
    """
    try:
        if atr_val is None or atr_val <= 0:
            atr_val = 0.001
        if adx_val is None or adx_val < 0:
            adx_val = 0
        if vol_ratio is None or vol_ratio < 0:
            vol_ratio = 1.0
        
        # 1. breakout_score
        if atr_val > 0:
            breakout_score = min(1.0, abs(close_price - st_line_prev) / (atr_val * 3.0))
        else:
            breakout_score = 0.0
        
        # 2. candle_score
        candle_range = high_price - low_price
        if candle_range is not None and candle_range > 0:
            candle_score = min(1.0, abs(close_price - open_price) / candle_range)
        else:
            candle_score = 0.0
        
        # 3. vol_score
        vol_score = max(0.0, min(1.0, (vol_ratio - 1.0) / 3.0))
        
        # 4. adx_score
        adx_score = max(0.0, min(1.0, (adx_val - 20.0) / 30.0))
        
        # 5. signal_strength
        signal_strength = (
            breakout_score * 0.30 +
            adx_score * 0.30 +
            vol_score * 0.20 +
            candle_score * 0.20
        )
        
        signal_strength = max(0.0, min(1.0, signal_strength))
        
        return signal_strength
        
    except Exception as e:
        logger.error(f"❌ خطأ في حساب signal_strength: {e}")
        return 0.5
