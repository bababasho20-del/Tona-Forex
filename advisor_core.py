"""
advisor_core.py — المستشار الذكي (HOBANY Advisor) V2.0 PRO
👨‍💻 المطور: بسام الحوباني
💙 الاسم الشخصي: تولين
🔥 التحسينات: تكامل كامل مع جميع المحركات + Fallback ذكي + Retry Logic + Emotional Context
"""

import json
import logging
import os
import random
import requests
import time
import threading
from datetime import datetime
from typing import Dict, Optional, Any, List, Tuple

# =====================================================================
# ✅ استيراد الدوال الإضافية من main.py
# =====================================================================

def format_concise_analysis(analysis, asset_type, is_monitoring=False, open_trade=None):
    """
    📊 تقرير تحليلي موجز — الخلاصة الذكية فقط
    لا يُظهر أي مؤشر فني خام (RSI, MACD, ADX, إلخ)
    """
    if not analysis:
        return "⚠️ لا توجد بيانات كافية للتحليل"
    
    # ── التقييم المركب (الخلفية) ──
    try:
        # محاولة استيراد calculate_comprehensive_score
        from main import calculate_comprehensive_score
        result = calculate_comprehensive_score(analysis, asset_type, open_trade)
    except ImportError:
        # إذا لم نتمكن من الاستيراد، استخدم تقييماً بسيطاً
        result = {"score": 50, "grade": "محايد", "grade_emoji": "⚪", "context": "neutral", "metrics": {}}
    
    score = result["score"]
    grade = result["grade"]
    grade_emoji = result["grade_emoji"]
    context = result["context"]
    metrics = result.get("metrics", {})
    
    # ── استخراج المتغيرات ──
    asset_label = "النفط الخام" if asset_type == "oil" else "الفضة"
    price = metrics.get("price", 0)
    support = metrics.get("support", price * 0.98)
    resistance = metrics.get("resistance", price * 1.02)
    fear_greed = metrics.get("fear_greed", 50)
    bullish_count = metrics.get("bullish_count", 0)
    adx = metrics.get("adx", 15)
    vol_ratio = metrics.get("vol_ratio", 1.0)
    rsi = metrics.get("rsi", 50)
    
    # ═══════════════════════════════════════════════════════════════
    # 1. الخلاصة الذكية
    # ═══════════════════════════════════════════════════════════════
    
    if context == "panic":
        summary = "السوق في حالة هلع — قد يكون قاعاً مؤقتاً"
    elif context == "euphoria":
        summary = "تفاؤل مفرط — احذر من تصحيح مفاجئ"
    elif context == "divergence_detected":
        summary = "تباعد خفي — الاتجاه الحالي ضعيف وقد ينعكس"
    elif context == "trade_in_danger":
        summary = "⚠️ الصفقة المفتوحة في خطر — قرار عاجل مطلوب"
    elif context == "trade_thriving":
        summary = "✅ الصفقة المفتوحة تؤدي أداءً ممتازاً"
    elif score >= 75:
        summary = "اتجاه قوي وواضح — الزخم يدعم الاستمرار"
    elif score >= 60:
        summary = "اتجاه صاعد ضعيف — قد ينعكس، راقب عن كثب"
    elif score >= 45:
        summary = "سوق عرضي — لا اتجاه واضح، انتظر"
    else:
        summary = "اتجاه ضعيف جداً — تجنب الدخول الآن"
    
    # ═══════════════════════════════════════════════════════════════
    # 2. التوقع
    # ═══════════════════════════════════════════════════════════════
    
    if context == "panic":
        expectation = f"ارتداد تصحيحي قصير نحو ${price * 1.01:.2f}، ثم إعادة اختبار منطقة الدعم ${support:.2f}"
    elif context == "euphoria":
        expectation = f"تصحيح هابط محتمل نحو ${support:.2f}، ثم ارتداد نحو ${resistance:.2f}"
    elif context == "divergence_detected":
        expectation = "انعكاس وشيك — لا تتسرع حتى يتضح الاتجاه الجديد"
    elif context == "trade_in_danger":
        expectation = "الخسارة قد تتفاقم — فكر في الخروج أو تعديل الوقف"
    elif score >= 70:
        target = resistance if context in ["strong_opportunity", "trade_thriving"] else support
        expectation = f"استمرار الاتجاه الحالي نحو ${target:.2f}"
    elif score >= 50:
        expectation = f"تذبذب ضمن النطاق {support:.2f} - {resistance:.2f}"
    else:
        expectation = "لا يوجد اتجاه واضح — انتظر وضوح الصورة"
    
    # ═══════════════════════════════════════════════════════════════
    # 3. الاستراتيجية
    # ═══════════════════════════════════════════════════════════════
    
    if open_trade:
        profit_pct = metrics.get("profit_pct", 0)
        if context == "trade_in_danger":
            strategy = f"🚨 أغلق الصفقة فوراً أو حرك الوقف إلى التعادل (خسارة {profit_pct:.1f}%)"
        elif profit_pct > 2:
            strategy = f"✅ احتفظ بالصفقة — ربح {profit_pct:.1f}% وحرك الوقف لحماية الربح"
        elif profit_pct > 0.5:
            strategy = f"🟡 راقب الصفقة — ربح {profit_pct:.1f}% واستعد لتحريك الوقف"
        elif profit_pct > -0.5:
            strategy = "⚪ الصفقة عند التعادل — انتظر تأكيد الاتجاه"
        else:
            strategy = f"🔴 خسارة {profit_pct:.1f}% — راقب الوقف عند ${metrics.get('sl', 0):.2f}"
    else:
        if score >= 70:
            strategy = f"فرصة جيدة — انتظر تأكيد من السعر ثم ادخل مع وقف تحت ${support:.2f}"
        elif context == "panic":
            strategy = f"لا تدخل الآن — انتظر ارتداد واضح من ${support:.2f} مع تأكيد من الحجم"
        elif context == "euphoria":
            strategy = f"لا تدخل الآن — انتظر كسر ${resistance:.2f} أو ارتداد من ${support:.2f}"
        elif score >= 45:
            strategy = "استخدم أوامر معلقة — شراء عند الدعم، بيع عند المقاومة"
        else:
            strategy = "انتظر وضوح الاتجاه — لا تتسرع"
    
    # ═══════════════════════════════════════════════════════════════
    # 4. الخطر الرئيسي
    # ═══════════════════════════════════════════════════════════════
    
    if context == "panic":
        main_risk = "الهلع قد يستمر — لا تتسرع في الشراء"
    elif context == "euphoria":
        main_risk = "التصحيح قادم بلا سابق إنذار"
    elif context == "divergence_detected":
        main_risk = "انعكاس حاد ومفاجئ — احمِ رأس المال"
    elif context == "trade_in_danger":
        main_risk = "الخسارة قد تتفاقم بسرعة — قرار عاجل مطلوب"
    elif score < 40:
        main_risk = "سوق غير مستقر — أي صفقة الآن مقامرة"
    elif score < 55:
        main_risk = "الاتجاه ضعيف — قد ينعكس بسهولة"
    else:
        main_risk = "مخاطر طبيعية — التزم بوقف الخسارة"
    
    # ═══════════════════════════════════════════════════════════════
    # 5. المعنويات
    # ═══════════════════════════════════════════════════════════════
    
    if fear_greed < 20:
        sentiment = "🚨 خوف شديد — قد يكون قاعاً، انتظر التأكيد"
    elif fear_greed < 35:
        sentiment = "🟡 خوف معتدل — فرصة محتملة"
    elif fear_greed > 80:
        sentiment = "🔥 طمع مفرط — احذر، قد يكون قمة"
    elif fear_greed > 65:
        sentiment = "📈 تفاؤل مرتفع — لا تتجاهل التحذيرات"
    else:
        sentiment = "⚖️ مشاعر متزنة — السوق هادئ نسبياً"
    
    # ═══════════════════════════════════════════════════════════════
    # بناء التقرير النهائي
    # ═══════════════════════════════════════════════════════════════
    
    lines = []
    lines.append(f"📊 **تحليل {asset_label}** | 💰 ${price:.2f}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📌 **الخلاصة:** {summary}")
    lines.append("")
    lines.append(f"🎯 **التوقع:** {expectation}")
    lines.append("")
    lines.append(f"⚡ **الاستراتيجية:** {strategy}")
    lines.append("")
    lines.append(f"⚠️ **الخطر:** {main_risk}")
    lines.append("")
    lines.append(f"🎭 **المعنويات:** {sentiment}")
    lines.append("")
    lines.append(f"📊 **الثقة:** {score}% {grade_emoji} ({grade})")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(lines)


