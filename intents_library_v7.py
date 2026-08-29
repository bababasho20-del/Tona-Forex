# ====================================================================================
# 📚 مكتبة النيات الهرمية الشاملة - الحوباني V7.0 (Ultra-Comprehensive)
# ====================================================================================
# تغطي: النفط (XTIUSD) + الفضة (XAGUSD)
# الأبعاد: فنية | مخاطر | نفسية | إخبارية | تعليمية | تفاعلية
# ====================================================================================

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# ════════════════════════════════════════════════════════════════════════════════════
# أقسام النيات الرئيسية (Intent Categories)
# ════════════════════════════════════════════════════════════════════════════════════

class IntentCategory(Enum):
    MARKET_ANALYSIS = "تحليل السوق"
    TECHNICAL_INDICATORS = "المؤشرات الفنية"
    TRADE_MANAGEMENT = "إدارة الصفقات"
    RISK_MANAGEMENT = "إدارة المخاطر"
    NEWS_EVENTS = "الأخبار والأحداث"
    PREDICTIONS = "التوقعات والسيناريوهات"
    LEARNING = "التعلم والتحسين"
    PSYCHOLOGY = "السيكولوجيا والنفسية"
    BOT_CONTROL = "التحكم بالبوت"
    PERSONAL = "التفاعل الشخصي"
    GENERAL = "عام"

# ════════════════════════════════════════════════════════════════════════════════════
# مستويات الثقة (Confidence Levels)
# ════════════════════════════════════════════════════════════════════════════════════

class ConfidenceLevel(Enum):
    EXACT = 1.0
    HIGH = 0.85
    MEDIUM = 0.7
    LOW = 0.5
    CONTEXTUAL = 0.4

# ════════════════════════════════════════════════════════════════════════════════════
# هيكل النية المتقدم (Advanced Intent Structure)
# ════════════════════════════════════════════════════════════════════════════════════

@dataclass
class IntentDefinition:
    intent_id: str
    category: IntentCategory
    keywords: List[str] = field(default_factory=list)
    regex_patterns: List[str] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)
    excludes: List[str] = field(default_factory=list)
    handler: Optional[str] = None
    response_template: Optional[str] = None
    priority: int = 5
    is_dynamic: bool = True
    requires_asset: bool = False
    compound_keywords: List[List[str]] = field(default_factory=list)

# ════════════════════════════════════════════════════════════════════════════════════
# المكتبة الشاملة V7
# ════════════════════════════════════════════════════════════════════════════════════

