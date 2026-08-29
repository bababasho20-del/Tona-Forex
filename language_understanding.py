"""
🗣️ الفهم اللغوي - Language Understanding Module
🤖 تولين: فهم اللغة العربية والإنجليزية في سياق التداول
"""

import re
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger("TonaPrometheus")

class LanguageUnderstanding:
    """
    فهم اللغة العربية والإنجليزية في سياق التداول
    
    يقوم بتحليل النصوص واستخراج المعلومات المهمة مثل:
    - الأرقام والأسعار
    - نية الإشارة (شراء/بيع/انتظار)
    - مستوى المخاطرة
    - المشاعر
    - مستويات الأسعار
    """
    
    # =================================================================
    # أنماط الأرقام
    # =================================================================
    
    NUMBER_PATTERNS = [
        r'\d+\.?\d*',  # أرقام إنجليزية
        r'[٠١٢٣٤٥٦٧٨٩]+\.?[٠١٢٣٤٥٦٧٨٩]*'  # أرقام عربية
    ]
    
    PRICE_PATTERNS = [
        r'(?:سعر|price|بسعر|≈|~)\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:دولار|\$|usd|ريال)',
        r'at\s*\$?\s*(\d+\.?\d*)',
    ]
    
    # =================================================================
    # قوائم الكلمات المفتاحية
    # =================================================================
    
    SIGNAL_WORDS = {
        "buy": [
            "شراء", "اشتري", "buy", "long", "شرا", "ادخل شراء",
            "صاعد", "ارتفاع", "up", "bullish", "طويل"
        ],
        "sell": [
            "بيع", "ابيع", "sell", "short", "شورت", "ادخل بيع",
            "هابط", "انخفاض", "down", "bearish", "قصير"
        ],
        "wait": [
            "انتظر", "wait", "hold", "تجنب", "لا تدخل",
            "صبر", "تمهل", "ترقب", "مشاهدة"
        ]
    }
    
    RISK_WORDS = {
        "high": [
            "خطر", "خطير", "high risk", "dangerous", "محفوف",
            "مخاطرة عالية", "تقلب", "volatile", "غير مستقر"
        ],
        "low": [
            "آمن", "safe", "low risk", "محمي", "حذر",
            "مستقر", "stable", "مضمون", "محافظ"
        ],
        "moderate": [
            "متوسط", "moderate", "reasonable", "معتدل",
            "مقبول", "طبيعي", "normal", "متوازن"
        ]
    }
    
    EMOTION_WORDS = {
        "fear": [
            "خايف", "أخاف", "قلق", "متردد", "حذر", "خوف",
            "خائف", "قلقان", "مذعور", "مرعوب", "worried", "scared"
        ],
        "greed": [
            "مغامر", "جريء", "طمع", "سريع", "aggressive",
            "متهور", "طماع", "جشع", "greedy"
        ],
        "confidence": [
            "واثق", "متأكد", "جاهز", "قوي", "ممتاز",
            "مستعد", "واثق", "أكيد", "متيقن", "confident", "ready"
        ],
        "sadness": [
            "حزين", "محبط", "يأس", "تعبت", "فشل",
            "خسران", "حزنان", "مكتئب", "مكسور", "sad", "depressed"
        ],
        "joy": [
            "فرحان", "مبسوط", "سعيد", "نجحت", "ممتاز",
            "فرحة", "سعادة", "نجاح", "happy", "great", "excellent"
        ],
        "frustration": [
            "زعلان", "ضيق", "مضيق", "متضايق", "زعل", "غضبان",
            "معصب", "غاضب", "frustrated", "angry", "upset"
        ]
    }
    
    TRADING_TERMS = {
        "technical": [
            "rsi", "macd", "supertrend", "bollinger", "stochastic",
            "adx", "vwap", "ichimoku", "fibonacci", "support", "resistance"
        ],
        "market": [
            "نفط", "oil", "فضة", "silver", "ذهب", "gold", "dollar", "دولار",
            "spread", "سبريد", "commission", "عمولة", "swap", "مبادلة"
        ],
        "order": [
            "حد", "limit", "وقف", "stop", "market", "سوق",
            "pending", "معلق", "instant", "فوري"
        ]
    }
    
    # =================================================================
    # دوال الاستخراج والتحليل
    # =================================================================
    
    @classmethod
    def extract_numbers(cls, text: str) -> List[float]:
        """
        استخراج الأرقام من النص
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            List[float]: قائمة الأرقام المستخرجة
        """
        if not text:
            return []
        
        numbers = []
        for pattern in cls.NUMBER_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                # تحويل الأرقام العربية إلى إنجليزية
                arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
                num_str = match.translate(arabic_to_english)
                try:
                    numbers.append(float(num_str))
                except ValueError:
                    continue
        
        # إزالة التكرارات
        return list(set(numbers))
    
    @classmethod
    def extract_prices(cls, text: str) -> List[float]:
        """
        استخراج الأسعار من النص
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            List[float]: قائمة الأسعار المستخرجة
        """
        if not text:
            return []
        
        prices = []
        for pattern in cls.PRICE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    price = float(match)
                    if 0.1 <= price <= 10000:  # نطاق معقول للأسعار
                        prices.append(price)
                except ValueError:
                    continue
        
        # إذا لم يتم العثور على أسعار، استخدم extract_numbers
        if not prices:
            numbers = cls.extract_numbers(text)
            prices = [n for n in numbers if 0.1 <= n <= 10000]
        
        return list(set(prices))
    
    @classmethod
    def detect_signal_intent(cls, text: str) -> Optional[str]:
        """
        اكتشاف نية الإشارة (شراء/بيع/انتظار)
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            Optional[str]: "buy" أو "sell" أو "wait" أو None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        for signal, words in cls.SIGNAL_WORDS.items():
            if any(w in text_lower for w in words):
                return signal
        return None
    
    @classmethod
    def detect_risk_level(cls, text: str) -> str:
        """
        اكتشاف مستوى المخاطرة
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            str: "high" أو "moderate" أو "low"
        """
        if not text:
            return "moderate"
        
        text_lower = text.lower()
        for level, words in cls.RISK_WORDS.items():
            if any(w in text_lower for w in words):
                return level
        return "moderate"
    
    @classmethod
    def detect_emotion(cls, text: str) -> str:
        """
        اكتشاف المشاعر
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            str: اسم المشاعر المكتشفة
        """
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        # حساب درجة كل عاطفة
        emotion_scores = {}
        for emotion, words in cls.EMOTION_WORDS.items():
            score = sum(1 for w in words if w in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return "neutral"
        
        # إرجاع العاطفة الأعلى درجة
        return max(emotion_scores, key=emotion_scores.get)
    
    @classmethod
    def extract_price_levels(cls, text: str) -> List[float]:
        """
        استخراج مستويات الأسعار (دعم/مقاومة)
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            List[float]: قائمة مستويات الأسعار
        """
        return cls.extract_prices(text)
    
    @classmethod
    def is_question(cls, text: str) -> bool:
        """
        التحقق مما إذا كان النص سؤالاً
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            bool: True إذا كان النص سؤالاً
        """
        if not text:
            return False
        
        question_marks = ['?', '؟']
        question_words = ['كيف', 'ما', 'لماذا', 'متى', 'أين', 'من', 'هل', 
                         'who', 'what', 'how', 'why', 'when', 'where']
        text_lower = text.lower()
        
        return any(m in text for m in question_marks) or any(w in text_lower for w in question_words)
    
    @classmethod
    def is_command(cls, text: str) -> bool:
        """
        التحقق مما إذا كان النص أمراً
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            bool: True إذا كان النص أمراً
        """
        if not text:
            return False
        
        command_words = [
            'أرسل', 'حلل', 'افحص', 'أغلق', 'افتح', 'اشتر', 'بع',
            'send', 'analyze', 'check', 'close', 'open', 'buy', 'sell'
        ]
        text_lower = text.lower()
        return any(w in text_lower for w in command_words)
    
    @classmethod
    def is_greeting(cls, text: str) -> bool:
        """
        التحقق مما إذا كان النص تحية
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            bool: True إذا كان النص تحية
        """
        if not text:
            return False
        
        greeting_words = [
            'مرحبا', 'أهلا', 'سلام', 'صباح', 'مساء', 'السلام عليكم',
            'hello', 'hi', 'hey', 'good morning', 'good evening'
        ]
        text_lower = text.lower()
        return any(w in text_lower for w in greeting_words)
    
    @classmethod
    def is_farewell(cls, text: str) -> bool:
        """
        التحقق مما إذا كان النص وداعاً
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            bool: True إذا كان النص وداعاً
        """
        if not text:
            return False
        
        farewell_words = [
            'مع السلامة', 'وداع', 'باي', 'إلى اللقاء', 'سلام',
            'goodbye', 'bye', 'see you', 'farewell'
        ]
        text_lower = text.lower()
        return any(w in text_lower for w in farewell_words)
    
    @classmethod
    def extract_asset(cls, text: str) -> Optional[str]:
        """
        استخراج الأصل المذكور في النص
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            Optional[str]: "oil" أو "silver" أو None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["نفط", "oil", "usoil", "خام", "برنت", "petrol", "crude"]):
            return "oil"
        elif any(w in text_lower for w in ["فضة", "silver", "xag", "xagusd"]):
            return "silver"
        
        return None
    
    @classmethod
    def extract_timeframe(cls, text: str) -> Optional[str]:
        """
        استخراج الإطار الزمني المذكور في النص
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            Optional[str]: "5m" أو "15m" أو "1h" أو "4h" أو "1d" أو None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        timeframes = {
            "5m": ["5 دق", "5 دقيقة", "5m", "خمس دق"],
            "15m": ["15 دق", "15 دقيقة", "15m", "خمسة عشر دق"],
            "1h": ["1 ساعة", "ساعة", "1h", "hour"],
            "4h": ["4 ساعات", "4 ساعة", "4h", "اربعة ساعات"],
            "1d": ["يوم", "يومي", "1d", "daily", "daily"],
            "1w": ["اسبوع", "اسبوعي", "1w", "weekly"]
        }
        
        for tf, keywords in timeframes.items():
            if any(kw in text_lower for kw in keywords):
                return tf
        
        return None
    
    @classmethod
    def get_understanding_summary(cls, text: str) -> Dict[str, Any]:
        """
        الحصول على ملخص الفهم الكامل للنص
        
        Args:
            text: النص المراد تحليله
        
        Returns:
            Dict[str, Any]: ملخص الفهم
        """
        if not text:
            return {"error": "النص فارغ"}
        
        return {
            "text": text,
            "is_question": cls.is_question(text),
            "is_command": cls.is_command(text),
            "is_greeting": cls.is_greeting(text),
            "is_farewell": cls.is_farewell(text),
            "signal_intent": cls.detect_signal_intent(text),
            "risk_level": cls.detect_risk_level(text),
            "emotion": cls.detect_emotion(text),
            "numbers": cls.extract_numbers(text),
            "prices": cls.extract_prices(text),
            "asset": cls.extract_asset(text),
            "timeframe": cls.extract_timeframe(text),
            "is_trading_related": bool(cls.extract_asset(text) or cls.detect_signal_intent(text))
        }


# =====================================================================
# دالة مساعدة للاستخدام السريع
# =====================================================================

def understand(text: str) -> Dict[str, Any]:
    """فهم النص (وظيفة مساعدة)"""
    return LanguageUnderstanding.get_understanding_summary(text)


# =====================================================================
# اختبار سريع
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 اختبار Language Understanding")
    print("=" * 60)
    
    test_texts = [
        "اشتري النفط عند 75.50 دولار",
        "هل تحليل الفضة جيد؟",
        "أغلق صفقة النفط",
        "كيف السوق اليوم يا صديقي؟",
        "أنا خائف من هذه الصفقة",
        "بيع الفضة بسعر 29.75",
        "السلام عليكم، كيف حالك؟",
        "مع السلامة",
        "حلل لي النفط على فريم 4 ساعات"
    ]
    
    for text in test_texts:
        print(f"\n📩 '{text}'")
        understanding = LanguageUnderstanding.get_understanding_summary(text)
        print(f"   سؤال: {understanding['is_question']}")
        print(f"   أمر: {understanding['is_command']}")
        print(f"   تحية: {understanding['is_greeting']}")
        print(f"   وداع: {understanding['is_farewell']}")
        print(f"   إشارة: {understanding['signal_intent']}")
        print(f"   مخاطرة: {understanding['risk_level']}")
        print(f"   مشاعر: {understanding['emotion']}")
        print(f"   أرقام: {understanding['numbers']}")
        print(f"   أسعار: {understanding['prices']}")
        print(f"   أصل: {understanding['asset']}")
        print(f"   فريم: {understanding['timeframe']}")
    
    print("\n✅ اختبار Language Understanding ناجح!")
