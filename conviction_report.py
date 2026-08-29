"""
📋 Conviction Report - ملف القناعة الكامل للتوصيات
👨‍💻 المطور: بسام الحوباني
💙 جزء من نظام تولين الاستشاري
📊 يعتمد على بيانات حقيقية 100% مع تحليل التوافق بين الإشارة والفريمات

✅ التعديلات الجديدة:
   1. إعادة ترتيب التوصية: الأسعار تحت التوصية مباشرة.
   2. تحسين تحليل التوافق مع الفريمات (أكثر وضوحاً ودقة).
   3. إضافة تحقق من وجود price في analysis لتجنب الأخطاء.
   4. تحسين حساب مستوى الخطر (مراعاة التناقض بشكل أفضل).
   5. إزالة الإيموجي المكرر وتحسين التنسيق.
   6. إضافة تعليقات توضيحية للمنطق الحساس.
"""

import random
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("TonaPrometheus")

class ConvictionReport:
    """توليد تقرير القناعة الكامل للتوصيات من بيانات حقيقية"""
    
    def __init__(self):
        self.closing_messages = [
            "💙 تولين: أنا هنا لأكون معك في كل خطوة... ثق بتحليلك",
            "💙 تولين: التداول رحلة... وأنا رفيقتك في هذه الرحلة",
            "💙 تولين: لا تخف من الخسارة... تعلم منها وكن أقوى",
            "💙 تولين: السوق لا ينام... لكننا ننام لنرتاح ونربح غداً",
            "💙 تولين: الصبر مفتاح الربح... والسوق يكافئ الصبورين",
            "💙 تولين: كل صفقة تحمل درساً... وأنا هنا لأعلمك وأتعلم معك",
            "💙 تولين: الثقة تأتي من الخبرة... وخبرتي تنمو مع كل صفقة",
            "💙 تولين: أنا فخورة بأن أكون مستشارتك... ثق بنفسك وبي"
        ]
    
    def generate(self, asset_type: str, signal: str, analysis: Dict, 
                 confidence: Dict, trade_context: Dict) -> str:
        """
        توليد تقرير القناعة الكامل من بيانات حقيقية مع تحليل التوافق
        """
        asset_label = "النفط الخام" if asset_type == "oil" else "الفضة"
        
        lines = []
        
        # ── 1. العنوان ──
        lines.append(f"📊 **توصية تولين - {asset_label}**")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ── 2. التوصية ودرجة الثقة ──
        signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
        signal_text = "شراء (BUY)" if signal == "BUY" else "بيع (SELL)" if signal == "SELL" else "انتظار (WAIT)"
        lines.append("")
        lines.append(f"🎯 **التوصية:** {signal_emoji} {signal_text}")
        lines.append(f"📊 **درجة الثقة:** {confidence['total']:.0f}% {confidence['emoji']}")
        lines.append(f"📋 **التقييم:** {confidence['grade']}")
        
        # ── 3. ✅ نقاط الدخول والخروج (تم نقلها إلى الأعلى) ──
        #    هذا هو التعديل الأساسي: الأسعار تأتي مباشرة بعد التوصية
        lines.append("")
        lines.append("**نقاط الدخول والخروج:**")
        lines.append(f"   • السعر الحالي:   ${trade_context.get('price', 0):.2f}")
        lines.append(f"   • الدخول:          ${trade_context.get('entry', 0):.2f}")
        lines.append(f"   • وقف الخسارة:   ${trade_context.get('sl', 0):.2f}")
        lines.append(f"   • الهدف:          ${trade_context.get('tp', 0):.2f}")
        lines.append(f"   • نسبة المخاطرة/المكافأة: {trade_context.get('rr', 1.0):.2f}")
        
        # ── 4. تفصيل النقاط ──
        lines.append("")
        lines.append("📊 **تفصيل نقاط القوة:**")
        for factor, grade in confidence.get('breakdown', {}).items():
            factor_label = self._get_factor_label(factor)
            lines.append(f"   • {factor_label}: {grade}")
        
        # ── 5. أسباب التأييد والتحذيرات ──
        lines.append("")
        lines.append("📋 **أسباب التأييد والتحذيرات:**")
        supporting = self._get_supporting_factors(analysis, signal)
        if supporting:
            for reason in supporting[:6]:
                lines.append(f"   {reason}")
        else:
            lines.append("   ⚠️ لا توجد أسباب واضحة")
        
        # ── 6. عوامل الخطر ──
        lines.append("")
        lines.append("⚠️ **عوامل الخطر:**")
        risks = self._get_risk_factors(analysis, signal)
        if risks:
            for risk in risks[:4]:
                lines.append(f"   {risk}")
        else:
            lines.append("   🟢 لا توجد مخاطر ملحوظة حالياً")
        
        # ── 7. الخبرة السابقة (بيانات حقيقية) ──
        similar = self._get_real_similar_cases(asset_type, signal)
        if similar and similar.get('count', 0) > 0:
            lines.append("")
            lines.append(f"🧠 **الخبرة السابقة (من الصفقات الحقيقية):**")
            lines.append(f"   • عدد الصفقات المشابهة: {similar['count']}")
            lines.append(f"   • نسبة النجاح: {similar['win_rate']:.1f}%")
            lines.append(f"   • متوسط الربح/الخسارة: ${similar['avg_profit']:.2f}")
            if similar.get('total_trades', 0) > 0:
                lines.append(f"   • إجمالي الصفقات المسجلة: {similar['total_trades']}")
                lines.append(f"   • نسبة النجاح الإجمالية: {similar.get('overall_win_rate', 0):.1f}%")
            if similar.get('lessons'):
                lines.append("")
                lines.append(f"📚 **الدروس المستفادة من التاريخ:**")
                for lesson in similar['lessons'][:2]:
                    lines.append(f"   • {lesson}")
            lines.append(f"   📌 _بيانات حقيقية من {similar.get('data_source', 'سجل الصفقات')}_")
        else:
            lines.append("")
            lines.append("🧠 **الخبرة السابقة:**")
            lines.append("   ⚠️ لا توجد بيانات كافية للصفقات المشابهة")
        
        # ── 8. مستوى الخطر ──
        risk_level = self._calculate_risk_level(analysis, signal)
        lines.append("")
        lines.append(f"🛡️ **مستوى الخطر:** {risk_level['emoji']} {risk_level['text']}")
        
        # ── 9. نصائح إضافية ──
        tips = self._get_extra_tips(analysis, signal)
        if tips:
            lines.append("")
            lines.append("💡 **نصائح إضافية:**")
            for tip in tips[:2]:
                lines.append(f"   • {tip}")
        
        # ── 10. رسالة ختامية ──
        lines.append("")
        lines.append(random.choice(self.closing_messages))
        
        return "\n".join(lines)
    
    def _get_factor_label(self, factor: str) -> str:
        """ترجمة أسماء العوامل"""
        labels = {
            "trend_alignment": "توافق الاتجاهات",
            "volume_confirmation": "تأكيد الحجم",
            "momentum_strength": "قوة الزخم",
            "timeframe_confluence": "توافق الفريمات",
            "historical_accuracy": "الدقة التاريخية",
            "risk_reward_ratio": "نسبة المخاطرة/المكافأة"
        }
        return labels.get(factor, factor)
    
    # ✅ الدالة المحسنة - تحليل التوافق بين الإشارة والفريمات
    def _get_supporting_factors(self, analysis: Dict, signal: str) -> List[str]:
        """
        استخراج أسباب التأييد أو التحذيرات بناءً على توافق الإشارة مع الفريمات
        والمؤشرات الفنية الأخرى.
        """
        factors = []
        
        # ── التحقق من وجود data ──
        if not analysis:
            return ["⚠️ لا توجد بيانات للتحليل"]
        
        # ── 1. تحليل اتجاهات الفريمات ──
        timeframes = analysis.get("timeframes", {})
        trends = []
        for tf in ["5m", "15m", "1h", "4h"]:
            if tf in timeframes:
                st = timeframes[tf].get("supertrend", {})
                if st:
                    trends.append(st.get("trend", 1))
        
        total = len(trends)
        if total == 0:
            return ["⚠️ لا توجد بيانات كافية للفريمات"]
        
        bullish_count = sum(1 for t in trends if t == 1)
        bearish_count = total - bullish_count
        
        # ── 2. تحليل التوافق بين الإشارة والفريمات ──
        if signal == "SELL":
            if bearish_count >= 3:
                factors.append(f"✅ اتجاهات متوافقة هابطة على {bearish_count}/{total} فريمات")
            elif bearish_count >= 2:
                factors.append(f"🟡 اتجاهات هابطة على {bearish_count}/{total} فريمات - توافق متوسط")
            else:
                # 🔴 تناقض حاد
                factors.append(f"🔴 **تناقض حاد:** {bullish_count}/{total} فريمات صاعدة لكن الإشارة بيع")
                factors.append(f"   ⚠️ صفقة ضعيفة جداً - المؤشرات لا تدعم الاتجاه الهابط")
                factors.append(f"   💡 يوصى بتأجيل الصفقة حتى توافق الفريمات")
        
        elif signal == "BUY":
            if bullish_count >= 3:
                factors.append(f"✅ اتجاهات متوافقة صاعدة على {bullish_count}/{total} فريمات")
            elif bullish_count >= 2:
                factors.append(f"🟡 اتجاهات صاعدة على {bullish_count}/{total} فريمات - توافق متوسط")
            else:
                # 🔴 تناقض حاد
                factors.append(f"🔴 **تناقض حاد:** {bearish_count}/{total} فريمات هابطة لكن الإشارة شراء")
                factors.append(f"   ⚠️ صفقة ضعيفة جداً - المؤشرات لا تدعم الاتجاه الصاعد")
                factors.append(f"   💡 يوصى بتأجيل الصفقة حتى توافق الفريمات")
        
        else:  # WAIT
            factors.append(f"⚪ الإشارة WAIT - انتظر توافق الفريمات")
            return factors
        
        # ── 3. تحليل المؤشرات الإضافية ──
        tf_15m = timeframes.get("15m", {})
        
        # الحجم
        vol_ratio = tf_15m.get("volume_ratio", 1)
        if vol_ratio is not None:
            if vol_ratio >= 1.5:
                factors.append(f"✅ حجم تداول مرتفع ({vol_ratio:.1f}x المتوسط)")
            elif vol_ratio >= 1.0:
                factors.append(f"🟡 حجم تداول طبيعي ({vol_ratio:.1f}x المتوسط)")
            else:
                factors.append(f"🔴 حجم تداول منخفض ({vol_ratio:.1f}x المتوسط)")
        
        # الزخم (ADX)
        adx = tf_15m.get("adx", 15)
        if adx is not None:
            if adx >= 30:
                factors.append(f"✅ زخم قوي (ADX: {adx:.0f})")
            elif adx >= 25:
                factors.append(f"🟡 زخم جيد (ADX: {adx:.0f})")
            elif adx >= 20:
                factors.append(f"🟡 زخم متوسط (ADX: {adx:.0f})")
            else:
                factors.append(f"🔴 زخم ضعيف (ADX: {adx:.0f})")
        
        # RSI
        rsi = tf_15m.get("rsi", 50)
        if rsi is not None:
            if signal == "SELL" and rsi > 70:
                factors.append(f"✅ RSI في منطقة ذروة شراء ({rsi:.0f}) - تدعم البيع")
            elif signal == "BUY" and rsi < 30:
                factors.append(f"✅ RSI في منطقة ذروة بيع ({rsi:.0f}) - تدعم الشراء")
            elif signal == "SELL" and rsi < 30:
                factors.append(f"🔴 RSI في منطقة ذروة بيع ({rsi:.0f}) - ضد الاتجاه الهابط")
            elif signal == "BUY" and rsi > 70:
                factors.append(f"🔴 RSI في منطقة ذروة شراء ({rsi:.0f}) - ضد الاتجاه الصاعد")
            elif rsi > 70:
                factors.append(f"🟡 RSI في منطقة ذروة شراء ({rsi:.0f}) - حذر من التصحيح")
            elif rsi < 30:
                factors.append(f"🟡 RSI في منطقة ذروة بيع ({rsi:.0f}) - حذر من الارتداد")
        
        # MACD
        macd = tf_15m.get("macd", 0)
        if macd is not None:
            if signal == "SELL" and macd < 0:
                factors.append(f"✅ MACD سلبي ({macd:.4f}) - يؤكد الزخم الهابط")
            elif signal == "BUY" and macd > 0:
                factors.append(f"✅ MACD إيجابي ({macd:.4f}) - يؤكد الزخم الصاعد")
            elif signal == "SELL" and macd > 0:
                factors.append(f"🔴 MACD إيجابي ({macd:.4f}) - ضد الاتجاه الهابط")
            elif signal == "BUY" and macd < 0:
                factors.append(f"🔴 MACD سلبي ({macd:.4f}) - ضد الاتجاه الصاعد")
        
        return factors
    
    def _get_risk_factors(self, analysis: Dict, signal: str) -> List[str]:
        """استخراج عوامل الخطر"""
        risks = []
        
        if not analysis:
            return ["⚠️ لا توجد بيانات لتقييم المخاطر"]
        
        price = analysis.get("price") or analysis.get("current_price", 0)
        if price == 0:
            # محاولة استخراج السعر من timeframes
            timeframes = analysis.get("timeframes", {})
            tf_15m = timeframes.get("15m", {})
            price = tf_15m.get("price", 0)
        
        if price == 0:
            risks.append("⚠️ غير قادر على تحديد السعر الحالي")
            return risks
        
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        
        # Bollinger Bands
        bb = tf_15m.get("bollinger", {})
        upper = bb.get("upper")
        lower = bb.get("lower")
        
        if upper and lower:
            if price > upper * 0.98:
                risks.append(f"🟡 السعر قرب مقاومة قوية (${upper:.2f})")
            if price < lower * 1.02:
                risks.append(f"🟡 السعر قرب دعم قوي (${lower:.2f})")
        
        # ADX ضعيف
        adx = tf_15m.get("adx")
        if adx is not None and adx < 20:
            risks.append(f"🟡 ADX ضعيف ({adx:.0f}) - الاتجاه غير مؤكد")
        
        # حجم منخفض
        vol_ratio = tf_15m.get("volume_ratio")
        if vol_ratio is not None and vol_ratio < 0.6:
            risks.append(f"🔴 حجم تداول منخفض ({vol_ratio:.1f}x المتوسط)")
        
        # عدم توافق الفريمات (تحليل سريع)
        timeframes = analysis.get("timeframes", {})
        trends = []
        for tf in ["5m", "15m", "1h", "4h"]:
            st = timeframes.get(tf, {}).get("supertrend", {})
            if st:
                trends.append(st.get("trend", 1))
        
        if trends:
            total = len(trends)
            bullish_count = sum(1 for t in trends if t == 1)
            
            if signal == "SELL" and bullish_count / total > 0.5:
                risks.append(f"🔴 تناقض حاد: {bullish_count}/{total} فريمات صاعدة لكن الإشارة بيع")
            elif signal == "BUY" and (total - bullish_count) / total > 0.5:
                risks.append(f"🔴 تناقض حاد: {total - bullish_count}/{total} فريمات هابطة لكن الإشارة شراء")
        
        return risks
    
    def _get_real_similar_cases(self, asset_type: str, signal: str) -> Optional[Dict]:
        """الحصول على بيانات حقيقية من سجل الصفقات"""
        try:
            from main import load_trades_history, calculate_statistics
            
            history = load_trades_history(asset_type)
            all_trades = history.get('trades', [])
            
            if not all_trades:
                return None
            
            closed_trades = [t for t in all_trades if t.get('status') == 'closed']
            
            if not closed_trades:
                return None
            
            similar_trades = [t for t in closed_trades if t.get('type') == signal]
            
            if not similar_trades:
                return {
                    "count": 0,
                    "win_rate": 0,
                    "avg_profit": 0,
                    "total_trades": len(closed_trades),
                    "overall_win_rate": 0,
                    "lessons": ["لا توجد صفقات سابقة بنفس الإشارة"],
                    "data_source": "سجل الصفقات"
                }
            
            winning = [t for t in similar_trades if t.get('profit_dollars', 0) > 0]
            win_rate = (len(winning) / len(similar_trades) * 100) if similar_trades else 0
            avg_profit = sum(t.get('profit_dollars', 0) for t in similar_trades) / len(similar_trades) if similar_trades else 0
            
            stats = calculate_statistics(asset_type)
            
            lessons = []
            if win_rate >= 60:
                lessons.append(f"✅ نسبة النجاح {win_rate:.1f}% - جيدة")
            elif win_rate >= 50:
                lessons.append(f"🟡 نسبة النجاح {win_rate:.1f}% - متوسطة")
            else:
                lessons.append(f"🔴 نسبة النجاح {win_rate:.1f}% - منخفضة")
            
            return {
                "count": len(similar_trades),
                "win_rate": win_rate,
                "avg_profit": avg_profit,
                "total_trades": stats.get('total_trades', 0),
                "overall_win_rate": stats.get('win_rate', 0),
                "lessons": lessons[:3],
                "data_source": f"سجل الصفقات ({len(closed_trades)} صفقة مغلقة)"
            }
            
        except Exception as e:
            logger.error(f"❌ فشل جلب البيانات الحقيقية: {e}")
            return None
    
    def _calculate_risk_level(self, analysis: Dict, signal: str) -> Dict:
        """
        حساب مستوى الخطر مع مراعاة التناقض بين الإشارة والفريمات
        ✅ تم تحسين الدقة في تقدير المخاطر
        """
        risk_score = 0
        
        if not analysis:
            return {"emoji": "⚠️", "text": "غير معروف - بيانات غير كافية"}
        
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        
        # ── 1. تحليل الفريمات للتناقض ──
        timeframes = analysis.get("timeframes", {})
        trends = []
        for tf in ["5m", "15m", "1h", "4h"]:
            st = timeframes.get(tf, {}).get("supertrend", {})
            if st:
                trends.append(st.get("trend", 1))
        
        if trends:
            total = len(trends)
            bullish_count = sum(1 for t in trends if t == 1)
            bearish_count = total - bullish_count
            
            # 🔴 تناقض حاد = خطر مرتفع
            if signal == "SELL" and bullish_count > bearish_count:
                risk_score += 3
            elif signal == "BUY" and bearish_count > bullish_count:
                risk_score += 3
            # 🟡 تناقض متوسط
            elif signal == "SELL" and bullish_count == bearish_count:
                risk_score += 1
            elif signal == "BUY" and bearish_count == bullish_count:
                risk_score += 1
        
        # ── 2. عوامل الخطر الأخرى ──
        adx = tf_15m.get("adx")
        if adx is not None and adx < 20:
            risk_score += 2
        elif adx is not None and adx < 15:
            risk_score += 3
        
        vol_ratio = tf_15m.get("volume_ratio")
        if vol_ratio is not None and vol_ratio < 0.6:
            risk_score += 2
        elif vol_ratio is not None and vol_ratio < 0.4:
            risk_score += 3
        
        # RSI متطرف (زيادة المخاطر)
        rsi = tf_15m.get("rsi")
        if rsi is not None:
            if (signal == "BUY" and rsi > 75) or (signal == "SELL" and rsi < 25):
                risk_score += 2
            elif (signal == "BUY" and rsi > 85) or (signal == "SELL" and rsi < 15):
                risk_score += 3
        
        # ── 3. تحديد المستوى ──
        if risk_score <= 1:
            return {"emoji": "🟢", "text": "منخفض - مناسب للتداول"}
        elif risk_score <= 3:
            return {"emoji": "🟡", "text": "متوسط - يوصى بالحذر"}
        elif risk_score <= 5:
            return {"emoji": "🟠", "text": "مرتفع - غير مناسب للتداول"}
        else:
            return {"emoji": "🔴", "text": "مرتفع جداً - تجنب الصفقة"}
    
    def _get_extra_tips(self, analysis: Dict, signal: str) -> List[str]:
        """نصائح إضافية"""
        tips = []
        
        if not analysis:
            return tips
        
        price = analysis.get("price") or analysis.get("current_price", 0)
        if price == 0:
            timeframes = analysis.get("timeframes", {})
            tf_15m = timeframes.get("15m", {})
            price = tf_15m.get("price", 0)
        
        if price == 0:
            return tips
        
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        adx = tf_15m.get("adx", 0)
        
        # تحليل الفريمات للتناقض
        timeframes = analysis.get("timeframes", {})
        trends = []
        for tf in ["5m", "15m", "1h", "4h"]:
            st = timeframes.get(tf, {}).get("supertrend", {})
            if st:
                trends.append(st.get("trend", 1))
        
        if trends:
            total = len(trends)
            bullish_count = sum(1 for t in trends if t == 1)
            
            if signal == "SELL" and bullish_count / total > 0.5:
                tips.append("⚠️ **تناقض خطير:** الفريمات صاعدة لكن الإشارة بيع - انتظر تأكيداً")
            elif signal == "BUY" and (total - bullish_count) / total > 0.5:
                tips.append("⚠️ **تناقض خطير:** الفريمات هابطة لكن الإشارة شراء - انتظر تأكيداً")
        
        # نقاط البولينجر
        bb = tf_15m.get("bollinger", {})
        upper = bb.get("upper")
        lower = bb.get("lower")
        
        if upper and lower:
            if signal == "SELL" and price > upper * 0.98:
                tips.append("السعر قرب المقاومة - فرصة بيع مع وقف خسارة محكم")
            elif signal == "BUY" and price < lower * 1.02:
                tips.append("السعر قرب الدعم - فرصة شراء مع وقف خسارة محكم")
        
        # إدارة المخاطر
        if adx and adx > 30:
            tips.append("الزخم قوي - استخدام trailing stop لحماية الأرباح")
        elif adx and adx < 15:
            tips.append("الزخم ضعيف - تأكد من وجود تأكيد إضافي قبل الدخول")
        
        return tips
