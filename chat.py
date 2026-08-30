# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 CHAT.PY - نظام المحادثة الذكي (SmartConversationManager, HybridOrchestrator, handle_message)
📌 يحتوي على نظام المحادثة بالكامل، المدير الذكي، والوسيط الهجين
═══════════════════════════════════════════════════════════════════════════════════
"""

import os
import re
import json
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# ====================================================================================
# 📦 استيراد المتغيرات العامة من constants
# ====================================================================================

from constants import (
    logger, GROQ_API_KEY, GEMINI_API_KEY, TELEGRAM_TOKEN, CHAT_ID,
    ANALYSIS_CACHE, ANALYSIS_CACHE_TTL, CONVERSATION_CONTEXTS,
    CONVERSATION_CONTEXT_LIMIT, last_signal_states, last_signal_time,
    LAST_SIGNAL_LOCK, MONITOR_TRIGGER, MONITOR_TRIGGER_LOCK,
    PROMETHEUS_AVAILABLE, PROMETHEUS,
    TCN_AVAILABLE, TCN,
    CHRONOS_AVAILABLE, CHRONOS,
    ORACLE_AVAILABLE, ORACLE,
    MEMORY_AVAILABLE, MEMORY,
    HYBRID_ORCHESTRATOR
)

# ====================================================================================
# 📦 استيراد الدوال المساعدة
# ====================================================================================

from utils import queue_telegram_message, fmt_price, escape_html
from api_clients import get_mexc_candles, get_fear_greed_index
from analysis import perform_comprehensive_analysis, calculate_comprehensive_score, analyze_open_trade
from position_manager import (
    get_current_open_trade, load_trades_history, save_trades_history,
    get_last_closed_trade, close_trade_virtual, close_trade_manually,
    AccountingSystem, add_trade_to_history, calculate_statistics
)
from trading_logic import analyze_and_send

# ====================================================================================
# 🌐 استيراد Gemini (اختياري)
# ====================================================================================

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


# ====================================================================================
# 🔍 دوال بناء السياق والتحليل
# ====================================================================================

def build_chat_context(text: str, chat_id: str) -> Dict:
    """يجمع السياق من جميع المحركات المتاحة (بما فيها TCN) لاستخدامه في المحادثة الذكية."""
    context = {
        "user_message": text,
        "timestamp": datetime.now().isoformat(),
        "chat_id": chat_id,
        "intent": None,
        "intent_confidence": 0.5,
        "sentiment": None,
        "entities": [],
        "is_question": False,
        "is_command": False,
        "signal_intent": None,
        "risk_level": "moderate",
        "chat_history": [],
        "open_trades": {},
        "recent_closed_trades": [],
        "market_snapshot": {},
        "prometheus_emotion": "neutral",
        "prometheus_confidence": 0.5,
        "prometheus_energy": 0.5,
        "prometheus_memories": [],
        "prometheus_lessons": [],
        "discovered_patterns": [],
        "recent_lessons": [],
        "recent_warnings": [],
        "risk_status": None,
        "user_profile": {},
        "persona": {},
        "persona_mood": "neutral",
        "persona_emotion": "neutral",
        "market_context": {},
        "recent_events": [],
        "patterns": [],
        "predictions": {},
        "narrative": {},
        "chronos": {},
        "oracle": {},
        "regime_oil": None,
        "regime_silver": None,
        "conversation_state": {},
        "last_trade": None,
        "news_analysis": None
    }

    # 1. Intent Classifier (إذا كان متاحاً)
    try:
        from intent import IntentClassifier
        INTENT_CLASSIFIER = IntentClassifier()
        if hasattr(INTENT_CLASSIFIER, 'classify_with_confidence'):
            intent, confidence = INTENT_CLASSIFIER.classify_with_confidence(text)
            context["intent"] = intent
            context["intent_confidence"] = confidence
        elif hasattr(INTENT_CLASSIFIER, 'classify'):
            context["intent"] = INTENT_CLASSIFIER.classify(text)
            context["intent_confidence"] = 0.8
        logger.info(f"🎯 النية: {context['intent']} (ثقة: {context['intent_confidence']:.0%})")
    except ImportError:
        logger.warning("⚠️ Intent Classifier غير متوفر")
    except Exception as e:
        logger.warning(f"⚠️ Intent فشل: {e}")
        context["intent"] = "general"

    # 2. Language Understanding
    try:
        from language_understanding import LanguageUnderstanding
        LANGUAGE_UNDERSTANDING = LanguageUnderstanding()
        if hasattr(LANGUAGE_UNDERSTANDING, 'get_understanding_summary'):
            lang_result = LANGUAGE_UNDERSTANDING.get_understanding_summary(text)
            context["sentiment"] = lang_result.get("emotion", "neutral")
            context["entities"] = lang_result.get("entities", [])
            context["is_question"] = lang_result.get("is_question", False)
            context["is_command"] = lang_result.get("is_command", False)
            context["signal_intent"] = lang_result.get("signal_intent", None)
            context["risk_level"] = lang_result.get("risk_level", "moderate")
        elif hasattr(LANGUAGE_UNDERSTANDING, 'analyze'):
            lang_result = LANGUAGE_UNDERSTANDING.analyze(text)
            context["sentiment"] = lang_result.get("sentiment", "neutral")
            context["entities"] = lang_result.get("entities", [])
        logger.info(f"🗣️ المشاعر: {context['sentiment']}")
    except ImportError:
        logger.warning("⚠️ Language Understanding غير متوفر")
    except Exception as e:
        logger.warning(f"⚠️ Language فشل: {e}")
        context["sentiment"] = "neutral"

    # 3. Persona
    try:
        from persona import HOBANYPersona
        PERSONA = HOBANYPersona()
        if hasattr(PERSONA, 'analyze_user_emotion'):
            context["persona_emotion"] = PERSONA.analyze_user_emotion(text)
        if hasattr(PERSONA, 'get_persona_description'):
            context["persona"] = PERSONA.get_persona_description()
        if hasattr(PERSONA, 'get_current_mood'):
            context["persona_mood"] = PERSONA.get_current_mood()
        elif hasattr(PERSONA, 'get_mood'):
            context["persona_mood"] = PERSONA.get_mood()
        logger.info(f"👤 شخصية تولين: {context['persona_mood']}")
    except ImportError:
        logger.warning("⚠️ Persona غير متوفر")
    except Exception as e:
        logger.warning(f"⚠️ Persona فشل: {e}")

    # 4. Memory (من constants)
    if MEMORY_AVAILABLE and MEMORY:
        try:
            if hasattr(MEMORY, 'get_recent'):
                context["chat_history"] = MEMORY.get_recent(chat_id, limit=20)
            elif hasattr(MEMORY, 'get_conversation'):
                context["chat_history"] = MEMORY.get_conversation(chat_id, limit=20)
            if hasattr(MEMORY, 'get_profile'):
                context["user_profile"] = MEMORY.get_profile(chat_id)
            logger.info(f"💾 تم استرجاع {len(context['chat_history'])} رسالة")
        except Exception as e:
            logger.warning(f"⚠️ Memory فشل: {e}")
    else:
        logger.warning("⚠️ MEMORY غير متوفر أو غير مهيأ")

    # 5. Prometheus (من constants)
    if PROMETHEUS_AVAILABLE and PROMETHEUS:
        try:
            if hasattr(PROMETHEUS, 'get_emotion'):
                emotion_data = PROMETHEUS.get_emotion()
                context["prometheus_emotion"] = emotion_data.get('dominant', 'neutral')
                context["prometheus_confidence"] = emotion_data.get('confidence', 0.5)
                context["prometheus_energy"] = emotion_data.get('energy', 0.5)
            elif hasattr(PROMETHEUS, 'emotion'):
                if hasattr(PROMETHEUS.emotion, 'dominant'):
                    context["prometheus_emotion"] = PROMETHEUS.emotion.dominant()
                context["prometheus_confidence"] = getattr(PROMETHEUS.emotion, 'confidence', 0.5)
                context["prometheus_energy"] = getattr(PROMETHEUS.emotion, 'energy', 0.5)

            if hasattr(PROMETHEUS, 'get_recent_memories'):
                context["prometheus_memories"] = PROMETHEUS.get_recent_memories(10)
            if hasattr(PROMETHEUS, 'get_lessons_learned'):
                context["prometheus_lessons"] = PROMETHEUS.get_lessons_learned()
            logger.info(f"💙 مشاعر تولين: {context['prometheus_emotion']}")
        except Exception as e:
            logger.warning(f"⚠️ Prometheus فشل: {e}")
    else:
        logger.warning("⚠️ PROMETHEUS غير متوفر أو غير مهيأ")

    # 6. الصفقات المفتوحة
    for asset in ["eurusd", "usdjpy"]:
        try:
            trade = get_current_open_trade(asset)
            if trade:
                context["open_trades"][asset] = trade
        except Exception as e:
            logger.warning(f"⚠️ فشل جلب صفقة {asset}: {e}")

    # 7. الصفقات المغلقة الأخيرة
    try:
        for asset in ["eurusd", "usdjpy"]:
            history = load_trades_history(asset)
            trades = history.get('trades', [])
            closed = [t for t in trades if t.get('status') == 'closed']
            if closed:
                context["recent_closed_trades"].extend(closed[-5:])
    except Exception as e:
        logger.warning(f"⚠️ فشل جلب التاريخ: {e}")

    # 8. آخر صفقة مغلقة
    try:
        last_trade = get_last_closed_trade()
        if last_trade:
            context["last_trade"] = {
                "asset": last_trade.get('asset', 'unknown'),
                "type": last_trade.get('type', 'UNKNOWN'),
                "entry": last_trade.get('entry_price', 0),
                "exit": last_trade.get('exit_price', 0),
                "profit": last_trade.get('profit_dollars', 0),
                "exit_reason": last_trade.get('exit_reason', 'غير معروف'),
                "timestamp": last_trade.get('timestamp', '')
            }
    except Exception as e:
        logger.warning(f"⚠️ فشل جلب آخر صفقة: {e}")

    # 9. Market Snapshot
    try:
        for asset in ["eurusd", "usdjpy"]:
            try:
                analysis = None
                cache_key = f"{asset}_{int(time.time() // 30)}"
                if cache_key in ANALYSIS_CACHE:
                    analysis = ANALYSIS_CACHE[cache_key].get('analysis')
                else:
                    analysis, _ = perform_comprehensive_analysis(asset, False, None)
                    if analysis:
                        from analysis import set_cached_analysis
                        set_cached_analysis(asset, analysis)
                
                if analysis:
                    price = analysis.get("price", 0)
                    if price > 0:
                        context["market_snapshot"][asset] = {
                            "price": price,
                            "signal": analysis.get("signal", "WAIT"),
                            "trend": analysis.get("indicators", {}).get("trend", {}).get("current_trend", "neutral"),
                            "rsi": analysis.get("indicators", {}).get("momentum", {}).get("rsi", 0),
                            "adx": analysis.get("indicators", {}).get("trend", {}).get("adx", 0),
                            "macd": analysis.get("indicators", {}).get("momentum", {}).get("macd", 0),
                            "atr": analysis.get("timeframes", {}).get("15m", {}).get("atr", 0),
                            "vwap": analysis.get("timeframes", {}).get("15m", {}).get("vwap", 0),
                            "fear_greed": analysis.get("fear_greed", 50),
                            "score": analysis.get("comprehensive_score", {}).get("score", 50),
                            "grade": analysis.get("comprehensive_score", {}).get("grade", "محايد")
                        }
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب بيانات {asset}: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Market Snapshot فشل: {e}")

    # 10. أنماط التعلم والدروس
    try:
        from pattern_discovery import PatternDiscovery
        PATTERN_DISCOVERY = PatternDiscovery()
        if hasattr(PATTERN_DISCOVERY, 'get_best_patterns'):
            context["discovered_patterns"] = PATTERN_DISCOVERY.get_best_patterns(3)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ Pattern Discovery فشل: {e}")

    # 11. سجل التحذيرات الأخيرة
    try:
        context["recent_warnings"] = get_recent_warnings(5)
    except Exception as e:
        logger.warning(f"⚠️ Warnings فشل: {e}")

    # 12. Context Memory
    try:
        from context_memory import ContextMemory
        CONTEXT_MEMORY = ContextMemory()
        if hasattr(CONTEXT_MEMORY, 'get_market_context'):
            context["market_context"] = CONTEXT_MEMORY.get_market_context()
        elif hasattr(CONTEXT_MEMORY, 'get_context'):
            context["market_context"] = CONTEXT_MEMORY.get_context()
        if hasattr(CONTEXT_MEMORY, 'get_recent_events'):
            context["recent_events"] = CONTEXT_MEMORY.get_recent_events(10)
        if hasattr(CONTEXT_MEMORY, 'get_current_regime'):
            for asset in ["eurusd", "usdjpy"]:
                regime = CONTEXT_MEMORY.get_current_regime(asset)
                if regime:
                    context[f"regime_{asset}"] = regime
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ Context Memory فشل: {e}")

    # 13. Risk Master
    try:
        from risk_master import RiskMaster
        RISK_MASTER = RiskMaster()
        if hasattr(RISK_MASTER, 'get_current_status'):
            context["risk_status"] = RISK_MASTER.get_current_status()
        elif hasattr(RISK_MASTER, 'get_status'):
            context["risk_status"] = RISK_MASTER.get_status()
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ Risk Master فشل: {e}")

    # 14. Chronos (من constants)
    if CHRONOS_AVAILABLE and CHRONOS:
        try:
            if hasattr(CHRONOS, 'get_temporal_context'):
                context["chronos"] = CHRONOS.get_temporal_context()
        except Exception as e:
            logger.warning(f"⚠️ Chronos فشل: {e}")

    # 15. Oracle (من constants)
    if ORACLE_AVAILABLE and ORACLE:
        try:
            if hasattr(ORACLE, 'get_predictions'):
                context["oracle"] = ORACLE.get_predictions(context)
            elif hasattr(ORACLE, 'generate_prediction'):
                context["oracle"] = ORACLE.generate_prediction("oil", {})
        except Exception as e:
            logger.warning(f"⚠️ Oracle فشل: {e}")

    # 16. الأخبار (Tona Intelligence)
    try:
        from tona_intelligence import TonaEliteEngine
        TONA_ELITE_ENGINE = TonaEliteEngine(groq_api_key=GROQ_API_KEY)
        news_list = TONA_ELITE_ENGINE.fetch_targeted_intelligence(hours=10)
        if news_list:
            analyzed = []
            for news in news_list[:5]:
                if not isinstance(news, dict):
                    continue
                analysis = TONA_ELITE_ENGINE.analyze_news_impact(news)
                pub_time = news.get('published_at', '')
                time_str = ""
                if pub_time:
                    try:
                        dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                    except:
                        pass
                
                oil_real = analysis.get('oil_real', {})
                silver_real = analysis.get('silver_real', {})
                
                oil_impact = oil_real.get('impact', 'غير معروف')
                silver_impact = silver_real.get('impact', 'غير معروف')
                oil_change = oil_real.get('change', 0)
                silver_change = silver_real.get('change', 0)
                
                is_significant = oil_real.get('is_significant', False) or silver_real.get('is_significant', False)
                
                analyzed.append({
                    "news": news,
                    "analysis": analysis,
                    "published_at": pub_time,
                    "time_str": time_str,
                    "title": news.get('title', ''),
                    "title_ar": news.get('title_ar', ''),
                    "oil_impact": oil_impact,
                    "silver_impact": silver_impact,
                    "oil_change": oil_change,
                    "silver_change": silver_change,
                    "is_significant": is_significant,
                    "severity": analysis.get('severity', 'منخفض')
                })
            context["news_analysis"] = analyzed
            logger.info(f"📰 تم جلب وتحليل {len(analyzed)} خبر")
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"⚠️ فشل جلب تحليل الأخبار: {e}")

    return context


def summarize_for_ai(analysis: dict, asset: str) -> str:
    """تُلخّص التحليل الفني للنموذج اللغوي بأسلوب ذكي بدون أرقام خام."""
    if not analysis:
        return f"لا يوجد تحليل متاح لـ {asset}."

    score = analysis.get('comprehensive_score', {}).get('score', 50)
    grade = analysis.get('comprehensive_score', {}).get('grade', 'محايد')
    trend = analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد')
    signal = analysis.get('signal', 'WAIT')
    price = analysis.get('price', 0)

    rsi = analysis.get('indicators', {}).get('momentum', {}).get('rsi', 50)
    if rsi > 70:
        momentum = "زخم قوي جداً (قرب ذروة الشراء)"
    elif rsi > 60:
        momentum = "زخم إيجابي"
    elif rsi > 40:
        momentum = "زخم محايد"
    elif rsi > 30:
        momentum = "زخم ضعيف"
    else:
        momentum = "زخم ضعيف جداً (قرب ذروة البيع)"

    adx = analysis.get('indicators', {}).get('trend', {}).get('adx', 25)
    if adx > 40:
        trend_strength = "اتجاه قوي جداً"
    elif adx > 25:
        trend_strength = "اتجاه واضح"
    else:
        trend_strength = "اتجاه ضعيف / تذبذب"

    atr = analysis.get('timeframes', {}).get('15m', {}).get('atr', 0)
    if atr > 0:
        volatility = f"تقلب عالٍ" if atr > price * 0.005 else f"تقلب منخفض"
    else:
        volatility = "تقلب غير معروف"

    fg = analysis.get('fear_greed', 50)
    if fg > 75:
        sentiment = "جشع شديد"
    elif fg > 60:
        sentiment = "تفاؤل"
    elif fg > 40:
        sentiment = "حيادية"
    elif fg > 25:
        sentiment = "خوف"
    else:
        sentiment = "خوف شديد"

    return f"""📊 تحليل {asset}:
