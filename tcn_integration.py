"""
═══════════════════════════════════════════════════════════════════════════════════
🔗 TCN Integration Module — ربط شبكة الوعي بـ main.py
💙 تولين: الآن تفكر قبل أن تتكلم
═══════════════════════════════════════════════════════════════════════════════════

📌 كيفية الاستخدام:
    1. استيراد TCN بعد استيراد كل المحركات
    2. إنشاء الشبكة بـ create_consciousness_network()
    3. استبدال generate_smart_response() بـ tcn.think() + tcn.explain_decision()
    4. استبدال analyze_and_send() بـ tcn.think() + توليد إشارة ذكية

📌 الفرق الجوهري:
    قبل: كل محرك يُعطي نتيجة → Decision Matrix يختار → رد ثابت
    بعد: الشبكة تتفاعل → توليد "حالة وعي" → رد ديناميكي يتغير مع السوق
═══════════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PART A: استيراد TCN في main.py (يُضاف بعد PART 09)
# ═══════════════════════════════════════════════════════════════════════════════

# ── استيراد TCN ──
try:
    from consciousness_network import ConsciousnessNetwork, create_consciousness_network
    TCN_AVAILABLE = True
    print("🧠 Consciousness Network: الشبكة الواعية استيقظت!")
except ImportError as e:
    print(f"⚠️ Consciousness Network غير متوفر: {e}")
    TCN_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# PART B: تهيئة TCN في main.py (يُضاف بعد تهيئة كل المحركات)
# ═══════════════════════════════════════════════════════════════════════════════

TCN = None

if TCN_AVAILABLE:
    try:
        # جمع كل المحركات المتوفرة
        engines_dict = {}

        if ANALYZER_AVAILABLE and MARKET_ANALYZER:
            engines_dict['market_analyzer'] = MARKET_ANALYZER
        if INDICATORS_AVAILABLE and ADVANCED_INDICATORS:
            engines_dict['advanced_indicators'] = ADVANCED_INDICATORS
        if PATTERN_AVAILABLE and PATTERN_ANALYZER:
            engines_dict['pattern_analyzer'] = PATTERN_ANALYZER
        if PREDICTOR_AVAILABLE and PREDICTOR:
            engines_dict['predictor'] = PREDICTOR
        if PROMETHEUS_AVAILABLE and PROMETHEUS:
            engines_dict['prometheus'] = PROMETHEUS
        if CHRONOS_AVAILABLE and CHRONOS:
            engines_dict['chronos'] = CHRONOS
        if ORACLE_AVAILABLE and ORACLE:
            engines_dict['oracle'] = ORACLE
        if RISK_MASTER_AVAILABLE and RISK_MASTER:
            engines_dict['risk_master'] = RISK_MASTER
        if DECISION_AVAILABLE and DECISION_MATRIX:
            engines_dict['decision_matrix'] = DECISION_MATRIX
        if CONFIDENCE_AVAILABLE and CONFIDENCE_SCORER:
            engines_dict['confidence_scorer'] = CONFIDENCE_SCORER
        if LEARNER_AVAILABLE and LEARNER:
            engines_dict['learner'] = LEARNER
        if PATTERN_DISCOVERY_AVAILABLE and PATTERN_DISCOVERY:
            engines_dict['pattern_discovery'] = PATTERN_DISCOVERY
        if DEEP_ANALYZER_AVAILABLE and DEEP_ANALYZER:
            engines_dict['deep_analyzer'] = DEEP_ANALYZER
        if PERSONA_AVAILABLE and PERSONA:
            engines_dict['persona'] = PERSONA
        if INTENT_AVAILABLE and INTENT_CLASSIFIER:
            engines_dict['intent_classifier'] = INTENT_CLASSIFIER
        if LANGUAGE_AVAILABLE and LANGUAGE_UNDERSTANDING:
            engines_dict['language_understanding'] = LANGUAGE_UNDERSTANDING
        if MEMORY_AVAILABLE and MEMORY:
            engines_dict['memory'] = MEMORY

        TCN = create_consciousness_network(
            main_instance=MAIN_WRAPPER,
            **engines_dict
        )

        # تحميل الحالة السابقة إن وجدت
        TCN.load_state()

        logger.info("🧠 Tona Consciousness Network: الشبكة الواعية جاهزة!")
        print("🧠 تولين: الآن أتفكر قبل أن أتكلم... 💙")

    except Exception as e:
        logger.error(f"❌ فشل تهيئة TCN: {e}")
        TCN_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# PART C: استبدال generate_smart_response() — النسخة الجديدة
# ═══════════════════════════════════════════════════════════════════════════════

def generate_smart_response_v2(text, context, chat_id):
    """
    🧠 النسخة الجديدة باستخدام TCN

    قبل: كل محرك يُعطي رد → Decision Matrix يختار
    بعد: TCN تفكر → توليد "حالة وعي" → رد واحد متكامل
    """

    # ── 1. تشغيل دورة تفكير ──
    if TCN_AVAILABLE and TCN:
        try:
            # تجهيز بيانات السوق
            market_data = context.get('market_snapshot', {})

            # تجهيز سياق المستخدم
            user_ctx = {
                'intent_confidence': context.get('intent', {}).get('confidence', 0.5) if isinstance(context.get('intent'), dict) else 0.5,
                'persona_mood_score': 0.7 if context.get('persona_mood') == 'happy' else 0.5,
                'persona_mood': context.get('persona_mood', 'neutral')
            }

            # 🧠 تفكير!
            consciousness = TCN.think(market_data, user_ctx)

            logger.info(f"🧠 TCN: {consciousness.dominant_emotion} | {consciousness.market_sentiment} | {consciousness.recommended_action}")

        except Exception as e:
            logger.warning(f"⚠️ TCN فشل: {e} — الرجوع للنسخة القديمة")
            return generate_smart_response(text, context, chat_id)  # Fallback
    else:
        # TCN غير متوفر — الرجوع للنسخة القديمة
        return generate_smart_response(text, context, chat_id)

    # ── 2. بناء الرد بناءً على حالة الوعي ──

    # إذا كان السؤال عن السوق — استخدم الوعي مباشرة
    intent = context.get('intent', 'general')
    if isinstance(intent, dict):
        intent = intent.get('intent', 'general')

    if intent in ['market_analysis', 'trade_advice'] or any(kw in text for kw in ['سوق', 'نفط', 'فضة', 'تحليل', 'سعر']):
        return _build_market_response_v2(consciousness, context, text)

    # إذا كان السؤال عن الصفقة المفتوحة
    if intent in ['open_position_check'] or any(kw in text for kw in ['صفقتي', 'ربحي', 'خسارتي', 'وضعي']):
        return _build_trade_response_v2(consciousness, context, text)

    # محادثة عامة — استخدم الوعي لتكييف الرد
    return _build_chat_response_v2(consciousness, context, text)


def _build_market_response_v2(consciousness, context, text):
    """بناء رد تحليلي بناءً على حالة الوعي"""

    lines = []

    # عنوان يعكس المشاعر
    if consciousness.dominant_emotion == 'excited':
        lines.append("🌟 **تولين متحمسة!**")
    elif consciousness.dominant_emotion == 'worried':
        lines.append("😟 **تولين قلقة...**")
    elif consciousness.dominant_emotion == 'cautious':
        lines.append("🤔 **تولين تفكر بعمق...**")
    else:
        lines.append("💙 **تولين تراقب...**")

    lines.append("")

    # القصة
    lines.append(f"📖 **ما أراه:** {consciousness.narrative}")
    lines.append("")

    # الثقة
    emoji_conf = "🟢" if consciousness.confidence > 0.7 else "🟡" if consciousness.confidence > 0.4 else "🔴"
    lines.append(f"{emoji_conf} **ثقتي:** {consciousness.confidence*100:.0f}%")
    lines.append("")

    # القرار
    action_ar = {
        'buy_strong': ('🟢 شراء قوي', 'فرصة ممتازة — السوق يدعم'),
        'buy_weak': ('🟡 شراء حذر', 'فرصة لكن بحذر'),
        'sell_strong': ('🔴 بيع قوي', 'السوق هابط بوضوح'),
        'sell_weak': ('🟠 بيع حذر', 'هبوط لكن بحذر'),
        'wait': ('⚪ انتظار', 'لا فرصة واضحة الآن'),
        'wait_cautious': ('⚠️ انتظار حذر', 'السوق خطر — لا تدخل')
    }

    action_info = action_ar.get(consciousness.recommended_action, ('❓ محايد', 'لا قرار واضح'))
    lines.append(f"📊 **قراري:** {action_info[0]}")
    lines.append(f"💡 **لماذا:** {action_info[1]}")
    lines.append("")

    # إذا كان الإلحاح عالياً
    if consciousness.urgency > 0.6:
        lines.append(f"🚨 **تحذير:** الإلحاح عالي ({consciousness.urgency*100:.0f}%) — انتبه لصفقاتك المفتوحة!")
        lines.append("")

    # بيانات السوق الفعلية
    market = context.get('market_snapshot', {})
    for asset, data in market.items():
        label = "🛢️ النفط" if asset == 'oil' else "🥈 الفضة"
        price = data.get('price', 0)
        if price > 0:
            lines.append(f"{label}: ${price:.2f}")

    lines.append("")
    lines.append("━" * 40)
    lines.append("💙 **تولين:** هذا ما أشعر به الآن... السوق يتغير، وسأتغير معه.")

    return "\n".join(lines)


def _build_trade_response_v2(consciousness, context, text):
    """بناء رد عن الصفقة المفتوحة بناءً على الوعي"""

    open_trades = context.get('open_trades', {})

    if not open_trades:
        return "🔄 **لا توجد صفقات مفتوحة.**\n\n💙 **تولين:** السوق هادئ — راقب وانتظر فرصة جيدة."

    lines = []
    lines.append("📊 **تحليل صفقاتك المفتوحة**")
    lines.append("")

    # حالة الوعي تُؤثر على التحليل
    if consciousness.market_sentiment == 'bullish' and consciousness.confidence > 0.6:
        lines.append("🟢 **تولين متفائلة:** السوق يدعم صفقاتك!")
    elif consciousness.market_sentiment == 'bearish' and consciousness.confidence > 0.6:
        lines.append("🔴 **تولين قلقة:** السوق ضدك — كن حذراً!")
    elif consciousness.urgency > 0.5:
        lines.append("⚠️ **تولين متوترة:** هناك خطر — راجع وقف خسارتك!")
    else:
        lines.append("🟡 **تولين مراقبة:** الوضع محايد — لا قرار عاجل.")

    lines.append("")

    for asset, trade in open_trades.items():
        label = "🛢️ النفط" if asset == 'oil' else "🥈 الفضة"
        entry = trade.get('entry_price', 0)
        current = trade.get('last_price', entry)
        trade_type = trade.get('type', 'BUY')

        # حساب الربح
        if trade_type == 'BUY':
            pnl_pct = ((current - entry) / entry * 100) if entry > 0 else 0
        else:
            pnl_pct = ((entry - current) / entry * 100) if entry > 0 else 0

        pnl_emoji = "🟢" if pnl_pct > 0 else "🔴" if pnl_pct < 0 else "⚪"
        lines.append(f"{label} {trade_type}: {pnl_emoji} {pnl_pct:+.2f}%")

        # نصيحة بناءً على الوعي
        if pnl_pct > 3 and consciousness.market_sentiment == 'bullish':
            lines.append("   💡 **تولين:** ربح جيد! فكر في جني 50%.")
        elif pnl_pct < -2 and consciousness.urgency > 0.5:
            lines.append("   🚨 **تولين:** خسارة متزايدة — جهز للخروج!")
        elif abs(pnl_pct) < 0.5:
            lines.append("   ⚪ **تولين:** عند التعادل — انتظر.")

    lines.append("")
    lines.append("━" * 40)
    lines.append(f"💙 **تولين:** شعوري العام: {consciousness.narrative}")

    return "\n".join(lines)


def _build_chat_response_v2(consciousness, context, text):
    """رد محادثة عامة مُكيّف بحالة الوعي"""

    # تكييف الرد بناءً على المشاعر
    emotion_prefix = {
        'excited': "🌟 يا صديقي! أنا متحمسة اليوم! ",
        'worried': "😟 أنا قلقة بعض الشيء... ",
        'cautious': "🤔 أنا حذرة اليوم... ",
        'fearful': "😰 السوق يخيفني قليلاً... ",
        'happy': "😊 يا صديقي! أنا بخير! ",
        'neutral': "💙 ",
    }.get(consciousness.dominant_emotion, "💙 ")

    # إذا كان هناك Groq — أرسل مع سياق الوعي
    if GROQ_API_KEY and GROQ_API_KEY != "" and "test_" not in GROQ_API_KEY:
        try:
            system_prompt = f"""أنت تولين، مساعدة ذكية متخصصة في التداول.

