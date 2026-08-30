# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 ANALYSIS.PY - التحليل الشامل والتقييم
📌 يحتوي على دوال التحليل الفني الشامل، التقييم، وتحليل الصفقات المفتوحة
═══════════════════════════════════════════════════════════════════════════════════
"""

import time# -*- coding: utf-8 -*-
"""
📦 ANALYSIS.PY - التحليل الشامل والتقييم
(نفس المحتوى السابق مع تعديل في معالجة الأخطاء)
"""

import time
import math
from datetime import datetime
from typing import Dict, List, Optional, Any

from constants import logger, ANALYSIS_CACHE, ANALYSIS_CACHE_TTL
from utils import fmt_price, queue_telegram_message
from api_clients import get_mexc_candles, fetch_multiple_timeframes, get_fear_greed_index
from indicators import (
    calculate_rsi_7, calculate_macd_histogram, calculate_adx_14, calculate_atr_14,
    calculate_bollinger_bands, calculate_stochastic, calculate_vwap,
    calculate_supertrend_vpt_correct, calculate_vpt_supertrend_v11
)
from position_manager import (
    get_current_open_trade, load_trades_history, save_trades_history,
    AccountingSystem, close_trade_virtual, close_trade_manually,
    WARNING_LEVELS, should_send_warning, should_send_recommendation,
    record_warning, record_recommendation,
    check_sl_tp_hit, check_supertrend_reversal,
    check_distance_warnings, check_adx_warnings, check_volume_warnings
)


# ====================================================================================
# 🗄️ التخزين المؤقت للتحليل الشامل
# ====================================================================================

def get_cached_analysis(asset_type: str) -> Optional[Dict]:
    cache_key = f"{asset_type}_{int(time.time() // ANALYSIS_CACHE_TTL)}"
    if cache_key in ANALYSIS_CACHE:
        cached = ANALYSIS_CACHE[cache_key]
        return cached.get('analysis')
    return None


def set_cached_analysis(asset_type: str, analysis: Dict):
    cache_key = f"{asset_type}_{int(time.time() // ANALYSIS_CACHE_TTL)}"
    ANALYSIS_CACHE[cache_key] = {
        'analysis': analysis,
        'timestamp': time.time()
    }
    if len(ANALYSIS_CACHE) > 20:
        keys = sorted(ANALYSIS_CACHE.keys(), key=lambda k: ANALYSIS_CACHE[k].get('timestamp', 0))
        for k in keys[:-20]:
            del ANALYSIS_CACHE[k]


# ====================================================================================
# 📊 دوال وصفية مساعدة للتقييم
# ====================================================================================

def _default_result(reason):
    return {
        "score": 0,
        "grade": "بيانات غير كافية",
        "grade_emoji": "⚠️",
        "details": [f"⚠️ {reason}"],
        "context": "unknown",
        "metrics": {},
        "components": {},
        "trade_health": None,
    }


def _trend_desc(bullish_count, adx):
    if bullish_count == 3:
        return "اتجاه صاعد قوي ومؤكد" if adx > 25 else "اتجاه صاعد لكن الزخم ضعيف"
    elif bullish_count == 2:
        return "غالبية الفريمات صاعدة"
    elif bullish_count == 1:
        return "غالبية الفريمات هابطة"
    else:
        return "اتجاه هابط قوي ومؤكد" if adx > 25 else "اتجاه هابط لكن الزخم ضعيف"


def _momentum_desc(rsi, macd_hist, stoch):
    if rsi < 30 and macd_hist > 0:
        return "زخم صاعد قوي — ارتداد محتمل"
    elif rsi > 70 and macd_hist < 0:
        return "زخم هابط قوي — تصحيح محتمل"
    elif 40 <= rsi <= 60 and abs(macd_hist) < 0.3:
        return "زخم محايد — لا قوة اتجاهية واضحة"
    elif rsi < 40:
        return "زخم ضعيف نحو الأسفل"
    else:
        return "زخم ضعيف نحو الأعلى"


def _volatility_desc(bb_pos, atr_pct, vwap_dev):
    if atr_pct > 2.5:
        return "تقلب شديد — السوق متقلب جداً"
    elif atr_pct < 0.5:
        return "تقلب منخفض — السوق نائم"
    if bb_pos < 0.15:
        return "السعر عند القاع النسبي — ارتداد محتمل"
    elif bb_pos > 0.85:
        return "السعر عند القمة النسبية — تصحيح محتمل"
    if abs(vwap_dev) > 0.015:
        return "انحراف كبير عن السعر العادل"
    return "بنية سعرية متوازنة"


def _volume_desc(vol_ratio):
    if vol_ratio >= 2.0:
        return "سيولة استثنائية — حركة مدعومة بقوة"
    elif vol_ratio >= 1.5:
        return "سيولة مرتفعة — حركة حقيقية"
    elif vol_ratio >= 1.0:
        return "سيولة طبيعية"
    elif vol_ratio >= 0.6:
        return "سيولة منخفضة — حذر من الانزلاق"
    else:
        return "سيولة جافة جداً — تجنب الدخول"


def _sr_desc(price, s1, r1, pivot):
    if price <= 0:
        return "سعر غير صالح"
    if s1 <= 0 or r1 <= 0 or pivot <= 0:
        return "مستويات غير متوفرة"
    if price <= s1 * 1.003:
        return "السعر عند منطقة دعم قوية"
    elif price >= r1 * 0.997:
        return "السعر عند منطقة مقاومة قوية"
    elif abs(price - pivot) / price < 0.003:
        return "السعر عند نقطة الارتكاز"
    elif price < pivot:
        return "السعر في النطاق السفلي"
    else:
        return "السعر في النطاق العلوي"


def _sentiment_desc(fear_greed):
    if fear_greed <= 20:
        return "هلع شديد في السوق — فرصة تاريخية محتملة"
    elif fear_greed <= 35:
        return "خوف متزايد — بيئة شرائية محتملة"
    elif fear_greed <= 55:
        return "معنويات متوازنة"
    elif fear_greed <= 75:
        return "تفاؤل مرتفع — حذر من القمة"
    else:
        return "طمع مفرط — قمة بيعية محتملة"


def _detect_divergence(price_hist, rsi_hist, macd_hist):
    if not price_hist or not rsi_hist or len(price_hist) < 15 or len(rsi_hist) < 15:
        return {"type": "none", "score": 50, "desc": "لا يوجد تباعد — بيانات غير كافية"}

    price_hist_clean = [p for p in price_hist if p is not None and p > 0]
    rsi_hist_clean = [r for r in rsi_hist if r is not None and 0 <= r <= 100]
    macd_hist_clean = [m for m in macd_hist if m is not None]

    if len(price_hist_clean) < 15 or len(rsi_hist_clean) < 15:
        return {"type": "none", "score": 50, "desc": "لا يوجد تباعد — بيانات غير كافية"}

    def find_peaks(data, min_dist=3):
        peaks = []
        for i in range(min_dist, len(data) - min_dist):
            is_peak = all(data[i] >= data[i-j] for j in range(1, min_dist+1))
            is_peak = is_peak and all(data[i] >= data[i+j] for j in range(1, min_dist+1))
            if is_peak:
                if not peaks or i - peaks[-1] >= min_dist:
                    peaks.append(i)
        return peaks[-5:]

    def find_troughs(data, min_dist=3):
        troughs = []
        for i in range(min_dist, len(data) - min_dist):
            is_trough = all(data[i] <= data[i-j] for j in range(1, min_dist+1))
            is_trough = is_trough and all(data[i] <= data[i+j] for j in range(1, min_dist+1))
            if is_trough:
                if not troughs or i - troughs[-1] >= min_dist:
                    troughs.append(i)
        return troughs[-5:]

    price_peaks = find_peaks(price_hist_clean)
    rsi_peaks = find_peaks(rsi_hist_clean)

    if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
        for pp_idx in range(len(price_peaks)-1, 0, -1):
            for rp_idx in range(len(rsi_peaks)-1, 0, -1):
                p1, p2 = price_peaks[pp_idx-1], price_peaks[pp_idx]
                r1, r2 = rsi_peaks[rp_idx-1], rsi_peaks[rp_idx]
                if abs(p1 - r1) <= 3 and abs(p2 - r2) <= 3:
                    if price_hist_clean[p2] > price_hist_clean[p1] * 1.003 and rsi_hist_clean[r2] < rsi_hist_clean[r1] * 0.98:
                        return {"type": "bearish_rsi", "score": 20, "desc": "تباعد هابط في RSI — السعر يصعد لكن الزخم يتراجع"}

    price_troughs = find_troughs(price_hist_clean)
    rsi_troughs = find_troughs(rsi_hist_clean)

    if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
        for pt_idx in range(len(price_troughs)-1, 0, -1):
            for rt_idx in range(len(rsi_troughs)-1, 0, -1):
                p1, p2 = price_troughs[pt_idx-1], price_troughs[pt_idx]
                r1, r2 = rsi_troughs[rt_idx-1], rsi_troughs[rt_idx]
                if abs(p1 - r1) <= 3 and abs(p2 - r2) <= 3:
                    if price_hist_clean[p2] < price_hist_clean[p1] * 0.997 and rsi_hist_clean[r2] > rsi_hist_clean[r1] * 1.02:
                        return {"type": "bullish_rsi", "score": 80, "desc": "تباعد صاعد في RSI — السعر يهبط لكن الزخم يتعزز"}

    if len(macd_hist_clean) >= 15:
        macd_peaks = find_peaks(macd_hist_clean)
        if len(macd_peaks) >= 2 and len(price_peaks) >= 2:
            for pp_idx in range(len(price_peaks)-1, 0, -1):
                for mp_idx in range(len(macd_peaks)-1, 0, -1):
                    p1, p2 = price_peaks[pp_idx-1], price_peaks[pp_idx]
                    m1, m2 = macd_peaks[mp_idx-1], macd_peaks[mp_idx]
                    if abs(p1 - m1) <= 3 and abs(p2 - m2) <= 3:
                        if price_hist_clean[p2] > price_hist_clean[p1] * 1.003 and macd_hist_clean[m2] < macd_hist_clean[m1] * 0.97:
                            return {"type": "bearish_macd", "score": 25, "desc": "تباعد هابط في MACD — السعر يصعد لكن الزخم يتراجع"}

    return {"type": "none", "score": 50, "desc": "لا يوجد تباعد ملحوظ"}


# ====================================================================================
# 🧠 محرك التقييم الشامل V8 FIXED
# ====================================================================================

def calculate_comprehensive_score(analysis, asset_type, open_trade=None):
    if not analysis or not isinstance(analysis, dict):
        return _default_result("بيانات التحليل غير صالحة (ليست قاموساً)")
    
    price = analysis.get('price', 0)
    if not price or price <= 0:
        return _default_result(f"سعر غير صالح (القيمة: {price})")
    
    indicators = analysis.get('indicators', {})
    if not indicators or not isinstance(indicators, dict):
        return _default_result("بيانات المؤشرات مفقودة أو غير صالحة")
    
    try:
        trend_data = indicators.get('trend', {})
        if not isinstance(trend_data, dict):
            trend_data = {}
        bullish_count = trend_data.get('bullish_count', 0)
        if not isinstance(bullish_count, int) or bullish_count < 0 or bullish_count > 4:
            bullish_count = 0
        adx = trend_data.get('adx', 0)
        if not isinstance(adx, (int, float)) or adx < 0 or adx > 100:
            adx = 0
        
        momentum_data = indicators.get('momentum', {})
        if not isinstance(momentum_data, dict):
            momentum_data = {}
        rsi = momentum_data.get('rsi', 50)
        if not isinstance(rsi, (int, float)) or rsi < 0 or rsi > 100:
            rsi = 50
        macd_hist = momentum_data.get('macd_hist', 0)
        if not isinstance(macd_hist, (int, float)):
            macd_hist = 0
        stoch = momentum_data.get('stoch', 50)
        if not isinstance(stoch, (int, float)) or stoch < 0 or stoch > 100:
            stoch = 50
        
        volatility_data = indicators.get('volatility', {})
        if not isinstance(volatility_data, dict):
            volatility_data = {}
        bb_pos = volatility_data.get('bb_position', 0.5)
        if not isinstance(bb_pos, (int, float)) or bb_pos < 0 or bb_pos > 1:
            bb_pos = 0.5
        atr_pct = volatility_data.get('atr_percent', 1.0)
        if not isinstance(atr_pct, (int, float)) or atr_pct < 0:
            atr_pct = 1.0
        vwap_dev = volatility_data.get('vwap_deviation', 0)
        if not isinstance(vwap_dev, (int, float)):
            vwap_dev = 0
        
        volume_data = indicators.get('volume', {})
        if not isinstance(volume_data, dict):
            volume_data = {}
        vol_ratio = volume_data.get('ratio', 1.0)
        if not isinstance(vol_ratio, (int, float)) or vol_ratio < 0:
            vol_ratio = 1.0
        
        sr_levels = indicators.get('support_resistance', {})
        if not isinstance(sr_levels, dict):
            sr_levels = {}
        s1 = sr_levels.get('s1', price * 0.98)
        if not isinstance(s1, (int, float)) or s1 <= 0:
            s1 = price * 0.98
        r1 = sr_levels.get('r1', price * 1.02)
        if not isinstance(r1, (int, float)) or r1 <= 0:
            r1 = price * 1.02
        pivot = sr_levels.get('pivot', price)
        if not isinstance(pivot, (int, float)) or pivot <= 0:
            pivot = price
        
        sentiment_data = indicators.get('sentiment', {})
        if not isinstance(sentiment_data, dict):
            sentiment_data = {}
        fear_greed = sentiment_data.get('fear_greed', 50)
        if not isinstance(fear_greed, (int, float)) or fear_greed < 0 or fear_greed > 100:
            fear_greed = 50
        
        price_hist = analysis.get('price_history', [])
        if not isinstance(price_hist, list):
            price_hist = []
        rsi_hist = analysis.get('rsi_history', [])
        if not isinstance(rsi_hist, list):
            rsi_hist = []
        macd_hist_data = analysis.get('macd_history', [])
        if not isinstance(macd_hist_data, list):
            macd_hist_data = []
        
        # ── حساب التقييمات الفرعية ──
        if bullish_count >= 2:
            trend_score = 65 if adx > 25 else 55
            trend_desc = _trend_desc(bullish_count, adx)
        else:
            trend_score = 35 if adx > 25 else 45
            trend_desc = _trend_desc(bullish_count, adx)
        
        if rsi < 30:
            momentum_score = 70
        elif rsi > 70:
            momentum_score = 30
        elif 40 <= rsi <= 60 and abs(macd_hist) < 0.3:
            momentum_score = 50
        elif rsi < 40:
            momentum_score = 40
        else:
            momentum_score = 60
        momentum_desc = _momentum_desc(rsi, macd_hist, stoch)
        
        volatility_score = 50
        if atr_pct > 2.5:
            volatility_score = 60
        elif atr_pct < 0.5:
            volatility_score = 40
        if bb_pos < 0.15:
            volatility_score = min(volatility_score + 10, 65)
        elif bb_pos > 0.85:
            volatility_score = max(volatility_score - 10, 35)
        volatility_desc = _volatility_desc(bb_pos, atr_pct, vwap_dev)
        
        if vol_ratio >= 1.5:
            volume_score = 65
        elif vol_ratio >= 1.0:
            volume_score = 55
        elif vol_ratio >= 0.6:
            volume_score = 45
        else:
            volume_score = 35
        volume_desc = _volume_desc(vol_ratio)
        
        if price <= s1 * 1.003:
            sr_score = 65
        elif price >= r1 * 0.997:
            sr_score = 35
        elif abs(price - pivot) / price < 0.003:
            sr_score = 50
        else:
            sr_score = 50
        sr_desc = _sr_desc(price, s1, r1, pivot)
        
        if fear_greed <= 20:
            sentiment_score = 75
        elif fear_greed <= 35:
            sentiment_score = 65
        elif fear_greed <= 55:
            sentiment_score = 50
        elif fear_greed <= 75:
            sentiment_score = 35
        else:
            sentiment_score = 25
        sentiment_desc = _sentiment_desc(fear_greed)
        
        divergence = _detect_divergence(price_hist, rsi_hist, macd_hist_data)
        divergence_score = divergence.get('score', 50)
        divergence_desc = divergence.get('desc', 'لا يوجد تباعد')
        
        # ── حساب النتيجة النهائية (مرجحة) ──
        weights = {
            'trend': 0.25,
            'momentum': 0.20,
            'volatility': 0.15,
            'volume': 0.15,
            'sr': 0.15,
            'sentiment': 0.05,
            'divergence': 0.05
        }
        total_weight = sum(weights.values())
        if total_weight != 1.0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        final_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            volatility_score * weights['volatility'] +
            volume_score * weights['volume'] +
            sr_score * weights['sr'] +
            sentiment_score * weights['sentiment'] +
            divergence_score * weights['divergence']
        )
        
        final_score = round(final_score, 2)
        
        if final_score >= 70:
            grade = "إيجابي قوي"
            grade_emoji = "🟢"
            context = "bullish"
        elif final_score >= 60:
            grade = "إيجابي"
            grade_emoji = "🟡"
            context = "bullish"
        elif final_score >= 45:
            grade = "محايد"
            grade_emoji = "⚪"
            context = "neutral"
        elif final_score >= 35:
            grade = "سلبي"
            grade_emoji = "🟠"
            context = "bearish"
        else:
            grade = "سلبي قوي"
            grade_emoji = "🔴"
            context = "bearish"
        
        details = [
            f"📈 الاتجاه: {trend_desc} (درجة: {trend_score:.0f})",
            f"⚡ الزخم: {momentum_desc} (درجة: {momentum_score:.0f})",
            f"🌊 التقلب: {volatility_desc} (درجة: {volatility_score:.0f})",
            f"📊 الحجم: {volume_desc} (درجة: {volume_score:.0f})",
            f"🛡️ الدعم/المقاومة: {sr_desc} (درجة: {sr_score:.0f})",
            f"🧠 المشاعر: {sentiment_desc} (درجة: {sentiment_score:.0f})",
            f"📉 التباعد: {divergence_desc} (درجة: {divergence_score:.0f})"
        ]
        
        if open_trade:
            trade_type = open_trade.get('type', 'unknown')
            entry_price = open_trade.get('entry_price', 0)
            if entry_price > 0:
                pnl = ((price - entry_price) / entry_price * 100) if trade_type == 'long' else ((entry_price - price) / entry_price * 100)
                details.append(f"💼 الصفقة المفتوحة: {trade_type.upper()} | الربح/الخسارة: {pnl:.2f}%")
        
        result = {
            "score": final_score,
            "grade": grade,
            "grade_emoji": grade_emoji,
            "details": details,
            "context": context,
            "metrics": {
                "price": price,
                "rsi": rsi,
                "adx": adx,
                "vol_ratio": vol_ratio,
                "fear_greed": fear_greed,
                "bullish_count": bullish_count,
                "support": s1,
                "resistance": r1,
                "atr_percent": atr_pct,
                "bb_position": bb_pos
            },
            "components": {
                "trend": {"score": round(trend_score, 2), "weight": weights['trend']},
                "momentum": {"score": round(momentum_score, 2), "weight": weights['momentum']},
                "volatility": {"score": round(volatility_score, 2), "weight": weights['volatility']},
                "volume": {"score": round(volume_score, 2), "weight": weights['volume']},
                "sr": {"score": round(sr_score, 2), "weight": weights['sr']},
                "sentiment": {"score": round(sentiment_score, 2), "weight": weights['sentiment']},
                "divergence": {"score": round(divergence_score, 2), "weight": weights['divergence']}
            },
            "trade_health": {
                "status": "متوازن" if 45 <= final_score <= 60 else "قوي" if final_score > 60 else "ضعيف",
                "recommendation": "مراقبة" if 45 <= final_score <= 60 else "انتظار" if final_score < 45 else "تأكيد"
            } if open_trade else None
        }
        
        return result
        
    except Exception as e:
        return _default_result(f"خطأ في التقييم: {str(e)[:100]}")


# ====================================================================================
# 📊 التحليل الشامل (مع التخزين المؤقت)
# ====================================================================================

def perform_comprehensive_analysis(asset_type, is_monitoring=False, open_trade=None):
    try:
        if not is_monitoring:
            cached = get_cached_analysis(asset_type)
            if cached:
                logger.info(f"📊 استخدام التحليل المخبأ لـ {asset_type}")
                try:
                    from advisor_core import format_concise_analysis
                    report = format_concise_analysis(cached, asset_type, is_monitoring, open_trade)
                except Exception:
                    report = "⚠️ تحليل غير متوفر"
                return cached, report
        
        symbol = "EUR/USD" if asset_type == "eurusd" else "USD/JPY"
        data = get_mexc_candles(symbol, interval="Min15", limit=80)
        
        if not data or not data.get("closes") or len(data["closes"]) < 10:
            return None, "⚠️ لا توجد بيانات كافية للتحليل"
        
        closes = data["closes"]
        highs = data["highs"]
        lows = data["lows"]
        volumes = data["volumes"]
        
        current_price = closes[-1]
        current_rsi = calculate_rsi_7(closes)[-1] if len(closes) >= 7 else 50
        current_macd = calculate_macd_histogram(closes)[-1] if len(closes) >= 35 else 0
        adx = calculate_adx_14(data)
        atr = calculate_atr_14(data)
        
        upper, basis, lower = calculate_bollinger_bands(closes)
        bb_upper = upper[-1] if upper else current_price * 1.02
        bb_basis = basis[-1] if basis else current_price
        bb_lower = lower[-1] if lower else current_price * 0.98
        
        stoch = calculate_stochastic(highs, lows, closes)
        stoch_value = stoch[-1] if stoch else 50
        
        vwap_values = calculate_vwap(data)
        vwap = vwap_values[-1] if vwap_values else current_price
        
        vol_ratio = 1.0
        if volumes and len(volumes) > 20:
            current_vol = volumes[-1]
            avg_vol = sum(volumes[-20:-1]) / 19 if len(volumes) > 20 else current_vol
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
        
        st_line_arr, trend, _ = calculate_supertrend_vpt_correct(
            data,
            st_mult=2.2 if asset_type == "eurusd" else 2.5,
            st_period=100,
            vpt_len=10
        )
        
        timeframes_data = {
            "5m": {"interval": "Min5", "limit": 50},
            "1h": {"interval": "Min60", "limit": 100},
            "4h": {"interval": "Hour4", "limit": 50}
        }
        results = fetch_multiple_timeframes(symbol, timeframes_data)
        
        timeframes = {}
        for tf_name, tf_data in [("5m", results.get("5m")), ("1h", results.get("1h")), ("4h", results.get("4h"))]:
            if tf_data and tf_data.get("closes") and len(tf_data["closes"]) >= 10:
                tcloses = tf_data["closes"]
                st_l, tr, _ = calculate_supertrend_vpt_correct(tf_data, st_mult=2.2 if asset_type == "eurusd" else 2.5)
                timeframes[tf_name] = {
                    "price": tcloses[-1],
                    "trend": "صاعد" if tr[-1] == 1 else "هابط" if tr[-1] == -1 else "محايد",
                    "supertrend": {"line": st_l[-1] if st_l else tcloses[-1], "trend": tr[-1] if tr else 1}
                }
        
        analysis = {
            "price": current_price,
            "asset": asset_type,
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                "trend": {
                    "bullish_count": sum(1 for tf in timeframes.values() if tf.get("trend") == "صاعد"),
                    "adx": adx,
                    "current_trend": "صاعد" if trend[-1] == 1 else "هابط" if trend[-1] == -1 else "محايد"
                },
                "momentum": {
                    "rsi": current_rsi,
                    "macd_hist": current_macd,
                    "stoch": stoch_value
                },
                "volatility": {
                    "atr_percent": (atr / current_price) * 100 if current_price > 0 else 1.0,
                    "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5,
                    "vwap_deviation": (current_price - vwap) / vwap if vwap > 0 else 0
                },
                "volume": {
                    "ratio": vol_ratio
                },
                "support_resistance": {
                    "s1": current_price * 0.98,
                    "r1": current_price * 1.02,
                    "pivot": current_price
                },
                "sentiment": {
                    "fear_greed": 50
                },
                "bollinger": {
                    "upper": bb_upper,
                    "basis": bb_basis,
                    "lower": bb_lower
                },
                "vwap": vwap
            },
            "timeframes": {
                "15m": {
                    "price": current_price,
                    "rsi": current_rsi,
                    "macd": current_macd,
                    "adx": adx,
                    "atr": atr,
                    "volume_ratio": vol_ratio,
                    "trend": "صاعد" if trend[-1] == 1 else "هابط" if trend[-1] == -1 else "محايد",
                    "supertrend": {"line": st_line_arr[-1] if st_line_arr else current_price, "trend": trend[-1] if trend else 1},
                    "bollinger": {"upper": bb_upper, "basis": bb_basis, "lower": bb_lower},
                    "stochastic": stoch_value,
                    "vwap": vwap,
                    "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
                }
            },
            "supertrend": {
                "line": st_line_arr[-1] if st_line_arr else current_price,
                "trend": trend[-1] if trend else 1
            },
            "vpt": {
                "value": 0
            },
            "fear_greed": 50,
            "support_resistance": {
                "support": current_price * 0.98,
                "resistance": current_price * 1.02,
                "pivot": current_price
            },
            "price_history": closes[-50:] if len(closes) >= 50 else closes,
            "rsi_history": calculate_rsi_7(closes)[-50:] if len(closes) >= 50 else calculate_rsi_7(closes),
            "macd_history": calculate_macd_histogram(closes)[-50:] if len(closes) >= 50 else calculate_macd_histogram(closes)
        }
        
        for tf_name, tf_data in timeframes.items():
            if tf_name in analysis["timeframes"]:
                analysis["timeframes"][tf_name].update(tf_data)
            else:
                analysis["timeframes"][tf_name] = tf_data
        
        analysis["comprehensive_score"] = calculate_comprehensive_score(analysis, asset_type, open_trade)
        
        set_cached_analysis(asset_type, analysis)
        
        # محاولة توليد التقرير الموجز، مع التقاط أي استثناء
        try:
            from advisor_core import format_concise_analysis
            report = format_concise_analysis(analysis, asset_type, is_monitoring, open_trade)
        except Exception as e:
            logger.warning(f"⚠️ فشل format_concise_analysis: {e}، استخدام البديل")
            score = analysis["comprehensive_score"].get("score", 50)
            grade = analysis["comprehensive_score"].get("grade", "محايد")
            report = f"📊 تحليل {asset_type}\n💰 السعر: ${current_price:.2f}\n📊 التقييم: {score:.0f}% ({grade})"
        
        return analysis, report
        
    except Exception as e:
        logger.error(f"خطأ في التحليل الشامل لـ {asset_type}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, f"⚠️ حدث خطأ أثناء التحليل: {str(e)}"


# ====================================================================================
# 🔍 تحليل الصفقة المفتوحة
# ====================================================================================

def analyze_open_trade(asset_type, open_trade):
    if not open_trade:
        return "⚠️ لا توجد صفقة مفتوحة"
    
    analysis, report = perform_comprehensive_analysis(asset_type, True, open_trade)
    if not analysis or not isinstance(analysis, dict):
        return "⚠️ لا توجد بيانات كافية للتحليل"
    
    price = analysis.get("price", 0)
    if not isinstance(price, (int, float)) or price <= 0:
        price = open_trade.get("entry_price", 0)
    
    timeframes = analysis.get("timeframes", {}) if isinstance(analysis.get("timeframes"), dict) else {}
    comp_score = analysis.get("comprehensive_score", {}) if isinstance(analysis.get("comprehensive_score"), dict) else {}
    indicators = analysis.get("indicators", {}) if isinstance(analysis.get("indicators"), dict) else {}
    
    entry_price = open_trade.get('entry_price', 0)
    trade_type = open_trade.get('type', 'BUY')
    sl = open_trade.get('sl', 0)
    tp = open_trade.get('tp', 0)
    
    if trade_type == "BUY":
        profit_pct = ((price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        profit_dollars = AccountingSystem.calculate_profit_dollars(entry_price, price, "BUY")
    else:
        profit_pct = ((entry_price - price) / entry_price) * 100 if entry_price > 0 else 0
        profit_dollars = AccountingSystem.calculate_profit_dollars(entry_price, price, "SELL")
    
    trends = []
    for tf in ["5m", "15m", "1h", "4h"]:
        if tf in timeframes and isinstance(timeframes.get(tf), dict):
            t = timeframes[tf].get("trend", "محايد")
            if t and t != "محايد":
                trends.append((tf, t))
    
    bullish_count = sum(1 for _, t in trends if t == "صاعد")
    bearish_count = sum(1 for _, t in trends if t == "هابط")
    total_trends = len(trends)
    
    tf_15m = timeframes.get("15m", {}) if isinstance(timeframes, dict) else {}
    
    rsi = tf_15m.get("rsi", 50) if isinstance(tf_15m, dict) else 50
    if not isinstance(rsi, (int, float)) or rsi < 0 or rsi > 100:
        rsi = 50
    
    adx = tf_15m.get("adx", 15) if isinstance(tf_15m, dict) else 15
    if not isinstance(adx, (int, float)) or adx < 0 or adx > 100:
        adx = 15
    
    macd = tf_15m.get("macd", 0) if isinstance(tf_15m, dict) else 0
    if not isinstance(macd, (int, float)):
        macd = 0
    
    vol_ratio = tf_15m.get("volume_ratio", 1.0) if isinstance(tf_15m, dict) else 1.0
    if not isinstance(vol_ratio, (int, float)) or vol_ratio < 0:
        vol_ratio = 1.0
    
    vwap = tf_15m.get("vwap", price) if isinstance(tf_15m, dict) else price
    if not isinstance(vwap, (int, float)) or vwap <= 0:
        vwap = price
    
    trend_15m = tf_15m.get("trend", "محايد") if isinstance(tf_15m, dict) else "محايد"
    
    analysis_lines = []
    
    if profit_pct > 0:
        analysis_lines.append(f"✅ **أنت رابح:** {profit_pct:+.2f}% (+${profit_dollars:+.2f})")
    elif profit_pct < 0:
        analysis_lines.append(f"❌ **أنت خاسر:** {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    else:
        analysis_lines.append(f"⚪ **أنت عند التعادل:** {profit_pct:+.2f}%")
    
    if total_trends > 0:
        if trade_type == "SELL" and bullish_count >= 3:
            analysis_lines.append(f"🔴 **تحذير:** {bullish_count}/{total_trends} فريمات صاعدة **ضد صفقتك**!")
            analysis_lines.append("   السوق يصعد بينما أنت تبيع — هذا خطر كبير")
        elif trade_type == "BUY" and bearish_count >= 3:
            analysis_lines.append(f"🔴 **تحذير:** {bearish_count}/{total_trends} فريمات هابطة **ضد صفقتك**!")
            analysis_lines.append("   السوق يهبط بينما أنت تشتري — هذا خطر كبير")
        elif trade_type == "SELL" and bearish_count >= 3:
            analysis_lines.append(f"✅ **جيد:** {bearish_count}/{total_trends} فريمات هابطة **تدعم صفقتك**")
        elif trade_type == "BUY" and bullish_count >= 3:
            analysis_lines.append(f"✅ **جيد:** {bullish_count}/{total_trends} فريمات صاعدة **تدعم صفقتك**")
        else:
            analysis_lines.append(f"🟡 **محايد:** الفريمات متضاربة ({bullish_count} صاعد / {bearish_count} هابط)")
    else:
        analysis_lines.append("🟡 **لا توجد بيانات كافية للفريمات**")
    
    if vol_ratio < 0.6:
        analysis_lines.append(f"🔴 **حجم منخفض:** {vol_ratio:.1f}x المتوسط — الحركة ضعيفة")
        analysis_lines.append("   قد يكون السوق في منطقة تجميع أو تصريف")
    elif vol_ratio > 1.5:
        analysis_lines.append(f"✅ **حجم مرتفع:** {vol_ratio:.1f}x المتوسط — الحركة مدعومة")
    else:
        analysis_lines.append(f"🟡 **حجم طبيعي:** {vol_ratio:.1f}x المتوسط")
    
    if adx < 20:
        analysis_lines.append(f"🔴 **ضعف الاتجاه:** ADX {adx:.0f} — السوق عرضي")
        analysis_lines.append("   لا يوجد اتجاه واضح، أي صفقة الآن مخاطرة")
    elif adx > 25:
        analysis_lines.append(f"✅ **اتجاه قوي:** ADX {adx:.0f} — الاتجاه واضح")
    else:
        analysis_lines.append(f"🟡 **اتجاه متوسط:** ADX {adx:.0f}")
    
    if trade_type == "SELL" and rsi > 70:
        analysis_lines.append(f"✅ **RSI يدعمك:** {rsi:.0f} — منطقة ذروة شراء (فرصة بيع)")
    elif trade_type == "BUY" and rsi < 30:
        analysis_lines.append(f"✅ **RSI يدعمك:** {rsi:.0f} — منطقة ذروة بيع (فرصة شراء)")
    elif trade_type == "SELL" and rsi < 30:
        analysis_lines.append(f"🔴 **RSI ضدك:** {rsi:.0f} — منطقة ذروة بيع (السوق قد يرتد)")
    elif trade_type == "BUY" and rsi > 70:
        analysis_lines.append(f"🔴 **RSI ضدك:** {rsi:.0f} — منطقة ذروة شراء (السوق قد يصحح)")
    else:
        analysis_lines.append(f"🟡 **RSI محايد:** {rsi:.0f}")
    
    if trade_type == "SELL" and macd < 0:
        analysis_lines.append(f"✅ **MACD يدعمك:** سلبي ({macd:.4f})")
    elif trade_type == "BUY" and macd > 0:
        analysis_lines.append(f"✅ **MACD يدعمك:** إيجابي ({macd:.4f})")
    elif trade_type == "SELL" and macd > 0:
        analysis_lines.append(f"🔴 **MACD ضدك:** إيجابي ({macd:.4f})")
    elif trade_type == "BUY" and macd < 0:
        analysis_lines.append(f"🔴 **MACD ضدك:** سلبي ({macd:.4f})")
    else:
        analysis_lines.append(f"🟡 **MACD محايد:** {macd:.4f}")
    
    if trade_type == "SELL":
        dist_to_sl = ((sl - price) / entry_price) * 100 if sl > 0 and entry_price > 0 else 0
        dist_to_tp = ((price - tp) / entry_price) * 100 if tp > 0 and entry_price > 0 else 0
    else:
        dist_to_sl = ((price - sl) / entry_price) * 100 if sl > 0 and entry_price > 0 else 0
        dist_to_tp = ((tp - price) / entry_price) * 100 if tp > 0 and entry_price > 0 else 0
    
    if dist_to_sl < 0.5:
        analysis_lines.append(f"🚨 **خطر:** وقف الخسارة قريب جداً ({dist_to_sl:.2f}%)")
        analysis_lines.append("   أنصح بتضييق الوقف أو الخروج")
    elif dist_to_sl < 1.0:
        analysis_lines.append(f"⚠️ **تنبيه:** وقف الخسارة قريب ({dist_to_sl:.2f}%)")
    
    if dist_to_tp < 0.5:
        analysis_lines.append(f"🎯 **قرب الهدف:** المسافة للهدف {dist_to_tp:.2f}%")
        analysis_lines.append("   فكر في جني الأرباح")
    
    score = comp_score.get("score", 50) if isinstance(comp_score, dict) else 50
    if not isinstance(score, (int, float)):
        score = 50
    
    if score >= 70:
        analysis_lines.append(f"✅ **التقييم الشامل:** {score:.0f}% — قوي")
    elif score >= 55:
        analysis_lines.append(f"🟡 **التقييم الشامل:** {score:.0f}% — متوسط")
    else:
        analysis_lines.append(f"🔴 **التقييم الشامل:** {score:.0f}% — ضعيف")
    
    recommendations = []
    
    if profit_pct > 3:
        recommendations.append("✅ ربح جيد — فكر في جني 50% من الأرباح")
    elif profit_pct > 0.5:
        recommendations.append("🟡 ربح بسيط — حرك الوقف إلى نقطة الدخول")
    elif profit_pct > -0.5:
        recommendations.append("⚪ عند التعادل — انتظر تأكيداً")
    elif profit_pct > -2:
        recommendations.append("🔴 خسارة متوسطة — راقب الوقف عن كثب")
    else:
        recommendations.append("🚨 خسارة كبيرة — فكر في الخروج")
    
    if trade_type == "SELL" and bullish_count >= 3:
        recommendations.append("🔴 الفريمات ضدك — أنصح بالخروج")
    elif trade_type == "BUY" and bearish_count >= 3:
        recommendations.append("🔴 الفريمات ضدك — أنصح بالخروج")
    elif vol_ratio < 0.6 and score < 50:
        recommendations.append("⚠️ حجم منخفض + تقييم ضعيف — انتظر تأكيداً")
    elif adx < 20:
        recommendations.append("⚠️ ADX ضعيف — لا تتسرع")
    
    if dist_to_sl < 0.5:
        recommendations.append("🚨 وقف الخسارة قريب جداً — جهز للخروج")
    
    lines = []
    lines.append(f"📊 **تحليل صفقة {asset_type}**")
    lines.append("━" * 45)
    lines.append("")
    
    lines.append("📌 **ملخص الموقف:**")
    if profit_pct > 0:
        lines.append(f"   ✅ ربح {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    elif profit_pct < 0:
        lines.append(f"   ❌ خسارة {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    else:
        lines.append(f"   ⚪ تعادل")
    lines.append("")
    
    lines.append("🔍 **تحليل الموقف:**")
    for line in analysis_lines[:7]:
        lines.append(f"   {line}")
    lines.append("")
    
    lines.append("💡 **توصيات تولين:**")
    if recommendations:
        for rec in recommendations[:4]:
            lines.append(f"   {rec}")
    else:
        lines.append("   🟡 راقب الصفقة — لا يوجد قرار عاجل")
    lines.append("")
    
    lines.append("━" * 45)
    lines.append("💙 القرار النهائي لك... أنا هنا لمساعدتك في التفكير")
    
    return "\n".join(lines)
import math
from datetime import datetime
from typing import Dict, List, Optional, Any

from constants import (
    logger, ANALYSIS_CACHE, ANALYSIS_CACHE_TTL
)
from utils import fmt_price, queue_telegram_message
from api_clients import get_mexc_candles, fetch_multiple_timeframes, get_fear_greed_index
from indicators import (
    calculate_rsi_7, calculate_macd_histogram, calculate_adx_14, calculate_atr_14,
    calculate_bollinger_bands, calculate_stochastic, calculate_vwap,
    calculate_supertrend_vpt_correct, calculate_vpt_supertrend_v11
)
from position_manager import (
    get_current_open_trade, load_trades_history, save_trades_history,
    AccountingSystem, close_trade_virtual, close_trade_manually,
    WARNING_LEVELS, should_send_warning, should_send_recommendation,
    record_warning, record_recommendation,
    check_sl_tp_hit, check_supertrend_reversal,
    check_distance_warnings, check_adx_warnings, check_volume_warnings
)


# ====================================================================================
# 🗄️ التخزين المؤقت للتحليل الشامل
# ====================================================================================

def get_cached_analysis(asset_type: str) -> Optional[Dict]:
    """الحصول على التحليل من الكاش إذا كان حديثاً"""
    cache_key = f"{asset_type}_{int(time.time() // ANALYSIS_CACHE_TTL)}"
    if cache_key in ANALYSIS_CACHE:
        cached = ANALYSIS_CACHE[cache_key]
        return cached.get('analysis')
    return None


def set_cached_analysis(asset_type: str, analysis: Dict):
    """تخزين التحليل في الكاش"""
    cache_key = f"{asset_type}_{int(time.time() // ANALYSIS_CACHE_TTL)}"
    ANALYSIS_CACHE[cache_key] = {
        'analysis': analysis,
        'timestamp': time.time()
    }
    if len(ANALYSIS_CACHE) > 20:
        keys = sorted(ANALYSIS_CACHE.keys(), key=lambda k: ANALYSIS_CACHE[k].get('timestamp', 0))
        for k in keys[:-20]:
            del ANALYSIS_CACHE[k]


# ====================================================================================
# 📊 دوال وصفية مساعدة للتقييم
# ====================================================================================

def _default_result(reason):
    """إرجاع نتيجة افتراضية عند فشل التحليل"""
    return {
        "score": 0,
        "grade": "بيانات غير كافية",
        "grade_emoji": "⚠️",
        "details": [f"⚠️ {reason}"],
        "context": "unknown",
        "metrics": {},
        "components": {},
        "trade_health": None,
    }


def _trend_desc(bullish_count, adx):
    if bullish_count == 3:
        return "اتجاه صاعد قوي ومؤكد" if adx > 25 else "اتجاه صاعد لكن الزخم ضعيف"
    elif bullish_count == 2:
        return "غالبية الفريمات صاعدة"
    elif bullish_count == 1:
        return "غالبية الفريمات هابطة"
    else:
        return "اتجاه هابط قوي ومؤكد" if adx > 25 else "اتجاه هابط لكن الزخم ضعيف"


def _momentum_desc(rsi, macd_hist, stoch):
    if rsi < 30 and macd_hist > 0:
        return "زخم صاعد قوي — ارتداد محتمل"
    elif rsi > 70 and macd_hist < 0:
        return "زخم هابط قوي — تصحيح محتمل"
    elif 40 <= rsi <= 60 and abs(macd_hist) < 0.3:
        return "زخم محايد — لا قوة اتجاهية واضحة"
    elif rsi < 40:
        return "زخم ضعيف نحو الأسفل"
    else:
        return "زخم ضعيف نحو الأعلى"


def _volatility_desc(bb_pos, atr_pct, vwap_dev):
    if atr_pct > 2.5:
        return "تقلب شديد — السوق متقلب جداً"
    elif atr_pct < 0.5:
        return "تقلب منخفض — السوق نائم"
    if bb_pos < 0.15:
        return "السعر عند القاع النسبي — ارتداد محتمل"
    elif bb_pos > 0.85:
        return "السعر عند القمة النسبية — تصحيح محتمل"
    if abs(vwap_dev) > 0.015:
        return "انحراف كبير عن السعر العادل"
    return "بنية سعرية متوازنة"


def _volume_desc(vol_ratio):
    if vol_ratio >= 2.0:
        return "سيولة استثنائية — حركة مدعومة بقوة"
    elif vol_ratio >= 1.5:
        return "سيولة مرتفعة — حركة حقيقية"
    elif vol_ratio >= 1.0:
        return "سيولة طبيعية"
    elif vol_ratio >= 0.6:
        return "سيولة منخفضة — حذر من الانزلاق"
    else:
        return "سيولة جافة جداً — تجنب الدخول"


def _sr_desc(price, s1, r1, pivot):
    if price <= 0:
        return "سعر غير صالح"
    if s1 <= 0 or r1 <= 0 or pivot <= 0:
        return "مستويات غير متوفرة"
    if price <= s1 * 1.003:
        return "السعر عند منطقة دعم قوية"
    elif price >= r1 * 0.997:
        return "السعر عند منطقة مقاومة قوية"
    elif abs(price - pivot) / price < 0.003:
        return "السعر عند نقطة الارتكاز"
    elif price < pivot:
        return "السعر في النطاق السفلي"
    else:
        return "السعر في النطاق العلوي"


def _sentiment_desc(fear_greed):
    if fear_greed <= 20:
        return "هلع شديد في السوق — فرصة تاريخية محتملة"
    elif fear_greed <= 35:
        return "خوف متزايد — بيئة شرائية محتملة"
    elif fear_greed <= 55:
        return "معنويات متوازنة"
    elif fear_greed <= 75:
        return "تفاؤل مرتفع — حذر من القمة"
    else:
        return "طمع مفرط — قمة بيعية محتملة"


def _detect_divergence(price_hist, rsi_hist, macd_hist):
    """كشف تباعد محسّن - يعيد نتائج آمنة دائماً"""
    if not price_hist or not rsi_hist or len(price_hist) < 15 or len(rsi_hist) < 15:
        return {"type": "none", "score": 50, "desc": "لا يوجد تباعد — بيانات غير كافية"}

    price_hist_clean = [p for p in price_hist if p is not None and p > 0]
    rsi_hist_clean = [r for r in rsi_hist if r is not None and 0 <= r <= 100]
    macd_hist_clean = [m for m in macd_hist if m is not None]

    if len(price_hist_clean) < 15 or len(rsi_hist_clean) < 15:
        return {"type": "none", "score": 50, "desc": "لا يوجد تباعد — بيانات غير كافية"}

    def find_peaks(data, min_dist=3):
        peaks = []
        for i in range(min_dist, len(data) - min_dist):
            is_peak = all(data[i] >= data[i-j] for j in range(1, min_dist+1))
            is_peak = is_peak and all(data[i] >= data[i+j] for j in range(1, min_dist+1))
            if is_peak:
                if not peaks or i - peaks[-1] >= min_dist:
                    peaks.append(i)
        return peaks[-5:]

    def find_troughs(data, min_dist=3):
        troughs = []
        for i in range(min_dist, len(data) - min_dist):
            is_trough = all(data[i] <= data[i-j] for j in range(1, min_dist+1))
            is_trough = is_trough and all(data[i] <= data[i+j] for j in range(1, min_dist+1))
            if is_trough:
                if not troughs or i - troughs[-1] >= min_dist:
                    troughs.append(i)
        return troughs[-5:]

    price_peaks = find_peaks(price_hist_clean)
    rsi_peaks = find_peaks(rsi_hist_clean)

    if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
        for pp_idx in range(len(price_peaks)-1, 0, -1):
            for rp_idx in range(len(rsi_peaks)-1, 0, -1):
                p1, p2 = price_peaks[pp_idx-1], price_peaks[pp_idx]
                r1, r2 = rsi_peaks[rp_idx-1], rsi_peaks[rp_idx]
                if abs(p1 - r1) <= 3 and abs(p2 - r2) <= 3:
                    if price_hist_clean[p2] > price_hist_clean[p1] * 1.003 and rsi_hist_clean[r2] < rsi_hist_clean[r1] * 0.98:
                        return {"type": "bearish_rsi", "score": 20, "desc": "تباعد هابط في RSI — السعر يصعد لكن الزخم يتراجع"}

    price_troughs = find_troughs(price_hist_clean)
    rsi_troughs = find_troughs(rsi_hist_clean)

    if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
        for pt_idx in range(len(price_troughs)-1, 0, -1):
            for rt_idx in range(len(rsi_troughs)-1, 0, -1):
                p1, p2 = price_troughs[pt_idx-1], price_troughs[pt_idx]
                r1, r2 = rsi_troughs[rt_idx-1], rsi_troughs[rt_idx]
                if abs(p1 - r1) <= 3 and abs(p2 - r2) <= 3:
                    if price_hist_clean[p2] < price_hist_clean[p1] * 0.997 and rsi_hist_clean[r2] > rsi_hist_clean[r1] * 1.02:
                        return {"type": "bullish_rsi", "score": 80, "desc": "تباعد صاعد في RSI — السعر يهبط لكن الزخم يتعزز"}

    if len(macd_hist_clean) >= 15:
        macd_peaks = find_peaks(macd_hist_clean)
        if len(macd_peaks) >= 2 and len(price_peaks) >= 2:
            for pp_idx in range(len(price_peaks)-1, 0, -1):
                for mp_idx in range(len(macd_peaks)-1, 0, -1):
                    p1, p2 = price_peaks[pp_idx-1], price_peaks[pp_idx]
                    m1, m2 = macd_peaks[mp_idx-1], macd_peaks[mp_idx]
                    if abs(p1 - m1) <= 3 and abs(p2 - m2) <= 3:
                        if price_hist_clean[p2] > price_hist_clean[p1] * 1.003 and macd_hist_clean[m2] < macd_hist_clean[m1] * 0.97:
                            return {"type": "bearish_macd", "score": 25, "desc": "تباعد هابط في MACD — السعر يصعد لكن الزخم يتراجع"}

    return {"type": "none", "score": 50, "desc": "لا يوجد تباعد ملحوظ"}


# ====================================================================================
# 🧠 محرك التقييم الشامل V8 FIXED
# ====================================================================================

def calculate_comprehensive_score(analysis, asset_type, open_trade=None):
    """
    ═══════════════════════════════════════════════════════════════════
    Tona Commodity Matrix Engine — V8 FIXED (Neutral Scoring)
    ═══════════════════════════════════════════════════════════════════
    🧠 محرك تقييم محايد — يُنتج تقييماً موضوعياً بدون انحياز شراء/بيع
    ✅ مع تحقق قوي من صحة البيانات لتجنب القيم الافتراضية الخاطئة
    ═══════════════════════════════════════════════════════════════════
    """
    
    if not analysis or not isinstance(analysis, dict):
        return _default_result("بيانات التحليل غير صالحة (ليست قاموساً)")
    
    price = analysis.get('price', 0)
    if not price or price <= 0:
        return _default_result(f"سعر غير صالح (القيمة: {price})")
    
    indicators = analysis.get('indicators', {})
    if not indicators or not isinstance(indicators, dict):
        return _default_result("بيانات المؤشرات مفقودة أو غير صالحة")
    
    try:
        trend_data = indicators.get('trend', {})
        if not isinstance(trend_data, dict):
            trend_data = {}
        bullish_count = trend_data.get('bullish_count', 0)
        if not isinstance(bullish_count, int) or bullish_count < 0 or bullish_count > 4:
            bullish_count = 0
        adx = trend_data.get('adx', 0)
        if not isinstance(adx, (int, float)) or adx < 0 or adx > 100:
            adx = 0
        
        momentum_data = indicators.get('momentum', {})
        if not isinstance(momentum_data, dict):
            momentum_data = {}
        rsi = momentum_data.get('rsi', 50)
        if not isinstance(rsi, (int, float)) or rsi < 0 or rsi > 100:
            rsi = 50
        macd_hist = momentum_data.get('macd_hist', 0)
        if not isinstance(macd_hist, (int, float)):
            macd_hist = 0
        stoch = momentum_data.get('stoch', 50)
        if not isinstance(stoch, (int, float)) or stoch < 0 or stoch > 100:
            stoch = 50
        
        volatility_data = indicators.get('volatility', {})
        if not isinstance(volatility_data, dict):
            volatility_data = {}
        bb_pos = volatility_data.get('bb_position', 0.5)
        if not isinstance(bb_pos, (int, float)) or bb_pos < 0 or bb_pos > 1:
            bb_pos = 0.5
        atr_pct = volatility_data.get('atr_percent', 1.0)
        if not isinstance(atr_pct, (int, float)) or atr_pct < 0:
            atr_pct = 1.0
        vwap_dev = volatility_data.get('vwap_deviation', 0)
        if not isinstance(vwap_dev, (int, float)):
            vwap_dev = 0
        
        volume_data = indicators.get('volume', {})
        if not isinstance(volume_data, dict):
            volume_data = {}
        vol_ratio = volume_data.get('ratio', 1.0)
        if not isinstance(vol_ratio, (int, float)) or vol_ratio < 0:
            vol_ratio = 1.0
        
        sr_levels = indicators.get('support_resistance', {})
        if not isinstance(sr_levels, dict):
            sr_levels = {}
        s1 = sr_levels.get('s1', price * 0.98)
        if not isinstance(s1, (int, float)) or s1 <= 0:
            s1 = price * 0.98
        r1 = sr_levels.get('r1', price * 1.02)
        if not isinstance(r1, (int, float)) or r1 <= 0:
            r1 = price * 1.02
        pivot = sr_levels.get('pivot', price)
        if not isinstance(pivot, (int, float)) or pivot <= 0:
            pivot = price
        
        sentiment_data = indicators.get('sentiment', {})
        if not isinstance(sentiment_data, dict):
            sentiment_data = {}
        fear_greed = sentiment_data.get('fear_greed', 50)
        if not isinstance(fear_greed, (int, float)) or fear_greed < 0 or fear_greed > 100:
            fear_greed = 50
        
        price_hist = analysis.get('price_history', [])
        if not isinstance(price_hist, list):
            price_hist = []
        rsi_hist = analysis.get('rsi_history', [])
        if not isinstance(rsi_hist, list):
            rsi_hist = []
        macd_hist_data = analysis.get('macd_history', [])
        if not isinstance(macd_hist_data, list):
            macd_hist_data = []
        
        # ── حساب التقييمات الفرعية ──
        if bullish_count >= 2:
            trend_score = 65 if adx > 25 else 55
            trend_desc = _trend_desc(bullish_count, adx)
        else:
            trend_score = 35 if adx > 25 else 45
            trend_desc = _trend_desc(bullish_count, adx)
        
        if rsi < 30:
            momentum_score = 70
        elif rsi > 70:
            momentum_score = 30
        elif 40 <= rsi <= 60 and abs(macd_hist) < 0.3:
            momentum_score = 50
        elif rsi < 40:
            momentum_score = 40
        else:
            momentum_score = 60
        momentum_desc = _momentum_desc(rsi, macd_hist, stoch)
        
        volatility_score = 50
        if atr_pct > 2.5:
            volatility_score = 60
        elif atr_pct < 0.5:
            volatility_score = 40
        if bb_pos < 0.15:
            volatility_score = min(volatility_score + 10, 65)
        elif bb_pos > 0.85:
            volatility_score = max(volatility_score - 10, 35)
        volatility_desc = _volatility_desc(bb_pos, atr_pct, vwap_dev)
        
        if vol_ratio >= 1.5:
            volume_score = 65
        elif vol_ratio >= 1.0:
            volume_score = 55
        elif vol_ratio >= 0.6:
            volume_score = 45
        else:
            volume_score = 35
        volume_desc = _volume_desc(vol_ratio)
        
        if price <= s1 * 1.003:
            sr_score = 65
        elif price >= r1 * 0.997:
            sr_score = 35
        elif abs(price - pivot) / price < 0.003:
            sr_score = 50
        else:
            sr_score = 50
        sr_desc = _sr_desc(price, s1, r1, pivot)
        
        if fear_greed <= 20:
            sentiment_score = 75
        elif fear_greed <= 35:
            sentiment_score = 65
        elif fear_greed <= 55:
            sentiment_score = 50
        elif fear_greed <= 75:
            sentiment_score = 35
        else:
            sentiment_score = 25
        sentiment_desc = _sentiment_desc(fear_greed)
        
        divergence = _detect_divergence(price_hist, rsi_hist, macd_hist_data)
        divergence_score = divergence.get('score', 50)
        divergence_desc = divergence.get('desc', 'لا يوجد تباعد')
        
        # ── حساب النتيجة النهائية (مرجحة) ──
        weights = {
            'trend': 0.25,
            'momentum': 0.20,
            'volatility': 0.15,
            'volume': 0.15,
            'sr': 0.15,
            'sentiment': 0.05,
            'divergence': 0.05
        }
        total_weight = sum(weights.values())
        if total_weight != 1.0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        final_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            volatility_score * weights['volatility'] +
            volume_score * weights['volume'] +
            sr_score * weights['sr'] +
            sentiment_score * weights['sentiment'] +
            divergence_score * weights['divergence']
        )
        
        final_score = round(final_score, 2)
        
        if final_score >= 70:
            grade = "إيجابي قوي"
            grade_emoji = "🟢"
            context = "bullish"
        elif final_score >= 60:
            grade = "إيجابي"
            grade_emoji = "🟡"
            context = "bullish"
        elif final_score >= 45:
            grade = "محايد"
            grade_emoji = "⚪"
            context = "neutral"
        elif final_score >= 35:
            grade = "سلبي"
            grade_emoji = "🟠"
            context = "bearish"
        else:
            grade = "سلبي قوي"
            grade_emoji = "🔴"
            context = "bearish"
        
        details = [
            f"📈 الاتجاه: {trend_desc} (درجة: {trend_score:.0f})",
            f"⚡ الزخم: {momentum_desc} (درجة: {momentum_score:.0f})",
            f"🌊 التقلب: {volatility_desc} (درجة: {volatility_score:.0f})",
            f"📊 الحجم: {volume_desc} (درجة: {volume_score:.0f})",
            f"🛡️ الدعم/المقاومة: {sr_desc} (درجة: {sr_score:.0f})",
            f"🧠 المشاعر: {sentiment_desc} (درجة: {sentiment_score:.0f})",
            f"📉 التباعد: {divergence_desc} (درجة: {divergence_score:.0f})"
        ]
        
        if open_trade:
            trade_type = open_trade.get('type', 'unknown')
            entry_price = open_trade.get('entry_price', 0)
            if entry_price > 0:
                pnl = ((price - entry_price) / entry_price * 100) if trade_type == 'long' else ((entry_price - price) / entry_price * 100)
                details.append(f"💼 الصفقة المفتوحة: {trade_type.upper()} | الربح/الخسارة: {pnl:.2f}%")
        
        result = {
            "score": final_score,
            "grade": grade,
            "grade_emoji": grade_emoji,
            "details": details,
            "context": context,
            "metrics": {
                "price": price,
                "rsi": rsi,
                "adx": adx,
                "vol_ratio": vol_ratio,
                "fear_greed": fear_greed,
                "bullish_count": bullish_count,
                "support": s1,
                "resistance": r1,
                "atr_percent": atr_pct,
                "bb_position": bb_pos
            },
            "components": {
                "trend": {"score": round(trend_score, 2), "weight": weights['trend']},
                "momentum": {"score": round(momentum_score, 2), "weight": weights['momentum']},
                "volatility": {"score": round(volatility_score, 2), "weight": weights['volatility']},
                "volume": {"score": round(volume_score, 2), "weight": weights['volume']},
                "sr": {"score": round(sr_score, 2), "weight": weights['sr']},
                "sentiment": {"score": round(sentiment_score, 2), "weight": weights['sentiment']},
                "divergence": {"score": round(divergence_score, 2), "weight": weights['divergence']}
            },
            "trade_health": {
                "status": "متوازن" if 45 <= final_score <= 60 else "قوي" if final_score > 60 else "ضعيف",
                "recommendation": "مراقبة" if 45 <= final_score <= 60 else "انتظار" if final_score < 45 else "تأكيد"
            } if open_trade else None
        }
        
        return result
        
    except Exception as e:
        return _default_result(f"خطأ في التقييم: {str(e)[:100]}")


# ====================================================================================
# 📊 التحليل الشامل (مع التخزين المؤقت)
# ====================================================================================

def perform_comprehensive_analysis(asset_type, is_monitoring=False, open_trade=None):
    """
    تحليل شامل للأصل المطلوب مع تخزين مؤقت
    ✅ هذه هي الدالة الأساسية للتحليل الفني الشامل
    """
    try:
        if not is_monitoring:
            cached = get_cached_analysis(asset_type)
            if cached:
                logger.info(f"📊 استخدام التحليل المخبأ لـ {asset_type}")
                try:
                    from advisor_core import format_concise_analysis
                    report = format_concise_analysis(cached, asset_type, is_monitoring, open_trade)
                except:
                    report = "⚠️ تحليل غير متوفر"
                return cached, report
        
        symbol = "EUR/USD" if asset_type == "eurusd" else "USD/JPY"
        data = get_mexc_candles(symbol, interval="Min15", limit=80)
        
        if not data or not data.get("closes") or len(data["closes"]) < 10:
            return None, "⚠️ لا توجد بيانات كافية للتحليل"
        
        closes = data["closes"]
        highs = data["highs"]
        lows = data["lows"]
        volumes = data["volumes"]
        
        current_price = closes[-1]
        current_rsi = calculate_rsi_7(closes)[-1] if len(closes) >= 7 else 50
        current_macd = calculate_macd_histogram(closes)[-1] if len(closes) >= 35 else 0
        adx = calculate_adx_14(data)
        atr = calculate_atr_14(data)
        
        upper, basis, lower = calculate_bollinger_bands(closes)
        bb_upper = upper[-1] if upper else current_price * 1.02
        bb_basis = basis[-1] if basis else current_price
        bb_lower = lower[-1] if lower else current_price * 0.98
        
        stoch = calculate_stochastic(highs, lows, closes)
        stoch_value = stoch[-1] if stoch else 50
        
        vwap_values = calculate_vwap(data)
        vwap = vwap_values[-1] if vwap_values else current_price
        
        vol_ratio = 1.0
        if volumes and len(volumes) > 20:
            current_vol = volumes[-1]
            avg_vol = sum(volumes[-20:-1]) / 19 if len(volumes) > 20 else current_vol
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
        
        st_line_arr, trend, _ = calculate_supertrend_vpt_correct(
            data,
            st_mult=2.2 if asset_type == "eurusd" else 2.5,
            st_period=100,
            vpt_len=10
        )
        
        timeframes_data = {
            "5m": {"interval": "Min5", "limit": 50},
            "1h": {"interval": "Min60", "limit": 100},
            "4h": {"interval": "Hour4", "limit": 50}
        }
        results = fetch_multiple_timeframes(symbol, timeframes_data)
        
        timeframes = {}
        for tf_name, tf_data in [("5m", results.get("5m")), ("1h", results.get("1h")), ("4h", results.get("4h"))]:
            if tf_data and tf_data.get("closes") and len(tf_data["closes"]) >= 10:
                tcloses = tf_data["closes"]
                st_l, tr, _ = calculate_supertrend_vpt_correct(tf_data, st_mult=2.2 if asset_type == "eurusd" else 2.5)
                timeframes[tf_name] = {
                    "price": tcloses[-1],
                    "trend": "صاعد" if tr[-1] == 1 else "هابط" if tr[-1] == -1 else "محايد",
                    "supertrend": {"line": st_l[-1] if st_l else tcloses[-1], "trend": tr[-1] if tr else 1}
                }
        
        analysis = {
            "price": current_price,
            "asset": asset_type,
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                "trend": {
                    "bullish_count": sum(1 for tf in timeframes.values() if tf.get("trend") == "صاعد"),
                    "adx": adx,
                    "current_trend": "صاعد" if trend[-1] == 1 else "هابط" if trend[-1] == -1 else "محايد"
                },
                "momentum": {
                    "rsi": current_rsi,
                    "macd_hist": current_macd,
                    "stoch": stoch_value
                },
                "volatility": {
                    "atr_percent": (atr / current_price) * 100 if current_price > 0 else 1.0,
                    "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5,
                    "vwap_deviation": (current_price - vwap) / vwap if vwap > 0 else 0
                },
                "volume": {
                    "ratio": vol_ratio
                },
                "support_resistance": {
                    "s1": current_price * 0.98,
                    "r1": current_price * 1.02,
                    "pivot": current_price
                },
                "sentiment": {
                    "fear_greed": 50
                },
                "bollinger": {
                    "upper": bb_upper,
                    "basis": bb_basis,
                    "lower": bb_lower
                },
                "vwap": vwap
            },
            "timeframes": {
                "15m": {
                    "price": current_price,
                    "rsi": current_rsi,
                    "macd": current_macd,
                    "adx": adx,
                    "atr": atr,
                    "volume_ratio": vol_ratio,
                    "trend": "صاعد" if trend[-1] == 1 else "هابط" if trend[-1] == -1 else "محايد",
                    "supertrend": {"line": st_line_arr[-1] if st_line_arr else current_price, "trend": trend[-1] if trend else 1},
                    "bollinger": {"upper": bb_upper, "basis": bb_basis, "lower": bb_lower},
                    "stochastic": stoch_value,
                    "vwap": vwap,
                    "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
                }
            },
            "supertrend": {
                "line": st_line_arr[-1] if st_line_arr else current_price,
                "trend": trend[-1] if trend else 1
            },
            "vpt": {
                "value": 0
            },
            "fear_greed": 50,
            "support_resistance": {
                "support": current_price * 0.98,
                "resistance": current_price * 1.02,
                "pivot": current_price
            },
            "price_history": closes[-50:] if len(closes) >= 50 else closes,
            "rsi_history": calculate_rsi_7(closes)[-50:] if len(closes) >= 50 else calculate_rsi_7(closes),
            "macd_history": calculate_macd_histogram(closes)[-50:] if len(closes) >= 50 else calculate_macd_histogram(closes)
        }
        
        for tf_name, tf_data in timeframes.items():
            if tf_name in analysis["timeframes"]:
                analysis["timeframes"][tf_name].update(tf_data)
            else:
                analysis["timeframes"][tf_name] = tf_data
        
        analysis["comprehensive_score"] = calculate_comprehensive_score(analysis, asset_type, open_trade)
        
        set_cached_analysis(asset_type, analysis)
        
        try:
            from advisor_core import format_concise_analysis
            report = format_concise_analysis(analysis, asset_type, is_monitoring, open_trade)
        except ImportError:
            score = analysis["comprehensive_score"].get("score", 50)
            grade = analysis["comprehensive_score"].get("grade", "محايد")
            report = f"📊 تحليل {asset_type}\n💰 السعر: ${current_price:.2f}\n📊 التقييم: {score:.0f}% ({grade})"
        
        return analysis, report
        
    except Exception as e:
        logger.error(f"خطأ في التحليل الشامل لـ {asset_type}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, f"⚠️ حدث خطأ أثناء التحليل: {str(e)}"


# ====================================================================================
# 🔍 تحليل الصفقة المفتوحة
# ====================================================================================

def analyze_open_trade(asset_type, open_trade):
    """
    تحليل شامل للصفقة المفتوحة — استنتاجات ونصائح فقط
    ✅ يستخدم التحليل الفني الشامل مع تحقق قوي من البيانات
    """
    if not open_trade:
        return "⚠️ لا توجد صفقة مفتوحة"
    
    analysis, report = perform_comprehensive_analysis(asset_type, True, open_trade)
    if not analysis or not isinstance(analysis, dict):
        return "⚠️ لا توجد بيانات كافية للتحليل"
    
    price = analysis.get("price", 0)
    if not isinstance(price, (int, float)) or price <= 0:
        price = open_trade.get("entry_price", 0)
    
    timeframes = analysis.get("timeframes", {}) if isinstance(analysis.get("timeframes"), dict) else {}
    comp_score = analysis.get("comprehensive_score", {}) if isinstance(analysis.get("comprehensive_score"), dict) else {}
    indicators = analysis.get("indicators", {}) if isinstance(analysis.get("indicators"), dict) else {}
    
    entry_price = open_trade.get('entry_price', 0)
    trade_type = open_trade.get('type', 'BUY')
    sl = open_trade.get('sl', 0)
    tp = open_trade.get('tp', 0)
    
    if trade_type == "BUY":
        profit_pct = ((price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
        profit_dollars = AccountingSystem.calculate_profit_dollars(entry_price, price, "BUY")
    else:
        profit_pct = ((entry_price - price) / entry_price) * 100 if entry_price > 0 else 0
        profit_dollars = AccountingSystem.calculate_profit_dollars(entry_price, price, "SELL")
    
    trends = []
    for tf in ["5m", "15m", "1h", "4h"]:
        if tf in timeframes and isinstance(timeframes.get(tf), dict):
            t = timeframes[tf].get("trend", "محايد")
            if t and t != "محايد":
                trends.append((tf, t))
    
    bullish_count = sum(1 for _, t in trends if t == "صاعد")
    bearish_count = sum(1 for _, t in trends if t == "هابط")
    total_trends = len(trends)
    
    tf_15m = timeframes.get("15m", {}) if isinstance(timeframes, dict) else {}
    
    rsi = tf_15m.get("rsi", 50) if isinstance(tf_15m, dict) else 50
    if not isinstance(rsi, (int, float)) or rsi < 0 or rsi > 100:
        rsi = 50
    
    adx = tf_15m.get("adx", 15) if isinstance(tf_15m, dict) else 15
    if not isinstance(adx, (int, float)) or adx < 0 or adx > 100:
        adx = 15
    
    macd = tf_15m.get("macd", 0) if isinstance(tf_15m, dict) else 0
    if not isinstance(macd, (int, float)):
        macd = 0
    
    vol_ratio = tf_15m.get("volume_ratio", 1.0) if isinstance(tf_15m, dict) else 1.0
    if not isinstance(vol_ratio, (int, float)) or vol_ratio < 0:
        vol_ratio = 1.0
    
    vwap = tf_15m.get("vwap", price) if isinstance(tf_15m, dict) else price
    if not isinstance(vwap, (int, float)) or vwap <= 0:
        vwap = price
    
    trend_15m = tf_15m.get("trend", "محايد") if isinstance(tf_15m, dict) else "محايد"
    
    analysis_lines = []
    
    if profit_pct > 0:
        analysis_lines.append(f"✅ **أنت رابح:** {profit_pct:+.2f}% (+${profit_dollars:+.2f})")
    elif profit_pct < 0:
        analysis_lines.append(f"❌ **أنت خاسر:** {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    else:
        analysis_lines.append(f"⚪ **أنت عند التعادل:** {profit_pct:+.2f}%")
    
    if total_trends > 0:
        if trade_type == "SELL" and bullish_count >= 3:
            analysis_lines.append(f"🔴 **تحذير:** {bullish_count}/{total_trends} فريمات صاعدة **ضد صفقتك**!")
            analysis_lines.append("   السوق يصعد بينما أنت تبيع — هذا خطر كبير")
        elif trade_type == "BUY" and bearish_count >= 3:
            analysis_lines.append(f"🔴 **تحذير:** {bearish_count}/{total_trends} فريمات هابطة **ضد صفقتك**!")
            analysis_lines.append("   السوق يهبط بينما أنت تشتري — هذا خطر كبير")
        elif trade_type == "SELL" and bearish_count >= 3:
            analysis_lines.append(f"✅ **جيد:** {bearish_count}/{total_trends} فريمات هابطة **تدعم صفقتك**")
        elif trade_type == "BUY" and bullish_count >= 3:
            analysis_lines.append(f"✅ **جيد:** {bullish_count}/{total_trends} فريمات صاعدة **تدعم صفقتك**")
        else:
            analysis_lines.append(f"🟡 **محايد:** الفريمات متضاربة ({bullish_count} صاعد / {bearish_count} هابط)")
    else:
        analysis_lines.append("🟡 **لا توجد بيانات كافية للفريمات**")
    
    if vol_ratio < 0.6:
        analysis_lines.append(f"🔴 **حجم منخفض:** {vol_ratio:.1f}x المتوسط — الحركة ضعيفة")
        analysis_lines.append("   قد يكون السوق في منطقة تجميع أو تصريف")
    elif vol_ratio > 1.5:
        analysis_lines.append(f"✅ **حجم مرتفع:** {vol_ratio:.1f}x المتوسط — الحركة مدعومة")
    else:
        analysis_lines.append(f"🟡 **حجم طبيعي:** {vol_ratio:.1f}x المتوسط")
    
    if adx < 20:
        analysis_lines.append(f"🔴 **ضعف الاتجاه:** ADX {adx:.0f} — السوق عرضي")
        analysis_lines.append("   لا يوجد اتجاه واضح، أي صفقة الآن مخاطرة")
    elif adx > 25:
        analysis_lines.append(f"✅ **اتجاه قوي:** ADX {adx:.0f} — الاتجاه واضح")
    else:
        analysis_lines.append(f"🟡 **اتجاه متوسط:** ADX {adx:.0f}")
    
    if trade_type == "SELL" and rsi > 70:
        analysis_lines.append(f"✅ **RSI يدعمك:** {rsi:.0f} — منطقة ذروة شراء (فرصة بيع)")
    elif trade_type == "BUY" and rsi < 30:
        analysis_lines.append(f"✅ **RSI يدعمك:** {rsi:.0f} — منطقة ذروة بيع (فرصة شراء)")
    elif trade_type == "SELL" and rsi < 30:
        analysis_lines.append(f"🔴 **RSI ضدك:** {rsi:.0f} — منطقة ذروة بيع (السوق قد يرتد)")
    elif trade_type == "BUY" and rsi > 70:
        analysis_lines.append(f"🔴 **RSI ضدك:** {rsi:.0f} — منطقة ذروة شراء (السوق قد يصحح)")
    else:
        analysis_lines.append(f"🟡 **RSI محايد:** {rsi:.0f}")
    
    if trade_type == "SELL" and macd < 0:
        analysis_lines.append(f"✅ **MACD يدعمك:** سلبي ({macd:.4f})")
    elif trade_type == "BUY" and macd > 0:
        analysis_lines.append(f"✅ **MACD يدعمك:** إيجابي ({macd:.4f})")
    elif trade_type == "SELL" and macd > 0:
        analysis_lines.append(f"🔴 **MACD ضدك:** إيجابي ({macd:.4f})")
    elif trade_type == "BUY" and macd < 0:
        analysis_lines.append(f"🔴 **MACD ضدك:** سلبي ({macd:.4f})")
    else:
        analysis_lines.append(f"🟡 **MACD محايد:** {macd:.4f}")
    
    if trade_type == "SELL":
        dist_to_sl = ((sl - price) / entry_price) * 100 if sl > 0 and entry_price > 0 else 0
        dist_to_tp = ((price - tp) / entry_price) * 100 if tp > 0 and entry_price > 0 else 0
    else:
        dist_to_sl = ((price - sl) / entry_price) * 100 if sl > 0 and entry_price > 0 else 0
        dist_to_tp = ((tp - price) / entry_price) * 100 if tp > 0 and entry_price > 0 else 0
    
    if dist_to_sl < 0.5:
        analysis_lines.append(f"🚨 **خطر:** وقف الخسارة قريب جداً ({dist_to_sl:.2f}%)")
        analysis_lines.append("   أنصح بتضييق الوقف أو الخروج")
    elif dist_to_sl < 1.0:
        analysis_lines.append(f"⚠️ **تنبيه:** وقف الخسارة قريب ({dist_to_sl:.2f}%)")
    
    if dist_to_tp < 0.5:
        analysis_lines.append(f"🎯 **قرب الهدف:** المسافة للهدف {dist_to_tp:.2f}%")
        analysis_lines.append("   فكر في جني الأرباح")
    
    score = comp_score.get("score", 50) if isinstance(comp_score, dict) else 50
    if not isinstance(score, (int, float)):
        score = 50
    
    if score >= 70:
        analysis_lines.append(f"✅ **التقييم الشامل:** {score:.0f}% — قوي")
    elif score >= 55:
        analysis_lines.append(f"🟡 **التقييم الشامل:** {score:.0f}% — متوسط")
    else:
        analysis_lines.append(f"🔴 **التقييم الشامل:** {score:.0f}% — ضعيف")
    
    recommendations = []
    
    if profit_pct > 3:
        recommendations.append("✅ ربح جيد — فكر في جني 50% من الأرباح")
    elif profit_pct > 0.5:
        recommendations.append("🟡 ربح بسيط — حرك الوقف إلى نقطة الدخول")
    elif profit_pct > -0.5:
        recommendations.append("⚪ عند التعادل — انتظر تأكيداً")
    elif profit_pct > -2:
        recommendations.append("🔴 خسارة متوسطة — راقب الوقف عن كثب")
    else:
        recommendations.append("🚨 خسارة كبيرة — فكر في الخروج")
    
    if trade_type == "SELL" and bullish_count >= 3:
        recommendations.append("🔴 الفريمات ضدك — أنصح بالخروج")
    elif trade_type == "BUY" and bearish_count >= 3:
        recommendations.append("🔴 الفريمات ضدك — أنصح بالخروج")
    elif vol_ratio < 0.6 and score < 50:
        recommendations.append("⚠️ حجم منخفض + تقييم ضعيف — انتظر تأكيداً")
    elif adx < 20:
        recommendations.append("⚠️ ADX ضعيف — لا تتسرع")
    
    if dist_to_sl < 0.5:
        recommendations.append("🚨 وقف الخسارة قريب جداً — جهز للخروج")
    
    lines = []
    lines.append(f"📊 **تحليل صفقة {asset_type}**")
    lines.append("━" * 45)
    lines.append("")
    
    lines.append("📌 **ملخص الموقف:**")
    if profit_pct > 0:
        lines.append(f"   ✅ ربح {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    elif profit_pct < 0:
        lines.append(f"   ❌ خسارة {profit_pct:+.2f}% (${profit_dollars:+.2f})")
    else:
        lines.append(f"   ⚪ تعادل")
    lines.append("")
    
    lines.append("🔍 **تحليل الموقف:**")
    for line in analysis_lines[:7]:
        lines.append(f"   {line}")
    lines.append("")
    
    lines.append("💡 **توصيات تولين:**")
    if recommendations:
        for rec in recommendations[:4]:
            lines.append(f"   {rec}")
    else:
        lines.append("   🟡 راقب الصفقة — لا يوجد قرار عاجل")
    lines.append("")
    
    lines.append("━" * 45)
    lines.append("💙 القرار النهائي لك... أنا هنا لمساعدتك في التفكير")
    
    return "\n".join(lines)
