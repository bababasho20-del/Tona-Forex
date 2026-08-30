# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 MONITORING.PY - الخيوط (الماسح، المراقبة العميقة، مرسل تليجرام، فحص الصحة، محرك الأحلام)
📌 يحتوي على جميع خيوط التشغيل الخلفية للبوت
═══════════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import json
import threading
import queue
from datetime import datetime

from constants import (
    logger, TELEGRAM_QUEUE, MONITOR_TRIGGER, MONITOR_TRIGGER_LOCK,
    SIGNAL_CHECK_INTERVAL, MONITORING_INTERVAL,
    ANALYSIS_CACHE, ANALYSIS_CACHE_TTL
)
from utils import queue_telegram_message, _send_telegram_message, get_position_file
from api_clients import get_mexc_candles
from indicators import calculate_adx_14
from analysis import perform_comprehensive_analysis, set_cached_analysis
from position_manager import (
    get_current_open_trade, load_trades_history, save_trades_history,
    check_sl_tp_hit, check_supertrend_reversal, check_distance_warnings,
    check_adx_warnings, check_volume_warnings, save_snapshot_to_learning
)
from trading_logic import analyze_and_send


# ====================================================================================
# 🔄 ماسح الإشارات (Signal Scanner)
# ====================================================================================

def signal_scanner():
    """ماسح الإشارات - يعمل كل 60 ثانية"""
    logger.info("[Scanner] بدأ التشغيل")
    while True:
        start = time.time()
        for asset_type in ["eurusd", "usdjpy"]:
            try:
                analyze_and_send(asset_type, is_manual=False)
            except Exception as e:
                logger.error(f"[Scanner] خطأ في فحص {asset_type}: {e}")
        elapsed = time.time() - start
        time.sleep(max(0, SIGNAL_CHECK_INTERVAL - elapsed))


# ====================================================================================
# 🔍 المراقبة العميقة (Deep Monitor)
# ====================================================================================

def deep_monitor():
    """المراقبة العميقة - تعمل كل 5 دقائق وتستخدم التحليل الشامل"""
    logger.info("[Monitor] بدأ التشغيل")
    last_scheduled = {"oil": 0, "silver": 0}
    last_tcn_save = 0
    
    while True:
        now = time.time()
        
        # محاولة حفظ حالة TCN (إذا كان متاحاً)
        try:
            from constants import TCN_AVAILABLE, TCN
            if TCN_AVAILABLE and TCN and now - last_tcn_save >= 300:
                try:
                    TCN.save_state()
                    logger.info("🧠 تم حفظ حالة TCN")
                    last_tcn_save = now
                except Exception as e:
                    logger.error(f"❌ فشل حفظ TCN: {e}")
        except:
            pass
        
        for asset_type in ["eurusd", "usdjpy"]:
            should_run = False
            reason = "scheduled"
            if now - last_scheduled[asset_type] >= MONITORING_INTERVAL:
                should_run = True
            with MONITOR_TRIGGER_LOCK:
                trigger = MONITOR_TRIGGER[asset_type]
                if trigger and now - trigger["time"] < 60:
                    should_run = True
                    reason = trigger["reason"]
                    MONITOR_TRIGGER[asset_type] = None
            if should_run:
                try:
                    _run_deep_monitor(asset_type, reason)
                    last_scheduled[asset_type] = now
                except Exception as e:
                    logger.error(f"[Monitor] خطأ في {asset_type}: {e}")
        
        time.sleep(5)


