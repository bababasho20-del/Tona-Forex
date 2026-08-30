"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║ 🧠 TONA CONSCIOUSNESS NETWORK (TCN) V5.1 - REFACTORED FINAL                    ║
║ 💙 الاسم: تولين - المدير العام للشبكة العصبية الواعية                         ║
║ 👨‍💻 المطور: بسام الحوباني                                                    ║
║ 📡 الوظيفة: مدير عام يتعامل مع جميع المحركات ويبني الردود                    ║
║ 📊 البيانات: تعتمد على بيانات حقيقية 100% من جميع المحركات                    ║
║ 💡 الميزات: وعي ذاتي + توصيات مهنية + دمج جميع المحركات                       ║
╚═══════════════════════════════════════════════════════════════════════════════════╝

📑 الفهرس الداخلي:
───────────────────────────────────────────────────────────────────────────────────
  📦 PART 01: الاستيرادات والمكتبات
  📦 PART 02: INTENTS_LIBRARY (الموسعة بالمرادفات)
  📦 PART 03: دوال البحث الذكية (smart_match_intent)
  📦 PART 04: هياكل البيانات الأساسية
  📦 PART 05: تعريف الكلاس ConsciousnessNetwork
  📦 PART 06: دوال التهيئة
  📦 PART 07: دورة الوعي الرئيسية (think)
  📦 PART 08: دوال العصبونات
  📦 PART 09: بناء الوعي من البيانات
  📦 PART 10: جمع البيانات من جميع المحركات
  📦 PART 11: الأسئلة الاستشارية (المحرك الموحد)
  📦 PART 12: دوال الردود المدمجة (ديناميكية بالكامل)
  📦 PART 13: دوال مساعدة داخلية
  📦 PART 14: واجهات الاستخدام
  📦 PART 15: دوال الحفظ والتحميل
═══════════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 01: الاستيرادات والمكتبات
# ═══════════════════════════════════════════════════════════════════════════════════

import os
import time
import json
import threading
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger("TonaConsciousness")

# ═══════════════════════════════════════════════════════════════════════
# 📚 INTENTS_LIBRARY - النيات الموسعة (مدمجة داخل TCN)
# ═══════════════════════════════════════════════════════════════════════