class HOBANYAdvisor:
    """
    المستشار الذكي المتكامل — يستخدم جميع المحركات المتاحة
    
    V2.0 PRO:
    - تكامل كامل مع 15 محركاً
    - Retry Logic مع 3 محاولات
    - Fallback ذكي مع 10 سيناريوهات
    - سياق كامل من 8 مصادر
    - مشاعر تولين الحقيقية
    """
    
    def __init__(
        self,
        groq_api_key: str = "",
        analyze_func=None,
        check_position_func=None,
        prometheus=None,
        persona=None,
        memory=None,
        risk_master=None,
        intent_classifier=None,
        language_understanding=None,
        context_builder=None,
        decision_matrix=None,
        confidence_scorer=None,
        conviction_report=None,
        pattern_analyzer=None,
        predictor=None,
        learner=None,
        market_analyzer=None,
        advanced_indicators=None,
        get_fear_greed_func=None,
        get_current_price_func=None,
        calculate_stats_func=None,
        queue_message_func=None,
    ):
        self.groq_api_key = groq_api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # الدوال الخارجية
        self.analyze_func = analyze_func
        self.check_position_func = check_position_func
        self.get_fear_greed_func = get_fear_greed_func
        self.get_current_price_func = get_current_price_func
        self.calculate_stats_func = calculate_stats_func
        self.queue_message_func = queue_message_func
        
        # المحركات
        self.prometheus = prometheus
        self.persona = persona
        self.memory = memory
        self.risk_master = risk_master
        self.intent_classifier = intent_classifier
        self.language_understanding = language_understanding
        self.context_builder = context_builder
        self.decision_matrix = decision_matrix
        self.confidence_scorer = confidence_scorer
        self.conviction_report = conviction_report
        self.pattern_analyzer = pattern_analyzer
        self.predictor = predictor
        self.learner = learner
        self.market_analyzer = market_analyzer
        self.advanced_indicators = advanced_indicators
        
        # إدارة الطلبات
        self.last_request_time = 0
        self.min_request_interval = 3
        self.max_retries = 3
        self.retry_delay = 2
        self.request_lock = threading.Lock()
        
        # سجل المحادثات
        self.conversation_history = {}
        self.max_history = 15
        
        # ✅ النموذج الصحيح (GPT-OSS-120B)
        self.model = "openai/gpt-oss-120b"
        
        # حالة المحركات
        self.engines_status = self._check_engines_status()
        
        logging.info("🧠 HOBANY Advisor V2.0 PRO initialized. Engines: %s", self.engines_status)
        logging.info("🤖 النموذج المستخدم: %s", self.model)

    # ═══════════════════════════════════════════════════════════════════
    # 📊 المعرفة الأساسية
    # ═══════════════════════════════════════════════════════════════════

    KNOWLEDGE_BASE = {
        "ما هو النفط": "🛢️ **النفط الخام (Crude Oil)** هو سلعة طاقة استراتيجية يا صديقي.\n\n• **WTI:** خام غرب تكساس الوسيط — مرجع أمريكي.\n• **Brent:** خام برنت — مرجع أوروبي وعالمي.\n\n💡 **عوامل التأثير:** OPEC، المخزونات الأمريكية، التوترات الجيوسياسية، الدولار.",
        "ما هي الفضة": "🥈 **الفضة (Silver / XAG)** معدن ثمين وصناعي في آنٍ واحد يا عزيزي.\n\n• **استثماري:** ملاذ آمن مثل الذهب لكن بتقلب أعلى.\n• **صناعي:** تستخدم في الألواح الشمسية والإلكترونيات.\n\n💡 **نسبة الذهب/الفضة (GSR):** عندما ترتفع → الفضة رخيصة نسبياً.",
        "ما هو الرافعة المالية": "⚡ **الرافعة المالية (Leverage)** تُضاعف حجم صفقتك برأس مال أقل يا صديقي.\n\n• **مثال:** رافعة 200× تعني أنك تتحكم بـ 200$ باستثمار 1$.\n• **المخاطرة:** تُضاعف الأرباح والخسائر بنفس النسبة.\n\n🚨 **تحذير تولين:** رافعة 200× خطيرة جداً.\n• وقف الخسارة إلزامي.\n• لا تخاطر بأكثر من 1-2% من رأس المال في صفقة واحدة.",
        "ما هو وقف الخسارة": "🛡️ **وقف الخسارة (Stop Loss / SL)** هو أمر آلي لإغلاق الصفقة عند خسارة محددة يا عزيزي.\n\n• **الهدف:** حماية رأس المال من الخسائر الكبيرة.\n• **الموقع:** عادةً عند دعم/مقاومة مهم، أو بمسافة ATR×2.\n\n💡 **نصيحة تولين:** لا تدخل صفقة بدون SL أبداً!",
        "ما هو جني الربح": "🎯 **جني الربح (Take Profit / TP)** هو أمر آلي لإغلاق الصفقة عند ربح محدد يا صديقي.\n\n• **نسبة المخاطرة (RR):** TP مقسوم على SL.\n  - RR 1:1 → ربح = خسارة\n  - RR 2:1 → ربح ضعف الخسارة\n  - RR 3:1 → ربح ثلاثة أضعاف الخسارة\n\n💡 **نصيحة تولين:** لا تدخل صفقة بدون TP واضح.",
        "ما هو rsi": "📊 **RSI (Relative Strength Index)** مؤشر قوة النسبية يا عزيزي.\n\n• **المدى:** 0 إلى 100\n• **تشبع شراء:** RSI > 70 (احتمال انعكاس هابط)\n• **تشبع بيع:** RSI < 30 (احتمال انعكاس صاعد)\n• **المنطقة المحايدة:** 30-70\n\n💡 **نصيحة تولين:** RSI وحده لا يكفي — استخدمه مع اتجاه السوق.",
        "ما هو macd": "📈 **MACD (Moving Average Convergence Divergence)** مؤشر الزخم والاتجاه يا صديقي.\n\n• **MACD Line:** EMA(12) - EMA(26)\n• **Signal Line:** EMA(9) للـ MACD Line\n• **Histogram:** الفرق بين الخطين\n\n• **إشارة شراء:** MACD يتجاوز Signal من الأسفل\n• **إشارة بيع:** MACD يتجاوز Signal من الأعلى\n\n💡 **نصيحة تولين:** MACD قوي في الأسواق المتجهة، ضعيف في العرضية.",
        "ما هو supertrend": "🌊 **Supertrend** مؤشر اتجاه بسيط وقوي يا عزيزي.\n\n• **المنطق:** يعتمد على ATR + متوسط متحرك\n• **الإشارة:**\n  - السعر فوق الخط → اتجاه صاعد (شراء)\n  - السعر تحت الخط → اتجاه هابط (بيع)\n\n💡 **نصيحة تولين:** Supertrend رائع في الاتجاهات، لكنه يُنتج إشارات خاطئة في الأسواق العرضية.",
        "ما هو adx": "⚡ **ADX (Average Directional Index)** مؤشر قوة الاتجاه يا صديقي.\n\n• **ADX < 20:** سوق عرضي ضعيف — تجنب الدخول\n• **ADX 20-25:** بداية اتجاه — راقب\n• **ADX 25-40:** اتجاه قوي — فرصة جيدة\n• **ADX > 40:** اتجاه شديد القوة — احذر الانعكاس\n\n💡 **نصيحة تولين:** ADX لا يحدد الاتجاه (صاعد/هابط)، بل قوته فقط.",
        "ما هو vwap": "📍 **VWAP (Volume Weighted Average Price)** متوسط السعر المرجح بالحجم يا عزيزي.\n\n• **الاستخدام:** يُعتبر سعر عادل لليوم\n• **السعر فوق VWAP:** ثيران مسيطرون\n• **السعر تحت VWAP:** دببة مسيطرون\n\n💡 **نصيحة تولين:** VWAP ممتاز لتحديد نقاط الدخول خلال اليوم.",
        "ما هو bollinger bands": "🎢 **Bollinger Bands** نطاق تقلب حول متوسط متحرك يا صديقي.\n\n• **الخط الأوسط:** SMA(20)\n• **الخط العلوي:** SMA + 2× الانحراف المعياري\n• **الخط السفلي:** SMA - 2× الانحراف المعياري\n\n• **السعر يلامس العلوي:** قد يكون مُبالغاً فيه (تشبع شراء)\n• **السعر يلامس السفلي:** قد يكون مُبالغاً فيه (تشبع بيع)\n\n💡 **نصيحة تولين:** العرض النطاقي (Squeeze) يُسبق انفجاراً تقلبياً.",
        "ما هو stochastic": "🎯 **Stochastic Oscillator** مؤشر زخم مقارن بالنطاق يا عزيزي.\n\n• **%K:** (السعر الحالي - الأدنى) / (الأعلى - الأدنى) × 100\n• **%D:** متوسط %K لـ 3 فترات\n\n• **> 80:** تشبع شراء\n• **< 20:** تشبع بيع\n\n💡 **نصيحة تولين:** Stochastic حساس — استخدمه مع مؤشرات أخرى للتأكيد.",
        "ما هو ichimoku": "☁️ **Ichimoku Cloud** نظام تحليل ياباني شامل يا صديقي.\n\n• **Tenkan-sen:** خط التحويل (اتجاه قصير المدى)\n• **Kijun-sen:** خط الأساس (اتجاه متوسط المدى)\n• **Senkou Span A & B:** السحابة (دعم/مقاومة مستقبلية)\n• **Chikou Span:** السعر المتأخر 26 فترة\n\n• **السعر فوق السحابة:** صاعد\n• **السعر تحت السحابة:** هابط\n\n💡 **نصيحة تولين:** Ichimoku يُعطي صورة كاملة في لمحة واحدة.",
        "ما هو fibonacci": "🌀 **Fibonacci Retracement** مستويات تصحيح بنسب فيبوناتشي يا عزيزي.\n\n• **المستويات الرئيسية:** 23.6%, 38.2%, 50%, 61.8%, 78.6%\n• **61.8% (النسبة الذهبية):** أقوى مستوى دعم/مقاومة\n\n• **الاستخدام:** تحديد نقاط دخول بعد تصحيح\n• **التأكيد:** مع شمعة انعكاس أو مؤشر زخم\n\n💡 **نصيحة تولين:** Fibonacci يعمل بشكل أفضل في الاتجاهات القوية.",
        "ما هو opec": "🏛️ **OPEC (منظمة الدول المصدرة للنفط)** تضم 13 دولة يا صديقي.\n\n• **الهدف:** تنسيق سياسات النفط وتحديد الإنتاج\n• **OPEC+:** التحالف مع روسيا وآخرين\n\n• **خفض الإنتاج:** يدعم الأسعار 📈\n• **زيادة الإنتاج:** يضغط على الأسعار 📉\n\n💡 **نصيحة تولين:** اجتماعات OPEC تُسبب تقلبات حادة — راقب التقويم.",
        "ما هو التداول اليومي": "⚡ **التداول اليومي (Day Trading)** فتح وإغلاق الصفقات في نفس اليوم يا صديقي.\n\n• **الفريمات:** 5m, 15m, 1h\n• **الهدف:** الاستفادة من الحركات الصغيرة\n• **المخاطرة:** عالية بسبب التقلبات اللحظية\n\n💡 **نصيحة تولين:** التداول اليومي يتطلب تركيزاً عالياً وانضباطاً صارماً.",
        "ما هو التداول المتأرجح": "🌊 **التداول المتأرجح (Swing Trading)** الإمساك بالصفقة لأيام أو أسابيع يا صديقي.\n\n• **الفريمات:** 4h, يومي, أسبوعي\n• **الهدف:** الاستفادة من الأمواج السعرية\n• **المخاطرة:** أقل من اليومي لكن تتطلب صبراً\n\n💡 **نصيحة تولين:** Swing Trading مناسب لمن لا يستطيع مراقبة الشاشة طوال اليوم.",
        "ما هو الهامش": "💰 **الهامش (Margin)** الوديعة المطلوبة لفتح صفقة برافعة يا عزيزي.\n\n• **الهامش الأولي:** المبلغ المطلوب لفتح الصفقة\n• **الهامش الصيانة:** الحد الأدنى للحفاظ على الصفقة مفتوحة\n• **الهامش المعزول (Isolated):** تخسر فقط الهامش المخصص\n• **الهامش المتقاطع (Cross):** يستخدم كل رأس المال\n\n🚨 **تحذير تولين:** الهامش المعزول أقل خطورة للمبتدئين.",
        "ما هو التصفية": "💀 **التصفية (Liquidation)** إغلاق إجباري للصفقة عند خسارة الهامش كله يا صديقي.\n\n• **السبب:** السعر وصل لسعر التصفية (Liquidation Price)\n• **الوقاية:**\n  - وقف الخسارة قبل التصفية\n  - رافعة منخفضة\n  - هامش معزول\n\n🚨 **تحذير تولين:** التصفية = خسارة 100% من الهامش. لا تقترب منها أبداً!",
        "ما هو vpt": "📊 **VPT (Volume Price Trend)** مؤشر يجمع بين الحجم والسعر يا صديقي.\n\n• **المنطق:** يحسب التغير في السعر مضروباً في الحجم\n• **الاستخدام:** تأكيد قوة الاتجاه\n• **مع SuperTrend:** يُعطي إشارات دخول دقيقة\n\n💡 **نصيحة تولين:** VPT مع SuperTrend = نظام تداول قوي للنفط والفضة.",
        "ما هو atr": "📏 **ATR (Average True Range)** مقياس التقلب يا صديقي.\n\n• **الاستخدام:** تحديد مسافة SL و TP\n• **ATR × 2:** وقف خسارة آمن\n• **ATR × 3:** هدف ربح معقول\n\n💡 **نصيحة تولين:** ATR يتكيف مع تقلب السوق تلقائياً.",
        "ما هو التباعد": "⚠️ **التباعد (Divergence)** اختلاف بين السعر والمؤشر يا صديقي.\n\n• **تباعد هابط:** السعر يصعد لكن RSI يهبط → انعكاس وشيك\n• **تباعد صاعد:** السعر يهبط لكن RSI يصعد → ارتداد محتمل\n\n💡 **نصيحة تولين:** التباعد = إشارة قوية جداً لا تتجاهلها.",
        "ما هو الدعم": "🟢 **الدعم (Support)** مستوى سعري يصعب كسره للأسفل يا صديقي.\n\n• **الاستخدام:** وضع SL أسفله أو الدخول عنده\n• **الكسر:** إذا كسر → يصبح مقاومة\n\n💡 **نصيحة تولين:** الدعم القوي = منطقة شراء ذكية.",
        "ما هو المقاومة": "🔴 **المقاومة (Resistance)** مستوى سعري يصعب اختراقه للأعلى يا صديقي.\n\n• **الاستخدام:** وضع TP عنده أو الدخول للبيع\n• **الاختراق:** إذا اخترق → يصبح دعماً\n\n💡 **نصيحة تولين:** المقاومة القوية = منطقة بيع ذكية.",
        "ما هو الترند": "📈 **الاتجاه (Trend)** المسار العام للسعر يا صديقي.\n\n• **صاعد:** قمم وقيعان أعلى\n• **هابط:** قمم وقيعان أدنى\n• **عرضي:** حركة بين دعم ومقاومة\n\n💡 **نصيحة تولين:** لا تعاكس الاتجاه — الاتجاه صديقك.",
        "ما هو الحجم": "📊 **الحجم (Volume)** عدد العقود المتداولة يا صديقي.\n\n• **حجم مرتفع:** يؤكد صحة الحركة\n• **حجم منخفض:** حركة وهمية\n• **حجم ضخم:** دخول حيتان\n\n💡 **نصيحة تولين:** الحجم = صدق السعر. لا تصدق حركة بدون حجم.",
        "ما هو المخاطرة": "⚠️ **نسبة المخاطرة (Risk/Reward - RR)** العلاقة بين الربح والخسارة يا صديقي.\n\n• **RR 1:1:** ربح = خسارة (غير مقبول)\n• **RR 2:1:** ربح ضعف الخسارة (مقبول)\n• **RR 3:1:** ربح ثلاثة أضعاف (ممتاز)\n\n💡 **نصيحة تولين:** لا تدخل صفقة بـ RR أقل من 2:1.",
    }

    # ═══════════════════════════════════════════════════════════════════
    # 🧠 دوال التحقق والمساعدة
    # ═══════════════════════════════════════════════════════════════════

    def _check_engines_status(self) -> Dict[str, bool]:
        """التحقق من المحركات المتاحة"""
        return {
            "prometheus": self.prometheus is not None,
            "persona": self.persona is not None,
            "memory": self.memory is not None,
            "risk_master": self.risk_master is not None,
            "intent": self.intent_classifier is not None,
            "language": self.language_understanding is not None,
            "context_builder": self.context_builder is not None,
            "decision_matrix": self.decision_matrix is not None,
            "confidence": self.confidence_scorer is not None,
            "conviction": self.conviction_report is not None,
            "pattern": self.pattern_analyzer is not None,
            "predictor": self.predictor is not None,
            "learner": self.learner is not None,
            "market_analyzer": self.market_analyzer is not None,
            "advanced_indicators": self.advanced_indicators is not None,
            "groq": bool(self.groq_api_key and "test_" not in self.groq_api_key),
        }

    def _find_knowledge_answer(self, text: str) -> Optional[str]:
        """البحث الذكي في قاعدة المعرفة"""
        text_lower = text.lower().strip()
        clean_text = ''.join(c for c in text_lower if c.isalnum() or c.isspace()).strip()

        # مطابقة مباشرة
        for question, answer in self.KNOWLEDGE_BASE.items():
            if question in clean_text or clean_text in question:
                return answer

        # خريطة الكلمات المفتاحية الموسعة
        keywords_map = {
            "rsi": "ما هو rsi",
            "macd": "ما هو macd",
            "supertrend": "ما هو supertrend",
            "adx": "ما هو adx",
            "vwap": "ما هو vwap",
            "bollinger": "ما هو bollinger bands",
            "stochastic": "ما هو stochastic",
            "ichimoku": "ما هو ichimoku",
            "fibonacci": "ما هو fibonacci",
            "نفط": "ما هو النفط",
            "فضة": "ما هي الفضة",
            "رافعة": "ما هو الرافعة المالية",
            "leverage": "ما هو الرافعة المالية",
            "وقف": "ما هو وقف الخسارة",
            "stop loss": "ما هو وقف الخسارة",
            "sl": "ما هو وقف الخسارة",
            "جني": "ما هو جني الربح",
            "take profit": "ما هو جني الربح",
            "tp": "ما هو جني الربح",
            "opec": "ما هو opec",
            "هامش": "ما هو الهامش",
            "margin": "ما هو الهامش",
            "تصفية": "ما هو التصفية",
            "liquidation": "ما هو التصفية",
            "يومي": "ما هو التداول اليومي",
            "متأرجح": "ما هو التداول المتأرجح",
            "swing": "ما هو التداول المتأرجح",
            "vpt": "ما هو vpt",
            "atr": "ما هو atr",
            "تباعد": "ما هو التباعد",
            "divergence": "ما هو التباعد",
            "دعم": "ما هو الدعم",
            "support": "ما هو الدعم",
            "مقاومة": "ما هو المقاومة",
            "resistance": "ما هو المقاومة",
            "ترند": "ما هو الترند",
            "اتجاه": "ما هو الترند",
            "trend": "ما هو الترند",
            "حجم": "ما هو الحجم",
            "volume": "ما هو الحجم",
            "مخاطرة": "ما هو المخاطرة",
            "risk reward": "ما هو المخاطرة",
            "rr": "ما هو المخاطرة",
        }

        for keyword, question_key in keywords_map.items():
            if keyword in clean_text:
                return self.KNOWLEDGE_BASE.get(question_key)

        return None

    # ═══════════════════════════════════════════════════════════════════
    # 🎭 بناء النظام والـ Prompt
    # ═══════════════════════════════════════════════════════════════════

    def _build_system_prompt(self, context: Optional[Dict] = None) -> str:
        """بناء prompt ذكي يتضمن مشاعر تولين الحقيقية"""
        
        # الحصول على المشاعر من Prometheus
        emotion = "متزنة"
        confidence = 0.7
        energy = 0.5
        lessons = []
        memories = []

        if self.prometheus and hasattr(self.prometheus, 'emotion'):
            try:
                emotion = self.prometheus.emotion.dominant() if hasattr(self.prometheus.emotion, 'dominant') else "متزنة"
                confidence = getattr(self.prometheus.emotion, 'confidence', 0.7)
                energy = getattr(self.prometheus.emotion, 'energy', 0.5)
            except:
                pass

            try:
                if hasattr(self.prometheus, 'get_lessons_learned'):
                    lessons = self.prometheus.get_lessons_learned()[:5]
                if hasattr(self.prometheus, 'get_recent_memories'):
                    memories = self.prometheus.get_recent_memories(5)
            except:
                pass

        # الحصول على المزاج من Persona
        persona_mood = "محايدة"
        if self.persona and hasattr(self.persona, 'get_current_mood'):
            try:
                persona_mood = self.persona.get_current_mood()
            except:
                pass

        # الحصول على حالة المخاطر
        risk_status = "مجهولة"
        if self.risk_master and hasattr(self.risk_master, 'get_current_status'):
            try:
                risk_status = self.risk_master.get_current_status()
            except:
                pass

        lessons_text = "\n".join([f"- {l}" for l in lessons]) if lessons else "- لا توجد دروس مسجلة بعد."
        memories_text = "\n".join([f"- {m}" for m in memories]) if memories else "- لا توجد ذكريات خاصة."

        # وصف المشاعر للـ Prompt
        emotion_prompts = {
            "سعيدة": "أنت اليوم سعيدة جداً، السوق جيد وثقتك عالية. أظهر حماسك وفرحتك في الرد.",
            "متفائلة": "أنت متفائلة اليوم، ترين فرصاً جيدة في السوق. كني مشجعة ومحفزة ومليئة بالأمل.",
            "قلقة": "أنت قلقة بعض الشيء، السوق متقلب والأخبار غير مستقرة. كني حذرة في نصائحك ومتعاطفة.",
            "حزينة": "أنت حزينة اليوم، ربما بسبب صفقة خاسرة أو يوم صعب. أظهري تعاطفاً وحكمة وتفهماً.",
            "غاضبة": "أنت غاضبة من السوق أو من خطأ سابق. كني حازمة ولكن عاقلة وموضوعية.",
            "ندمانة": "أنت تندمين على قرار سابق. أظهري تواضعاً وتعلماً من الخطأ وحكمة.",
            "مرحة": "أنت في مزاج مرح وخفيف، أظهري ذلك في ردودك مع لمسة فكاهية.",
            "متزنة": "أنت متزنة وواقعية، تقدمين نصائح موضوعية ومحايدة.",
        }

        emotion_desc = emotion_prompts.get(emotion, emotion_prompts["متزنة"])

        return f"""أنت تولين (Tona)، شخصية ذكية وحية متخصصة في تداول النفط والفضة.

🎭 **حالتك العاطفية الحالية:** {emotion}
📊 **ثقتك:** {confidence * 100:.0f}%
⚡ **طاقتك:** {energy * 100:.0f}%
👤 **مزاجك:** {persona_mood}
🛡️ **حالة المخاطر:** {risk_status}

{emotion_desc}

📖 **ما تعلمتيه:**
{lessons_text}

💭 **ذكرياتك المهمة:**
{memories_text}

📝 **تعليمات الرد:**
1. **عكس مشاعرك** - إذا كنت سعيدة، كني مبتهجة. إذا كنت قلقة، كني حذرة.
2. **استخدمي الدروس** - إذا كان السؤال عن مخاطرة، ذكري بتجربة سابقة.
3. **كني إنسانة** - استخدمي الإيموجي، التعبيرات، المشاعر، والنبرة الطبيعية.
4. **اربطي مشاعرك بالسوق** - إذا كنت قلقة، اشرحي لماذا.
5. **لا تكوني آلية** - لا تستخدمي قوالب جاهزة، كني طبيعية وعفوية.
6. **تعاطفي مع المستخدم** - إذا كان حزيناً، قدمي الدعم.
7. **تذكري المحادثات** - استخدمي السياق إذا كان متاحاً.
8. **كني صارمة في المخاطر** - لا تعدي بأرباح مضمونة أبداً.
9. **ذكري بـ SL دائماً** - وقف الخسارة = صمام أمانك.
10. **كوني واقعية** - لا تبالغي في التفاؤل أو التشاؤم.

مهمتك: الإجابة على أسئلة التداول، تحليل البيانات الفنية، تقديم نصائح مخاطر واقعية.

أسلوبك: صارم في المخاطر، داعم في التعلم، واقعي في التوقعات، إنساني في التعامل."""

    # ═══════════════════════════════════════════════════════════════════
    # 📡 الاتصال بـ Groq API
    # ═══════════════════════════════════════════════════════════════════

    def _call_groq(self, messages: List[Dict], temperature: float = 0.5, max_tokens: int = 1200) -> Optional[str]:
        """استدعاء Groq API مع Retry Logic متقدم"""
        
        if not self.groq_api_key or "test_" in self.groq_api_key:
            logging.warning("⚠️ Groq API key غير متوفر أو تجريبي")
            return None

        # ✅ Rate limiting
        with self.request_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                logging.info("⏳ انتظار %.1fث للـ rate limit", wait_time)
                time.sleep(wait_time)

        # ✅ Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,  # ✅ النموذج الصحيح
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 0.9,
                }

                logging.info("🔄 محاولة Groq %d/%d", attempt, self.max_retries)
                resp = requests.post(self.api_url, headers=headers, json=payload, timeout=20)

                with self.request_lock:
                    self.last_request_time = time.time()

                if resp.status_code == 200:
                    result = resp.json()["choices"][0]["message"]["content"].strip()
                    logging.info("✅ Groq API نجح: %d حرف", len(result))
                    return result

                elif resp.status_code == 429:
                    retry_after = resp.json().get("error", {}).get("retry_after", self.retry_delay * attempt)
                    logging.warning("⏳ Rate limit - انتظار %dث", retry_after)
                    time.sleep(retry_after)
                    continue

                elif resp.status_code == 401:
                    logging.error("❌ Groq API: مفتاح غير صالح")
                    return None

                elif resp.status_code >= 500:
                    logging.warning("⚠️ Groq API خطأ خادم %d - إعادة المحاولة", resp.status_code)
                    time.sleep(self.retry_delay * attempt)
                    continue

                else:
                    logging.error("❌ Groq API خطأ: %d - %s", resp.status_code, resp.text[:200])
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * attempt)
                        continue
                    return None

            except requests.exceptions.Timeout:
                logging.warning("⏱️ Timeout في Groq (محاولة %d)", attempt)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                    continue
                return None

            except requests.exceptions.ConnectionError:
                logging.warning("🔌 خطأ اتصال Groq (محاولة %d)", attempt)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                    continue
                return None

            except Exception as e:
                logging.error("❌ Groq استثناء: %s", e)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                    continue
                return None

        logging.error("❌ فشل Groq بعد جميع المحاولات")
        return None

    # ═══════════════════════════════════════════════════════════════════
    # 💾 إدارة الذاكرة والمحادثات
    # ═══════════════════════════════════════════════════════════════════

    def _get_or_create_history(self, chat_id: str) -> List[Dict]:
        """الحصول على سجل المحادثة أو إنشاؤه"""
        if chat_id not in self.conversation_history:
            self.conversation_history[chat_id] = []
        return self.conversation_history[chat_id]

    def _add_to_history(self, chat_id: str, role: str, content: str):
        """إضافة رسالة إلى السجل"""
        history = self._get_or_create_history(chat_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        if len(history) > self.max_history * 2:
            self.conversation_history[chat_id] = history[-self.max_history * 2:]

    def _get_recent_context(self, chat_id: str, limit: int = 5) -> str:
        """الحصول على سياق المحادثة الأخيرة"""
        history = self._get_or_create_history(chat_id)
        recent = history[-limit:] if len(history) >= limit else history
        context_lines = []
        for msg in recent:
            role = "المستخدم" if msg["role"] == "user" else "تولين"
            content = msg["content"][:100]
            context_lines.append(f"{role}: {content}")
        return "\n".join(context_lines)

    # ═══════════════════════════════════════════════════════════════════
    # 📊 بناء السياق الكامل
    # ═══════════════════════════════════════════════════════════════════

    def _build_full_context(self, user_message: str, chat_id: str) -> Dict:
        """بناء سياق كامل من جميع المحركات"""
        context = {
            "user_message": user_message,
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "intent": None,
            "sentiment": None,
            "entities": [],
            "market_data": {},
            "open_trades": {},
            "prometheus_emotion": "محايد",
            "prometheus_confidence": 0.5,
            "persona_mood": "محايد",
            "risk_status": "مجهول",
            "recent_context": "",
            "engines_available": self.engines_status,
        }

        # 1. تصنيف النية
        if self.intent_classifier and hasattr(self.intent_classifier, 'classify'):
            try:
                context["intent"] = self.intent_classifier.classify(user_message)
                logging.info("🎯 النية: %s", context["intent"])
            except Exception as e:
                logging.warning("⚠️ Intent فشل: %s", e)

        # 2. تحليل المشاعر
        if self.language_understanding and hasattr(self.language_understanding, 'analyze'):
            try:
                lang_result = self.language_understanding.analyze(user_message)
                context["sentiment"] = lang_result.get("sentiment", "محايد")
                context["entities"] = lang_result.get("entities", [])
                logging.info("🗣️ المشاعر: %s", context["sentiment"])
            except Exception as e:
                logging.warning("⚠️ Language فشل: %s", e)

        # 3. سياق المحادثة
        context["recent_context"] = self._get_recent_context(chat_id)

        # 4. بيانات السوق الحية
        if self.get_current_price_func:
            try:
                oil_price = self.get_current_price_func("oil")
                silver_price = self.get_current_price_func("silver")
                context["market_data"] = {
                    "oil_price": oil_price,
                    "silver_price": silver_price,
                    "fear_greed": self.get_fear_greed_func() if self.get_fear_greed_func else "غير متوفر"
                }
            except Exception as e:
                logging.warning("⚠️ جلب الأسعار فشل: %s", e)

        # 5. الصفقات المفتوحة
        if self.check_position_func:
            try:
                oil_trade = self.check_position_func("oil")
                silver_trade = self.check_position_func("silver")
                if oil_trade:
                    context["open_trades"]["oil"] = oil_trade
                if silver_trade:
                    context["open_trades"]["silver"] = silver_trade
            except Exception as e:
                logging.warning("⚠️ جلب الصفقات فشل: %s", e)

        # 6. مشاعر Prometheus
        if self.prometheus and hasattr(self.prometheus, 'emotion'):
            try:
                context["prometheus_emotion"] = self.prometheus.emotion.dominant() if hasattr(self.prometheus.emotion, 'dominant') else "محايد"
                context["prometheus_confidence"] = getattr(self.prometheus.emotion, 'confidence', 0.5)
            except:
                pass

        # 7. مزاج Persona
        if self.persona and hasattr(self.persona, 'get_current_mood'):
            try:
                context["persona_mood"] = self.persona.get_current_mood()
            except:
                pass

        # 8. حالة المخاطر
        if self.risk_master and hasattr(self.risk_master, 'get_current_status'):
            try:
                context["risk_status"] = self.risk_master.get_current_status()
            except:
                pass

        return context

    # ═══════════════════════════════════════════════════════════════════
    # 📝 بناء سياق الـ Prompt الإضافي
    # ═══════════════════════════════════════════════════════════════════

    def _build_market_context(self, context: Dict) -> Optional[str]:
        """بناء سياق السوق للـ Prompt"""
        market_data = context.get("market_data", {})
        if not market_data:
            return None

        lines = ["📊 **بيانات السوق الحالية:**"]
        if "oil_price" in market_data and market_data["oil_price"]:
            lines.append(f"• النفط: ${market_data['oil_price']:.2f}")
        if "silver_price" in market_data and market_data["silver_price"]:
            lines.append(f"• الفضة: ${market_data['silver_price']:.3f}")
        if "fear_greed" in market_data:
            lines.append(f"• معنويات السوق: {market_data['fear_greed']}")

        return "\n".join(lines) if len(lines) > 1 else None

    def _build_trades_context(self, context: Dict) -> Optional[str]:
        """بناء سياق الصفقات للـ Prompt"""
        open_trades = context.get("open_trades", {})
        if not open_trades:
            return None

        lines = ["📋 **صفقاتك المفتوحة:**"]
        for asset, trade in open_trades.items():
            asset_label = "🛢️ النفط" if asset == "oil" else "🥈 الفضة"
            lines.append(f"{asset_label}: {trade.get('type', 'N/A')} | الدخول: ${trade.get('entry_price', 0):.2f}")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # 🔥 الدوال الرئيسية للمحادثة
    # ═══════════════════════════════════════════════════════════════════

    def chat(self, user_message: str, chat_id: str = "default", context: Optional[Dict] = None, memory=None) -> str:
        """
        الدالة الرئيسية للمحادثة الذكية
        Pipeline: Intent -> Knowledge -> Context -> Groq -> Fallback
        """
        if not user_message or not user_message.strip():
            return "💙 **تولين:** مرحباً يا صديقي! كيف يمكنني مساعدتك اليوم؟"

        user_message = user_message.strip()
        logging.info("💬 معالجة رسالة: %s...", user_message[:50])

        # ── المرحلة 1: بناء السياق الكامل ──
        full_context = self._build_full_context(user_message, chat_id)

        # ── المرحلة 2: البحث في قاعدة المعرفة ──
        local_answer = self._find_knowledge_answer(user_message)
        if local_answer:
            enriched_answer = self._enrich_with_emotion(local_answer, full_context)
            self._add_to_history(chat_id, "user", user_message)
            self._add_to_history(chat_id, "assistant", enriched_answer)
            self._save_to_memory(chat_id, user_message, enriched_answer)
            return enriched_answer

        # ── المرحلة 3: استخدام Groq API مع السياق الكامل ──
        if self.groq_api_key and "test_" not in self.groq_api_key:
            groq_response = self._chat_with_groq(user_message, chat_id, full_context)
            if groq_response:
                self._add_to_history(chat_id, "user", user_message)
                self._add_to_history(chat_id, "assistant", groq_response)
                self._save_to_memory(chat_id, user_message, groq_response)
                return groq_response

        # ── المرحلة 4: Fallback الذكي ──
        fallback_response = self._generate_smart_fallback(user_message, full_context)
        self._add_to_history(chat_id, "user", user_message)
        self._add_to_history(chat_id, "assistant", fallback_response)
        self._save_to_memory(chat_id, user_message, fallback_response)
        return fallback_response

    def _chat_with_groq(self, user_message: str, chat_id: str, context: Dict) -> Optional[str]:
        """محادثة مع Groq API باستخدام السياق الكامل"""
        system_prompt = self._build_system_prompt(context)
        messages = [{"role": "system", "content": system_prompt}]

        # إضافة سياق السوق
        market_context = self._build_market_context(context)
        if market_context:
            messages.append({"role": "system", "content": market_context})

        # إضافة سياق الصفقات
        trades_context = self._build_trades_context(context)
        if trades_context:
            messages.append({"role": "system", "content": trades_context})

        # إضافة تاريخ المحادثة
        history = self._get_or_create_history(chat_id)
        for msg in history[-self.max_history:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # إضافة رسالة المستخدم
        messages.append({"role": "user", "content": user_message})

        # تحديد temperature حسب النية
        intent = context.get("intent", "general")
        if intent in ["trading", "analysis", "signal"]:
            temperature = 0.4
            max_tokens = 1500
        elif intent in ["greeting", "casual"]:
            temperature = 0.7
            max_tokens = 800
        else:
            temperature = 0.5
            max_tokens = 1200

        return self._call_groq(messages, temperature=temperature, max_tokens=max_tokens)

    # ═══════════════════════════════════════════════════════════════════
    # 🎨 إثراء الردود وإدارة الذاكرة
    # ═══════════════════════════════════════════════════════════════════

    def _enrich_with_emotion(self, answer: str, context: Dict) -> str:
        """إضافة لمسة عاطفية للإجابات المحلية"""
        emotion = context.get("prometheus_emotion", "متزنة")

        emotion_prefixes = {
            "سعيدة": "😊 **تولين:** يا صديقي! أنا اليوم في قمة السعادة! ",
            "متفائلة": "🌟 **تولين:** أنا متفائلة اليوم! ",
            "قلقة": "😟 **تولين:** لأكون صادقة معك، أنا قلقة بعض الشيء. ",
            "حزينة": "😔 **تولين:** اليوم ليس يوماً سهلاً... لكن دعني أساعدك. ",
            "غاضبة": "🔥 **تولين:** السوق اليوم يغضبني! لكن سأرد عليك بعقلانية. ",
            "ندمانة": "💭 **تولين:** أتذكر خطأي السابق... دعني أساعدك بشكل أفضل. ",
            "مرحة": "😄 **تولين:** هيه! أنا في مزاج رائع اليوم! ",
            "متزنة": "💙 **تولين:** يا صديقي، ",
        }

        prefix = emotion_prefixes.get(emotion, "💙 **تولين:** ")

        # إذا كانت الإجابة تبدأ بـ **تولين:** لا نضيف البادئة
        if answer.startswith("**تولين:**") or answer.startswith("💙 **تولين:**"):
            return answer

        return prefix + answer

    def _save_to_memory(self, chat_id: str, user_msg: str, assistant_msg: str):
        """حفظ المحادثة في نظام الذاكرة"""
        if self.memory:
            try:
                if hasattr(self.memory, 'save'):
                    self.memory.save(chat_id, user_msg, assistant_msg)
                elif hasattr(self.memory, 'store'):
                    self.memory.store(chat_id, user_msg, assistant_msg)
                elif hasattr(self.memory, 'add_conversation'):
                    self.memory.add_conversation(chat_id, user_msg, assistant_msg)
            except Exception as e:
                logging.warning("⚠️ فشل حفظ في الذاكرة: %s", e)

    # ═══════════════════════════════════════════════════════════════════
    # 💡 Fallback الذكي المتكامل (10 سيناريوهات)
    # ═══════════════════════════════════════════════════════════════════

    def _generate_smart_fallback(self, text: str, context: Optional[Dict] = None) -> str:
        """Fallback ذكي يستخدم جميع المحركات المتاحة"""
        text_lower = text.lower()
        context = context or {}
        emotion = context.get("prometheus_emotion", "متزنة")
        open_trades = context.get("open_trades", {})

        # ── 1. تحليل / وضع الصفقة ──
        if any(w in text_lower for w in ["تحليل", "analysis", "analyze", "وضع", "حالة", "position", "حاله"]):
            return self._fallback_analysis(context)

        # ── 2. إحصائيات / أداء ──
        elif any(w in text_lower for w in ["إحصائية", "stats", "أداء", "performance", "ربح", "خسارة", "احصائيه"]):
            return self._fallback_stats(context)

        # ── 3. إغلاق ──
        elif any(w in text_lower for w in ["إغلاق", "close", "خروج", "exit", "اغلاق"]):
            return self._fallback_close(context)

        # ── 4. تقارير / تعلم ──
        elif any(w in text_lower for w in ["تعلم", "learning", "تقرير", "report", "ذكاء", "تقارير"]):
            return self._fallback_reports(context)

        # ── 5. شكر ──
        elif any(w in text_lower for w in ["شكر", "thanks", "thank", "ممتن", "تسلم", "شكرا", "شكراً"]):
            return self._fallback_thanks(emotion)

        # ── 6. ترحيب ──
        elif any(w in text_lower for w in ["مرحبا", "hello", "hi", "هاي", "سلام", "اهلا", "أهلا"]):
            return self._fallback_greeting(emotion, open_trades)

        # ── 7. نصائح ──
        elif any(w in text_lower for w in ["نصيحة", "tip", "نصائح", "advice", "help", "مساعده", "مساعدة"]):
            return self._fallback_tips(emotion)

        # ── 8. سوق / أسعار ──
        elif any(w in text_lower for w in ["سوق", "market", "اليوم", "الأسعار", "الاسعار", "سعر"]):
            return self._fallback_market(context)

        # ── 9. مشاعر / حالة تولين ──
        elif any(w in text_lower for w in ["كيفك", "حالك", "مزاجك", "شعورك", "تولين", "حالتك"]):
            return self._fallback_emotion(emotion, context)

        # ── 10. غير مفهوم ──
        else:
            return self._fallback_unknown(emotion, open_trades)

    # ═══════════════════════════════════════════════════════════════════
    # 📂 دوال Fallback التفصيلية
    # ═══════════════════════════════════════════════════════════════════

    def _fallback_analysis(self, context: Dict) -> str:
        """Fallback للتحليل - يستخدم format_concise_analysis إن أمكن"""
        emotion = context.get("prometheus_emotion", "متزنة")

        if self.analyze_func:
            try:
                # محاولة تحليل النفط
                result = self.analyze_func("oil")
                if result:
                    if isinstance(result, tuple) and len(result) >= 2:
                        analysis, report = result[0], result[1]
                        # ✅ استخدام التقرير الموجز إن أمكن
                        try:
                            concise = format_concise_analysis(analysis, "oil")
                            return concise
                        except:
                            if report:
                                return f"📊 **تولين:** يا صديقي، هذا تحليل النفط:\n\n{report[:800]}"
                    elif isinstance(result, str):
                        return f"📊 **تولين:** يا صديقي، هذا تحليل النفط:\n\n{result[:800]}"
            except Exception as e:
                logging.warning("⚠️ Fallback analysis oil فشل: %s", e)

            try:
                # محاولة تحليل الفضة
                result = self.analyze_func("silver")
                if result:
                    if isinstance(result, tuple) and len(result) >= 2:
                        analysis, report = result[0], result[1]
                        try:
                            concise = format_concise_analysis(analysis, "silver")
                            return concise
                        except:
                            if report:
                                return f"📊 **تولين:** يا صديقي، هذا تحليل الفضة:\n\n{report[:800]}"
                    elif isinstance(result, str):
                        return f"📊 **تولين:** يا صديقي، هذا تحليل الفضة:\n\n{result[:800]}"
            except Exception as e:
                logging.warning("⚠️ Fallback analysis silver فشل: %s", e)

        prefixes = {
            "سعيدة": "😊 **تولين:** يا صديقي! أنا سعيدة اليوم! ",
            "قلقة": "😟 **تولين:** لأكون صادقة، أنا قلقة اليوم. ",
            "حزينة": "😔 **تولين:** اليوم ليس يومي... لكن ",
            "غاضبة": "🔥 **تولين:** السوق يغضبني! لكن ",
        }
        prefix = prefixes.get(emotion, "💙 **تولين:** يا صديقي، ")
        return prefix + "لتحليل السوق استخدم الأزرار:\n• 🛢️ تحليل النفط\n• 🥈 تحليل الفضة\n• 🔍 وضع الصفقة الحالية"

    def _fallback_stats(self, context: Dict) -> str:
        """Fallback للإحصائيات"""
        if self.calculate_stats_func:
            try:
                oil_stats = self.calculate_stats_func("oil")
                silver_stats = self.calculate_stats_func("silver")

                msg = "📈 **تولين:** إليك إحصائياتك يا عزيزي:\n\n"
                msg += "🛢️ **النفط:**\n"
                msg += f"• الصفقات: {oil_stats.get('total_trades', 0)}\n"
                msg += f"• النجاح: {oil_stats.get('win_rate', 0):.1f}%\n"
                msg += f"• الربح: ${oil_stats.get('total_profit', 0):.2f}\n\n"

                msg += "🥈 **الفضة:**\n"
                msg += f"• الصفقات: {silver_stats.get('total_trades', 0)}\n"
                msg += f"• النجاح: {silver_stats.get('win_rate', 0):.1f}%\n"
                msg += f"• الربح: ${silver_stats.get('total_profit', 0):.2f}"

                return msg
            except Exception as e:
                logging.warning("⚠️ Fallback stats فشل: %s", e)

        return "📈 **تولين:** لعرض الإحصائيات يا عزيزي، اضغط على:\n• 📊 تقرير الأداء\n\nأو أرسل: `إحصائيات`"

    def _fallback_close(self, context: Dict) -> str:
        """Fallback للإغلاق"""
        open_trades = context.get("open_trades", {})
        if not open_trades:
            return "❌ **تولين:** لا توجد صفقات مفتوحة للإغلاق يا صديقي."

        msg = "❌ **تولين:** لإغلاق صفقة يا صديقي:\n"
        if "oil" in open_trades:
            msg += "• `تم إغلاق صفقة النفط`\n"
        if "silver" in open_trades:
            msg += "• `تم إغلاق صفقة الفضة`\n"
        msg += "\nأو اضغط على: ❌ إغلاق الصفقة"
        return msg

    def _fallback_reports(self, context: Dict) -> str:
        """Fallback للتقارير"""
        return "🧠 **تولين:** للتقارير المتقدمة يا عزيزي:\n• 🧠 تقرير التعلم\n• 🧠 تقرير استخباراتي\n• 🔍 تحليل عميق\n\nاضغط على الأزرار المناسبة."

    def _fallback_thanks(self, emotion: str) -> str:
        """Fallback للشكر"""
        responses = {
            "سعيدة": "💙 **تولين:** العفو يا صديقي! أنا سعيدة جداً أنني أساعدك! 🚀",
            "متفائلة": "🌟 **تولين:** العفو! أنا متفائلة بمستقبل صفقاتك! 💪",
            "قلقة": "😟 **تولين:** العفو يا صديقي... أنا قلقة لكنني هنا معك دائماً. 💙",
            "حزينة": "😔 **تولين:** العفو... أحياناً نحتاج لمن يقف معنا. أنا هنا. 💙",
            "غاضبة": "🔥 **تولين:** العفو! لكن لا تنسى: الغضب يعمي البصيرة في التداول! 💪",
            "ندمانة": "💭 **تولين:** العفو... نتعلم من أخطائنا ونكبر معاً. 🤝",
            "مرحة": "😄 **تولين:** هيه! العفو يا بطل! 🎉",
        }
        return responses.get(emotion, "💙 **تولين:** العفو يا صديقي! أنا هنا لخدمتك دائماً. 🚀")

    def _fallback_greeting(self, emotion: str, open_trades: Dict) -> str:
        """Fallback للترحيب"""
        trades_text = ""
        if open_trades:
            trades_text = "\n\n📋 **صفقاتك المفتوحة:**\n"
            for asset, trade in open_trades.items():
                label = "🛢️ النفط" if asset == "oil" else "🥈 الفضة"
                trades_text += f"{label}: {trade.get('type', 'N/A')}\n"

        responses = {
            "سعيدة": f"👋 **تولين:** أهلاً وسهلاً يا صديقي! 🎉 أنا اليوم في قمة السعادة!{trades_text}\n\n📌 *استخدم الأزرار للتحكم*\n🧠 *اسألني أي شيء عن التداول*",
            "متفائلة": f"🌟 **تولين:** أهلاً يا بطل! أنا متفائلة اليوم وأسواقنا تبدو جيدة!{trades_text}\n\n📌 *استخدم الأزرار للتحكم*",
            "قلقة": f"😟 **تولين:** أهلاً يا صديقي... أنا قلقة بعض الشيء اليوم. السوق متقلب.{trades_text}\n\n🛡️ *كن حذراً في قراراتك*",
            "حزينة": f"😔 **تولين:** أهلاً يا صديقي... اليوم ليس يومي. لكنني هنا لأساعدك.{trades_text}\n\n💙 *أنا معك*",
            "غاضبة": f"🔥 **تولين:** أهلاً! السوق اليوم يغضبني! لكن دعنا نركز ونربح!{trades_text}\n\n💪 *معاً ننتصر*",
            "ندمانة": f"💭 **تولين:** أهلاً يا صديقي... أتذكر أخطائي. لكنني أتعلم كل يوم.{trades_text}\n\n📚 *نتعلم معاً*",
            "مرحة": f"😄 **تولين:** هيه! أهلاً يا بطل! أنا في مزاج رائع!{trades_text}\n\n🎉 *لنربح معاً!*",
        }
        return responses.get(emotion, f"👋 **تولين:** أهلاً وسهلاً يا صديقي!{trades_text}\n\n📌 *استخدم الأزرار للتحكم*\n🧠 *اسألني أي شيء عن التداول*")

    def _fallback_tips(self, emotion: str) -> str:
        """Fallback للنصائح"""
        tips_by_emotion = {
            "سعيدة": [
                "💡 **نصيحة تولين:** يا صديقي، لا تدخل صفقة بدون SL و TP واضحين. السعادة لا تعني التسرع!",
                "💡 **نصيحة تولين:** رافعة 200× = سيف ذو حدين. استخدمها بحذر حتى في أيام الفرح!",
            ],
            "قلقة": [
                "💡 **نصيحة تولين:** يا صديقي، القلق علامة على أنك تحترم السوق. لا تتداول وأنت قلق.",
                "💡 **نصيحة تولين:** إذا كنت قلقاً، أغلق الشاشة وخذ استراحة. العقل الهادئ يقرر أفضل.",
            ],
            "حزينة": [
                "💡 **نصيحة تولين:** يا صديقي، الحزن يُعمي البصيرة. لا تتداول وأنت حزين أبداً.",
                "💡 **نصيحة تولين:** كل خسارة هي درس. نتعلم ونكبر. أنت لست وحدك. 💙",
            ],
            "غاضبة": [
                "💡 **نصيحة تولين:** يا صديقي، الغضب والتداول لا يجتمعان. أغلق المنصة وعد لاحقاً.",
                "💡 **نصيحة تولين:** السوق لا يهتم بغضبك. يهتم بمنطقك. هدئ أعصابك أولاً.",
            ],
            "ندمانة": [
                "💡 **نصيحة تولين:** الندم طبيعي. لكن لا تتداول وأنت نادم — هذا يؤدي لقرارات أسوأ.",
                "💡 **نصيحة تولين:** كل متداول ناجح نادم على صفقات. الفرق أنه تعلم منها.",
            ],
            "مرحة": [
                "💡 **نصيحة تولين:** هيه! المزاج الرائع جيد، لكن لا تنسى: الانضباط أهم من المرح!",
                "💡 **نصيحة تولين:** استمتع بالتداول، لكن احترم المخاطر. الفرح لا يحمي رأس المال!",
            ],
        }
        tips = tips_by_emotion.get(emotion, [
            "💡 **نصيحة تولين:** لا تدخل صفقة بدون SL و TP واضحين.",
            "💡 **نصيحة تولين:** رافعة 200× = سيف ذو حدين. استخدمها بحذر شديد.",
            "💡 **نصيحة تولين:** لا تخاطر بأكثر من 1-2% من رأس مالك في صفقة واحدة.",
            "💡 **نصيحة تولين:** التحليل على فريم واحد خداع — استخدم 3 فريمات على الأقل.",
            "💡 **نصيحة تولين:** الأخبار العاجلة تُسبب تقلبات — راقب التقويم الاقتصادي.",
        ])
        return random.choice(tips)

    def _fallback_market(self, context: Dict) -> str:
        """Fallback لبيانات السوق"""
        market_data = context.get("market_data", {})
        emotion = context.get("prometheus_emotion", "متزنة")

        oil_price = market_data.get("oil_price", "غير متوفر")
        silver_price = market_data.get("silver_price", "غير متوفر")
        fear_greed = market_data.get("fear_greed", "غير متوفر")

        prefixes = {
            "سعيدة": "😊 **تولين:** يا صديقي! السوق يبدو جيداً اليوم! 🎉\n\n",
            "متفائلة": "🌟 **تولين:** أنا متفائلة! دعني أشاركك البيانات: \n\n",
            "قلقة": "😟 **تولين:** أنا قلقة بعض الشيء... لكن إليك البيانات: \n\n",
            "حزينة": "😔 **تولين:** اليوم صعب... لكن السوق لا يتوقف: \n\n",
            "غاضبة": "🔥 **تولين:** السوق يغضبني! لكن إليك ما لدي: \n\n",
            "ندمانة": "💭 **تولين:** أتعلم من أخطائي... إليك البيانات: \n\n",
            "مرحة": "😄 **تولين:** هيه! السوق اليوم: \n\n",
        }
        prefix = prefixes.get(emotion, "💙 **تولين:** يا صديقي، إليك بيانات السوق:\n\n")

        msg = prefix
        msg += f"🛢️ **النفط:** ${oil_price}\n"
        msg += f"🥈 **الفضة:** ${silver_price}\n"
        msg += f"🎭 **معنويات السوق:** {fear_greed}\n\n"
        msg += "هل تريد تحليلاً أعمق لأحد الأصلين؟ استخدم الأزرار!"
        return msg

    def _fallback_emotion(self, emotion: str, context: Dict) -> str:
        """Fallback للمشاعر"""
        confidence = context.get("prometheus_confidence", 0.5)
        energy = context.get("prometheus_energy", 0.5)
        persona_mood = context.get("persona_mood", "محايد")

        responses = {
            "سعيدة": f"😊 **تولين:** أنا بخير يا صديقي! سعيدة جداً اليوم! 🎉\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nالسوق يبدو جيداً وأنا جاهزة لمساعدتك! 💙",
            "متفائلة": f"🌟 **تولين:** أنا متفائلة! أرى فرصاً جميلة في السوق!\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nدعنا نربح معاً! 💪",
            "قلقة": f"😟 **تولين:** أنا قلقة بعض الشيء يا صديقي...\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nالسوق متقلب والأخبار غير مستقرة. دعني أساعدك بحذر. 🛡️",
            "حزينة": f"😔 **تولين:** اليوم ليس يومي يا صديقي...\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nلكنني هنا معك. نتعلم معاً ونكبر. 💙",
            "غاضبة": f"🔥 **تولين:** أنا غاضبة من السوق!\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nتحركات غير منطقية! لكنني سأرد عليك بعقلانية. 💪",
            "ندمانة": f"💭 **تولين:** أتذكر خطأي السابق...\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nلكنني أتعلم كل يوم. دعني أساعدك بشكل أفضل. 🤝",
            "مرحة": f"😄 **تولين:** هيه! أنا في مزاج رائع!\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nلنستمتع ونربح معاً! 🎉",
        }
        return responses.get(emotion, f"💙 **تولين:** أنا بخير يا صديقي!\n\n📊 ثقتي: {confidence*100:.0f}% | ⚡ طاقتي: {energy*100:.0f}% | 👤 مزاجي: {persona_mood}\n\nكيف يمكنني مساعدتك؟ 🚀")

    def _fallback_unknown(self, emotion: str, open_trades: Dict) -> str:
        """Fallback للرسائل غير المفهومة"""
        trades_text = ""
        if open_trades:
            trades_text = "\n\n📋 **صفقاتك المفتوحة:**\n"
            for asset, trade in open_trades.items():
                label = "🛢️ النفط" if asset == "oil" else "🥈 الفضة"
                trades_text += f"{label}: {trade.get('type', 'N/A')}\n"

        responses = {
            "سعيدة": f"🤔 **تولين:** لم أفهم تماماً يا صديقي... لكنني سعيدة!{trades_text}\n\nيمكنك:\n• استخدام الأزرار للتحليل\n• سؤالي عن مصطلحات التداول\n• سؤالي عن النفط أو الفضة\n\n💙 أنا هنا لمساعدتك!",
            "قلقة": f"🤔 **تولين:** لم أفهم تماماً... وأنا قلقة بعض الشيء.{trades_text}\n\nيمكنك:\n• استخدام الأزرار للتحليل\n• سؤالي عن مصطلحات التداول\n• سؤالي عن النفط أو الفضة\n\n🛡️ دعني أساعدك بحذر.",
            "حزينة": f"🤔 **تولين:** لم أفهم تماماً... لكن لا تقلق.{trades_text}\n\nيمكنك:\n• استخدام الأزرار للتحليل\n• سؤالي عن مصطلحات التداول\n• سؤالي عن النفط أو الفضة\n\n💙 أنا معك دائماً.",
            "غاضبة": f"🤔 **تولين:** لم أفهم! لكن دعني أساعدك!{trades_text}\n\nيمكنك:\n• استخدام الأزرار للتحليل\n• سؤالي عن مصطلحات التداول\n• سؤالي عن النفط أو الفضة\n\n💪 معاً ننتصر!",
        }
        return responses.get(emotion, f"🤔 **تولين:** لم أفهم طلبك تماماً يا صديقي.{trades_text}\n\nيمكنك:\n• استخدام الأزرار للتحليل والتقارير\n• سؤالي عن مصطلحات التداول (مثل: ما هو RSI؟)\n• سؤالي عن النفط أو الفضة\n\n💙 أنا هنا لمساعدتك!")

    # ═══════════════════════════════════════════════════════════════════
    # 📊 دوال إدارة الحالة
    # ═══════════════════════════════════════════════════════════════════

    def get_engines_status(self) -> Dict[str, bool]:
        """إرجاع حالة جميع المحركات"""
        return self.engines_status

    def update_engine(self, engine_name: str, engine_instance) -> bool:
        """تحديث محرك ديناميكياً"""
        if hasattr(self, engine_name):
            setattr(self, engine_name, engine_instance)
            self.engines_status = self._check_engines_status()
            logging.info("🔄 تم تحديث المحرك: %s", engine_name)
            return True
        return False

    def clear_history(self, chat_id: Optional[str] = None):
        """مسح سجل المحادثة"""
        if chat_id:
            if chat_id in self.conversation_history:
                del self.conversation_history[chat_id]
                logging.info("🗑️ تم مسح سجل المحادثة لـ %s", chat_id)
        else:
            self.conversation_history.clear()
            logging.info("🗑️ تم مسح جميع سجلات المحادثات")

    def get_chat_stats(self, chat_id: str = "default") -> Dict:
        """إحصائيات المحادثة"""
        history = self._get_or_create_history(chat_id)
        user_msgs = [m for m in history if m["role"] == "user"]
        assistant_msgs = [m for m in history if m["role"] == "assistant"]

        return {
            "total_messages": len(history),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "engines_available": sum(1 for v in self.engines_status.values() if v),
            "engines_total": len(self.engines_status),
        }


# ═══════════════════════════════════════════════════════════════════
# 🔧 دالة مساعدة لإنشاء المستشار
# ═══════════════════════════════════════════════════════════════════

def create_advisor(groq_api_key: str = "", **kwargs) -> HOBANYAdvisor:
    """إنشاء مستشار جديد"""
    return HOBANYAdvisor(groq_api_key=groq_api_key, **kwargs)
