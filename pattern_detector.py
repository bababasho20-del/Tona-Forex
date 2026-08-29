# =====================================================================
# 🧠 pattern_detector.py - نظام اكتشاف الأنماط للحوباني
# =====================================================================

import logging
from datetime import datetime

class PatternDetector:
    """
    يكتشف الأنماط الفنية من تحليل السوق ويترجمها إلى رؤى.
    """
    
    def __init__(self):
        self.detected_patterns = []
    
    def detect(self, analysis):
        """
        اكتشاف الأنماط من تحليل السوق.
        يعيد قائمة بالأنماط المكتشفة مع توصيات.
        """
        if not analysis:
            return []
        
        patterns = []
        
        # ============================================================
        # 1. نمط الارتداد من الدعم
        # ============================================================
        if analysis.get("bb_position") == "الحد السفلي (دعم)":
            if analysis.get("rsi", 50) < 40:
                patterns.append({
                    "type": "bounce_from_support",
                    "name": "🔄 ارتداد من الدعم",
                    "description": f"السعر عند الحد السفلي للبولينجر ({analysis['bb_lower']:.2f}$) مع RSI منخفض ({analysis['rsi']}).",
                    "signal": "احتمال ارتداد صاعد",
                    "confidence": "متوسطة" if analysis.get("volume_ratio", 1) > 1 else "ضعيفة",
                    "recommendation": "مراقبة تأكيد الارتداد قبل الدخول."
                })
        
        # ============================================================
        # 2. نمط اختراق المقاومة
        # ============================================================
        if analysis.get("bb_position") == "الحد العلوي (مقاومة)":
            if analysis.get("volume_ratio", 1) > 1.5:
                patterns.append({
                    "type": "breakout_resistance",
                    "name": "🚀 اختراق مقاومة",
                    "description": f"السعر عند الحد العلوي للبولينجر ({analysis['bb_upper']:.2f}$) مع فوليوم مرتفع ({analysis['volume_ratio']:.2f}x).",
                    "signal": "اختراق محتمل للمقاومة",
                    "confidence": "قوية" if analysis.get("adx", 15) > 25 else "متوسطة",
                    "recommendation": "انتظر تأكيد الاختراق بفوليوم أعلى."
                })
        
        # ============================================================
        # 3. نمط ضعف الزخم
        # ============================================================
        if analysis.get("macd", 0) < 0 and analysis.get("trend") == "صاعد":
            patterns.append({
                "type": "momentum_weakness",
                "name": "⚠️ ضعف الزخم",
                "description": f"MACD سالب ({analysis['macd']:.4f}) مع اتجاه صاعد. بداية ضعف.",
                "signal": "احتمال تصحيح أو انعكاس",
                "confidence": "متوسطة",
                "recommendation": "تضييق وقف الخسارة أو تأمين الأرباح."
            })
        
        # ============================================================
        # 4. نمط قوة الزخم
        # ============================================================
        if analysis.get("macd", 0) > 0 and analysis.get("trend") == "هابط":
            patterns.append({
                "type": "momentum_strength",
                "name": "⚡ قوة الزخم",
                "description": f"MACD موجب ({analysis['macd']:.4f}) مع اتجاه هابط. بداية قوة.",
                "signal": "احتمال انعكاس صاعد",
                "confidence": "متوسطة",
                "recommendation": "مراقبة تأكيد الانعكاس."
            })
        
        # ============================================================
        # 5. سيولة استثنائية
        # ============================================================
        if analysis.get("volume_ratio", 1) > 2.0:
            patterns.append({
                "type": "exceptional_liquidity",
                "name": "🔥 سيولة استثنائية",
                "description": f"الفوليوم أعلى بـ {analysis['volume_ratio']:.2f}x من المتوسط.",
                "signal": "حركة قوية قادمة",
                "confidence": "قوية",
                "recommendation": "استعد لحركة حادة. راقب الاتجاه."
            })
        
        # ============================================================
        # 6. تباطؤ (سوق جانبي)
        # ============================================================
        if analysis.get("adx", 15) < 20 and analysis.get("volume_ratio", 1) < 0.8:
            patterns.append({
                "type": "sideways_market",
                "name": "⏸️ سوق جانبي",
                "description": f"ADX منخفض ({analysis['adx']}) وفوليوم ضعيف ({analysis['volume_ratio']:.2f}x).",
                "signal": "سوق بدون اتجاه واضح",
                "confidence": "عالية",
                "recommendation": "تجنب الدخول حتى يتضح الاتجاه."
            })
        
        # ============================================================
        # 7. تشبع شراء/بيع
        # ============================================================
        if analysis.get("stochastic", 50) > 80:
            patterns.append({
                "type": "overbought",
                "name": "🔴 تشبع شراء",
                "description": f"Stochastic عند {analysis['stochastic']:.1f} (فوق 80).",
                "signal": "احتمال هبوط أو تصحيح",
                "confidence": "متوسطة",
                "recommendation": "تجنب الشراء. انتظر تصحيحاً."
            })
        elif analysis.get("stochastic", 50) < 20:
            patterns.append({
                "type": "oversold",
                "name": "🟢 تشبع بيع",
                "description": f"Stochastic عند {analysis['stochastic']:.1f} (تحت 20).",
                "signal": "احتمال صعود أو ارتداد",
                "confidence": "متوسطة",
                "recommendation": "تجنب البيع. انتظر ارتداداً."
            })
        
        # ============================================================
        # 8. قوة الاتجاه
        # ============================================================
        if analysis.get("adx", 15) > 30:
            if analysis.get("trend") == "صاعد":
                patterns.append({
                    "type": "strong_uptrend",
                    "name": "📈 اتجاه صاعد قوي",
                    "description": f"ADX قوي ({analysis['adx']}) مع اتجاه صاعد.",
                    "signal": "اتجاه صاعد قوي ومستمر",
                    "confidence": "عالية",
                    "recommendation": "استمر في الشراء مع تضييق الوقف."
                })
            elif analysis.get("trend") == "هابط":
                patterns.append({
                    "type": "strong_downtrend",
                    "name": "📉 اتجاه هابط قوي",
                    "description": f"ADX قوي ({analysis['adx']}) مع اتجاه هابط.",
                    "signal": "اتجاه هابط قوي ومستمر",
                    "confidence": "عالية",
                    "recommendation": "استمر في البيع مع تضييق الوقف."
                })
        
        # ============================================================
        # 9. تباعد (Divergence) - نمط متقدم
        # ============================================================
        # ملاحظة: هذا يحتاج إلى مقارنة مع بيانات سابقة، سنضيفه لاحقاً
        
        self.detected_patterns = patterns
        return patterns
    
    def get_summary(self, analysis):
        """
        يحصل على ملخص للأنماط المكتشفة.
        يعيد تقريراً مختصراً يمكن استخدامه في الردود.
        """
        patterns = self.detect(analysis)
        
        if not patterns:
            return "📊 **لا توجد أنماط واضحة حالياً.** السوق في منطقة انتظار."
        
        # ترتيب الأنماط حسب الثقة
        confidence_order = {"عالية": 0, "متوسطة": 1, "ضعيفة": 2}
        sorted_patterns = sorted(patterns, key=lambda p: confidence_order.get(p.get("confidence", "متوسطة"), 1))
        
        # بناء التقرير
        report = "🧠 **الأنماط المكتشفة:**\n\n"
        
        for i, pattern in enumerate(sorted_patterns[:3], 1):
            report += f"{i}. {pattern['name']}\n"
            report += f"   • {pattern['description']}\n"
            report += f"   • **الإشارة:** {pattern['signal']}\n"
            report += f"   • **الثقة:** {pattern.get('confidence', 'متوسطة')}\n"
            report += f"   • **توصية:** {pattern.get('recommendation', 'مراقبة')}\n\n"
        
        # إضافة توصية عامة
        report += "💡 **الخلاصة:**\n"
        high_confidence = [p for p in patterns if p.get("confidence") == "عالية"]
        if high_confidence:
            report += f"• أقوى إشارة حالياً: {high_confidence[0]['name']}\n"
            report += f"• {high_confidence[0]['recommendation']}"
        else:
            report += "• لا توجد إشارات قوية حالياً. انتظر وضوحاً أكبر."
        
        return report
    
    def get_trade_recommendation(self, analysis):
        """
        يحصل على توصية تداول بناءً على الأنماط.
        """
        patterns = self.detect(analysis)
        
        # حساب الدرجة الإجمالية
        score = 0
        
        for pattern in patterns:
            if pattern.get("signal") in ["احتمال ارتداد صاعد", "اختراق محتمل للمقاومة", "اتجاه صاعد قوي ومستمر"]:
                score += 1
            elif pattern.get("signal") in ["احتمال هبوط أو تصحيح", "اتجاه هابط قوي ومستمر"]:
                score -= 1
        
        # إضافة وزن للثقة
        for pattern in patterns:
            if pattern.get("confidence") == "عالية":
                score += 0.5 if score > 0 else -0.5
            elif pattern.get("confidence") == "ضعيفة":
                score -= 0.5 if score > 0 else 0.5
        
        # توليد التوصية
        if score >= 2:
            return "🟢 **توصية: شراء (BUY)** - المؤشرات تدعم الصعود بقوة."
        elif score >= 0.5:
            return "🟡 **توصية: ميل للشراء** - المؤشرات إيجابية لكن بحذر."
        elif score <= -2:
            return "🔴 **توصية: بيع (SELL)** - المؤشرات تدعم الهبوط بقوة."
        elif score <= -0.5:
            return "🟡 **توصية: ميل للبيع** - المؤشرات سلبية لكن بحذر."
        else:
            return "⚪ **توصية: انتظار** - المؤشرات متضاربة، انتظر وضوحاً."
