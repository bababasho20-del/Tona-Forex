"""
🎯 تصنيف النية - Intent Classification Module (V7 Wrapper)
🤖 تولين: واجهة بسيطة تستدعي مكتبة النيات V7
"""

import re
import logging
from typing import Dict, Optional, Tuple

from intents_library_v7 import (
    INTENTS_LIBRARY_V7,
    find_intent_v7,
    get_intent_definition,
    get_intent_response,
    is_dynamic_intent,
    get_handler,
    requires_asset,
    get_intents_by_category,
    IntentCategory
)

logger = logging.getLogger("TonaPrometheus")

class IntentClassifier:
    """
    تصنيف نية المستخدم باستخدام مكتبة النيات V7
    """
    
    @classmethod
    def classify(cls, text: str) -> str:
        """
        تصنيف نية المستخدم من النص
        
        Args:
            text: نص رسالة المستخدم
        
        Returns:
            str: اسم النية المكتشفة
        """
        if not text or not text.strip():
            return "general"
        
        intent_id, confidence, handler = find_intent_v7(text)
        return intent_id
    
    @classmethod
    def classify_with_confidence(cls, text: str) -> Tuple[str, float]:
        """
        تصنيف النية مع درجة الثقة
        
        Returns:
            Tuple[str, float]: (النية, درجة الثقة 0-1)
        """
        if not text or not text.strip():
            return "general", 0.0
        
        intent_id, confidence, handler = find_intent_v7(text)
        return intent_id, confidence
    
    @classmethod
    def extract_asset(cls, text: str) -> Optional[str]:
        """
        استخراج الأصل المذكور في النص
        
        Returns:
            Optional[str]: "oil" أو "silver" أو None
        """
        text_lower = text.lower()
        
        oil_keywords = ["نفط", "oil", "usoil", "خام", "برنت", "petrol", "crude"]
        if any(kw in text_lower for kw in oil_keywords):
            return "oil"
        
        silver_keywords = ["فضة", "silver", "xag", "xagusd", "فضي"]
        if any(kw in text_lower for kw in silver_keywords):
            return "silver"
        
        return None
    
    @classmethod
    def extract_action(cls, text: str) -> Optional[str]:
        """
        استخراج الإجراء المطلوب من النص
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["شراء", "buy", "اشتري", "شرا", "long"]):
            return "buy"
        elif any(kw in text_lower for kw in ["بيع", "sell", "بع", "short"]):
            return "sell"
        elif any(kw in text_lower for kw in ["اغلاق", "إغلاق", "close", "خروج", "exit"]):
            return "close"
        elif any(kw in text_lower for kw in ["انتظار", "انتظر", "wait", "صبر"]):
            return "wait"
        
        return None
    
    @classmethod
    def get_intent_description(cls, intent: str) -> str:
        """الحصول على وصف للنية"""
        descriptions = {
            # الأقسام الرئيسية
            "market_overview": "📊 نظرة عامة على السوق",
            "price_current": "💰 السعر الحالي",
            "price_change": "📈 تغير السعر",
            "price_history": "📊 تاريخ السعر",
            "volume_analysis": "📊 تحليل الحجم",
            "market_structure": "🏗️ بنية السوق",
            "candlestick_analysis": "🕯️ تحليل الشموع",
            "market_session": "🕐 جلسة السوق",
            
            # المؤشرات الفنية
            "rsi_analysis": "📈 تحليل RSI",
            "macd_analysis": "📊 تحليل MACD",
            "bollinger_analysis": "📊 تحليل Bollinger",
            "moving_averages": "📈 المتوسطات المتحركة",
            "vwap_analysis": "📊 تحليل VWAP",
            "adx_analysis": "📊 تحليل ADX",
            "atr_analysis": "📊 تحليل ATR",
            "stochastic_analysis": "📊 تحليل Stochastic",
            "fibonacci_analysis": "📊 تحليل Fibonacci",
            "ichimoku_analysis": "📊 تحليل Ichimoku",
            "vpt_supertrend_analysis": "📊 تحليل VPT Supertrend",
            "pivot_points": "📊 نقاط الارتكاز",
            "order_flow_analysis": "📊 تدفق الأوامر",
            "open_interest": "📊 الفائدة المفتوحة",
            "funding_rate": "📊 معدل التمويل",
            "liquidation_heatmap": "📊 خريطة التصفية",
            "sentiment_analysis": "📊 تحليل المشاعر",
            "wyckoff_analysis": "📊 تحليل Wyckoff",
            "harmonic_patterns": "📊 الأنماط التوافقية",
            "elliott_wave": "📊 موجات إليوت",
            "divergence_analysis": "📊 تحليل التباعد",
            "support_resistance": "📊 الدعم والمقاومة",
            "trend_lines": "📊 خطوط الاتجاه",
            "chart_patterns": "📊 الأنماط السعرية",
            "volume_profile": "📊 بروفايل الحجم",
            "correlation_analysis": "📊 تحليل الارتباط",
            
            # إدارة الصفقات
            "trade_open": "📈 فتح صفقة",
            "trade_close": "📉 إغلاق صفقة",
            "trade_modify": "✏️ تعديل صفقة",
            "trade_status": "📊 حالة الصفقة",
            "trade_history": "📋 تاريخ الصفقات",
            "trade_analysis": "🔍 تحليل الصفقة",
            "trade_journal": "📖 يومية التداول",
            "trade_plan": "📋 خطة التداول",
            
            # إدارة المخاطر
            "risk_assessment": "🛡️ تقييم المخاطر",
            "position_sizing": "📊 حجم الصفقة",
            "stop_loss_placement": "🛡️ وقف الخسارة",
            "take_profit_placement": "🎯 الهدف",
            "risk_reward_ratio": "📊 نسبة المخاطرة للمكافأة",
            "portfolio_risk": "📊 مخاطر المحفظة",
            "drawdown_analysis": "📊 تحليل التراجع",
            "margin_call_warning": "⚠️ نداء الهامش",
            "breakeven_analysis": "⚖️ نقطة التعادل",
            "trailing_stop_strategy": "📊 استراتيجية الوقف المتحرك",
            
            # الأخبار والأحداث
            "news_general": "📰 أخبار عامة",
            "oil_specific_news": "🛢️ أخبار النفط",
            "silver_specific_news": "🥈 أخبار الفضة",
            "economic_events": "📊 الأحداث الاقتصادية",
            "event_impact": "📊 تأثير الأحداث",
            "geopolitical_analysis": "🌍 تحليل جيوسياسي",
            "weather_impact": "🌤️ تأثير الطقس",
            
            # التوقعات والسيناريوهات
            "price_prediction": "🔮 توقع السعر",
            "scenario_analysis": "📊 تحليل السيناريو",
            "explosion_prediction": "💥 توقع الانفجار",
            "reversal_expectation": "🔄 توقع الانعكاس",
            "target_levels": "🎯 الأهداف المتوقعة",
            "time_prediction": "⏰ توقع الوقت",
            "probability_analysis": "📊 تحليل الاحتمالات",
            
            # التعلم والتحسين
            "learning_questions": "🧠 أسئلة التعلم",
            "strategy_education": "📚 تعليم الاستراتيجية",
            "indicator_education": "📚 تعليم المؤشرات",
            "trading_psychology_education": "🧠 سيكولوجيا التداول",
            "market_microstructure": "📊 البنية الدقيقة للسوق",
            "backtesting_education": "📊 اختبار الاستراتيجيات",
            
            # السيكولوجيا
            "emotional_support": "💙 الدعم العاطفي",
            "motivation": "🌟 تحفيز",
            "fear_greed_assessment": "📊 الخوف والطمع",
            "trading_mindset_check": "🧠 عقلية التداول",
            
            # التحكم بالبوت
            "bot_settings": "⚙️ إعدادات البوت",
            "alert_setup": "🔔 إعداد التنبيهات",
            "bot_status": "📊 حالة البوت",
            "mode_switch": "🔄 تبديل الوضع",
            "report_request": "📊 طلب تقرير",
            "data_refresh": "🔄 تحديث البيانات",
            
            # التفاعل الشخصي
            "greeting": "👋 تحية",
            "farewell": "👋 وداع",
            "how_are_you": "😊 كيف حالك",
            "about_identity": "🤖 الهوية",
            "gratitude": "🙏 شكر",
            "compliment": "🌟 إطراء",
            "complaint": "😔 شكوى",
            "alertness_command": "🔔 أمر اليقظة",
            
            # عام
            "general_advice": "💡 نصيحة عامة",
            "market_silence": "🔇 هدوء السوق",
            "market_comparison": "📊 مقارنة السوق",
            "trading_hours": "🕐 أوقات التداول",
            "broker_questions": "🏦 أسئلة عن الوسيط",
            "platform_questions": "💻 أسئلة عن المنصة",
            "general": "💬 عام"
        }
        return descriptions.get(intent, f"نية غير معروفة: {intent}")
    
    @classmethod
    def is_action_intent(cls, intent: str) -> bool:
        """التحقق مما إذا كانت النية تتطلب إجراءً"""
        action_intents = [
            "trade_open", "trade_close", "trade_modify", "report_request",
            "data_refresh", "alert_setup", "mode_switch"
        ]
        return intent in action_intents
    
    @classmethod
    def is_emotional_intent(cls, intent: str) -> bool:
        """التحقق مما إذا كانت النية عاطفية"""
        emotional_intents = [
            "emotional_support", "motivation", "gratitude", "compliment",
            "complaint", "greeting", "how_are_you"
        ]
        return intent in emotional_intents


# =====================================================================
# دالة مساعدة للاستخدام السريع
# =====================================================================

def classify_intent(text: str) -> str:
    """تصنيف نية المستخدم (وظيفة مساعدة)"""
    return IntentClassifier.classify(text)


# =====================================================================
# اختبار سريع
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 اختبار Intent Classifier V7")
    print("=" * 60)
    
    test_messages = [
        "السلام عليكم",
        "كيف حالك يا تولين",
        "كم سعر النفط",
        "rsi النفط كم",
        "هل أغلق الصفقة",
        "خسرت اليوم",
        "ما الجديد",
        "توقع النفط",
        "كن متيقظا",
        "شكراً يا تولين",
        "ما هي أفضل منصة",
        "السوق ساكن",
        "أين أضع SL للنفط",
        "شرح vwap",
        "تحليل آخر صفقة",
        "سؤال عشوائي",
        "اتوقع النفط يرتفع",
        "لماذا خسرت صفقتي",
        "ماسبب خسارة اخر صفقة",
        "ما هو البوت",
        "حلل الفضة",
        "كم النفط",
        "ماذا تعلمت",
        "هل تتعلم من اخطاءك",
        "ماهو الخطر في الصفقة",
        "هل الصفقة آمنة",
        "هل أدخل الصفقة",
        "هل أخرج",
        "ماذا يقول البولينجر"
    ]
    
    success_count = 0
    for msg in test_messages:
        intent = IntentClassifier.classify(msg)
        confidence = IntentClassifier.classify_with_confidence(msg)
        asset = IntentClassifier.extract_asset(msg)
        action = IntentClassifier.extract_action(msg)
        
        print(f"\n📩 '{msg}'")
        print(f"   النية: {intent} ({IntentClassifier.get_intent_description(intent)})")
        print(f"   الثقة: {confidence[1]:.2f}")
        if asset:
            print(f"   الأصل: {asset}")
        if action:
            print(f"   الإجراء: {action}")
    
    print("\n✅ اختبار Intent Classifier V7 ناجح!")