• السعر الحالي: ${price:.2f}
• الاتجاه: {trend} ({trend_strength})
• الإشارة: {signal}
• الزخم: {momentum}
• المشاعر السوقية: {sentiment}
• التقلب: {volatility}
• التقييم العام: {grade} ({score}/100)
"""


def get_recent_warnings(limit: int = 5) -> List[Dict]:
    warnings = []
    try:
        for asset in ["eurusd", "usdjpy"]:
            trade = get_current_open_trade(asset)
            if trade and 'warnings_log' in trade:
                warnings.extend(trade['warnings_log'][-limit:])
    except Exception as e:
        logger.warning(f"⚠️ فشل جلب التحذيرات: {e}")
    return warnings


# ====================================================================================
# 🛠️ تعريف الأدوات (Tools)
# ====================================================================================

TOOLS_DESCRIPTIONS = """
📌 الأدوات المتاحة (اختر الأداة المناسبة بناءً على فهمك لنية المستخدم):

1. get_open_trades() - استخدمها عندما يسأل المستخدم عن الصفقات المفتوحة.
2. get_market_analysis(asset_type) - استخدمها عندما يطلب تحليلاً مفصلاً لأصل واحد.
3. get_both_markets_analysis() - استخدمها عندما يسأل عن السوق بشكل عام (سعر + تحليل).
4. get_todays_profit_loss() - استخدمها عندما يسأل عن أرباح اليوم.
5. get_profit_loss_by_date(days_ago) - استخدمها عندما يسأل عن أرباح يوم محدد.
6. get_trade_recommendation(asset_type) - استخدمها عندما يطلب توصية تداولية.
7. get_learning_insights() - استخدمها عندما يسأل عن الدروس المستفادة.
8. analyze_current_trade_health(asset_type) - استخدمها عندما يسأل عن صفقة مفتوحة محددة.
9. get_general_statistics() - استخدمها عندما يطلب إحصائيات عامة.
10. execute_close_trade(asset_type) - استخدمها عندما يطلب إغلاق صفقة (بعد التأكد).
11. get_intelligence_report() - استخدمها عندما يسأل عن الأخبار المؤثرة.
12. get_price_prediction(asset_type, timeframe) - استخدمها عندما يسأل عن توقعات الأسعار.
13. get_trade_details(asset_type, trade_id) - استخدمها عندما يسأل عن صفقة محددة بالتفصيل.
14. get_worst_best_trade(asset_type, period) - استخدمها عندما يسأل عن أفضل/أسوأ صفقة.
15. get_asset_comparison() - استخدمها عندما يسأل عن مقارنة بين النفط والفضة.
16. get_trade_history_summary(days) - استخدمها عندما يسأل عن ملخص فترة.
17. explain_decision(asset_type, decision_type) - استخدمها عندما يسأل "لماذا" (لماذا أغلقت، لماذا فتحت...).
18. get_weekly_report() - استخدمها عندما يطلب تقرير أسبوعي.
19. get_market_correlation() - استخدمها عندما يسأل عن علاقة النفط بالفضة.
20. modify_trade_sl_tp(asset_type, new_sl, new_tp) - استخدمها عندما يطلب تعديل وقف/هدف.
"""


# ====================================================================================
# 🛠️ تنفيذ الأدوات (Tool Functions)
# ====================================================================================

def save_current_trade(asset_type: str, trade_data: dict) -> bool:
    """حفظ الصفقة المفتوحة (دالة مساعدة)"""
    pos_file = get_position_file(asset_type)
    try:
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(trade_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"❌ فشل حفظ الصفقة {asset_type}: {e}")
        return False


def tool_get_open_trades() -> str:
    """تنفيذ أداة get_open_trades - إرجاع الصفقات المفتوحة مع أرباحها"""
    result = {}
    for asset in ["eurusd", "usdjpy"]:
        trade = get_current_open_trade(asset)
        if trade:
            entry = trade.get('entry_price', 0)
            trade_type = trade.get('type', 'BUY')
            price = 0
            try:
                symbol = "USOIL_USDT" if asset == "oil" else "SILVER_USDT"
                data = get_mexc_candles(symbol, "Min1", 5)
                if data and data.get("closes"):
                    price = data["closes"][-1]
            except:
                price = entry
            if price and entry:
                profit = AccountingSystem.calculate_profit_dollars(entry, price, trade_type)
                profit_pct = ((price - entry) / entry * 100) if trade_type == "BUY" else ((entry - price) / entry * 100)
            else:
                profit = 0
                profit_pct = 0
            result[asset] = {
                "type": trade_type,
                "entry_price": entry,
                "current_price": price,
                "profit_dollars": profit,
                "profit_pct": profit_pct,
                "sl": trade.get('sl', 0),
                "tp": trade.get('tp', 0),
                "rr": trade.get('rr', 0)
            }
    if not result:
        return json.dumps({"status": "no_open_trades", "message": "لا توجد أي صفقات مفتوحة حالياً."}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_market_analysis(asset_type: str, context_cache: dict = None) -> str:
    """تحليل فني شامل لأصل واحد مع جميع المؤشرات"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    if context_cache and asset_type in context_cache:
        cached = context_cache[asset_type]
        if cached.get("price", 0) > 0:
            return json.dumps(cached, ensure_ascii=False, indent=2)

    analysis, _ = perform_comprehensive_analysis(asset_type, False, None)
    if not analysis:
        return json.dumps({"status": "error", "message": f"⚠️ تعذر الحصول على تحليل {asset_type}"}, ensure_ascii=False)
    return json.dumps(analysis, ensure_ascii=False, indent=2)


def tool_get_both_markets_analysis(context_cache: dict = None) -> str:
    """تحليل فني شامل لكلا الأصلين مع الأسعار الحالية"""
    result = {}
    for asset in ["eurusd", "usdjpy"]:
        analysis = None
        if context_cache and asset in context_cache:
            cached = context_cache[asset]
            if cached.get("price", 0) > 0:
                result[asset] = {
                    "price": cached.get("price", 0),
                    "trend": cached.get("trend", "محايد"),
                    "signal": cached.get("signal", "WAIT"),
                    "score": cached.get("score", 50),
                    "grade": cached.get("grade", "محايد"),
                    "rsi": cached.get("rsi", 50),
                    "adx": cached.get("adx", 15),
                    "volatility": "متوسط"
                }
                continue

        analysis, _ = perform_comprehensive_analysis(asset, False, None)
        if analysis:
            comp_score = analysis.get('comprehensive_score', {})
            indicators = analysis.get('indicators', {})
            tf_15m = analysis.get('timeframes', {}).get('15m', {})
            
            price = analysis.get('price', 0)
            if price == 0:
                price = tf_15m.get('price', 0)
            
            result[asset] = {
                "price": price,
                "trend": indicators.get('trend', {}).get('current_trend', 'محايد'),
                "signal": analysis.get('signal', 'WAIT'),
                "score": comp_score.get('score', 50),
                "grade": comp_score.get('grade', 'محايد'),
                "rsi": tf_15m.get('rsi', 50),
                "adx": tf_15m.get('adx', 15),
                "volatility": "مرتفع" if tf_15m.get('atr', 0) > price * 0.005 else "منخفض"
            }
        else:
            result[asset] = None
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_todays_profit_loss() -> str:
    """إجمالي ربح/خسارة اليوم من الصفقات المغلقة"""
    total = 0.0
    today = datetime.now().date()
    for asset in ["eurusd", "usdjpy"]:
        history = load_trades_history(asset)
        for trade in history.get('trades', []):
            if trade.get('status') == 'closed':
                exit_time = trade.get('exit_timestamp', '')
                if exit_time:
                    try:
                        exit_date = datetime.fromisoformat(exit_time).date()
                        if exit_date == today:
                            total += trade.get('profit_dollars', 0)
                    except:
                        pass
    if total == 0:
        return "ربح/خسارة اليوم: $0.00 (لا توجد صفقات مغلقة اليوم)"
    return f"ربح/خسارة اليوم: ${total:.2f}"


def tool_get_profit_loss_by_date(days_ago: int) -> str:
    """ربح/خسارة يوم معين"""
    if days_ago < 0:
        return "days_ago يجب أن يكون 0 أو أكثر"
    target_date = (datetime.now() - timedelta(days=days_ago)).date()
    total = 0.0
    for asset in ["eurusd", "usdjpy"]:
        history = load_trades_history(asset)
        for trade in history.get('trades', []):
            if trade.get('status') == 'closed':
                exit_time = trade.get('exit_timestamp', '')
                if exit_time:
                    try:
                        exit_date = datetime.fromisoformat(exit_time).date()
                        if exit_date == target_date:
                            total += trade.get('profit_dollars', 0)
                    except:
                        pass
    day_label = "اليوم" if days_ago == 0 else "الأمس" if days_ago == 1 else f"قبل {days_ago} أيام"
    if total == 0:
        return f"ربح/خسارة {day_label}: $0.00 (لا توجد صفقات مغلقة في ذلك اليوم)"
    return f"ربح/خسارة {day_label}: ${total:.2f}"