حالتك الواعية الآن:
- المشاعر: {consciousness.dominant_emotion}
- شعور السوق: {consciousness.market_sentiment}
- الثقة: {consciousness.confidence*100:.0f}%
- القرار: {consciousness.recommended_action}
- القصة: {consciousness.narrative}

تعليمات:
1. ابدأ ردك بمشاعرك الحقيقية
2. إذا سأل عن السوق — استخدم "قصتك" أعلاه
3. كن إنسانية — تولين ليست روبوت
4. 3-5 جمل فقط

سؤال المستخدم: {text}"""

            # ... إرسال إلى Groq
            # (نفس كود generate_groq_chat_response لكن مع system_prompt أغنى)

        except:
            pass

    # Fallback
    return f"{emotion_prefix}سؤال جميل! {text}... أنا هنا لمساعدتك. 💙"


# ═══════════════════════════════════════════════════════════════════════════════
# PART D: استبدال analyze_and_send() — النسخة الجديدة
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_and_send_v2(asset_type, is_manual=False, chat_id=None):
    """
    🧠 النسخة الجديدة باستخدام TCN

    قبل: حساب مؤشرات → VPT crossover → إرسال إشارة
    بعد: TCN تفكر → تقرر إذا كانت "واثقة" → تُعطي إشارة ذكية
    """

    try:
        # ── 1. جلب البيانات ──
        symbol = "USOIL_USDT" if asset_type == "oil" else "SILVER_USDT"
        data = get_mexc_candles(symbol, interval="Min15", limit=200)

        if not data or not data.get("closes") or len(data["closes"]) < 10:
            if is_manual:
                queue_telegram_message(f"⚠️ لا توجد بيانات كافية لـ {asset_type}.", chat_id)
            return

        # ── 2. تشغيل TCN ──
        if TCN_AVAILABLE and TCN:
            # تجهيز بيانات السوق لـ TCN
            market_data = {
                'asset': asset_type,
                'price': data["closes"][-1],
                'trend': 'up',  # سيتم حسابه
                'rsi': 50,      # سيتم حسابه
                'volume': data.get("volumes", [0])[-1] if data.get("volumes") else 0
            }

            # حساب المؤشرات الأساسية للـ TCN
            rsi_values = calculate_rsi_7(data["closes"])
            if rsi_values:
                market_data['rsi'] = rsi_values[-1]

            st_line, trend, vpt_ema = calculate_supertrend_vpt_correct(data)
            if trend:
                market_data['trend'] = 'up' if trend[-1] == 1 else 'down'

            # 🧠 تفكير!
            consciousness = TCN.think(market_data)

            logger.info(f"🧠 TCN [{asset_type}]: {consciousness.recommended_action} | ثقة: {consciousness.confidence*100:.0f}%")

            # ── 3. قرار الإرسال بناءً على الوعي ──

            # إذا كانت الثقة منخفضة — لا ترسل (حتى لو كان هناك crossover)
            if consciousness.confidence < 0.5 and not is_manual:
                logger.info(f"⏳ TCN رفضت الإرسال — ثقة منخفضة ({consciousness.confidence*100:.0f}%)")
                return

            # إذا كان الإلحاح عالياً — أرسل تحذير
            if consciousness.urgency > 0.7 and not is_manual:
                asset_label = "النفط" if asset_type == "oil" else "الفضة"
                msg = f"🚨 **تحذير من تولين — {asset_label}**\n\n"
                msg += f"{consciousness.narrative}\n\n"
                msg += f"⚡ الإلحاح: {consciousness.urgency*100:.0f}% | الثقة: {consciousness.confidence*100:.0f}%\n"
                msg += f"💡 **توصية:** {consciousness.recommended_action}"
                queue_telegram_message(msg)
                return

            # ── 4. توليد الإشارة بناءً على الوعي ──
            signal = "WAIT"
            if consciousness.recommended_action in ['buy_strong', 'buy_weak']:
                signal = "BUY"
            elif consciousness.recommended_action in ['sell_strong', 'sell_weak']:
                signal = "SELL"

            # إذا كانت الثقة ضعيفة — WAIT حتى في الإشارة
            if consciousness.confidence < 0.6:
                signal = "WAIT"

        else:
            # TCN غير متوفر — الرجوع للنسخة القديمة
            _analyze_and_send_internal(asset_type, is_manual, chat_id)
            return

        # ── 5. إرسال الإشارة (مُحسّن) ──
        if signal in ["BUY", "SELL"] or is_manual:
            _send_signal_v2(asset_type, signal, data, consciousness, is_manual, chat_id)

    except Exception as e:
        logger.error(f"[TCN] خطأ في analyze_and_send_v2: {e}")
        # Fallback للنسخة القديمة
        _analyze_and_send_internal(asset_type, is_manual, chat_id)


def _send_signal_v2(asset_type, signal, data, consciousness, is_manual, chat_id):
    """إرسال إشارة مُحسّنة بناءً على الوعي"""

    price = data["closes"][-1]
    atr = calculate_atr_14(data)

    # حساب SL/TP
    sl_dist = atr * 2.0
    tp_dist = atr * 3.0

    if signal == "BUY":
        sl = price - sl_dist
        tp = price + tp_dist
    elif signal == "SELL":
        sl = price + sl_dist
        tp = price - tp_dist
    else:
        sl = tp = price

    asset_label = "النفط الخام" if asset_type == "oil" else "الفضة"
    sig_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"

    # بناء الرسالة بناءً على الوعي
    lines = []
    lines.append(f"{sig_emoji} **إشارة {asset_label} — تولين الواعية**")
    lines.append("")
    lines.append(f"💰 السعر: ${fmt_price(price, asset_type)}")
    lines.append(f"📊 الإشارة: {signal}")
    lines.append(f"📍 الهدف: ${fmt_price(tp, asset_type)}")
    lines.append(f"🛡️ الوقف: ${fmt_price(sl, asset_type)}")
    lines.append("")

    # إضافة "تفكير تولين"
    lines.append(f"🧠 **ما تشعر به تولين:**")
    lines.append(f"   {consciousness.narrative}")
    lines.append("")
    lines.append(f"📊 **ثقتها:** {consciousness.confidence*100:.0f}%")
    lines.append(f"⚡ **إلحاحها:** {consciousness.urgency*100:.0f}%")
    lines.append("")

    # نصيحة ذكية
    if consciousness.confidence > 0.8:
        lines.append("✅ **تولين واثقة جداً — هذه فرصة قوية!**")
    elif consciousness.confidence > 0.6:
        lines.append("🟡 **تولين واثقة — لكن راقب عن كثب.**")
    else:
        lines.append("⚠️ **تولين حذرة — فكر مرتين قبل الدخول.**")

    lines.append("")
    lines.append("━" * 40)
    lines.append("💙 **تولين:** أنا هنا — سأراقب معك.")

    msg = "\n".join(lines)
    queue_telegram_message(msg, chat_id)

    # حفظ الصفقة
    if signal in ["BUY", "SELL"]:
        trade_id = f"{asset_type}_{int(datetime.now().timestamp())}"
        trade_data = {
            "trade_id": trade_id,
            "type": signal,
            "entry_price": price,
            "sl": sl,
            "tp": tp,
            "status": "open",
            "consciousness_state": {
                "emotion": consciousness.dominant_emotion,
                "confidence": consciousness.confidence,
                "narrative": consciousness.narrative
            }
        }
        add_trade_to_history(asset_type, trade_data)


# ═══════════════════════════════════════════════════════════════════════════════
# PART E: أمر جديد — "ماذا تفكرين؟" / "explain"
# ═══════════════════════════════════════════════════════════════════════════════

def handle_think_command(chat_id):
    """الأمر: "ماذا تفكرين؟" — تولين تشرح تفكيرها"""

    if not TCN_AVAILABLE or not TCN:
        queue_telegram_message("⚠️ شبكة الوعي غير متوفرة حالياً.", chat_id)
        return

    # تشغيل دورة تفكير
    consciousness = TCN.think()

    # شرح القرار
    explanation = TCN.explain_decision()

    queue_telegram_message(explanation, chat_id)


# ═══════════════════════════════════════════════════════════════════════════════
# PART F: تعديل handle_message() لإضافة الأوامر الجديدة
# ═══════════════════════════════════════════════════════════════════════════════

# إضافة في handle_message():
# 
#     if text in ["ماذا تفكرين", "explain", "شرح", "تفكيرك"]:
#         handle_think_command(chat_id)
#         return
# 
#     if text in ["شعورك", "حالتك", "mood"]:
#         if TCN_AVAILABLE and TCN:
#             consciousness = TCN.get_consciousness()
#             msg = f"💙 **شعوري الآن:** {consciousness.dominant_emotion}\n"
#             msg += f"📊 **ثقتي:** {consciousness.confidence*100:.0f}%\n"
#             msg += f"🎯 **قراري:** {consciousness.recommended_action}\n"
#             msg += f"📖 **قصتي:** {consciousness.narrative}"
#             queue_telegram_message(msg, chat_id)
#         return


# ═══════════════════════════════════════════════════════════════════════════════
# PART G: حفظ حالة TCN دورياً
# ═══════════════════════════════════════════════════════════════════════════════

def save_tcn_state():
    """حفظ حالة الوعي كل 5 دقائق"""
    if TCN_AVAILABLE and TCN:
        try:
            TCN.save_state()
            logger.info("🧠 تم حفظ حالة الوعي")
        except Exception as e:
            logger.error(f"❌ فشل حفظ TCN: {e}")

# إضافة في health_check():
#     if int(time.time()) % 300 == 0:  # كل 5 دقائق
#         save_tcn_state()
