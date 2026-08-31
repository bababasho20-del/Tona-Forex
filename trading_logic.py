# -*- coding: utf-8 -*-
"""
📦 TRADING_LOGIC.PY - استراتيجية الدخول (analyze_and_send)
(نفس المحتوى السابق مع تحسينات في معالجة الأخطاء وإضافة رسائل تصحيح)
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

from constants import (
    logger, SIGNAL_COOLDOWN, MONITOR_TRIGGER, MONITOR_TRIGGER_LOCK,
    last_signal_states, last_signal_time, LAST_SIGNAL_LOCK
)
from utils import fmt_price, queue_telegram_message
from api_clients import get_mexc_candles, fetch_multiple_timeframes, get_fear_greed_index
from indicators import (
    calculate_supertrend_vpt_correct, calculate_rsi_7, calculate_macd_histogram,
    calculate_adx_14, calculate_atr_14, calculate_bollinger_bands,
    calculate_stochastic, calculate_vwap
)
from analysis import calculate_comprehensive_score
from position_manager import (
    load_config, add_trade_to_history, get_current_open_trade,
    close_trade_manually, AccountingSystem
)


def analyze_and_send(asset_type, is_manual=False, chat_id=None):
    """الدالة الرئيسية لتحليل وإرسال الإشارات"""
    try:
        logger.info(f"📊 [analyze_and_send] بدء تحليل {asset_type} (يدوي={is_manual})")
        _analyze_and_send_internal(asset_type, is_manual, chat_id)
    except Exception as e:
        import traceback
        logger.error(f"[Scanner] خطأ في analyze_and_send لـ {asset_type}: {e}")
        logger.error(traceback.format_exc())
        if is_manual:
            queue_telegram_message(f"⚠️ حدث خطأ أثناء تحليل {asset_type}. تفاصيل: {str(e)[:100]}", chat_id)


def _analyze_and_send_internal(asset_type, is_manual=False, chat_id=None):
    global last_signal_states, last_signal_time
    
    config = load_config()
    strategy_config = config["strategies"][asset_type]
    
    base_timeframe = strategy_config.get("base_timeframe", "Min15")
    
    st_multiplier = strategy_config.get("st_multiplier", 2.5 if asset_type == "oil" else 2.2)
    st_period = strategy_config.get("st_period", 100)
    vpt_len = strategy_config.get("vpt_len", 10)
    
    use_rsi_filter = strategy_config.get("use_rsi_filter", False)
    use_macd_filter = strategy_config.get("use_macd_filter", False)
    use_adx_filter = strategy_config.get("use_adx_filter", False)
    rsi_period = strategy_config.get("rsi_period", 7)
    rsi_min = strategy_config.get("rsi_min", 35)
    rsi_max = strategy_config.get("rsi_max", 65)
    macd_threshold = strategy_config.get("macd_threshold", 0.0)
    
    sltp_mode = strategy_config.get("sltp_mode", "ATR")
    sl_atr_mult = strategy_config.get("sl_atr_mult", 2.0)
    tp_atr_mult = strategy_config.get("tp_atr_mult", 3.0)
    min_rr = strategy_config.get("min_rr", 1.0)
    channel_buffer = strategy_config.get("channel_buffer", 0.0)
    
    symbol = "USOIL_USDT" if asset_type == "oil" else "SILVER_USDT"
    
    logger.info(f"📊 استخدام الفريم الزمني {base_timeframe} لـ {asset_type}")
    
    data = get_mexc_candles(symbol, interval=base_timeframe, limit=150)
    
    if not data or not data.get("closes") or len(data["closes"]) < 10:
        if is_manual:
            queue_telegram_message(f"⚠️ عذراً، لم أتمكن من جلب بيانات السوق حالياً (الفريم: {base_timeframe}).", chat_id)
        logger.warning(f"⚠️ بيانات {asset_type} غير كافية (القناة: {base_timeframe})")
        return
    
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    opens = data["opens"]
    volumes = data["volumes"]
    
    if len(closes) < 5:
        if is_manual:
            queue_telegram_message("⚠️ بيانات السوق غير كافية حالياً.", chat_id)
        return
    
    st_line_arr, trend, vpt_ema = calculate_supertrend_vpt_correct(
        data, 
        st_mult=st_multiplier,
        st_period=st_period,
        vpt_len=vpt_len
    )
    
    rsi_values = calculate_rsi_7(closes, length=rsi_period)
    current_rsi = rsi_values[-1] if rsi_values else 50
    
    macd_values = calculate_macd_histogram(closes)
    current_macd = macd_values[-1] if macd_values else 0
    
    adx = calculate_adx_14(data)
    
    signal_idx = -2
    
    if len(vpt_ema) > abs(signal_idx) and len(st_line_arr) > abs(signal_idx):
        current_vpt = vpt_ema[signal_idx]
        current_st = st_line_arr[signal_idx]
        previous_vpt = vpt_ema[signal_idx - 1] if len(vpt_ema) > abs(signal_idx - 1) else current_vpt
        previous_st = st_line_arr[signal_idx - 1] if len(st_line_arr) > abs(signal_idx - 1) else current_st
        
        crossover = previous_vpt <= previous_st and current_vpt > current_st
        crossunder = previous_vpt >= previous_st and current_vpt < current_st
    else:
        crossover = False
        crossunder = False
    
    logger.info(f"🔍 [{base_timeframe}] {asset_type}: VPT={current_vpt:.6f}, ST={current_st:.6f}, diff={current_vpt-current_st:.6f}")
    logger.info(f"🔍 [{base_timeframe}] {asset_type}: prev_VPT={previous_vpt:.6f}, prev_ST={previous_st:.6f}")
    logger.info(f"🔍 [{base_timeframe}] {asset_type}: crossover={crossover}, crossunder={crossunder}")
    logger.info(f"📊 [{base_timeframe}] {asset_type}: RSI={current_rsi:.1f}, MACD={current_macd:.4f}, ADX={adx:.1f}")
    
    signal = "WAIT"
    
    rsi_ok = True
    if use_rsi_filter:
        if crossover:
            rsi_ok = current_rsi < rsi_max
        elif crossunder:
            rsi_ok = current_rsi > rsi_min
    
    macd_ok = True
    if use_macd_filter:
        if crossover:
            macd_ok = current_macd > macd_threshold
        elif crossunder:
            macd_ok = current_macd < macd_threshold
    
    adx_ok = True
    if use_adx_filter:
        adx_ok = adx > 20
    
    if crossover and rsi_ok and macd_ok and adx_ok:
        signal = "BUY"
        logger.info(f"🚨 إشارة BUY مكتشفة لـ {asset_type}!")
    elif crossunder and rsi_ok and macd_ok and adx_ok:
        signal = "SELL"
        logger.info(f"🚨 إشارة SELL مكتشفة لـ {asset_type}!")
    
    if not is_manual:
        with LAST_SIGNAL_LOCK:
            current_state = last_signal_states[asset_type]
            now = time.time()
            
            if signal == "WAIT":
                return
            
            if signal == current_state["signal"] and (now - last_signal_time[asset_type]) < SIGNAL_COOLDOWN:
                logger.info(f"⏳ تجاهل إشارة {signal} مكررة لـ {asset_type} (قبل {int((now - last_signal_time[asset_type])/60)} دقيقة)")
                return
            
            last_signal_states[asset_type] = {"signal": signal, "time": now}
            last_signal_time[asset_type] = now
            logger.info(f"✅ تم تحديث last_signal_states[{asset_type}] = {signal} (الوقت: {now})")
    
    if signal == "WAIT" and not is_manual:
        return
    
    price = closes[-1]
    atr = calculate_atr_14(data)
    
    if sltp_mode == "Channel":
        pc_length = 130
        pc_max = max(highs[-pc_length:]) if len(highs) >= pc_length else max(highs)
        pc_min = min(lows[-pc_length:]) if len(lows) >= pc_length else min(lows)
        pc_atr = atr * 0.5
        
        pc_res = pc_max + pc_atr
        pc_sup = pc_min - pc_atr
        
        if signal == "BUY":
            sl = pc_sup - channel_buffer
            tp = pc_res
            rr = (tp - price) / (price - sl) if (price - sl) != 0 else 1.0
            if rr < min_rr:
                sl = price - (price - sl) * 0.8
        elif signal == "SELL":
            sl = pc_res + channel_buffer
            tp = pc_sup
            rr = (price - tp) / (sl - price) if (sl - price) != 0 else 1.0
            if rr < min_rr:
                sl = price + (sl - price) * 0.8
        else:
            sl = tp = price
    else:
        sl_dist = atr * sl_atr_mult
        tp_dist = atr * tp_atr_mult
        
        if signal == "BUY":
            sl = price - sl_dist
            tp = price + tp_dist
            rr = tp_atr_mult / sl_atr_mult
        elif signal == "SELL":
            sl = price + sl_dist
            tp = price - tp_dist
            rr = tp_atr_mult / sl_atr_mult
        else:
            sl = tp = price
    
    asset_label = "النفط الخام" if asset_type == "oil" else "الفضة"
    sig_label = "🟢 شراء (BUY)" if signal == "BUY" else "🔴 بيع (SELL)" if signal == "SELL" else "⚪ انتظار (WAIT)"
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "asset": asset_type,
        "current_price": price,
        "timeframes": {
            "15m": {
                "price": price,
                "rsi": current_rsi,
                "macd": current_macd,
                "adx": adx,
                "atr": atr,
                "volume_ratio": 1.0,
                "supertrend": {"line": st_line_arr[-1] if st_line_arr else price, "trend": trend[-1] if trend else 1}
            }
        }
    }
    
    timeframes = {
        "5m": {"interval": "Min5", "limit": 50},
        "1h": {"interval": "Min60", "limit": 100},
        "4h": {"interval": "Hour4", "limit": 50}
    }
    results = fetch_multiple_timeframes(symbol, timeframes)
    
    for tf_name, tf_data in [("5m", results.get("5m")), ("1h", results.get("1h")), ("4h", results.get("4h"))]:
        if tf_data and tf_data.get("closes") and len(tf_data["closes"]) >= 10:
            tcloses = tf_data["closes"]
            st_l, tr, _ = calculate_supertrend_vpt_correct(tf_data, st_mult=st_multiplier)
            analysis["timeframes"][tf_name] = {
                "price": tcloses[-1],
                "supertrend": {"line": st_l[-1] if st_l else tcloses[-1], "trend": tr[-1] if tr else 1}
            }
    
    vol_ratio = 1.0
    if volumes and len(volumes) > 20:
        current_vol = volumes[-1]
        avg_vol = sum(volumes[-20:-1]) / 19 if len(volumes) > 20 else current_vol
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
    analysis["timeframes"]["15m"]["volume_ratio"] = vol_ratio
    
    upper, basis, lower = calculate_bollinger_bands(closes)
    analysis["timeframes"]["15m"]["bollinger"] = {
        "upper": upper[-1] if upper else price * 1.02,
        "basis": basis[-1] if basis else price,
        "lower": lower[-1] if lower else price * 0.98
    }
    
    stoch = calculate_stochastic(highs, lows, closes)
    analysis["timeframes"]["15m"]["stochastic"] = stoch[-1] if stoch else 50
    
    vwap_values = calculate_vwap(data)
    analysis["timeframes"]["15m"]["vwap"] = vwap_values[-1] if vwap_values else price
    
    analysis["comprehensive_score"] = calculate_comprehensive_score(analysis, asset_type)
    
    # توليد التقرير الموجز (مع التعامل مع الأخطاء)
    full_report = "⚠️ تحليل غير متوفر"
    try:
        from advisor_core import format_concise_analysis
        full_report = format_concise_analysis(analysis, asset_type, is_monitoring=False)
    except Exception as e:
        logger.warning(f"⚠️ فشل format_concise_analysis في trading_logic: {e}")
        # استخدام بديل
        score = analysis.get("comprehensive_score", {}).get("score", 50)
        grade = analysis.get("comprehensive_score", {}).get("grade", "محايد")
        full_report = f"📊 تحليل {asset_type}\n💰 السعر: ${price:.2f}\n📊 التقييم: {score:.0f}% ({grade})"
    
    if is_manual:
        result = calculate_comprehensive_score(analysis, asset_type, None)
        score = result.get("score", 50)
        context = result.get("context", "neutral")
        metrics = result.get("metrics", {})
        
        bullish_count = metrics.get("bullish_count", 0)
        adx = metrics.get("adx", 20)
        rsi = metrics.get("rsi", 50)
        vol_ratio = metrics.get("vol_ratio", 1.0)
        fear_greed_raw = metrics.get("fear_greed", 50)
        support = metrics.get("support", price * 0.98)
        resistance = metrics.get("resistance", price * 1.02)
        atr = metrics.get("atr", price * 0.01)
        mid_range = (support + resistance) / 2
        fear_greed_text = get_fear_greed_index()
        
        lines = []
        
        lines.append(f"🤖 **رادار هوباني — تحليل {asset_label}**")
        lines.append(f"💰 السعر الحالي: ${fmt_price(price, asset_type)} | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        lines.append("🧠 **تشريح سيكولوجية الماركت الحالية:**")
        
        if bullish_count == 4:
            trend_desc = "سيطرة مطلقة للمشترين على كافة الفريمات والزخم يتسارع بقوة"
        elif bullish_count == 3:
            trend_desc = "المشترون يقودون الأسعار بثبات والمسار العام يتعزز تدريجياً"
        elif bullish_count == 2:
            trend_desc = "معركة عنيفة متساوية بين الثيران والدببة، السوق حائر تماماً"
        elif bullish_count == 1:
            trend_desc = "البائعون يسيطرون على معظم الفريمات والمشترون يدافعون بيأس عن خط دفاع أخير"
        else:
            trend_desc = "سيطرة مطلقة وحاسمة للبائعين وضغط هبوطي عنيف يجتاح الفريمات"
        lines.append(f" • 🧭 **ميزان القوى الفني:** {trend_desc} (تطابق الفريمات: {bullish_count}/4).")
        
        if rsi > 75:
            momentum_desc = f"اندفاع شرائي أعمى في قمة (RSI: {rsi:.1f}) — الأسعار متضخمة جداً والتصحيح مسألة وقت"
        elif rsi > 60:
            momentum_desc = f"ثقة شرائية عالية (RSI: {rsi:.1f}) — سيولة ذكية ومستقرة تدفع الأسعار لأعلى بأمان"
        elif 40 <= rsi <= 60:
            momentum_desc = f"حياد تام وترقب (RSI: {rsi:.1f}) — غياب تام للرغبة في السيطرة من الطرفين"
        elif rsi >= 30:
            momentum_desc = f"تراجع مستمر في العزم (RSI: {rsi:.1f}) — انسحاب المشترين تدريجياً وتفوق البائعين"
        else:
            momentum_desc = f"استسلام كامل للثيران (RSI: {rsi:.1f}) — هلع بيعي شديد يمهد لارتداد تصحيحي لاصطياد قاع حتمي"
        lines.append(f" • ⚖️ **نفسية وعاطفة المتداولين:** {momentum_desc}.")
        
        if adx > 30:
            strength_desc = f"عنيف وحاسم جداً (ADX: {adx:.1f}) — هناك حيتان تقود الاتجاه بقوة ولا مجال لمعاكسته"
        elif adx > 20:
            strength_desc = f"مستقر وصحي (ADX: {adx:.1f}) — حركة حقيقية نامية وموثوقة التداول"
        else:
            strength_desc = f"ميت اتجاهياً (ADX: {adx:.1f}) — مسار عرضي ممل يستنزف الحساب بالعمولات فقط"
        lines.append(f" • 🌪️ **قوة وقدرة المعركة الحالية:** {strength_desc}.")
        
        if vol_ratio > 2.0:
            vol_desc = f"تدفق ضخم واستثنائي ({vol_ratio:.1f}x) — دخول حيتان يؤكد صدق وصحة الحركة الحالية"
        elif vol_ratio > 1.2:
            vol_desc = f"نشاط تداول نشط وفوق المعدل ({vol_ratio:.1f}x) — المتداولون يدخلون بثقة جيدة"
        elif vol_ratio > 0.8:
            vol_desc = f"تداول اعتيادي وطبيعي ({vol_ratio:.1f}x) — سيولة ضمن النطاقات اليومية المستقرة"
        else:
            vol_desc = f"جفاف حاد في السيولة ({vol_ratio:.1f}x) — السوق يتنفس بصعوبة، الحركة الحالية مصيدة وهمية كاذبة"
        lines.append(f" • 🌊 **مصداقية السيولة والحجم:** {vol_desc}.")
        
        if fear_greed_raw < 20:
            sentiment_desc = f"هلع كامل ورعب بالأسواق ({fear_greed_raw}/100) — التسييل العشوائي يسيطر على الجماهير"
        elif fear_greed_raw < 35:
            sentiment_desc = f"خوف متزايد وحذر يسري بين المتداولين ({fear_greed_raw}/100)"
        elif fear_greed_raw > 80:
            sentiment_desc = f"نشوة وطمع مفرط خطير ({fear_greed_raw}/100) — شراء جنوني جماعي يسبق حدوث الكوارث العكسية"
        elif fear_greed_raw > 65:
            sentiment_desc = f"تفاؤل مبالغ فيه وقرب تشكيل قمة سعريّة ({fear_greed_raw}/100)"
        else:
            sentiment_desc = f"معنويات طبيعية ومتوازنة ({fear_greed_raw}/100)"
        lines.append(f" • 🎭 **معنويات ومشاعر الجماهير:** {sentiment_desc}.")
        lines.append("")
        
        lines.append("🔮 **مصفوفة خريطة الطريق والسيناريوهات المتوقعة (24 ساعة):**")
        
        if context == "panic":
            lines.append(f" 🟢 السيناريو الأفضل (40%): ارتداد تصحيحي حاد وسريع من مستويات الخوف نحو المستهدف ${fmt_price(mid_range, asset_type)}.")
            lines.append(f" 🟡 السيناريو المتوسط (40%): استقرار تدريجي وتجميع قاع شرائي محكم عند مستويات الدعم ${fmt_price(support, asset_type)}.")
            lines.append(f" 🔴 السيناريو الأسوأ (20%): استمرار موجة الذعر العشوائية وكسر القاع اللحظي نحو ${fmt_price(support - atr * 2, asset_type)}.")
        elif context == "euphoria":
            lines.append(f" 🟢 السيناريو المتفائل (30%): اندفاع أخير ناتج عن جنون الطمع لاختبار مستويات ${fmt_price(resistance + atr, asset_type)} قبل الهبوط.")
            lines.append(f" 🟡 السيناريو المرجح (50%): بدء تصحيح صحي هابط يفرغ التضخم السعري ويتجه نحو خط الوسط ${fmt_price(mid_range, asset_type)}.")
            lines.append(f" 🔴 السيناريو الأسوأ (20%): جني أرباح مفاجئ وعنيف يهبط بالأسعار مباشرة لسحق المشتريين عند الدعم ${fmt_price(support, asset_type)}.")
        elif context == "dead":
            lines.append(f" 🟢 السيناريو المتفائل (25%): اختراق مفاجئ يكسر جمود المسار العرضي لأعلى مستهدفاً ${fmt_price(resistance + atr, asset_type)}.")
            lines.append(f" 🟡 السيناريو المرجح (50%): استمرار الحركة المملة وانحصار السعر داخل القناة بين الدعم ${fmt_price(support, asset_type)} والمقاومة ${fmt_price(resistance, asset_type)}.")
            lines.append(f" 🔴 السيناريو المتشائم (25%): كسر مفاجئ للأسفل هرباً من ركود السيولة نحو مستويات ${fmt_price(support - atr, asset_type)}.")
        elif context == "bullish_confirmed":
            lines.append(f" 🟢 السيناريو الأفضل (50%): استمرار الاندفاع الصاعد الصحي نحو تحقيق أهداف عليا جديدة قرب ${fmt_price(resistance + atr, asset_type)}.")
            lines.append(f" 🟡 السيناريو المتوسط (35%): تراجع تصحيحي طفيف وصحي لإعادة اختبار خط الدعم اللحظي عند ${fmt_price(mid_range, asset_type)} ثم مواصلة الارتفاع.")
            lines.append(f" 🔴 السيناريو الأسوأ (15%): انعكاس مفاجئ لصناع السوق يضرب مستويات وقف الخسارة عند الدعم الحاسم ${fmt_price(support, asset_type)}.")
        elif context == "bearish_confirmed":
            lines.append(f" 🟢 السيناريو البديل (20%): حدوث ارتداد تصحيحي صاعد قصير الأجل لاختبار مناطق التسييل عند ${fmt_price(mid_range, asset_type)}.")
            lines.append(f" 🟡 السيناريو المرجح (40%): استمرار النزيف السلبي الهابط بثبات نحو خط الهدف الأدنى ${fmt_price(support, asset_type)}.")
            lines.append(f" 🔴 السيناريو الأسوأ (40%): تسارع حدة ضغط البيع والانزلاق العنيف للأسفل نحو مستويات ${fmt_price(support - atr * 2, asset_type)}.")
        elif context == "divergence":
            lines.append(" 🟢 السيناريو المتفائل (35%): اكتمال التباين وانعكاس حاد يعيد الاتجاه للمسار الصحيح.")
            lines.append(" 🟡 السيناريو المرجح (40%): استمرار التباين والتذبذب العنيف دون حسم واضح.")
            lines.append(f" 🔴 السيناريو المتشائم (25%): فشل التباين واستمرار الاتجاه الحالي نحو ${fmt_price(resistance if bullish_count >= 3 else support, asset_type)}.")
        else:
            lines.append(f" 🟢 السيناريو المتفائل (35%): كسر الاتجاه العرضي الحائر لصالح الصعود نحو ${fmt_price(resistance, asset_type)}.")
            lines.append(" 🟡 السيناريو المرجح (45%): استمرار تذبذب الأسعار بشكل عشوائي دون وجهة حاسمة.")
            lines.append(f" 🔴 السيناريو المتشائم (20%): هبوط واختبار لمستويات الدعم القريبة عند ${fmt_price(support, asset_type)}.")
        lines.append("")
        
        lines.append("⚠️ **إدارة المخاطر والتحذيرات الحرجة:**")
        
        warnings = []
        
        if context == "panic":
            warnings.append(("🔴", "هلع بيعي شديد وعشوائي بالأسواق — التحليلات الفنية قد تفقد منطقها مؤقتاً."))
        if context == "euphoria":
            warnings.append(("🔴", "طمع متضخم ونشوة شرائية مفرطة — القمم التاريخية تتكون في هذه الأجواء."))
        if vol_ratio < 0.6:
            warnings.append(("🔴", "سيولة جافة وشبه منعدمة — خطر الانعكاس السريع والمفاجئ."))
        if context == "divergence":
            warnings.append(("🔴", "تباين حاد (Divergence) بين حركة السعر والزخم الحقيقي — الانعكاس قريب جداً."))
        if adx < 20 and score > 40:
            warnings.append(("🟡", "زخم اتجاهي ضعيف بالرغم من صعود السعر — خطر الوقوع في مصيدة الشراء."))
        if vol_ratio < 1.0 and score > 35:
            warnings.append(("🟡", "حجم تداول منخفض يتعارض مع قوة الحركة الحالية."))
        if 65 < fear_greed_raw <= 80:
            warnings.append(("🟡", "تفاؤل مبالغ فيه — تجنب إضافة مراكز شرائية جديدة."))
        if 20 <= fear_greed_raw < 35:
            warnings.append(("🟡", "خوف عام يتصاعد — جهز الكاش لفرصة شرائية عكسية."))
        if rsi > 70 and adx < 25:
            warnings.append(("🟡", "تشبع شرائي بدون زخم قوي — تصحيح وشيك."))
        if rsi < 30 and adx < 25:
            warnings.append(("🟡", "تشبع بيعي بدون زخم قوي — ارتداد وشيك لكنه ضعيف."))
        
        if warnings:
            warnings.sort(key=lambda x: 0 if x[0] == "🔴" else 1)
            for emoji, text in warnings:
                lines.append(f" {emoji} {text}")
        else:
            lines.append(" 🟢 المخاطر ضمن الحدود الطبيعية — السوق يتحرك بانتظام.")
        lines.append("")
        
        lines.append("💡 **نصائح وتوجيهات تولين الاستراتيجية:**")
        
        if context == "panic":
            lines.append(" 1. **حظر البيع:** البيع هنا انتحار لأنك تبيع عند القاع.")
            lines.append(" 2. **حظر الشراء العشوائي:** انتظر إغلاق شمعة ارتداد صاعدة مع حجم.")
            lines.append(" 3. **للبائعين:** اغلق صفقات البيع فوراً واحجز أرباحك.")
        elif context == "euphoria":
            lines.append(" 1. **حظر الشراء:** أنت تشتري في سقف القمة.")
            lines.append(" 2. **للمشترين:** فعل جني الأرباح الجزئي فوراً.")
            lines.append(" 3. **لخارج السوق:** انتظر هبوطاً تصحيحياً قبل التفكير بالدخول.")
        elif context == "dead":
            lines.append(f" 1. **استراتيجية الأوامر المعلقة:** شراء عند اختراق ${fmt_price(resistance, asset_type)} أو بيع عند كسر ${fmt_price(support, asset_type)}.")
            lines.append(" 2. **إدارة العقود:** ضيق وقف الخسارة لأن الانفجار السعري قد يكون عنيفاً.")
        elif context == "bullish_confirmed":
            if fear_greed_raw > 65:
                lines.append(" 1. الاتجاه صاعد لكن الطمع مرتفع، ادخل بصفقات شراء مجزأة.")
                lines.append(" 2. حرك وقف الخسارة ديناميكياً لتأمين رأس المال.")
            else:
                lines.append(" 1. **بيئة شراء مثالية:** الزخم والسيولة يدعمون الصعود.")
                lines.append(f" 2. **التنفيذ:** شراء عند التراجع، الهدف ${fmt_price(resistance, asset_type)}.")
        elif context == "bearish_confirmed":
            if fear_greed_raw < 35:
                lines.append(" 1. الاتجاه هابط لكن الخوف متصاعد، لا تبيع ماركت.")
                lines.append(" 2. انتظر ارتداداً صغيراً لفتح صفقات بيع آمنة.")
            else:
                lines.append(" 1. **بيئة بيع مثالية:** البائعون يمسكون المبادرة.")
                lines.append(f" 2. **الأهداف:** استهدف الدعم ${fmt_price(support, asset_type)}.")
        elif context == "divergence":
            lines.append(" 1. **تحذير التباين:** حركة السعر وهمية، الانعكاس وشيك.")
            lines.append(" 2. ممنوع إضافة عقود، وضيق وقف الخسارة.")
        else:
            lines.append(" 1. السوق حائر — الهدوء والصب هما صمام أمان محفظتك.")
            lines.append(" 2. استخدم أوامر معلقة عند المستويات الرئيسية.")
        
        lines.append("")
        lines.append(f"🎭 **معنويات السوق العامة:** {fear_greed_text}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        msg = "\n".join(lines)
        # التأكد من أن الرسالة ليست فارغة
        if not msg or msg.strip() == "":
            msg = f"⚠️ لا توجد بيانات كافية لعرض تحليل {asset_label} حالياً."
        queue_telegram_message(msg, chat_id)
        return

    if signal in ["BUY", "SELL"]:
        trade_context = {
            "entry": price,
            "sl": sl,
            "tp": tp,
            "rr": rr,
            "price": price
        }
        
        confidence = None
        try:
            from confidence_scorer import ConfidenceScorer
            confidence_scorer = ConfidenceScorer()
            confidence = confidence_scorer.calculate(analysis, signal, trade_context)
            logger.info(f"📊 درجة الثقة: {confidence['total']:.0f}% ({confidence['grade']})")
        except ImportError:
            confidence = {"total": 70, "grade": "جيدة", "emoji": "📊", "breakdown": {}}
        except Exception as e:
            logger.error(f"❌ فشل حساب درجة الثقة: {e}")
            confidence = {"total": 70, "grade": "جيدة", "emoji": "📊", "breakdown": {}}
        
        try:
            from conviction_report import ConvictionReport
            conviction_report = ConvictionReport()
            report = conviction_report.generate(asset_type, signal, analysis, confidence, trade_context)
            logger.info(f"📋 تم توليد تقرير القناعة لـ {asset_type}")
        except ImportError:
            report = f"🤖 <b>إشعار صفقة جديدة - تولين AI V12.0</b>\n"
            report += f"📊 الأصل: {asset_label}\n"
            report += f"📉 الإشارة: {sig_label}\n"
            report += f"• الدخول: ${fmt_price(price, asset_type)}\n"
            report += f"📍 الهدف: ${fmt_price(tp, asset_type)}\n"
            report += f"🛡️ وقف الخسارة: ${fmt_price(sl, asset_type)}\n"
            report += f"⚡ قوة الاتجاه: {'قوي' if adx > 25 else 'متوسط' if adx > 20 else 'ضعيف'}\n"
            if full_report:
                report += "\n" + full_report
        except Exception as e:
            logger.error(f"❌ فشل توليد تقرير القناعة: {e}")
            report = f"🤖 <b>إشعار صفقة جديدة - تولين AI V12.0</b>\n"
            report += f"📊 الأصل: {asset_label}\n"
            report += f"📉 الإشارة: {sig_label}\n"
            report += f"• الدخول: ${fmt_price(price, asset_type)}\n"
            report += f"📍 الهدف: ${fmt_price(tp, asset_type)}\n"
            report += f"🛡️ وقف الخسارة: ${fmt_price(sl, asset_type)}\n"
            report += f"⚡ قوة الاتجاه: {'قوي' if adx > 25 else 'متوسط' if adx > 20 else 'ضعيف'}\n"
            if full_report:
                report += "\n" + full_report
        
        logger.info(f"📤 إرسال إشعار {asset_type} - {signal} (طول النص: {len(report)})")
        queue_telegram_message(report)
        logger.info(f"✅ تم إرسال إشعار {asset_type} بنجاح")

        # ================================================================
        # ✅ تسجيل الصفقة
        # ================================================================
        trade_id = f"{asset_type}_{int(datetime.now().timestamp())}"
        current_rsi = rsi_values[-1] if rsi_values else 50
        current_macd = macd_values[-1] if macd_values else 0

        trade_data = {
            "trade_id": trade_id,
            "type": signal,
            "entry_price": price,
            "sl": sl,
            "tp": tp,
            "profit_dollars": 0.0,
            "status": "open",
            "warnings_sent": [],
            "warnings_log": [],
            "recommendations_sent": [],
            "asset_type": asset_type,
            "entry_indicators": {
                "rsi": current_rsi,
                "adx": adx,
                "trend": "صاعد" if trend[-1] == 1 else "هابط",
                "macd": current_macd,
                "vpt": vpt_ema[-1] if vpt_ema else 0,
                "st_line": st_line_arr[-1] if st_line_arr else price
            },
            "rr": rr,
            "confidence": confidence.get('total', 70) if confidence else 70
        }

        logger.info(f"🟢 [Scanner] استدعاء add_trade_to_history لـ {asset_type} مع trade_id: {trade_id}")
        trade_saved = add_trade_to_history(asset_type, trade_data, holistic_entry_analysis=None)
        
        if not trade_saved:
            logger.error(f"❌ [Scanner] فشل حفظ صفقة {asset_type} - trade_id: {trade_id}")
            queue_telegram_message(
                f"⚠️ عذراً، حدث خطأ في حفظ صفقة {asset_label}. "
                f"تم إرسال التوصية ولكن الصفقة لم تُسجل. يرجى المحاولة مرة أخرى.",
                chat_id
            )
            return
        else:
            logger.info(f"✅ [Scanner] تم حفظ صفقة {asset_type} بنجاح - trade_id: {trade_id}")

        verify_trade = get_current_open_trade(asset_type)
        if verify_trade:
            logger.info(f"✅ [Scanner] تم التحقق من وجود الصفقة في current_position_*.json")
        else:
            logger.error(f"❌ [Scanner] الصفقة غير موجودة في current_position_*.json رغم نجاح الحفظ!")

        with MONITOR_TRIGGER_LOCK:
            MONITOR_TRIGGER[asset_type] = {"reason": "new_trade", "time": time.time()}
