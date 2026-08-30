# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 POSITION_MANAGER.PY - إدارة الصفقات (فتح، إغلاق، حفظ، تحميل، المحاسبة، التحذيرات)
📌 يحتوي على نظام إدارة الصفقات بالكامل، المحاسبة، ونظام التحذيرات الذكي
═══════════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from constants import (
    logger, FILE_LOCKS, TRADES_FILE_OIL, TRADES_FILE_SILVER,
    CURRENT_POSITION_FILE_OIL, CURRENT_POSITION_FILE_SILVER,
    MONITOR_TRIGGER, MONITOR_TRIGGER_LOCK,
    last_signal_states, last_signal_time, LAST_SIGNAL_LOCK
)
from utils import (
    safe_file_operation, get_trades_file, get_position_file,
    fmt_price, queue_telegram_message
)
from api_clients import (
    load_json_from_gist, save_json_to_gist,
    save_trade_to_learning, save_snapshot_to_learning
)
from indicators import (
    calculate_adx_14, calculate_atr_14,
    calculate_rsi_7, calculate_macd_histogram
)

# ====================================================================================
# 📊 نظام المحاسبة (Accounting)
# ====================================================================================

class AccountingSystem:
    """نظام المحاسبة - حساب الأرباح والخسائر"""
    INITIAL_CAPITAL = 100.0
    ENTRY_AMOUNT = 1.0
    LEVERAGE = 200.0
    ISOLATED_MARGIN = 20.0

    @classmethod
    def calculate_profit_dollars(cls, entry_price, exit_price, trade_type, leverage=None):
        leverage = leverage or cls.LEVERAGE
        if trade_type == "BUY":
            price_change = (exit_price - entry_price) / entry_price
        else:
            price_change = (entry_price - exit_price) / entry_price
        return price_change * cls.ENTRY_AMOUNT * leverage

    @classmethod
    def format_profit(cls, profit_dollars):
        if profit_dollars > 0:
            return f"✅ ربح: +${profit_dollars:.2f}"
        elif profit_dollars < 0:
            return f"❌ خسارة: -${abs(profit_dollars):.2f}"
        return "⚖️ متعادلة: $0.00"


# ====================================================================================
# 📁 دوال تحميل وحفظ البيانات
# ====================================================================================

def load_config():
    """تحميل إعدادات الاستراتيجية من Gist أو الملف المحلي"""
    default_config = {
        "strategies": {
            "oil": {
                "st_multiplier": 1.5,
                "st_period": 100,
                "vpt_len": 10,
                "vpt_ema_length": 14,
                "base_timeframe": "Min15",
                "use_rsi_filter": False,
                "use_macd_filter": False,
                "use_adx_filter": False,
                "rsi_period": 7,
                "rsi_min": 35,
                "rsi_max": 65,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "macd_threshold": 0.0,
                "sltp_mode": "ATR",
                "sl_atr_mult": 2.0,
                "tp_atr_mult": 3.0,
                "min_rr": 1.0,
                "use_trailing": True,
                "trail_offset": 1.5,
                "channel_buffer": 0.0,
                "risk_per_trade": 1.0,
                "max_leverage": 200.0,
                "signal_strength_enabled": True,
                "confirmation_required": False,
                "base_sl_mult": 1.5,
                "base_tp_mult": 2.5,
                "min_rr_dynamic": 1.0,
                "atr_period_dynamic": 14,
            },
            "silver": {
                "st_multiplier": 2.2,
                "st_period": 100,
                "vpt_len": 10,
                "vpt_ema_length": 10,
                "base_timeframe": "Min15",
                "use_rsi_filter": True,
                "use_macd_filter": True,
                "use_adx_filter": False,
                "rsi_period": 7,
                "rsi_min": 35,
                "rsi_max": 65,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "macd_threshold": 0.0,
                "sltp_mode": "ATR",
                "sl_atr_mult": 2.0,
                "tp_atr_mult": 3.0,
                "min_rr": 1.0,
                "use_trailing": True,
                "trail_offset": 1.5,
                "channel_buffer": 0.0,
                "risk_per_trade": 1.0,
                "max_leverage": 200.0,
                "signal_strength_enabled": True,
                "confirmation_required": False,
                "base_sl_mult": 1.5,
                "base_tp_mult": 2.5,
                "min_rr_dynamic": 1.0,
                "atr_period_dynamic": 14,
            }
        },
        "system": {
            "bot_name": "تولين",
            "developer": "بسام الحوباني",
            "version": "V13.0"
        }
    }
    try:
        cloud = load_json_from_gist("config", default_config)
        for key, val in default_config.items():
            if key not in cloud:
                cloud[key] = val
            elif isinstance(val, dict):
                for sub_key, sub_val in val.items():
                    if sub_key not in cloud[key]:
                        cloud[key][sub_key] = sub_val
                    elif isinstance(sub_val, dict):
                        for asset in ["eurusd", "usdjpy"]:
                            if asset in cloud["strategies"]:
                                for new_key, new_val in sub_val.items():
                                    if new_key not in cloud["strategies"][asset]:
                                        cloud["strategies"][asset][new_key] = new_val
        return cloud
    except:
        return default_config