def _run_deep_monitor(asset_type, reason):
    """
    تشغيل المراقبة العميقة - باستخدام التحليل الشامل
    ✅ معدل بالكامل لإزالة خطأ 'trades'
    ✅ يستخدم التحليل الشامل مباشرة دون افتراض وجود مفتاح 'trades'
    """
    logger.info(f"[Monitor] تحليل عميق لـ {asset_type} — السبب: {reason}")
    
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        if reason == "scheduled":
            return
        with MONITOR_TRIGGER_LOCK:
            MONITOR_TRIGGER[asset_type] = None
        return

    analysis, _ = perform_comprehensive_analysis(asset_type, True, open_trade)
    
    if not analysis:
        logger.warning(f"⚠️ فشل الحصول على التحليل الشامل لـ {asset_type} في المراقبة")
        return
    
    # ================================================================
    # ✅ استخراج البيانات من التحليل الشامل (بدون استخدام 'trades')
    # ================================================================
    current_price = analysis.get("price", 0)
    
    # استخراج بيانات الفريم 15 دقيقة
    timeframes = analysis.get("timeframes", {})
    tf_15m = timeframes.get("15m", {}) if isinstance(timeframes, dict) else {}
    
    # استخراج المؤشرات
    indicators = analysis.get("indicators", {}) if isinstance(analysis.get("indicators"), dict) else {}
    
    # ================================================================
    # ✅ قراءة المؤشرات من tf_15m مع تحقق get()
    # ================================================================
    adx = tf_15m.get("adx", 15) if isinstance(tf_15m, dict) else 15
    vol_ratio = tf_15m.get("volume_ratio", 1.0) if isinstance(tf_15m, dict) else 1.0
    rsi = tf_15m.get("rsi", 50) if isinstance(tf_15m, dict) else 50
    trend = tf_15m.get("trend", "محايد") if isinstance(tf_15m, dict) else "محايد"
    macd = tf_15m.get("macd", 0) if isinstance(tf_15m, dict) else 0
    
    # ================================================================
    # ✅ استخراج SuperTrend من التحليل
    # ================================================================
    supertrend_data = analysis.get("supertrend", {}) if isinstance(analysis.get("supertrend"), dict) else {}
    st_trend = supertrend_data.get("trend", 1) if isinstance(supertrend_data, dict) else 1
    st_line = supertrend_data.get("line", current_price) if isinstance(supertrend_data, dict) else current_price
    
    # ================================================================
    # ✅ استخراج Bollinger Bands من tf_15m
    # ================================================================
    bb = tf_15m.get("bollinger", {}) if isinstance(tf_15m, dict) else {}
    bb_upper = bb.get("upper", current_price * 1.02) if isinstance(bb, dict) else current_price * 1.02
    bb_middle = bb.get("basis", current_price) if isinstance(bb, dict) else current_price
    bb_lower = bb.get("lower", current_price * 0.98) if isinstance(bb, dict) else current_price * 0.98
    
    # ================================================================
    # ✅ استخراج الدعم والمقاومة من indicators
    # ================================================================
    sr = indicators.get("support_resistance", {}) if isinstance(indicators, dict) else {}
    support = sr.get("s1", current_price * 0.98) if isinstance(sr, dict) else current_price * 0.98
    resistance = sr.get("r1", current_price * 1.02) if isinstance(sr, dict) else current_price * 1.02
    
    # ================================================================
    # ✅ استخراج المشاعر من indicators
    # ================================================================
    sentiment = indicators.get("sentiment", {}) if isinstance(indicators, dict) else {}
    fear_greed = sentiment.get("fear_greed", 50) if isinstance(sentiment, dict) else 50
    
    # ================================================================
    # ✅ استخراج VWAP من tf_15m
    # ================================================================
    vwap = tf_15m.get("vwap", 0) if isinstance(tf_15m, dict) else 0
    
    # تحديث السعر في الصفقة المفتوحة
    if open_trade:
        open_trade["last_price"] = current_price
        pos_file = get_position_file(asset_type)
        try:
            with open(pos_file, 'w', encoding='utf-8') as f:
                json.dump(open_trade, f, indent=2, ensure_ascii=False)
        except:
            pass

    # التحقق من ضرب SL/TP
    if open_trade:
        if check_sl_tp_hit(asset_type, current_price, open_trade):
            return
        if check_supertrend_reversal(asset_type, current_price, st_trend, open_trade):
            return

    # إرسال التحذيرات
    if open_trade:
        check_distance_warnings(asset_type, current_price, open_trade)
        check_adx_warnings(asset_type, adx, open_trade)
        check_volume_warnings(asset_type, vol_ratio, open_trade)

    # حفظ اللقطة في قاعدة التعلم
    try:
        if open_trade:
            profit_dollars = open_trade.get('profit_dollars', 0)
            entry_price = open_trade.get('entry_price', current_price)
            profit_pct = ((current_price - entry_price) / entry_price * 100) if entry_price != 0 else 0
            
            snapshot_data = {
                'trade_id': open_trade.get('trade_id', ''),
                'timestamp': datetime.now().isoformat(),
                'price': current_price,
                'rsi': rsi,
                'adx': adx,
                'macd': macd,
                'st_trend': 'صاعد' if st_trend == 1 else 'هابط',
                'volume_ratio': vol_ratio,
                'profit_dollars': profit_dollars,
                'profit_pct': profit_pct,
                'warning_level': len(open_trade.get('warnings_sent', [])),
                'fear_greed_index': fear_greed,
                'market_regime': 'unknown',
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'vwap': vwap,
                'support': support,
                'resistance': resistance,
                'trend': trend,
            }
            save_snapshot_to_learning(snapshot_data)
            logger.info(f"💾 تم حفظ لقطة للصفقة {open_trade.get('trade_id')} - السعر: ${current_price:.2f}")
    except Exception as e:
        logger.error(f"❌ فشل حفظ اللقطة: {e}")