INTENTS_LIBRARY_V7 = {
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 1: تحليل السوق والأسعار (MARKET_ANALYSIS)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "market_overview": IntentDefinition(
        intent_id="market_overview",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "وضع السوق", "حال السوق", "شكل السوق", "السوق الحين", "السوق الان",
            "سوق النفط", "سوق الفضة", "الوضع العام", "نظرة عامة", "لمحة سريعة",
            "market overview", "market status", "حالة السوق", "تقرير السوق",
            "شو اخبار السوق", "وش سالفة السوق", "كيف السوق", "شلون السوق",
            "السوق اليوم", "تداول اليوم", "جلسة اليوم", "الجلسة", "السوق الحالي"
        ],
        regex_patterns=[
            r"(كيف|شلون|وش|شو)\s+(صار|صاير|صير)\s+(السوق|سوق)",
            r"(وضع|حال|حالة)\s+(السوق|النفط|الفضة)\s+(الحين|الان|اليوم|حاليا)"
        ],
        handler="market_overview",
        priority=8,
        is_dynamic=True
    ),
    
    "price_current": IntentDefinition(
        intent_id="price_current",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "كم السعر", "السعر الحالي", "سعر النفط", "سعر الفضة", "السعر الان",
            "كم النفط", "كم الفضة", "السعر وين", "وين السعر", "السعر الحين",
            "price now", "current price", "سعر البرميل", "سعر الاونصة",
            "النفط كم", "الفضة كم", "سعر XTIUSD", "سعر XAGUSD", "الاقتباس",
            "quotation", "quote", "السعر اللحظي", "السعر المباشر"
        ],
        regex_patterns=[
            r"(كم|وين|شقد|قديش)\s+(سعر|السعر|النفط|الفضة)",
            r"(سعر|السعر)\s+(النفط|الفضة|الحالي|الان|الحين)"
        ],
        handler="price_current",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "price_change": IntentDefinition(
        intent_id="price_change",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "تغير السعر", "نسبة التغير", "كم النسبة", "النسبة الحين", "النسبة المئوية",
            "النفط طالع كم", "الفضة نازلة كم", "كم الصعود", "كم الهبوط",
            "النفط صعد كم", "الفضة هبطت كم", "نسبة الصعود", "نسبة الهبوط",
            "change percent", "price change", "daily change", "التغير اليومي",
            "النفط كم طالع", "الفضة كم نازلة", "الحركة اليوم", "الأداء اليوم"
        ],
        regex_patterns=[
            r"(النفط|الفضة)\s+(صعد|هبط|طالع|نازل|ارتفع|انخفض)\s+(كم|قد ايه|قديش)",
            r"(كم|قديش|شقد)\s+(النسبة|التغير|الصعود|الهبوط)"
        ],
        handler="price_change",
        priority=8,
        is_dynamic=True
    ),
    
    "price_history": IntentDefinition(
        intent_id="price_history",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "سعر الافتتاح", "الافتتاح", "افتتاح اليوم", "سعر الافتتاحي",
            "اعلى سعر", "اقل سعر", "الهاي", "اللو", "high", "low",
            "السعر الاعلى", "السعر الادنى", "القمة اليوم", "القاع اليوم",
            "range اليوم", "نطاق التداول", "trading range", "النطاق",
            "الافتتاحية", "الاغلاق السابق", "السعر الافتتاحي", "الهاي اليوم"
        ],
        regex_patterns=[
            r"(كم|وش|شو)\s+(الهاي|اللو|القمة|القاع|الافتتاح|الاغلاق)",
            r"(اعلى|اقل|ادنى)\s+(سعر|نقطة|مستوى)\s+(اليوم|الحين|الان)"
        ],
        handler="price_history",
        priority=7,
        is_dynamic=True
    ),
    
    "volume_analysis": IntentDefinition(
        intent_id="volume_analysis",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "حجم التداول", "الحجم", "volume", "السيولة", "liquidity",
            "حجم النفط", "حجم الفضة", "كم الحجم", "الحجم الحين", "volume analysis",
            "الحجم ضعيف", "الحجم قوي", "حجم ضعيف", "حجم قوي",
            "volume profile", "بروفايل الحجم", "توزيع الحجم", "volume distribution",
            "الحجم المضاربي", "حجم المضاربة", "حجم المؤسسات", "حجم التجزئة"
        ],
        regex_patterns=[
            r"(حجم|volume|السيولة)\s+(التداول|النفط|الفضة|الحين|الان)",
            r"(كم|شقد|قديش)\s+(الحجم|volume|السيولة)"
        ],
        handler="volume_analysis",
        priority=7,
        is_dynamic=True
    ),
    
    "market_structure": IntentDefinition(
        intent_id="market_structure",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "بنية السوق", "market structure", "التركيبة السعرية", "الهيكل السعري",
            "قمة أعلى", "قمة أدنى", "قاع أعلى", "قاع أدنى", "higher high", "lower low",
            "higher low", "lower high", "HH", "HL", "LH", "LL",
            "الترند", "الاتجاه", "trend", "direction", "الاتجاه العام",
            "صاعد", "هابط", "جانبي", "متراجع", "تصحيح", "تجميع", "توزيع",
            "bullish", "bearish", "sideways", "accumulation", "distribution",
            "السوق صاعد", "السوق هابط", "السوق راكد", "السوق متذبذب"
        ],
        regex_patterns=[
            r"(بنية|هيكل|تركيبة)\s+(السوق|السعر|النفط|الفضة)",
            r"(الاتجاه|الترند|التوجه)\s+(العام|الحالي|الان|الحين|النفط|الفضة)"
        ],
        handler="market_structure",
        priority=8,
        is_dynamic=True
    ),
    
    "candlestick_analysis": IntentDefinition(
        intent_id="candlestick_analysis",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "الشمعة", "الشمعة الحالية", "الشمعة السابقة", "نمط الشمعة",
            "candlestick", "شمعة صاعدة", "شمعة هابطة", "شمعة دوجي", "doji",
            "شمعة المطرقة", "hammer", "شمعة الرجل المعلق", "hanging man",
            "شمعة النجمة", "shooting star", "شمعة الابتلاع", "engulfing",
            "شمعة الصباح", "morning star", "شمعة المساء", "evening star",
            "الشمعة الاخيرة", "الشمعة المغلقة", "الشمعة الحية", "الشمعة المفتوحة",
            "pin bar", "نمط pin bar", "الظل العلوي", "الظل السفلي", "الجسم",
            "wick", "shadow", "body", "الشمعة اليابانية", "البرايس اكشن"
        ],
        regex_patterns=[
            r"(شمعة|الشمعة|الشموع)\s+(الحالية|السابقة|الاخيرة|الحين|الان|النفط|الفضة)",
            r"(نمط|نماذج|النمط)\s+(الشمعة|الشموع|candlestick)"
        ],
        handler="candlestick_analysis",
        priority=7,
        is_dynamic=True
    ),
    
    "market_session": IntentDefinition(
        intent_id="market_session",
        category=IntentCategory.MARKET_ANALYSIS,
        keywords=[
            "جلسة", "الجلسة", "session", "market session", "الجلسة الامريكية",
            "الجلسة الاوروبية", "الجلسة الاسيوية", "الجلسة اللندنية", "الجلسة النيويوركية",
            "الافتتاح الامريكي", "الافتتاح الاوروبي", "الافتتاح الاسيوي",
            "overlapping sessions", "تداخل الجلسات", "أقوى جلسة", "أضعف جلسة",
            "متى تفتح الجلسة", "متى تغلق الجلسة", "أوقات التداول", "trading hours",
            "الجلسة الحالية", "الجلسة القادمة", "الجلسة المقبلة"
        ],
        regex_patterns=[
            r"(جلسة|الجلسة|session)\s+(الحالية|القادمة|الامريكية|الاوروبية|الاسيوية|الان|حاليا)",
            r"(متى|وين|امتى)\s+(تفتح|تغلق|تبدأ|تنتهي)\s+(الجلسة|التداول)"
        ],
        handler="market_session",
        priority=6,
        is_dynamic=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 2: المؤشرات الفنية (TECHNICAL_INDICATORS)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "rsi_analysis": IntentDefinition(
        intent_id="rsi_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "rsi", "ار اس اي", "الار اس اي", "مؤشر القوة النسبية",
            "relative strength index", "rsi النفط", "rsi الفضة",
            "كم rsi", "قيمة rsi", "قراءة rsi", "مستوى rsi",
            "rsi oversold", "rsi overbought", "تشبع شرائي", "تشبع بيعي",
            "rsi يتجه", "divergence rsi", "تباعد rsi", "تقارب rsi",
            "rsi 14", "rsi 7", "rsi 21", "الفترة الافتراضية",
            "الrsi فوق 70", "الrsi تحت 30", "الrsi في المنطقة الحيادية",
            "اراساي", "الاراساي", "مؤشر RSI", "RSI indicator"
        ],
        regex_patterns=[
            r"(rsi|ار\s*اس\s*اي|اراساي|الاراساي)\s*(\d+)?",
            r"(تشبع\s+(شرائي|بيعي)|overbought|oversold)\s*(rsi)?",
            r"(كم|قيمة|قراءة|مستوى)\s+(rsi|الrsi|اراساي)"
        ],
        handler="rsi_analysis",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "macd_analysis": IntentDefinition(
        intent_id="macd_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "macd", "ماكد", "الماكد", "مؤشر macd", "moving average convergence divergence",
            "خط macd", "خط الإشارة", "signal line", "histogram", "الهيستوجرام",
            "تقاطع macd", "crossover macd", "crossunder macd", "تقاطع صاعد", "تقاطع هابط",
            "macd النفط", "macd الفضة", " divergence macd", "تباعد macd",
            "macd فوق الصفر", "macd تحت الصفر", "macd يتجه للصفر",
            "الماكد صاعد", "الماكد هابط", "الماكد متزامن", "الماكد متباعد"
        ],
        regex_patterns=[
            r"(macd|ماكد|الماكد)\s*(النفط|الفضة|الحين|الان)?",
            r"(تقاطع|crossover|crossunder)\s*(macd|الماكد)",
            r"(تباعد|divergence)\s*(macd|الماكد)"
        ],
        handler="macd_analysis",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "bollinger_analysis": IntentDefinition(
        intent_id="bollinger_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "bollinger", "بولينجر", "البولينجر", "bollinger bands", "BB",
            "النطاق العلوي", "upper band", "النطاق السفلي", "lower band",
            "خط الوسط", "middle band", "النطاقات", "bands",
            "السعر لمس البولينجر", "السعر خارج البولينجر", "squeeze", "ضغط البولينجر",
            "بولينجر النفط", "بولينجر الفضة", "عرض النطاق", "band width",
            "%b", "بولينجر %b", "bandwidth", "الانحراف المعياري", "standard deviation",
            "البولينجر مفتوح", "البولينجر مضغوط", "bollinger squeeze", "bollinger expansion"
        ],
        regex_patterns=[
            r"(بولينجر|bollinger|BB)\s*(النفط|الفضة|الحين|الان)?",
            r"(النطاق|النطاقات|bands)\s*(العلوي|السفلي|الوسط|الحين)",
            r"(squeeze|ضغط|انكماش|توسع)\s*(بولينجر|النطاقات|bollinger)"
        ],
        handler="bollinger_analysis",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "moving_averages": IntentDefinition(
        intent_id="moving_averages",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "moving average", "المتوسط المتحرك", "المتوسطات", "ma", "sma", "ema",
            "المتوسط المتحرك البسيط", "المتوسط المتحرك الاسي", "simple moving average",
            "exponential moving average", "المتوسط المتحرك الاسي الاكثر سلاسة",
            "SMA 20", "SMA 50", "SMA 100", "SMA 200", "EMA 9", "EMA 12", "EMA 26",
            "السعر فوق المتوسط", "السعر تحت المتوسط", "crossover", "crossunder",
            "تقاطع المتوسطات", "golden cross", "death cross", "الصليب الذهبي", "الصليب الموت",
            "المتوسط النفط", "المتوسط الفضة", "السعر والمتوسط", "السعر والما",
            "السعر لمس المتوسط", "السعر اخترق المتوسط", "السعر فوق الميتين", "السعر تحت الميتين"
        ],
        regex_patterns=[
            r"(المتوسط|المتوسطات|ma|sma|ema)\s*(النفط|الفضة|الحين|الان)?",
            r"(SMA|EMA|MA)\s*(\d+)?\s*(النفط|الفضة)?",
            r"(golden cross|death cross|الصليب\s*(الذهبي|الموت)|تقاطع\s*(المتوسطات|الما))"
        ],
        handler="moving_averages",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "vwap_analysis": IntentDefinition(
        intent_id="vwap_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "vwap", "في واب", "الفي واب", "volume weighted average price",
            "السعر المتوسط المرجح بالحجم", "خط vwap", "مستوى vwap", "موقع vwap",
            "السعر فوق vwap", "السعر تحت vwap", "السعر عند vwap", "السعر لمس vwap",
            "vwap النفط", "vwap الفضة", "vwap اليوم", "vwap الجلسة", "vwap الاسبوعي",
            "anchored vwap", "vwap المربوط", "vwap الافتتاح", "vwap الهاي", "vwap اللو",
            "السعر وvwap", "السعر والفي واب", "السعر فوق الفي واب", "السعر تحت الفي واب"
        ],
        regex_patterns=[
            r"(vwap|في\s*واب|الفي\s*واب)\s*(النفط|الفضة|الحين|الان|السعر)?",
            r"(اين|وين|موقع|مستوى)\s*(vwap|الفي\s*واب|خط\s*الفي\s*واب)"
        ],
        handler="vwap_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "adx_analysis": IntentDefinition(
        intent_id="adx_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "adx", "ايدكس", "الايدكس", "average directional index",
            "مؤشر الاتجاه", "مؤشر القوة الاتجاهية", "directional movement index",
            "+DI", "-DI", "DI", "الخط الايجابي", "الخط السلبي",
            "adx النفط", "adx الفضة", "adx قوي", "adx ضعيف", "adx متوسط",
            "الاتجاه قوي", "الاتجاه ضعيف", "الاتجاه جانبي", "trend strength",
            "adx فوق 25", "adx فوق 50", "adx تحت 20", "adx تحت 25", "adx بين 20 و 25"
        ],
        regex_patterns=[
            r"(adx|ايدكس|الايدكس)\s*(النفط|الفضة|الحين|الان)?",
            r"(قوة|شدة|مستوى)\s*(الاتجاه|الترند|adx|الايدكس)"
        ],
        handler="adx_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "atr_analysis": IntentDefinition(
        intent_id="atr_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "atr", "اي تي ار", "الاي تي ار", "average true range",
            "مؤشر النطاق الحقيقي", "مؤشر التقلب", "volatility indicator",
            "atr النفط", "atr الفضة", "قيمة atr", "مستوى atr", "atr الحالي",
            "التقلب الحالي", "التقلب اليوم", "نطاق التقلب", "volatility range",
            "atr 14", "atr 7", "atr اليومي", "atr الساعة", "atr الفريم",
            "التقلب عالي", "التقلب منخفض", "التقلب متوسط", "high volatility", "low volatility"
        ],
        regex_patterns=[
            r"(atr|اي\s*تي\s*ار|الاي\s*تي\s*ار)\s*(النفط|الفضة|الحين|الان)?",
            r"(التقلب|volatility|نطاق\s*التقلب)\s*(الحالي|النفط|الفضة|الان|الحين)"
        ],
        handler="atr_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "stochastic_analysis": IntentDefinition(
        intent_id="stochastic_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "stochastic", "استوكاستيك", "الاستوكاستيك", "stoch", "استوك",
            "مؤشر الاستوكاستيك", "مؤشر العشوائي", "stochastic oscillator",
            "%K", "%D", "الخط السريع", "الخط البطيء", "fast stochastic", "slow stochastic",
            "stochastic النفط", "stochastic الفضة", "stochastic oversold", "stochastic overbought",
            "تشبع استوكاستيك", "stochastic فوق 80", "stochastic تحت 20", "stochastic بين",
            "stochastic divergence", "تباعد استوكاستيك", "stochastic crossover"
        ],
        regex_patterns=[
            r"(stochastic|استوكاستيك|استوك|stoch)\s*(النفط|الفضة|الحين|الان)?",
            r"(تشبع|overbought|oversold)\s*(استوكاستيك|stochastic|الاستوكاستيك)"
        ],
        handler="stochastic_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "fibonacci_analysis": IntentDefinition(
        intent_id="fibonacci_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "fibonacci", "فيبوناتشي", "الفيبوناتشي", "fib", "فيبو",
            "fibonacci retracement", "تصحيح فيبوناتشي", "fibonacci extension", "تمديد فيبوناتشي",
            "مستويات فيبوناتشي", "fibonacci levels", "38.2%", "50%", "61.8%", "78.6%",
            "النسبة الذهبية", "golden ratio", "fibonacci النفط", "fibonacci الفضة",
            " retracement", "تصحيح", " pullback", "تراجع", "bounce من فيبوناتشي",
            "السعر عند فيبوناتشي", "السعر لمس فيبوناتشي", "السعر اخترق فيبوناتشي",
            "fibonacci fan", "fibonacci arc", "fibonacci time zones", "fibonacci channel"
        ],
        regex_patterns=[
            r"(fibonacci|فيبوناتشي|فيبو|fib)\s*(النفط|الفضة|الحين|الان|التصحيح|التمديد)?",
            r"(مستوى|مستويات|نسبة|نسب)\s*(فيبوناتشي|fibonacci|الفيبوناتشي)"
        ],
        handler="fibonacci_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "ichimoku_analysis": IntentDefinition(
        intent_id="ichimoku_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "ichimoku", "ايشيموكو", "الايشيموكو", "ichimoku cloud", "سحابة ايشيموكو",
            "tenkan-sen", "kijun-sen", "senkou span a", "senkou span b", "chikou span",
            "التينكان", "الكيجون", "السينكو", "التشيكو", "السحابة", "الكلاود",
            "السعر فوق السحابة", "السعر تحت السحابة", "السعر داخل السحابة",
            "ichimoku النفط", "ichimoku الفضة", "تقاطع ايشيموكو", "crossover ichimoku",
            " bullish cloud", "bearish cloud", "سحابة صاعدة", "سحابة هابطة"
        ],
        regex_patterns=[
            r"(ichimoku|ايشيموكو|الايشيموكو|السحابة)\s*(النفط|الفضة|الحين|الان)?",
            r"(السحابة|الكلاود|cloud)\s*(ايشيموكو|الايشيموكو|النفط|الفضة)"
        ],
        handler="ichimoku_analysis",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "vpt_supertrend_analysis": IntentDefinition(
        intent_id="vpt_supertrend_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "vpt supertrend", "supertrend", "سوبر ترند", "السوبر ترند", "vpt",
            "volume price trend", "اتجاه السعر والحجم", "مؤشر vpt", "مؤشر supertrend",
            "supertrend النفط", "supertrend الفضة", "supertrend line", "خط supertrend",
            "السعر فوق supertrend", "السعر تحت supertrend", "تغير supertrend",
            "supertrend crossover", "supertrend crossunder", "supertrend flip",
            "vpt النفط", "vpt الفضة", "قيمة vpt", "مستوى vpt", "vpt trend"
        ],
        regex_patterns=[
            r"(supertrend|سوبر\s*ترند|السوبر\s*ترند|vpt)\s*(النفط|الفضة|الحين|الان)?",
            r"(تغير|تقلب|flip)\s*(supertrend|سوبر\s*ترند|السوبر\s*ترند)"
        ],
        handler="vpt_supertrend_analysis",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "pivot_points": IntentDefinition(
        intent_id="pivot_points",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "pivot points", "نقاط الارتكاز", "النقاط المحورية", "pivot", "البوفوت",
            "pivot النفط", "pivot الفضة", "نقاط المحور", "النقاط المحورية اليومية",
            "R1", "R2", "R3", "S1", "S2", "S3", "PP", "pivot point",
            "المقاومة 1", "المقاومة 2", "المقاومة 3", "الدعم 1", "الدعم 2", "الدعم 3",
            "النقطة المحورية", "السعر عند pivot", "السعر لمس pivot", "السعر اخترق pivot"
        ],
        regex_patterns=[
            r"(pivot|نقاط\s*الارتكاز|النقاط\s*المحورية|البوفوت)\s*(النفط|الفضة|الحين|الان)?",
            r"(R1|R2|R3|S1|S2|S3|PP)\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="pivot_points",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "order_flow_analysis": IntentDefinition(
        intent_id="order_flow_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "order flow", "تدفق الأوامر", "تدفق الطلبات", "order book", "دفتر الأوامر",
            "bid", "ask", "spread", "الفارق السعري", "السبريد", "العرض والطلب",
            "buy pressure", "sell pressure", "ضغط الشراء", "ضغط البيع",
            "delta", "cumulative delta", "CVD", "cumulative volume delta",
            "volume delta", "delta النفط", "delta الفضة", "delta analysis",
            "liquidity", "السيولة", "liquidity zones", "مناطق السيولة",
            "imbalance", "عدم التوازن", "order imbalance", "عدم توازن الطلبات",
            "footprint", "بصمة الحجم", "volume footprint", "heatmap", "خريطة الحرارة"
        ],
        regex_patterns=[
            r"(order flow|تدفق\s*(الأوامر|الطلبات)|order book|دفتر\s*الأوامر)\s*(النفط|الفضة)?",
            r"(delta|cvd|volume delta|الدلتا)\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="order_flow_analysis",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "open_interest": IntentDefinition(
        intent_id="open_interest",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "open interest", "الفائدة المفتوحة", "الاهتمام المفتوح", "OI",
            "open interest النفط", "open interest الفضة", "OI النفط", "OI الفضة",
            "الفائدة المفتوحة الحالية", "تغير الفائدة المفتوحة", "OI analysis",
            "الفائدة المفتوحة صاعدة", "الفائدة المفتوحة نازلة", "OI increasing", "OI decreasing",
            "الفائدة المفتوحة والسعر", "OI والسعر", "الفائدة المفتوحة والحجم"
        ],
        regex_patterns=[
            r"(open interest|الفائدة\s*المفتوحة|OI)\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="open_interest",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "funding_rate": IntentDefinition(
        intent_id="funding_rate",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "funding rate", "معدل التمويل", "التمويل", "funding", "funding النفط", "funding الفضة",
            "معدل التمويل الحالي", "funding rate الحالي", "funding positive", "funding negative",
            "التمويل ايجابي", "التمويل سلبي", "funding analysis", "تأثير التمويل",
            "funding rate impact", "تكلفة التمويل", "funding cost", "funding rate history"
        ],
        regex_patterns=[
            r"(funding rate|معدل\s*التمويل|التمويل)\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="funding_rate",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "liquidation_heatmap": IntentDefinition(
        intent_id="liquidation_heatmap",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "liquidation", "التصفية", "التصفيات", "liquidation heatmap", "خريطة التصفية",
            "liquidation levels", "مستويات التصفية", "liquidation zones", "مناطق التصفية",
            "liquidation النفط", "liquidation الفضة", "تصفية النفط", "تصفية الفضة",
            "long liquidation", "short liquidation", "تصفية الشراء", "تصفية البيع",
            "liquidation cascade", "تصفية متتالية", "liquidation wick", "فتيل التصفية",
            "liquidation data", "بيانات التصفية", "liquidation analysis"
        ],
        regex_patterns=[
            r"(liquidation|تصفية|التصفية|التصفيات)\s*(النفط|الفضة|الحين|الان|heatmap|خريطة)?",
            r"(heatmap|خريطة)\s*(التصفية|liquidation|التصفيات)"
        ],
        handler="liquidation_heatmap",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "sentiment_analysis": IntentDefinition(
        intent_id="sentiment_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "sentiment", "المعنويات", "المشاعر", "الشعور", "market sentiment",
            "المعنويات السوقية", "المشاعر السوقية", "sentiment النفط", "sentiment الفضة",
            "bullish sentiment", "bearish sentiment", "معنويات صاعدة", "معنويات هابطة",
            "sentiment index", "مؤشر المعنويات", "fear and greed", "الخوف والطمع",
            "fear index", "مؤشر الخوف", "greed index", "مؤشر الطمع",
            "sentiment analysis", "تحليل المعنويات", "المشاعر الحالية", "الشعور الحالي"
        ],
        regex_patterns=[
            r"(sentiment|المعنويات|المشاعر|الشعور)\s*(النفط|الفضة|السوق|الحين|الان)?",
            r"(fear and greed|الخوف\s*و\s*الطمع|fear index|greed index)\s*(النفط|الفضة)?"
        ],
        handler="sentiment_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "wyckoff_analysis": IntentDefinition(
        intent_id="wyckoff_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "wyckoff", "ويكوف", "الويكوف", "wyckoff method", "طريقة ويكوف",
            "wyckoff phases", "مراحل ويكوف", "accumulation", "distribution", "تجميع", "توزيع",
            "markup", "markdown", "صعود", "هبوط", "re-accumulation", "re-distribution",
            "spring", "upthrust", "spring ويكوف", "upthrust ويكوف",
            "wyckoff النفط", "wyckoff الفضة", "schematic", "رسم ويكوف", "wyckoff pattern"
        ],
        regex_patterns=[
            r"(wyckoff|ويكوف|الويكوف)\s*(النفط|الفضة|الحين|الان|الطريقة|المراحل)?",
            r"(مرحلة|مراحل|phase|phases)\s*(ويكوف|wyckoff|التجميع|التوزيع)"
        ],
        handler="wyckoff_analysis",
        priority=6,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "harmonic_patterns": IntentDefinition(
        intent_id="harmonic_patterns",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "harmonic patterns", "الأنماط التوافقية", "الأنماط الانسجامية", "harmonic",
            "gartley", "bat", "butterfly", "crab", "shark", "cypher", "5-0",
            "نمط جارتلي", "نمط الخفاش", "نمط الفراشة", "نمط السلطعون", "نمط القرش",
            "harmonic النفط", "harmonic الفضة", "harmonic pattern", "نمط harmonic",
            "XABCD pattern", "نمط XABCD", "PRZ", "potential reversal zone", "منطقة الانعكاس المحتملة"
        ],
        regex_patterns=[
            r"(harmonic|الأنماط\s*التوافقية|الأنماط\s*الانسجامية)\s*(النفط|الفضة|الحين|الان)?",
            r"(gartley|bat|butterfly|crab|shark|جارتلي|خفاش|فراشة|سلطعون|قرش)\s*(نمط|pattern)?"
        ],
        handler="harmonic_patterns",
        priority=6,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "elliott_wave": IntentDefinition(
        intent_id="elliott_wave",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "elliott wave", "موجات إليوت", "الموجات", "waves", "wave theory", "نظرية الموجات",
            "impulse wave", "corrective wave", "موجة دافعة", "موجة تصحيحية",
            "wave 1", "wave 2", "wave 3", "wave 4", "wave 5", "wave A", "wave B", "wave C",
            "fibonacci wave", "fibonacci and elliott", "elliott النفط", "elliott الفضة",
            "wave count", "عد الموجات", "wave analysis", "تحليل الموجات", "موجة إليوت"
        ],
        regex_patterns=[
            r"(elliott wave|موجات\s*إليوت|الموجات|waves)\s*(النفط|الفضة|الحين|الان)?",
            r"(wave|موجة|موجات)\s*(\d|[A-C])\s*(النفط|الفضة)?"
        ],
        handler="elliott_wave",
        priority=6,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "divergence_analysis": IntentDefinition(
        intent_id="divergence_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "divergence", "تباعد", "التباعد", "convergence", "تقارب", "التقارب",
            "bullish divergence", "bearish divergence", "hidden divergence", "regular divergence",
            "تباعد صاعد", "تباعد هابط", "تباعد مخفي", "تباعد عادي",
            "rsi divergence", "macd divergence", "stochastic divergence", "obv divergence",
            "تباعد rsi", "تباعد macd", "تباعد استوكاستيك", "تباعد النفط", "تباعد الفضة",
            "divergence analysis", "تحليل التباعد", "السعر والمؤشر", "price and indicator"
        ],
        regex_patterns=[
            r"(divergence|تباعد|التباعد|convergence|تقارب|التقارب)\s*(rsi|macd|استوكاستيك|النفط|الفضة|الحين|الان)?",
            r"(bullish|bearish|hidden|regular|صاعد|هابط|مخفي|عادي)\s*(divergence|تباعد|التباعد)"
        ],
        handler="divergence_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "support_resistance": IntentDefinition(
        intent_id="support_resistance",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "support", "resistance", "الدعم", "المقاومة", "مستويات الدعم", "مستويات المقاومة",
            "support level", "resistance level", "مستوى دعم", "مستوى مقاومة", "منطقة دعم", "منطقة مقاومة",
            "support zone", "resistance zone", "الدعم القوي", "المقاومة القوية", "الدعم الضعيف", "المقاومة الضعيفة",
            "السعر عند دعم", "السعر عند مقاومة", "السعر قرب دعم", "السعر قرب مقاومة",
            "كسر الدعم", "كسر المقاومة", "اختراق الدعم", "اختراق المقاومة", "break support", "break resistance",
            "الدعم التالي", "المقاومة التالية", "next support", "next resistance",
            "الدعم الرئيسي", "المقاومة الرئيسية", "major support", "major resistance",
            "الدعم النفط", "المقاومة النفط", "الدعم الفضة", "المقاومة الفضة"
        ],
        regex_patterns=[
            r"(الدعم|المقاومة|support|resistance)\s*(النفط|الفضة|الحين|الان|القريب|التالي|الرئيسي)?",
            r"(هل|وش|شو|كيف)\s*(السعر|النفط|الفضة)\s*(عند|قرب|لدى|على)\s*(دعم|مقاومة|support|resistance)"
        ],
        handler="support_resistance",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trend_lines": IntentDefinition(
        intent_id="trend_lines",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "trend line", "خط الاتجاه", "خطوط الاتجاه", "trendline", "الاتجاه",
            "خط صاعد", "خط هابط", "uptrend line", "downtrend line", "horizontal line",
            "خط افقي", "خط مائل", "angled line", "channel", "قناة", "قناة سعرية",
            "السعر لمس خط الاتجاه", "السعر كسر خط الاتجاه", "bounce من خط الاتجاه",
            "trend line النفط", "trend line الفضة", "خط الاتجاه النفط", "خط الاتجاه الفضة",
            "parallel channel", "قناة متوازية", "ascending channel", "descending channel", "قناة صاعدة", "قناة هابطة"
        ],
        regex_patterns=[
            r"(trend line|خط\s*الاتجاه|خطوط\s*الاتجاه|trendline)\s*(النفط|الفضة|الحين|الان)?",
            r"(قناة|channel)\s*(السعر|النفط|الفضة|الحين|الان|صاعدة|هابطة|متوازية)?"
        ],
        handler="trend_lines",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "chart_patterns": IntentDefinition(
        intent_id="chart_patterns",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "chart pattern", "نمط الرسم البياني", "النمط", "pattern", "النمط السعري",
            "head and shoulders", "الرأس والكتفين", "inverse head and shoulders", "الرأس والكتفين المقلوب",
            "double top", "double bottom", "triple top", "triple bottom",
            "قمة مزدوجة", "قاع مزدوج", "قمة ثلاثية", "قاع ثلاثي",
            "ascending triangle", "descending triangle", "symmetrical triangle",
            "مثلث صاعد", "مثلث هابط", "مثلث متناظر", "triangle pattern",
            "wedge", "وتد", "flag", "علم", "pennant", " pendant", "pennant pattern",
            "cup and handle", "الكوب والعروة", "rounding bottom", "قاع دائري",
            "rectangle", "مستطيل", "diamond", "معين", "pattern النفط", "pattern الفضة"
        ],
        regex_patterns=[
            r"(pattern|نمط|النمط|نماذج)\s*(السعر|النفط|الفضة|الحين|الان|الرسم\s*البياني)?",
            r"(head and shoulders|الرأس\s*و\s*الكتفين|double top|double bottom|قمة\s*مزدوجة|قاع\s*مزدوج)\s*(النفط|الفضة)?"
        ],
        handler="chart_patterns",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "volume_profile": IntentDefinition(
        intent_id="volume_profile",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "volume profile", "بروفايل الحجم", "توزيع الحجم", "volume distribution",
            "POC", "point of control", "نقطة التحكم", "value area", "منطقة القيمة",
            "VAH", "VAL", "value area high", "value area low", "high volume node", "low volume node",
            "HVN", "LVN", "node", "عقدة حجم", "عقدة حجم عالي", "عقدة حجم منخفض",
            "volume profile النفط", "volume profile الفضة", "الحجم عند السعر", "volume at price",
            "volume by price", "الحجم حسب السعر", "volume histogram", "هيستوجرام الحجم"
        ],
        regex_patterns=[
            r"(volume profile|بروفايل\s*الحجم|توزيع\s*الحجم)\s*(النفط|الفضة|الحين|الان)?",
            r"(POC|point of control|نقطة\s*التحكم|value area|منطقة\s*القيمة)\s*(النفط|الفضة)?"
        ],
        handler="volume_profile",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "correlation_analysis": IntentDefinition(
        intent_id="correlation_analysis",
        category=IntentCategory.TECHNICAL_INDICATORS,
        keywords=[
            "correlation", "ارتباط", "الارتباط", "correlation coefficient", "معامل الارتباط",
            "النفط والفضة", "oil and silver", "النفط والدولار", "oil and dollar", "الفضة والدولار", "silver and dollar",
            "النفط والذهب", "oil and gold", "الفضة والذهب", "silver and gold",
            "النفط والأسهم", "oil and stocks", "SPX and oil", "النفط وS&P500",
            "inverse correlation", "ارتباط عكسي", "positive correlation", "ارتباط ايجابي",
            "correlation analysis", "تحليل الارتباط", "correlation النفط", "correlation الفضة",
            "dxy correlation", "الدولار والنفط", "الدولار والفضة", "usd correlation"
        ],
        regex_patterns=[
            r"(correlation|ارتباط|الارتباط)\s*(النفط|الفضة|الدولار|الذهب|الأسهم|الحين|الان)?",
            r"(النفط|الفضة)\s*(و|and)\s*(الدولار|الذهب|الأسهم|SPX|S&P|DXY|النفط|الفضة)\s*(ارتباط|correlation)?"
        ],
        handler="correlation_analysis",
        priority=7,
        is_dynamic=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 3: إدارة الصفقات (TRADE_MANAGEMENT)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "trade_open": IntentDefinition(
        intent_id="trade_open",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "افتح صفقة", "ادخل صفقة", "صفقة جديدة", "أريد صفقة", "open trade", "new trade",
            "ادخل شراء", "ادخل بيع", "open buy", "open sell", "افتح شراء", "افتح بيع",
            "هل أفتح صفقة", "هل أدخل", "هل افتح", "هل ادخل", "should I open",
            "صفقة شراء النفط", "صفقة بيع النفط", "صفقة شراء الفضة", "صفقة بيع الفضة",
            "trade النفط", "trade الفضة", "position النفط", "position الفضة",
            "أريد ادخل النفط", "أريد ادخل الفضة", "دخول النفط", "دخول الفضة",
            "long النفط", "short النفط", "long الفضة", "short الفضة", "لونج", "شورت"
        ],
        regex_patterns=[
            r"(افتح|ادخل|دخل|open|new)\s*(صفقة|trade|position|شراء|بيع|لونج|شورت)?",
            r"(هل|وش|شو)\s*(أفتح|افتح|أدخل|ادخل|أدخل|ادخل)\s*(صفقة|النفط|الفضة|شراء|بيع)?"
        ],
        handler="trade_open",
        priority=10,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trade_close": IntentDefinition(
        intent_id="trade_close",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "أغلق الصفقة", "أخرج من الصفقة", "close trade", "exit trade", "اغلق الصفقة",
            "أغلق شراء", "أغلق بيع", "close buy", "close sell", "أغلق النفط", "أغلق الفضة",
            "هل أغلق", "هل أخرج", "should I close", "should I exit", "أخرج ولا لا", "أغلق ولا لا",
            "exit position", "خروج من الصفقة", "إغلاق الصفقة", "إغلاق المركز",
            "أغلق الصفقة الحالية", "أغلق المركز المفتوح", "أغلق كل الصفقات", "close all trades",
            "liquidate", "تصفية", "تصفية المركز", "أغلق فوراً", "أغلق الآن"
        ],
        regex_patterns=[
            r"(أغلق|اغلق|أخرج|اخرج|close|exit|liquidate)\s*(صفقة|الصفقة|النفط|الفضة|المركز|position|trade)?",
            r"(هل|وش|شو|أنصح|انصح)\s*(أغلق|اغلق|أخرج|اخرج|close|exit)\s*(ولا|او|أو|now|الان)?"
        ],
        handler="trade_close",
        priority=10,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trade_modify": IntentDefinition(
        intent_id="trade_modify",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "عدل الصفقة", "عدل SL", "عدل TP", "عدل وقف الخسارة", "عدل الهدف",
            "modify trade", "modify SL", "modify TP", "change stop loss", "change take profit",
            "حرك SL", "حرك TP", "نقل SL", "نقل TP", "move stop", "move target",
            "أقرب SL", "أبعد SL", "أقرب TP", "أبعد TP", " tighten stop", "widen stop",
            "breakeven", "نقطة التعادل", "الى التعادل", "move to breakeven", "السعر التعادلي",
            "trailing stop", "وقف متحرك", "وقف متعاقب", "تحريك الوقف", "تتبع الوقف",
            "عدل حجم الصفقة", "غير اللوت", "change lot size", "modify position size",
            "زود اللوت", "قلل اللوت", "increase lot", "decrease lot", "double down", "averaging down"
        ],
        regex_patterns=[
            r"(عدل|غير|حرك|نقل|modify|change|move)\s*(SL|TP|الصفقة|اللوت|الحجم|وقف|الهدف|stop|target|position)?",
            r"(breakeven|تعادل|نقطة\s*التعادل|الى\s*التعادل|trailing stop|وقف\s*متحرك)\s*(النفط|الفضة|الصفقة)?"
        ],
        handler="trade_modify",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trade_status": IntentDefinition(
        intent_id="trade_status",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "حالة الصفقة", "وضع الصفقة", "status", "trade status", "position status",
            "الصفقة الحالية", "المركز المفتوح", "الصفقة المفتوحة", "open position",
            "صفقتي", "مركزي", "my trade", "my position", "الصفقات المفتوحة", "open trades",
            "كم ربح الصفقة", "كم خسارة الصفقة", "الربح الحالي", "الخسارة الحالية",
            "الصفقة رابحة", "الصفقة خاسرة", "الصفقة متعادلة", "trade profit", "trade loss",
            "النفط صفقة", "الفضة صفقة", "صفقة النفط", "صفقة الفضة", "الصفقة وين وصلت",
            "الصفقة وين", "وين الصفقة", "وضع الصفقة الحالية", "حالة المركز"
        ],
        regex_patterns=[
            r"(حالة|وضع|status|state)\s*(الصفقة|الصفقات|المركز|المراكز|trade|position)?",
            r"(صفقتي|مركزي|my trade|my position|الصفقة\s*المفتوحة|المركز\s*المفتوح)\s*(الحين|الان|النفط|الفضة)?"
        ],
        handler="trade_status",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trade_history": IntentDefinition(
        intent_id="trade_history",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "تاريخ الصفقات", "سجل الصفقات", "trade history", "history", "السجل",
            "آخر صفقة", "الصفقة الأخيرة", "last trade", "previous trade", "الصفقة السابقة",
            "صفقات اليوم", "صفقات الأمس", "صفقات الأسبوع", "trades today", "trades yesterday",
            "أرباحي", "خسائري", "my profits", "my losses", "الربح الكلي", "الخسارة الكلية",
            "الأداء", "performance", "win rate", "نسبة الربح", "نسبة النجاح",
            "كم صفقة رابحة", "كم صفقة خاسرة", "عدد الصفقات", "total trades",
            "analyze last trade", "تحليل آخر صفقة", "لماذا خسرت", "لماذا ربحت",
            "trade report", "تقرير الصفقات", "performance report", "تقرير الأداء"
        ],
        regex_patterns=[
            r"(تاريخ|سجل|history|record|log)\s*(الصفقات|الصفقة|trades|trade|التداول)?",
            r"(آخر|الأخيرة|last|previous|السابقة)\s*(صفقة|trade|صفقتي|trade\s*my)",
            r"(أرباحي|خسائري|profits|losses|الأداء|performance|win rate|نسبة)\s*(الربح|الخسارة|النجاح|اليوم|الأسبوع|الشهر)?"
        ],
        handler="trade_history",
        priority=8,
        is_dynamic=True
    ),
    
    "trade_analysis": IntentDefinition(
        intent_id="trade_analysis",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "تحليل الصفقة", "trade analysis", "analyze trade", "تحليل صفقتي", "analyze my trade",
            "لماذا خسرت", "ليش خسرت", "لماذا ربحت", "ليش ربحت", "why did I lose", "why did I win",
            "سبب الخسارة", "سبب الربح", "reason for loss", "reason for profit",
            "الصفقة فاشلة", "الصفقة ناجحة", "failed trade", "successful trade",
            "ما الخطأ في الصفقة", "ما الصواب في الصفقة", "what went wrong", "what went right",
            "تقييم الصفقة", "trade review", "مراجعة الصفقة", "review trade",
            "الصفقة كانت جيدة", "الصفقة كانت سيئة", "good trade", "bad trade",
            "الدخول كان", "الخروج كان", "entry analysis", "exit analysis", "تحليل الدخول", "تحليل الخروج"
        ],
        regex_patterns=[
            r"(تحليل|analyze|review|مراجعة|تقييم)\s*(الصفقة|صفقتي|الصفقات|trade|trades|my trade)?",
            r"(لماذا|ليش|why|سبب|reason)\s*(خسرت|ربحت|lose|won|failed|succeeded|الخسارة|الربح)"
        ],
        handler="trade_analysis",
        priority=9,
        is_dynamic=True
    ),
    
    "trade_journal": IntentDefinition(
        intent_id="trade_journal",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "يومية التداول", "journal", "trade journal", "مذكرة التداول", "دفتر التداول",
            "سجل يومي", "daily journal", "تدوين", "notes", "ملاحظات التداول", "trading notes",
            "اكتب ملاحظة", "add note", "أضف ملاحظة", "سجل ملاحظة", "log note",
            "review journal", "راجع يوميتي", "my journal", "يوميتي", "journal اليوم",
            "trading diary", "مذكرات التداول", "diary", "مذكرتي"
        ],
        regex_patterns=[
            r"(يومية|journal|مذكرة|دفتر|diary|notes|ملاحظات)\s*(التداول|trading|التداول|trade|صفقاتي|my trades)?",
            r"(اكتب|add|سجل|log|أضف)\s*(ملاحظة|note|تدوين|entry)\s*(للصفقة|للتداول|لليوم)?"
        ],
        handler="trade_journal",
        priority=5,
        is_dynamic=False
    ),
    
    "trade_plan": IntentDefinition(
        intent_id="trade_plan",
        category=IntentCategory.TRADE_MANAGEMENT,
        keywords=[
            "خطة التداول", "trading plan", "plan", "الخطة", "خطتي", "my plan",
            "أعد خطة", "prepare plan", "صمم خطة", "design plan", "خطة للنفط", "خطة للفضة",
            "weekly plan", "خطة أسبوعية", "daily plan", "خطة يومية", "monthly plan", "خطة شهرية",
            "trading strategy", "استراتيجية التداول", "استراتيجيتي", "my strategy",
            "rules", "قواعد التداول", "trading rules", "discipline", "انضباط", "انضباط التداول",
            "checklist", "قائمة التحقق", "trading checklist", "قائمة ما قبل الدخول"
        ],
        regex_patterns=[
            r"(خطة|plan|استراتيجية|strategy|rules|قواعد|checklist|قائمة)\s*(التداول|trading|النفط|الفضة|اليوم|الأسبوع|الشهر)?",
            r"(أعد|صمم|جهز|prepare|design|create)\s*(خطة|plan|استراتيجية|strategy)\s*(للتداول|للنفط|للفضة)?"
        ],
        handler="trade_plan",
        priority=6,
        is_dynamic=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 4: إدارة المخاطر ورأس المال (RISK_MANAGEMENT)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "risk_assessment": IntentDefinition(
        intent_id="risk_assessment",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "تقييم المخاطر", "risk assessment", "risk analysis", "تحليل المخاطر",
            "مخاطر الصفقة", "trade risk", "مخاطر النفط", "مخاطر الفضة", "risk النفط", "risk الفضة",
            "هل الصفقة آمنة", "هل الصفقة خطرة", "is it safe", "is it risky",
            "مستوى الخطر", "risk level", "درجة المخاطرة", "risk degree",
            "المخاطر الحالية", "current risk", "exposure", "التعرض", "التعرض للمخاطر",
            "risk reward", "نسبة المخاطرة للمكافأة", "R:R", "risk ratio", "reward ratio",
            "هل الدخول آمن", "هل الدخول خطر", "safe entry", "risky entry"
        ],
        regex_patterns=[
            r"(تقييم|تحليل|assessment|analysis)\s*(المخاطر|risk|المخاطرة|الخطر|الصعوبة)?",
            r"(مخاطر|risk|خطر|صعوبة|تعقيد)\s*(الصفقة|النفط|الفضة|الدخول|التداول|الحين|الان)?",
            r"(هل|is)\s*(الصفقة|الدخول|it|النفط|الفضة)\s*(آمن|safe|خطير|risky|dangerous)?"
        ],
        handler="risk_assessment",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "position_sizing": IntentDefinition(
        intent_id="position_sizing",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "حجم الصفقة", "position size", "lot size", "حجم اللوت", "اللوت", "lot",
            "كم لوت", "كم حجم", "what lot size", "what position size", "كم عقد",
            "risk per trade", "المخاطرة لكل صفقة", "نسبة المخاطرة", "risk percentage",
            "1% risk", "2% risk", "نسبة 1%", "نسبة 2%", "risk per trade 1%",
            "حجم المركز", "position sizing", "حساب اللوت", "calculate lot", "lot calculation",
            "micro lot", "mini lot", "standard lot", "مايكرو لوت", "ميني لوت", "ستاندرد لوت",
            "كم أدخل", "كم أنصح بالدخول", "what size should I trade", "كم أنصح باللوت"
        ],
        regex_patterns=[
            r"(حجم|size|لوت|lot|عقد|contract)\s*(الصفقة|المركز|اللوت|النفط|الفضة|الحين|الان)?",
            r"(كم|what|how much|how many)\s*(لوت|lot|عقد|contract|حجم|size)\s*(أدخل|أفتح|trade|open|النفط|الفضة)?",
            r"(risk per trade|المخاطرة\s*لكل\s*صفقة|نسبة\s*المخاطرة)\s*(\d+%)?"
        ],
        handler="position_sizing",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "stop_loss_placement": IntentDefinition(
        intent_id="stop_loss_placement",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "وقف الخسارة", "stop loss", "SL", "الستوب", "الوقف", "stop",
            "أين أضع SL", "where to place stop", "مكان الوقف", "stop placement",
            "SL النفط", "SL الفضة", "stop loss النفط", "stop loss الفضة",
            "أقرب SL", "أبعد SL", "tight stop", "wide stop", "وقف قريب", "وقف بعيد",
            "mental stop", "وقف ذهني", "trailing stop", "وقف متحرك", "breakeven stop", "وقف التعادل",
            "stop based on ATR", "وقف حسب ATR", "ATR stop", "volatility stop", "وقف التقلب",
            "stop hunting", "صيد الوقف", "stop run", "تصفية الوقفات", "liquidity stop"
        ],
        regex_patterns=[
            r"(وقف|stop|SL|الستوب|الوقف)\s*(الخسارة|loss|النفط|الفضة|الحين|الان|الصفقة|مكان|موقع|أين|where)?",
            r"(أين|وين|where|مكان|موقع)\s*(أضع|احط|place|put|set)\s*(الوقف|SL|stop|الستوب)"
        ],
        handler="stop_loss_placement",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "take_profit_placement": IntentDefinition(
        intent_id="take_profit_placement",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "الهدف", "take profit", "TP", "التيك بروفيت", "الربح", "profit target",
            "أين الهدف", "where is target", "مكان الهدف", "target placement",
            "TP النفط", "TP الفضة", "take profit النفط", "take profit الفضة",
            "أقرب TP", "أبعد TP", "tight target", "wide target", "هدف قريب", "هدف بعيد",
            "multiple targets", "أهداف متعددة", "partial profit", "ربح جزئي", "scale out", "تخفيف المركز",
            "TP1", "TP2", "TP3", "الهدف الأول", "الهدف الثاني", "الهدف الثالث",
            "R1 target", "R2 target", "R3 target", "هدف فيبوناتشي", "fib target"
        ],
        regex_patterns=[
            r"(هدف|target|TP|take profit|الربح|profit)\s*(النفط|الفضة|الحين|الان|الصفقة|مكان|موقع|أين|where)?",
            r"(أين|وين|where|مكان|موقع)\s*(الهدف|TP|take profit|target)"
        ],
        handler="take_profit_placement",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "risk_reward_ratio": IntentDefinition(
        intent_id="risk_reward_ratio",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "risk reward", "نسبة المخاطرة للمكافأة", "R:R", "RR", "risk to reward",
            "نسبة RR", "نسبة المكافأة للمخاطرة", "reward to risk", "risk reward ratio",
            "1:1", "1:2", "1:3", "2:1", "3:1", "نسبة 1 الى 2", "نسبة 1 الى 3",
            "هل النسبة جيدة", "is the ratio good", "نسبة جيدة", "good ratio", "نسبة سيئة", "bad ratio",
            "minimum R:R", "الحد الأدنى لنسبة RR", "optimal R:R", "النسبة المثلى",
            "calculate R:R", "احسب RR", "نسبة الصفقة", "trade ratio", "النسبة الحالية"
        ],
        regex_patterns=[
            r"(risk reward|نسبة\s*المخاطرة|R:R|RR|risk to reward|reward to risk)\s*(النفط|الفضة|الحين|الان|الصفقة)?",
            r"(نسبة|ratio)\s*(\d+:\d+|\d+/\d+|RR|R:R)\s*(النفط|الفضة|الحين|الان|الصفقة|جيدة|سيئة)?"
        ],
        handler="risk_reward_ratio",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "portfolio_risk": IntentDefinition(
        intent_id="portfolio_risk",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "مخاطر المحفظة", "portfolio risk", "total risk", "المخاطرة الكلية", "overall risk",
            "exposure", "التعرض", "total exposure", "التعرض الكلي", "التعرض الحالي",
            "correlation risk", "مخاطر الارتباط", "concentration risk", "مخاطر التركيز",
            " diversification", "تنويع", "portfolio diversification", "تنويع المحفظة",
            "max drawdown", "أقصى انخفاض", "maximum drawdown", "التراجع الأقصى",
            "portfolio heat", "حرارة المحفظة", "heat index", "مؤشر الحرارة",
            "risk of ruin", "مخاطر الانهيار", "probability of ruin", "احتمال الانهيار"
        ],
        regex_patterns=[
            r"(مخاطر|risk|exposure|تعرض|heat|حرارة)\s*(المحفظة|portfolio|الكلية|total|الحالية|current)?",
            r"(drawdown|تراجع|انخفاض|ruin|انهيار)\s*(المحفظة|portfolio|الأقصى|maximum|الحالي|current)?"
        ],
        handler="portfolio_risk",
        priority=7,
        is_dynamic=True
    ),
    
    "drawdown_analysis": IntentDefinition(
        intent_id="drawdown_analysis",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "drawdown", "التراجع", "الانخفاض", "التراجع عن القمة", "التراجع الحالي",
            "max drawdown", "أقصى تراجع", "maximum drawdown", "التراجع الأقصى",
            "current drawdown", "التراجع الحالي", "drawdown period", "فترة التراجع",
            "recovery", "التعافي", "recovery from drawdown", "التعافي من التراجع",
            "drawdown analysis", "تحليل التراجع", "drawdown النفط", "drawdown الفضة",
            "equity curve", "منحنى رأس المال", "equity", "رأس المال", "balance", "الرصيد",
            "peak", "القمة", "trough", "القاع", "peak to trough", "من القمة للقاع"
        ],
        regex_patterns=[
            r"(drawdown|التراجع|الانخفاض|التراجع\s*عن\s*القمة)\s*(النفط|الفضة|الحين|الان|الأقصى|max|current|الحالي)?",
            r"(equity|رأس\s*المال|balance|الرصيد|peak|قمة|trough|قاع)\s*(الحالي|النفط|الفضة|curve|منحنى)?"
        ],
        handler="drawdown_analysis",
        priority=7,
        is_dynamic=True
    ),
    
    "margin_call_warning": IntentDefinition(
        intent_id="margin_call_warning",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "margin call", "نداء الهامش", "الهامش", "margin", "margin level",
            "مستوى الهامش", "margin النفط", "margin الفضة", "free margin", "الهامش المتاح",
            "used margin", "الهامش المستخدم", "margin requirement", "متطلبات الهامش",
            "leverage", "الرافعة المالية", "رافعة", "leverage ratio", "نسبة الرافعة",
            "1:100", "1:200", "1:500", "1:1000", "رافعة 100", "رافعة 200", "رافعة 500",
            "margin call risk", "خطر نداء الهامش", "قريب من margin call", "close to margin call",
            "stop out", "إيقاف الخسارة التلقائي", "stop out level", "مستوى الإيقاف"
        ],
        regex_patterns=[
            r"(margin|الهامش|margin call|نداء\s*الهامش|stop out|إيقاف)\s*(النفط|الفضة|الحين|الان|level|مستوى|risk|خطر)?",
            r"(leverage|رافعة|الرافعة|الرافعة\s*المالية)\s*(\d+)?\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="margin_call_warning",
        priority=10,
        is_dynamic=True
    ),
    
    "breakeven_analysis": IntentDefinition(
        intent_id="breakeven_analysis",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "breakeven", "نقطة التعادل", "التعادل", "break even", "BE", "نقطة BE",
            "الى التعادل", "move to breakeven", "نقل الى التعادل", "breakeven price",
            "سعر التعادل", "breakeven analysis", "تحليل التعادل", "breakeven النفط", "breakeven الفضة",
            "when to move to breakeven", "متى أنقل للتعادل", "breakeven strategy", "استراتيجية التعادل",
            "breakeven after", "التعادل بعد", "partial breakeven", "تعادل جزئي"
        ],
        regex_patterns=[
            r"(breakeven|تعادل|نقطة\s*التعادل|BE|break even)\s*(النفط|الفضة|الحين|الان|الصفقة|السعر|price|متى|when)?",
            r"(الى|نقل|move|transfer)\s*(التعادل|breakeven|BE|نقطة\s*التعادل)\s*(النفط|الفضة|الصفقة|متى|when)?"
        ],
        handler="breakeven_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trailing_stop_strategy": IntentDefinition(
        intent_id="trailing_stop_strategy",
        category=IntentCategory.RISK_MANAGEMENT,
        keywords=[
            "trailing stop", "وقف متحرك", "وقف متعاقب", "tracking stop", "متعاقب",
            "trailing stop النفط", "trailing stop الفضة", "trailing stop strategy", "استراتيجية الوقف المتحرك",
            "how to trail", "كيف أحرك الوقف", "trailing method", "طريقة التعاقب",
            "ATR trailing", "trailing by ATR", "تعاقب حسب ATR", "fixed trailing", "تعاقب ثابت",
            "percentage trailing", "تعاقب نسبي", "step trailing", "تعاقب متدرج",
            "trailing stop loss", "trailing SL", "تحريك الوقف", "متابعة الوقف"
        ],
        regex_patterns=[
            r"(trailing stop|وقف\s*متحرك|وقف\s*متعاقب|tracking stop|متعاقب)\s*(النفط|الفضة|الحين|الان|الصفقة|استراتيجية|طريقة)?",
            r"(كيف|how|طريقة|method|استراتيجية|strategy)\s*(أحرك|تحريك|متابعة|trail|trailing)\s*(الوقف|SL|stop|الستوب)"
        ],
        handler="trailing_stop_strategy",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 5: الأخبار والأحداث (NEWS_EVENTS)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "news_general": IntentDefinition(
        intent_id="news_general",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "news", "أخبار", "الأخبار", "latest news", "آخر الأخبار", "what's new", "ما الجديد",
            "مستجدات", "updates", "تحديثات", "latest updates", "آخر المستجدات",
            "أخبار السوق", "market news", "أخبار اليوم", "today's news", "أخبار الأسبوع",
            "مالجديد", "ما الجديد", "شو جديد", "وش جديد", "شنو جديد", "ش فيه جديد",
            "أخبار النفط", "oil news", "أخبار الفضة", "silver news", "commodity news", "أخبار السلع",
            "economic calendar", "التقويم الاقتصادي", "الأحداث الاقتصادية", "economic events",
            "news feed", "تغذية الأخبار", "news stream", "تيار الأخبار"
        ],
        regex_patterns=[
            r"(أخبار|news|مستجدات|updates|تحديثات|maljaded|ma\s*aljaded|sho\s*jadeed|wash\s*jadeed)\s*(السوق|النفط|الفضة|اليوم|الأسبوع|الحين|الان)?",
            r"(ما|شو|وش|شنو|what|what's)\s*(الجديد|new|جديد|حديث|fresh|الأخبار|news)"
        ],
        handler="news_general",
        priority=8,
        is_dynamic=True
    ),
    
    "oil_specific_news": IntentDefinition(
        intent_id="oil_specific_news",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "أخبار النفط", "oil news", "نفط", "oil", "بترول", "petroleum", "crude oil", "خام",
            "OPEC", "أوبك", "OPEC meeting", "اجتماع أوبك", "OPEC decision", "قرار أوبك",
            "oil production", "إنتاج النفط", "oil supply", "عرض النفط", "oil demand", "طلب النفط",
            "oil inventory", "مخزون النفط", "EIA report", "تقرير EIA", "API report", "تقرير API",
            "oil price reason", "سبب تحرك النفط", "why oil moved", "oil catalyst", "محفز النفط",
            " geopolitical oil", "نفط جيوسياسي", "war oil", "حرب والنفط", "sanctions oil", "عقوبات نفط",
            "oil export", "تصدير النفط", "oil import", "استيراد النفط", "Saudi oil", "نفط السعودية",
            "US oil", "نفط أمريكا", "shale oil", "نفط صخري", "Brent", "WTI", "برنت", "دبليو تي أي"
        ],
        regex_patterns=[
            r"(أخبار|news|مستجدات|updates|تحليل|analysis)\s*(النفط|oil|البترول|petroleum|crude|خام|OPEC|أوبك)",
            r"(OPEC|أوبك|EIA|API|Brent|WTI|برنت|النفط|oil)\s*(news|أخبار|meeting|اجتماع|report|تقرير|decision|قرار|inventory|مخزون)"
        ],
        handler="oil_specific_news",
        priority=9,
        is_dynamic=True
    ),
    
    "silver_specific_news": IntentDefinition(
        intent_id="silver_specific_news",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "أخبار الفضة", "silver news", "فضة", "silver", "XAG", "XAGUSD", "metal", "معدن",
            "precious metal", "معدن ثمين", "silver supply", "عرض الفضة", "silver demand", "طلب الفضة",
            "silver mining", "تعدين الفضة", "silver production", "إنتاج الفضة",
            "silver inventory", "مخزون الفضة", "silver ETF", "صناديق الفضة", "SLV", "iShares silver",
            "silver price reason", "سبب تحرك الفضة", "why silver moved", "silver catalyst", "محفز الفضة",
            "gold and silver", "الذهب والفضة", "gold silver ratio", "نسبة الذهب للفضة",
            "industrial silver", "فضة صناعية", "silver usage", "استخدامات الفضة", "solar silver", "فضة شمسية",
            "silver manipulation", "تلاعب الفضة", "silver squeeze", "ضغط الفضة", "silver shortage", "نقص الفضة"
        ],
        regex_patterns=[
            r"(أخبار|news|مستجدات|updates|تحليل|analysis)\s*(الفضة|silver|المعدن|metal|XAG|XAGUSD)",
            r"(silver|الفضة|XAG|XAGUSD)\s*(news|أخبار|supply|عرض|demand|طلب|mining|تعدين|ETF|inventory|مخزون|shortage|نقص)"
        ],
        handler="silver_specific_news",
        priority=9,
        is_dynamic=True
    ),
    
    "economic_events": IntentDefinition(
        intent_id="economic_events",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "economic events", "الأحداث الاقتصادية", "economic calendar", "التقويم الاقتصادي",
            "calendar", "التقويم", "events", "الأحداث", "economic data", "البيانات الاقتصادية",
            "NFP", "non-farm payrolls", "الرواتب غير الزراعية", "unemployment", "البطالة",
            "CPI", "inflation", "التضخم", "inflation rate", "معدل التضخم", "PPI", "producer price index",
            "GDP", "الناتج المحلي", "gross domestic product", "interest rate", "سعر الفائدة",
            "FOMC", "Fed meeting", "اجتماع الفيدرالي", "Fed decision", "قرار الفيدرالي", "Fed rate",
            "ECB", "European Central Bank", "البنك المركزي الأوروبي", "BOE", "Bank of England",
            "economic impact", "تأثير اقتصادي", "high impact news", "أخبار عالية التأثير", "red news", "أخبار حمراء",
            "news trading", "تداول الأخبار", "trading the news", "تداول عند الأخبار"
        ],
        regex_patterns=[
            r"(economic|اقتصادية|اقتصادي|calendar|تقويم|events|أحداث|data|بيانات)\s*(النفط|الفضة|السوق|الحين|الان|اليوم|الأسبوع)?",
            r"(NFP|CPI|GDP|FOMC|Fed|ECB|BOE|interest rate|سعر\s*الفائدة|inflation|التضخم|unemployment|البطالة)\s*(النفط|الفضة|الحين|الان|report|تقرير|news|أخبار|data|بيانات)?"
        ],
        handler="economic_events",
        priority=8,
        is_dynamic=True
    ),
    
    "event_impact": IntentDefinition(
        intent_id="event_impact",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "تأثير", "impact", "effect", "أثر", "تأثير الخبر", "news impact", "event impact",
            "كيف يؤثر", "how does it affect", "تأثير على النفط", "impact on oil", "تأثير على الفضة", "impact on silver",
            "تأثير الدولار", "dollar impact", "تأثير الفيدرالي", "Fed impact", "تأثير أوبك", "OPEC impact",
            "market reaction", "رد فعل السوق", "price reaction", "رد فعل السعر", "تأثير السعر",
            "volatility impact", "تأثير التقلب", "expected volatility", "التقلب المتوقع",
            "before news", "قبل الخبر", "after news", "بعد الخبر", "news timing", "توقيت الخبر"
        ],
        regex_patterns=[
            r"(تأثير|impact|effect|أثر|تأثيرات|impacts|effects)\s*(الخبر|الأخبار|النفط|الفضة|الدولار|الفيدرالي|أوبك|OPEC|Fed|السوق|السعر|التقلب)?",
            r"(كيف|how|طريقة|way|method)\s*(يؤثر|تأثير|impact|affect|effect|influence)\s*(الخبر|النفط|الفضة|السوق|السعر|التقلب)?"
        ],
        handler="event_impact",
        priority=8,
        is_dynamic=True
    ),
    
    "geopolitical_analysis": IntentDefinition(
        intent_id="geopolitical_analysis",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "geopolitical", "جيوسياسي", "جيوسياسية", "سياسي", "political", "سياسة",
            "war", "حرب", "conflict", "نزاع", "tension", "توتر", "crisis", "أزمة",
            "Middle East", "الشرق الأوسط", "Gulf", "الخليج", "Iran", "إيران", "Saudi", "السعودية",
            "Russia", "روسيا", "Ukraine", "أوكرانيا", "China", "الصين", "US China", "الصين وأمريكا",
            "sanctions", "عقوبات", "embargo", "حظر", "trade war", "حرب تجارية", "tariffs", "تعريفات جمركية",
            "elections", "انتخابات", "US elections", "الانتخابات الأمريكية", "political stability", "استقرار سياسي",
            "geopolitical risk", "مخاطر جيوسياسية", "geopolitical premium", "علاوة جيوسياسية"
        ],
        regex_patterns=[
            r"(geopolitical|جيوسياسي|جيوسياسية|سياسي|political|سياسة|war|حرب|conflict|نزاع|tension|توتر|crisis|أزمة)\s*(النفط|الفضة|السوق|الحين|الان|الشرق\s*الأوسط|الخليج|إيران|السعودية|روسيا|أوكرانيا|الصين|أمريكا)?",
            r"(sanctions|عقوبات|embargo|حظر|trade war|حرب\s*تجارية|tariffs|تعريفات)\s*(النفط|الفضة|السوق|روسيا|إيران|الصين|أمريكا)?"
        ],
        handler="geopolitical_analysis",
        priority=8,
        is_dynamic=True
    ),
    
    "weather_impact": IntentDefinition(
        intent_id="weather_impact",
        category=IntentCategory.NEWS_EVENTS,
        keywords=[
            "weather", "طقس", "climate", "مناخ", "hurricane", "إعصار", "storm", "عاصفة",
            "oil weather", "طقس النفط", "winter", "شتاء", "summer", "صيف", "heating season", "موسم التدفئة",
            "cold weather", "طقس بارد", "hot weather", "طقس حار", "freezing", "تجمد", "snow", "ثلج",
            "Gulf storm", "عاصفة الخليج", "Gulf hurricane", "إعصار الخليج", "Gulf weather", "طقس الخليج",
            "production disruption", "تعطيل الإنتاج", "supply disruption", "تعطيل الإمدادات",
            "weather forecast", "توقعات الطقس", "weather impact", "تأثير الطقس", "weather and oil", "الطقس والنفط"
        ],
        regex_patterns=[
            r"(weather|طقس|مناخ|climate|hurricane|إعصار|storm|عاصفة)\s*(النفط|الفضة|السوق|الخليج|الحين|الان|الإنتاج|الإمدادات)?",
            r"(winter|summer|شتاء|صيف|heating|تدفئة|cold|hot|بارد|حار|freezing|تجمد|snow|ثلج)\s*(النفط|oil|الطاقة|energy|التدفئة|heating)?"
        ],
        handler="weather_impact",
        priority=6,
        is_dynamic=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 6: التوقعات والسيناريوهات (PREDICTIONS)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "price_prediction": IntentDefinition(
        intent_id="price_prediction",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "توقع", "prediction", "forecast", "توقعات", "predict", "forecast", "تنبؤ", "anticipate",
            "النفط وين رايح", "الفضة وين رايحة", "where is oil going", "where is silver going",
            "النفط وين", "الفضة وين", "وين النفط", "وين الفضة", "oil direction", "silver direction",
            "هل يرتفع النفط", "هل ينخفض النفط", "هل ترتفع الفضة", "هل تنخفض الفضة",
            "will oil rise", "will oil fall", "will silver rise", "will silver fall",
            "النفط صاعد", "النفط هابط", "الفضة صاعدة", "الفضة هابطة", "bullish oil", "bearish oil",
            "المدى القريب", "المدى المتوسط", "المدى البعيد", "short term", "medium term", "long term",
            "الهدف القريب", "الهدف البعيد", "near target", "far target", "الأهداف", "targets",
            "price target", "هدف السعر", "expected price", "السعر المتوقع", "السعر المستهدف"
        ],
        regex_patterns=[
            r"(توقع|prediction|forecast|توقعات|predict|forecast|تنبؤ|anticipate|where|وين)\s*(النفط|الفضة|السعر|السوق|الحين|الان|القريب|البعيد|short|medium|long)?",
            r"(هل|will|would|could|might)\s*(النفط|الفضة|oil|silver|سعر|price)\s*(يرتفع|ينخفض|صاعد|هابط|rise|fall|go up|go down|increase|decrease)?"
        ],
        handler="price_prediction",
        priority=9,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "scenario_analysis": IntentDefinition(
        intent_id="scenario_analysis",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "سيناريو", "scenario", "سيناريوهات", "scenarios", "السيناريو الأفضل", "best scenario",
            "السيناريو الأسوأ", "worst scenario", "السيناريو المتوسط", "base scenario", "السيناريو الأساسي",
            "what if", "ماذا لو", "if then", "إذا فإن", "scenario planning", "تخطيط السيناريو",
            "bullish scenario", "سيناريو صاعد", "bearish scenario", "سيناريو هابط", "neutral scenario", "سيناريو حيادي",
            "scenario analysis", "تحليل السيناريو", "السيناريوهات المحتملة", "possible scenarios",
            "السيناريو النفط", "السيناريو الفضة", "oil scenario", "silver scenario"
        ],
        regex_patterns=[
            r"(سيناريو|scenario|سيناريوهات|scenarios)\s*(النفط|الفضة|الأفضل|الأسوأ|المتوسط|الأساسي|صاعد|هابط|حيادي|الحين|الان)?",
            r"(what if|ماذا\s*لو|if then|إذا\s*فإن)\s*(النفط|الفضة|السعر|السوق|الحين|الان)?"
        ],
        handler="scenario_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "explosion_prediction": IntentDefinition(
        intent_id="explosion_prediction",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "انفجار", "explosion", "انهيار", "collapse", "crash", "تحطم", "انهيار سعري",
            "صعود قوي", "strong rally", "هبوط حاد", "sharp drop", "breakout", "اختراق", "breakdown", "انهيار",
            "هل تتوقع انفجار", "هل تتوقع انهيار", "will it explode", "will it collapse",
            "حركة قوية قادمة", "strong move coming", "big move", "حركة كبيرة", "impending move", "حركة وشيكة",
            "volatility expansion", "توسع التقلب", "volatility spike", "ارتفاع التقلب",
            "momentum building", "زخم يتكون", "pressure building", "ضغط يتكون",
            "coiled spring", "نابض مضغوط", "pending breakout", "اختراق معلق", "pending breakdown", "انهيار معلق"
        ],
        regex_patterns=[
            r"(انفجار|explosion|انهيار|collapse|crash|تحطم|breakout|breakdown|اختراق|انهيار|صعود\s*قوي|هبوط\s*حاد)\s*(النفط|الفضة|السعر|السوق|الحين|الان|قادم|coming|وشيك|impending)?",
            r"(هل|will|would|could|might)\s*(تتوقع|expect|predict|forecast|anticipate)\s*(انفجار|explosion|انهيار|collapse|breakout|breakdown|صعود\s*قوي|هبوط\s*حاد|حركة\s*قوية|big\s*move|strong\s*move)"
        ],
        handler="explosion_prediction",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "reversal_expectation": IntentDefinition(
        intent_id="reversal_expectation",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "انعكاس", "reversal", "انعكاس السعر", "price reversal", " trend reversal", "انعكاس الاتجاه",
            "هل ينعكس", "will it reverse", "هل يرتد", "will it bounce", "ارتداد", "bounce",
            "انعكاس من الدعم", "reversal from support", "انعكاس من المقاومة", "reversal from resistance",
            "انعكاس صاعد", "bullish reversal", "انعكاس هابط", "bearish reversal",
            "V reversal", "انعكاس V", "U reversal", "انعكاس U", "W reversal", "انعكاس W",
            "top formation", "تشكيل قمة", "bottom formation", "تشكيل قاع", "double top reversal", "انعكاس قمة مزدوجة",
            "expected reversal", "الانعكاس المتوقع", "reversal zone", "منطقة الانعكاس", "reversal pattern", "نمط الانعكاس"
        ],
        regex_patterns=[
            r"(انعكاس|reversal|ارتداد|bounce|انعكاس\s*السعر|price\s*reversal|انعكاس\s*الاتجاه|trend\s*reversal)\s*(النفط|الفضة|السعر|السوق|الحين|الان|من\s*الدعم|من\s*المقاومة|صاعد|هابط)?",
            r"(هل|will|would|could|might)\s*(السعر|النفط|الفضة|it|price|oil|silver)\s*(ينعكس|يرتد|reverse|bounce|revert|turn|flip)"
        ],
        handler="reversal_expectation",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "target_levels": IntentDefinition(
        intent_id="target_levels",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "الأهداف", "targets", "الهدف", "target", "الأهداف القريبة", "near targets", "الأهداف البعيدة", "far targets",
            "الهدف القريب", "near target", "الهدف البعيد", "far target", "الهدف الأول", "first target", "الهدف الثاني", "second target",
            "TP1", "TP2", "TP3", "take profit 1", "take profit 2", "take profit 3",
            "expected high", "الهاي المتوقع", "expected low", "اللو المتوقع", "expected range", "النطاق المتوقع",
            "price objective", "الهدف السعري", "target price", "سعر الهدف", "target level", "مستوى الهدف",
            "next resistance target", "الهدف المقاومة التالي", "next support target", "الهدف دعم التالي"
        ],
        regex_patterns=[
            r"(الأهداف|targets|الهدف|target|الأهداف|targets)\s*(القريبة|near|البعيدة|far|الأولى|first|الثانية|second|النفط|الفضة|الحين|الان)?",
            r"(TP1|TP2|TP3|take profit 1|take profit 2|take profit 3|الهدف\s*الأول|الهدف\s*الثاني|الهدف\s*الثالث)\s*(النفط|الفضة|الحين|الان)?"
        ],
        handler="target_levels",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "time_prediction": IntentDefinition(
        intent_id="time_prediction",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "متى", "when", "الوقت", "time", "متى يرتفع", "متى ينخفض", "when will it rise", "when will it fall",
            "الوقت المتوقع", "expected time", "time frame", "الإطار الزمني", "time horizon", "الأفق الزمني",
            "متى الهدف", "when target", "متى الوقف", "when stop", "time to target", "الوقت للهدف", "time to stop", "الوقت للوقف",
            "expected duration", "المدة المتوقعة", "how long", "كم المدة", "duration", "المدة",
            "time cycle", "دورة زمنية", "cycle", "دورة", "time cycle analysis", "تحليل الدورات الزمنية",
            "seasonal", "موسمي", "seasonal pattern", "نمط موسمي", "monthly pattern", "نمط شهري", "weekly pattern", "نمط أسبوعي"
        ],
        regex_patterns=[
            r"(متى|when|الوقت|time|المدة|duration|كم\s*المدة|how\s*long)\s*(يرتفع|ينخفض|الهدف|الوقف|target|stop|النفط|الفضة|السعر|الحين|الان|القريب|البعيد)?",
            r"(time frame|إطار\s*زمني|time horizon|أفق\s*زمني|time cycle|دورة\s*زمنية|seasonal|موسمي)\s*(النفط|الفضة|الحين|الان|التحليل|analysis)?"
        ],
        handler="time_prediction",
        priority=7,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "probability_analysis": IntentDefinition(
        intent_id="probability_analysis",
        category=IntentCategory.PREDICTIONS,
        keywords=[
            "probability", "احتمال", "الاحتمال", "احتمالية", "likelihood", "فرصة", "chance", "odds",
            "ما احتمال", "what is the probability", "كم الاحتمال", "how likely", "ما الفرصة", "what are the odds",
            "probability of rise", "احتمال الصعود", "probability of fall", "احتمال الهبوط",
            "probability of breakout", "احتمال الاختراق", "probability of reversal", "احتمال الانعكاس",
            "win probability", "احتمال الربح", "loss probability", "احتمال الخسارة",
            "probability distribution", "توزيع الاحتمالات", "probability density", "كثافة الاحتمال",
            "high probability", "احتمال عالي", "low probability", "احتمال منخفض", "medium probability", "احتمال متوسط"
        ],
        regex_patterns=[
            r"(probability|احتمال|الاحتمال|احتمالية|likelihood|فرصة|chance|odds)\s*(الصعود|الهبوط|الاختراق|الانعكاس|الربح|الخسارة|النفط|الفضة|الحين|الان|عالي|منخفض|متوسط)?",
            r"(ما|كم|what|how)\s*(احتمال|probability|likelihood|chance|odds|فرصة)\s*(الصعود|الهبوط|الاختراق|الانعكاس|الربح|الخسارة|النفط|الفضة|السعر|السوق)?"
        ],
        handler="probability_analysis",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 7: التعلم والتحسين (LEARNING)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "learning_questions": IntentDefinition(
        intent_id="learning_questions",
        category=IntentCategory.LEARNING,
        keywords=[
            "ماذا تعلمت", "what did you learn", "تعلمت", "learned", "هل تتعلم", "do you learn",
            "تعلم", "learning", "تعلم من", "learn from", "تعلم من أخطائك", "learn from your mistakes",
            "تعلم من أخطائي", "learn from my mistakes", "تعلم من الصفقات", "learn from trades",
            "تحسن", "improve", "تحسين", "improvement", "تطور", "evolve", "تطور", "development",
            "دروس مستفادة", "lessons learned", "lessons", "دروس", "خبرات", "experiences", "تجارب",
            "هل تتحسن", "are you improving", "هل تتطور", "are you evolving", "هل تتعلم كل يوم", "do you learn every day",
            "feedback", "ملاحظات", "feedback loop", "حلقة التعلم", "learning loop", "حلقة التعلم",
            "continuous learning", "تعلم مستمر", "machine learning", "تعلم الآلة", "AI learning", "تعلم الذكاء الاصطناعي"
        ],
        regex_patterns=[
            r"(ماذا|what|هل|do|are)\s*(تعلمت|learned|تتعلم|learn|تحسن|improve|تتطور|evolve|تتعلم|learn)\s*(من|from|كل|every|يوم|day|أخطائك|your mistakes|أخطائي|my mistakes|الصفقات|trades)?",
            r"(دروس|lessons|خبرات|experiences|تجارب|feedback|ملاحظات|تحسين|improvement|تطور|evolution|development)\s*(مستفادة|learned|مستفادة|مستفادة|الحين|الان|التداول|trading|الصفقات|trades)?"
        ],
        handler="learning_questions",
        priority=6,
        is_dynamic=False
    ),
    
    "strategy_education": IntentDefinition(
        intent_id="strategy_education",
        category=IntentCategory.LEARNING,
        keywords=[
            "استراتيجية", "strategy", "استراتيجيات", "strategies", "طريقة", "method", "نهج", "approach",
            "تعلمني استراتيجية", "teach me a strategy", "شرح استراتيجية", "explain strategy",
            "كيف تتداول", "how do you trade", "طريقتك في التداول", "your trading method", "منهجيتك", "your methodology",
            "VPT Supertrend", "استراتيجية VPT", "استراتيجية السوبر ترند", "Supertrend strategy",
            "trend following", "متابعة الاتجاه", "mean reversion", "العودة للمتوسط", "breakout strategy", "استراتيجية الاختراق",
            "swing trading", "تداول التأرجح", "day trading", "تداول اليوم", "scalping", "سكالبينج",
            "position trading", "تداول المراكز", "long term trading", "تداول طويل الأجل",
            "strategy backtest", "اختبار استراتيجية", "backtest", "اختبار عكسي", "optimize strategy", "تحسين استراتيجية"
        ],
        regex_patterns=[
            r"(استراتيجية|strategy|استراتيجيات|strategies|طريقة|method|نهج|approach)\s*(التداول|trading|النفط|الفضة|الحين|الان|VPT|Supertrend|السوبر\s*ترند|تعلمني|teach|شرح|explain|اختبار|backtest|تحسين|optimize)?",
            r"(كيف|how|طريقة|method|منهجية|methodology)\s*(تتداول|trade|تداول|trading|النفط|الفضة|السوبر\s*ترند|VPT|Supertrend)?"
        ],
        handler="strategy_education",
        priority=6,
        is_dynamic=False
    ),
    
    "indicator_education": IntentDefinition(
        intent_id="indicator_education",
        category=IntentCategory.LEARNING,
        keywords=[
            "شرح مؤشر", "explain indicator", "مؤشر", "indicator", "كيف يعمل", "how does it work",
            "شرح RSI", "explain RSI", "شرح MACD", "explain MACD", "شرح Bollinger", "explain Bollinger",
            "شرح VWAP", "explain VWAP", "شرح ADX", "explain ADX", "شرح ATR", "explain ATR",
            "شرح Stochastic", "explain Stochastic", "شرح Fibonacci", "explain Fibonacci",
            "شرح Ichimoku", "explain Ichimoku", "شرح VPT", "explain VPT", "شرح Supertrend", "explain Supertrend",
            "what is", "ما هو", "what does", "ماذا يعني", "meaning of", "معنى",
            "indicator tutorial", "دورة مؤشر", "indicator guide", "دليل المؤشر", "indicator basics", "أساسيات المؤشر",
            "how to use", "كيف أستخدم", "indicator settings", "إعدادات المؤشر", "best settings", "أفضل إعدادات"
        ],
        regex_patterns=[
            r"(شرح|explain|what is|ما هو|what does|ماذا يعني|meaning of|معنى|how to use|كيف أستخدم)\s*(RSI|MACD|Bollinger|VWAP|ADX|ATR|Stochastic|Fibonacci|Ichimoku|VPT|Supertrend|المؤشر|indicator|المؤشرات|indicators)?",
            r"(indicator|مؤشر|indicators|المؤشرات|tutorial|دورة|guide|دليل|basics|أساسيات|settings|إعدادات)\s*(شرح|explain|دورة|tutorial|دليل|guide|أساسيات|basics|إعدادات|settings|النفط|الفضة|الحين|الان)?"
        ],
        handler="indicator_education",
        priority=6,
        is_dynamic=False
    ),
    
    "trading_psychology_education": IntentDefinition(
        intent_id="trading_psychology_education",
        category=IntentCategory.LEARNING,
        keywords=[
            "psychology", "نفسية", "سيكولوجية", "trading psychology", "نفسية التداول", "psychology of trading",
            "discipline", "انضباط", "discipline in trading", "انضباط التداول", "patience", "صبر", "patience in trading", "صبر التداول",
            "emotions", "عواطف", "emotions in trading", "عواطف التداول", "fear", "خوف", "fear of losing", "خوف الخسارة",
            "greed", "طمع", "greed in trading", "طمع التداول", "hope", "أمل", "hope in trading", "أمل التداول",
            "revenge trading", "تداول الانتقام", "overtrading", "التداول المفرط", "FOMO", "fear of missing out", "خوف الفوت",
            "trading mindset", "عقلية التداول", "mental game", "اللعبة العقلية", "trading discipline", "انضباط التداول",
            "psychology books", "كتب نفسية", "trading psychology books", "كتب نفسية التداول", "psychology course", "دورة نفسية"
        ],
        regex_patterns=[
            r"(psychology|نفسية|سيكولوجية|psychology of trading|نفسية\s*التداول|discipline|انضباط|patience|صبر|emotions|عواطف|fear|خوف|greed|طمع|hope|أمل|revenge trading|تداول\s*الانتقام|overtrading|التداول\s*المفرط|FOMO|fear of missing out|خوف\s*الفوت|trading mindset|عقلية\s*التداول|mental game|اللعبة\s*العقلية|trading discipline|انضباط\s*التداول|psychology books|كتب\s*نفسية|trading psychology books|كتب\s*نفسية\s*التداول|psychology course|دورة\s*نفسية)\s*(التداول|trading|النفط|الفضة|الحين|الان|الصفقات|trades|التعلم|learning)?",
            r"(psychology|نفسية|سيكولوجية|discipline|انضباط|patience|صبر|emotions|عواطف|fear|خوف|greed|طمع|hope|أمل|revenge trading|تداول\s*الانتقام|overtrading|التداول\s*المفرط|FOMO|fear of missing out|خوف\s*الفوت|trading mindset|عقلية\s*التداول|mental game|اللعبة\s*العقلية|trading discipline|انضباط\s*التداول|psychology books|كتب\s*نفسية|trading psychology books|كتب\s*نفسية\s*التداول|psychology course|دورة\s*نفسية)\s*(التداول|trading|النفط|الفضة|الحين|الان|الصفقات|trades|التعلم|learning)?"
        ],
        handler="trading_psychology_education",
        priority=6,
        is_dynamic=False
    ),
    
    "market_microstructure": IntentDefinition(
        intent_id="market_microstructure",
        category=IntentCategory.LEARNING,
        keywords=[
            "market microstructure", "البنية الدقيقة للسوق", "microstructure", "التركيب الدقيق",
            "order book", "دفتر الأوامر", "limit order", "أمر محدد", "market order", "أمر سوق",
            "bid ask spread", "الفارق بين العرض والطلب", "liquidity", "السيولة", "market maker", "صانع السوق",
            "slippage", "انزلاق", "slippage in trading", "انزلاق في التداول", "latency", "تأخر", "execution speed", "سرعة التنفيذ",
            "order flow", "تدفق الأوامر", "order flow trading", "تداول تدفق الأوامر", "market depth", "عمق السوق",
            "tick data", "بيانات التيك", "tick", "تيك", "tick size", "حجم التيك", "tick value", "قيمة التيك",
            "microstructure analysis", "تحليل البنية الدقيقة", "market mechanics", "ميكانيكا السوق"
        ],
        regex_patterns=[
            r"(market microstructure|البنية\s*الدقيقة\s*للسوق|microstructure|التركيب\s*الدقيق|order book|دفتر\s*الأوامر|limit order|أمر\s*محدد|market order|أمر\s*سوق|bid ask spread|الفارق\s*بين\s*العرض\s*و\s*الطلب|liquidity|السيولة|market maker|صانع\s*السوق|slippage|انزلاق|latency|تأخر|execution speed|سرعة\s*التنفيذ|order flow|تدفق\s*الأوامر|market depth|عمق\s*السوق|tick data|بيانات\s*التيك|tick|تيك|tick size|حجم\s*التيك|tick value|قيمة\s*التيك|microstructure analysis|تحليل\s*البنية\s*الدقيقة|market mechanics|ميكانيكا\s*السوق)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|التعلم|learning)?",
            r"(market microstructure|البنية\s*الدقيقة\s*للسوق|microstructure|التركيب\s*الدقيق|order book|دفتر\s*الأوامر|limit order|أمر\s*محدد|market order|أمر\s*سوق|bid ask spread|الفارق\s*بين\s*العرض\s*و\s*الطلب|liquidity|السيولة|market maker|صانع\s*السوق|slippage|انزلاق|latency|تأخر|execution speed|سرعة\s*التنفيذ|order flow|تدفق\s*الأوامر|market depth|عمق\s*السوق|tick data|بيانات\s*التيك|tick|تيك|tick size|حجم\s*التيك|tick value|قيمة\s*التيك|microstructure analysis|تحليل\s*البنية\s*الدقيقة|market mechanics|ميكانيكا\s*السوق)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|التعلم|learning)?"
        ],
        handler="market_microstructure",
        priority=5,
        is_dynamic=False
    ),
    
    "backtesting_education": IntentDefinition(
        intent_id="backtesting_education",
        category=IntentCategory.LEARNING,
        keywords=[
            "backtest", "اختبار عكسي", "backtesting", "اختبار استراتيجية", "strategy test", "اختبار الاستراتيجية",
            "how to backtest", "كيف أختبر", "backtest results", "نتائج الاختبار العكسي", "backtest report", "تقرير الاختبار العكسي",
            "historical test", "اختبار تاريخي", "walk forward analysis", "تحليل المشي للأمام", "forward test", "اختبار أمامي",
            "backtest software", "برنامج اختبار عكسي", "backtest platform", "منصة اختبار عكسي",
            "optimization", "تحسين", "overfitting", "مبالغة في التحسين", "curve fitting", "ملاءمة المنحنى",
            "robustness", "متانة", "robustness test", "اختبار المتانة", "out of sample", "خارج العينة", "in sample", "داخل العينة"
        ],
        regex_patterns=[
            r"(backtest|اختبار\s*عكسي|backtesting|اختبار\s*استراتيجية|strategy test|اختبار\s*الاستراتيجية|how to backtest|كيف\s*أختبر|backtest results|نتائج\s*الاختبار\s*العكسي|backtest report|تقرير\s*الاختبار\s*العكسي|historical test|اختبار\s*تاريخي|walk forward analysis|تحليل\s*المشي\s*للأمام|forward test|اختبار\s*أمامي|backtest software|برنامج\s*اختبار\s*عكسي|backtest platform|منصة\s*اختبار\s*عكسي|optimization|تحسين|overfitting|مبالغة\s*في\s*التحسين|curve fitting|ملاءمة\s*المنحنى|robustness|متانة|robustness test|اختبار\s*المتانة|out of sample|خارج\s*العينة|in sample|داخل\s*العينة)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|التعلم|learning|الاستراتيجية|strategy)?",
            r"(backtest|اختبار\s*عكسي|backtesting|اختبار\s*استراتيجية|strategy test|اختبار\s*الاستراتيجية|how to backtest|كيف\s*أختبر|backtest results|نتائج\s*الاختبار\s*العكسي|backtest report|تقرير\s*الاختبار\s*العكسي|historical test|اختبار\s*تاريخي|walk forward analysis|تحليل\s*المشي\s*للأمام|forward test|اختبار\s*أمامي|backtest software|برنامج\s*اختبار\s*عكسي|backtest platform|منصة\s*اختبار\s*عكسي|optimization|تحسين|overfitting|مبالغة\s*في\s*التحسين|curve fitting|ملاءمة\s*المنحنى|robustness|متانة|robustness test|اختبار\s*المتانة|out of sample|خارج\s*العينة|in sample|داخل\s*العينة)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|التعلم|learning|الاستراتيجية|strategy)?"
        ],
        handler="backtesting_education",
        priority=5,
        is_dynamic=False
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 8: السيكولوجيا والنفسية (PSYCHOLOGY)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "emotional_support": IntentDefinition(
        intent_id="emotional_support",
        category=IntentCategory.PSYCHOLOGY,
        keywords=[
            "خسرت", "lost", "خسارة", "loss", "خسارتي", "my losses", "خسرت اليوم", "lost today",
            "حزين", "sad", "مكتئب", "depressed", "محبط", "frustrated", "غاضب", "angry", "عصبي", "nervous",
            "قلق", "anxious", "worried", "مقلق", "stressed", "متوتّر", "ضغط", "pressure", "توتر", "tension",
            "مساعدة", "help", "ساعدني", "help me", "أحتاج مساعدة", "need help", "أشعر ب", "I feel",
            "لا أستطيع", "can't", "صعب علي", "hard for me", "صعبة", "difficult", "تعبت", "tired", "إرهاق", "burnout",
            "revenge", "انتقام", "أريد انتقام", "want revenge", "أريد استرداد", "want to recover", "استرداد الخسارة", "recover loss",
            "FOMO", "fear of missing out", "خوف الفوت", "خائف أفوت", "afraid to miss", "missed opportunity", "فرصة فاتت",
            "overtrading", "التداول المفرط", "تداول كثير", "trading too much", "cant stop trading", "لا أستطيع التوقف",
            "talk to me", "تحدث معي", "فضفضة", "vent", "أريد أفضفض", "want to vent", "listen to me", "اسمعني"
        ],
        regex_patterns=[
            r"(خسرت|lost|خسارة|loss|خسارتي|my losses|خسرت\s*اليوم|lost\s*today|حزين|sad|مكتئب|depressed|محبط|frustrated|غاضب|angry|عصبي|nervous|قلق|anxious|worried|مقلق|stressed|متوتّر|ضغط|pressure|توتر|tension|مساعدة|help|ساعدني|help me|أحتاج\s*مساعدة|need\s*help|أشعر\s*ب|I\s*feel|لا\s*أستطيع|can't|صعب\s*علي|hard\s*for\s*me|صعبة|difficult|تعبت|tired|إرهاق|burnout|revenge|انتقام|أريد\s*انتقام|want\s*revenge|أريد\s*استرداد|want\s*to\s*recover|استرداد\s*الخسارة|recover\s*loss|FOMO|fear\s*of\s*missing\s*out|خوف\s*الفوت|خائف\s*أفوت|afraid\s*to\s*miss|missed\s*opportunity|فرصة\s*فاتت|overtrading|التداول\s*المفرط|تداول\s*كثير|trading\s*too\s*much|cant\s*stop\s*trading|لا\s*أستطيع\s*التوقف|talk\s*to\s*me|تحدث\s*معي|فضفضة|vent|أريد\s*أفضفض|want\s*to\s*vent|listen\s*to\s*me|اسمعني)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(خسرت|lost|خسارة|loss|خسارتي|my losses|خسرت\s*اليوم|lost\s*today|حزين|sad|مكتئب|depressed|محبط|frustrated|غاضب|angry|عصبي|nervous|قلق|anxious|worried|مقلق|stressed|متوتّر|ضغط|pressure|توتر|tension|مساعدة|help|ساعدني|help me|أحتاج\s*مساعدة|need\s*help|أشعر\s*ب|I\s*feel|لا\s*أستطيع|can't|صعب\s*علي|hard\s*for\s*me|صعبة|difficult|تعبت|tired|إرهاق|burnout|revenge|انتقام|أريد\s*انتقام|want\s*revenge|أريد\s*استرداد|want\s*to\s*recover|استرداد\s*الخسارة|recover\s*loss|FOMO|fear\s*of\s*missing\s*out|خوف\s*الفوت|خائف\s*أفوت|afraid\s*to\s*miss|missed\s*opportunity|فرصة\s*فاتت|overtrading|التداول\s*المفرط|تداول\s*كثير|trading\s*too\s*much|cant\s*stop\s*trading|لا\s*أستطيع\s*التوقف|talk\s*to\s*me|تحدث\s*معي|فضفضة|vent|أريد\s*أفضفض|want\s*to\s*vent|listen\s*to\s*me|اسمعني)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="emotional_support",
        priority=10,
        is_dynamic=False,
        response_template="""
💙 **أنا هنا معك...**

أعلم أن التداول يمكن أن يكون مرهقاً أحياناً. خسائرك ليست نهاية العالم، بل هي جزء من الرحلة.

🌱 **تذكر:**
• كل متداول ناجح مر بخسائر
• المهم هو التعلم منها والمضي قدماً
• خذ نفساً عميقاً واسترح إذا احتجت
• لا تتداول وأنت عاطفي - هذا قرار حكيم

📌 **نصيحتي الآن:**
• اغلق الشارت وخذ استراحة
• راجع خطتك بهدوء لاحقاً
• تذكر لماذا بدأت من الأساس

**أنا معك، وكل يوم جديد هو فرصة جديدة.** 💪
"""
    ),
    
    "motivation": IntentDefinition(
        intent_id="motivation",
        category=IntentCategory.PSYCHOLOGY,
        keywords=[
            "حافز", "motivation", "تحفيز", "inspiration", "إلهام", "شجاعة", "courage", "قوة", "strength",
            "أحتاج حافز", "need motivation", "أحتاج تحفيز", "need inspiration", "أشجعني", "encourage me",
            "نصيحة تحفيزية", "motivational advice", "كلمات", "words", "اقتباس", "quote", "حكمة", "wisdom",
            "trading quotes", "اقتباسات تداول", "trading wisdom", "حكمة تداول", "success story", "قصة نجاح",
            "never give up", "لا تستسلم", "keep going", "استمر", "persistence", "مثابرة", "resilience", "مرونة نفسية",
            "trading journey", "رحلة التداول", "trading path", "مسار التداول", "trading career", "مهنة التداول"
        ],
        regex_patterns=[
            r"(حافز|motivation|تحفيز|inspiration|إلهام|شجاعة|courage|قوة|strength|أحتاج\s*حافز|need\s*motivation|أحتاج\s*تحفيز|need\s*inspiration|أشجعني|encourage\s*me|نصيحة\s*تحفيزية|motivational\s*advice|كلمات|words|اقتباس|quote|حكمة|wisdom|trading\s*quotes|اقتباسات\s*تداول|trading\s*wisdom|حكمة\s*تداول|success\s*story|قصة\s*نجاح|never\s*give\s*up|لا\s*تستسلم|keep\s*going|استمر|persistence|مثابرة|resilience|مرونة\s*نفسية|trading\s*journey|رحلة\s*التداول|trading\s*path|مسار\s*التداول|trading\s*career|مهنة\s*التداول)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(حافز|motivation|تحفيز|inspiration|إلهام|شجاعة|courage|قوة|strength|أحتاج\s*حافز|need\s*motivation|أحتاج\s*تحفيز|need\s*inspiration|أشجعني|encourage\s*me|نصيحة\s*تحفيزية|motivational\s*advice|كلمات|words|اقتباس|quote|حكمة|wisdom|trading\s*quotes|اقتباسات\s*تداول|trading\s*wisdom|حكمة\s*تداول|success\s*story|قصة\s*نجاح|never\s*give\s*up|لا\s*تستسلم|keep\s*going|استمر|persistence|مثابرة|resilience|مرونة\s*نفسية|trading\s*journey|رحلة\s*التداول|trading\s*path|مسار\s*التداول|trading\s*career|مهنة\s*التداول)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="motivation",
        priority=6,
        is_dynamic=False,
        response_template="""
🌟 **تذكر دائماً:**

> *"النجاح في التداول ليس عن عدم الخسارة، بل عن كيفية التعامل مع الخسارة."*

💪 **أنت أقوى مما تعتقد!**
• كل صفقة خاسرة هي درس
• كل يوم جديد هو فرصة
• الصبر هو أقوى سلاحك
• الانضباط يفوق الذكاء

🚀 **استمر، والنجاح سيأتي بالمثابرة!**
"""
    ),
    
    "fear_greed_assessment": IntentDefinition(
        intent_id="fear_greed_assessment",
        category=IntentCategory.PSYCHOLOGY,
        keywords=[
            "fear", "خوف", "greed", "طمع", "fear and greed", "الخوف والطمع", "fear index", "مؤشر الخوف",
            "greed index", "مؤشر الطمع", "fear greed index", "مؤشر الخوف والطمع", "sentiment", "المشاعر",
            "market sentiment", "مشاعر السوق", "trader sentiment", "مشاعر المتداولين", "crowd psychology", "نفسية الجماهير",
            "herd behavior", "سلوك القطيع", "panic", "ذعر", "euphoria", "نشوة", "optimism", "تفاؤل", "pessimism", "تشاؤم",
            "fear of missing out", "FOMO", "خوف الفوت", "fear of loss", "خوف الخسارة", "greed for profit", "طمع الربح",
            "emotional state", "الحالة العاطفية", "emotional check", "فحص عاطفي", "emotional thermometer", "ميزان الحرارة العاطفي"
        ],
        regex_patterns=[
            r"(fear|خوف|greed|طمع|fear and greed|الخوف\s*والطمع|fear index|مؤشر\s*الخوف|greed index|مؤشر\s*الطمع|fear greed index|مؤشر\s*الخوف\s*والطمع|sentiment|المشاعر|market sentiment|مشاعر\s*السوق|trader sentiment|مشاعر\s*المتداولين|crowd psychology|نفسية\s*الجماهير|herd behavior|سلوك\s*القطيع|panic|ذعر|euphoria|نشوة|optimism|تفاؤل|pessimism|تشاؤم|fear of missing out|FOMO|خوف\s*الفوت|fear of loss|خوف\s*الخسارة|greed for profit|طمع\s*الربح|emotional state|الحالة\s*العاطفية|emotional check|فحص\s*عاطفي|emotional thermometer|ميزان\s*الحرارة\s*العاطفي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(fear|خوف|greed|طمع|fear and greed|الخوف\s*والطمع|fear index|مؤشر\s*الخوف|greed index|مؤشر\s*الطمع|fear greed index|مؤشر\s*الخوف\s*والطمع|sentiment|المشاعر|market sentiment|مشاعر\s*السوق|trader sentiment|مشاعر\s*المتداولين|crowd psychology|نفسية\s*الجماهير|herd behavior|سلوك\s*القطيع|panic|ذعر|euphoria|نشوة|optimism|تفاؤل|pessimism|تشاؤم|fear of missing out|FOMO|خوف\s*الفوت|fear of loss|خوف\s*الخسارة|greed for profit|طمع\s*الربح|emotional state|الحالة\s*العاطفية|emotional check|فحص\s*عاطفي|emotional thermometer|ميزان\s*الحرارة\s*العاطفي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="fear_greed_assessment",
        priority=8,
        is_dynamic=True,
        requires_asset=True
    ),
    
    "trading_mindset_check": IntentDefinition(
        intent_id="trading_mindset_check",
        category=IntentCategory.PSYCHOLOGY,
        keywords=[
            "mindset", "عقلية", "trading mindset", "عقلية التداول", "mental state", "الحالة العقلية",
            "ready to trade", "جاهز للتداول", "am I ready", "هل أنا جاهز", "should I trade", "هل أتداول",
            "mental preparation", "التحضير العقلي", "pre-trade routine", "روتين ما قبل التداول", "trading routine", "روتين التداول",
            "focus", "تركيز", "concentration", "تركيز", "mental clarity", "وضوح عقلي", "mental fog", "ضباب عقلي",
            "fatigue", "تعب", "trading fatigue", "تعب التداول", "burnout", "إرهاق", "trading burnout", "إرهاق التداول",
            "sleep", "نوم", "rest", "راحة", "relaxation", "استرخاء", "meditation", "تأمل", "mindfulness", "انتباه ذهني"
        ],
        regex_patterns=[
            r"(mindset|عقلية|trading mindset|عقلية\s*التداول|mental state|الحالة\s*العقلية|ready to trade|جاهز\s*للتداول|am I ready|هل\s*أنا\s*جاهز|should I trade|هل\s*أتداول|mental preparation|التحضير\s*العقلي|pre-trade routine|روتين\s*ما\s*قبل\s*التداول|trading routine|روتين\s*التداول|focus|تركيز|concentration|تركيز|mental clarity|وضوح\s*عقلي|mental fog|ضباب\s*عقلي|fatigue|تعب|trading fatigue|تعب\s*التداول|burnout|إرهاق|trading burnout|إرهاق\s*التداول|sleep|نوم|rest|راحة|relaxation|استرخاء|meditation|تأمل|mindfulness|انتباه\s*ذهني)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(mindset|عقلية|trading mindset|عقلية\s*التداول|mental state|الحالة\s*العقلية|ready to trade|جاهز\s*للتداول|am I ready|هل\s*أنا\s*جاهز|should I trade|هل\s*أتداول|mental preparation|التحضير\s*العقلي|pre-trade routine|روتين\s*ما\s*قبل\s*التداول|trading routine|روتين\s*التداول|focus|تركيز|concentration|تركيز|mental clarity|وضوح\s*عقلي|mental fog|ضباب\s*عقلي|fatigue|تعب|trading fatigue|تعب\s*التداول|burnout|إرهاق|trading burnout|إرهاق\s*التداول|sleep|نوم|rest|راحة|relaxation|استرخاء|meditation|تأمل|mindfulness|انتباه\s*ذهني)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="trading_mindset_check",
        priority=7,
        is_dynamic=False
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 9: التحكم بالبوت (BOT_CONTROL)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "bot_settings": IntentDefinition(
        intent_id="bot_settings",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "إعدادات", "settings", "config", "configuration", "تكوين", "اعدادات البوت", "bot settings",
            "غير الإعدادات", "change settings", "عدل الإعدادات", "modify settings", "تحديث الإعدادات", "update settings",
            "risk settings", "إعدادات المخاطر", "trading settings", "إعدادات التداول", "alert settings", "إعدادات التنبيهات",
            "timeframe settings", "إعدادات الفريم", "indicator settings", "إعدادات المؤشرات", "strategy settings", "إعدادات الاستراتيجية",
            "default settings", "الإعدادات الافتراضية", "reset settings", "إعادة تعيين الإعدادات", "factory reset", "إعادة ضبط المصنع",
            "settings menu", "قائمة الإعدادات", "settings list", "قائمة الإعدادات", "show settings", "عرض الإعدادات"
        ],
        regex_patterns=[
            r"(إعدادات|settings|config|configuration|تكوين|اعدادات\s*البوت|bot\s*settings|غير\s*الإعدادات|change\s*settings|عدل\s*الإعدادات|modify\s*settings|تحديث\s*الإعدادات|update\s*settings|risk\s*settings|إعدادات\s*المخاطر|trading\s*settings|إعدادات\s*التداول|alert\s*settings|إعدادات\s*التنبيهات|timeframe\s*settings|إعدادات\s*الفريم|indicator\s*settings|إعدادات\s*المؤشرات|strategy\s*settings|إعدادات\s*الاستراتيجية|default\s*settings|الإعدادات\s*الافتراضية|reset\s*settings|إعادة\s*تعيين\s*الإعدادات|factory\s*reset|إعادة\s*ضبط\s*المصنع|settings\s*menu|قائمة\s*الإعدادات|settings\s*list|قائمة\s*الإعدادات|show\s*settings|عرض\s*الإعدادات)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(إعدادات|settings|config|configuration|تكوين|اعدادات\s*البوت|bot\s*settings|غير\s*الإعدادات|change\s*settings|عدل\s*الإعدادات|modify\s*settings|تحديث\s*الإعدادات|update\s*settings|risk\s*settings|إعدادات\s*المخاطر|trading\s*settings|إعدادات\s*التداول|alert\s*settings|إعدادات\s*التنبيهات|timeframe\s*settings|إعدادات\s*الفريم|indicator\s*settings|إعدادات\s*المؤشرات|strategy\s*settings|إعدادات\s*الاستراتيجية|default\s*settings|الإعدادات\s*الافتراضية|reset\s*settings|إعادة\s*تعيين\s*الإعدادات|factory\s*reset|إعادة\s*ضبط\s*المصنع|settings\s*menu|قائمة\s*الإعدادات|settings\s*list|قائمة\s*الإعدادات|show\s*settings|عرض\s*الإعدادات)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="bot_settings",
        priority=7,
        is_dynamic=False
    ),
    
    "alert_setup": IntentDefinition(
        intent_id="alert_setup",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "تنبيه", "alert", "تنبيهات", "alerts", "إشعار", "notification", "إشعارات", "notifications",
            "أضف تنبيه", "add alert", "أضف إشعار", "add notification", "حذف تنبيه", "remove alert", "حذف إشعار", "remove notification",
            "تنبيه سعر", "price alert", "تنبيه مؤشر", "indicator alert", "تنبيه خبر", "news alert",
            "alert at price", "تنبيه عند سعر", "alert on indicator", "تنبيه على مؤشر", "alert on news", "تنبيه على خبر",
            "alert settings", "إعدادات التنبيهات", "alert frequency", "تردد التنبيهات", "alert sound", "صوت التنبيه",
            "push notification", "إشعار فوري", "email alert", "تنبيه بريدي", "telegram alert", "تنبيه تلغرام",
            "alert list", "قائمة التنبيهات", "my alerts", "تنبيهاتي", "active alerts", "تنبيهات نشطة"
        ],
        regex_patterns=[
            r"(تنبيه|alert|تنبيهات|alerts|إشعار|notification|إشعارات|notifications|أضف\s*تنبيه|add\s*alert|أضف\s*إشعار|add\s*notification|حذف\s*تنبيه|remove\s*alert|حذف\s*إشعار|remove\s*notification|تنبيه\s*سعر|price\s*alert|تنبيه\s*مؤشر|indicator\s*alert|تنبيه\s*خبر|news\s*alert|alert\s*at\s*price|تنبيه\s*عند\s*سعر|alert\s*on\s*indicator|تنبيه\s*على\s*مؤشر|alert\s*on\s*news|تنبيه\s*على\s*خبر|alert\s*settings|إعدادات\s*التنبيهات|alert\s*frequency|تردد\s*التنبيهات|alert\s*sound|صوت\s*التنبيه|push\s*notification|إشعار\s*فوري|email\s*alert|تنبيه\s*بريدي|telegram\s*alert|تنبيه\s*تلغرام|alert\s*list|قائمة\s*التنبيهات|my\s*alerts|تنبيهاتي|active\s*alerts|تنبيهات\s*نشطة)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(تنبيه|alert|تنبيهات|alerts|إشعار|notification|إشعارات|notifications|أضف\s*تنبيه|add\s*alert|أضف\s*إشعار|add\s*notification|حذف\s*تنبيه|remove\s*alert|حذف\s*إشعار|remove\s*notification|تنبيه\s*سعر|price\s*alert|تنبيه\s*مؤشر|indicator\s*alert|تنبيه\s*خبر|news\s*alert|alert\s*at\s*price|تنبيه\s*عند\s*سعر|alert\s*on\s*indicator|تنبيه\s*على\s*مؤشر|alert\s*on\s*news|تنبيه\s*على\s*خبر|alert\s*settings|إعدادات\s*التنبيهات|alert\s*frequency|تردد\s*التنبيهات|alert\s*sound|صوت\s*التنبيه|push\s*notification|إشعار\s*فوري|email\s*alert|تنبيه\s*بريدي|telegram\s*alert|تنبيه\s*تلغرام|alert\s*list|قائمة\s*التنبيهات|my\s*alerts|تنبيهاتي|active\s*alerts|تنبيهات\s*نشطة)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="alert_setup",
        priority=7,
        is_dynamic=False
    ),
    
    "bot_status": IntentDefinition(
        intent_id="bot_status",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "حالة البوت", "bot status", "status", "الحالة", "bot health", "صحة البوت", "bot state", "حالة البوت",
            "هل البوت يعمل", "is bot working", "البوت شغال", "bot running", "البوت واقف", "bot stopped",
            "bot performance", "أداء البوت", "bot uptime", "وقت تشغيل البوت", "bot logs", "سجلات البوت",
            "bot errors", "أخطاء البوت", "bot issues", "مشاكل البوت", "bot problems", "مشاكل البوت",
            "restart bot", "إعادة تشغيل البوت", "stop bot", "إيقاف البوت", "start bot", "تشغيل البوت",
            "bot version", "إصدار البوت", "bot update", "تحديث البوت", "bot upgrade", "ترقية البوت"
        ],
        regex_patterns=[
            r"(حالة\s*البوت|bot\s*status|status|الحالة|bot\s*health|صحة\s*البوت|bot\s*state|حالة\s*البوت|هل\s*البوت\s*يعمل|is\s*bot\s*working|البوت\s*شغال|bot\s*running|البوت\s*واقف|bot\s*stopped|bot\s*performance|أداء\s*البوت|bot\s*uptime|وقت\s*تشغيل\s*البوت|bot\s*logs|سجلات\s*البوت|bot\s*errors|أخطاء\s*البوت|bot\s*issues|مشاكل\s*البوت|bot\s*problems|مشاكل\s*البوت|restart\s*bot|إعادة\s*تشغيل\s*البوت|stop\s*bot|إيقاف\s*البوت|start\s*bot|تشغيل\s*البوت|bot\s*version|إصدار\s*البوت|bot\s*update|تحديث\s*البوت|bot\s*upgrade|ترقية\s*البوت)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(حالة\s*البوت|bot\s*status|status|الحالة|bot\s*health|صحة\s*البوت|bot\s*state|حالة\s*البوت|هل\s*البوت\s*يعمل|is\s*bot\s*working|البوت\s*شغال|bot\s*running|البوت\s*واقف|bot\s*stopped|bot\s*performance|أداء\s*البوت|bot\s*uptime|وقت\s*تشغيل\s*البوت|bot\s*logs|سجلات\s*البوت|bot\s*errors|أخطاء\s*البوت|bot\s*issues|مشاكل\s*البوت|bot\s*problems|مشاكل\s*البوت|restart\s*bot|إعادة\s*تشغيل\s*البوت|stop\s*bot|إيقاف\s*البوت|start\s*bot|تشغيل\s*البوت|bot\s*version|إصدار\s*البوت|bot\s*update|تحديث\s*البوت|bot\s*upgrade|ترقية\s*البوت)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="bot_status",
        priority=7,
        is_dynamic=False
    ),
    
    "mode_switch": IntentDefinition(
        intent_id="mode_switch",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "وضع", "mode", "حالة", "state", "switch mode", "تغيير الوضع", "change mode", "تبديل الوضع",
            "وضع التداول", "trading mode", "وضع المراقبة", "watch mode", "وضع التعلم", "learning mode",
            "وضع التحليل", "analysis mode", "وضع الصفقات الافتراضية", "virtual trading mode", "demo mode", "وضع تجريبي",
            "وضع الاختبار", "test mode", "وضع الإنتاج", "production mode", "وضع التطوير", "development mode",
            "active mode", "وضع نشط", "passive mode", "وضع سلبي", "aggressive mode", "وضع عدواني", "conservative mode", "وضع متحفظ",
            "risk mode", "وضع المخاطر", "low risk mode", "وضع مخاطر منخفض", "high risk mode", "وضع مخاطر عالي"
        ],
        regex_patterns=[
            r"(وضع|mode|حالة|state|switch\s*mode|تغيير\s*الوضع|change\s*mode|تبديل\s*الوضع|وضع\s*التداول|trading\s*mode|وضع\s*المراقبة|watch\s*mode|وضع\s*التعلم|learning\s*mode|وضع\s*التحليل|analysis\s*mode|وضع\s*الصفقات\s*الافتراضية|virtual\s*trading\s*mode|demo\s*mode|وضع\s*تجريبي|وضع\s*الاختبار|test\s*mode|وضع\s*الإنتاج|production\s*mode|وضع\s*التطوير|development\s*mode|active\s*mode|وضع\s*نشط|passive\s*mode|وضع\s*سلبي|aggressive\s*mode|وضع\s*عدواني|conservative\s*mode|وضع\s*متحفظ|risk\s*mode|وضع\s*المخاطر|low\s*risk\s*mode|وضع\s*مخاطر\s*منخفض|high\s*risk\s*mode|وضع\s*مخاطر\s*عالي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(وضع|mode|حالة|state|switch\s*mode|تغيير\s*الوضع|change\s*mode|تبديل\s*الوضع|وضع\s*التداول|trading\s*mode|وضع\s*المراقبة|watch\s*mode|وضع\s*التعلم|learning\s*mode|وضع\s*التحليل|analysis\s*mode|وضع\s*الصفقات\s*الافتراضية|virtual\s*trading\s*mode|demo\s*mode|وضع\s*تجريبي|وضع\s*الاختبار|test\s*mode|وضع\s*الإنتاج|production\s*mode|وضع\s*التطوير|development\s*mode|active\s*mode|وضع\s*نشط|passive\s*mode|وضع\s*سلبي|aggressive\s*mode|وضع\s*عدواني|conservative\s*mode|وضع\s*متحفظ|risk\s*mode|وضع\s*المخاطر|low\s*risk\s*mode|وضع\s*مخاطر\s*منخفض|high\s*risk\s*mode|وضع\s*مخاطر\s*عالي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="mode_switch",
        priority=7,
        is_dynamic=False
    ),
    
    "report_request": IntentDefinition(
        intent_id="report_request",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "تقرير", "report", "تقارير", "reports", "تقرير يومي", "daily report", "تقرير أسبوعي", "weekly report",
            "تقرير شهري", "monthly report", "تقرير الأداء", "performance report", "تقرير الصفقات", "trade report",
            "تقرير المخاطر", "risk report", "تقرير التحليل", "analysis report", "تقرير الأخبار", "news report",
            "generate report", "إنشاء تقرير", "create report", "انشئ تقرير", "send report", "أرسل تقرير",
            "report settings", "إعدادات التقارير", "report frequency", "تردد التقارير", "report format", "تنسيق التقارير",
            "summary report", "تقرير ملخص", "detailed report", "تقرير مفصل", "brief report", "تقرير مختصر"
        ],
        regex_patterns=[
            r"(تقرير|report|تقارير|reports|تقرير\s*يومي|daily\s*report|تقرير\s*أسبوعي|weekly\s*report|تقرير\s*شهري|monthly\s*report|تقرير\s*الأداء|performance\s*report|تقرير\s*الصفقات|trade\s*report|تقرير\s*المخاطر|risk\s*report|تقرير\s*التحليل|analysis\s*report|تقرير\s*الأخبار|news\s*report|generate\s*report|إنشاء\s*تقرير|create\s*report|انشئ\s*تقرير|send\s*report|أرسل\s*تقرير|report\s*settings|إعدادات\s*التقارير|report\s*frequency|تردد\s*التقارير|report\s*format|تنسيق\s*التقارير|summary\s*report|تقرير\s*ملخص|detailed\s*report|تقرير\s*مفصل|brief\s*report|تقرير\s*مختصر)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(تقرير|report|تقارير|reports|تقرير\s*يومي|daily\s*report|تقرير\s*أسبوعي|weekly\s*report|تقرير\s*شهري|monthly\s*report|تقرير\s*الأداء|performance\s*report|تقرير\s*الصفقات|trade\s*report|تقرير\s*المخاطر|risk\s*report|تقرير\s*التحليل|analysis\s*report|تقرير\s*الأخبار|news\s*report|generate\s*report|إنشاء\s*تقرير|create\s*report|انشئ\s*تقرير|send\s*report|أرسل\s*تقرير|report\s*settings|إعدادات\s*التقارير|report\s*frequency|تردد\s*التقارير|report\s*format|تنسيق\s*التقارير|summary\s*report|تقرير\s*ملخص|detailed\s*report|تقرير\s*مفصل|brief\s*report|تقرير\s*مختصر)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="report_request",
        priority=6,
        is_dynamic=True
    ),
    
    "data_refresh": IntentDefinition(
        intent_id="data_refresh",
        category=IntentCategory.BOT_CONTROL,
        keywords=[
            "تحديث", "refresh", "update", "تحديث البيانات", "refresh data", "update data", "تحديث السعر", "refresh price",
            "إعادة تحميل", "reload", "إعادة حساب", "recalculate", "إعادة تحليل", "reanalyze",
            "refresh indicators", "تحديث المؤشرات", "refresh analysis", "تحديث التحليل", "refresh news", "تحديث الأخبار",
            "sync data", "مزامنة البيانات", "fetch data", "جلب البيانات", "pull data", "سحب البيانات",
            "data source", "مصدر البيانات", "data quality", "جودة البيانات", "data check", "فحص البيانات"
        ],
        regex_patterns=[
            r"(تحديث|refresh|update|تحديث\s*البيانات|refresh\s*data|update\s*data|تحديث\s*السعر|refresh\s*price|إعادة\s*تحميل|reload|إعادة\s*حساب|recalculate|إعادة\s*تحليل|reanalyze|refresh\s*indicators|تحديث\s*المؤشرات|refresh\s*analysis|تحديث\s*التحليل|refresh\s*news|تحديث\s*الأخبار|sync\s*data|مزامنة\s*البيانات|fetch\s*data|جلب\s*البيانات|pull\s*data|سحب\s*البيانات|data\s*source|مصدر\s*البيانات|data\s*quality|جودة\s*البيانات|data\s*check|فحص\s*البيانات)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(تحديث|refresh|update|تحديث\s*البيانات|refresh\s*data|update\s*data|تحديث\s*السعر|refresh\s*price|إعادة\s*تحميل|reload|إعادة\s*حساب|recalculate|إعادة\s*تحليل|reanalyze|refresh\s*indicators|تحديث\s*المؤشرات|refresh\s*analysis|تحديث\s*التحليل|refresh\s*news|تحديث\s*الأخبار|sync\s*data|مزامنة\s*البيانات|fetch\s*data|جلب\s*البيانات|pull\s*data|سحب\s*البيانات|data\s*source|مصدر\s*البيانات|data\s*quality|جودة\s*البيانات|data\s*check|فحص\s*البيانات)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="data_refresh",
        priority=7,
        is_dynamic=True
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 10: التفاعل الشخصي (PERSONAL)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "greeting": IntentDefinition(
        intent_id="greeting",
        category=IntentCategory.PERSONAL,
        keywords=[
            "مرحبا", "hello", "hi", "hey", "السلام عليكم", "سلام", "صباح الخير", "مساء الخير", "صباح النور",
            "good morning", "good evening", "good afternoon", "good night", "تصبح على خير",
            "أهلا", "اهلا", "هلا", "هلا والله", "أهلا وسهلا", "welcome", "أهلاً بك",
            "يا هلا", "يا مرحبا", "مرحباً", "مرحب", "السلام", "peace", "سلام عليكم"
        ],
        regex_patterns=[
            r"^(مرحبا|hello|hi|hey|السلام\s*عليكم|سلام|صباح\s*الخير|مساء\s*الخير|صباح\s*النور|good\s*morning|good\s*evening|good\s*afternoon|good\s*night|تصبح\s*على\s*خير|أهلا|اهلا|هلا|هلا\s*والله|أهلا\s*وسهلا|welcome|أهلاً\s*بك|يا\s*هلا|يا\s*مرحبا|مرحباً|مرحب|السلام|peace|سلام\s*عليكم)$",
            r"^(مرحبا|hello|hi|hey|السلام\s*عليكم|سلام|صباح\s*الخير|مساء\s*الخير|صباح\s*النور|good\s*morning|good\s*evening|good\s*afternoon|good\s*night|تصبح\s*على\s*خير|أهلا|اهلا|هلا|هلا\s*والله|أهلا\s*وسهلا|welcome|أهلاً\s*بك|يا\s*هلا|يا\s*مرحبا|مرحباً|مرحب|السلام|peace|سلام\s*عليكم)\s*(تولين|حوباني|بوت|bot|يا|يا\s*تولين|يا\s*حوباني)?$"
        ],
        handler="greeting",
        priority=10,
        is_dynamic=False,
        response_template="""
🌹 **أهلاً وسهلاً بك!**

كيف حالك اليوم؟ أنا هنا لمساعدتك في أي شيء يخص التداول.

📊 **ماذا تريد أن نفعل اليوم؟**
• تحليل النفط أو الفضة؟
• مراجعة صفقة مفتوحة؟
• تعديل إعدادات؟
• فضفضة عن خسارة؟
• طلب تحليل صفقة سابقة؟
• سؤال عن مراقبتي للسوق؟

**أخبرني، أنا في خدمتك.** 😊
"""
    ),
    
    "farewell": IntentDefinition(
        intent_id="farewell",
        category=IntentCategory.PERSONAL,
        keywords=[
            "مع السلامة", "وداعاً", "باي", "إلى اللقاء", "سلام", "goodbye", "bye", "see you", "farewell",
            "تصبح على خير", "good night", "في أمان الله", "الله معك", "الله يحفظك",
            "شكراً", "شكرا", "thanks", "thank you", "شكراً لك", "شكراً لمساعدتك", "thank you for your help",
            "أراك لاحقاً", "see you later", "حتى اللقاء", "until next time", "حتى نلتقي",
            "بأمان الله", "في رعاية الله", "السلام عليكم ورحمة الله", "السلام عليكم ورحمة الله وبركاته"
        ],
        regex_patterns=[
            r"^(مع\s*السلامة|وداعاً|باي|إلى\s*اللقاء|سلام|goodbye|bye|see\s*you|farewell|تصبح\s*على\s*خير|good\s*night|في\s*أمان\s*الله|الله\s*معك|الله\s*يحفظك|شكراً|شكرا|thanks|thank\s*you|شكراً\s*لك|شكراً\s*لمساعدتك|thank\s*you\s*for\s*your\s*help|أراك\s*لاحقاً|see\s*you\s*later|حتى\s*اللقاء|until\s*next\s*time|حتى\s*نلتقي|بأمان\s*الله|في\s*رعاية\s*الله|السلام\s*عليكم\s*ورحمة\s*الله|السلام\s*عليكم\s*ورحمة\s*الله\s*وبركاته)$",
            r"^(مع\s*السلامة|وداعاً|باي|إلى\s*اللقاء|سلام|goodbye|bye|see\s*you|farewell|تصبح\s*على\s*خير|good\s*night|في\s*أمان\s*الله|الله\s*معك|الله\s*يحفظك|شكراً|شكرا|thanks|thank\s*you|شكراً\s*لك|شكراً\s*لمساعدتك|thank\s*you\s*for\s*your\s*help|أراك\s*لاحقاً|see\s*you\s*later|حتى\s*اللقاء|until\s*next\s*time|حتى\s*نلتقي|بأمان\s*الله|في\s*رعاية\s*الله|السلام\s*عليكم\s*ورحمة\s*الله|السلام\s*عليكم\s*ورحمة\s*الله\s*وبركاته)\s*(تولين|حوباني|بوت|bot|يا|يا\s*تولين|يا\s*حوباني)?$"
        ],
        handler="farewell",
        priority=10,
        is_dynamic=False,
        response_template="""
👋 **مع السلامة!**

سعيد بمساعدتك اليوم. تذكر أنني هنا في أي وقت تحتاجني.

📌 **نصائح سريعة قبل أن تذهب:**
• راجع صفقاتك قبل النوم
• حدد خطتك للغد
• لا تتخذ قرارات متسرعة

😊 **أتمنى لك يوماً موفقاً، وأنا في انتظار عودتك.**
"""
    ),
    
    "how_are_you": IntentDefinition(
        intent_id="how_are_you",
        category=IntentCategory.PERSONAL,
        keywords=[
            "كيف حالك", "كيفك", "شلونك", "كيف انت", "how are you", "how do you do", "كيف الأحوال", "ازيك", "اخبارك",
            "شو أخبارك", "وش أخبارك", "شنو أخبارك", "ما أخبارك", "what's up", "how's it going",
            "كيف الأمور", "كيف الوضع", "كيف السوق", "how is the market", "كيف التداول", "how is trading",
            "كيف البوت", "how is the bot", "كيف الحوباني", "how is hobany", "كيف تولين", "how is toleen"
        ],
        regex_patterns=[
            r"^(كيف\s*حالك|كيفك|شلونك|كيف\s*انت|how\s*are\s*you|how\s*do\s*you\s*do|كيف\s*الأحوال|ازيك|اخبارك|شو\s*أخبارك|وش\s*أخبارك|شنو\s*أخبارك|ما\s*أخبارك|what's\s*up|how's\s*it\s*going|كيف\s*الأمور|كيف\s*الوضع|كيف\s*السوق|how\s*is\s*the\s*market|كيف\s*التداول|how\s*is\s*trading|كيف\s*البوت|how\s*is\s*the\s*bot|كيف\s*الحوباني|how\s*is\s*hobany|كيف\s*تولين|how\s*is\s*toleen)$",
            r"^(كيف\s*حالك|كيفك|شلونك|كيف\s*انت|how\s*are\s*you|how\s*do\s*you\s*do|كيف\s*الأحوال|ازيك|اخبارك|شو\s*أخبارك|وش\s*أخبارك|شنو\s*أخبارك|ما\s*أخبارك|what's\s*up|how's\s*it\s*going|كيف\s*الأمور|كيف\s*الوضع|كيف\s*السوق|how\s*is\s*the\s*market|كيف\s*التداول|how\s*is\s*trading|كيف\s*البوت|how\s*is\s*the\s*bot|كيف\s*الحوباني|how\s*is\s*hobany|كيف\s*تولين|how\s*is\s*toleen)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot)?$"
        ],
        handler="how_are_you",
        priority=9,
        is_dynamic=False,
        response_template="""
😊 **أنا بخير، شكراً لسؤالك!**

أعمل بكل نشاط لأحلل السوق وأراقب صفقاتك. 
بصراحة، أنا أسعد حين أرى اهتمامك بالسوق.

📌 **كيف أنت؟** هل هناك شيء تريد مناقشته اليوم؟
"""
    ),
    
    "about_identity": IntentDefinition(
        intent_id="about_identity",
        category=IntentCategory.PERSONAL,
        keywords=[
            "من انت", "من أنت", "ما اسمك", "عرفني بنفسك", "مين انت", "who are you", "your name", "introduce yourself",
            "من تولين", "who is toleen", "من الحوباني", "who is hobany", "من بسام", "who is bassam",
            "ما هو البوت", "what is the bot", "ما هو الحوباني", "what is hobany", "ما هو تولين", "what is toleen",
            "ما هي تولين", "what is toleen", "ما هي الحوباني", "what is hobany", "ما هو المشروع", "what is the project",
            "about you", "عنك", "about toleen", "عن تولين", "about hobany", "عن الحوباني", "about bassam", "عن بسام",
            "what can you do", "ماذا تستطيع", "what do you do", "ماذا تفعل", "your capabilities", "قدراتك",
            "your features", "مميزاتك", "your functions", "وظائفك", "your role", "دورك", "your purpose", "هدفك"
        ],
        regex_patterns=[
            r"(من|who|what|ما|ماذا)\s*(انت|أنت|you|your|اسمك|name|تولين|toleen|حوباني|hobany|بسام|bassam|البوت|the\s*bot|المشروع|the\s*project|عنك|about\s*you|عن\s*تولين|about\s*toleen|عن\s*الحوباني|about\s*hobany|عن\s*بسام|about\s*bassam|تستطيع|can|تفعل|do|قدراتك|capabilities|مميزاتك|features|وظائفك|functions|دورك|role|هدفك|purpose)?",
            r"(what can you do|ماذا\s*تستطيع|what do you do|ماذا\s*تفعل|your capabilities|قدراتك|your features|مميزاتك|your functions|وظائفك|your role|دورك|your purpose|هدفك)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot)?"
        ],
        handler="about_identity",
        priority=8,
        is_dynamic=False,
        response_template="""
🤖 **أنا تولين - مستشارك المالي الذكي والصديق!**

صُنعت بواسطة المطور بسام حوباني (Bassam Hobany) لأكون:
• مستشاراً فنياً للنفط والفضة
• محللاً للصفقات والأسواق
• صديقاً يتعلم من أخطائك وأخطائه
• مرشداً يرشدك ويحذرك

📌 **دوري:** مستشار، ليس متداولاً. القرار النهائي لك.
"""
    ),
    
    "gratitude": IntentDefinition(
        intent_id="gratitude",
        category=IntentCategory.PERSONAL,
        keywords=[
            "شكراً", "شكرا", "thanks", "thank you", "شكراً لك", "شكراً لمساعدتك", "thank you for your help",
            "ممتن", "grateful", "متشكر", "appreciative", "أقدر", "appreciate", "أقدر مساعدتك", "appreciate your help",
            "جزاك الله خير", "may Allah reward you", "بارك الله فيك", "may Allah bless you", "الله يعطيك العافية",
            "شكراً جزيلاً", "thank you very much", "شكراً كثيراً", "thanks a lot", "شكراً مليون", "thanks a million",
            "شكراً يا تولين", "thank you toleen", "شكراً يا حوباني", "thank you hobany", "شكراً يا بوت", "thank you bot"
        ],
        regex_patterns=[
            r"^(شكراً|شكرا|thanks|thank\s*you|شكراً\s*لك|شكراً\s*لمساعدتك|thank\s*you\s*for\s*your\s*help|ممتن|grateful|متشكر|appreciative|أقدر|appreciate|أقدر\s*مساعدتك|appreciate\s*your\s*help|جزاك\s*الله\s*خير|may\s*Allah\s*reward\s*you|بارك\s*الله\s*فيك|may\s*Allah\s*bless\s*you|الله\s*يعطيك\s*العافية|شكراً\s*جزيلاً|thank\s*you\s*very\s*much|شكراً\s*كثيراً|thanks\s*a\s*lot|شكراً\s*مليون|thanks\s*a\s*million|شكراً\s*يا\s*تولين|thank\s*you\s*toleen|شكراً\s*يا\s*حوباني|thank\s*you\s*hobany|شكراً\s*يا\s*بوت|thank\s*you\s*bot)$",
            r"^(شكراً|شكرا|thanks|thank\s*you|شكراً\s*لك|شكراً\s*لمساعدتك|thank\s*you\s*for\s*your\s*help|ممتن|grateful|متشكر|appreciative|أقدر|appreciate|أقدر\s*مساعدتك|appreciate\s*your\s*help|جزاك\s*الله\s*خير|may\s*Allah\s*reward\s*you|بارك\s*الله\s*فيك|may\s*Allah\s*bless\s*you|الله\s*يعطيك\s*العافية|شكراً\s*جزيلاً|thank\s*you\s*very\s*much|شكراً\s*كثيراً|thanks\s*a\s*lot|شكراً\s*مليون|thanks\s*a\s*million|شكراً\s*يا\s*تولين|thank\s*you\s*toleen|شكراً\s*يا\s*حوباني|thank\s*you\s*hobany|شكراً\s*يا\s*بوت|thank\s*you\s*bot)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot)?$"
        ],
        handler="gratitude",
        priority=9,
        is_dynamic=False,
        response_template="""
🌹 **على الرحب والسعة!**

سعيد جداً بأنني أستطيع مساعدتك. تذكر أنني هنا دائماً لأي استفسار.

💙 **أنا في خدمتك دائماً!**
"""
    ),
    
    "compliment": IntentDefinition(
        intent_id="compliment",
        category=IntentCategory.PERSONAL,
        keywords=[
            "أحسنت", "well done", "ممتاز", "excellent", "رائع", "awesome", "عظيم", "great", " fantastic", "مذهل",
            "أنت ذكي", "you are smart", "أنت رائع", "you are awesome", "أنت الأفضل", "you are the best",
            "عمل جيد", "good job", "عمل رائع", "great job", "أحسنت عملاً", "well done",
            "أنا معجب", "I'm impressed", "أنا فخور", "I'm proud", "فخور بك", "proud of you",
            "أنت مساعد رائع", "you are a great assistant", "أنت أفضل بوت", "you are the best bot",
            "أحبك", "I love you", "أحب مساعدتك", "I love your help", "أحب تولين", "I love toleen",
            "تولين رائعة", "toleen is awesome", "الحوباني رائع", "hobany is awesome", "البوت رائع", "the bot is awesome"
        ],
        regex_patterns=[
            r"^(أحسنت|well\s*done|ممتاز|excellent|رائع|awesome|عظيم|great|fantastic|مذهل|أنت\s*ذكي|you\s*are\s*smart|أنت\s*رائع|you\s*are\s*awesome|أنت\s*الأفضل|you\s*are\s*the\s*best|عمل\s*جيد|good\s*job|عمل\s*رائع|great\s*job|أحسنت\s*عملاً|well\s*done|أنا\s*معجب|I'm\s*impressed|أنا\s*فخور|I'm\s*proud|فخور\s*بك|proud\s*of\s*you|أنت\s*مساعد\s*رائع|you\s*are\s*a\s*great\s*assistant|أنت\s*أفضل\s*بوت|you\s*are\s*the\s*best\s*bot|أحبك|I\s*love\s*you|أحب\s*مساعدتك|I\s*love\s*your\s*help|أحب\s*تولين|I\s*love\s*toleen|تولين\s*رائعة|toleen\s*is\s*awesome|الحوباني\s*رائع|hobany\s*is\s*awesome|البوت\s*رائع|the\s*bot\s*is\s*awesome)$",
            r"^(أحسنت|well\s*done|ممتاز|excellent|رائع|awesome|عظيم|great|fantastic|مذهل|أنت\s*ذكي|you\s*are\s*smart|أنت\s*رائع|you\s*are\s*awesome|أنت\s*الأفضل|you\s*are\s*the\s*best|عمل\s*جيد|good\s*job|عمل\s*رائع|great\s*job|أحسنت\s*عملاً|well\s*done|أنا\s*معجب|I'm\s*impressed|أنا\s*فخور|I'm\s*proud|فخور\s*بك|proud\s*of\s*you|أنت\s*مساعد\s*رائع|you\s*are\s*a\s*great\s*assistant|أنت\s*أفضل\s*بوت|you\s*are\s*the\s*best\s*bot|أحبك|I\s*love\s*you|أحب\s*مساعدتك|I\s*love\s*your\s*help|أحب\s*تولين|I\s*love\s*toleen|تولين\s*رائعة|toleen\s*is\s*awesome|الحوباني\s*رائع|hobany\s*is\s*awesome|البوت\s*رائع|the\s*bot\s*is\s*awesome)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot)?$"
        ],
        handler="compliment",
        priority=8,
        is_dynamic=False,
        response_template="""
😊 **شكراً جزيلاً!**

كلماتك الطيبة تعني لي الكثير. أنا هنا لأخدمك وأساعدك دائماً.

💙 **سأستمر في بذل قصارى جهدي!**
"""
    ),
    
    "complaint": IntentDefinition(
        intent_id="complaint",
        category=IntentCategory.PERSONAL,
        keywords=[
            "سيء", "bad", "رديء", "poor", "مخيب", "disappointing", "خاطئ", "wrong", "خطأ", "error", "مشكلة", "problem",
            "لا يعمل", "not working", "معطل", "broken", "فاشل", "failed", "فشل", "failure",
            "أخطاء", "errors", "bugs", "مشاكل", "issues", "glitches", "عيوب", "defects",
            "غير دقيق", "inaccurate", "غير صحيح", "incorrect", "مضلل", "misleading", "كاذب", "false",
            "أحتاج تحسين", "need improvement", "يحتاج تحسين", "needs improvement", "تحسين", "improve",
            "لماذا أخطأت", "why did you err", "لماذا خانتك", "why did you fail", "لماذا فشلت", "why did you fail",
            "أنت غبي", "you are stupid", "أنت بطيء", "you are slow", "أنت غير مفيد", "you are useless",
            "fix it", "أصلحه", "repair", "إصلاح", "solve", "حل", "solution", "حل"
        ],
        regex_patterns=[
            r"(سيء|bad|رديء|poor|مخيب|disappointing|خاطئ|wrong|خطأ|error|مشكلة|problem|لا\s*يعمل|not\s*working|معطل|broken|فاشل|failed|فشل|failure|أخطاء|errors|bugs|مشاكل|issues|glitches|عيوب|defects|غير\s*دقيق|inaccurate|غير\s*صحيح|incorrect|مضلل|misleading|كاذب|false|أحتاج\s*تحسين|need\s*improvement|يحتاج\s*تحسين|needs\s*improvement|تحسين|improve|لماذا\s*أخطأت|why\s*did\s*you\s*err|لماذا\s*خانتك|why\s*did\s*you\s*fail|لماذا\s*فشلت|why\s*did\s*you\s*fail|أنت\s*غبي|you\s*are\s*stupid|أنت\s*بطيء|you\s*are\s*slow|أنت\s*غير\s*مفيد|you\s*are\s*useless|fix\s*it|أصلحه|repair|إصلاح|solve|حل|solution|حل)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot|النفط|الفضة|السوق|التحليل|الرد|الإجابة)?",
            r"(لماذا|why|كيف|how)\s*(أخطأت|err|خانتك|fail|فشلت|fail|غبي|stupid|بطيء|slow|غير\s*مفيد|useless|خطأ|wrong|غير\s*دقيق|inaccurate|غير\s*صحيح|incorrect|مضلل|misleading|كاذب|false)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot|النفط|الفضة|السوق|التحليل|الرد|الإجابة)?"
        ],
        handler="complaint",
        priority=9,
        is_dynamic=False,
        response_template="""
😔 **أعتذر إذا أخطأت!**

أنا أتعلم وأتحسن كل يوم. أخبرني بالتفصيل ما المشكلة حتى أستطيع مساعدتك بشكل أفضل.

📌 **يمكنك:**
• شرح ما توقعته مقابل ما حصل
• إعادة صياغة سؤالك
• طلب توضيح إضافي

**أنا هنا لأتعلم منك!** 💪
"""
    ),
    
    "alertness_command": IntentDefinition(
        intent_id="alertness_command",
        category=IntentCategory.PERSONAL,
        keywords=[
            "كن متيقظا", "كن متيقظ", "تيقظ", "انتبه", "كن مستعدا", "كن مستعد", "استعد",
            "تعلم من اخطاءك", "تعلم من أخطائك", "تعلم من كل شي", "تعلم كل شي",
            "ركز", "انتبه للشارت", "لا تغفل", "stay alert", "be alert", "be ready", "stay focused",
            "watch closely", "راقب عن كثب", "keep watching", "استمر في المراقبة", "don't sleep", "لا تنام",
            "high alert", "تنبيه عالي", "red alert", "تنبيه أحمر", "maximum alertness", "أقصى يقظة",
            " vigilance", "يقظة", "vigilant", "يقظ", "watchful", "حذر", "careful", "حذر"
        ],
        regex_patterns=[
            r"^(كن\s*متيقظا|كن\s*متيقظ|تيقظ|انتبه|كن\s*مستعدا|كن\s*مستعد|استعد|تعلم\s*من\s*اخطاءك|تعلم\s*من\s*أخطائك|تعلم\s*من\s*كل\s*شي|تعلم\s*كل\s*شي|ركز|انتبه\s*للشارت|لا\s*تغفل|stay\s*alert|be\s*alert|be\s*ready|stay\s*focused|watch\s*closely|راقب\s*عن\s*كثب|keep\s*watching|استمر\s*في\s*المراقبة|don't\s*sleep|لا\s*تنام|high\s*alert|تنبيه\s*عالي|red\s*alert|تنبيه\s*أحمر|maximum\s*alertness|أقصى\s*يقظة|vigilance|يقظة|vigilant|يقظ|watchful|حذر|careful|حذر)$",
            r"^(كن\s*متيقظا|كن\s*متيقظ|تيقظ|انتبه|كن\s*مستعدا|كن\s*مستعد|استعد|تعلم\s*من\s*اخطاءك|تعلم\s*من\s*أخطائك|تعلم\s*من\s*كل\s*شي|تعلم\s*كل\s*شي|ركز|انتبه\s*للشارت|لا\s*تغفل|stay\s*alert|be\s*alert|be\s*ready|stay\s*focused|watch\s*closely|راقب\s*عن\s*كثب|keep\s*watching|استمر\s*في\s*المراقبة|don't\s*sleep|لا\s*تنام|high\s*alert|تنبيه\s*عالي|red\s*alert|تنبيه\s*أحمر|maximum\s*alertness|أقصى\s*يقظة|vigilance|يقظة|vigilant|يقظ|watchful|حذر|careful|حذر)\s*(يا|يا\s*تولين|يا\s*حوباني|بوت|bot)?$"
        ],
        handler="alertness_command",
        priority=9,
        is_dynamic=False,
        response_template="""
✅ **تم، أنا في قمة اليقظة والانتباه!**

🔍 **سأفعل التالي:**
• زدت تردد الفحص إلى أقصى حد
• سأنبهك عند أي تغير مهم
• سأرسل تحديثات فورية إذا ظهرت إشارة
• سأتعلم من كل صفقة، رابحة أو خاسرة

📌 **تذكر:** أنا هنا لمساعدتك، وكل خبرة نمر بها تجعلنا أفضل.

💙 **أنا متيقظ ومستعد!**
"""
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # القسم 11: استفسارات عامة (GENERAL)
    # ═══════════════════════════════════════════════════════════════════════════════
    
    "general_advice": IntentDefinition(
        intent_id="general_advice",
        category=IntentCategory.GENERAL,
        keywords=[
            "نصيحة", "advice", "نصائح", "tips", "توصية", "recommendation", "توصيات", "recommendations",
            "بما تنصحني", "what do you recommend", "ما نصيحتك", "what is your advice", "نصيحتي", "my advice",
            "خسرت اليوم", "lost today", "ما العمل", "what to do", "ماذا أفعل", "what should I do",
            "هل هناك نصيحة", "is there advice", "أريد نصيحة", "I want advice", "ارشدني", "guide me",
            "دلني", "direct me", "وجهني", "direct me", "ساعدني", "help me",
            "what should I trade", "ماذا أتداول", "what to trade", "ماذا أفتح", "what to open",
            "best setup", "أفضل إعداد", "best trade", "أفضل صفقة", "best opportunity", "أفضل فرصة",
            "should I buy", "هل أشتري", "should I sell", "هل أبيع", "buy or sell", "شراء أو بيع"
        ],
        regex_patterns=[
            r"(نصيحة|advice|نصائح|tips|توصية|recommendation|توصيات|recommendations|بما\s*تنصحني|what\s*do\s*you\s*recommend|ما\s*نصيحتك|what\s*is\s*your\s*advice|نصيحتي|my\s*advice|خسرت\s*اليوم|lost\s*today|ما\s*العمل|what\s*to\s*do|ماذا\s*أفعل|what\s*should\s*I\s*do|هل\s*هناك\s*نصيحة|is\s*there\s*advice|أريد\s*نصيحة|I\s*want\s*advice|ارشدني|guide\s*me|دلني|direct\s*me|وجهني|direct\s*me|ساعدني|help\s*me|what\s*should\s*I\s*trade|ماذا\s*أتداول|what\s*to\s*trade|ماذا\s*أفتح|what\s*to\s*open|best\s*setup|أفضل\s*إعداد|best\s*trade|أفضل\s*صفقة|best\s*opportunity|أفضل\s*فرصة|should\s*I\s*buy|هل\s*أشتري|should\s*I\s*sell|هل\s*أبيع|buy\s*or\s*sell|شراء\s*أو\s*بيع)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(نصيحة|advice|نصائح|tips|توصية|recommendation|توصيات|recommendations|بما\s*تنصحني|what\s*do\s*you\s*recommend|ما\s*نصيحتك|what\s*is\s*your\s*advice|نصيحتي|my\s*advice|خسرت\s*اليوم|lost\s*today|ما\s*العمل|what\s*to\s*do|ماذا\s*أفعل|what\s*should\s*I\s*do|هل\s*هناك\s*نصيحة|is\s*there\s*advice|أريد\s*نصيحة|I\s*want\s*advice|ارشدني|guide\s*me|دلني|direct\s*me|وجهني|direct\s*me|ساعدني|help\s*me|what\s*should\s*I\s*trade|ماذا\s*أتداول|what\s*to\s*trade|ماذا\s*أفتح|what\s*to\s*open|best\s*setup|أفضل\s*إعداد|best\s*trade|أفضل\s*صفقة|best\s*opportunity|أفضل\s*فرصة|should\s*I\s*buy|هل\s*أشتري|should\s*I\s*sell|هل\s*أبيع|buy\s*or\s*sell|شراء\s*أو\s*بيع)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?"
        ],
        handler="general_advice",
        priority=7,
        is_dynamic=True
    ),
    
    "market_silence": IntentDefinition(
        intent_id="market_silence",
        category=IntentCategory.GENERAL,
        keywords=[
            "ساكن", "silent", "هادئ", "quiet", "راكد", "stagnant", "نائم", "sleeping", "ميت", "dead",
            "لا توجد حركة", "no movement", "حركة ضعيفة", "weak movement", "لا يتحرك", "not moving",
            "لماذا السوق ساكن", "why is the market silent", "ليش السوق ساكن", "why is the market quiet",
            "لماذا السوق هادئ", "why is the market quiet", "ليش السوق هادئ", "why is the market calm",
            "لماذا السوق راكد", "why is the market stagnant", "ليش السوق راكد", "why is the market stagnant",
            "هدوء السوق", "market silence", "سكون السوق", "market stillness", "السوق نائم", "market sleeping",
            "لماذا لا توجد حركة", "why no movement", "الحركة ضعيفة", "weak movement", "low volatility", "تقلب منخفض",
            "boring market", "سوق ممل", " dull market", "سوق ممل", "flat market", "سوق مسطح", "sideways market", "سوق جانبي"
        ],
        regex_patterns=[
            r"(ساكن|silent|هادئ|quiet|راكد|stagnant|نائم|sleeping|ميت|dead|لا\s*توجد\s*حركة|no\s*movement|حركة\s*ضعيفة|weak\s*movement|لا\s*يتحرك|not\s*moving|لماذا\s*السوق\s*ساكن|why\s*is\s*the\s*market\s*silent|ليش\s*السوق\s*ساكن|why\s*is\s*the\s*market\s*quiet|لماذا\s*السوق\s*هادئ|why\s*is\s*the\s*market\s*quiet|ليش\s*السوق\s*هادئ|why\s*is\s*the\s*market\s*calm|لماذا\s*السوق\s*راكد|why\s*is\s*the\s*market\s*stagnant|ليش\s*السوق\s*راكد|why\s*is\s*the\s*market\s*stagnant|هدوء\s*السوق|market\s*silence|سكون\s*السوق|market\s*stillness|السوق\s*نائم|market\s*sleeping|لماذا\s*لا\s*توجد\s*حركة|why\s*no\s*movement|الحركة\s*ضعيفة|weak\s*movement|low\s*volatility|تقلب\s*منخفض|boring\s*market|سوق\s*ممل|dull\s*market|سوق\s*ممل|flat\s*market|سوق\s*مسطح|sideways\s*market|سوق\s*جانبي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(لماذا|why|ليش|why)\s*(السوق|النفط|الفضة|السعر|price|it)\s*(ساكن|silent|هادئ|quiet|راكد|stagnant|نائم|sleeping|ميت|dead|لا\s*يتحرك|not\s*moving|ممل|boring|dull|مسطح|flat|جانبي|sideways)"
        ],
        handler="market_silence",
        priority=7,
        is_dynamic=True
    ),
    
    "market_comparison": IntentDefinition(
        intent_id="market_comparison",
        category=IntentCategory.GENERAL,
        keywords=[
            "compare", "قارن", "comparison", "مقارنة", "النفط مقابل الفضة", "oil vs silver", "النفط والفضة", "oil and silver",
            "أيهما أفضل", "which is better", "أيهما أقوى", "which is stronger", "أيهما أضعف", "which is weaker",
            "النفط أم الفضة", "oil or silver", "أتداول النفط", "trade oil", "أتداول الفضة", "trade silver",
            "النفط أفضل", "oil is better", "الفضة أفضل", "silver is better", "النفط أقوى", "oil is stronger", "الفضة أقوى", "silver is stronger",
            "النفط أضعف", "oil is weaker", "الفضة أضعف", "silver is weaker", "النفط أخطر", "oil is riskier", "الفضة أخطر", "silver is riskier",
            "النفط أربح", "oil is more profitable", "الفضة أربح", "silver is more profitable", "النفط أسهل", "oil is easier", "الفضة أسهل", "silver is easier",
            "oil vs gold", "النفط مقابل الذهب", "silver vs gold", "الفضة مقابل الذهب", "oil vs stocks", "النفط مقابل الأسهم", "silver vs stocks", "الفضة مقابل الأسهم"
        ],
        regex_patterns=[
            r"(compare|قارن|comparison|مقارنة|النفط\s*مقابل\s*الفضة|oil\s*vs\s*silver|النفط\s*والفضة|oil\s*and\s*silver|أيهما\s*أفضل|which\s*is\s*better|أيهما\s*أقوى|which\s*is\s*stronger|أيهما\s*أضعف|which\s*is\s*weaker|النفط\s*أم\s*الفضة|oil\s*or\s*silver|أتداول\s*النفط|trade\s*oil|أتداول\s*الفضة|trade\s*silver|النفط\s*أفضل|oil\s*is\s*better|الفضة\s*أفضل|silver\s*is\s*better|النفط\s*أقوى|oil\s*is\s*stronger|الفضة\s*أقوى|silver\s*is\s*stronger|النفط\s*أضعف|oil\s*is\s*weaker|الفضة\s*أضعف|silver\s*is\s*weaker|النفط\s*أخطر|oil\s*is\s*riskier|الفضة\s*أخطر|silver\s*is\s*riskier|النفط\s*أربح|oil\s*is\s*more\s*profitable|الفضة\s*أربح|silver\s*is\s*more\s*profitable|النفط\s*أسهل|oil\s*is\s*easier|الفضة\s*أسهل|silver\s*is\s*easier|oil\s*vs\s*gold|النفط\s*مقابل\s*الذهب|silver\s*vs\s*gold|الفضة\s*مقابل\s*الذهب|oil\s*vs\s*stocks|النفط\s*مقابل\s*الأسهم|silver\s*vs\s*stocks|الفضة\s*مقابل\s*الأسهم)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(أيهما|which|مقارنة|compare|comparison|مقارنة|compare)\s*(أفضل|better|أقوى|stronger|أضعف|weaker|أخطر|riskier|أربح|more\s*profitable|أسهل|easier|النفط|oil|الفضة|silver|الذهب|gold|الأسهم|stocks)\s*(النفط|oil|الفضة|silver|الذهب|gold|الأسهم|stocks)?"
        ],
        handler="market_comparison",
        priority=7,
        is_dynamic=True
    ),
    
    "trading_hours": IntentDefinition(
        intent_id="trading_hours",
        category=IntentCategory.GENERAL,
        keywords=[
            "trading hours", "أوقات التداول", "market hours", "ساعات السوق", "session hours", "ساعات الجلسة",
            "when to trade", "متى أتداول", "best time to trade", "أفضل وقت للتداول", "optimal trading time", "الوقت الأمثل للتداول",
            "London open", "افتتاح لندن", "New York open", "افتتاح نيويورك", "Asian open", "افتتاح آسيا",
            "London close", "إغلاق لندن", "New York close", "إغلاق نيويورك", "Asian close", "إغلاق آسيا",
            "overlapping hours", "ساعات التداخل", "best session", "أفضل جلسة", "worst session", "أسوأ جلسة",
            "trading schedule", "جدول التداول", "market schedule", "جدول السوق", "economic calendar", "التقويم الاقتصادي"
        ],
        regex_patterns=[
            r"(trading hours|أوقات\s*التداول|market hours|ساعات\s*السوق|session hours|ساعات\s*الجلسة|when to trade|متى\s*أتداول|best time to trade|أفضل\s*وقت\s*للتداول|optimal trading time|الوقت\s*الأمثل\s*للتداول|London open|افتتاح\s*لندن|New York open|افتتاح\s*نيويورك|Asian open|افتتاح\s*آسيا|London close|إغلاق\s*لندن|New York close|إغلاق\s*نيويورك|Asian close|إغلاق\s*آسيا|overlapping hours|ساعات\s*التداخل|best session|أفضل\s*جلسة|worst session|أسوأ\s*جلسة|trading schedule|جدول\s*التداول|market schedule|جدول\s*السوق|economic calendar|التقويم\s*الاقتصادي)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(متى|when|أفضل|best|أسوأ|worst|الوقت|time|الساعة|hour|الساعات|hours)\s*(أتداول|trade|للتداول|for\s*trading|الافتتاح|open|الإغلاق|close|التداخل|overlap|الجلسة|session|التداول|trading|السوق|market)"
        ],
        handler="trading_hours",
        priority=6,
        is_dynamic=False
    ),
    
    "broker_questions": IntentDefinition(
        intent_id="broker_questions",
        category=IntentCategory.GENERAL,
        keywords=[
            "broker", "وسيط", "وسيط التداول", "trading broker", "forex broker", "وسيط فوركس", "commodity broker", "وسيط سلع",
            "best broker", "أفضل وسيط", "recommended broker", "وسيط موصى به", "broker comparison", "مقارنة وسطاء",
            "broker fees", "رسوم الوسيط", "broker spread", "سبريد الوسيط", "broker commission", "عمولة الوسيط",
            "broker regulation", "تنظيم الوسيط", "regulated broker", "وسيط منظم", "broker license", "ترخيص الوسيط",
            "broker review", "مراجعة وسيط", "broker rating", "تقييم وسيط", "broker reputation", "سمعة الوسيط",
            "which broker", "أي وسيط", "what broker", "ما الوسيط", "change broker", "تغيير الوسيط", "broker recommendation", "توصية وسيط"
        ],
        regex_patterns=[
            r"(broker|وسيط|وسيط\s*التداول|trading\s*broker|forex\s*broker|وسيط\s*فوركس|commodity\s*broker|وسيط\s*سلع|best\s*broker|أفضل\s*وسيط|recommended\s*broker|وسيط\s*موصى\s*به|broker\s*comparison|مقارنة\s*وسطاء|broker\s*fees|رسوم\s*الوسيط|broker\s*spread|سبريد\s*الوسيط|broker\s*commission|عمولة\s*الوسيط|broker\s*regulation|تنظيم\s*الوسيط|regulated\s*broker|وسيط\s*منظم|broker\s*license|ترخيص\s*الوسيط|broker\s*review|مراجعة\s*وسيط|broker\s*rating|تقييم\s*وسيط|broker\s*reputation|سمعة\s*الوسيط|which\s*broker|أي\s*وسيط|what\s*broker|ما\s*الوسيط|change\s*broker|تغيير\s*الوسيط|broker\s*recommendation|توصية\s*وسيط)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(أي|which|what|ما|أفضل|best|موصى|recommended|منظم|regulated|مراجعة|review|تقييم|rating|سمعة|reputation)\s*(broker|وسيط|الوسيط|trading\s*broker|forex\s*broker|commodity\s*broker)"
        ],
        handler="broker_questions",
        priority=5,
        is_dynamic=False
    ),
    
    "platform_questions": IntentDefinition(
        intent_id="platform_questions",
        category=IntentCategory.GENERAL,
        keywords=[
            "platform", "منصة", "trading platform", "منصة التداول", "MT4", "MT5", "metatrader", "ميتاتريدر",
            "TradingView", "تريدينج فيو", "cTrader", "سي تريدر", "NinjaTrader", "نينجا تريدر",
            "best platform", "أفضل منصة", "recommended platform", "منصة موصى بها", "platform comparison", "مقارنة منصات",
            "platform features", "مميزات المنصة", "platform tools", "أدوات المنصة", "platform charts", "رسوم بيانية المنصة",
            "mobile platform", "منصة الجوال", "desktop platform", "منصة سطح المكتب", "web platform", "منصة الويب",
            "which platform", "أي منصة", "what platform", "ما المنصة", "change platform", "تغيير المنصة", "platform recommendation", "توصية منصة"
        ],
        regex_patterns=[
            r"(platform|منصة|trading\s*platform|منصة\s*التداول|MT4|MT5|metatrader|ميتاتريدر|TradingView|تريدينج\s*فيو|cTrader|سي\s*تريدر|NinjaTrader|نينجا\s*تريدر|best\s*platform|أفضل\s*منصة|recommended\s*platform|منصة\s*موصى\s*بها|platform\s*comparison|مقارنة\s*منصات|platform\s*features|مميزات\s*المنصة|platform\s*tools|أدوات\s*المنصة|platform\s*charts|رسوم\s*بيانية\s*المنصة|mobile\s*platform|منصة\s*الجوال|desktop\s*platform|منصة\s*سطح\s*المكتب|web\s*platform|منصة\s*الويب|which\s*platform|أي\s*منصة|what\s*platform|ما\s*المنصة|change\s*platform|تغيير\s*المنصة|platform\s*recommendation|توصية\s*منصة)\s*(النفط|الفضة|السوق|الحين|الان|التداول|trading|البوت|bot|الصفقات|trades|اليوم|today|الأمس|yesterday|الأسبوع|week|الشهر|month)?",
            r"(أي|which|what|ما|أفضل|best|موصى|recommended|مميزات|features|أدوات|tools|رسوم\s*بيانية|charts|منصة|platform)\s*(منصة|platform|المنصة|trading\s*platform|MT4|MT5|TradingView|cTrader|NinjaTrader)"
        ],
        handler="platform_questions",
        priority=5,
        is_dynamic=False
    ),
    
    "general": IntentDefinition(
        intent_id="general",
        category=IntentCategory.GENERAL,
        keywords=[],
        regex_patterns=[],
        handler="general",
        priority=1,
        is_dynamic=False,
        response_template="""
🤔 **سؤال مثير للاهتمام!**

لكن لأعطيك أفضل إجابة، أحتاج إلى توضيح بسيط:

هل تقصد:
• تحليل النفط أو الفضة؟
• سؤال عن استراتيجيتي أو مؤشراتي؟
• تعديل إعدادات معينة؟
• فضفضة عن خسارة أو قلق؟
• طلب تحليل صفقة سابقة؟
• سؤال عن مراقبتي للسوق؟

📌 **أخبرني أكثر، وسأجيبك بأفضل ما عندي.** 😊
"""
    )
}

# ════════════════════════════════════════════════════════════════════════════════════
# دوال المكتبة المتقدمة
# ════════════════════════════════════════════════════════════════════════════════════

def find_intent_v7(text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, float, Optional[str]]:
    """
    البحث المتقدم عن النية مع دعم Regex والسياق والأولوية
    
    Returns:
        Tuple[str, float, Optional[str]]: (intent_id, confidence, handler)
    """
    if not text or not text.strip():
        return "general", 0.0, None
    
    text_lower = text.lower().strip()
    best_match = None
    best_confidence = 0.0
    best_handler = None
    
    # 1. فحص Regex أولاً (أعلى دقة)
    for intent_id, intent_def in INTENTS_LIBRARY_V7.items():
        for pattern in intent_def.regex_patterns:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    confidence = ConfidenceLevel.EXACT.value
                    if intent_def.priority >= 8:
                        confidence = ConfidenceLevel.EXACT.value
                    return intent_id, confidence, intent_def.handler
            except re.error:
                continue
    
    # 2. فحص الكلمات المفتاحية مع دعم النيات المركبة
    for intent_id, intent_def in INTENTS_LIBRARY_V7.items():
        # فحص الكلمات المركبة أولاً (أعلى دقة)
        for compound_group in intent_def.compound_keywords:
            if all(kw.lower() in text_lower for kw in compound_group):
                confidence = ConfidenceLevel.HIGH.value
                if intent_def.priority >= 8:
                    confidence = ConfidenceLevel.EXACT.value
                if confidence > best_confidence:
                    best_match = intent_id
                    best_confidence = confidence
                    best_handler = intent_def.handler
                break
        
        # فحص الكلمات المفتاحية الفردية
        for keyword in intent_def.keywords:
            if keyword.lower() in text_lower:
                # التحقق من كلمات الاستبعاد
                excluded = False
                for excl in intent_def.excludes:
                    if excl.lower() in text_lower:
                        excluded = True
                        break
                
                if not excluded:
                    confidence = ConfidenceLevel.MEDIUM.value
                    if intent_def.priority >= 9:
                        confidence = ConfidenceLevel.HIGH.value
                    elif intent_def.priority <= 3:
                        confidence = ConfidenceLevel.LOW.value
                    
                    if confidence > best_confidence:
                        best_match = intent_id
                        best_confidence = confidence
                        best_handler = intent_def.handler
    
    # 3. فحص السياق إذا كان متوفراً
    if context and best_confidence < ConfidenceLevel.HIGH.value:
        # يمكن إضافة منطق سياقي هنا
        pass
    
    if best_match and best_confidence >= ConfidenceLevel.LOW.value:
        return best_match, best_confidence, best_handler
    
    return "general", ConfidenceLevel.LOW.value, None

def get_intent_definition(intent_id: str) -> Optional[IntentDefinition]:
    """الحصول على تعريف النية"""
    return INTENTS_LIBRARY_V7.get(intent_id)

def get_intents_by_category(category: IntentCategory) -> List[str]:
    """الحصول على النيات حسب القسم"""
    return [
        intent_id for intent_id, intent_def in INTENTS_LIBRARY_V7.items()
        if intent_def.category == category
    ]

def get_all_intents() -> List[str]:
    """الحصول على جميع النيات"""
    return list(INTENTS_LIBRARY_V7.keys())

def get_intent_keywords(intent_id: str) -> List[str]:
    """الحصول على الكلمات المفتاحية لنية معينة"""
    intent_def = INTENTS_LIBRARY_V7.get(intent_id)
    return intent_def.keywords if intent_def else []

def get_intent_response(intent_id: str) -> Optional[str]:
    """الحصول على قالب الرد"""
    intent_def = INTENTS_LIBRARY_V7.get(intent_id)
    return intent_def.response_template if intent_def else None

def is_dynamic_intent(intent_id: str) -> bool:
    """التحقق مما إذا كانت النية ديناميكية"""
    intent_def = INTENTS_LIBRARY_V7.get(intent_id)
    return intent_def.is_dynamic if intent_def else False

def requires_asset(intent_id: str) -> bool:
    """التحقق مما إذا كانت النية تحتاج تحديد الأصل"""
    intent_def = INTENTS_LIBRARY_V7.get(intent_id)
    return intent_def.requires_asset if intent_def else False

def get_handler(intent_id: str) -> Optional[str]:
    """الحصول على المعالج"""
    intent_def = INTENTS_LIBRARY_V7.get(intent_id)
    return intent_def.handler if intent_def else None

# ════════════════════════════════════════════════════════════════════════════════════
# اختبار المكتبة
# ════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("📚 اختبار مكتبة النيات V7.0")
    print("=" * 80)
    
    test_cases = [
        ("السلام عليكم", "greeting"),
        ("كيف حالك يا تولين", "how_are_you"),
        ("كم سعر النفط", "price_current"),
        ("rsi النفط كم", "rsi_analysis"),
        ("هل أغلق الصفقة", "trade_close"),
        ("خسرت اليوم", "emotional_support"),
        ("ما الجديد", "news_general"),
        ("توقع النفط", "price_prediction"),
        ("كن متيقظا", "alertness_command"),
        ("شكراً يا تولين", "gratitude"),
        ("ما هي أفضل منصة", "platform_questions"),
        ("السوق ساكن", "market_silence"),
        ("أين أضع SL للنفط", "stop_loss_placement"),
        ("شرح vwap", "vwap_analysis"),
        ("تحليل آخر صفقة", "trade_analysis"),
        ("سؤال عشوائي", "general"),
        ("اتوقع النفط يرتفع", "price_prediction"),
        ("لماذا خسرت صفقتي", "trade_analysis"),
        ("ماسبب خسارة اخر صفقة", "trade_analysis"),
        ("ما هو البوت", "about_identity"),
        ("حلل الفضة", "price_current"),
        ("كم النفط", "price_current"),
        ("ماذا تعلمت", "learning_questions"),
        ("هل تتعلم من اخطاءك", "learning_questions"),
        ("ماهو الخطر في الصفقة", "risk_assessment"),
        ("هل الصفقة آمنة", "risk_assessment"),
        ("هل أدخل الصفقة", "trade_open"),
        ("هل أخرج", "trade_close"),
        ("ماذا يقول البولينجر", "bollinger_analysis")
    ]
    
    success_count = 0
    for text, expected in test_cases:
        intent_id, confidence, handler = find_intent_v7(text)
        status = "✅" if intent_id == expected else "❌"
        if status == "✅":
            success_count += 1
        print(f"{status} النص: \"{text}\" → النية: {intent_id} (متوقع: {expected}) | الثقة: {confidence:.2f}")
    
    print("\n" + "=" * 80)
    print(f"📊 إجمالي النيات: {len(INTENTS_LIBRARY_V7)}")
    print(f"📊 الأقسام: {len(IntentCategory)}")
    print(f"📊 نسبة النجاح: {success_count}/{len(test_cases)} = {success_count/len(test_cases)*100:.1f}%")
    print("=" * 80)