def load_trades_history(asset_type):
    """تحميل تاريخ الصفقات من Gist أو الملف المحلي"""
    try:
        cloud = load_json_from_gist(f"trades_{asset_type}", None)
        if cloud is not None:
            logger.info(f"✅ تم تحميل {asset_type} من Gist ({len(cloud.get('trades', []))} صفقة)")
            file = get_trades_file(asset_type)
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(cloud, f, indent=2, ensure_ascii=False)
            return cloud
    except Exception as e:
        logger.warning(f"⚠️ فشل تحميل {asset_type} من Gist: {e}")

    file = get_trades_file(asset_type)
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ تم تحميل {asset_type} من الملف المحلي ({len(data.get('trades', []))} صفقة)")
                return data
        except Exception as e:
            logger.error(f"خطأ في قراءة ملف الصفقات: {e}")

    return {"trades": [], "last_cleanup": datetime.now().isoformat()}


def save_trades_history(asset_type, history):
    """حفظ تاريخ الصفقات في الملف المحلي و Gist"""
    trade_count = len(history.get("trades", []))
    logger.info(f"💾 حفظ {asset_type}: {trade_count} صفقة")
    
    file = get_trades_file(asset_type)
    backup_file = f"{file}.backup"
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 تم حفظ نسخة احتياطية: {backup_file}")
    except Exception as e:
        logger.warning(f"⚠️ فشل حفظ النسخة الاحتياطية: {e}")
    
    gist_success = False
    try:
        gist_success = save_json_to_gist(f"trades_{asset_type}", history)
        if gist_success:
            logger.info(f"✅ تم حفظ {asset_type} في Gist ({trade_count} صفقة)")
    except Exception as e:
        logger.error(f"❌ خطأ في حفظ {asset_type} في Gist: {e}")

    local_success = False
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ تم حفظ {asset_type} في الملف المحلي: {file}")
        local_success = True
    except Exception as e:
        logger.error(f"❌ خطأ في حفظ {asset_type} في الملف المحلي: {e}")

    if local_success:
        try:
            if os.path.exists(file) and os.path.getsize(file) > 0:
                with open(file, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                    verify_count = len(verify_data.get("trades", []))
                    
                    if verify_count == trade_count:
                        logger.info(f"✅ تم التحقق من حفظ {asset_type}: {verify_count} صفقة")
                    else:
                        logger.error(f"❌ فشل التحقق: توقعت {trade_count} صفقة، وجدت {verify_count}")
                        try:
                            with open(file, 'w', encoding='utf-8') as f2:
                                json.dump(history, f2, indent=2, ensure_ascii=False)
                            logger.info(f"✅ تم الحفظ مرة أخرى لـ {asset_type}")
                        except Exception as e2:
                            logger.error(f"❌ فشل الحفظ مرة أخرى: {e2}")
            else:
                logger.error(f"❌ الملف {file} غير موجود أو فارغ بعد الحفظ!")
                try:
                    with open(file, 'w', encoding='utf-8') as f2:
                        json.dump(history, f2, indent=2, ensure_ascii=False)
                    logger.info(f"✅ تم الحفظ مرة أخرى لـ {asset_type}")
                except Exception as e2:
                    logger.error(f"❌ فشل الحفظ مرة أخرى: {e2}")
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من الحفظ: {e}")

    if not gist_success:
        logger.warning(f"⚠️ سيتم إعادة محاولة حفظ {asset_type} في Gist بعد 10 ثوانٍ")
        threading.Timer(10.0, lambda: save_json_to_gist(f"trades_{asset_type}", history)).start()
    
    return local_success or gist_success


def get_current_open_trade(asset_type):
    """
    قراءة الصفقة المفتوحة من ملف current_position_*.json
    ✅ معالجة محسنة للأخطاء
    """
    pos_file = get_position_file(asset_type)
    if not os.path.exists(pos_file):
        return None
    try:
        with open(pos_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                os.remove(pos_file)
                return None
            trade = json.loads(content)
            if trade and isinstance(trade, dict) and trade.get("status") == "open":
                return trade
            else:
                try:
                    os.remove(pos_file)
                except:
                    pass
                return None
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        logger.warning(f"⚠️ [get_current_open_trade] خطأ في قراءة {pos_file}: {e}")
        try:
            os.remove(pos_file)
        except:
            pass
        return None


def cleanup_old_trades(asset_type):
    """تنظيف الصفقات القديمة (أكثر من 7 أيام)"""
    def _cleanup():
        history = load_trades_history(asset_type)
        seven_days_ago = datetime.now() - timedelta(days=7)
        history["trades"] = [t for t in history["trades"] 
            if t.get("status") == "open" or datetime.fromisoformat(t["timestamp"]) > seven_days_ago]
        history["last_cleanup"] = datetime.now().isoformat()
        save_trades_history(asset_type, history)
        return len(history["trades"])
    return safe_file_operation(asset_type, _cleanup)


def calculate_statistics(asset_type):
    """حساب إحصائيات الأداء"""
    cleanup_old_trades(asset_type)
    history = load_trades_history(asset_type)
    trades = history.get("trades", [])
    
    logger.info(f"📊 حساب إحصائيات {asset_type}: {len(trades)} صفقة إجمالاً")
    
    closed = []
    open_trades = []
    
    for t in trades:
        if t.get("status") == "closed":
            closed.append(t)
            logger.info(f"   • صفقة مغلقة: {t.get('trade_id')} - ربح: {t.get('profit_dollars', 0):.2f}$ - سبب: {t.get('exit_reason')}")
        else:
            open_trades.append(t)
    
    logger.info(f"📊 {asset_type}: {len(closed)} مغلقة, {len(open_trades)} مفتوحة")

    if not closed:
        return {
            "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
            "total_profit": 0, "win_rate": 0, "current_balance": 100.0,
            "tp_count": 0, "sl_count": 0, "manual_count": 0, "strong_close": 0
        }

    winning = [t for t in closed if t.get("profit_dollars", 0) > 0]
    losing = [t for t in closed if t.get("profit_dollars", 0) < 0]
    total_profit = sum(t.get("profit_dollars", 0) for t in closed)
    win_rate = (len(winning) / len(closed) * 100) if closed else 0

    return {
        "total_trades": len(closed),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "total_profit": total_profit,
        "win_rate": win_rate,
        "current_balance": 100.0 + total_profit,
        "tp_count": len([t for t in closed if t.get("exit_reason") == "Hit Take Profit"]),
        "sl_count": len([t for t in closed if t.get("exit_reason") == "Hit Stop Loss"]),
        "manual_count": len([t for t in closed if t.get("manual_close") == True]),
        "strong_close": len([t for t in closed if t.get("exit_reason") == "تحذير قوي - إغلاق تلقائي"])
    }


def get_last_closed_trade(asset_type=None):
    """الحصول على آخر صفقة مغلقة"""
    all_trades = []
    for asset in ["eurusd", "usdjpy"]:
        history = load_trades_history(asset)
        for trade in history.get("trades", []):
            if trade.get("status") == "closed":
                trade["asset"] = asset
                all_trades.append(trade)
    all_trades.sort(key=lambda x: x.get("exit_timestamp", x.get("timestamp", "")), reverse=True)
    if asset_type:
        all_trades = [t for t in all_trades if t.get("asset") == asset_type]
    return all_trades[0] if all_trades else None


def add_trade_to_history(asset_type, trade, holistic_entry_analysis=None) -> bool:
    """
    ✅ إضافة صفقة جديدة وحفظها في current_position_*.json فوراً.
    تعيد True إذا نجحت، False إذا فشلت.
    الأولوية القصوى: حفظ الملف المحلي، ثم Supabase (اختياري).
    """
    logger.info(f"🔴 [add_trade_to_history] استدعاء لـ {asset_type} – trade_id: {trade.get('trade_id')}")

    if 'trade_id' not in trade or not trade['trade_id']:
        trade['trade_id'] = f"{asset_type}_{int(datetime.now().timestamp())}"
        logger.info(f"🆔 [add_trade_to_history] تم إنشاء trade_id: {trade['trade_id']}")
    
    if 'timestamp' not in trade or not trade['timestamp']:
        trade['timestamp'] = datetime.now().isoformat()
        logger.info(f"⏱️ [add_trade_to_history] تم تعيين timestamp: {trade['timestamp']}")
    
    trade['status'] = 'open'
    trade.setdefault('warnings_sent', [])
    trade.setdefault('warnings_log', [])
    trade.setdefault('recommendations_sent', [])
    if holistic_entry_analysis:
        trade['holistic_entry_analysis'] = holistic_entry_analysis
        logger.info(f"📊 [add_trade_to_history] تم حفظ التحليل الشامل")

    logger.info(f"📋 [add_trade_to_history] بيانات الصفقة: {trade.get('type')} @ {trade.get('entry_price')}, SL: {trade.get('sl')}, TP: {trade.get('tp')}")

    # ================================================================
    # 1. حفظ في current_position_*.json (الأولوية القصوى)
    # ================================================================
    pos_file = get_position_file(asset_type)
    try:
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(trade, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ [add_trade_to_history] تم حفظ الصفقة في {pos_file}")
    except Exception as e:
        logger.error(f"❌ [add_trade_to_history] فشل حفظ {pos_file}: {e}")
        return False

    # ================================================================
    # 2. حفظ في trades_history (نسخة احتياطية)
    # ================================================================
    try:
        history = load_trades_history(asset_type)
        existing = None
        for t in history.get('trades', []):
            if t.get('trade_id') == trade['trade_id']:
                existing = t
                break
        if existing:
            existing.update(trade)
            logger.info(f"🔄 [add_trade_to_history] تحديث صفقة موجودة في trades_history")
        else:
            history['trades'].append(trade)
            logger.info(f"➕ [add_trade_to_history] إضافة صفقة جديدة إلى trades_history")
        save_trades_history(asset_type, history)
        logger.info(f"💾 [add_trade_to_history] تم تحديث trades_history لـ {asset_type}")
    except Exception as e:
        logger.error(f"⚠️ [add_trade_to_history] فشل تحديث trades_history: {e}")

    # ================================================================
    # 3. محاولة حفظ في Supabase (اختياري، لا يؤثر على فتح الصفقة)
    # ================================================================
    try:
        trade_full_data = {
            'trade_id': trade['trade_id'],
            'asset_type': asset_type,
            'trade_type': trade.get('type', 'BUY'),
            'entry_price': trade.get('entry_price', 0),
            'entry_time': trade.get('timestamp', datetime.now().isoformat()),
            'sl_price': trade.get('sl', 0),
            'tp_price': trade.get('tp', 0),
            'rr': trade.get('rr', 1.0),
            'confidence': trade.get('confidence', 70),
        }
        entry_indicators = trade.get('entry_indicators', {})
        if entry_indicators:
            trade_full_data['entry_rsi'] = entry_indicators.get('rsi', 50)
            trade_full_data['entry_adx'] = entry_indicators.get('adx', 15)
            trade_full_data['entry_macd'] = entry_indicators.get('macd', 0)
            trade_full_data['entry_trend'] = entry_indicators.get('trend', 'محايد')
        
        if holistic_entry_analysis:
            trade_full_data['full_entry_analysis'] = holistic_entry_analysis
        
        save_trade_to_learning(trade_full_data)
        logger.info(f"☁️ [add_trade_to_history] تم محاولة حفظ في Supabase (اختياري)")
    except Exception as e:
        logger.error(f"⚠️ [add_trade_to_history] فشل حفظ Supabase (غير مؤثر): {e}")

    logger.info(f"✅ [add_trade_to_history] اكتمل حفظ الصفقة {trade['trade_id']} بنجاح")
    return True


# ====================================================================================
# 🧹 تنظيف الصفقات العالقة عند بدء التشغيل
# ====================================================================================

def cleanup_stuck_trades_on_startup():
    """تنظيف الصفقات العالقة عند بدء التشغيل"""
    
    logger.info("🧹 بدء تنظيف الصفقات العالقة...")
    cleaned = 0
    added = 0
    
    for asset_type in ["eurusd", "usdjpy"]:
        pos_file = get_position_file(asset_type)
        
        if not os.path.exists(pos_file):
            continue
        
        try:
            with open(pos_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    os.remove(pos_file)
                    cleaned += 1
                    continue
                trade = json.loads(content)
            
            trade_id = trade.get("trade_id", "")
            
            history = load_trades_history(asset_type)
            found_in_history = False
            is_closed_in_history = False
            
            for t in history.get("trades", []):
                if t.get("trade_id") == trade_id:
                    found_in_history = True
                    if t.get("status") == "closed":
                        is_closed_in_history = True
                    break
            
            if is_closed_in_history:
                os.remove(pos_file)
                cleaned += 1
                logger.info(f"🗑️ تم حذف صفقة مغلقة: {pos_file}")
            elif not found_in_history:
                logger.info(f"ℹ️ صفقة جديدة غير مسجلة: {trade_id} - الاحتفاظ بها وإضافتها للسجل")
                trade["status"] = "open"
                trade["timestamp"] = trade.get("timestamp", datetime.now().isoformat())
                if "warnings_sent" not in trade:
                    trade["warnings_sent"] = []
                if "recommendations_sent" not in trade:
                    trade["recommendations_sent"] = []
                history["trades"].append(trade)
                save_trades_history(asset_type, history)
                added += 1
                logger.info(f"✅ تم إضافة الصفقة الجديدة إلى السجل: {trade_id}")
            else:
                logger.info(f"✅ صفقة مفتوحة موجودة: {trade_id}")
            
        except (json.JSONDecodeError, Exception) as e:
            try:
                os.remove(pos_file)
                cleaned += 1
                logger.info(f"🗑️ تم حذف ملف تالف: {pos_file}")
            except:
                pass
    
    with MONITOR_TRIGGER_LOCK:
        MONITOR_TRIGGER["oil"] = None
        MONITOR_TRIGGER["silver"] = None
    
    with LAST_SIGNAL_LOCK:
        last_signal_states["oil"] = {"signal": "WAIT", "time": 0}
        last_signal_states["silver"] = {"signal": "WAIT", "time": 0}
    
    if cleaned > 0 or added > 0:
        logger.info(f"✅ تم تنظيف {cleaned} صفقة عالقة وإضافة {added} صفقة جديدة")
    return cleaned, added


# ====================================================================================
# 🔒 دوال إغلاق الصفقات
# ====================================================================================

def close_trade_virtual(asset_type, reason="أمر افتراضي", current_price=None):
    """إغلاق الصفقة مع حفظ التحليل الشامل للفتح والإغلاق في قاعدة التعلم"""
    
    logger.info(f"🔒 بدء إغلاق {asset_type}: {reason}")
    
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        queue_telegram_message(f"❌ لا توجد صفقة {asset_type} مفتوحة.")
        return False

    from api_clients import get_mexc_candles
    from analysis import perform_comprehensive_analysis

    symbol = "USOIL_USDT" if asset_type == "oil" else "SILVER_USDT"
    if current_price is None:
        data = get_mexc_candles(symbol, "Min1", 5)
        current_price = data["closes"][-1] if data and data.get("closes") else open_trade["entry_price"]

    entry_price = open_trade["entry_price"]
    trade_type = open_trade["type"]
    profit_dollars = AccountingSystem.calculate_profit_dollars(entry_price, current_price, trade_type)
    trade_id = open_trade.get("trade_id", "")

    # ── 1. الحصول على التحليل الشامل عند الإغلاق ──
    closing_analysis, _ = perform_comprehensive_analysis(asset_type, False, None)
    
    # ── 2. استخراج بيانات التحليل الشامل عند الإغلاق ──
    if closing_analysis and isinstance(closing_analysis, dict):
        price_now = closing_analysis.get("price", current_price)
        tf_15m = closing_analysis.get("timeframes", {}).get("15m", {}) if isinstance(closing_analysis.get("timeframes"), dict) else {}
        indicators = closing_analysis.get("indicators", {}) if isinstance(closing_analysis.get("indicators"), dict) else {}
        comp_score = closing_analysis.get("comprehensive_score", {}) if isinstance(closing_analysis.get("comprehensive_score"), dict) else {}
        
        close_rsi = tf_15m.get("rsi", 50) if isinstance(tf_15m, dict) else 50
        close_adx = tf_15m.get("adx", 15) if isinstance(tf_15m, dict) else 15
        close_macd = tf_15m.get("macd", 0) if isinstance(tf_15m, dict) else 0
        close_trend = tf_15m.get("trend", "محايد") if isinstance(tf_15m, dict) else "محايد"
        close_vol_ratio = tf_15m.get("volume_ratio", 1.0) if isinstance(tf_15m, dict) else 1.0
        close_vwap = tf_15m.get("vwap", current_price) if isinstance(tf_15m, dict) else current_price
        
        bb = tf_15m.get("bollinger", {}) if isinstance(tf_15m, dict) else {}
        close_bb_upper = bb.get("upper", current_price * 1.02) if isinstance(bb, dict) else current_price * 1.02
        close_bb_lower = bb.get("lower", current_price * 0.98) if isinstance(bb, dict) else current_price * 0.98
        
        sr = indicators.get("support_resistance", {}) if isinstance(indicators, dict) else {}
        close_support = sr.get("s1", current_price * 0.98) if isinstance(sr, dict) else current_price * 0.98
        close_resistance = sr.get("r1", current_price * 1.02) if isinstance(sr, dict) else current_price * 1.02
        
        close_score = comp_score.get("score", 50) if isinstance(comp_score, dict) else 50
        close_grade = comp_score.get("grade", "محايد") if isinstance(comp_score, dict) else "محايد"
    else:
        close_rsi = 50
        close_adx = 15
        close_macd = 0
        close_trend = "محايد"
        close_vol_ratio = 1.0
        close_vwap = current_price
        close_bb_upper = current_price * 1.02
        close_bb_lower = current_price * 0.98
        close_support = current_price * 0.98
        close_resistance = current_price * 1.02
        close_score = 50
        close_grade = "محايد"

    # ── 3. استخراج بيانات التحليل الشامل عند الفتح ──
    holistic_entry = open_trade.get("holistic_entry_analysis", {})
    if holistic_entry and isinstance(holistic_entry, dict):
        entry_tf_15m = holistic_entry.get("timeframes", {}).get("15m", {}) if isinstance(holistic_entry.get("timeframes"), dict) else {}
        entry_indicators_data = holistic_entry.get("indicators", {}) if isinstance(holistic_entry.get("indicators"), dict) else {}
        entry_comp_score = holistic_entry.get("comprehensive_score", {}) if isinstance(holistic_entry.get("comprehensive_score"), dict) else {}
        
        entry_rsi = entry_tf_15m.get("rsi", 50) if isinstance(entry_tf_15m, dict) else 50
        entry_adx = entry_tf_15m.get("adx", 15) if isinstance(entry_tf_15m, dict) else 15
        entry_macd = entry_tf_15m.get("macd", 0) if isinstance(entry_tf_15m, dict) else 0
        entry_trend = entry_tf_15m.get("trend", "محايد") if isinstance(entry_tf_15m, dict) else "محايد"
        entry_vol_ratio = entry_tf_15m.get("volume_ratio", 1.0) if isinstance(entry_tf_15m, dict) else 1.0
        entry_vwap = entry_tf_15m.get("vwap", entry_price) if isinstance(entry_tf_15m, dict) else entry_price
        
        entry_bb = entry_tf_15m.get("bollinger", {}) if isinstance(entry_tf_15m, dict) else {}
        entry_bb_upper = entry_bb.get("upper", entry_price * 1.02) if isinstance(entry_bb, dict) else entry_price * 1.02
        entry_bb_lower = entry_bb.get("lower", entry_price * 0.98) if isinstance(entry_bb, dict) else entry_price * 0.98
        
        entry_sr = entry_indicators_data.get("support_resistance", {}) if isinstance(entry_indicators_data, dict) else {}
        entry_support = entry_sr.get("s1", entry_price * 0.98) if isinstance(entry_sr, dict) else entry_price * 0.98
        entry_resistance = entry_sr.get("r1", entry_price * 1.02) if isinstance(entry_sr, dict) else entry_price * 1.02
        
        entry_score = entry_comp_score.get("score", 50) if isinstance(entry_comp_score, dict) else 50
        entry_grade = entry_comp_score.get("grade", "محايد") if isinstance(entry_comp_score, dict) else "محايد"
    else:
        entry_indicators_old = open_trade.get("entry_indicators", {})
        entry_rsi = entry_indicators_old.get("rsi", 50) if isinstance(entry_indicators_old, dict) else 50
        entry_adx = entry_indicators_old.get("adx", 15) if isinstance(entry_indicators_old, dict) else 15
        entry_macd = entry_indicators_old.get("macd", 0) if isinstance(entry_indicators_old, dict) else 0
        entry_trend = entry_indicators_old.get("trend", "محايد") if isinstance(entry_indicators_old, dict) else "محايد"
        entry_vol_ratio = 1.0
        entry_vwap = entry_price
        entry_bb_upper = entry_price * 1.02
        entry_bb_lower = entry_price * 0.98
        entry_support = entry_price * 0.98
        entry_resistance = entry_price * 1.02
        entry_score = 50
        entry_grade = "محايد"

    # ── 4. تحديث السجل المحلي ──
    history = load_trades_history(asset_type)
    trade_found = False
    for trade in history["trades"]:
        if trade.get("trade_id") == trade_id:
            trade_found = True
            trade["status"] = "closed"
            trade["exit_price"] = current_price
            trade["exit_reason"] = reason
            trade["profit_dollars"] = profit_dollars
            trade["exit_timestamp"] = datetime.now().isoformat()
            trade["manual_close"] = reason in ["أمر يدوي من المستخدم", "أمر يدوي من الزر"]
            break
    
    if not trade_found:
        new_trade = {
            "trade_id": trade_id,
            "type": trade_type,
            "entry_price": entry_price,
            "exit_price": current_price,
            "sl": open_trade.get("sl", 0),
            "tp": open_trade.get("tp", 0),
            "profit_dollars": profit_dollars,
            "status": "closed",
            "exit_reason": reason,
            "timestamp": open_trade.get("timestamp", datetime.now().isoformat()),
            "exit_timestamp": datetime.now().isoformat(),
            "manual_close": True,
            "asset_type": asset_type,
            "entry_indicators": open_trade.get("entry_indicators", {}),
            "warnings_sent": open_trade.get("warnings_sent", []),
            "recommendations_sent": open_trade.get("recommendations_sent", [])
        }
        history["trades"].append(new_trade)

    save_trades_history(asset_type, history)

    # ── 5. حذف ملف الصفقة المفتوحة ──
    pos_file = get_position_file(asset_type)
    if os.path.exists(pos_file):
        try:
            os.remove(pos_file)
            logger.info(f"🗑️ تم حذف ملف الصفقة المفتوحة: {pos_file}")
        except Exception as e:
            logger.error(f"❌ فشل حذف ملف الصفقة: {e}")

    with MONITOR_TRIGGER_LOCK:
        MONITOR_TRIGGER[asset_type] = None
    with LAST_SIGNAL_LOCK:
        last_signal_states[asset_type] = {"signal": "WAIT", "time": 0}
        last_signal_time[asset_type] = 0

    # ── 6. حفظ البيانات في قواعد التعلم ──
    try:
        entry_time = open_trade.get('timestamp', datetime.now().isoformat())
        exit_time = datetime.now().isoformat()
        duration_minutes = 0
        try:
            entry_dt = datetime.fromisoformat(entry_time)
            exit_dt = datetime.now()
            duration_minutes = int((exit_dt - entry_dt).total_seconds() / 60)
        except:
            pass
        
        profit_pct = ((current_price - entry_price) / entry_price * 100) if entry_price != 0 else 0
        sl = open_trade.get('sl', 0)
        tp = open_trade.get('tp', 0)
        rr = 1.0
        if sl and tp and entry_price:
            if trade_type == "BUY":
                risk = entry_price - sl
                reward = tp - entry_price
            else:
                risk = sl - entry_price
                reward = entry_price - tp
            rr = reward / risk if risk != 0 else 1.0
        
        trade_full_data = {
            'trade_id': trade_id,
            'asset_type': asset_type,
            'trade_type': trade_type,
            'entry_price': entry_price,
            'exit_price': current_price,
            'profit_dollars': profit_dollars,
            'profit_pct': profit_pct,
            'exit_reason': reason,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'duration_minutes': duration_minutes,
            'entry_rsi': entry_rsi,
            'entry_adx': entry_adx,
            'entry_macd': entry_macd,
            'entry_trend': entry_trend,
            'entry_volume_ratio': entry_vol_ratio,
            'entry_vwap': entry_vwap,
            'entry_bb_upper': entry_bb_upper,
            'entry_bb_lower': entry_bb_lower,
            'entry_support': entry_support,
            'entry_resistance': entry_resistance,
            'entry_comprehensive_score': entry_score,
            'entry_comprehensive_grade': entry_grade,
            'close_rsi': close_rsi,
            'close_adx': close_adx,
            'close_macd': close_macd,
            'close_trend': close_trend,
            'close_volume_ratio': close_vol_ratio,
            'close_vwap': close_vwap,
            'close_bb_upper': close_bb_upper,
            'close_bb_lower': close_bb_lower,
            'close_support': close_support,
            'close_resistance': close_resistance,
            'close_comprehensive_score': close_score,
            'close_comprehensive_grade': close_grade,
            'sl_price': open_trade.get('sl', 0),
            'tp_price': open_trade.get('tp', 0),
            'rr': rr,
            'confidence': open_trade.get('confidence', 70)
        }
        
        logger.info(f"📤 [close_trade_virtual] محاولة حفظ الصفقة المغلقة {trade_id} في Supabase...")
        save_trade_to_learning(trade_full_data)
        
        # تشغيل اكتشاف الأنماط بعد الإغلاق
        try:
            from learning import discover_patterns_from_trades
            threading.Timer(10.0, lambda: discover_patterns_from_trades(asset_type)).start()
        except:
            pass
        
    except Exception as e:
        logger.error(f"❌ فشل حفظ الصفقة في قواعد التعلم: {e}")

    # ── 7. إرسال رسالة الإغلاق للمستخدم ──
    asset_label = "النفط" if asset_type == "oil" else "الفضة"
    msg = f"✅ **تم إغلاق صفقة {asset_label}**\n"
    msg += f"📊 سعر الدخول: ${fmt_price(entry_price, asset_type)}\n"
    msg += f"📊 سعر الخروج: ${fmt_price(current_price, asset_type)}\n"
    msg += f"📊 النتيجة: {AccountingSystem.format_profit(profit_dollars)}\n"
    msg += f"📌 سبب الإغلاق: {reason}"

    queue_telegram_message(msg)
    logger.info(f"✅ تم إغلاق صفقة {asset_type} بنجاح")
    return True


def close_trade_manually(asset_type, reason="أمر يدوي"):
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        queue_telegram_message(f"❌ لا توجد صفقة {asset_type} مفتوحة للإغلاق.")
        return False
    return close_trade_virtual(asset_type, reason)


# ====================================================================================
# ⚠️ نظام التحذيرات الذكي
# ====================================================================================

WARNING_LEVELS = {
    "distance_sl": {
        1: {"threshold_pct": 0.30, "label": "تحذير", "emoji": "⚠️"},
        2: {"threshold_pct": 0.60, "label": "تنبيه", "emoji": "🔴"},
        3: {"threshold_pct": 0.90, "label": "تحذير أخير", "emoji": "🚨"}
    },
    "adx_weak": {
        1: {"threshold": 20, "label": "ADX ضعيف", "emoji": "⚠️"},
        2: {"threshold": 15, "label": "ADX ضعيف جداً", "emoji": "🔴"}
    },
    "volume_low": {
        1: {"threshold": 0.5, "label": "حجم منخفض", "emoji": "⚠️"}
    },
    "sentiment_negative": {
        1: {"threshold": 25, "label": "معنويات سلبية", "emoji": "⚠️"}
    }
}


def should_send_warning(open_trade, warning_type, level, current_value=None):
    """التحقق من إرسال تحذير مسبقاً لتجنب التكرار"""
    warnings_sent = open_trade.get("warnings_sent", [])
    
    for w in warnings_sent:
        if w.get("type") == warning_type and w.get("level") == level:
            return False
    
    return True


def should_send_recommendation(open_trade, recommendation_type):
    """التحقق من إرسال توصية مسبقاً لتجنب التكرار"""
    recommendations_sent = open_trade.get("recommendations_sent", [])
    
    if recommendation_type in recommendations_sent:
        return False
    
    return True


def record_warning(open_trade, warning_type, level, current_price, message):
    """تسجيل تحذير في سجل الصفقة"""
    if "warnings_sent" not in open_trade:
        open_trade["warnings_sent"] = []

    open_trade["warnings_sent"].append({
        "type": warning_type,
        "level": level,
        "sent_at": datetime.now().isoformat(),
        "price_at": current_price,
        "message": message[:100]
    })

    asset_type = open_trade.get("asset_type", "eurusd")
    pos_file = get_position_file(asset_type)
    try:
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(open_trade, f, indent=2, ensure_ascii=False)
    except:
        pass


def record_recommendation(open_trade, recommendation_type, message):
    """تسجيل توصية في سجل الصفقة"""
    if "recommendations_sent" not in open_trade:
        open_trade["recommendations_sent"] = []

    open_trade["recommendations_sent"].append(recommendation_type)

    asset_type = open_trade.get("asset_type", "eurusd")
    pos_file = get_position_file(asset_type)
    try:
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(open_trade, f, indent=2, ensure_ascii=False)
    except:
        pass


def check_sl_tp_hit(asset_type, current_price, open_trade):
    """التحقق من ضرب SL أو TP"""
    if not open_trade:
        return False

    trade_type = open_trade.get("type", "BUY")
    sl = open_trade.get("sl", 0)
    tp = open_trade.get("tp", 0)

    if trade_type == "BUY":
        if current_price <= sl:
            close_trade_virtual(asset_type, "Hit Stop Loss", current_price)
            return True
        if current_price >= tp:
            close_trade_virtual(asset_type, "Hit Take Profit", current_price)
            return True
    else:
        if current_price >= sl:
            close_trade_virtual(asset_type, "Hit Stop Loss", current_price)
            return True
        if current_price <= tp:
            close_trade_virtual(asset_type, "Hit Take Profit", current_price)
            return True

    return False


def check_supertrend_reversal(asset_type, current_price, current_trend, open_trade):
    """التحقق من انعكاس SuperTrend (يستخدم في المراقبة فقط)"""
    if not open_trade:
        return False

    trade_type = open_trade.get("type", "BUY")

    if trade_type == "BUY" and current_trend == -1:
        close_trade_virtual(asset_type, "تغيير اتجاه SuperTrend - إغلاق تلقائي", current_price)
        return True
    elif trade_type == "SELL" and current_trend == 1:
        close_trade_virtual(asset_type, "تغيير اتجاه SuperTrend - إغلاق تلقائي", current_price)
        return True

    return False


def check_distance_warnings(asset_type, current_price, open_trade):
    """التحقق من المسافة إلى SL وإرسال تحذيرات"""
    if not open_trade:
        return

    entry_price = open_trade.get("entry_price", current_price)
    sl = open_trade.get("sl", entry_price)
    trade_type = open_trade.get("type", "BUY")

    total_distance = abs(entry_price - sl)
    if total_distance == 0:
        return

    current_distance = abs(current_price - sl)
    distance_pct = current_distance / total_distance

    asset_label = "النفط" if asset_type == "oil" else "الفضة"

    for level, config in WARNING_LEVELS["distance_sl"].items():
        if distance_pct <= config["threshold_pct"]:
            if should_send_warning(open_trade, "distance_sl", level, current_price):
                msg = f"{config['emoji']} <b>{config['label']}:</b> صفقة {asset_label} على وشك ضرب SL!\n"
                msg += f"💰 السعر: ${fmt_price(current_price, asset_type)} | SL: ${fmt_price(sl, asset_type)}\n"
                msg += f"📉 المسافة المتبقية: {distance_pct*100:.1f}%\n"

                if level == 3:
                    rec_type = "close_immediate"
                    if should_send_recommendation(open_trade, rec_type):
                        msg += "\n💡 <b>توصية تولين:</b> أنصح بالإغلاق فوراً"
                        record_recommendation(open_trade, rec_type, "إغلاق فوري")
                elif level == 2:
                    rec_type = "close_watch"
                    if should_send_recommendation(open_trade, rec_type):
                        msg += "\n💡 <b>توصية تولين:</b> راقب عن كثب - جهز للإغلاق"
                        record_recommendation(open_trade, rec_type, "مراقبة وإغلاق")
                else:
                    rec_type = "caution"
                    if should_send_recommendation(open_trade, rec_type):
                        msg += "\n💡 <b>توصية تولين:</b> تباعد عن SL - كن حذراً"
                        record_recommendation(open_trade, rec_type, "حذر")

                queue_telegram_message(msg)
                record_warning(open_trade, "distance_sl", level, current_price, msg)


def check_adx_warnings(asset_type, adx, open_trade):
    """التحقق من ضعف ADX وإرسال تحذيرات"""
    if not open_trade:
        return

    for level, config in WARNING_LEVELS["adx_weak"].items():
        if adx < config["threshold"]:
            if should_send_warning(open_trade, "adx_weak", level):
                asset_label = "النفط" if asset_type == "oil" else "الفضة"
                msg = f"{config['emoji']} <b>{config['label']}:</b> صفقة {asset_label}\n"
                msg += f"📊 ADX: {adx:.1f} - لا يوجد زخم تأكيدي\n"
                
                rec_type = "adx_warning"
                if should_send_recommendation(open_trade, rec_type):
                    msg += "\n💡 <b>توصية تولين:</b> الاتجاه ضعيف - فكر في الإغلاق"
                    record_recommendation(open_trade, rec_type, "ADX ضعيف")
                
                queue_telegram_message(msg)
                record_warning(open_trade, "adx_weak", level, None, msg)


def check_volume_warnings(asset_type, vol_ratio, open_trade):
    """التحقق من انخفاض الحجم وإرسال تحذيرات"""
    if not open_trade:
        return

    for level, config in WARNING_LEVELS["volume_low"].items():
        if vol_ratio < config["threshold"]:
            if should_send_warning(open_trade, "volume_low", level):
                asset_label = "النفط" if asset_type == "oil" else "الفضة"
                msg = f"{config['emoji']} <b>{config['label']}:</b> صفقة {asset_label}\n"
                msg += f"📊 نسبة الحجم: {vol_ratio:.2f}x - حركة ضعيفة\n"
                
                rec_type = "volume_warning"
                if should_send_recommendation(open_trade, rec_type):
                    msg += "\n💡 <b>توصية تولين:</b> الحجم لا يؤكد الاتجاه"
                    record_recommendation(open_trade, rec_type, "حجم منخفض")
                
                queue_telegram_message(msg)
                record_warning(open_trade, "volume_low", level, None, msg)