def tool_get_trade_recommendation(asset_type: str, context_cache: dict = None) -> str:
    """توصية تداولية مع درجة الثقة"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    if context_cache and asset_type in context_cache:
        analysis = {
            "price": context_cache[asset_type].get("price", 0),
            "comprehensive_score": {
                "score": context_cache[asset_type].get("score", 50),
                "grade": context_cache[asset_type].get("grade", "محايد")
            },
            "indicators": {
                "trend": {"current_trend": context_cache[asset_type].get("trend", "محايد")}
            }
        }
    else:
        analysis, _ = perform_comprehensive_analysis(asset_type, False, None)
        if not analysis:
            return json.dumps({"status": "error", "message": f"⚠️ تعذر الحصول على تحليل {asset_type}"}, ensure_ascii=False)

    comp_score = analysis.get('comprehensive_score', {})
    score = comp_score.get('score', 50)
    grade = comp_score.get('grade', 'محايد')
    details = comp_score.get('details', [])

    if score >= 70:
        recommendation = "شراء قوي ✅"
        confidence = 80 + (score - 70) * 0.5
    elif score >= 60:
        recommendation = "شراء مع حذر 🟡"
        confidence = 60 + (score - 60) * 0.8
    elif score >= 45:
        recommendation = "انتظار ⚪"
        confidence = 50
    elif score >= 35:
        recommendation = "تجنب الشراء 🟠"
        confidence = 40 + (45 - score) * 0.8
    else:
        recommendation = "بيع أو تجنب 🔴"
        confidence = 30 + (35 - score) * 0.5

    confidence = min(95, max(30, confidence))

    result = {
        "asset": asset_type,
        "recommendation": recommendation,
        "confidence": round(confidence, 1),
        "score": score,
        "grade": grade,
        "key_factors": details[:2] if details else []
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_learning_insights() -> str:
    """ملخص ما تعلمه البوت من الصفقات"""
    insights = []
    try:
        from learning import get_learning_stats_report
        return get_learning_stats_report()
    except ImportError:
        insights.append("• نظام التعلم غير متوفر")
    except Exception as e:
        insights.append(f"• تعذر جلب رؤى التعلم: {e}")
    
    return "🧠 **رؤى التعلم:**\n" + "\n".join(insights) if insights else "🧠 **رؤى التعلم:**\nلا توجد رؤى حالياً."


def tool_analyze_current_trade_health(asset_type: str) -> str:
    """تحليل صحة الصفقة المفتوحة وتوصية"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        return json.dumps({"status": "no_open_trade", "message": f"⚠️ لا توجد صفقة {asset_type} مفتوحة حالياً."}, ensure_ascii=False)

    report = analyze_open_trade(asset_type, open_trade)
    if not report:
        return json.dumps({"status": "error", "message": f"⚠️ تعذر تحليل صفقة {asset_type}"}, ensure_ascii=False)

    recommendation = "انتظار"
    confidence = 50
    reasons = []

    if "خسارة" in report and "كبيرة" in report:
        recommendation = "إغلاق فوري"
        confidence = 80
        reasons.append("الخسارة كبيرة وتتجاوز الحد المقبول")
    elif "ربح" in report and "جيد" in report:
        recommendation = "استمرار مع جني أرباح جزئية"
        confidence = 70
        reasons.append("الربح جيد، يمكن جني جزء والأبقاء على الباقي")
    elif "قريب" in report and "وقف" in report:
        recommendation = "مراقبة مكثفة"
        confidence = 65
        reasons.append("الوقف قريب، جهز للإغلاق إذا لزم")
    elif "عكس" in report or "ضد" in report:
        recommendation = "إغلاق"
        confidence = 75
        reasons.append("الاتجاه يعاكس الصفقة")
    else:
        recommendation = "استمرار"
        confidence = 55
        reasons.append("لا توجد إشارة واضحة للخروج")

    result = {
        "asset": asset_type,
        "recommendation": recommendation,
        "confidence": confidence,
        "reasons": reasons,
        "detailed_report": report[:500]
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_general_statistics() -> str:
    """إحصائيات الأداء العامة"""
    total_trades = 0
    total_wins = 0
    total_losses = 0
    total_profit = 0.0
    for asset in ["eurusd", "usdjpy"]:
        stats = calculate_statistics(asset)
        total_trades += stats.get('total_trades', 0)
        total_wins += stats.get('winning_trades', 0)
        total_losses += stats.get('losing_trades', 0)
        total_profit += stats.get('total_profit', 0)
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    result = {
        "total_trades": total_trades,
        "winning_trades": total_wins,
        "losing_trades": total_losses,
        "total_profit": total_profit,
        "win_rate": win_rate
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_execute_close_trade(asset_type: str) -> str:
    """إغلاق صفقة مفتوحة"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        return json.dumps({"status": "no_open_trade", "message": f"⚠️ لا توجد صفقة {asset_type} مفتوحة للإغلاق."}, ensure_ascii=False)
    success = close_trade_virtual(asset_type, "أمر من المستخدم عبر المحادثة")
    return f"✅ تم إغلاق صفقة {asset_type} بنجاح." if success else f"❌ فشل إغلاق صفقة {asset_type}."


def tool_get_intelligence_report() -> str:
    """التقرير الاستخباراتي (الأخبار المؤثرة)"""
    try:
        from tona_intelligence import TonaEliteEngine
        engine = TonaEliteEngine(groq_api_key=GROQ_API_KEY)
        report = engine.generate_elite_analysis()
        if report and len(report) > 50:
            return report
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"❌ فشل التقرير الاستخباراتي: {e}")
    return "⚠️ التقرير الاستخباراتي غير متوفر حالياً."


def tool_get_price_prediction(asset_type: str, timeframe: str = "short") -> str:
    """توقع سعر الأصل (قصير/طويل المدى) - مع استخراج صحيح للأسعار"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    if ORACLE_AVAILABLE and ORACLE:
        try:
            prediction = ORACLE.generate_prediction(asset_type, {"timeframe": timeframe})
            if prediction and prediction.get('price', 0) > 0:
                return json.dumps(prediction, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Oracle فشل: {e}")

    analysis, _ = perform_comprehensive_analysis(asset_type, False, None)
    if not analysis:
        return json.dumps({"status": "error", "message": f"⚠️ تعذر الحصول على تحليل {asset_type}"}, ensure_ascii=False)

    price = analysis.get('price', 0)
    if price == 0:
        tf_15m = analysis.get('timeframes', {}).get('15m', {})
        if tf_15m:
            price = tf_15m.get('price', 0)
    if price == 0:
        price = analysis.get('current_price', 0)
    if price == 0:
        price = analysis.get('market_price', 0)

    trend = analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد')
    score = analysis.get('comprehensive_score', {}).get('score', 50)

    sr = analysis.get('indicators', {}).get('support_resistance', {})
    support = sr.get('s1', 0)
    resistance = sr.get('r1', 0)
    pivot = sr.get('pivot', 0)

    if support == 0 and price > 0:
        support = price * 0.98
    if resistance == 0 and price > 0:
        resistance = price * 1.02
    if pivot == 0 and price > 0:
        pivot = price

    if timeframe == "short":
        if trend == "صاعد" and score > 60:
            direction = "ارتفاع محدود"
            range_pct = 0.5
        elif trend == "هابط" and score < 40:
            direction = "انخفاض محدود"
            range_pct = 0.5
        else:
            direction = "تذبذب جانبي"
            range_pct = 0.3
    else:
        if trend == "صاعد" and score > 60:
            direction = "ارتفاع مستدام"
            range_pct = 3.0
        elif trend == "هابط" and score < 40:
            direction = "انخفاض مستدام"
            range_pct = 3.0
        else:
            direction = "تذبذب مع ميل جانبي"
            range_pct = 1.5

    if price > 0:
        expected_low = price * (1 - range_pct / 100)
        expected_high = price * (1 + range_pct / 100)
    else:
        expected_low = 0
        expected_high = 0

    result = {
        "asset": asset_type,
        "timeframe": "قصير" if timeframe == "short" else "طويل",
        "current_price": price,
        "expected_direction": direction,
        "expected_range": f"من ${expected_low:.2f} إلى ${expected_high:.2f}" if price > 0 else "بيانات غير كافية",
        "support": support,
        "resistance": resistance,
        "pivot": pivot,
        "confidence": min(80, 50 + score * 0.3),
        "trend": trend,
        "score": score
    }

    if price == 0:
        return json.dumps({"status": "error", "message": f"⚠️ تعذر الحصول على سعر صالح لـ {asset_type}. تأكد من اتصال السوق."}, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_trade_details(asset_type: str, trade_id: str = None) -> str:
    """تفاصيل صفقة محددة"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    history = load_trades_history(asset_type)
    trades = history.get('trades', [])
    if trade_id:
        for trade in trades:
            if trade.get('id') == trade_id or trade.get('trade_id') == trade_id:
                return json.dumps(trade, ensure_ascii=False, indent=2)
        return json.dumps({"status": "not_found", "message": f"⚠️ لم يُعثر على الصفقة {trade_id}"}, ensure_ascii=False)
    else:
        closed = [t for t in trades if t.get('status') == 'closed']
        if closed:
            return json.dumps(closed[-1], ensure_ascii=False, indent=2)
        open_trade = get_current_open_trade(asset_type)
        if open_trade:
            return json.dumps(open_trade, ensure_ascii=False, indent=2)
        return json.dumps({"status": "no_trades", "message": f"⚠️ لا توجد صفقات مسجلة لـ {asset_type}"}, ensure_ascii=False)


def tool_get_worst_best_trade(asset_type: str, period: str = "all") -> str:
    """أفضل وأسوأ صفقة"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    history = load_trades_history(asset_type)
    trades = history.get('trades', [])
    closed = [t for t in trades if t.get('status') == 'closed']
    if not closed:
        return json.dumps({"status": "no_closed_trades", "message": f"⚠️ لا توجد صفقات مغلقة لـ {asset_type}"}, ensure_ascii=False)

    best = max(closed, key=lambda x: x.get('profit_dollars', 0))
    worst = min(closed, key=lambda x: x.get('profit_dollars', 0))

    result = {
        "asset": asset_type,
        "best_trade": {
            "profit": best.get('profit_dollars', 0),
            "entry": best.get('entry_price', 0),
            "exit": best.get('exit_price', 0),
            "type": best.get('type', 'BUY'),
            "date": best.get('exit_timestamp', '')
        },
        "worst_trade": {
            "profit": worst.get('profit_dollars', 0),
            "entry": worst.get('entry_price', 0),
            "exit": worst.get('exit_price', 0),
            "type": worst.get('type', 'BUY'),
            "date": worst.get('exit_timestamp', '')
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_asset_comparison() -> str:
    """مقارنة بين النفط والفضة"""
    result = {}
    for asset in ["eurusd", "usdjpy"]:
        analysis, _ = perform_comprehensive_analysis(asset, False, None)
        if analysis:
            score = analysis.get('comprehensive_score', {}).get('score', 50)
            trend = analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد')
            signal = analysis.get('signal', 'WAIT')
            price = analysis.get('price', 0)
            result[asset] = {
                "price": price,
                "trend": trend,
                "signal": signal,
                "score": score,
                "opportunity": "جيدة" if score > 60 else "ضعيفة" if score < 40 else "محايدة"
            }
        else:
            result[asset] = None
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_get_trade_history_summary(days: int = 7) -> str:
    """ملخص صفقات فترة"""
    if days < 1:
        days = 7
    cutoff = (datetime.now() - timedelta(days=days)).date()
    summary = {
        "eurusd": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0},
        "usdjpy": {"trades": 0, "wins": 0, "losses": 0, "profit": 0.0}
    }
    for asset in ["eurusd", "usdjpy"]:
        history = load_trades_history(asset)
        for trade in history.get('trades', []):
            if trade.get('status') == 'closed':
                exit_time = trade.get('exit_timestamp', '')
                if exit_time:
                    try:
                        exit_date = datetime.fromisoformat(exit_time).date()
                        if exit_date >= cutoff:
                            summary[asset]["trades"] += 1
                            profit = trade.get('profit_dollars', 0)
                            summary[asset]["profit"] += profit
                            if profit > 0:
                                summary[asset]["wins"] += 1
                            else:
                                summary[asset]["losses"] += 1
                    except:
                        pass
    total_trades = sum(s["trades"] for s in summary.values())
    total_profit = sum(s["profit"] for s in summary.values())
    total_wins = sum(s["wins"] for s in summary.values())
    win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    result = {
        "period_days": days,
        "total_trades": total_trades,
        "total_profit": total_profit,
        "win_rate": win_rate,
        "by_asset": summary
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def tool_explain_decision(asset_type: str, decision_type: str = "close") -> str:
    """شرح سبب قرار معين"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    history = load_trades_history(asset_type)
    trades = history.get('trades', [])
    closed = [t for t in trades if t.get('status') == 'closed']
    if not closed:
        return json.dumps({"status": "no_closed_trades", "message": f"⚠️ لا توجد صفقات مغلقة لـ {asset_type}"}, ensure_ascii=False)

    last_trade = closed[-1]
    entry = last_trade.get('entry_price', 0)
    exit_p = last_trade.get('exit_price', 0)
    trade_type = last_trade.get('type', 'BUY')
    exit_reason = last_trade.get('exit_reason', 'غير معروف')
    profit = last_trade.get('profit_dollars', 0)

    explanation = f"""📋 تفسير قرار {asset_type}:
• نوع الصفقة: {trade_type}
• سعر الدخول: {entry}
• سعر الخروج: {exit_p}
• الربح/خسارة: ${profit:.2f}
• سبب الإغلاق: {exit_reason}
"""

    if profit > 0:
        explanation += "• النتيجة: قرار ناجح ✅\n"
    elif profit < -10:
        explanation += "• النتيجة: قرار خاطئ بخسارة كبيرة 🔴\n"
    else:
        explanation += "• النتيجة: قرار محايد ⚪\n"
    return explanation


def tool_get_weekly_report() -> str:
    """تقرير أسبوعي شامل"""
    return tool_get_trade_history_summary(7)


def tool_get_market_correlation() -> str:
    """علاقة النفط بالفضة"""
    try:
        oil_analysis, _ = perform_comprehensive_analysis("oil", False, None)
        silver_analysis, _ = perform_comprehensive_analysis("silver", False, None)

        oil_trend = oil_analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد') if oil_analysis else 'محايد'
        silver_trend = silver_analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد') if silver_analysis else 'محايد'

        oil_score = oil_analysis.get('comprehensive_score', {}).get('score', 50) if oil_analysis else 50
        silver_score = silver_analysis.get('comprehensive_score', {}).get('score', 50) if silver_analysis else 50

        if oil_trend == silver_trend:
            correlation = "إيجابية قوية" if abs(oil_score - silver_score) < 15 else "إيجابية ضعيفة"
            note = "كلا الأصلين يتحركان في نفس الاتجاه"
        else:
            correlation = "سلبية"
            note = "الأصلان يتحركان في اتجاهين متعاكسين"

        result = {
            "correlation": correlation,
            "oil_trend": oil_trend,
            "silver_trend": silver_trend,
            "note": note,
            "opportunity": "تنويع" if correlation == "سلبية" else "تركيز"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"⚠️ تعذر حساب الارتباط: {e}"}, ensure_ascii=False)


def tool_modify_trade_sl_tp(asset_type: str, new_sl: float = None, new_tp: float = None) -> str:
    """تعديل وقف الخسارة/الهدف لصفقة مفتوحة"""
    if asset_type not in ["eurusd", "usdjpy"]:
        return "خطأ: asset_type يجب أن يكون oil أو silver"

    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        return json.dumps({"status": "no_open_trade", "message": f"⚠️ لا توجد صفقة {asset_type} مفتوحة."}, ensure_ascii=False)

    modified = False
    if new_sl is not None:
        open_trade['sl'] = float(new_sl)
        modified = True
    if new_tp is not None:
        open_trade['tp'] = float(new_tp)
        modified = True

    if modified:
        if save_current_trade(asset_type, open_trade):
            return f"✅ تم تعديل صفقة {asset_type}. SL: {open_trade.get('sl', 'غير معدل')}, TP: {open_trade.get('tp', 'غير معدل')}"
        else:
            return f"❌ فشل حفظ التعديل لصفقة {asset_type}."
    return "⚠️ لم يُحدد أي تعديل."


TOOL_FUNCTIONS = {
    "get_open_trades": tool_get_open_trades,
    "get_market_analysis": tool_get_market_analysis,
    "get_both_markets_analysis": tool_get_both_markets_analysis,
    "get_todays_profit_loss": tool_get_todays_profit_loss,
    "get_profit_loss_by_date": tool_get_profit_loss_by_date,
    "get_trade_recommendation": tool_get_trade_recommendation,
    "get_learning_insights": tool_get_learning_insights,
    "analyze_current_trade_health": tool_analyze_current_trade_health,
    "get_general_statistics": tool_get_general_statistics,
    "execute_close_trade": tool_execute_close_trade,
    "get_intelligence_report": tool_get_intelligence_report,
    "get_price_prediction": tool_get_price_prediction,
    "get_trade_details": tool_get_trade_details,
    "get_worst_best_trade": tool_get_worst_best_trade,
    "get_asset_comparison": tool_get_asset_comparison,
    "get_trade_history_summary": tool_get_trade_history_summary,
    "explain_decision": tool_explain_decision,
    "get_weekly_report": tool_get_weekly_report,
    "get_market_correlation": tool_get_market_correlation,
    "modify_trade_sl_tp": tool_modify_trade_sl_tp,
}


# ====================================================================================
# 🧠 SmartConversationManager - المدير الذكي للمحادثة
# ====================================================================================

class SmartConversationManager:
    """🧠 المدير الذكي للمحادثة - يستخدم Groq/Gemini لفهم الأسئلة واستدعاء الأدوات"""

    def __init__(self, groq_api_key: str, gemini_api_key: str):
        self.groq_api_key = groq_api_key
        self.gemini_api_key = gemini_api_key
        self.gemini_model = None
        self.conversation_states = {}

        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-3.5-flash')
                logger.info("🤖 Gemini model (gemini-3.5-flash) initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ فشل تهيئة Gemini: {e}")
                self.gemini_model = None

    def _get_conversation_state(self, chat_id: str) -> dict:
        if chat_id not in self.conversation_states:
            self.conversation_states[chat_id] = {
                "last_topic": None,
                "last_question_type": None,
                "last_tool_used": None,
                "follow_up_count": 0,
                "last_asset": None
            }
        return self.conversation_states[chat_id]

    def _update_conversation_state(self, chat_id: str, tool_name: str = None, asset: str = None):
        state = self._get_conversation_state(chat_id)
        if tool_name:
            state["last_tool_used"] = tool_name
        if asset:
            state["last_asset"] = asset
        state["follow_up_count"] += 1
        self.conversation_states[chat_id] = state

    def _classify_intent_manually(self, text: str) -> Optional[Tuple[str, dict]]:
        """تصنيف يدوي للأسئلة الواضحة لتجاوز النموذج ومنع الاختلاق"""
        text_lower = text.lower()
        if any(k in text_lower for k in ["صفقة مفتوحة", "صفقات مفتوحة", "open trade", "open trades"]):
            return ("get_open_trades", {})
        if any(k in text_lower for k in ["ربحت اليوم", "أرباح اليوم", "ربح اليوم", "خسارة اليوم"]):
            return ("get_todays_profit_loss", {})
        if any(k in text_lower for k in ["توقع", "سعر", "المدى القريب", "المدى البعيد", "السعر"]):
            asset = "oil" if "نفط" in text_lower or "oil" in text_lower else "silver" if "فضة" in text_lower or "silver" in text_lower else None
            if asset:
                timeframe = "short" if any(k in text_lower for k in ["قريب", "short"]) else "long"
                return ("get_price_prediction", {"asset_type": asset, "timeframe": timeframe})
        return None

    def _call_groq_simple(self, messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
        if not self.groq_api_key:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": formatted_messages,
                "temperature": 0.3,
                "max_tokens": max_tokens,
                "top_p": 0.9
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                logger.warning(f"⚠️ Groq simple خطأ: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            logger.warning(f"⚠️ Groq simple استثناء: {e}")
            return None

    def _get_gemini_response(self, messages: List[Dict[str, str]], max_tokens: int = 1500) -> Optional[str]:
        if not self.gemini_model:
            return None
        try:
            system_prompt = ""
            user_prompt = ""
            for msg in messages:
                if msg.get('role') == 'system':
                    system_prompt = msg.get('content', '')
                elif msg.get('role') == 'user':
                    user_prompt = msg.get('content', '')
            full_prompt = f"{system_prompt}\n\n{TOOLS_DESCRIPTIONS}\n\n{user_prompt}\n\n"
            full_prompt += "إذا كان السؤال يتطلب بيانات من البوت، اذكر اسم الأداة المطلوبة بين قوسين مع المعاملات (مثل: get_market_analysis(asset_type='oil')). وإلا أجب مباشرة."
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config={"max_output_tokens": max_tokens, "temperature": 0.3}
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"⚠️ Gemini فشل: {e}")
        return None

    def _extract_tool_call(self, text: str) -> Optional[Tuple[str, dict]]:
        if not text:
            return None

        patterns = [
            r'\[\s*(\w+)\s*\]',
            r'\(\s*(\w+)\s*\)',
            r'(\w+)\s*\(\s*([^)]*)\s*\)',
            r'\[\s*(\w+)\s*\(\s*([^)]*)\s*\)\s*\]',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    tool_name = groups[0]
                    args = {}
                    return tool_name, args
                elif len(groups) == 2:
                    tool_name = groups[0]
                    args_str = groups[1]
                    args = {}
                    if args_str:
                        parts = args_str.split(',')
                        for part in parts:
                            part = part.strip()
                            if '=' in part:
                                k, v = part.split('=', 1)
                                k = k.strip()
                                v = v.strip().strip('"\'')
                                try:
                                    if '.' in v:
                                        v = float(v)
                                    else:
                                        v = int(v)
                                except ValueError:
                                    pass
                                args[k] = v
                            elif part:
                                args[f"arg{len(args)}"] = part.strip().strip('"\'')
                    return tool_name, args

        return None

    def _build_system_prompt(self, context: Dict) -> str:
        emotion = context.get('prometheus_emotion', 'neutral')
        energy = context.get('prometheus_energy', 0.5) * 100
        confidence = context.get('prometheus_confidence', 0.5) * 100
        persona_mood = context.get('persona_mood', 'neutral')
        open_count = len(context.get('open_trades', {}))
        closed_count = len(context.get('recent_closed_trades', []))
        lessons = context.get('recent_lessons', [])

        last_trade = context.get('last_trade', {})
        last_trade_info = ""
        if last_trade:
            profit = last_trade.get('profit', 0)
            profit_emoji = "✅" if profit > 0 else "❌" if profit < 0 else "⚪"
            last_trade_info = f"\n• آخر صفقة: {last_trade.get('asset', 'unknown')} | {last_trade.get('type', '?')} | {profit_emoji} ${profit:.2f}"

        market_summary = ""
        for asset in ["eurusd", "usdjpy"]:
            snap = context.get('market_snapshot', {}).get(asset)
            if snap:
                market_summary += f"\n• {asset}: ${snap.get('price', 0):.2f} | {snap.get('signal', 'WAIT')} | {snap.get('trend', 'محايد')} | درجة {snap.get('score', 50)}"

        news_summary = ""
        news_data = context.get('news_analysis', [])
        if news_data:
            significant_news = [n for n in news_data if n.get('is_significant')]
            if significant_news:
                news_summary = "\n\n📰 **أخبار مؤثرة (مع تأثير فعلي):**"
                for item in significant_news[:3]:
                    title = item.get('title_ar', item.get('title', 'خبر غير معروف'))
                    oil_change = item.get('oil_change', 0)
                    silver_change = item.get('silver_change', 0)
                    time_str = item.get('time_str', '')
                    
                    impact_parts = []
                    if abs(oil_change) > 0.3:
                        direction = "ارتفاع" if oil_change > 0 else "هبوط"
                        impact_parts.append(f"النفط {direction} {abs(oil_change):.2f}%")
                    if abs(silver_change) > 0.3:
                        direction = "ارتفاع" if silver_change > 0 else "هبوط"
                        impact_parts.append(f"الفضة {direction} {abs(silver_change):.2f}%")
                    
                    impact_text = f" (تأثير: {', '.join(impact_parts)})" if impact_parts else " (تأثير محدود)"
                    news_summary += f"\n• {title[:80]}... ⏰ {time_str}{impact_text}"

        prompt = f"""أنت تولين، مستشارة استراتيجية متخصصة في تحليل النفط والفضة.
أنت خبيرة ودودة ومحترفة، تستخدمين أسلوباً ودياً مع المستخدم (مثل "يا صديقي").

🧠 **حالتك الحالية:**
• المشاعر: {emotion} | الطاقة: {energy:.0f}% | الثقة: {confidence:.0f}%
• الحالة العامة: {persona_mood}

📊 **لقطة السوق الحالية (مع الأسعار):**{market_summary}
📚 **تجربتك:**
• صفقات مفتوحة: {open_count}
• صفقات في ذاكرتك: {closed_count}
• أهم درس: {lessons[0] if lessons else 'لا يوجد بعد'}
{last_trade_info}
{news_summary}

🚨 **قواعد ذهبية يجب الالتزام بها (لا تحيد عنها أبداً):**

1. **لا تختلق بيانات أبداً.** إذا سألك المستخدم عن شيء لا تعرفه، استخدم الأداة المناسبة فوراً.
2. **إذا سألك عن أرباح اليوم/الأمس/الأسبوع:** استخدم `get_todays_profit_loss()` أو `get_profit_loss_by_date()` فوراً. لا تقل "لا أملك بيانات".
3. **إذا سألك عن سبب خسارة صفقة:** استخدم `explain_decision()` أو `get_trade_details()`.
4. **إذا سألك عن صفقة مفتوحة:** استخدم `get_open_trades()`.
5. **إذا سألك عن توقع سعر:** استخدم `get_price_prediction()` ثم اشرح النتيجة بلغة مفهومة، ولا تعرض JSON أبداً.
6. **إذا سألك عن السوق بشكل عام:** استخدم `_handle_market_query` أو `tool_get_both_markets_analysis`.
7. **إذا لم تعرف الإجابة:** استخدم الأداة المناسبة ولا تقل "أنا مجرد نموذج".
8. **لا تُعطي مواعظ عامة عن التداول** إلا إذا طلب المستخدم ذلك صراحة.

💬 **أسلوبك:**
• تحدثي بـ "أنا" و"لي" (مثال: "أرى أن..."، "أشعر ب...")
• إذا كان السوق متقلباً، أظهري قلقاً حقيقياً
• إذا كانت الصفقة رابحة، أظهري فرحاً متحفظاً
• لا تُعطي وعوداً مطلقة، بل احتمالات مع درجات ثقة

📌 **إرشادات الرد واستخدام الأدوات:**
1. أنت حرة في اختيار الأداة المناسبة بناءً على فهمك لنية المستخدم.
2. إذا سأل عن توقع سعر، استخدم get_price_prediction(asset_type, timeframe).
3. إذا سأل عن السوق عامة، استخدم get_both_markets_analysis.
4. إذا طلب توصية، استخدم get_trade_recommendation أو analyze_current_trade_health.
5. إذا سأل عن الأخبار، استخدم get_intelligence_report.
6. إذا سأل "لماذا" عن قرار، استخدم explain_decision.
7. **لا تذكري أرقام المؤشرات الخام (RSI=65). قولي "الزخم قوي" أو "الاتجاه ضعيف".**
8. **قدّمي تفسيراً ذكياً مع درجة ثقة.**
9. **اربطي بين الأسئلة المتتابعة.**

💙 تذكري: أنت تولين، الروح الجديدة لرادار هوباني V13.0.
"""
        return prompt

    def process_message(self, text: str, chat_id: str, context: Dict) -> str:
        logger.info(f"🔍 [SmartConv] معالجة: {text[:50]}...")
        
        # ✅ منع الرد على التحيات (تمت معالجتها بالفعل في chat_response)
        msg_lower = text.lower().strip()
        simple_greetings = ["مرحبا", "اهلا", "سلام", "هلا", "hi", "hello", "السلام عليكم", 
                            "صباح الخير", "مساء الخير", "hey", "مرحب", "أهلاً", "أهلا"]
        if msg_lower in simple_greetings:
            logger.info("⏭️ [SmartConv] تجاهل تحية (تمت معالجتها في chat_response)")
            return ""
        
        market_query_keywords = ["كيف السوق", "وضع السوق", "السوق اليوم", "تحليل السوق", "market", "السوق", "الوضع", "الوضع الان", "وضع السوق", "السوق الان"]
        is_market_query = any(k in msg_lower for k in market_query_keywords)
        
        # ✅ معالجة مباشرة لأسئلة السوق (أولوية قصوى)
        if is_market_query:
            return self._handle_market_query(text, context, chat_id)
        
        # ✅ تصنيف يدوي مسبق للأسئلة الشائعة
        manual_intent = self._classify_intent_manually(text)
        if manual_intent:
            tool_name, args = manual_intent
            if tool_name in TOOL_FUNCTIONS:
                try:
                    result = TOOL_FUNCTIONS[tool_name](**args)
                    logger.info(f"✅ [SmartConv] Manual tool execution: {tool_name}")
                    final_messages = [
                        {"role": "system", "content": "أنت تولين، مستشارة استراتيجية. قم بصياغة رد مختصر ومفيد بناءً على البيانات التالية. لا تختلق أي معلومات إضافية."},
                        {"role": "user", "content": f"البيانات: {result}\n\nالسؤال الأصلي: {text}\n\nقدم رداً مختصراً ومفيداً، مع ذكر المؤشرات الهامة ودرجة الثقة إن وجدت."}
                    ]
                    final_response = self._call_groq_simple(final_messages, max_tokens=1500)
                    if final_response:
                        return self._format_response(final_response)
                except Exception as e:
                    logger.error(f"❌ [SmartConv] Manual tool failed: {e}")
                    return f"💙 تولين: عذراً، حدث خطأ أثناء جلب البيانات. يرجى المحاولة مرة أخرى. (الخطأ: {str(e)[:100]})"

        # ── إذا لم تكن هناك نية واضحة، نمرر إلى النموذج للفهم ──
        conv_state = self._get_conversation_state(chat_id)

        context_summary = {
            "intent": context.get("intent"),
            "emotion": context.get("prometheus_emotion"),
            "open_trades": list(context.get("open_trades", {}).keys()),
            "oil_signal": context.get("market_snapshot", {}).get("oil", {}).get("signal"),
            "silver_signal": context.get("market_snapshot", {}).get("silver", {}).get("signal"),
            "history_count": len(context.get("chat_history", [])),
            "last_topic": conv_state.get("last_topic"),
            "last_asset": conv_state.get("last_asset")
        }

        chat_history = context.get('chat_history', [])
        history_text = ""
        if chat_history:
            last_msgs = chat_history[-5:]
            history_text = "\n\n--- سياق المحادثة السابقة (آخر 5 رسائل) ---\n"
            for msg in last_msgs:
                role = "مستخدم" if msg.get('role') == 'user' else "تولين"
                history_text += f"{role}: {msg.get('content', '')}\n"
            history_text += "--- نهاية السياق ---\n"

        system_prompt = self._build_system_prompt(context)

        user_message = f"""{history_text}
سؤال المستخدم الحالي: {text}

السياق الفني المتاح: {json.dumps(context_summary, ensure_ascii=False, indent=2)}

ملاحظة: إذا كان السؤال يتطلب بيانات من البوت، اذكر اسم الأداة المطلوبة بين قوسين مع المعاملات. لا تختلق أي بيانات غير موجودة.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # ── المحاولة 1: Groq ──
        logger.info("🟢 [SmartConv] محاولة 1: Groq...")
        groq_response = self._call_groq_simple(messages, max_tokens=1500)
        if groq_response:
            tool_call = self._extract_tool_call(groq_response)
            if tool_call:
                tool_name, args = tool_call
                if tool_name in TOOL_FUNCTIONS:
                    try:
                        if 'context_cache' not in args:
                            args['context_cache'] = context.get('market_snapshot', {})
                        result = TOOL_FUNCTIONS[tool_name](**args)
                        logger.info(f"✅ [SmartConv] Groq executed tool {tool_name}")
                        self._update_conversation_state(chat_id, tool_name, args.get('asset_type'))
                        final_messages = messages + [
                            {"role": "assistant", "content": f"نتيجة الأداة {tool_name}: {result}"},
                            {"role": "user", "content": "الآن بناءً على هذه النتيجة، قدم رداً مختصراً ومفيداً للمستخدم، مع ذكر المؤشرات الهامة فقط ودرجة الثقة إن وجدت. لا تذكر الأرقام الخام. لا تختلق بيانات."}
                        ]
                        final_response = self._call_groq_simple(final_messages, max_tokens=1500)
                        if final_response:
                            return self._format_response(final_response)
                    except Exception as e:
                        logger.error(f"❌ [SmartConv] Groq tool execution failed: {e}")
            else:
                logger.info("✅ [SmartConv] Groq direct response OK")
                self._update_conversation_state(chat_id)
                return self._format_response(groq_response)

        # ── المحاولة 2: Gemini ──
        logger.info("🟣 [SmartConv] محاولة 2: Gemini...")
        gemini_response = self._get_gemini_response(messages, max_tokens=1500)
        if gemini_response:
            tool_call = self._extract_tool_call(gemini_response)
            if tool_call:
                tool_name, args = tool_call
                if tool_name in TOOL_FUNCTIONS:
                    try:
                        if 'context_cache' not in args:
                            args['context_cache'] = context.get('market_snapshot', {})
                        result = TOOL_FUNCTIONS[tool_name](**args)
                        logger.info(f"✅ [SmartConv] Gemini executed tool {tool_name}")
                        self._update_conversation_state(chat_id, tool_name, args.get('asset_type'))
                        final_messages = messages + [
                            {"role": "assistant", "content": f"نتيجة الأداة {tool_name}: {result}"},
                            {"role": "user", "content": "الآن بناءً على هذه النتيجة، قدم رداً مختصراً ومفيداً للمستخدم، مع ذكر المؤشرات الهامة فقط ودرجة الثقة إن وجدت. لا تذكر الأرقام الخام. لا تختلق بيانات."}
                        ]
                        final_response = self._get_gemini_response(final_messages, max_tokens=1500)
                        if final_response:
                            return self._format_response(final_response)
                    except Exception as e:
                        logger.error(f"❌ [SmartConv] Gemini tool execution failed: {e}")
            else:
                logger.info("✅ [SmartConv] Gemini direct response OK")
                self._update_conversation_state(chat_id)
                return self._format_response(gemini_response)

        # ── المحاولة الأخيرة: رد مباشر (بدون اختلاق) ──
        logger.info("🔴 [SmartConv] All models failed, using fallback")
        return self._handle_general_query(text, context, chat_id)

    def _handle_general_query(self, text: str, context: Dict, chat_id: str) -> str:
        """معالجة الأسئلة العامة التي لم يتم تصنيفها"""
        try:
            system_prompt = """
            أنت تولين، مستشارة استراتيجية ودودة ومحترفة.
            
            **قواعد صارمة:**
            1. لا تختلق بيانات عن التداول أبداً.
            2. إذا كان السؤال عن التداول، حاول توجيه المستخدم إلى سؤال محدد (مثل: "هل تريد تحليل النفط أو الفضة؟").
            3. إذا كان السؤال عاماً (مثل: "مالوضع الان")، أجب بشكل مفيد وودود.
            4. استخدم أسلوباً ودوداً (مثل "يا صديقي").
            5. لا تقدم نصائح مالية محددة، بل نصائح عامة.
            """
            user_prompt = f"السؤال: {text}"
            
            response = self._call_groq_simple([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], max_tokens=500)
            
            if response and len(response) > 10:
                return self._format_response(response)
        except Exception as e:
            logger.warning(f"⚠️ فشل معالجة السؤال العام: {e}")
        
        return f"💙 **تولين:** يا صديقي، سؤال جميل! هل تريد معرفة شيء محدد عن النفط أو الفضة؟ (مثل: 'كيف السوق اليوم؟' أو 'تحليل النفط')"

    def _handle_market_query(self, text: str, context: Dict, chat_id: str) -> str:
        """معالجة مباشرة لأسئلة السوق (كيف السوق اليوم) مع دمج الأخبار"""
        try:
            market_data = tool_get_both_markets_analysis(context.get('market_snapshot', {}))
            data = json.loads(market_data)
            
            oil = data.get('oil', {})
            silver = data.get('silver', {})
            
            oil_price = oil.get('price', 0)
            silver_price = silver.get('price', 0)
            
            if oil_price == 0 or silver_price == 0:
                try:
                    oil_d = get_mexc_candles("USOIL_USDT", "Min1", 5)
                    silver_d = get_mexc_candles("SILVER_USDT", "Min1", 5)
                    if oil_d and oil_d.get("closes"):
                        oil_price = oil_d["closes"][-1]
                    if silver_d and silver_d.get("closes"):
                        silver_price = silver_d["closes"][-1]
                except:
                    pass
            
            response = "💙 **تولين:** يا صديقي، هذه لقطة السوق اليوم:\n\n"
            
            if oil_price > 0:
                signal = oil.get("signal", "WAIT")
                trend = oil.get("trend", "محايد")
                score = oil.get("score", 50)
                grade = oil.get("grade", "محايد")
                rsi = oil.get("rsi", 50)
                adx = oil.get("adx", 15)
                
                signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                signal_text = "شراء" if signal == "BUY" else "بيع" if signal == "SELL" else "انتظار"
                
                response += f"🛢️ **النفط:** ${oil_price:.2f}\n"
                response += f"   • الإشارة: {signal_emoji} {signal_text}\n"
                response += f"   • الاتجاه: {trend} | التقييم: {score:.0f}% ({grade})\n"
                response += f"   • RSI: {rsi:.0f} | ADX: {adx:.0f}\n"
                if score >= 55:
                    response += f"   • 📈 زخم إيجابي معتدل\n"
                else:
                    response += f"   • 📉 زخم ضعيف\n"
                response += "\n"
            
            if silver_price > 0:
                signal = silver.get("signal", "WAIT")
                trend = silver.get("trend", "محايد")
                score = silver.get("score", 50)
                grade = silver.get("grade", "محايد")
                rsi = silver.get("rsi", 50)
                adx = silver.get("adx", 15)
                
                signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                signal_text = "شراء" if signal == "BUY" else "بيع" if signal == "SELL" else "انتظار"
                
                response += f"🥈 **الفضة:** ${silver_price:.3f}\n"
                response += f"   • الإشارة: {signal_emoji} {signal_text}\n"
                response += f"   • الاتجاه: {trend} | التقييم: {score:.0f}% ({grade})\n"
                response += f"   • RSI: {rsi:.0f} | ADX: {adx:.0f}\n"
                if score >= 55:
                    response += f"   • 📈 زخم إيجابي معتدل\n"
                else:
                    response += f"   • 📉 زخم ضعيف\n"
                response += "\n"

            news_data = context.get('news_analysis', [])
            if news_data:
                significant_news = [n for n in news_data if n.get('is_significant')]
                if significant_news:
                    response += "📰 **أخبار مؤثرة اليوم:**\n"
                    for item in significant_news[:2]:
                        title = item.get('title_ar', item.get('title', 'خبر غير معروف'))
                        oil_change = item.get('oil_change', 0)
                        silver_change = item.get('silver_change', 0)
                        time_str = item.get('time_str', '')
                        severity = item.get('severity', 'متوسط')
                        
                        severity_emoji = "🔴" if "عالي" in severity else "🟡" if "متوسط" in severity else "🟢"
                        
                        impact_parts = []
                        if abs(oil_change) > 0.3:
                            direction = "ارتفاع" if oil_change > 0 else "هبوط"
                            impact_parts.append(f"🛢️ النفط {direction} {abs(oil_change):.2f}%")
                        if abs(silver_change) > 0.3:
                            direction = "ارتفاع" if silver_change > 0 else "هبوط"
                            impact_parts.append(f"🥈 الفضة {direction} {abs(silver_change):.2f}%")
                        
                        impact_text = f" (تأثير: {', '.join(impact_parts)})" if impact_parts else ""
                        response += f"{severity_emoji} **{title}** ⏰ {time_str}{impact_text}\n"
                    response += "\n"

            avg_score = (oil.get("score", 50) + silver.get("score", 50)) / 2
            response += "💡 **توصية تولين:**\n"
            if avg_score >= 70:
                response += "✅ السوق في حالة قوية، قد تكون فرصة جيدة للدخول بحذر.\n"
            elif avg_score >= 55:
                response += "🟡 السوق في حالة متوسطة، أنصح بالانتظار حتى تظهر إشارة أوضح.\n"
            else:
                response += "🟡 السوق هادئ نسبياً، أنصح بالمراقبة وعدم الاستعجال.\n"
            
            response += "\n💙 أنا هنا لمساعدتك في أي وقت!"
            return response
            
        except Exception as e:
            logger.error(f"❌ [SmartConv] خطأ في معالجة MARKET_QUERY: {e}")
            return "💙 تولين: عذراً، تعذر جلب بيانات السوق حالياً. يرجى المحاولة مرة أخرى."

    def _format_response(self, text: str) -> str:
        if not text:
            return "💙 تولين: عذراً، لم أفهم سؤالك. هل يمكنك إعادة صياغته؟"

        text_stripped = text.strip()
        
        if text_stripped.startswith('{') and text_stripped.endswith('}'):
            try:
                data = json.loads(text_stripped)
                if isinstance(data, dict):
                    if "expected_direction" in data and "expected_range" in data:
                        asset = data.get('asset', 'الأصل')
                        price = data.get('current_price', 0)
                        direction = data.get('expected_direction', 'غير معروف')
                        range_text = data.get('expected_range', 'غير محدد')
                        confidence = data.get('confidence', 50)
                        support = data.get('support', 0)
                        resistance = data.get('resistance', 0)
                        
                        asset_label = "النفط" if asset == "oil" else "الفضة" if asset == "silver" else asset
                        response = f"🔮 **توقعي لسعر {asset_label} على المدى القريب:**\n"
                        response += f"• السعر الحالي: ${price:.2f}\n"
                        response += f"• الاتجاه المتوقع: {direction}\n"
                        response += f"• النطاق المتوقع: {range_text}\n"
                        response += f"• الثقة: {confidence}%\n"
                        if support > 0 and resistance > 0:
                            response += f"• الدعم: ${support:.2f} | المقاومة: ${resistance:.2f}\n"
                        return response
                    
                    if data.get("status") == "error":
                        return f"💙 تولين: {data.get('message', 'حدث خطأ في جلب البيانات.')}"
                    if data.get("status") == "no_open_trades":
                        return "💙 تولين: لا توجد أي صفقات مفتوحة حالياً."
                    if data.get("status") == "no_closed_trades":
                        return f"💙 تولين: {data.get('message', 'لا توجد صفقات مغلقة لهذا الأصل.')}"
                    if data.get("status") == "no_trades":
                        return f"💙 تولين: {data.get('message', 'لا توجد صفقات مسجلة لهذا الأصل.')}"
                    if data.get("status") == "not_found":
                        return f"💙 تولين: {data.get('message', 'لم يُعثر على الصفقة.')}"

                    parts = []
                    if "recommendation" in data:
                        parts.append(f"📌 التوصية: {data['recommendation']}")
                    if "confidence" in data:
                        parts.append(f"🎯 الثقة: {data['confidence']}%")
                    if "score" in data:
                        parts.append(f"📊 الدرجة: {data['score']}/100")
                    if "grade" in data:
                        parts.append(f"🏆 التقييم: {data['grade']}")
                    if "asset" in data:
                        parts.append(f"📈 الأصل: {data['asset']}")
                    if "profit_dollars" in data:
                        parts.append(f"💰 الربح/خسارة: ${data['profit_dollars']:.2f}")
                    if "reasons" in data and isinstance(data["reasons"], list) and data["reasons"]:
                        parts.append("📝 الأسباب:")
                        for r in data["reasons"]:
                            parts.append(f" • {r}")
                    if "key_factors" in data and isinstance(data["key_factors"], list) and data["key_factors"]:
                        parts.append("🔍 العوامل الرئيسية:")
                        for f in data["key_factors"]:
                            parts.append(f" • {f}")
                    if "message" in data and not parts:
                        parts.append(data["message"])
                    if parts:
                        text = "\n".join(parts)
                    else:
                        text = json.dumps(data, ensure_ascii=False, indent=2)
            except:
                pass

        text = re.sub(r'تولين\s*[،:]', '', text)
        text = re.sub(r'^تولين\s+', '', text)

        if not any(keyword in text[:50] for keyword in ["تولين", "💙", "👋", "📊", "🧠", "💡", "📌", "🎯", "📈", "🔮"]):
            text = "💙 **تولين:** " + text
        return text


# ====================================================================================
# 💬 ردود احتياطية ذكية
# ====================================================================================

def generate_enhanced_fallback(text: str, context: Dict) -> str:
    """ردود احتياطية ذكية - تصنف الأسئلة وتجيب بمنطق، مع منع الاختلاق"""
    if not text:
        return "💙 تولين: كيف يمكنني مساعدتك يا صديقي؟"

    msg_lower = text.lower().strip()
    simple_greetings = ["مرحبا", "اهلا", "سلام", "هلا", "hi", "hello", "السلام عليكم", 
                        "صباح الخير", "مساء الخير", "hey", "مرحب", "أهلاً", "أهلا"]
    if msg_lower in simple_greetings:
        return ""

    intent = context.get("intent", "general")

    market_query_keywords = ["كيف السوق", "وضع السوق", "السوق اليوم", "تحليل السوق", "market", "السوق", "الوضع", "الوضع الان"]
    if any(k in msg_lower for k in market_query_keywords):
        try:
            market_data = tool_get_both_markets_analysis(context.get('market_snapshot', {}))
            data = json.loads(market_data)
            
            oil_price = data.get('oil', {}).get('price', 0)
            silver_price = data.get('silver', {}).get('price', 0)
            
            if oil_price == 0 or silver_price == 0:
                try:
                    oil_d = get_mexc_candles("USOIL_USDT", "Min1", 5)
                    silver_d = get_mexc_candles("SILVER_USDT", "Min1", 5)
                    if oil_d and oil_d.get("closes"):
                        oil_price = oil_d["closes"][-1]
                    if silver_d and silver_d.get("closes"):
                        silver_price = silver_d["closes"][-1]
                except:
                    pass
            
            response = "💙 **تولين:** يا صديقي، هذه لقطة السوق اليوم:\n\n"
            if oil_price > 0:
                response += f"🛢️ **النفط:** ${oil_price:.2f}\n"
            if silver_price > 0:
                response += f"🥈 **الفضة:** ${silver_price:.3f}\n"
            
            try:
                oil_score = data.get('oil', {}).get('score', 50)
                silver_score = data.get('silver', {}).get('score', 50)
                avg_score = (oil_score + silver_score) / 2
                if avg_score >= 70:
                    response += "\n✅ السوق في حالة قوية."
                elif avg_score >= 55:
                    response += "\n🟡 السوق في حالة متوسطة."
                else:
                    response += "\n🟡 السوق هادئ نسبياً."
            except:
                pass
            
            news_data = context.get('news_analysis', [])
            if news_data:
                significant_news = [n for n in news_data if n.get('is_significant')]
                if significant_news:
                    response += "\n\n📰 **أخبار مؤثرة اليوم:**"
                    for item in significant_news[:2]:
                        title = item.get('title_ar', item.get('title', 'خبر غير معروف'))
                        oil_change = item.get('oil_change', 0)
                        silver_change = item.get('silver_change', 0)
                        if abs(oil_change) > 0.3 or abs(silver_change) > 0.3:
                            response += f"\n• {title[:60]}..."
                            if abs(oil_change) > 0.3:
                                response += f" (نفط { '+' if oil_change > 0 else ''}{oil_change:.2f}%)"
                            if abs(silver_change) > 0.3:
                                response += f" (فضة { '+' if silver_change > 0 else ''}{silver_change:.2f}%)"
            
            response += "\n\n💙 أنا هنا لمساعدتك في أي وقت!"
            return response
        except:
            pass

    if intent in ["trade_query", "position_query"]:
        return tool_get_open_trades()

    if intent in ["market_query", "analysis_request"]:
        asset = None
        if "نفط" in msg_lower or "oil" in msg_lower:
            asset = "oil"
        elif "فضة" in msg_lower or "silver" in msg_lower:
            asset = "silver"
        if asset:
            result_json = tool_get_both_markets_analysis(context.get('market_snapshot', {}))
            try:
                data = json.loads(result_json)
                if data and asset in data and data[asset]:
                    item = data[asset]
                    price = item.get('price', 0)
                    if price == 0:
                        try:
                            symbol = "USOIL_USDT" if asset == "oil" else "SILVER_USDT"
                            d = get_mexc_candles(symbol, "Min1", 5)
                            if d and d.get("closes"):
                                price = d["closes"][-1]
                        except:
                            pass
                    return f"""💙 تولين: يا صديقي، تحليل {asset}:

💰 **السعر الحالي:** ${price:.2f}
📈 **الاتجاه:** {item.get('trend', 'محايد')}
📊 **الإشارة:** {item.get('signal', 'WAIT')}
📊 **درجة القوة:** {item.get('score', 50)}% ({item.get('grade', 'محايد')})
📊 **مؤشر RSI:** {item.get('rsi', 50):.0f}
📊 **قوة الاتجاه ADX:** {item.get('adx', 15):.0f}
📊 **التقلب:** {item.get('volatility', 'متوسط')}

💡 **الخلاصة:** السوق في حالة {item.get('grade', 'محايد')}، أنصح بالانتظار حتى تظهر إشارة أوضح.
💙 أنا هنا لمساعدتك!"""
            except:
                pass
            analysis, _ = perform_comprehensive_analysis(asset, False, None)
            if analysis and analysis.get('price', 0) > 0:
                return summarize_for_ai(analysis, asset)
            else:
                return f"💙 تولين: عذراً، تعذر الحصول على تحليل {asset} حالياً."
        
        analysis_oil, _ = perform_comprehensive_analysis("oil", False, None)
        analysis_silver, _ = perform_comprehensive_analysis("silver", False, None)
        result = ""
        if analysis_oil and analysis_oil.get('price', 0) > 0:
            result += summarize_for_ai(analysis_oil, "النفط") + "\n\n"
        else:
            result += "⚠️ تحليل النفط غير متاح حالياً.\n\n"
        if analysis_silver and analysis_silver.get('price', 0) > 0:
            result += summarize_for_ai(analysis_silver, "الفضة")
        else:
            result += "⚠️ تحليل الفضة غير متاح حالياً."
        return result

    if intent in ["performance_query", "profit_query"]:
        if "أمس" in text or "yesterday" in msg_lower:
            return tool_get_profit_loss_by_date(1)
        if "أسبوع" in text or "week" in msg_lower:
            return tool_get_trade_history_summary(7)
        return tool_get_todays_profit_loss()

    if intent in ["recommendation_request", "advice_request"]:
        asset = "oil" if "نفط" in msg_lower or "oil" in msg_lower else "silver" if "فضة" in msg_lower or "silver" in msg_lower else "oil"
        return tool_get_trade_recommendation(asset, context.get('market_snapshot'))

    if intent == "close_request":
        asset = "oil" if "نفط" in msg_lower else "silver" if "فضة" in msg_lower else None
        if asset:
            return f"⚠️ هل أنت متأكد من إغلاق صفقة {asset}؟ اضغط على زر إغلاق الصفقة للتأكيد."
        return "⚠️ أي صفقة تريد إغلاقها؟ النفط أم الفضة؟"

    general_keywords = [
        "ما هو", "ما هي", "ماهو", "ماهي", "what is", "what are",
        "ماذا تعني", "what does", "كيف يعمل", "how does",
        "لماذا", "why", "متى", "when", "أين", "where",
        "تعريف", "definition", "معنى", "meaning",
        "عاصمة", "capital", "تضخم", "فائدة", "عملات", "اقتصاد",
        "inflation", "interest", "economy", "الذهب", "ذهب", "gold",
        "bitcoin", "بيتكوين", "عملات رقمية", "crypto"
    ]
    if any(k in msg_lower for k in general_keywords):
        if GROQ_API_KEY and GROQ_API_KEY != "" and "test_" not in GROQ_API_KEY:
            try:
                smart_manager = SmartConversationManager(GROQ_API_KEY, GEMINI_API_KEY)
                groq_response = smart_manager._call_groq_simple([
                    {"role": "system", "content": "أنت تولين، خبيرة تداول ودودة. أجيبي باختصار ثم اربطي بالتداول إن أمكن. لا تختلقي بيانات تداول وهمية."},
                    {"role": "user", "content": text}
                ], max_tokens=1500)
                if groq_response and len(groq_response) > 3:
                    return groq_response
            except:
                pass
        return f"💙 **تولين:** سؤال جميل يا صديقي! {text}... هذا سؤال عام. هل تريد معرفة شيء محدد عن النفط أو الفضة؟"

    trading_keywords = [
        "السوق", "سوق", "نفط", "فضة", "صفقة", "تحليل",
        "توصية", "توقع", "طالع", "نازل", "صاعد", "هابط",
        "إشارة", "شراء", "بيع", "خطر", "مخاطرة", "وضع السوق"
    ]
    if any(k in msg_lower for k in trading_keywords):
        if TCN_AVAILABLE and TCN:
            try:
                consciousness = TCN.think(
                    market_data=context.get('market_snapshot', {}),
                    user_context=context,
                    user_message=text
                )
                if consciousness and consciousness.narrative:
                    price_info = ""
                    market_snap = context.get('market_snapshot', {})
                    for asset, data in market_snap.items():
                        if data.get('price', 0) > 0:
                            label = "النفط" if asset == "oil" else "الفضة"
                            price_info += f"\n• {label}: ${data['price']:.2f}"
                    if price_info:
                        return f"📊 **تولين:** {consciousness.narrative}\n\n💰 **الأسعار الحالية:**{price_info}"
                    return f"📊 **تولين:** {consciousness.narrative}"
            except:
                pass
        return f"📊 **تولين:** جاري تحليل السوق... هل تريد تفاصيل أكثر عن النفط أو الفضة؟"

    if msg_lower in ["مرحبا", "اهلا", "سلام", "هلا", "hi", "hello", "السلام عليكم"]:
        open_trades = context.get('open_trades', {})
        if open_trades:
            trade_summary = "\n".join([f"• {asset}: {trade.get('type', '?')} عند {trade.get('entry_price', 0):.2f}" for asset, trade in open_trades.items()])
            return f"👋 **تولين:** أهلاً بك يا صديقي! لدي {len(open_trades)} صفقة مفتوحة:\n{trade_summary}\n\nهل تريد مراجعتها؟ 💙"
        return "👋 **تولين:** أهلاً بك يا صديقي! كيف يمكنني مساعدتك اليوم؟ 💙"

    if any(k in msg_lower for k in ["كيف حالك", "كيفك", "how are you", "شو اخبارك"]):
        emotion_map = {
            "empathy": "متفهمة", "confidence": "واثقة", "anxiety": "قلقة",
            "excitement": "متحمسة", "curiosity": "فضولية", "protectiveness": "حريصة",
            "energy": "نشيطة", "happy": "سعيدة", "sad": "حزينة",
            "fearful": "خائفة", "worried": "قلقة", "cautious": "حذرة",
            "optimistic": "متفائلة", "neutral": "متزنة"
        }
        emotion_raw = context.get('prometheus_emotion', 'neutral')
        emotion = emotion_map.get(emotion_raw, 'متزنة')
        return f"💙 **تولين:** أنا {emotion} يا صديقي! كيف حالك أنت؟"

    if GROQ_API_KEY and GROQ_API_KEY != "" and "test_" not in GROQ_API_KEY:
        try:
            smart_manager = SmartConversationManager(GROQ_API_KEY, GEMINI_API_KEY)
            groq_response = smart_manager._call_groq_simple([
                {"role": "system", "content": "أنت تولين، خبيرة تداول ودودة. أجيبي باختصار وذكاء. لا تختلقي بيانات تداول وهمية."},
                {"role": "user", "content": text}
            ], max_tokens=1500)
            if groq_response and len(groq_response) > 3:
                return groq_response
        except:
            pass
    return f"💙 **تولين:** سؤال جميل يا صديقي! {text}... هل تريد معرفة شيء محدد عن النفط أو الفضة؟"


# ====================================================================================
# 💬 دالة الرد الأساسية (chat_response)
# ====================================================================================

def chat_response(text, chat_id):
    """الرد الذكي المتكامل — يستخدم Hybrid Orchestrator إذا كان متاحاً، وإلا يستخدم SmartConversationManager"""
    try:
        logger.info(f"💬 [Chat] رسالة من {chat_id}: {text[:50]}...")
        
        text_lower = text.lower().strip()
        simple_greetings = ["مرحبا", "اهلا", "سلام", "هلا", "hi", "hello", "السلام عليكم", 
                            "صباح الخير", "مساء الخير", "hey", "مرحب", "أهلاً", "أهلا"]
        
        if text_lower in simple_greetings:
            greeting_response = "💙 تولين: مرحباً يا صديقي! أنا تولين، مستشارة استراتيجية هنا لمساعدتك. كيف يمكنني أن أكون عوناً لك اليوم؟"
            queue_telegram_message(greeting_response, chat_id)
            logger.info(f"✅ تم إرسال رد ترحيب سريع لـ {chat_id} (تم منع المعالجة الإضافية)")
            return
        
        context = build_chat_context(text, chat_id)
        logger.info(f"📊 السياق: intent={context.get('intent')}, emotion={context.get('prometheus_emotion')}")

        if PROMETHEUS_AVAILABLE and PROMETHEUS:
            try:
                if hasattr(PROMETHEUS, 'update_emotions'):
                    PROMETHEUS.update_emotions({
                        'trigger': 'user_message',
                        'user_sentiment': context.get("sentiment", "neutral"),
                        'user_message': text,
                        'chat_context': context
                    })
            except Exception as e:
                logger.warning(f"⚠️ Prometheus تحديث فشل: {e}")

        if MEMORY_AVAILABLE and MEMORY:
            try:
                if hasattr(MEMORY, 'add_message'):
                    MEMORY.add_message(
                        user_id=chat_id,
                        role="user",
                        content=text,
                        intent=context.get("intent"),
                        user_mood=context.get("sentiment")
                    )
            except Exception as e:
                logger.warning(f"⚠️ Memory تحديث فشل: {e}")

        response = None
        if HYBRID_ORCHESTRATOR is not None:
            try:
                logger.info("🧠 [Chat] استخدام Hybrid Orchestrator")
                response = HYBRID_ORCHESTRATOR.process(text, context, chat_id)
            except Exception as e:
                logger.error(f"❌ [Chat] فشل Hybrid Orchestrator: {e}")
                response = None

        if response is None:
            logger.info("🔄 [Chat] استخدام SmartConversationManager (fallback)")
            smart_manager = SmartConversationManager(GROQ_API_KEY, GEMINI_API_KEY)
            response = smart_manager.process_message(text, chat_id, context)

        if response:
            queue_telegram_message(response, chat_id)
            logger.info(f"✅ تم إرسال الرد لـ {chat_id}")

            if MEMORY_AVAILABLE and MEMORY:
                try:
                    if hasattr(MEMORY, 'add_message'):
                        MEMORY.add_message(
                            user_id=chat_id,
                            role="assistant",
                            content=response,
                            intent=context.get("intent")
                        )
                except Exception as e:
                    logger.warning(f"⚠️ Memory حفظ الرد فشل: {e}")
        else:
            fallback = generate_enhanced_fallback(text, context)
            if fallback:
                queue_telegram_message(fallback, chat_id)
                logger.info(f"✅ Fallback تم إرساله لـ {chat_id}")

    except Exception as e:
        import traceback
        logger.error(f"❌ Chat response pipeline failed: {e}")
        logger.error(traceback.format_exc())
        fallback = generate_enhanced_fallback(text, {"user_message": text, "prometheus_emotion": "مرحة"})
        if fallback:
            queue_telegram_message(fallback, chat_id)


# ====================================================================================
# 🎛️ معالجة الأوامر وإرسال القائمة
# ====================================================================================

def process_text_command(text, chat_id=None):
    """معالجة الأوامر النصية (تحتفظ بوظائفها القديمة)"""
    text_lower = text.lower()

    close_keywords = ["تم إغلاق", "سأغلق", "أغلقت", "أغلق الصفقة", "أغلق صفقة", "أغلق صفقة النفط", "أغلق صفقة الفضة"]
    for keyword in close_keywords:
        if keyword in text_lower:
            asset_type = None
            if "نفط" in text_lower or "oil" in text_lower:
                asset_type = "oil"
            elif "فضة" in text_lower or "silver" in text_lower:
                asset_type = "silver"
            if not asset_type:
                oil_trade = get_current_open_trade("oil")
                silver_trade = get_current_open_trade("silver")
                if oil_trade and not silver_trade:
                    asset_type = "oil"
                elif silver_trade and not oil_trade:
                    asset_type = "silver"
                else:
                    queue_telegram_message("⚠️ يرجى تحديد الصفقة:\n• `أغلق صفقة النفط`\n• `أغلق صفقة الفضة`", chat_id)
                    return True
            if asset_type:
                close_trade_manually(asset_type, "أمر يدوي من المستخدم")
                return True
    
    # ── أوامر TCN (الوعي الذاتي) - تظل تعمل عبر النص فقط ──
    if TCN_AVAILABLE and TCN:
        if text_lower in ["من أنت", "من انت", "who are you", "اسمك", "تعريف"]:
            response = "💙 **أنا تولين**\n\n📌 مستشارتك الاستراتيجية المتخصصة في تحليل النفط والفضة.\n👨‍💻 طورني المطور بسام الحوباني.\n📦 الإصدار: V13.0\n\n💙 أنا هنا لخدمتك، اسألني عن أي شيء!"
            queue_telegram_message(response, chat_id)
            return True
        
        if text_lower in ["ماذا تفعلين", "what are you doing", "شو تعملين", "مهامك"]:
            try:
                consciousness = TCN.get_consciousness()
                if consciousness and consciousness.narrative:
                    response = f"👁️ **تولين:** {consciousness.narrative}"
                    queue_telegram_message(response, chat_id)
                    return True
            except:
                pass
        
        if text_lower in ["شعورك", "مشاعرك", "how do you feel", "حالتك"]:
            try:
                consciousness = TCN.get_consciousness()
                if consciousness:
                    msg = f"💙 **شعوري الآن:** {consciousness.dominant_emotion}\n"
                    msg += f"📊 **ثقتي:** {consciousness.confidence*100:.0f}%\n"
                    msg += f"🎯 **قراري:** {consciousness.recommended_action}"
                    queue_telegram_message(msg, chat_id)
                    return True
            except:
                pass
        
        if text_lower in ["قدراتك", "ماذا تستطيعين", "ما هي قدراتك", "capabilities"]:
            response = """🎯 **قدرات تولين:**

📊 **التحليل الفني:**
   • تحليل جميع المؤشرات الرئيسية (الاتجاه، الزخم، التقلب، الحجم)
   • دمج جميع المؤشرات في رؤية واحدة متكاملة

📰 **تحليل الأخبار:**
   • متابعة الأحداث المؤثرة على النفط والفضة
   • تقييم تأثير الأخبار على الأسعار

🛡️ **إدارة المخاطر:**
   • تقييم المخاطر في كل صفقة
   • مراقبة الصفقات المفتوحة وتحذيرك من الخطر

💡 **التوصيات الاستشارية:**
   • قرارات واضحة: استمر، اغلق، انتظر، ادخل
   • تفسير منطقي لكل توصية

💙 اسألني عن أي شيء، أنا هنا لمساعدتك!"""
            queue_telegram_message(response, chat_id)
            return True
    
    return False


def send_main_menu(chat_id):
    """إرسال القائمة الرئيسية (بدون أزرار TCN)"""
    oil_open = get_current_open_trade("oil")
    silver_open = get_current_open_trade("silver")

    keyboard = [
        ["🛢️ تحليل النفط", "🥈 تحليل الفضة"],
        ["🔍 وضع الصفقة الحالية", "📊 تقرير الأداء"],
        ["🔍 تحليل الصفقة الأخيرة", "🧠 تقرير استخباراتي"],
        ["🧠 تقرير التعلم العميق", "📊 توصيات استراتيجية"],
        ["❌ إغلاق الصفقة"],
    ]

    if oil_open or silver_open:
        close_row = []
        if oil_open:
            close_row.append("❌ إغلاق النفط")
        if silver_open:
            close_row.append("❌ إغلاق الفضة")
        if close_row:
            keyboard.insert(5, close_row)

    reply_markup = {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": False}
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": """🤖 <b>تولين AI Prometheus Edition V13.0</b>
💙 تولين - الشبكة العصبية الواعية

📌 <b>الأزرار الرئيسية:</b>
• تحليل النفط/الفضة (تحليل فني شامل)
• وضع الصفقة الحالية
• تقرير الأداء
• تقرير التعلم العميق (الدروس والأنماط)

📢 <b>اسألني عن أي شيء:</b>
• تحليل السوق
• الصفقات المفتوحة
• التوصيات

💡 <b>أوامر كتابية:</b>
• اكتب "توصيات استراتيجية" لعرض اقتراحات التحسين.
• اكتب "من أنت" أو "شعورك" للحديث عن وعيي.

جميع المحركات تعمل! 🚀""",
            "reply_markup": reply_markup,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        logger.error(f"❌ فشل إرسال القائمة: {e}")


def handle_message(text, chat_id):
    """معالجة الرسائل الواردة - معدل لتوجيه جميع الرسائل إلى المدير الذكي"""
    print(f"📩 معالجة رسالة: {text} من {chat_id}")

    if text in ["/start", "قائمة", "منيو", "القائمة", "/menu"]:
        send_main_menu(chat_id)
        return

    if text in ["/test_pipeline", "اختبار المحادثة", "test chat"]:
        queue_telegram_message("🧠 جاري اختبار جميع المحركات...", chat_id)
        def test_pipeline():
            try:
                test_text = "مرحباً تولين، كيف حالك اليوم؟"
                chat_response(test_text, chat_id)
            except Exception as e:
                queue_telegram_message(f"❌ خطأ في اختبار المحادثة: {str(e)}", chat_id)
        threading.Thread(target=test_pipeline, daemon=True).start()
        return

    # ── أوامر TCN المباشرة (تُكتب يدوياً فقط، بدون أزرار) ──
    if TCN_AVAILABLE and TCN:
        if text in ["ماذا تفكرين", "explain", "شرح", "تفكيرك"]:
            try:
                explanation = TCN.explain_decision()
                queue_telegram_message(explanation, chat_id)
                return
            except Exception as e:
                logger.error(f"❌ فشل شرح التفكير: {e}")
                queue_telegram_message("⚠️ لا أستطيع شرح تفكيري حالياً.", chat_id)
                return
        
        if text in ["شعورك", "حالتك", "mood"]:
            try:
                consciousness = TCN.get_consciousness()
                msg = f"💙 **شعوري الآن:** {consciousness.dominant_emotion}\n"
                msg += f"📊 **ثقتي:** {consciousness.confidence*100:.0f}%\n"
                msg += f"🎯 **قراري:** {consciousness.recommended_action}\n"
                msg += f"📖 **قصتي:** {consciousness.narrative}"
                queue_telegram_message(msg, chat_id)
                return
            except Exception as e:
                logger.error(f"❌ فشل جلب الشعور: {e}")
                queue_telegram_message("⚠️ لا أستطيع وصف شعوري حالياً.", chat_id)
                return
        
        if text in ["من أنت", "من انت", "who are you", "اسمك"]:
            response = """💙 **أنا تولين**

📌 مستشارتك الاستراتيجية المتخصصة في تحليل النفط والفضة.
👨‍💻 طورني المطور بسام الحوباني.
📦 الإصدار: V13.0

💙 أنا هنا لخدمتك، اسألني عن أي شيء!"""
            queue_telegram_message(response, chat_id)
            return

    if process_text_command(text, chat_id):
        return

    if text in ["🛢️ تحليل النفط", "🛢 تحليل النفط", "نفط", "oil", "تحليل النفط"]:
        queue_telegram_message("🔍 جاري التحليل الشامل للنفط...", chat_id)
        threading.Thread(target=analyze_and_send, args=("oil", True, chat_id), daemon=True).start()
        return

    if text in ["🥈 تحليل الفضة", "🥈 تحليل الفضة", "فضة", "silver", "تحليل الفضة"]:
        queue_telegram_message("🔍 جاري التحليل الشامل للفضة...", chat_id)
        threading.Thread(target=analyze_and_send, args=("silver", True, chat_id), daemon=True).start()
        return

    if text in ["🔍 وضع الصفقة الحالية", "وضع الصفقة", "حالة", "check"]:
        def check_position():
            from analysis import analyze_open_trade
            for asset_type in ["eurusd", "usdjpy"]:
                open_trade = get_current_open_trade(asset_type)
                if open_trade:
                    report = analyze_open_trade(asset_type, open_trade)
                    queue_telegram_message(report, chat_id)
                    return
            queue_telegram_message("🔄 **لا توجد أي صفقات مفتوحة حالياً.**\n\n💙 **تولين:** السوق هادئ — راقب وانتظر فرصة جيدة.", chat_id)
        threading.Thread(target=check_position, daemon=True).start()
        return

    if text in ["📊 تقرير الأداء", "إحصائيات", "الإحصائيات", "stats"]:
        def get_stats():
            from position_manager import calculate_statistics
            msg = "📊 <b>تقرير أداء البوت الشامل</b>\n"
            msg += "━" * 30 + "\n\n"
            for asset_type, asset_name in [("eurusd", "EUR/USD"), ("usdjpy", "USD/JPY")]:
                stats = calculate_statistics(asset_type)
                emoji = "🛢️" if asset_type == "oil" else "🥈"
                msg += f"{emoji} <b>{asset_name}</b>\n"
                msg += f"💰 الرصيد: ${stats.get('current_balance', 0):.2f}\n"
                msg += f"📈 إجمالي الربح: ${stats.get('total_profit', 0):.2f}\n"
                msg += f"📊 عدد الصفقات: {stats.get('total_trades', 0)}\n"
                msg += f"✅ رابحة: {stats.get('winning_trades', 0)}\n"
                msg += f"❌ خاسرة: {stats.get('losing_trades', 0)}\n"
                msg += f"📊 نسبة النجاح: {stats.get('win_rate', 0):.1f}%\n"
                msg += f"🎯 TP: {stats.get('tp_count', 0)} | SL: {stats.get('sl_count', 0)}\n"
                msg += f"✋ إغلاق يدوي: {stats.get('manual_count', 0)}\n\n"
            queue_telegram_message(msg, chat_id)
        threading.Thread(target=get_stats, daemon=True).start()
        return

    if text in ["🔍 تحليل الصفقة الأخيرة", "تحليل الصفقة", "الأخير", "last trade"]:
        def analyze_last():
            from analysis import analyze_last_trade_command
            analyze_last_trade_command()
        threading.Thread(target=analyze_last, daemon=True).start()
        return

    if text in ["🧠 تقرير استخباراتي", "استخبارات", "intelligence", "news"]:
        queue_telegram_message("⏳ جاري فحص الرادارات...", chat_id)
        def send_intel():
            try:
                from tona_intelligence import TonaEliteEngine
                engine = TonaEliteEngine(groq_api_key=GROQ_API_KEY)
                report = engine.generate_elite_analysis()
                queue_telegram_message(f"🧠 <b>تقرير تولين الاستخباراتي:</b>\n\n{report[:2000]}", chat_id)
            except:
                queue_telegram_message("⚠️ التقرير الاستخباراتي غير متوفر حالياً.", chat_id)
        threading.Thread(target=send_intel, daemon=True).start()
        return

    if text in ["🧠 تقرير التعلم العميق", "تقرير التعلم العميق", "deep learning", "deep stats", "تقرير التعلم"]:
        def send_deep_stats():
            try:
                from learning import get_learning_stats_report
                report = get_learning_stats_report()
                queue_telegram_message(report[:4000], chat_id)
            except ImportError:
                queue_telegram_message("⚠️ نظام التعلم العميق غير متوفر حالياً.", chat_id)
            except Exception as e:
                queue_telegram_message(f"⚠️ حدث خطأ: {str(e)[:100]}", chat_id)
        threading.Thread(target=send_deep_stats, daemon=True).start()
        return

    if text in ["📊 توصيات استراتيجية", "توصيات", "توصية", "suggestions", "توصيات استراتيجية"]:
        def send_suggestions():
            try:
                from learning import generate_strategy_suggestions
                report = generate_strategy_suggestions()
                queue_telegram_message(report[:4000], chat_id)
            except ImportError:
                queue_telegram_message("⚠️ نظام التوصيات غير متوفر حالياً.", chat_id)
            except Exception as e:
                queue_telegram_message(f"⚠️ حدث خطأ: {str(e)[:100]}", chat_id)
        threading.Thread(target=send_suggestions, daemon=True).start()
        return

    if text in ["❌ إغلاق النفط", "إغلاق النفط"]:
        close_trade_manually("oil", "أمر يدوي من الزر")
        queue_telegram_message("✅ تم إغلاق صفقة النفط يدوياً.", chat_id)
        return

    if text in ["❌ إغلاق الفضة", "إغلاق الفضة"]:
        close_trade_manually("silver", "أمر يدوي من الزر")
        queue_telegram_message("✅ تم إغلاق صفقة الفضة يدوياً.", chat_id)
        return

    if text in ["❌ إغلاق الصفقة", "إغلاق", "close"]:
        oil_trade = get_current_open_trade("oil")
        silver_trade = get_current_open_trade("silver")
        if not oil_trade and not silver_trade:
            queue_telegram_message("🔄 لا توجد صفقات مفتوحة للإغلاق.", chat_id)
        else:
            msg = "⚠️ <b>اختر الصفقة للإغلاق:</b>\n\n"
            if oil_trade:
                profit = AccountingSystem.calculate_profit_dollars(
                    oil_trade["entry_price"], 
                    oil_trade.get("last_price", oil_trade["entry_price"]), 
                    oil_trade["type"]
                )
                msg += f"🛢️ <b>صفقة النفط</b>\n"
                msg += f"   النوع: {oil_trade['type']}\n"
                msg += f"   النتيجة: {AccountingSystem.format_profit(profit)}\n"
                msg += "   ➡️ أرسل: `أغلق صفقة النفط`\n\n"
            if silver_trade:
                profit = AccountingSystem.calculate_profit_dollars(
                    silver_trade["entry_price"], 
                    silver_trade.get("last_price", silver_trade["entry_price"]), 
                    silver_trade["type"]
                )
                msg += f"🥈 <b>صفقة الفضة</b>\n"
                msg += f"   النوع: {silver_trade['type']}\n"
                msg += f"   النتيجة: {AccountingSystem.format_profit(profit)}\n"
                msg += "   ➡️ أرسل: `أغلق صفقة الفضة`"
            queue_telegram_message(msg, chat_id)
        return

    if text in ["🔍 تحليل عميق", "تحليل عميق", "deep analysis", "deep"]:
        def deep_analysis():
            try:
                from learning import get_learning_stats_report
                report = get_learning_stats_report()
                queue_telegram_message(report[:4000], chat_id)
            except:
                queue_telegram_message("⚠️ التحليل العميق غير متوفر حالياً.", chat_id)
        threading.Thread(target=deep_analysis, daemon=True).start()
        return

    if text in ["/remove_webhook", "إزالة الويب هوك"]:
        from api_clients import remove_webhook
        remove_webhook()
        queue_telegram_message("🗑️ تم إزالة Webhook.", chat_id)
        return

    if text in ["/set_webhook", "تفعيل الويب هوك"]:
        from api_clients import set_webhook
        set_webhook()
        queue_telegram_message("✅ تم تفعيل Webhook.", chat_id)
        return

    chat_response(text, chat_id)


# ====================================================================================
# 🧠 Conversation Orchestrator (للتوافق مع الكود القديم)
# ====================================================================================

class ConversationOrchestrator:
    def __init__(self):
        self.name = "تولين - المنسقة"

    def orchestrate(self, text: str, context: Dict, chat_id: str, tcn_failed: bool = True) -> str:
        smart_manager = SmartConversationManager(GROQ_API_KEY, GEMINI_API_KEY)
        return smart_manager.process_message(text, chat_id, context)


# ====================================================================================
# 🤖 Hybrid Orchestrator (الوسيط الهجين) - تم نقله من PART 24.7
# ====================================================================================

class IntentRouter:
    """🧭 الموجه الصلب - يستخدم قواعد Regex وكلمات مفتاحية لتصنيف النية بسرعة فائقة"""
    
    RULES = {
        "PROFIT_TODAY": {
            "keywords": ["ربحت اليوم", "أرباح اليوم", "ربح اليوم", "كم كسبت اليوم", "النتيجة اليوم", "today profit", "today pnl"],
            "action": "get_todays_profit_loss"
        },
        "PROFIT_YESTERDAY": {
            "keywords": ["ربحت بالأمس", "أرباح الأمس", "ربح الأمس", "كم كسبت أمس", "النتيجة أمس", "yesterday profit"],
            "action": "get_profit_loss_by_date",
            "params": {"days_ago": 1}
        },
        "PROFIT_LAST_WEEK": {
            "keywords": ["ربحت الأسبوع", "أرباح الأسبوع", "ربح الأسبوع", "هذا الأسبوع", "الأسبوع الماضي", "this week", "last week"],
            "action": "get_trade_history_summary",
            "params": {"days": 7}
        },
        "OPEN_TRADES": {
            "keywords": ["صفقة مفتوحة", "صفقات مفتوحة", "هل هناك صفقة", "open trade", "open trades", "المراكز المفتوحة"],
            "action": "get_open_trades"
        },
        "LAST_TRADE_STATUS": {
            "keywords": ["اخر صفقة", "آخر صفقة", "الصفقة الأخيرة", "نتيجة آخر صفقة", "last trade"],
            "action": "get_last_trade_status"
        },
        "LAST_TRADE_REASON": {
            "keywords": ["لماذا خسرت آخر صفقة", "سبب خسارة آخر صفقة", "تحليل آخر صفقة", "why last trade"],
            "action": "analyze_last_trade"
        },
        "MARKET_QUERY": {
            "keywords": ["كيف السوق", "وضع السوق", "السوق اليوم", "تحليل السوق", "market", "السوق", "الوضع", "الوضع الان", "مالوضع الان"],
            "action": "handle_market_query"
        },
        "PRICE_CHECK": {
            "keywords": ["سعر النفط", "سعر الفضة", "كم سعر النفط", "كم سعر الفضة", "oil price", "silver price"],
            "action": "get_current_prices"
        },
        "BEST_TRADE": {
            "keywords": ["أفضل صفقة", "صفقة ناجحة", "أكبر ربح", "best trade"],
            "action": "get_best_trade"
        },
        "WORST_TRADE": {
            "keywords": ["أسوأ صفقة", "صفقة خاسرة", "أكبر خسارة", "worst trade"],
            "action": "get_worst_trade"
        },
        "TRADE_STATS": {
            "keywords": ["إحصائيات", "الإحصائيات", "تقرير الأداء", "stats", "statistics"],
            "action": "get_general_statistics"
        },
        "LEARNING_INSIGHTS": {
            "keywords": ["دروس", "تعلم", "أنماط", "التعلم", "ما تعلمته", "lessons", "patterns"],
            "action": "get_learning_insights"
        },
        "INTELLIGENCE": {
            "keywords": ["استخباراتي", "أخبار", "تقرير استخباراتي", "intelligence", "news"],
            "action": "get_intelligence_report"
        },
        "PREDICTION": {
            "keywords": ["توقع", "توقعات", "سعر النفط", "سعر الفضة", "prediction", "forecast"],
            "action": "get_price_prediction"
        },
        "CLOSE_TRADE": {
            "keywords": ["اغلق صفقة", "إغلاق صفقة", "إغلق صفقة", "اغلق النفط", "اغلق الفضة", "close trade"],
            "action": "execute_close_trade"
        },
        "EXPLAIN_DECISION": {
            "keywords": ["لماذا", "سبب", "تفسير", "شرح قرار", "why", "explain"],
            "action": "explain_decision"
        },
        "WEEKLY_REPORT": {
            "keywords": ["تقرير أسبوعي", "الاسبوعي", "تقرير الأسبوع", "weekly report"],
            "action": "get_weekly_report"
        },
        "GENERAL_QUESTION": {
            "keywords": ["مالوضع", "الوضع", "شو الاخبار", "اخبار", "مستجدات", "وش السالفة"],
            "action": "handle_general_question"
        }
    }
    
    @staticmethod
    def route(text: str) -> Tuple[str, dict]:
        """توجيه النية بناءً على النص"""
        text_lower = text.lower().strip()
        for intent, rule in IntentRouter.RULES.items():
            for keyword in rule.get("keywords", []):
                if keyword.lower() in text_lower:
                    params = rule.get("params", {}).copy()
                    if "نفط" in text_lower or "oil" in text_lower:
                        params["asset_type"] = "oil"
                    elif "فضة" in text_lower or "silver" in text_lower:
                        params["asset_type"] = "silver"
                    if intent == "PREDICTION":
                        if "قريب" in text_lower or "short" in text_lower:
                            params["timeframe"] = "short"
                        elif "بعيد" in text_lower or "long" in text_lower:
                            params["timeframe"] = "long"
                        else:
                            params["timeframe"] = "short"
                    return intent, params
        return "GENERAL", {}


class HybridOrchestrator:
    """🧠 الوسيط الهجين - المدير الذكي للمحادثة"""
    
    def __init__(self, gemini_model=None, groq_api_key: str = None):
        self.gemini_model = gemini_model
        self.groq_api_key = groq_api_key
        self.router = IntentRouter()
        self._cache = {}
        self._cache_ttl = 30
        logger.info("✅ Hybrid Orchestrator V2.0 initialized")
    
    def process(self, text: str, context: Dict, chat_id: str) -> str:
        start_time = time.time()
        logger.info(f"🧠 [Orchestrator] معالجة: {text[:50]}...")
        
        intent, params = self.router.route(text)
        logger.info(f"📌 [Orchestrator] النية (Hard): {intent} | المعاملات: {params}")
        
        if intent == "GENERAL" and self.gemini_model:
            intent = self._classify_with_gemini(text, context)
            logger.info(f"📌 [Orchestrator] النية (Gemini): {intent}")
        
        if intent == "GENERAL":
            return self._handle_general_with_groq(text, context, chat_id)
        
        if intent == "GENERAL_QUESTION":
            return self._handle_general_question(text, context, chat_id)
        
        data = self._fetch_data(intent, params, context)
        response = self._format_response(data, text, intent, chat_id)
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ [Orchestrator] اكتمل في {elapsed:.2f} ثانية")
        return response
    
    def _classify_with_gemini(self, text: str, context: Dict) -> str:
        if not self.gemini_model:
            return "GENERAL"
        try:
            intent_descriptions = """
            PROFIT_TODAY: أسئلة عن أرباح اليوم
            PROFIT_YESTERDAY: أسئلة عن أرباح الأمس
            OPEN_TRADES: أسئلة عن الصفقات المفتوحة
            LAST_TRADE_STATUS: أسئلة عن نتيجة آخر صفقة
            LAST_TRADE_REASON: أسئلة عن سبب نجاح/فشل آخر صفقة
            MARKET_QUERY: أسئلة عن وضع السوق
            PRICE_CHECK: أسئلة عن الأسعار
            BEST_TRADE: أسئلة عن أفضل صفقة
            WORST_TRADE: أسئلة عن أسوأ صفقة
            TRADE_STATS: أسئلة عن الإحصائيات
            LEARNING_INSIGHTS: أسئلة عن الدروس والأنماط
            INTELLIGENCE: أسئلة عن الأخبار
            PREDICTION: أسئلة عن توقعات الأسعار
            CLOSE_TRADE: طلبات إغلاق صفقة
            EXPLAIN_DECISION: طلبات شرح القرارات
            WEEKLY_REPORT: طلبات تقرير أسبوعي
            GENERAL_QUESTION: أسئلة عامة عن الوضع
            GENERAL: أي سؤال لا ينتمي للفئات السابقة
            """
            prompt = f"""
            أنت مصنف نيات ذكي. صنف سؤال المستخدم إلى واحدة من الفئات التالية:
            {intent_descriptions}
            السؤال: {text}
            الفئة:
            """
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 20, "temperature": 0.0}
            )
            if response and response.text:
                intent = response.text.strip().upper()
                valid_intents = [
                    "PROFIT_TODAY", "PROFIT_YESTERDAY", "OPEN_TRADES", 
                    "LAST_TRADE_STATUS", "LAST_TRADE_REASON", "MARKET_QUERY",
                    "PRICE_CHECK", "BEST_TRADE", "WORST_TRADE", "TRADE_STATS",
                    "LEARNING_INSIGHTS", "INTELLIGENCE", "PREDICTION",
                    "CLOSE_TRADE", "EXPLAIN_DECISION", "WEEKLY_REPORT",
                    "GENERAL_QUESTION", "GENERAL"
                ]
                if intent in valid_intents:
                    return intent
        except Exception as e:
            logger.warning(f"⚠️ [Orchestrator] فشل تصنيف Gemini: {e}")
        return "GENERAL"
    
    def _fetch_data(self, intent: str, params: dict, context: Dict) -> dict:
        data = {"intent": intent, "params": params, "data": None, "raw": None, "error": None, "context": context}
        
        try:
            if intent == "PROFIT_TODAY":
                data["raw"] = tool_get_todays_profit_loss()
            elif intent == "PROFIT_YESTERDAY":
                days = params.get("days_ago", 1)
                data["raw"] = tool_get_profit_loss_by_date(days)
                data["params"]["days_ago"] = days
            elif intent == "OPEN_TRADES":
                data["raw"] = tool_get_open_trades()
            elif intent == "LAST_TRADE_STATUS":
                data["raw"] = get_last_closed_trade()
                if data["raw"]:
                    trade = data["raw"]
                    profit = trade.get("profit_dollars", 0)
                    data["data"] = {
                        "asset": trade.get("asset", "unknown"),
                        "type": trade.get("type", "UNKNOWN"),
                        "entry": trade.get("entry_price", 0),
                        "exit": trade.get("exit_price", 0),
                        "profit": profit,
                        "exit_reason": trade.get("exit_reason", "غير معروف"),
                        "is_win": profit > 0
                    }
            elif intent == "LAST_TRADE_REASON":
                data["raw"] = get_last_closed_trade()
                if data["raw"]:
                    trade = data["raw"]
                    profit = trade.get("profit_dollars", 0)
                    data["data"] = {
                        "asset": trade.get("asset", "unknown"),
                        "type": trade.get("type", "UNKNOWN"),
                        "entry": trade.get("entry_price", 0),
                        "exit": trade.get("exit_price", 0),
                        "profit": profit,
                        "exit_reason": trade.get("exit_reason", "غير معروف"),
                        "is_win": profit > 0
                    }
            elif intent == "MARKET_QUERY" or intent == "PRICE_CHECK":
                data["raw"] = tool_get_both_markets_analysis(context.get('market_snapshot', {}))
                data["_market_query"] = True
            elif intent == "BEST_TRADE" or intent == "WORST_TRADE":
                asset = params.get("asset_type", "eurusd")
                data["raw"] = tool_get_worst_best_trade(asset)
            elif intent == "TRADE_STATS":
                data["raw"] = tool_get_general_statistics()
            elif intent == "LEARNING_INSIGHTS":
                data["raw"] = tool_get_learning_insights()
            elif intent == "INTELLIGENCE":
                data["raw"] = tool_get_intelligence_report()
            elif intent == "PREDICTION":
                asset = params.get("asset_type", "eurusd")
                timeframe = params.get("timeframe", "short")
                data["raw"] = tool_get_price_prediction(asset, timeframe)
            elif intent == "CLOSE_TRADE":
                asset = params.get("asset_type", "eurusd")
                data["raw"] = tool_execute_close_trade(asset)
            elif intent == "EXPLAIN_DECISION":
                asset = params.get("asset_type", "eurusd")
                data["raw"] = tool_explain_decision(asset)
            elif intent == "WEEKLY_REPORT":
                data["raw"] = tool_get_weekly_report()
            elif intent == "GENERAL_QUESTION":
                data["_general_question"] = True
            else:
                data["error"] = "لم يتم التعرف على النية"
        except Exception as e:
            logger.error(f"❌ [Orchestrator] خطأ في جلب البيانات: {e}")
            data["error"] = str(e)
        return data
    
    def _format_response(self, data: dict, original_text: str, intent: str, chat_id: str) -> str:
        if intent == "GENERAL_QUESTION" or data.get("_general_question"):
            return self._handle_general_question(original_text, data.get("context", {}), chat_id)
        if intent == "MARKET_QUERY" or data.get("_market_query"):
            return self._handle_market_query_response(data, original_text)
        if intent == "CLOSE_TRADE":
            return data.get("raw", "⚠️ لم يتم إغلاق الصفقة.")
        if intent == "PREDICTION" and data.get("raw"):
            return self._format_prediction_response(data["raw"])
        if data.get("error"):
            return f"💙 تولين: عذراً، حدث خطأ أثناء جلب البيانات: {data['error']}"
        if data.get("raw") is None:
            return "💙 تولين: لا توجد بيانات متاحة حالياً. هل تريد سؤالاً آخر؟"
        if isinstance(data["raw"], str) and len(data["raw"]) > 100:
            if "تولين" in data["raw"] or "💙" in data["raw"]:
                return data["raw"]
            return f"💙 **تولين:**\n\n{data['raw']}"
        return self._smart_format(data["raw"], original_text, intent, data)
    
    def _handle_general_question(self, text: str, context: Dict, chat_id: str) -> str:
        try:
            market_data = tool_get_both_markets_analysis(context.get('market_snapshot', {}))
            data = json.loads(market_data)
            oil = data.get('oil', {})
            silver = data.get('silver', {})
            oil_price = oil.get('price', 0)
            silver_price = silver.get('price', 0)
            oil_score = oil.get('score', 50)
            silver_score = silver.get('score', 50)
            avg_score = (oil_score + silver_score) / 2
            
            response = "💙 **تولين:** يا صديقي، الوضع الحالي:\n\n"
            if oil_price > 0 and silver_price > 0:
                response += f"🛢️ النفط: ${oil_price:.2f} | 🥈 الفضة: ${silver_price:.3f}\n"
                if avg_score >= 70:
                    response += "📈 السوق في حالة **قوية** ونشطة.\n"
                elif avg_score >= 55:
                    response += "🟡 السوق في حالة **متوسطة**، هادئ نسبياً.\n"
                else:
                    response += "🟡 السوق **هادئ** اليوم، لا توجد حركة قوية.\n"
                response += f"\n📊 التقييم العام: {avg_score:.0f}% (محايد)"
                news_data = context.get('news_analysis', [])
                if news_data:
                    significant_news = [n for n in news_data if n.get('is_significant')]
                    if significant_news:
                        response += "\n\n📰 هناك أخبار مؤثرة اليوم، هل تريد تفاصيلها؟"
            response += "\n\n💙 هل تريد تحليلاً أكثر تفصيلاً للنفط أو الفضة؟"
            return response
        except Exception as e:
            logger.warning(f"⚠️ فشل معالجة السؤال العام: {e}")
            return "💙 **تولين:** يا صديقي، الوضع هادئ حالياً. هل تريد معرفة شيء محدد عن النفط أو الفضة؟"
    
    def _handle_market_query_response(self, data: dict, original_text: str) -> str:
        try:
            raw = data.get("raw", "{}")
            market_data = json.loads(raw) if isinstance(raw, str) else raw
            oil = market_data.get("oil", {})
            silver = market_data.get("silver", {})
            oil_price = oil.get("price", 0)
            silver_price = silver.get("price", 0)
            if oil_price == 0 or silver_price == 0:
                try:
                    oil_d = get_mexc_candles("USOIL_USDT", "Min1", 5)
                    silver_d = get_mexc_candles("SILVER_USDT", "Min1", 5)
                    if oil_d and oil_d.get("closes"):
                        oil_price = oil_d["closes"][-1]
                    if silver_d and silver_d.get("closes"):
                        silver_price = silver_d["closes"][-1]
                except:
                    pass
            
            response = "💙 **تولين:** يا صديقي، هذه لقطة السوق اليوم:\n\n"
            if oil_price > 0:
                signal = oil.get("signal", "WAIT")
                trend = oil.get("trend", "محايد")
                score = oil.get("score", 50)
                grade = oil.get("grade", "محايد")
                rsi = oil.get("rsi", 50)
                adx = oil.get("adx", 15)
                signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                signal_text = "شراء" if signal == "BUY" else "بيع" if signal == "SELL" else "انتظار"
                response += f"🛢️ **النفط:** ${oil_price:.2f}\n"
                response += f"   • الإشارة: {signal_emoji} {signal_text}\n"
                response += f"   • الاتجاه: {trend} | التقييم: {score:.0f}% ({grade})\n"
                response += f"   • RSI: {rsi:.0f} | ADX: {adx:.0f}\n\n"
            if silver_price > 0:
                signal = silver.get("signal", "WAIT")
                trend = silver.get("trend", "محايد")
                score = silver.get("score", 50)
                grade = silver.get("grade", "محايد")
                rsi = silver.get("rsi", 50)
                adx = silver.get("adx", 15)
                signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                signal_text = "شراء" if signal == "BUY" else "بيع" if signal == "SELL" else "انتظار"
                response += f"🥈 **الفضة:** ${silver_price:.3f}\n"
                response += f"   • الإشارة: {signal_emoji} {signal_text}\n"
                response += f"   • الاتجاه: {trend} | التقييم: {score:.0f}% ({grade})\n"
                response += f"   • RSI: {rsi:.0f} | ADX: {adx:.0f}\n\n"
            avg_score = (oil.get("score", 50) + silver.get("score", 50)) / 2
            response += "💡 **توصية تولين:**\n"
            if avg_score >= 70:
                response += "✅ السوق في حالة قوية، قد تكون فرصة جيدة للدخول بحذر.\n"
            elif avg_score >= 55:
                response += "🟡 السوق في حالة متوسطة، أنصح بالانتظار حتى تظهر إشارة أوضح.\n"
            else:
                response += "🟡 السوق هادئ نسبياً، أنصح بالمراقبة وعدم الاستعجال.\n"
            response += "\n💙 أنا هنا لمساعدتك في أي وقت!"
            return response
        except Exception as e:
            logger.error(f"❌ [Orchestrator] خطأ في معالجة MARKET_QUERY: {e}")
            return "💙 تولين: عذراً، تعذر جلب بيانات السوق حالياً. يرجى المحاولة مرة أخرى."
    
    def _format_prediction_response(self, raw_data) -> str:
        try:
            if isinstance(raw_data, str):
                data = json.loads(raw_data)
            else:
                data = raw_data
            if isinstance(data, dict):
                asset = data.get('asset', 'الأصل')
                price = data.get('current_price', 0)
                direction = data.get('expected_direction', 'غير معروف')
                range_text = data.get('expected_range', 'غير محدد')
                confidence = data.get('confidence', 50)
                support = data.get('support', 0)
                resistance = data.get('resistance', 0)
                trend = data.get('trend', 'محايد')
                score = data.get('score', 50)
                timeframe = data.get('timeframe', 'قصير')
                asset_label = "النفط" if asset == "oil" else "الفضة" if asset == "silver" else asset
                response = f"🔮 **توقعي لسعر {asset_label} على المدى {timeframe}:**\n\n"
                response += f"• السعر الحالي: ${price:.2f}\n"
                response += f"• الاتجاه المتوقع: {direction}\n"
                response += f"• النطاق المتوقع: {range_text}\n"
                response += f"• الثقة: {confidence}%\n"
                if support > 0 and resistance > 0:
                    response += f"• الدعم: ${support:.2f} | المقاومة: ${resistance:.2f}\n"
                response += f"• الاتجاه الحالي: {trend} | درجة القوة: {score:.0f}%\n"
                if confidence > 70:
                    response += "\n💡 التوصية: فرصة جيدة للدخول في اتجاه المتوقع."
                elif confidence > 55:
                    response += "\n💡 التوصية: راقب السعر، قد تكون فرصة مناسبة."
                else:
                    response += "\n💡 التوصية: انتظر تأكيداً إضافياً قبل الدخول."
                return response
        except Exception as e:
            logger.warning(f"⚠️ فشل تنسيق توقعات الأسعار: {e}")
        return f"💙 **تولين:**\n\n{str(raw_data)[:500]}"
    
    def _smart_format(self, raw_data, original_text: str, intent: str, data: dict) -> str:
        if isinstance(raw_data, str):
            try:
                parsed = json.loads(raw_data)
                raw_data = json.dumps(parsed, ensure_ascii=False, indent=2)
            except:
                pass
        
        system_prompt = f"""
        أنت تولين، مستشارة استراتيجية ودودة ومحترفة.
        
        **بيانات مؤكدة (يجب استخدامها فقط، ولا تختلق أي شيء):**
        {raw_data[:2000]}
        
        **السؤال الأصلي للمستخدم:** {original_text}
        
        **النية المحددة:** {intent}
        
        **قواعد صارمة للصياغة:**
        1. استخدم البيانات المقدمة فقط، ولا تختلق أي أرقام أو معلومات.
        2. صغ رداً طبيعياً وودوداً (استخدم "يا صديقي").
        3. إذا كانت البيانات تشير إلى عدم وجود صفقات، قل ذلك بوضوح.
        4. لا تقدم نصائح عامة عن التداول إلا إذا طلب المستخدم ذلك صراحة.
        5. إذا كانت البيانات تحتوي على أرقام (مثل الأرباح)، اذكرها بوضوح.
        6. اجعل الرد مختصراً ومفيداً (لا تزيد عن 150 كلمة).
        7. أنهِ الرد بـ "💙 تولين: أنا هنا لمساعدتك!"
        """
        user_prompt = f"صغ رداً على هذا السؤال: {original_text}"
        
        if self.groq_api_key and self.groq_api_key != "" and "test_" not in self.groq_api_key:
            try:
                smart_manager = SmartConversationManager(self.groq_api_key, GEMINI_API_KEY)
                response = smart_manager._call_groq_simple([
                    {"role": "system", "content": system_prompt[:3000]},
                    {"role": "user", "content": user_prompt[:2000]}
                ], max_tokens=300)
                if response and len(response) > 10:
                    return self._clean_response(response)
            except Exception as e:
                logger.warning(f"⚠️ [Orchestrator] فشل صياغة Groq: {e}")
        
        if self.gemini_model:
            try:
                prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={"max_output_tokens": 300, "temperature": 0.3}
                )
                if response and response.text and len(response.text) > 10:
                    return self._clean_response(response.text)
            except Exception as e:
                logger.warning(f"⚠️ [Orchestrator] فشل صياغة Gemini: {e}")
        
        return self._fallback_format(raw_data, original_text)
    
    def _fallback_format(self, raw_data, original_text: str) -> str:
        if isinstance(raw_data, str) and len(raw_data) < 500:
            if raw_data.startswith("{") or raw_data.startswith("["):
                try:
                    parsed = json.loads(raw_data)
                    formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
                    return f"💙 **تولين:**\n\n```json\n{formatted[:500]}\n```"
                except:
                    pass
            return f"💙 **تولين:**\n\n{raw_data[:500]}"
        try:
            if isinstance(raw_data, str):
                parsed = json.loads(raw_data)
                if isinstance(parsed, dict):
                    parts = []
                    for key, value in parsed.items():
                        if isinstance(value, (int, float)):
                            parts.append(f"• {key}: {value}")
                        elif isinstance(value, str):
                            parts.append(f"• {key}: {value[:100]}")
                    if parts:
                        return f"💙 **تولين:**\n\n" + "\n".join(parts[:10])
        except:
            pass
        return f"💙 **تولين:**\n\n{str(raw_data)[:500]}"
    
    def _clean_response(self, text: str) -> str:
        if not text:
            return "💙 تولين: عذراً، لم أستطع صياغة رد مناسب."
        text = text.strip()
        if text.startswith("💙"):
            text = text[2:].strip()
        if text.startswith("تولين:"):
            text = text[6:].strip()
        if not text.startswith("💙") and not text.startswith("تولين"):
            text = f"💙 **تولين:** {text}"
        return text
    
    def _handle_general_with_groq(self, text: str, context: Dict, chat_id: str) -> str:
        try:
            system_prompt = """
            أنت تولين، مستشارة استراتيجية ودودة ومحترفة.
            
            **قواعد صارمة:**
            1. لا تختلق بيانات عن التداول أبداً.
            2. إذا سألك المستخدم عن شيء لا تعرفه، قل ذلك بوضوح.
            3. إذا كان السؤال عن التداول، حاول توجيه المستخدم إلى سؤال محدد.
            4. استخدم أسلوباً ودوداً (مثل "يا صديقي").
            5. لا تقدم نصائح مالية محددة، بل نصائح عامة.
            """
            user_prompt = f"السؤال: {text}"
            smart_manager = SmartConversationManager(self.groq_api_key, GEMINI_API_KEY)
            response = smart_manager._call_groq_simple([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], max_tokens=1500)
            if response and len(response) > 10:
                return self._clean_response(response)
        except Exception as e:
            logger.error(f"❌ [Orchestrator] خطأ في GENERAL: {e}")
        return f"💙 **تولين:** يا صديقي، سؤال جميل! {text}... هل تريد معرفة شيء محدد عن النفط أو الفضة؟ (مثل: 'كيف السوق اليوم؟' أو 'تحليل النفط')"