def check_and_monitor_positions(asset_type, current_price, st_line, current_trend, data=None):
    """مراقبة الصفقة (Fallback)"""
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        return

    if check_sl_tp_hit(asset_type, current_price, open_trade):
        return

    if check_supertrend_reversal(asset_type, current_price, current_trend, open_trade):
        return

    if data:
        adx = calculate_adx_14(data)
        vol_ratio = 1.0
        if data.get("volumes") and len(data["volumes"]) > 20:
            current_vol = data["volumes"][-1]
            avg_vol = sum(data["volumes"][-20:-1]) / 19
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0

        check_distance_warnings(asset_type, current_price, open_trade)
        check_adx_warnings(asset_type, adx, open_trade)
        check_volume_warnings(asset_type, vol_ratio, open_trade)

    pos_file = get_position_file(asset_type)
    try:
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(open_trade, f, indent=2, ensure_ascii=False)
    except:
        pass


# ====================================================================================
# 📨 مرسل طابور Telegram
# ====================================================================================

def telegram_sender():
    """معالج طابور Telegram"""
    logger.info("[Sender] بدأ التشغيل")
    while True:
        try:
            msg = TELEGRAM_QUEUE.get(timeout=1)
            _send_telegram_message(msg["text"], msg.get("chat_id"))
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"[Sender] خطأ: {e}")


# ====================================================================================
# 🌙 محرك الأحلام (Dream Engine)
# ====================================================================================

def _dream_worker():
    """محرك الأحلام"""
    logger.info("🌙 Dream Worker بدأ التشغيل")
    while True:
        try:
            time.sleep(600)
            try:
                from constants import DREAM_AVAILABLE, DREAM, PROMETHEUS_AVAILABLE, PROMETHEUS
                if DREAM_AVAILABLE and DREAM:
                    DREAM.dream()
                    if PROMETHEUS_AVAILABLE and PROMETHEUS:
                        try:
                            PROMETHEUS._update_emotions({'trigger': 'dream_completed'})
                        except:
                            pass
            except ImportError:
                pass
            except Exception as e:
                logger.error(f"خطأ في Dream Worker: {e}")
        except Exception as e:
            logger.error(f"خطأ في Dream Worker: {e}")


# ====================================================================================
# 🩺 فحص صحة النظام
# ====================================================================================

def health_check():
    """فحص صحة النظام"""
    logger.info("[Health] بدأ التشغيل")
    while True:
        time.sleep(60)
        queue_size = TELEGRAM_QUEUE.qsize()
        if queue_size > 50:
            logger.warning(f"[Health] Queue كبيرة: {queue_size} رسائل")
        
        try:
            from constants import TCN_AVAILABLE, TCN
            if TCN_AVAILABLE and TCN:
                try:
                    consciousness = TCN.get_consciousness()
                    logger.info(f"[Health] 🧠 TCN: {consciousness.dominant_emotion} | ثقة: {consciousness.confidence*100:.0f}%")
                except Exception as e:
                    logger.error(f"[Health] ❌ TCN غير مستجيب: {e}")
        except:
            pass
        
        for asset in ["eurusd", "usdjpy"]:
            trade = get_current_open_trade(asset)
            if trade:
                logger.info(f"[Health] 📊 صفقة {asset} مفتوحة: {trade.get('type')} @ ${trade.get('entry_price', 0):.2f}")
        
        logger.info(f"[Health] ✅ Queue={queue_size}")