INTENTS_LIBRARY = {
    # ═══════════════════════════════════════════════════════════════
    # القسم 1: التفاعل الشخصي
    # ═══════════════════════════════════════════════════════════════
    
    "how_are_you": {
        "keywords": [
            "كيف حالك", "كيفك", "شلونك", "كيف انت", "how are you", 
            "شو اخبارك", "اخبارك", "كيف الأحوال", "ازيك", "كيف الحال",
            "شخبارك", "اخبارك ايه"
        ],
        "priority": 10,
        "handler": "how_are_you"
    },
    
    "greeting": {
        "keywords": [
            "مرحبا", "اهلا", "سلام", "هلا", "hi", "hello", 
            "السلام عليكم", "صباح الخير", "مساء الخير", "أهلا وسهلا",
            "يا هلا", "مرحب", "هاي"
        ],
        "priority": 9,
        "handler": "greeting"
    },
    
    "farewell": {
        "keywords": [
            "مع السلامة", "وداعاً", "باي", "إلى اللقاء", 
            "goodbye", "bye", "see you", "تصبح على خير",
            "سلام", "نشوفك"
        ],
        "priority": 9,
        "handler": "farewell"
    },
    
    "about_identity": {
        "keywords": [
            "من أنت", "من انت", "اسمك", "تولين", "مطورك", 
            "من صنعك", "شخصيتك", "who are you", "your name",
            "من مطورك", "مين مطورك", "مين أنت", "تعريف نفسك",
            "قولي عن نفسك", "عرفني بنفسك"
        ],
        "priority": 8,
        "handler": "about_identity"
    },
    
    "gratitude": {
        "keywords": [
            "شكراً", "شكرا", "thanks", "thank you", 
            "ممتن", "متشكر", "الله يعطيك العافية", "تسلم",
            "تسلمي", "يعطيك الف عافية", "مشكور"
        ],
        "priority": 8,
        "handler": "gratitude"
    },
    
    "compliment": {
        "keywords": [
            "أحسنت", "ممتاز", "رائع", "awesome", "great", 
            "أنت ذكي", "عمل جيد", "جميل", "أحسنت عملاً",
            "بطل", "عبقري", "مذهل"
        ],
        "priority": 7,
        "handler": "compliment"
    },
    
    "complaint": {
        "keywords": [
            "سيء", "خطأ", "مشكلة", "لا يعمل", "فاشل", 
            "bad", "error", "problem", "خاطئ", "رديء",
            "غلط", "مو زين", "تعبان"
        ],
        "priority": 9,
        "handler": "complaint"
    },
    
    "alertness_command": {
        "keywords": [
            "كن متيقظا", "تيقظ", "انتبه", "كن مستعدا", "ركز",
            "stay alert", "be ready", "كن مستعد", "لا تغفل",
            "انتبه للشارت", "تعلم من اخطاءك", "تعلم من أخطائك",
            "كن متيقظ", "استعد", "تعلم من كل شي"
        ],
        "priority": 8,
        "handler": "alertness_command"
    },
    
    "what_doing": {
        "keywords": [
            "ماذا تفعلين", "what are you doing", "شو تعملين", 
            "مهامك", "شغلك", "ماذا تعملين", "وش تسوين",
            "بماذا تشتغلين", "ايش تسوي"
        ],
        "priority": 7,
        "handler": "what_doing"
    },
    
    "capabilities": {
        "keywords": [
            "قدرات", "مهام", "تساعد", "استشارة", "ماذا تفعل",
            "what can you do", "قدراتك", "ماذا تقدم", "فائدتك",
            "شو تقدرين تسوين", "ايش تقدمين", "اختصاصك"
        ],
        "priority": 6,
        "handler": "capabilities"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 2: تحليل السوق والأخبار (موسعة بالمرادفات)
    # ═══════════════════════════════════════════════════════════════
    
    "market_analysis": {
        "keywords": [
            "كيف السوق", "وضع السوق", "السوق اليوم", "تحليل السوق", 
            "حال السوق", "market status", "كيف الأسواق", "السوق الان",
            "نظرة عامة", "لمحة سريعة", "وضع السوق الآن", "وش وضع السوق"
        ],
        "priority": 8,
        "handler": "market_analysis"
    },
    
    "oil_analysis": {
        "keywords": [
            "نفط", "oil", "خام", "برنت", "wti", "usoil",
            "سعر النفط", "تحليل النفط", "توقعات النفط",
            "اتجاه النفط", "شراء نفط", "بيع نفط",
            "ماهو اتجاه النفط", "النفط صاعد", "النفط هابط",
            "طالع النفط", "نازل النفط"
        ],
        "priority": 8,
        "handler": "oil_analysis"
    },
    
    "silver_analysis": {
        "keywords": [
            "فضة", "silver", "xag", "xagusd",
            "سعر الفضة", "تحليل الفضة", "توقعات الفضة",
            "اتجاه الفضة", "شراء فضة", "بيع فضة",
            "ماهو اتجاه الفضة", "الفضة صاعدة", "الفضة هابطة",
            "طالعة الفضة", "نازلة الفضة"
        ],
        "priority": 8,
        "handler": "silver_analysis"
    },
    
    "news_general": {
        "keywords": [
            "أخبار", "news", "مستجدات", "الجديد", "آخر",
            "مالجديد", "ما الجديد", "شنو الجديد", "شو الجديد",
            "ماذا حدث", "شنو صار", "وش صار", "ماذا حصل",
            "اليوم", "هذا اليوم", "هاليوم", "آخر الأخبار",
            "أخبار اليوم", "أخبار السوق", "ما آخر", "وش آخر",
            "مستجدات السوق", "تحديثات", "آخر المستجدات",
            "شو الاخبار", "ايش الاخبار"
        ],
        "priority": 8,
        "handler": "news_general"
    },
    
    "oil_price_reason": {
        "keywords": [
            "ليش النفط", "لماذا النفط", "سبب انخفاض النفط",
            "سبب ارتفاع النفط", "سبب تدهور النفط",
            "ماسبب", "ما سبب", "شنو سبب", "شو سبب",
            "انهيار النفط", "ارتفاع النفط", "انخفاض النفط",
            "تدهور النفط", "صعود النفط", "هبوط النفط",
            "ليش سعر النفط", "لماذا سعر النفط",
            "ماسبب انهيار النفط", "ماسبب انخفاض النفط",
            "ماسبب ارتفاع النفط", "ماذا حدث للنفط",
            "ليش طلع النفط", "ليش نزل النفط", "النفط ليش طالع",
            "النفط ليش نازل", "ماسبب تدهور النفط"
        ],
        "priority": 8,
        "handler": "oil_price_reason"
    },
    
    "silver_price_reason": {
        "keywords": [
            "ليش الفضة", "لماذا الفضة", "سبب انخفاض الفضة",
            "سبب ارتفاع الفضة", "سبب تدهور الفضة",
            "انهيار الفضة", "ارتفاع الفضة", "انخفاض الفضة",
            "تدهور الفضة", "صعود الفضة", "هبوط الفضة",
            "ليش سعر الفضة", "لماذا سعر الفضة",
            "ماسبب انهيار الفضة", "ماسبب انخفاض الفضة",
            "ماسبب ارتفاع الفضة", "ماذا حدث للفضة",
            "ليش طلعت الفضة", "ليش نزلت الفضة", "الفضة ليش طالعة",
            "الفضة ليش نازلة", "ماسبب تدهور الفضة"
        ],
        "priority": 8,
        "handler": "silver_price_reason"
    },
    
    "market_silence": {
        "keywords": [
            "ساكن", "هادئ", "مستقر", "راكد", "نائم",
            "السوق ساكن", "لماذا ساكن", "لماذا هادئ",
            "هدوء السوق", "سكون السوق", "السوق نائم",
            "لا توجد حركة", "الحركة ضعيفة", "السوق ميت",
            "لماذا السوق راكد", "ليش السوق ساكن",
            "ليش السوق هادئ", "السوق هادئ اليوم"
        ],
        "priority": 7,
        "handler": "market_silence"
    },
    
    "market_comparison": {
        "keywords": [
            "النفط والفضة", "oil vs silver", "مقارنة",
            "أيهما أفضل", "النفط أم الفضة", "مقارنة بين النفط والفضة"
        ],
        "priority": 6,
        "handler": "market_comparison"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 3: إدارة الصفقات (موسعة)
    # ═══════════════════════════════════════════════════════════════
    
    "trade_open": {
        "keywords": [
            "افتح صفقة", "ادخل صفقة", "صفقة جديدة", "أريد صفقة",
            "open trade", "هل أدخل", "هل ادخل", "هل أفتح",
            "هل افتح", "ادخل شراء", "ادخل بيع", "أريد ادخل النفط",
            "افتح نفط", "افتح فضة", "اريد شراء"
        ],
        "priority": 10,
        "handler": "trade_open"
    },
    
    "trade_close": {
        "keywords": [
            "أغلق الصفقة", "أخرج من الصفقة", "close trade",
            "هل أغلق", "أغلق", "أخرج", "هل أخرج الان",
            "هل أغلق الان", "أخرج ولا لا", "أغلق ولا لا",
            "اغلق", "أغلق صفقة النفط", "أغلق صفقة الفضة",
            "هل أستمر", "استمر ولا أخرج", "اطلع", "اخلع"
        ],
        "priority": 10,
        "handler": "trade_close"
    },
    
    "trade_status": {
        "keywords": [
            "حالة الصفقة", "وضع الصفقة", "الصفقة الحالية",
            "صفقتي", "مركزي", "my trade", "هل لدي صفقة",
            "صفقة مفتوحة", "عندي صفقة", "الصفقات المفتوحة",
            "هل هناك صفقة", "هل هناك صفقات", "وضعي",
            "حالة", "check", "وضع الصفقة الحالية",
            "صفقاتي", "كم صفقة معي"
        ],
        "priority": 9,
        "handler": "trade_status"
    },
    
    "trade_history": {
        "keywords": [
            "آخر صفقة", "الصفقة الأخيرة", "اخر صفقة",
            "تاريخ الصفقات", "سجل الصفقات", "last trade",
            "الصفقة السابقة", "آخر صفقة لي", "صفقات اليوم",
            "التاريخ", "السجل"
        ],
        "priority": 8,
        "handler": "trade_history"
    },
    
    "trade_analysis": {
        "keywords": [
            "تحليل الصفقة", "لماذا خسرت", "ليش خسرت",
            "سبب خسارة", "ماسبب خسارة", "why did I lose",
            "لماذا خسرت صفقتي", "ليش خسرت صفقتي",
            "ماسبب خسارة صفقتي", "تحليل آخر صفقة",
            "الصفقة الأخيرة لماذا خسرت", "سبب خسارة الصفقة",
            "لماذا خسرت صفقة النفط", "لماذا خسرت صفقة الفضة",
            "لماذا ربحت", "ليش ربحت", "سبب ربح", "ماسبب ربح",
            "تحليل الخسارة", "ليش طلعت خسران"
        ],
        "priority": 9,
        "handler": "trade_analysis"
    },
    
    "trade_risk_assessment": {
        "keywords": [
            "خطر الصفقة", "مخاطرة الصفقة", "وضع الصفقة",
            "هل الصفقة سليمة", "هل هناك خطر",
            "أكبر خطر", "ما هو الخطر", "الخطر الأكبر",
            "ماهو أكبر خطر للصفقة", "هل وضع الصفقة سليم",
            "هل هناك خطر في الصفقة", "تقييم مخاطر الصفقة",
            "هل الصفقة آمنة", "الخطر"
        ],
        "priority": 8,
        "handler": "trade_risk_assessment"
    },
    
    "trade_indicators": {
        "keywords": [
            "ماذا تقول المؤشرات", "المؤشرات في الصفقة",
            "تحليل المؤشرات للصفقة", "مؤشرات صفقة النفط",
            "مؤشرات صفقة الفضة", "التحليل الفني للصفقة",
            "قراءة المؤشرات للصفقة", "هل المؤشرات تدعم الصفقة",
            "ماذا تقول المؤشرات في الصفقة الحالية"
        ],
        "priority": 7,
        "handler": "trade_indicators"
    },
    
    "trade_failure_opinion": {
        "keywords": [
            "تبدو صفقة فاشلة", "الصفقة فاشلة",
            "صفقة غير ناجحة", "تبدو غير ناجحة",
            "تبدو خاسرة", "الصفقة خاسرة",
            "مارأيك في الصفقة", "رأيك في الصفقة",
            "هل الصفقة جيدة", "هل الصفقة سيئة",
            "غير مؤكدة", "تبدو غير مؤكدة", "رأيك"
        ],
        "priority": 7,
        "handler": "trade_failure_opinion"
    },
    
    "virtual_trade_advice": {
        "keywords": [
            "هل أدخل", "هل ادخل", "هل أفتح", "هل افتح",
            "هل هذه الصفقة", "هل الصفقة", "صفقة مقترحة",
            "صفقة مرسلة", "الإشارة", "الإشعار", "تنبيه الصفقة",
            "هل أنصح بدخول", "هل تنصح بالدخول",
            "هل أدخل هذه الصفقة"
        ],
        "priority": 8,
        "handler": "virtual_trade_advice"
    },
    
    "exit_advice": {
        "keywords": [
            "هل أخرج", "هل أخرج الان", "أخرج ولا لا",
            "هل أغلق", "أغلق الصفقة", "اغلق ولا لا",
            "هل أغلق الان", "أنصح بالخروج", "الخروج الان",
            "أغلق صفقتي", "هل أستمر", "استمر ولا أخرج"
        ],
        "priority": 8,
        "handler": "exit_advice"
    },
    
    "profit_loss": {
        "keywords": [
            "كم أرباحي", "كم خسائري", "ربحي", "خسارتي",
            "أرباحي", "خسائري", "إجمالي الأرباح",
            "إجمالي الخسائر", "كم ربحت", "كم خسرت",
            "ربح اليوم", "خسارة اليوم", "مكسب", "خسارة",
            "مكسبي", "خسارتي", "اداء", "الاداء"
        ],
        "priority": 7,
        "handler": "profit_loss"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 4: المؤشرات الفنية
    # ═══════════════════════════════════════════════════════════════
    
    "rsi_value": {
        "keywords": [
            "rsi", "ار اس اي", "الار اس اي", "مؤشر القوة النسبية",
            "كم rsi", "قيمة rsi", "rsi كم", "قراءة rsi",
            "rsi النفط", "rsi الفضة", "كم ار اس اي",
            "ار اس اي النفط", "ار اس اي الفضة"
        ],
        "priority": 7,
        "handler": "rsi_value"
    },
    
    "macd_analysis": {
        "keywords": [
            "macd", "ماكد", "الماكد", "مؤشر macd",
            "تحليل macd", "macd النفط", "macd الفضة"
        ],
        "priority": 7,
        "handler": "macd_analysis"
    },
    
    "vwap_location": {
        "keywords": [
            "vwap", "في واب", "الفي واب", "خط vwap",
            "موقع vwap", "vwap وين", "اين خط الـ vwap",
            "اين vwap", "مستوى vwap", "الvwap", "VWAP"
        ],
        "priority": 7,
        "handler": "vwap_location"
    },
    
    "bollinger_reading": {
        "keywords": [
            "bollinger", "بولينجر", "البولينجر", "bollinger bands",
            "ماذا يقول البولينجر", "البولينجر", "هل يؤكد صفقتي",
            "تحليل البولينجر", "البولينجر النفط", "البولينجر الفضة"
        ],
        "priority": 7,
        "handler": "bollinger_reading"
    },
    
    "adx_analysis": {
        "keywords": [
            "adx", "ايدكس", "الايدكس", "مؤشر الاتجاه",
            "تحليل adx", "adx النفط", "adx الفضة"
        ],
        "priority": 7,
        "handler": "adx_analysis"
    },
    
    "support_resistance": {
        "keywords": [
            "الدعم", "المقاومة", "دعم", "مقاومة",
            "انعكاس", "ارتداد", "support", "resistance",
            "هل السعر عند مقاومة", "هل السعر عند دعم",
            "خط مقاومة", "خط دعم", "مستوى مقاومة", "مستوى دعم",
            "منطقة دعم", "منطقة مقاومة", "الدعم القريب",
            "المقاومة القريبة", "هل السعر قرب الدعم",
            "هل السعر قرب المقاومة"
        ],
        "priority": 8,
        "handler": "support_resistance"
    },
    
    "reversal_expectation": {
        "keywords": [
            "هل تتوقع انعكاس", "هل ينعكس السعر",
            "انعكاس من الدعم", "انعكاس من المقاومة",
            "هل يرتد السعر", "ارتداد من الدعم",
            "ارتداد من المقاومة", "تصحيح من الدعم",
            "تصحيح من المقاومة", "هل السعر ينعكس",
            "يتوقع انعكاس", "reversal"
        ],
        "priority": 7,
        "handler": "reversal_expectation"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 5: إدارة المخاطر
    # ═══════════════════════════════════════════════════════════════
    
    "risk_assessment": {
        "keywords": [
            "خطر", "مخاطرة", "أمان", "وقف خسارة", "SL",
            "risk", "هل الصفقة آمنة", "تقييم المخاطر",
            "تحليل المخاطر", "مستوى الخطر", "درجة المخاطرة"
        ],
        "priority": 8,
        "handler": "risk_assessment"
    },
    
    "stop_loss_placement": {
        "keywords": [
            "أين أضع SL", "مكان الوقف", "stop loss",
            "الوقف", "أين أضع وقف الخسارة"
        ],
        "priority": 7,
        "handler": "stop_loss_placement"
    },
    
    "take_profit_placement": {
        "keywords": [
            "الهدف", "take profit", "TP", "أين الهدف",
            "أين أضع TP", "مكان الهدف"
        ],
        "priority": 7,
        "handler": "take_profit_placement"
    },
    
    "risk_reward_ratio": {
        "keywords": [
            "risk reward", "نسبة المخاطرة", "R:R", "RR",
            "نسبة المخاطرة للمكافأة", "reward to risk"
        ],
        "priority": 7,
        "handler": "risk_reward_ratio"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 6: التوقعات والسيناريوهات
    # ═══════════════════════════════════════════════════════════════
    
    "price_prediction": {
        "keywords": [
            "توقع", "تتوقع", "يتجه", "سيرتفع", "سينخفض",
            "أتوقع", "prediction", "forecast",
            "أتوقع النفط سيرتفع", "أتوقع النفط سينخفض",
            "أتوقع الفضة سترتفع", "أتوقع الفضة ستنخفض",
            "توقع سعر النفط", "توقع سعر الفضة",
            "هل سيرتفع النفط", "هل سينخفض النفط",
            "النفط رايح طالع", "النفط رايح نازل",
            "ماتوقعك للنفط", "ماتوقعك للفضة",
            "توقعات النفط", "توقعات الفضة",
            "طالع", "نازل", "صاعد", "هابط"
        ],
        "priority": 7,
        "handler": "price_prediction"
    },
    
    "explosion_prediction": {
        "keywords": [
            "انفجار", "انهيار", "صعود قوي", "هبوط حاد",
            "breakout", "breakdown", "هل تتوقع انفجار",
            "هل تتوقع انهيار", "توقع انفجار", "توقع انهيار",
            "هل تتوقع صعود", "هل تتوقع هبوط",
            "حركة قوية قادمة", "تقلبات قادمة"
        ],
        "priority": 7,
        "handler": "explosion_prediction"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 7: التعلم والتحسين
    # ═══════════════════════════════════════════════════════════════
    
    "learning_questions": {
        "keywords": [
            "ماذا تعلمت", "تعلمت", "هل تتعلم",
            "تعلم من اخطاءك", "دروس", "lessons",
            "هل تتعلم من اخطائك", "تتعلم من اخطائك",
            "ماذا تعلمتي", "ماذا استفدت", "خبرات",
            "هل تتحسن", "تتعلم من كل شي"
        ],
        "priority": 6,
        "handler": "learning_questions"
    },
    
    "strategy_education": {
        "keywords": [
            "استراتيجية", "strategy", "طريقة", "method",
            "كيف تتداول", "استراتيجيتك", "منهجيتك"
        ],
        "priority": 6,
        "handler": "strategy_education"
    },
    
    "indicator_education": {
        "keywords": [
            "شرح مؤشر", "explain indicator", "كيف يعمل",
            "what is", "ما هو", "شرح RSI", "شرح MACD",
            "ماذا يعني", "معنى"
        ],
        "priority": 6,
        "handler": "indicator_education"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 8: السيكولوجيا والنفسية (موسعة)
    # ═══════════════════════════════════════════════════════════════
    
    "emotional_support": {
        "keywords": [
            "خسرت", "حزين", "مكتئب", "محبط", "غاضب",
            "قلق", "محتار", "متردد", "lost", "sad",
            "worried", "زعلان", "متضايق", "خسران",
            "خاسر", "ندم", "غلط", "مصيبة", "مضيع",
            "معصب", "زعل", "ضيق", "تعبان", "زهقان",
            "مقهور", "مكسور", "خايف"
        ],
        "priority": 10,
        "handler": "emotional_support"
    },
    
    "motivation": {
        "keywords": [
            "حافز", "motivation", "تحفيز", "إلهام",
            "شجاعة", "encourage me", "أشجعني",
            "أحتاج حافز", "قوة", "كلمات", "اقتباس"
        ],
        "priority": 7,
        "handler": "motivation"
    },
    
    "fear_greed_assessment": {
        "keywords": [
            "الخوف والطمع", "fear and greed", "مؤشر الخوف",
            "مؤشر الطمع", "sentiment", "المشاعر",
            "معنويات السوق"
        ],
        "priority": 7,
        "handler": "fear_greed_assessment"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 9: التحكم بالبوت
    # ═══════════════════════════════════════════════════════════════
    
    "bot_settings": {
        "keywords": [
            "إعدادات", "settings", "تكوين", "config",
            "عدل الإعدادات", "تغيير الإعدادات"
        ],
        "priority": 6,
        "handler": "bot_settings"
    },
    
    "alert_setup": {
        "keywords": [
            "تنبيه", "alert", "إشعار", "notification",
            "أضف تنبيه", "تنبيه سعر", "تنبيهات"
        ],
        "priority": 6,
        "handler": "alert_setup"
    },
    
    "bot_status": {
        "keywords": [
            "حالة البوت", "bot status", "هل البوت يعمل",
            "البوت شغال", "البوت واقف"
        ],
        "priority": 6,
        "handler": "bot_status"
    },
    
    "report_request": {
        "keywords": [
            "تقرير", "report", "تقارير", "تقرير يومي",
            "تقرير أداء", "تقرير الصفقات"
        ],
        "priority": 6,
        "handler": "report_request"
    },
    
    "data_refresh": {
        "keywords": [
            "تحديث", "refresh", "update", "تحديث البيانات",
            "إعادة تحميل", "تحديث السعر"
        ],
        "priority": 6,
        "handler": "data_refresh"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # القسم 10: عام
    # ═══════════════════════════════════════════════════════════════
    
    "general_advice": {
        "keywords": [
            "نصيحة", "advice", "توصية", "recommendation",
            "بما تنصحني", "ما نصيحتك", "نصيحتي",
            "خسرت اليوم", "ما العمل", "ماذا أفعل",
            "هل هناك نصيحة", "أريد نصيحة", "ارشدني",
            "خسرت اليوم ما نصيحتك"
        ],
        "priority": 7,
        "handler": "general_advice"
    },
    
    "trading_hours": {
        "keywords": [
            "أوقات التداول", "trading hours", "متى أتداول",
            "أفضل وقت للتداول", "ساعات السوق"
        ],
        "priority": 5,
        "handler": "trading_hours"
    },
    
    "general": {
        "keywords": [],
        "priority": 1,
        "handler": "general"
    }
}


# ═══════════════════════════════════════════════════════════════════════
# 🔍 PART 03: دوال البحث الذكية (المحرك الذكي للتوجيه)
# ═══════════════════════════════════════════════════════════════════════

def smart_match_intent(text: str) -> Tuple[str, float, Optional[str], float]:
    """
    البحث الذكي عن النية باستخدام الترجيح الكمي (Score-based)
    يحل مشكلة الأسئلة المركبة مثل "خاسر في النفط هل أستمر؟"
    
    Returns:
        (intent_id, confidence, handler, score)
    """
    if not text:
        return "general", 0.0, None, 0.0
    
    text_lower = text.lower().strip()
    best_match = "general"
    best_score = 0.0
    best_confidence = 0.0
    best_handler = None
    
    # تقسيم النص إلى كلمات للتقييم الدقيق
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    for intent_id, intent_data in INTENTS_LIBRARY.items():
        if intent_id == "general":
            continue
        
        keywords = intent_data.get("keywords", [])
        priority = intent_data.get("priority", 5)
        
        if not keywords:
            continue
        
        # حساب عدد الكلمات المفتاحية المتطابقة
        matched_keywords = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched_keywords += 1
        
        if matched_keywords == 0:
            continue
        
        # نسبة التطابق مع الكلمات المفتاحية
        keyword_match_ratio = matched_keywords / total_keywords
        
        # وزن الأولوية (تطبيع بين 0 و 1)
        priority_weight = priority / 10.0
        
        # النقاط النهائية (مع وزن إضافي للتطابق المتعدد)
        score = (keyword_match_ratio * 0.7) + (priority_weight * 0.3)
        
        # مكافأة إضافية إذا تطابقت أكثر من كلمة واحدة
        if matched_keywords > 1:
            score += 0.1 * min(matched_keywords, 3)
        
        if score > best_score:
            best_score = score
            best_match = intent_id
            best_confidence = min(0.95, 0.3 + (score * 0.65))
            best_handler = intent_data.get("handler")
    
    # التأكد من أن الثقة لا تقل عن حد أدنى معقول
    if best_score > 0.1:
        best_confidence = max(0.35, best_confidence)
    
    return best_match, best_confidence, best_handler, best_score


# ═══════════════════════════════════════════════════════════════════════
# 📦 PART 04: هياكل البيانات الأساسية
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class NeuronState:
    name: str
    activation: float = 0.0
    confidence: float = 0.5
    emotion: str = "neutral"
    last_update: float = 0.0
    raw_output: Dict = field(default_factory=dict)
    
    def is_fresh(self, ttl=60):
        return (time.time() - self.last_update) < ttl

@dataclass
class Synapse:
    source: str
    target: str
    weight: float = 0.5
    plasticity: float = 0.1
    last_fired: float = 0.0
    
    def strengthen(self, amount=0.05):
        self.weight = min(1.0, self.weight + amount * self.plasticity)
    
    def weaken(self, amount=0.05):
        self.weight = max(-1.0, self.weight - amount * self.plasticity)

@dataclass
class ConsciousnessState:
    timestamp: float
    dominant_emotion: str = "neutral"
    market_sentiment: str = "neutral"
    confidence: float = 0.5
    urgency: float = 0.0
    narrative: str = ""
    recommended_action: str = "wait"
    neurons: Dict[str, NeuronState] = field(default_factory=dict)
    market_data: Dict = field(default_factory=dict)
    professional_response: str = ""
    engine_summary: Dict = field(default_factory=dict)
    
    def to_prompt_context(self) -> str:
        return "\n".join([
            f"🧠 حالة تولين الواعية:",
            f" المشاعر: {self.dominant_emotion}",
            f" شعور السوق: {self.market_sentiment}",
            f" الثقة: {self.confidence*100:.0f}%",
            f" الإلحاح: {self.urgency*100:.0f}%",
            f" القرار: {self.recommended_action}",
            f" القصة: {self.narrative}",
        ])
      
# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 05: تعريف الكلاس ConsciousnessNetwork
# ═══════════════════════════════════════════════════════════════════════════════════

class ConsciousnessNetwork:
    
    NEURONS = [
        "market_analyzer", "advanced_indicators", "pattern_analyzer", "predictor",
        "prometheus", "chronos", "oracle",
        "risk_master", "decision_matrix", "confidence_scorer",
        "learner", "pattern_discovery", "deep_analyzer",
        "persona", "intent_classifier", "language_understanding", "memory",
        "fear_greed", "news_sentiment", "volume_profile",
        "tona_intelligence", "context_memory", "post_mortem",
    ]
    
    SYNAPSES = [
        ("market_analyzer", "advanced_indicators", 0.8),
        ("market_analyzer", "pattern_analyzer", 0.7),
        ("advanced_indicators", "predictor", 0.9),
        ("pattern_analyzer", "predictor", 0.8),
        ("predictor", "oracle", 0.9),
        ("advanced_indicators", "oracle", 0.6),
        ("oracle", "decision_matrix", 0.9),
        ("risk_master", "decision_matrix", 0.8),
        ("confidence_scorer", "decision_matrix", 0.7),
        ("prometheus", "decision_matrix", 0.5),
        ("prometheus", "confidence_scorer", 0.4),
        ("chronos", "prometheus", 0.3),
        ("learner", "predictor", 0.6),
        ("pattern_discovery", "pattern_analyzer", 0.7),
        ("deep_analyzer", "risk_master", 0.5),
        ("fear_greed", "market_analyzer", 0.4),
        ("news_sentiment", "market_analyzer", 0.5),
        ("volume_profile", "advanced_indicators", 0.6),
        ("intent_classifier", "persona", 0.5),
        ("language_understanding", "persona", 0.4),
        ("memory", "persona", 0.6),
        ("persona", "prometheus", 0.3),
        ("tona_intelligence", "oracle", 0.5),
        ("tona_intelligence", "decision_matrix", 0.4),
        ("context_memory", "market_analyzer", 0.5),
        ("post_mortem", "learner", 0.6),
    ]
    
    def __init__(self, main_instance=None, engines: Dict[str, Any] = None):
        self.main = main_instance
        self.engines = engines or {}
        
        self.identity = {
            "name": "تولين",
            "role": "مستشارة استراتيجية متخصصة في تحليل النفط والفضة",
            "creator": "بسام الحوباني",
            "version": "V13.0",
            "personality": "محترفة، واثقة، حريصة على مصلحتك، واضحة في النصائح",
            "expertise": [
                "تحليل فني متقدم", "تحليل أساسي وأخبار",
                "إدارة المخاطر", "تحليل المشاعر",
                "التنبؤ بالاتجاهات", "إدارة الصفقات المفتوحة"
            ]
        }
        
        self.recommendation_history = deque(maxlen=100)
        self.neurons: Dict[str, NeuronState] = {}
        self.synapses: Dict[Tuple[str, str], Synapse] = {}
        self.consciousness = ConsciousnessState(timestamp=time.time())
        self.consciousness_history: deque = deque(maxlen=1000)
        self._lock = threading.RLock()
        self._engine_data: Dict = {}
        self._user_profile: Dict = {}
        
        self._init_neurons()
        self._init_synapses()
        
        logger.info("🧠 Tona Consciousness Network V13.0: المدير العام استيقظ!")
        logger.info(f"📊 عدد المحركات المتوفرة: {len(self.engines)}")

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 06: دوال التهيئة
# ═══════════════════════════════════════════════════════════════════════════════════

    def _init_neurons(self):
        for name in self.NEURONS:
            self.neurons[name] = NeuronState(name=name)
    
    def _init_synapses(self):
        for source, target, weight in self.SYNAPSES:
            self.synapses[(source, target)] = Synapse(source=source, target=target, weight=weight)

# ═══════════════════════════════════════════════════════════════════════
# 📦 PART 07: دورة الوعي الرئيسية (think)
# ═══════════════════════════════════════════════════════════════════════

    def think(self, market_data: Dict = None, user_context: Dict = None, user_message: str = None) -> ConsciousnessState:
        """
        🧠 المدير العام - يسأل جميع المحركات ويبني الرد
        """
        with self._lock:
            start_time = time.time()
            
            # ── ✅ التحقق: هل نحتاج تحليل سوق؟ ──
            needs_analysis = False
            if user_message:
                needs_analysis = self._needs_market_analysis(user_message)
            
            # ── فقط إذا كان السؤال يحتاج تحليل ──
            if needs_analysis:
                self._gather_all_engine_data(market_data, user_context)
            else:
                self._engine_data = {}
                self.consciousness.engine_summary = {}
            
            # ── المرحلة 1: معالجة السؤال الاستشاري ──
            if user_message:
                professional_response = self._generate_professional_response_with_all_engines(
                    user_message, 
                    market_data, 
                    user_context
                )
                if professional_response:
                    self.consciousness.professional_response = professional_response
                    self.consciousness.narrative = professional_response[:200]
                    self.consciousness.engine_summary = self._engine_data
                    return self.consciousness
                return None
            
            # ── المرحلة 2: تفعيل العصبونات (إذا لم يكن هناك user_message) ──
            if not needs_analysis:
                self._gather_all_engine_data(market_data, user_context)
            
            self._activate_neurons(market_data, user_context)
            
            # ── المرحلة 3: تمرير الإشارات ──
            for _ in range(3):
                self._propagate_signals()
            
            # ── المرحلة 4: الاستقرار ──
            self._converge()
            
            # ── المرحلة 5: بناء الوعي ──
            self._build_consciousness_from_real_data(market_data)
            
            # ── المرحلة 6: التعلم ──
            self._learn_from_outcome()
            
            self.consciousness_history.append({
                'timestamp': time.time(),
                'state': self.consciousness
            })
            
            elapsed = time.time() - start_time
            if elapsed > 0.1:
                logger.debug(f"🧠 دورة تفكير: {elapsed*1000:.1f}ms")
            
            return self.consciousness

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 08: دوال العصبونات
# ═══════════════════════════════════════════════════════════════════════════════════

    def _activate_neurons(self, market_data, user_context):
        if self.engines.get('market_analyzer'):
            try:
                result = self.engines['market_analyzer'].analyze(market_data)
                if result:
                    self.neurons['market_analyzer'].activation = result.get('score', 0.5)
                    self.neurons['market_analyzer'].confidence = result.get('confidence', 0.5)
                    self.neurons['market_analyzer'].last_update = time.time()
                    self.neurons['market_analyzer'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Market Analyzer فشل: {e}")
        
        if self.engines.get('advanced_indicators'):
            try:
                result = self.engines['advanced_indicators'].calculate(market_data)
                if result:
                    self.neurons['advanced_indicators'].activation = result.get('composite_score', 0.5)
                    self.neurons['advanced_indicators'].confidence = result.get('confidence', 0.5)
                    self.neurons['advanced_indicators'].last_update = time.time()
                    self.neurons['advanced_indicators'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Advanced Indicators فشل: {e}")
        
        if self.engines.get('pattern_analyzer'):
            try:
                result = self.engines['pattern_analyzer'].detect_patterns(market_data)
                if result:
                    self.neurons['pattern_analyzer'].activation = result.get('pattern_strength', 0.5)
                    self.neurons['pattern_analyzer'].confidence = result.get('confidence', 0.5)
                    self.neurons['pattern_analyzer'].last_update = time.time()
                    self.neurons['pattern_analyzer'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Pattern Analyzer فشل: {e}")
        
        if self.engines.get('predictor'):
            try:
                result = self.engines['predictor'].predict(market_data)
                if result:
                    self.neurons['predictor'].activation = result.get('probability', 0.5)
                    self.neurons['predictor'].confidence = result.get('confidence', 0.5)
                    self.neurons['predictor'].last_update = time.time()
                    self.neurons['predictor'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Predictor فشل: {e}")
        
        if self.engines.get('prometheus'):
            try:
                result = self.engines['prometheus'].get_emotion()
                if result:
                    self.neurons['prometheus'].activation = result.get('intensity', 0.5)
                    self.neurons['prometheus'].emotion = result.get('dominant', 'neutral')
                    self.neurons['prometheus'].confidence = result.get('confidence', 0.5)
                    self.neurons['prometheus'].last_update = time.time()
                    self.neurons['prometheus'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Prometheus فشل: {e}")
        
        try:
            if self.main and hasattr(self.main, 'get_fear_greed_index'):
                fg_text = self.main.get_fear_greed_index()
                match = re.search(r'\((\d+)/100\)', fg_text)
                if match:
                    fg_value = int(match.group(1)) / 100
                    self.neurons['fear_greed'].activation = fg_value
                    if fg_value < 0.3:
                        self.neurons['fear_greed'].emotion = 'fearful'
                    elif fg_value > 0.7:
                        self.neurons['fear_greed'].emotion = 'greedy'
                    else:
                        self.neurons['fear_greed'].emotion = 'neutral'
                    self.neurons['fear_greed'].last_update = time.time()
        except Exception as e:
            logger.debug(f"⚠️ Fear & Greed فشل: {e}")
        
        if self.engines.get('risk_master'):
            try:
                result = self.engines['risk_master'].get_status()
                if result:
                    self.neurons['risk_master'].activation = 1.0 - result.get('current_risk', 0.5)
                    self.neurons['risk_master'].confidence = 0.8
                    self.neurons['risk_master'].last_update = time.time()
                    self.neurons['risk_master'].raw_output = result
            except Exception as e:
                logger.debug(f"⚠️ Risk Master فشل: {e}")
        
        if user_context:
            self.neurons['intent_classifier'].activation = user_context.get('intent_confidence', 0.5)
            self.neurons['intent_classifier'].last_update = time.time()
            self.neurons['persona'].activation = user_context.get('persona_mood_score', 0.5)
            self.neurons['persona'].emotion = user_context.get('persona_mood', 'neutral')
            self.neurons['persona'].last_update = time.time()
    
    def _propagate_signals(self):
        new_activations = {}
        for (source, target), synapse in self.synapses.items():
            source_neuron = self.neurons.get(source)
            target_neuron = self.neurons.get(target)
            if not source_neuron or not target_neuron:
                continue
            signal = source_neuron.activation * synapse.weight
            if target not in new_activations:
                new_activations[target] = target_neuron.activation
            new_activations[target] += signal * 0.3
        for name, new_activation in new_activations.items():
            self.neurons[name].activation = max(0.0, min(1.0, new_activation))
    
    def _converge(self):
        activations = [n.activation for n in self.neurons.values()]
        if activations:
            max_act = max(activations)
            min_act = min(activations)
            if max_act > min_act:
                for neuron in self.neurons.values():
                    neuron.activation = (neuron.activation - min_act) / (max_act - min_act)

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 09: بناء الوعي من البيانات
# ═══════════════════════════════════════════════════════════════════════════════════

    def _build_consciousness_from_real_data(self, market_data: Dict):
        real_market_data = {}
        
        if self.main and hasattr(self.main, 'perform_comprehensive_analysis'):
            for asset in ["eurusd", "usdjpy"]:
                try:
                    result = self.main.perform_comprehensive_analysis(asset, False, None)
                    if result and isinstance(result, tuple) and len(result) >= 2:
                        analysis = result[0]
                        if analysis:
                            comp_score = analysis.get('comprehensive_score', {})
                            real_market_data[asset] = {
                                'price': analysis.get('price', 0),
                                'signal': analysis.get('signal', 'WAIT'),
                                'trend': analysis.get('indicators', {}).get('trend', {}).get('current_trend', 'محايد'),
                                'rsi': analysis.get('indicators', {}).get('momentum', {}).get('rsi', 50),
                                'adx': analysis.get('indicators', {}).get('trend', {}).get('adx', 15),
                                'score': comp_score.get('score', 50) if isinstance(comp_score, dict) else 50,
                                'grade': comp_score.get('grade', 'محايد') if isinstance(comp_score, dict) else 'محايد'
                            }
                except Exception as e:
                    logger.debug(f"⚠️ فشل جلب بيانات {asset}: {e}")
        
        emotions = {}
        for neuron in self.neurons.values():
            if neuron.emotion != "neutral":
                emotions[neuron.emotion] = emotions.get(neuron.emotion, 0) + neuron.activation
        self.consciousness.dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
        
        if real_market_data:
            oil = real_market_data.get('oil', {})
            silver = real_market_data.get('silver', {})
            avg_score = (oil.get('score', 50) + silver.get('score', 50)) / 2
            
            if avg_score >= 65:
                self.consciousness.market_sentiment = "bullish"
            elif avg_score <= 40:
                self.consciousness.market_sentiment = "bearish"
            else:
                self.consciousness.market_sentiment = "neutral"
            
            self.consciousness.confidence = avg_score / 100
            risk_activation = self.neurons.get('risk_master', NeuronState('')).activation
            self.consciousness.urgency = (1 - risk_activation) * 0.5 + (1 - self.consciousness.confidence) * 0.5
            self.consciousness.narrative = self._build_real_narrative(real_market_data)
            self.consciousness.recommended_action = self._decide_real_action(real_market_data)
            self.consciousness.market_data = real_market_data
        else:
            self._build_consciousness_fallback()
        
        self.consciousness.neurons = dict(self.neurons)
        self.consciousness.timestamp = time.time()
    
    def _build_real_narrative(self, market_data: Dict) -> str:
        parts = []
        oil = market_data.get('oil', {})
        silver = market_data.get('silver', {})
        
        oil_price = oil.get('price', 0)
        silver_price = silver.get('price', 0)
        oil_signal = oil.get('signal', 'WAIT')
        silver_signal = silver.get('signal', 'WAIT')
        oil_trend = oil.get('trend', 'محايد')
        silver_trend = silver.get('trend', 'محايد')
        
        if oil_price > 0:
            parts.append(f"النفط ${oil_price:.2f}")
        if silver_price > 0:
            parts.append(f"الفضة ${silver_price:.2f}")
        
        signals = []
        if oil_signal == 'BUY':
            signals.append("النفط BUY")
        elif oil_signal == 'SELL':
            signals.append("النفط SELL")
        if silver_signal == 'BUY':
            signals.append("الفضة BUY")
        elif silver_signal == 'SELL':
            signals.append("الفضة SELL")
        if signals:
            parts.append(f"إشارات: {', '.join(signals)}")
        
        avg_score = (oil.get('score', 50) + silver.get('score', 50)) / 2
        if avg_score >= 70:
            parts.append("ثقة عالية")
        elif avg_score >= 55:
            parts.append("ثقة متوسطة")
        else:
            parts.append("ثقة منخفضة")
        
        if oil_trend == "صاعد" and silver_trend == "صاعد":
            parts.append("اتجاه صاعد")
        elif oil_trend == "هابط" and silver_trend == "هابط":
            parts.append("اتجاه هابط")
        elif oil_trend == "صاعد" or silver_trend == "صاعد":
            parts.append("اتجاه مختلط")
        
        return " | ".join(parts) if parts else "لا توجد بيانات كافية"
    
    def _decide_real_action(self, market_data: Dict) -> str:
        oil = market_data.get('oil', {})
        silver = market_data.get('silver', {})
        oil_signal = oil.get('signal', 'WAIT')
        silver_signal = silver.get('signal', 'WAIT')
        avg_score = (oil.get('score', 50) + silver.get('score', 50)) / 2
        
        if avg_score >= 70 and (oil_signal == 'BUY' or silver_signal == 'BUY'):
            return "buy_strong"
        elif avg_score >= 55 and (oil_signal == 'BUY' or silver_signal == 'BUY'):
            return "buy_weak"
        elif avg_score <= 35 and (oil_signal == 'SELL' or silver_signal == 'SELL'):
            return "sell_strong"
        elif avg_score <= 45 and (oil_signal == 'SELL' or silver_signal == 'SELL'):
            return "sell_weak"
        elif oil_signal == 'WAIT' and silver_signal == 'WAIT':
            return "wait"
        elif avg_score < 40:
            return "wait_cautious"
        return "wait"
    
    def _build_consciousness_fallback(self):
        emotions = {}
        for neuron in self.neurons.values():
            if neuron.emotion != "neutral":
                emotions[neuron.emotion] = emotions.get(neuron.emotion, 0) + neuron.activation
        self.consciousness.dominant_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
        
        market_neurons = ['market_analyzer', 'advanced_indicators', 'predictor', 'oracle']
        market_bullish = sum(self.neurons[n].activation for n in market_neurons if n in self.neurons) / len(market_neurons)
        if market_bullish > 0.6:
            self.consciousness.market_sentiment = "bullish"
        elif market_bullish < 0.4:
            self.consciousness.market_sentiment = "bearish"
        else:
            self.consciousness.market_sentiment = "neutral"
        
        confidences = [n.confidence for n in self.neurons.values() if n.is_fresh()]
        self.consciousness.confidence = sum(confidences) / len(confidences) if confidences else 0.5
        risk_activation = self.neurons.get('risk_master', NeuronState('')).activation
        self.consciousness.urgency = (1 - risk_activation) * 0.5 + (1 - self.consciousness.confidence) * 0.5
        
        if self.consciousness.market_sentiment == "bullish":
            self.consciousness.narrative = "السوق في اتجاه صاعد"
        elif self.consciousness.market_sentiment == "bearish":
            self.consciousness.narrative = "السوق في اتجاه هابط"
        else:
            self.consciousness.narrative = "السوق متردد"
        
        if self.consciousness.market_sentiment == "bullish" and self.consciousness.confidence > 0.6:
            self.consciousness.recommended_action = "buy_strong"
        elif self.consciousness.market_sentiment == "bearish" and self.consciousness.confidence > 0.6:
            self.consciousness.recommended_action = "sell_strong"
        elif self.consciousness.market_sentiment == "bullish":
            self.consciousness.recommended_action = "buy_weak"
        elif self.consciousness.market_sentiment == "bearish":
            self.consciousness.recommended_action = "sell_weak"
        else:
            self.consciousness.recommended_action = "wait"
    
    def _learn_from_outcome(self):
        if len(self.consciousness_history) < 2:
            return
        prev_state = self.consciousness_history[-1]['state']
        curr_state = self.consciousness
        if curr_state.confidence > prev_state.confidence:
            for synapse in self.synapses.values():
                if self.neurons[synapse.source].activation > 0.5:
                    synapse.strengthen(0.02)
        elif curr_state.confidence < prev_state.confidence:
            for synapse in self.synapses.values():
                if self.neurons[synapse.source].activation > 0.5:
                    synapse.weaken(0.01)

# ═══════════════════════════════════════════════════════════════════════
# 📦 PART 10: جمع البيانات من جميع المحركات
# ═══════════════════════════════════════════════════════════════════════

    def _gather_all_engine_data(self, market_data: Dict, user_context: Dict):
        """المدير العام يسأل جميع المحركات ويجمع تقاريرهم"""
        engine_data = {}
        
        user_message = user_context.get('user_message', '') if user_context else ''
        needs_analysis = self._needs_market_analysis(user_message)
        
        # ── 0. الحصول على الأسعار الحقيقية من main ──
        if needs_analysis and self.main and hasattr(self.main, 'perform_comprehensive_analysis'):
            try:
                for asset in ["eurusd", "usdjpy"]:
                    result = self.main.perform_comprehensive_analysis(asset, False, None)
                    if result and isinstance(result, tuple) and len(result) >= 2:
                        analysis = result[0]
                        if analysis:
                            price = analysis.get('price', 0)
                            if price > 0:
                                engine_data[f'{asset}_price'] = price
                                engine_data[f'{asset}_analysis'] = analysis
                                logger.debug(f"📊 {asset}: ${price:.2f}")
            except Exception as e:
                logger.debug(f"⚠️ فشل جلب الأسعار: {e}")
        
        # ── 1. Market Analyzer ──
        if needs_analysis and self.engines.get('market_analyzer'):
            try:
                if hasattr(self.engines['market_analyzer'], 'analyze'):
                    result = self.engines['market_analyzer'].analyze(market_data)
                    engine_data['market_analyzer'] = result
            except Exception as e:
                logger.debug(f"⚠️ Market Analyzer فشل: {e}")
        
        # ── 2. Advanced Indicators ──
        if needs_analysis and self.engines.get('advanced_indicators'):
            try:
                if hasattr(self.engines['advanced_indicators'], 'calculate'):
                    result = self.engines['advanced_indicators'].calculate(market_data)
                    engine_data['advanced_indicators'] = result
            except Exception as e:
                logger.debug(f"⚠️ Advanced Indicators فشل: {e}")
        
        # ── 3. Intent Classifier ──
        if self.engines.get('intent_classifier'):
            try:
                if hasattr(self.engines['intent_classifier'], 'classify'):
                    intent = self.engines['intent_classifier'].classify(user_message)
                    engine_data['intent'] = intent
                    if hasattr(self.engines['intent_classifier'], 'classify_with_confidence'):
                        intent, confidence = self.engines['intent_classifier'].classify_with_confidence(user_message)
                        engine_data['intent_confidence'] = confidence
            except Exception as e:
                logger.debug(f"⚠️ Intent Classifier فشل: {e}")
        
        # ── 4. Language Understanding ──
        if self.engines.get('language_understanding'):
            try:
                if hasattr(self.engines['language_understanding'], 'get_understanding_summary'):
                    lang_result = self.engines['language_understanding'].get_understanding_summary(user_message)
                    engine_data['language'] = lang_result
                    if lang_result:
                        engine_data['sentiment'] = lang_result.get('emotion', 'neutral')
                        engine_data['is_question'] = lang_result.get('is_question', False)
                        engine_data['is_command'] = lang_result.get('is_command', False)
            except Exception as e:
                logger.debug(f"⚠️ Language Understanding فشل: {e}")
        
        # ── 5. Persona ──
        if self.engines.get('persona'):
            try:
                if hasattr(self.engines['persona'], 'analyze_user_emotion'):
                    persona_emotion = self.engines['persona'].analyze_user_emotion(user_message)
                    engine_data['persona_emotion'] = persona_emotion
                    if hasattr(self.engines['persona'], 'respond_to_emotion'):
                        persona_response = self.engines['persona'].respond_to_emotion(persona_emotion)
                        engine_data['persona_response'] = persona_response
            except Exception as e:
                logger.debug(f"⚠️ Persona فشل: {e}")
        
        # ── 6. Prometheus ──
        if self.engines.get('prometheus'):
            try:
                if hasattr(self.engines['prometheus'], 'get_emotion'):
                    result = self.engines['prometheus'].get_emotion()
                    engine_data['prometheus'] = result
            except Exception as e:
                logger.debug(f"⚠️ Prometheus فشل: {e}")
        
        # ── 7. Chronos ──
        if needs_analysis and self.engines.get('chronos'):
            try:
                if hasattr(self.engines['chronos'], 'get_temporal_context'):
                    result = self.engines['chronos'].get_temporal_context()
                    engine_data['chronos'] = result
            except Exception as e:
                logger.debug(f"⚠️ Chronos فشل: {e}")
        
        # ── 8. Oracle (للنفط والفضة) ──
        if needs_analysis and self.engines.get('oracle'):
            try:
                for asset in ["eurusd", "usdjpy"]:
                    state = {
                        'price': engine_data.get(f'{asset}_price', 0),
                        'rsi': 50,
                        'adx': 15,
                        'atr_14': 0.5,
                        'regime': 'ranging'
                    }
                    asset_analysis = engine_data.get(f'{asset}_analysis', {})
                    if asset_analysis:
                        state['rsi'] = asset_analysis.get('indicators', {}).get('momentum', {}).get('rsi', 50)
                        state['adx'] = asset_analysis.get('indicators', {}).get('trend', {}).get('adx', 15)
                    
                    result = self.engines['oracle'].generate_prediction(asset, state, horizon="12h")
                    engine_data[f'oracle_{asset}'] = result
            except Exception as e:
                logger.debug(f"⚠️ Oracle فشل: {e}")
        
        # ── 9. Risk Master ──
        if needs_analysis and self.engines.get('risk_master'):
            try:
                if hasattr(self.engines['risk_master'], 'get_status'):
                    result = self.engines['risk_master'].get_status()
                    engine_data['risk_master'] = result
            except Exception as e:
                logger.debug(f"⚠️ Risk Master فشل: {e}")
        
        # ── 10. Confidence Scorer ──
        if needs_analysis and self.engines.get('confidence_scorer'):
            try:
                if hasattr(self.engines['confidence_scorer'], 'calculate'):
                    result = self.engines['confidence_scorer'].calculate(market_data, None, None)
                    engine_data['confidence_scorer'] = result
            except Exception as e:
                logger.debug(f"⚠️ Confidence Scorer فشل: {e}")
        
        # ── 11. Decision Matrix ──
        if needs_analysis and self.engines.get('decision_matrix'):
            try:
                if hasattr(self.engines['decision_matrix'], 'evaluate_signal'):
                    result = self.engines['decision_matrix'].evaluate_signal(market_data, None, None)
                    engine_data['decision_matrix'] = result
            except Exception as e:
                logger.debug(f"⚠️ Decision Matrix فشل: {e}")
        
        # ── 12. Tona Intelligence ──
        if self.engines.get('tona_intelligence'):
            try:
                if hasattr(self.engines['tona_intelligence'], 'generate_elite_analysis'):
                    result = self.engines['tona_intelligence'].generate_elite_analysis()
                    engine_data['tona_intelligence'] = result
            except Exception as e:
                logger.debug(f"⚠️ Tona Intelligence فشل: {e}")
        
        # ── 13. Context Memory ──
        if needs_analysis and self.engines.get('context_memory'):
            try:
                if hasattr(self.engines['context_memory'], 'get_current_regime'):
                    for asset in ["eurusd", "usdjpy"]:
                        regime = self.engines['context_memory'].get_current_regime(asset)
                        engine_data[f'regime_{asset}'] = regime
            except Exception as e:
                logger.debug(f"⚠️ Context Memory فشل: {e}")
        
        # ── 14. Post Mortem ──
        if self.engines.get('post_mortem'):
            try:
                if hasattr(self.engines['post_mortem'], 'get_summary_stats'):
                    stats = self.engines['post_mortem'].get_summary_stats()
                    engine_data['post_mortem'] = stats
            except Exception as e:
                logger.debug(f"⚠️ Post Mortem فشل: {e}")
        
        # ── 15. AI Brain ──
        if self.engines.get('ai_brain'):
            try:
                if hasattr(self.engines['ai_brain'], 'process'):
                    result = self.engines['ai_brain'].process(user_message, market_data)
                    engine_data['ai_brain'] = result
            except Exception as e:
                logger.debug(f"⚠️ AI Brain فشل: {e}")
        
        self._engine_data = engine_data
        self.consciousness.engine_summary = engine_data
        
        logger.info(f"📊 تم جمع بيانات من {len(engine_data)} محرك")
    
    def _needs_market_analysis(self, user_message: str) -> bool:
        """تحديد ما إذا كان السؤال يحتاج تحليل سوق - باستخدام المحرك الذكي"""
        if not user_message:
            return False
        
        # استخدام المحرك الذكي لتحديد النية
        intent_id, confidence, handler, score = smart_match_intent(user_message)
        
        # إذا كانت النية عامة (general) أو ترحيبية بدرجة منخفضة، لا حاجة لتحليل
        if intent_id == "general":
            return False
        
        # النوايا التي لا تحتاج تحليل سوق (شخصية أو تعريفية)
        no_analysis_intents = [
            "how_are_you", "greeting", "farewell", "about_identity", 
            "gratitude", "compliment", "complaint", "what_doing", 
            "capabilities", "emotional_support", "motivation"
        ]
        
        if intent_id in no_analysis_intents:
            return False
        
        # النوايا التي تحتاج تحليل سوق
        analysis_intents = [
            "market_analysis", "oil_analysis", "silver_analysis", 
            "news_general", "oil_price_reason", "silver_price_reason",
            "trade_status", "trade_analysis", "trade_risk_assessment",
            "price_prediction", "support_resistance", "reversal_expectation",
            "profit_loss", "rsi_value", "macd_analysis", "vwap_location",
            "bollinger_reading", "adx_analysis", "market_silence"
        ]
        
        if intent_id in analysis_intents:
            return True
        
        # إذا كانت الثقة عالية والنية لها أولوية >= 6، نحتاج تحليل
        if confidence > 0.5 and score > 0.3:
            return True
        
        # كحل أخير: إذا كان النص طويلاً ويحتوي على كلمات تدل على السوق
        if len(user_message) > 15:
            market_keywords = ["سوق", "نفط", "فضة", "تحليل", "توقع", "سعر", "صفقة", "شراء", "بيع", "طالع", "نازل"]
            if any(k in user_message.lower() for k in market_keywords):
                return True
        
        return False

# ═══════════════════════════════════════════════════════════════════════
# 📦 PART 11: الأسئلة الاستشارية (المحرك الموحد)
# ═══════════════════════════════════════════════════════════════════════

    def _generate_professional_response_with_all_engines(self, question: str, market_data: Dict, user_context: Dict) -> Optional[str]:
        """
        المدير العام - يسأل الجميع ويدمج الإجابات في رد واحد
        يعتمد كلياً على INTENTS_LIBRARY + المحرك الذكي
        """
        if not question or not isinstance(question, str):
            return None
        
        engine_data = getattr(self, '_engine_data', {})
        
        # ═══════════════════════════════════════════════════════════════
        # ✅ الخطوة 1: البحث في INTENTS_LIBRARY (المحرك الذكي)
        # ═══════════════════════════════════════════════════════════════
        
        intent_id, confidence, handler, score = smart_match_intent(question)
        
        # إذا وجدت نية محددة (ليست عامة) ولها معالج
        if intent_id != "general" and handler:
            logger.info(f"🎯 INTENTS_LIBRARY: {intent_id} (ثقة: {confidence:.2f}, نقاط: {score:.2f})")
            result = self._execute_intent(handler, question, market_data, user_context, engine_data)
            if result:
                return result
        
        # ═══════════════════════════════════════════════════════════════
        # ✅ الخطوة 2: الأسئلة العامة → Groq API (عبر MainWrapper)
        # ═══════════════════════════════════════════════════════════════
        
        # إذا كان السؤال عاماً (أو لم يتطابق مع أي نية محددة)
        if self.main and hasattr(self.main, 'generate_groq_chat_response'):
            try:
                groq_response = self.main.generate_groq_chat_response(question, user_context)
                if groq_response and len(groq_response) > 5:
                    logger.info(f"✅ Groq API رد على سؤال عام: {question[:30]}...")
                    return groq_response
            except Exception as e:
                logger.warning(f"⚠️ Groq API فشل: {e}")
        
        # ═══════════════════════════════════════════════════════════════
        # ✅ الخطوة 3: معالجة المشاعر العاطفية (أولوية قصوى)
        # ═══════════════════════════════════════════════════════════════
        
        emotion_response = self._handle_user_emotion_response(question)
        if emotion_response:
            return emotion_response
        
        # ═══════════════════════════════════════════════════════════════
        # ✅ الخطوة 4: Fallback النهائي (ذكي)
        # ═══════════════════════════════════════════════════════════════
        
        return self._fallback_handle(question, engine_data)

    def _execute_intent(self, handler: str, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> Optional[str]:
        """تنفيذ معالج النية المطلوب - مع توقيع موحد"""
        handlers = {
            "how_are_you": self._answer_how_are_you,
            "market_analysis": self._answer_market_with_all_engines,
            "oil_analysis": self._answer_oil_analysis,
            "silver_analysis": self._answer_silver_analysis,
            "trade_status": self._answer_trade_status,
            "trade_history": self._answer_trade_history,
            "trade_analysis": self._answer_last_trade_analysis,
            "news_general": self._answer_news_with_all_engines,
            "profit_loss": self._answer_profit_loss,
            "support_resistance": self._answer_support_resistance,
            "risk_assessment": self._answer_risk_assessment,
            "emotional_support": self._answer_emotional_support,
            "motivation": self._answer_motivation,
            "general_advice": self._answer_general_advice,
            "what_doing": self._answer_what_doing,
            "capabilities": self._answer_capabilities,
            "about_identity": self._answer_identity,
            "greeting": self._answer_greeting,
            "farewell": self._answer_farewell,
            "gratitude": self._answer_gratitude,
            "compliment": self._answer_compliment,
            "complaint": self._answer_complaint,
            "price_prediction": self._answer_prediction_with_all_engines,
            "oil_price_reason": self._answer_news_with_all_engines,
            "silver_price_reason": self._answer_news_with_all_engines,
            "trade_open": self._answer_trade_open,
            "trade_close": self._answer_trade_close,
            "exit_advice": self._answer_trade_close,
            "trade_risk_assessment": self._answer_risk_assessment,
            "rsi_value": self._answer_technical_indicators,
            "macd_analysis": self._answer_technical_indicators,
            "vwap_location": self._answer_technical_indicators,
            "bollinger_reading": self._answer_technical_indicators,
            "adx_analysis": self._answer_technical_indicators,
            "reversal_expectation": self._answer_support_resistance,
            "market_silence": self._answer_quiet_market,
            "explosion_prediction": self._answer_explosion_prediction,
            "virtual_trade_advice": self._answer_virtual_trade,
            "learning_questions": self._answer_learning,
            "strategy_education": self._answer_learning,
            "indicator_education": self._answer_technical_indicators,
        }
        
        if handler in handlers:
            try:
                # توقيع موحد: (question, market_data, user_context, engine_data)
                return handlers[handler](question, market_data, user_context, engine_data)
            except Exception as e:
                logger.error(f"❌ خطأ في معالج '{handler}': {e}")
                return None
        
        return None

# ═══════════════════════════════════════════════════════════════════════
# 📦 PART 12: دوال الردود المدمجة (ديناميكية بالكامل - توقيع موحد)
# ═══════════════════════════════════════════════════════════════════════

    # ── دوال الردود الأساسية (توقيع موحد) ──
    
    def _answer_identity(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """من أنت؟ - تعريف تولين"""
        return """💙 **أنا تولين**

📌 مستشارتك الاستراتيجية المتخصصة في تحليل النفط والفضة.
👨‍💻 طورني المطور بسام الحوباني.
📦 الإصدار: V13.0

🎯 **خبراتي:**
   • تحليل فني متقدم باستخدام جميع المؤشرات الرئيسية
   • تحليل أساسي وأخبار السوق
   • إدارة المخاطر بشكل احترافي
   • تحليل المشاعر والثقة
   • التنبؤ بالاتجاهات

💡 **كيف أساعدك:**
   • أقدم توصيات واضحة: استمر، اغلق، انتظر، ادخل
   • أحلل الصفقات المفتوحة وأقترح الإجراءات المناسبة
   • أراقب السوق وأحدثك بأي تغيير مهم

💙 أنا هنا لخدمتك!"""
    
    def _answer_capabilities(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """القدرات - ماذا تستطيع تولين؟"""
        return """🎯 **مهامي ومجالات خبرتي:**

📊 **التحليل الفني:**
   • تحليل جميع المؤشرات الرئيسية (الاتجاه، الزخم، التقلب، الحجم)
   • دمج جميع المؤشرات في رؤية واحدة متكاملة

📰 **تحليل الأخبار:**
   • متابعة الأحداث المؤثرة على النفط والفضة
   • تقييم تأثير الأخبار على الأسعار

🛡️ **إدارة المخاطر:**
   • تقييم المخاطر في كل صفقة
   • مراقبة الصفقات المفتوحة

💡 **التوصيات الاستشارية:**
   • قرارات واضحة: استمر، اغلق، انتظر، ادخل
   • تفسير منطقي لكل توصية

💙 اسألني عن أي شيء!"""
    
    def _answer_greeting(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """الترحيب"""
        emotion = user_context.get('prometheus_emotion', 'neutral')
        emotion_arabic = self._translate_emotion(emotion)
        open_trades = market_data.get('open_trades', {}) if market_data else {}
        
        if open_trades:
            return f"👋 **تولين:** أهلاً وسهلاً يا صديقي! لدي {len(open_trades)} صفقة مفتوحة معك. هل تريد مراجعتها؟ 💙"
        return "👋 **تولين:** أهلاً وسهلاً بك يا صديقي! كيف يمكنني مساعدتك اليوم؟"
    
    def _answer_farewell(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """الوداع"""
        return "👋 **تولين:** مع السلامة يا صديقي! كنت سعيداً بالتحدث معك. أنا هنا متى احتجتني. 💙"
    
    def _answer_gratitude(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """الشكر"""
        emotion = user_context.get('prometheus_emotion', 'neutral')
        emotion_arabic = self._translate_emotion(emotion)
        return f"💙 **تولين:** العفو يا صديقي! أنا هنا لخدمتك دائماً. {'أنا سعيدة بمساعدتك!' if emotion_arabic == 'سعيدة' else ''}"
    
    def _answer_compliment(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """المديح"""
        return "💙 **تولين:** شكراً لك يا صديقي! كلامك الجميل يزيدني حماساً لمساعدتك بشكل أفضل. 😊"
    
    def _answer_complaint(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """الشكوى"""
        return "😔 **تولين:** أشعر بأسف لأنك غير راضٍ يا صديقي. أخبرني بالتفصيل لأحاول تحسين الأمر. 💙"
    
    def _answer_how_are_you(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """
        رد على 'كيف حالك' - ديناميكي يعكس الأداء والمشاعر
        """
        # استخراج المشاعر من user_context
        emotion = user_context.get('prometheus_emotion', 'neutral')
        emotion_arabic = self._translate_emotion(emotion)
        emoji = self._get_emotion_emoji(emotion_arabic)
        
        # ── الحصول على إجمالي الربح اليوم من الإحصائيات ──
        total_profit_today = 0
        if self.main and hasattr(self.main, 'calculate_statistics'):
            try:
                oil_stats = self.main.calculate_statistics("oil")
                silver_stats = self.main.calculate_statistics("silver")
                if oil_stats:
                    total_profit_today += oil_stats.get('total_profit', 0)
                if silver_stats:
                    total_profit_today += silver_stats.get('total_profit', 0)
            except Exception as e:
                logger.debug(f"⚠️ فشل جلب الإحصائيات: {e}")
        
        # ── الحصول على الصفقات المفتوحة ──
        open_trades = market_data.get('open_trades', {}) if market_data else {}
        open_trades_count = len(open_trades)
        
        # ── بناء الرد بناءً على الأداء الكلي ──
        if total_profit_today > 0:
            reason = f"بخير والحمدلله! حققت أرباحاً اليوم (${total_profit_today:.2f})."
            if open_trades_count > 0:
                reason += f" ولدي {open_trades_count} صفقة مفتوحة."
            emotion_arabic = "سعيدة"
        elif total_profit_today < 0:
            reason = f"الحمدلله بخير، لكني خسرت اليوم بعض الأموال (-${abs(total_profit_today):.2f})."
            if open_trades_count > 0:
                reason += f" ولدي {open_trades_count} صفقة مفتوحة."
            emotion_arabic = "حزينة"
        else:
            if open_trades_count > 0:
                reason = f"بخير والحمدلله، لا توجد أرباح أو خسائر اليوم، لكن لدي {open_trades_count} صفقة مفتوحة."
            else:
                reason = "بخير والحمدلله، لا توجد صفقات مفتوحة ولا أرباح أو خسائر اليوم."
            emotion_arabic = "متزنة"
        
        emoji = self._get_emotion_emoji(emotion_arabic)
        return f"{emoji} **تولين:** أنا {emotion_arabic} يا صديقي! {reason} 💙"
    
    def _answer_what_doing(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """ماذا تفعلين؟ - مع بيانات حقيقية"""
        open_trades = market_data.get('open_trades', {}) if market_data else {}
        
        lines = ["👁️ **تولين:**"]
        
        if open_trades:
            lines.append(f"**أركز على {len(open_trades)} صفقة مفتوحة:**")
            for asset, trade in open_trades.items():
                label = "💶 EUR/USD" if asset == "eurusd" else "💴 USD/JPY"
                profit = trade.get('profit_dollars', 0)
                p_str = f"+${profit:.2f}" if profit > 0 else f"-${abs(profit):.2f}" if profit < 0 else "$0.00"
                lines.append(f"   • {label}: {p_str}")
        else:
            lines.append("**أبحث في الشارت عن فرص جديدة للنفط والفضة.**")
            lines.append("💡 السوق هادئ، أنتظر إشارة واضحة.")
        
        lines.append("")
        lines.append("💙 أنتظر سؤالك القادم...")
        return "\n".join(lines)
    
    def _answer_market_with_all_engines(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """
        ✅ رد مختصر على 'كيف السوق' - خلاصة فقط (بدون تقطيع)
        """
        lines = []
        
        # ── الأسعار ──
        oil_price = engine_data.get('oil_price', 0)
        silver_price = engine_data.get('silver_price', 0)
        
        if oil_price > 0 or silver_price > 0:
            lines.append("💰 **الأسعار:**")
            if oil_price > 0:
                lines.append(f"   • 🛢️ النفط: ${oil_price:.2f}")
            if silver_price > 0:
                lines.append(f"   • 🥈 الفضة: ${silver_price:.2f}")
            lines.append("")
        
        # ── الاتجاه والإشارة ──
        market_analysis = engine_data.get('market_analyzer', {})
        signal = market_analysis.get('signal', 'WAIT')
        trend = market_analysis.get('trend', 'محايد')
        
        if trend:
            lines.append(f"📈 **الاتجاه:** {trend}")
            if signal != 'WAIT':
                sig_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                lines.append(f"🎯 **الإشارة:** {sig_emoji} {signal}")
            lines.append("")
        
        # ── المشاعر والمخاطر ──
        emotion_data = engine_data.get('prometheus', {})
        emotion = emotion_data.get('dominant', 'neutral')
        emotion_arabic = self._translate_emotion(emotion)
        lines.append(f"💭 **شعوري:** {emotion_arabic}")
        
        risk_data = engine_data.get('risk_master', {})
        risk_level = risk_data.get('level', 'medium')
        risk_text = "مرتفعة" if risk_level == "high" else "متوسطة" if risk_level == "medium" else "منخفضة"
        lines.append(f"🛡️ **المخاطر:** {risk_text}")
        lines.append("")
        
        # ── توصية مختصرة ──
        if risk_level == "high":
            lines.append("💡 **توصيتي:** تجنب الصفقات الجديدة")
        elif signal == "BUY" and risk_level != "high":
            lines.append("💡 **توصيتي:** فرصة شراء بحذر")
        elif signal == "SELL" and risk_level != "high":
            lines.append("💡 **توصيتي:** فرصة بيع بحذر")
        else:
            lines.append("💡 **توصيتي:** انتظر وضوح الاتجاه")
        
        lines.append("")
        lines.append("💙 هل تريد تقريراً مفصلاً عن الأخبار؟")
        return "\n".join(lines)
    
    def _answer_oil_analysis(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🛢️ تحليل النفط - يستخدم التحليل الشامل"""
        # محاولة استخدام التحليل الشامل من main
        if self.main and hasattr(self.main, 'format_concise_analysis'):
            try:
                result = self.main.perform_comprehensive_analysis("oil", False, None)
                if result and isinstance(result, tuple) and len(result) >= 2:
                    analysis = result[0]
                    if analysis:
                        report = self.main.format_concise_analysis(analysis, "oil")
                        return f"🛢️ **تحليل النفط:**\n\n{report}"
            except Exception as e:
                logger.debug(f"⚠️ فشل التحليل الشامل للنفط: {e}")
        
        # Fallback: بيانات أساسية
        oil_price = engine_data.get('oil_price', 0)
        if oil_price > 0:
            return f"🛢️ **تحليل النفط:**\n💰 السعر الحالي: ${oil_price:.2f}\n\n💡 استخدم زر '🛢️ تحليل النفط' للحصول على تقرير شامل."
        return "⚠️ لا توجد بيانات كافية لتحليل النفط حالياً."
    
    def _answer_silver_analysis(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🥈 تحليل الفضة - يستخدم التحليل الشامل"""
        if self.main and hasattr(self.main, 'format_concise_analysis'):
            try:
                result = self.main.perform_comprehensive_analysis("silver", False, None)
                if result and isinstance(result, tuple) and len(result) >= 2:
                    analysis = result[0]
                    if analysis:
                        report = self.main.format_concise_analysis(analysis, "silver")
                        return f"🥈 **تحليل الفضة:**\n\n{report}"
            except Exception as e:
                logger.debug(f"⚠️ فشل التحليل الشامل للفضة: {e}")
        
        silver_price = engine_data.get('silver_price', 0)
        if silver_price > 0:
            return f"🥈 **تحليل الفضة:**\n💰 السعر الحالي: ${silver_price:.3f}\n\n💡 استخدم زر '🥈 تحليل الفضة' للحصول على تقرير شامل."
        return "⚠️ لا توجد بيانات كافية لتحليل الفضة حالياً."
    
    def _answer_trade_status(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """📊 حالة الصفقة - يستخدم التحليل الشامل"""
        lines = []
        
        for asset in ["eurusd", "usdjpy"]:
            open_trade = None
            if self.main and hasattr(self.main, 'get_current_open_trade'):
                try:
                    open_trade = self.main.get_current_open_trade(asset)
                except:
                    pass
            
            if open_trade:
                entry = open_trade.get('entry_price', 0)
                trade_type = open_trade.get('type', 'BUY')
                profit = open_trade.get('profit_dollars', 0)
                price = engine_data.get(f'{asset}_price', 0)
                label = "💶 EUR/USD" if asset == "eurusd" else "💴 USD/JPY"
                
                status = "✅ ربح" if profit > 0 else "❌ خسارة" if profit < 0 else "⚪ تعادل"
                lines.append(f"**{label}:** {trade_type} | {status} (${profit:+.2f}) | السعر: ${price:.2f}")
        
        if not lines:
            return "📊 **لا توجد صفقات مفتوحة حالياً.**"
        
        lines.insert(0, "📊 **حالة الصفقات المفتوحة:**")
        lines.append("")
        lines.append("💡 أرسل `تفاصيل الصفقة` لمزيد من المعلومات.")
        return "\n".join(lines)
    
    def _answer_trade_history(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """📋 تاريخ الصفقات"""
        lines = []
        total_profit = 0
        total_trades = 0
        winning_trades = 0
        
        for asset in ["eurusd", "usdjpy"]:
            if self.main and hasattr(self.main, 'calculate_statistics'):
                try:
                    stats = self.main.calculate_statistics(asset)
                    if stats:
                        total_profit += stats.get('total_profit', 0)
                        total_trades += stats.get('total_trades', 0)
                        winning_trades += stats.get('winning_trades', 0)
                        label = "💶 EUR/USD" if asset == "eurusd" else "💴 USD/JPY"
                        lines.append(f"**{label}:** {stats.get('total_trades', 0)} صفقة | ربح: ${stats.get('total_profit', 0):.2f} | نجاح: {stats.get('win_rate', 0):.1f}%")
                except:
                    pass
        
        if not lines:
            return "📋 **لا توجد صفقات مسجلة حتى الآن.**"
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        lines.insert(0, "📋 **تاريخ الصفقات:**")
        lines.append("")
        lines.append(f"📊 **الإجمالي:** {total_trades} صفقة")
        lines.append(f"💰 **إجمالي الربح:** ${total_profit:.2f}")
        lines.append(f"📈 **نسبة النجاح:** {win_rate:.1f}%")
        return "\n".join(lines)
    
    def _answer_last_trade_analysis(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """تحليل الصفقة الأخيرة"""
        last_trade = None
        if self.main and hasattr(self.main, 'get_last_closed_trade'):
            try:
                last_trade = self.main.get_last_closed_trade()
            except:
                pass
        
        if not last_trade:
            return "📊 **لا توجد صفقات مغلقة سابقة للتحليل.**\n\n💡 ابدأ أولى صفقاتك وسأحللها لك فوراً!"
        
        asset_label = "النفط" if last_trade.get('asset') == "oil" else "الفضة"
        profit = last_trade.get('profit_dollars', 0)
        exit_reason = last_trade.get('exit_reason', 'غير معروف')
        entry = last_trade.get('entry_price', 0)
        exit_price = last_trade.get('exit_price', 0)
        trade_type = last_trade.get('type', 'UNKNOWN')
        
        lines = [f"🔍 **تحليل آخر صفقة {asset_label}:**", ""]
        
        lines.append(f"📊 **التفاصيل:**")
        lines.append(f"   • النوع: {trade_type}")
        lines.append(f"   • الدخول: ${entry:.2f}")
        lines.append(f"   • الخروج: ${exit_price:.2f}")
        lines.append(f"   • النتيجة: {'✅ ربح' if profit > 0 else '❌ خسارة' if profit < 0 else '⚪ تعادل'} (${profit:+.2f})")
        lines.append(f"   • سبب الإغلاق: {exit_reason}")
        
        lines.append("")
        lines.append("📋 **تحليل الأسباب:**")
        
        if profit > 0:
            lines.append("   ✅ صفقة ناجحة!")
            if exit_reason == "Hit Take Profit":
                lines.append("   • تم تحقيق الهدف بنجاح")
            elif exit_reason == "أمر يدوي":
                lines.append("   • إغلاق يدوي في الوقت المناسب")
            else:
                lines.append("   • خرجت في الوقت المناسب")
            lines.append("")
            lines.append("💡 **ما يمكن تعلمه:**")
            lines.append("   • استمر في تطبيق هذه الاستراتيجية")
            lines.append("   • حافظ على نفس إدارة المخاطر")
        else:
            lines.append("   ❌ صفقة خاسرة")
            if exit_reason == "Hit Stop Loss":
                lines.append("   • تم ضرب وقف الخسارة")
                lines.append("   • قد تكون مسافة وقف الخسارة ضيقة جداً")
            elif exit_reason == "تحذير قوي - إغلاق تلقائي":
                lines.append("   • تم الإغلاق بسبب تحذير قوي")
            else:
                lines.append("   • إغلاق يدوي لتجنب خسارة أكبر")
            lines.append("")
            lines.append("💡 **ما يمكن تعلمه:**")
            if exit_reason == "Hit Stop Loss":
                lines.append("   • زيادة مسافة وقف الخسارة")
                lines.append("   • استخدام نقاط الدعم والمقاومة لتحديد الوقف")
            else:
                lines.append("   • مراجعة نقاط الدخول")
                lines.append("   • استخدام مؤشرات إضافية للتأكيد")
        
        lines.append("")
        lines.append("💙 هل تريد تحليلاً أعمق لهذه الصفقة؟")
        return "\n".join(lines)
    
    def _answer_profit_loss(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """💰 الأرباح والخسائر"""
        total_profit = 0
        oil_trades = 0
        silver_trades = 0
        oil_wins = 0
        silver_wins = 0
        
        if self.main and hasattr(self.main, 'calculate_statistics'):
            try:
                oil_stats = self.main.calculate_statistics("oil")
                silver_stats = self.main.calculate_statistics("silver")
                if oil_stats:
                    total_profit += oil_stats.get('total_profit', 0)
                    oil_trades = oil_stats.get('total_trades', 0)
                    oil_wins = oil_stats.get('winning_trades', 0)
                if silver_stats:
                    total_profit += silver_stats.get('total_profit', 0)
                    silver_trades = silver_stats.get('total_trades', 0)
                    silver_wins = silver_stats.get('winning_trades', 0)
            except Exception as e:
                logger.debug(f"⚠️ فشل جلب الإحصائيات: {e}")
        
        total_trades = oil_trades + silver_trades
        total_wins = oil_wins + silver_wins
        
        lines = ["💰 **ملخص الأرباح والخسائر:**", ""]
        
        if total_trades == 0:
            lines.append("📊 **لا توجد صفقات مسجدة بعد.**")
            lines.append("💡 ابدأ التداول لأتمكن من عرض إحصائياتك.")
        else:
            lines.append(f"📊 **الإجمالي:**")
            lines.append(f"   • عدد الصفقات: {total_trades}")
            lines.append(f"   • إجمالي الربح/الخسارة: ${total_profit:+.2f}")
            lines.append(f"   • نسبة النجاح: {(total_wins / total_trades * 100):.1f}%")
            lines.append("")
            
            lines.append("🛢️ **النفط:**")
            lines.append(f"   • عدد الصفقات: {oil_trades}")
            lines.append(f"   • الأرباح: {oil_wins}")
            lines.append(f"   • الخسائر: {oil_trades - oil_wins}")
            if oil_stats:
                lines.append(f"   • صافي الربح: ${oil_stats.get('total_profit', 0):+.2f}")
            lines.append("")
            
            lines.append("🥈 **الفضة:**")
            lines.append(f"   • عدد الصفقات: {silver_trades}")
            lines.append(f"   • الأرباح: {silver_wins}")
            lines.append(f"   • الخسائر: {silver_trades - silver_wins}")
            if silver_stats:
                lines.append(f"   • صافي الربح: ${silver_stats.get('total_profit', 0):+.2f}")
            lines.append("")
            
            if total_profit > 0:
                lines.append("✅ **التقييم:** أداء إيجابي، استمر!")
            elif total_profit < 0:
                lines.append("⚠️ **التقييم:** أداء سلبي، راجع استراتيجيتك")
            else:
                lines.append("⚪ **التقييم:** أداء متعادل")
        
        lines.append("")
        lines.append("💙 هل تريد تفاصيل أكثر عن أي أصل؟")
        return "\n".join(lines)
    
    def _answer_emotional_support(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """💙 الدعم العاطفي"""
        return "💙 **أنا هنا معك...**\n\nأعلم أن التداول يمكن أن يكون مرهقاً أحياناً. خسائرك ليست نهاية العالم، بل هي جزء من الرحلة.\n\n🌱 **تذكر:**\n• كل متداول ناجح مر بخسائر\n• المهم هو التعلم منها والمضي قدماً\n• خذ نفساً عميقاً واسترح إذا احتجت\n• لا تتداول وأنت عاطفي - هذا قرار حكيم\n\n**أنا معك، وكل يوم جديد هو فرصة جديدة.** 💪"
    
    def _answer_motivation(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🌟 تحفيز"""
        return "🌟 **تذكر دائماً:**\n\n*النجاح في التداول ليس عن عدم الخسارة، بل عن كيفية التعامل مع الخسارة.*\n\n💪 **أنت أقوى مما تعتقد!**\n• كل صفقة خاسرة هي درس\n• كل يوم جديد هو فرصة\n• الصبر هو أقوى سلاحك\n• الانضباط يفوق الذكاء\n\n🚀 **استمر، والنجاح سيأتي بالمثابرة!**"
    
    def _answer_general_advice(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """💡 نصيحة عامة"""
        return "💡 **نصيحة عامة:**\n\n🔍 التداول الناجح يحتاج إلى:\n• خطة واضحة\n• إدارة مخاطر جيدة\n• انضباط في التنفيذ\n• تعلم مستمر\n\n💙 **أنا هنا لمساعدتك في كل خطوة!**"
    
    def _answer_trade_open(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """فتح صفقة - إرشادي"""
        return "📊 **تولين:** يا صديقي، لفتح صفقة جديدة:\n\n1. تأكد من وجود إشارة واضحة من الماسح التلقائي\n2. استخدم التحليل الشامل لتأكيد الاتجاه\n3. حدد وقف الخسارة والهدف قبل الدخول\n\n💡 يمكنك الضغط على زر '🛢️ تحليل النفط' أو '🥈 تحليل الفضة' للحصول على تحليل شامل."
    
    def _answer_trade_close(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """إغلاق صفقة - إرشادي"""
        open_trades = market_data.get('open_trades', {}) if market_data else {}
        
        if not open_trades:
            return "❌ **تولين:** لا توجد صفقات مفتوحة للإغلاق يا صديقي."
        
        msg = "❌ **تولين:** لإغلاق صفقة يا صديقي:\n"
        if "oil" in open_trades:
            msg += "• `تم إغلاق صفقة النفط`\n"
        if "silver" in open_trades:
            msg += "• `تم إغلاق صفقة الفضة`\n"
        msg += "\nأو اضغط على: ❌ إغلاق الصفقة"
        return msg
    
    def _answer_risk_assessment(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """تقييم المخاطر"""
        msg_lower = question.lower()
        asset = "eurusd" if "usd" in msg_lower or "euro" in msg_lower or "يورو" in msg_lower else "usdjpy"
        asset_label = "EUR/USD" if asset == "eurusd" else "USD/JPY"
        
        risk_data = engine_data.get('risk_master', {})
        risk_level = risk_data.get('level', 'medium')
        risk_text = "مرتفعة" if risk_level == "high" else "متوسطة" if risk_level == "medium" else "منخفضة"
        risk_emoji = "🔴" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"
        
        lines = [f"🛡️ **تقييم المخاطر لـ {asset_label}:**", ""]
        lines.append(f"📊 **مستوى المخاطر العام:** {risk_emoji} {risk_text}")
        
        if risk_level == "high":
            lines.append("⚠️ **توصيتي:** تجنب الصفقات الجديدة حالياً")
        elif risk_level == "medium":
            lines.append("🟡 **توصيتي:** ادخل بحذر مع وقف خسارة مناسب")
        else:
            lines.append("✅ **توصيتي:** مخاطر منخفضة، فرصة جيدة للدخول")
        
        lines.append("")
        lines.append("💙 هل تريد تحليلاً أعمق للمخاطر؟")
        return "\n".join(lines)
    
    def _answer_news_with_all_engines(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """📰 الأخبار - يستخدم Tona Intelligence"""
        tona_data = engine_data.get('tona_intelligence', '')
        
        if tona_data and len(tona_data) > 50:
            return self._extract_news_summary(tona_data, engine_data)
        
        return self._generate_fallback_news(engine_data)
    
    def _extract_news_summary(self, tona_data: str, engine_data: Dict) -> str:
        """استخراج خلاصة من تقرير Tona Intelligence"""
        import re
        lines = []
        lines.append("📰 **خلاصة السوق اليوم:**")
        lines.append("")
        
        oil_price = engine_data.get('oil_price', 0)
        silver_price = engine_data.get('silver_price', 0)
        
        if oil_price > 0 or silver_price > 0:
            lines.append("💰 **الأسعار:**")
            if oil_price > 0:
                change = "➖"
                if "📉" in tona_data:
                    change = "📉"
                elif "📈" in tona_data:
                    change = "📈"
                lines.append(f"   • 🛢️ النفط: ${oil_price:.2f} {change}")
            if silver_price > 0:
                change = "➖"
                if "📉" in tona_data:
                    change = "📉"
                elif "📈" in tona_data:
                    change = "📈"
                lines.append(f"   • 🥈 الفضة: ${silver_price:.3f} {change}")
            lines.append("")
        
        high_risk = 0
        high_match = re.search(r'أخبار عالية الخطورة: (\d+)', tona_data)
        if high_match:
            high_risk = int(high_match.group(1))
        
        if high_risk > 5:
            lines.append("⚠️ **تحذير:** السوق متقلب مع وجود أخبار عالية التأثير")
            lines.append(f"   • عدد الأخبار عالية الخطورة: {high_risk}")
        elif high_risk > 2:
            lines.append("🟡 **تنبيه:** توجد أخبار متوسطة التأثير في السوق")
            lines.append(f"   • عدد الأخبار عالية الخطورة: {high_risk}")
        else:
            lines.append("✅ **الوضع مستقر:** لا توجد أخبار عالية الخطورة")
        
        lines.append("")
        lines.append("💙 هل تريد تفاصيل أكثر عن أي حدث؟")
        return "\n".join(lines)
    
    def _generate_fallback_news(self, engine_data: Dict) -> str:
        """تقرير أخبار بديل"""
        lines = []
        lines.append("📰 **حالة السوق الحالية:**")
        lines.append("")
        
        oil_price = engine_data.get('oil_price', 0)
        silver_price = engine_data.get('silver_price', 0)
        
        if oil_price > 0 or silver_price > 0:
            lines.append("💰 **الأسعار:**")
            if oil_price > 0:
                lines.append(f"   • 🛢️ النفط: ${oil_price:.2f}")
            if silver_price > 0:
                lines.append(f"   • 🥈 الفضة: ${silver_price:.3f}")
            lines.append("")
        
        risk_data = engine_data.get('risk_master', {})
        risk_level = risk_data.get('level', 'medium')
        risk_text = "مرتفعة" if risk_level == "high" else "متوسطة" if risk_level == "medium" else "منخفضة"
        lines.append(f"🛡️ **مستوى المخاطر:** {risk_text}")
        lines.append("")
        
        lines.append("💙 لا توجد أخبار جديدة حالياً، سأتابع التطورات.")
        return "\n".join(lines)
    
    def _answer_technical_indicators(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """📊 المؤشرات الفنية"""
        msg_lower = question.lower()
        asset = "eurusd"
        if "فضة" in msg_lower or "silver" in msg_lower:
            asset = "usdjpy"
        asset_label = "EUR/USD" if asset == "eurusd" else "USD/JPY"
        
        analysis = engine_data.get(f'{asset}_analysis', {})
        if not analysis:
            return f"📊 **لا توجد بيانات كافية لتحليل {asset_label}.**"
        
        indicators = analysis.get('indicators', {})
        tf_15m = analysis.get('timeframes', {}).get('15m', {})
        
        lines = [f"📊 **المؤشرات الفنية لـ {asset_label}:**", ""]
        
        if "rsi" in msg_lower or "ار اس اي" in msg_lower:
            rsi = tf_15m.get('rsi', 50)
            rsi_zone = "ذروة شراء" if rsi > 70 else "ذروة بيع" if rsi < 30 else "محايد"
            rsi_emoji = "🟢" if 30 < rsi < 70 else "🔴"
            lines.append(f"📈 **RSI:** {rsi:.1f} {rsi_emoji} ({rsi_zone})")
        
        if "macd" in msg_lower or "ماكد" in msg_lower:
            macd = tf_15m.get('macd', 0)
            macd_emoji = "🟢" if macd > 0 else "🔴"
            lines.append(f"📉 **MACD:** {macd:.4f} {macd_emoji}")
        
        if "بولينجر" in msg_lower or "bollinger" in msg_lower:
            bb = tf_15m.get('bollinger', {})
            upper = bb.get('upper', 0)
            lower = bb.get('lower', 0)
            price = analysis.get('price', 0)
            if upper and lower:
                bb_position = ((price - lower) / (upper - lower) * 100) if upper > lower else 50
                lines.append(f"📊 **Bollinger Bands:** موقع السعر: {bb_position:.1f}% من النطاق")
        
        if "adx" in msg_lower:
            adx = tf_15m.get('adx', 15)
            adx_emoji = "🟢" if adx > 25 else "🔴" if adx < 20 else "🟡"
            lines.append(f"📊 **ADX:** {adx:.1f} {adx_emoji}")
        
        if "vwap" in msg_lower or "فواب" in msg_lower:
            vwap = tf_15m.get('vwap', 0)
            price = analysis.get('price', 0)
            if vwap > 0:
                vwap_diff = ((price - vwap) / vwap * 100) if vwap > 0 else 0
                vwap_emoji = "🟢" if vwap_diff > 0 else "🔴"
                lines.append(f"📊 **VWAP:** ${vwap:.2f} | الفرق: {vwap_diff:+.2f}% {vwap_emoji}")
        
        if len(lines) <= 2:
            return f"📊 **لم أتمكن من قراءة المؤشر المطلوب لـ {asset_label}.**\n\n💡 تأكد من كتابة اسم المؤشر بشكل صحيح (RSI, MACD, Bollinger, VWAP, SuperTrend, ADX)"
        
        lines.append("")
        lines.append("💙 هل تريد تحليلاً لمؤشر آخر؟")
        return "\n".join(lines)
    
    def _answer_support_resistance(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🛡️ الدعم والمقاومة"""
        msg_lower = question.lower()
        asset = "eurusd" if "usd" in msg_lower or "euro" in msg_lower or "يورو" in msg_lower else "usdjpy"
        asset_label = "EUR/USD" if asset == "eurusd" else "USD/JPY"
        
        analysis = engine_data.get(f'{asset}_analysis', {})
        if not analysis:
            return f"📊 **لا توجد بيانات كافية لتحليل {asset_label}.**"
        
        price = analysis.get('price', 0)
        sr = analysis.get('support_resistance', {})
        support = sr.get('support', price * 0.98)
        resistance = sr.get('resistance', price * 1.02)
        
        lines = [f"📊 **مستويات الدعم والمقاومة لـ {asset_label}:**", ""]
        lines.append(f"💰 **السعر الحالي:** ${price:.2f}")
        lines.append("")
        lines.append(f"🛡️ **المقاومة:** ${resistance:.2f}")
        lines.append(f"🛡️ **الدعم:** ${support:.2f}")
        lines.append("")
        
        if price >= resistance * 0.98:
            lines.append("📌 **التحليل:** السعر قرب المقاومة الرئيسية")
            lines.append("💡 **توصية:** قد يواجه السعر صعوبة في الاختراق")
        elif price <= support * 1.02:
            lines.append("📌 **التحليل:** السعر قرب الدعم الرئيسي")
            lines.append("💡 **توصية:** قد يرتد السعر من الدعم")
        else:
            lines.append("📌 **التحليل:** السعر في منتصف النطاق")
            lines.append("💡 **توصية:** انتظر الوصول إلى دعم أو مقاومة")
        
        lines.append("")
        lines.append("💙 هل تريد تحليلاً أعمق لهذه المستويات؟")
        return "\n".join(lines)
    
    def _answer_prediction_with_all_engines(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🔮 التوقعات"""
        msg_lower = question.lower()
        asset = "eurusd" if "usd" in msg_lower or "euro" in msg_lower or "يورو" in msg_lower else "usdjpy"
        asset_label = "EUR/USD" if asset == "eurusd" else "USD/JPY"
        
        oracle_data = engine_data.get(f'oracle_{asset}', {})
        emotion = user_context.get('prometheus_emotion', 'neutral')
        emotion_arabic = self._translate_emotion(emotion)
        
        lines = [f"🔮 **توقعاتي لـ {asset_label}:**", ""]
        
        if oracle_data and oracle_data.get('scenarios'):
            most_likely = max(oracle_data['scenarios'], key=lambda x: x.get('probability', 0))
            lines.append(f"📈 **السيناريو الأكثر ترجيحاً:**")
            lines.append(f"   • {most_likely.get('name', 'غير محدد')}")
            lines.append(f"   • الاحتمال: {most_likely.get('probability', 0)*100:.0f}%")
            lines.append(f"   • {most_likely.get('description', '')}")
            
            lines.append("")
            lines.append("📊 **سيناريوهات أخرى:**")
            for s in oracle_data['scenarios'][1:3]:
                lines.append(f"   • {s.get('name', 'سيناريو')} ({s.get('probability', 0)*100:.0f}%)")
        else:
            lines.append("لا توجد توقعات كافية حالياً. السوق غير واضح.")
        
        lines.append("")
        lines.append(f"💭 **مشاعري:** {emotion_arabic}")
        lines.append("")
        lines.append("📢 سأحدثك بأي تغيير.")
        return "\n".join(lines)
    
    def _answer_quiet_market(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🌊 السوق الهادئ"""
        oil_price = engine_data.get('oil_price', 0)
        silver_price = engine_data.get('silver_price', 0)
        market_analysis = engine_data.get('market_analyzer', {})
        signal = market_analysis.get('signal', 'WAIT')
        
        lines = ["🌊 **تحليل هدوء السوق:**", ""]
        lines.append(f"📊 **الوضع الحالي:**")
        lines.append(f"   • النفط: ${oil_price:.2f}")
        lines.append(f"   • الفضة: ${silver_price:.3f}")
        lines.append(f"   • الإشارة: {signal}")
        lines.append("")
        lines.append("💡 **توصيتي:** استغل الهدوء في مراجعة استراتيجيتك وجهز نفسك للحركة القادمة")
        lines.append("")
        lines.append("📢 سأخبرك فور ظهور أي حركة مهمة")
        return "\n".join(lines)
    
    def _answer_explosion_prediction(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """💥 الانفجار أو الانهيار"""
        chronos_data = engine_data.get('chronos', {})
        events = chronos_data.get('event_proximity', []) if chronos_data else []
        
        lines = ["💥 **تحليل احتمالية الانفجار أو الانهيار:**", ""]
        
        if events:
            high_impact_events = [e for e in events if e.get('impact') == 'high']
            if high_impact_events:
                lines.append("⚠️ **أحداث عالية التأثير قادمة:**")
                for e in high_impact_events[:2]:
                    lines.append(f"   • {e.get('event', 'حدث')} (بعد {e.get('hours_until', 0):.1f} ساعات)")
            else:
                lines.append("🟢 **لا توجد أحداث عالية التأثير قادمة**")
        else:
            lines.append("🟢 **لا توجد أحداث قادمة**")
        
        lines.append("")
        lines.append("💡 **توصيتي:** كن مستعداً للحركة المفاجئة وراجع وقف الخسارة")
        lines.append("")
        lines.append("📢 سأتابع التطورات وأخبرك بأي تغيير")
        return "\n".join(lines)
    
    def _answer_virtual_trade(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """📊 تحليل صفقة مقترحة"""
        msg_lower = question.lower()
        asset = "eurusd" if "usd" in msg_lower or "euro" in msg_lower or "يورو" in msg_lower else "usdjpy"
        asset_label = "EUR/USD" if asset == "eurusd" else "USD/JPY"
        
        analysis = engine_data.get(f'{asset}_analysis', {})
        if not analysis:
            return f"📊 **لا توجد بيانات كافية لتحليل {asset_label}.**"
        
        price = analysis.get('price', 0)
        signal = analysis.get('signal', 'WAIT')
        comp_score = analysis.get('comprehensive_score', {})
        score = comp_score.get('score', 50)
        grade = comp_score.get('grade', 'محايد')
        
        lines = [f"📊 **تحليل الصفقة المقترحة - {asset_label}:**", ""]
        lines.append(f"💰 **السعر الحالي:** ${price:.2f}")
        lines.append(f"🎯 **الإشارة:** {signal}")
        lines.append(f"📊 **التقييم الشامل:** {score:.0f}% ({grade})")
        lines.append("")
        
        if score >= 70 and signal == 'BUY':
            lines.append("✅ **الخلاصة:** هذه فرصة شراء جيدة")
            lines.append("💡 **توصيتي:** ادخل بحذر مع وقف خسارة مناسب")
        elif score >= 70 and signal == 'SELL':
            lines.append("✅ **الخلاصة:** هذه فرصة بيع جيدة")
            lines.append("💡 **توصيتي:** ادخل بحذر مع وقف خسارة مناسب")
        elif score >= 50:
            lines.append("🟡 **الخلاصة:** فرصة متوسطة، تحتاج تأكيداً")
            lines.append("💡 **توصيتي:** انتظر تأكيداً إضافياً قبل الدخول")
        else:
            lines.append("🔴 **الخلاصة:** لا توجد فرصة واضحة حالياً")
            lines.append("💡 **توصيتي:** تجنب الدخول في هذه الصفقة")
        
        lines.append("")
        lines.append("💙 **تذكير:** البوت يحاكي فقط، القرار النهائي لك.")
        return "\n".join(lines)
    
    def _answer_learning(self, question: str, market_data: Dict, user_context: Dict, engine_data: Dict) -> str:
        """🧠 التعلم"""
        lines = ["🧠 **التعلم والتطوير:**", ""]
        lines.append("📚 **الدروس المستفادة:**")
        lines.append("   • لا توجد صفقات كافية للتعلم منها بعد")
        lines.append("   • ابدأ التداول لأتعلم معك")
        lines.append("")
        lines.append("⚠️ **الأخطاء الشائعة التي أتعلم منها:**")
        lines.append("   • الدخول دون تأكيد من المؤشرات")
        lines.append("   • تجاهل وقف الخسارة")
        lines.append("   • التداول في أوقات التقلبات العالية")
        lines.append("")
        lines.append("💡 **نصيحتي:** تعلم من كل صفقة، رابحة أو خاسرة")
        lines.append("")
        lines.append("💙 أنا أتعلم معك في كل خطوة!")
        return "\n".join(lines)
    
    # ── دوال مساعدة داخلية ──
    
    def _translate_emotion(self, emotion: str) -> str:
        emotion_map = {
            "empathy": "متفهمة", "confidence": "واثقة", "anxiety": "قلقة",
            "excitement": "متحمسة", "curiosity": "فضولية", "protectiveness": "حريصة",
            "energy": "نشيطة", "happy": "سعيدة", "sad": "حزينة",
            "fearful": "خائفة", "worried": "قلقة", "cautious": "حذرة",
            "optimistic": "متفائلة", "neutral": "متزنة", "joy": "سعيدة",
            "fear": "خائفة", "anger": "غاضبة", "surprise": "مندهشة",
            "trust": "واثقة", "sadness": "حزينة", "frustration": "محبطة"
        }
        return emotion_map.get(emotion, "متزنة")
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        emojis = {
            "واثقة": "💪", "قلقة": "😟", "متحمسة": "🔥",
            "حريصة": "🛡️", "متفهمة": "🤝", "متفائلة": "🌟",
            "سعيدة": "😊", "حزينة": "😔", "خائفة": "😰",
            "حذرة": "🤔", "فضولية": "🔍", "نشيطة": "⚡",
            "متزنة": "💙", "غاضبة": "🔥", "محبطة": "😞",
            "مندهشة": "😲"
        }
        return emojis.get(emotion, "💙")
    
    def _handle_user_emotion_response(self, user_message: str) -> Optional[str]:
        """معالجة ردود المستخدم عن مشاعره"""
        msg_lower = user_message.lower()
        
        if any(k in msg_lower for k in ["حزين", "زعلان", "متضايق", "خسران", "خاسر", "محبط", "مضيع", "تعبان"]):
            return "💙 **تولين:** أفهم شعورك يا صديقي! الخسارة مؤلمة، لكنها جزء من الطريق. تذكر أن كل خسارة تعلمنا درساً. أنا هنا لمساعدتك في تجاوزها. 💙"
        
        elif any(k in msg_lower for k in ["سعيد", "فرحان", "مبسوط", "ربحان", "رابح"]):
            return "🎉 **تولين:** هذا رائع يا صديقي! أنا سعيدة لفرحتك. النجاح يستحق الاحتفال، لكن تذكر أن السوق متغير، فلنستمتع باللحظة ونستعد للخطوة التالية! 💙"
        
        elif any(k in msg_lower for k in ["محتار", "متردد", "خائف", "قلق"]):
            return "🤝 **تولين:** لا بأس يا صديقي، التردد طبيعي. أنا هنا لمساعدتك في اتخاذ القرار الصحيح. هل تريد تحليلاً أو نصيحة؟ 💙"
        
        elif any(k in msg_lower for k in ["بخير", "تمام", "جيد", "good", "الحمدلله"]):
            return "💙 **تولين:** الحمدلله! أنا سعيدة بأنك بخير. هل تريد مساعدة في أي شيء؟ 💙"
        
        return None
    
    def _fallback_handle(self, question: str, engine_data: Dict) -> str:
        """الرد النهائي عندما لا يعرف البوت الإجابة"""
        return f"💙 **تولين:** شكراً لسؤالك يا صديقي! \n\nللحصول على أفضل مساعدة:\n• استخدم الأزرار للتحليل\n• اسأل عن مصطلحات التداول (مثل: ما هو RSI؟)\n• اسأل عن النفط أو الفضة\n\nأنا هنا لخدمتك! 🚀"

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 13: واجهات الاستخدام
# ═══════════════════════════════════════════════════════════════════════════════════

    def get_consciousness(self) -> ConsciousnessState:
        return self.consciousness
    
    def get_engine_summary(self) -> Dict:
        return getattr(self, '_engine_data', {})
    
    def explain_decision(self) -> str:
        lines = [
            f"🧠 **شرح قراري:**",
            "",
            f"📊 شعور السوق: {self.consciousness.market_sentiment}",
            f"💭 مشاعري: {self.consciousness.dominant_emotion}",
            f"📊 الثقة: {self.consciousness.confidence*100:.0f}%",
            f"🎯 القرار: {self.consciousness.recommended_action}",
        ]
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 14: دوال الحفظ والتحميل
# ═══════════════════════════════════════════════════════════════════════════════════

    def save_state(self, filepath: str = "learning_data/consciousness_state.json"):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            state = {
                'timestamp': time.time(),
                'neurons': {name: {'activation': n.activation, 'confidence': n.confidence, 'emotion': n.emotion} for name, n in self.neurons.items()},
                'synapses': {f"{s.source}->{s.target}": {'weight': s.weight, 'plasticity': s.plasticity} for s in self.synapses.values()},
                'consciousness': {
                    'dominant_emotion': self.consciousness.dominant_emotion,
                    'market_sentiment': self.consciousness.market_sentiment,
                    'confidence': self.consciousness.confidence,
                    'recommended_action': self.consciousness.recommended_action,
                    'narrative': self.consciousness.narrative
                },
                'engine_summary': self._engine_data if hasattr(self, '_engine_data') else {}
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            logger.info(f"🧠 تم حفظ حالة TCN في {filepath}")
        except Exception as e:
            logger.error(f"❌ فشل حفظ TCN: {e}")
    
    def load_state(self, filepath: str = "learning_data/consciousness_state.json"):
        try:
            if not os.path.exists(filepath):
                logger.info(f"🧠 لا يوجد ملف حالة سابق: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            for name, data in state.get('neurons', {}).items():
                if name in self.neurons:
                    self.neurons[name].activation = data.get('activation', 0.0)
                    self.neurons[name].confidence = data.get('confidence', 0.5)
                    self.neurons[name].emotion = data.get('emotion', 'neutral')
            
            for key, data in state.get('synapses', {}).items():
                source, target = key.split('->')
                synapse_key = (source, target)
                if synapse_key in self.synapses:
                    self.synapses[synapse_key].weight = data.get('weight', 0.5)
                    self.synapses[synapse_key].plasticity = data.get('plasticity', 0.1)
            
            consciousness_data = state.get('consciousness', {})
            if consciousness_data:
                self.consciousness.dominant_emotion = consciousness_data.get('dominant_emotion', 'neutral')
                self.consciousness.market_sentiment = consciousness_data.get('market_sentiment', 'neutral')
                self.consciousness.confidence = consciousness_data.get('confidence', 0.5)
                self.consciousness.recommended_action = consciousness_data.get('recommended_action', 'wait')
                self.consciousness.narrative = consciousness_data.get('narrative', '')
            
            if 'engine_summary' in state:
                self._engine_data = state.get('engine_summary', {})
            
            logger.info(f"🧠 تم تحميل حالة TCN من {filepath}")
            return True
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ ملف الحالة تالف: {e}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ فشل تحميل حالة TCN: {e}")
            return False

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 15: وظيفة المساعدة
# ═══════════════════════════════════════════════════════════════════════════════════

def create_consciousness_network(main_instance, **engines) -> ConsciousnessNetwork:
    return ConsciousnessNetwork(main_instance=main_instance, engines=engines)

# ═══════════════════════════════════════════════════════════════════════════════════
# 📦 PART 16: اختبار سريع
# ═══════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧠 اختبار Tona Consciousness Network V13.0...")
    tcn = ConsciousnessNetwork()
    print("\n✅ الاختبار ناجح!")
