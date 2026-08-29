"""
🧠 Trade Post-Mortem - تحليل ما بعد الصفقة (رابحة وخاسرة)
👨‍💻 المطور: بسام الحوباني
💙 جزء من نظام تولين الاستشاري والتعلمي

📊 الوظيفة:
- تحليل شامل للصفقات المغلقة (رابحة وخاسرة)
- استخدام جميع المؤشرات الفنية (وليس فقط 3 منها)
- استخلاص الدروس من النجاح والفشل
- تقديم توصيات للتحسين
- تسجيل في نظام التعلم
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("TonaPrometheus")

class TradePostMortem:
    """
    تحليل ما بعد الصفقة - التعلم من كل صفقة (ربح أو خسارة)
    """
    
    def __init__(self, learning_db=None):
        self.learning_db = learning_db
        self.analysis_history = []
        self.max_history = 100
        
        logger.info("🧠 Trade Post-Mortem: جاهز للتحليل!")
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 التحليل الرئيسي
    # ═══════════════════════════════════════════════════════════════════════
    
    def analyze(self, trade_data: Dict) -> Dict:
        """
        تحليل شامل للصفقة (رابحة أو خاسرة)
        
        Args:
            trade_data: بيانات الصفقة كاملة من close_trade_virtual()
            
        Returns:
            Dict: التحليل الكامل مع الدروس والتوصيات
        """
        try:
            # ── 1. استخراج البيانات ──
            profit = trade_data.get('profit_dollars', 0)
            is_win = profit > 0
            
            # ── 2. تحليل شامل للمؤشرات ──
            indicators_analysis = self._analyze_all_indicators(trade_data)
            
            # ── 3. تحليل إدارة المخاطر ──
            risk_analysis = self._analyze_risk_management(trade_data)
            
            # ── 4. تحليل التوقيت ──
            timing_analysis = self._analyze_timing(trade_data)
            
            # ── 5. تحليل الفريمات ──
            timeframe_analysis = self._analyze_timeframes(trade_data)
            
            # ── 6. تحليل المشاعر ──
            sentiment_analysis = self._analyze_sentiment(trade_data)
            
            # ── 7. استخلاص الدروس ──
            lessons = self._extract_lessons(
                trade_data, 
                indicators_analysis, 
                risk_analysis,
                timing_analysis,
                timeframe_analysis,
                is_win
            )
            
            # ── 8. توصيات للتحسين ──
            recommendations = self._get_recommendations(
                trade_data,
                indicators_analysis,
                risk_analysis,
                timing_analysis,
                timeframe_analysis,
                is_win
            )
            
            # ── 9. تقييم الصفقة ──
            grade = self._calculate_grade(trade_data, is_win)
            
            # ── 10. حفظ التحليل ──
            analysis_result = {
                "trade_id": trade_data.get('trade_id', ''),
                "timestamp": datetime.now().isoformat(),
                "is_win": is_win,
                "profit": profit,
                "indicators": indicators_analysis,
                "risk": risk_analysis,
                "timing": timing_analysis,
                "timeframes": timeframe_analysis,
                "sentiment": sentiment_analysis,
                "lessons": lessons,
                "recommendations": recommendations,
                "grade": grade
            }
            
            self.analysis_history.append(analysis_result)
            if len(self.analysis_history) > self.max_history:
                self.analysis_history = self.analysis_history[-self.max_history:]
            
            # ── 11. تسجيل في قاعدة التعلم ──
            self._save_to_learning(analysis_result, trade_data)
            
            # ── 12. تحديث إحصائيات الملف ──
            self._update_stats(analysis_result)
            
            return {
                "grade": grade,
                "lessons": lessons,
                "recommendations": recommendations,
                "analysis": analysis_result,
                "is_win": is_win
            }
            
        except Exception as e:
            logger.error(f"❌ فشل تحليل ما بعد الصفقة: {e}")
            return {
                "grade": "فشل التحليل",
                "lessons": ["حدث خطأ في التحليل"],
                "recommendations": ["تحقق من بيانات الصفقة"],
                "analysis": {},
                "is_win": False
            }
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تحليل المؤشرات الفنية (كلها)
    # ═══════════════════════════════════════════════════════════════════════
    
    def _analyze_all_indicators(self, trade_data: Dict) -> Dict:
        """تحليل جميع المؤشرات الفنية"""
        
        entry_indicators = trade_data.get('entry_indicators', {})
        
        return {
            # ── مؤشرات الاتجاه ──
            "trend": {
                "supertrend": entry_indicators.get('trend', 'محايد'),
                "adx": entry_indicators.get('adx', 15),
                "trend_strength": self._get_trend_strength(entry_indicators.get('adx', 15)),
                "vpt": entry_indicators.get('vpt', 0),
                "st_line": entry_indicators.get('st_line', 0)
            },
            
            # ── مؤشرات الزخم ──
            "momentum": {
                "rsi": entry_indicators.get('rsi', 50),
                "rsi_zone": self._get_rsi_zone(entry_indicators.get('rsi', 50)),
                "macd": entry_indicators.get('macd', 0),
                "macd_signal": self._get_macd_signal(entry_indicators.get('macd', 0)),
                "stochastic": trade_data.get('stochastic', 50)
            },
            
            # ── مؤشرات التقلب ──
            "volatility": {
                "atr": trade_data.get('atr', 0.5),
                "bb_position": trade_data.get('bb_position', 0.5),
                "bb_width": trade_data.get('bb_width', 0.1),
                "volatility_level": self._get_volatility_level(trade_data.get('atr', 0.5))
            },
            
            # ── مؤشرات الحجم ──
            "volume": {
                "volume_ratio": trade_data.get('volume_ratio', 1.0),
                "volume_confirmation": trade_data.get('volume_ratio', 1.0) > 1.2
            },
            
            # ── مؤشرات السعر ──
            "price": {
                "entry": trade_data.get('entry_price', 0),
                "exit": trade_data.get('exit_price', 0),
                "sl": trade_data.get('sl_price', 0),
                "tp": trade_data.get('tp_price', 0),
                "rr": trade_data.get('rr', 1.0)
            }
        }
    
    def _get_trend_strength(self, adx: float) -> str:
        """تقييم قوة الاتجاه من ADX"""
        if adx >= 40:
            return "قوي جداً"
        elif adx >= 30:
            return "قوي"
        elif adx >= 25:
            return "جيد"
        elif adx >= 20:
            return "متوسط"
        else:
            return "ضعيف"
    
    def _get_rsi_zone(self, rsi: float) -> str:
        """تحديد منطقة RSI"""
        if rsi >= 80:
            return "ذروة شراء شديدة"
        elif rsi >= 70:
            return "ذروة شراء"
        elif rsi >= 60:
            return "مرتفع"
        elif rsi >= 40:
            return "محايد"
        elif rsi >= 30:
            return "منخفض"
        elif rsi >= 20:
            return "ذروة بيع"
        else:
            return "ذروة بيع شديدة"
    
    def _get_macd_signal(self, macd: float) -> str:
        """تحديد إشارة MACD"""
        if macd > 0.5:
            return "إيجابي قوي"
        elif macd > 0:
            return "إيجابي"
        elif macd > -0.5:
            return "سلبي"
        else:
            return "سلبي قوي"
    
    def _get_volatility_level(self, atr: float) -> str:
        """تحديد مستوى التقلب"""
        if atr > 1.5:
            return "مرتفع جداً"
        elif atr > 1.0:
            return "مرتفع"
        elif atr > 0.5:
            return "متوسط"
        else:
            return "منخفض"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تحليل إدارة المخاطر
    # ═══════════════════════════════════════════════════════════════════════
    
    def _analyze_risk_management(self, trade_data: Dict) -> Dict:
        """تحليل إدارة المخاطر"""
        entry = trade_data.get('entry_price', 0)
        sl = trade_data.get('sl_price', 0)
        tp = trade_data.get('tp_price', 0)
        rr = trade_data.get('rr', 1.0)
        
        if entry > 0 and sl > 0:
            sl_distance_pct = abs((entry - sl) / entry * 100)
        else:
            sl_distance_pct = 0
        
        if entry > 0 and tp > 0:
            tp_distance_pct = abs((tp - entry) / entry * 100)
        else:
            tp_distance_pct = 0
        
        return {
            "sl_distance_pct": sl_distance_pct,
            "tp_distance_pct": tp_distance_pct,
            "rr": rr,
            "rr_quality": self._get_rr_quality(rr),
            "risk_level": self._get_risk_level(sl_distance_pct)
        }
    
    def _get_rr_quality(self, rr: float) -> str:
        """تقييم جودة نسبة المخاطرة/المكافأة"""
        if rr >= 3.0:
            return "ممتاز"
        elif rr >= 2.0:
            return "جيد"
        elif rr >= 1.5:
            return "مقبول"
        elif rr >= 1.0:
            return "منخفض"
        else:
            return "سيء"
    
    def _get_risk_level(self, sl_distance_pct: float) -> str:
        """تقييم مستوى المخاطرة"""
        if sl_distance_pct > 2.0:
            return "مرتفع"
        elif sl_distance_pct > 1.0:
            return "متوسط"
        elif sl_distance_pct > 0.5:
            return "منخفض"
        else:
            return "منخفض جداً"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تحليل التوقيت
    # ═══════════════════════════════════════════════════════════════════════
    
    def _analyze_timing(self, trade_data: Dict) -> Dict:
        """تحليل توقيت الصفقة"""
        duration_minutes = trade_data.get('duration_minutes', 0)
        entry_time = trade_data.get('entry_time', '')
        exit_time = trade_data.get('exit_time', '')
        exit_reason = trade_data.get('exit_reason', 'غير معروف')
        
        return {
            "duration_minutes": duration_minutes,
            "duration_text": self._format_duration(duration_minutes),
            "entry_time": entry_time,
            "exit_time": exit_time,
            "exit_reason": exit_reason,
            "timing_quality": self._get_timing_quality(duration_minutes, exit_reason)
        }
    
    def _format_duration(self, minutes: int) -> str:
        """تنسيق مدة الصفقة"""
        if minutes < 60:
            return f"{minutes} دقيقة"
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} ساعة"
        return f"{hours} ساعة و {mins} دقيقة"
    
    def _get_timing_quality(self, duration_minutes: int, exit_reason: str) -> str:
        """تقييم جودة التوقيت"""
        if exit_reason == "Hit Take Profit":
            if duration_minutes < 60:
                return "ممتاز - هدف سريع"
            elif duration_minutes < 180:
                return "جيد - هدف في وقت معقول"
            else:
                return "مقبول - هدف بعد وقت طويل"
        elif exit_reason == "Hit Stop Loss":
            if duration_minutes < 30:
                return "سيء - ضرب SL بسرعة"
            else:
                return "ضعيف - ضرب SL بعد وقت"
        else:
            return "طبيعي"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تحليل الفريمات
    # ═══════════════════════════════════════════════════════════════════════
    
    def _analyze_timeframes(self, trade_data: Dict) -> Dict:
        """تحليل توافق الفريمات"""
        timeframes = trade_data.get('timeframes', {})
        
        trends = {}
        for tf in ['5m', '15m', '1h', '4h']:
            if tf in timeframes:
                st = timeframes[tf].get('supertrend', {})
                if st:
                    trends[tf] = st.get('trend', 1)
        
        if not trends:
            return {
                "trends": {},
                "confluence": "غير معروف",
                "bullish_count": 0,
                "bearish_count": 0,
                "total": 0
            }
        
        bullish_count = sum(1 for t in trends.values() if t == 1)
        bearish_count = sum(1 for t in trends.values() if t == -1)
        total = len(trends)
        
        return {
            "trends": trends,
            "confluence": self._get_confluence(bullish_count, bearish_count, total),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "total": total
        }
    
    def _get_confluence(self, bullish: int, bearish: int, total: int) -> str:
        """تقييم توافق الفريمات"""
        if total == 0:
            return "غير معروف"
        
        if bullish >= total - 1:
            return "صاعد قوي (جميع الفريمات صاعدة)"
        elif bearish >= total - 1:
            return "هابط قوي (جميع الفريمات هابطة)"
        elif bullish > bearish:
            return "صاعد ضعيف (غالبية الفريمات صاعدة)"
        elif bearish > bullish:
            return "هابط ضعيف (غالبية الفريمات هابطة)"
        else:
            return "متعارض (فريمات متضاربة)"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تحليل المشاعر
    # ═══════════════════════════════════════════════════════════════════════
    
    def _analyze_sentiment(self, trade_data: Dict) -> Dict:
        """تحليل المشاعر"""
        fear_greed = trade_data.get('fear_greed', 50)
        
        return {
            "fear_greed": fear_greed,
            "fear_greed_text": self._get_fear_greed_text(fear_greed),
            "sentiment": trade_data.get('sentiment', 'neutral')
        }
    
    def _get_fear_greed_text(self, value: float) -> str:
        """تقييم مؤشر الخوف والجشع"""
        if value >= 80:
            return "طمع شديد (خطر قمة)"
        elif value >= 70:
            return "طمع (تفاؤل مفرط)"
        elif value >= 60:
            return "تفاؤل"
        elif value >= 40:
            return "محايد"
        elif value >= 30:
            return "خوف"
        elif value >= 20:
            return "خوف (تشاؤم)"
        else:
            return "خوف شديد (فرصة قاع)"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📚 استخلاص الدروس
    # ═══════════════════════════════════════════════════════════════════════
    
    def _extract_lessons(self, trade_data: Dict, indicators: Dict, 
                         risk: Dict, timing: Dict, timeframes: Dict, is_win: bool) -> List[str]:
        """استخلاص الدروس من الصفقة"""
        lessons = []
        
        if is_win:
            lessons.extend(self._extract_win_lessons(trade_data, indicators, risk, timing, timeframes))
        else:
            lessons.extend(self._extract_loss_lessons(trade_data, indicators, risk, timing, timeframes))
        
        return lessons[:5]  # حد أقصى 5 دروس
    
    def _extract_win_lessons(self, trade_data: Dict, indicators: Dict,
                             risk: Dict, timing: Dict, timeframes: Dict) -> List[str]:
        """دروس من صفقة رابحة"""
        lessons = []
        
        # 1. المؤشرات
        rsi = indicators.get('momentum', {}).get('rsi', 50)
        rsi_zone = indicators.get('momentum', {}).get('rsi_zone', '')
        adx = indicators.get('trend', {}).get('adx', 15)
        
        if rsi < 30:
            lessons.append(f"✅ الشراء عند RSI منخفض ({rsi:.0f}) كان صحيحاً")
        elif rsi > 70:
            lessons.append(f"✅ البيع عند RSI مرتفع ({rsi:.0f}) كان صحيحاً")
        
        if adx > 25:
            lessons.append(f"✅ الاتجاه القوي (ADX: {adx:.0f}) ساعد في تحقيق الربح")
        
        # 2. نسبة المخاطرة/المكافأة
        rr = risk.get('rr', 1.0)
        if rr >= 2.0:
            lessons.append(f"✅ نسبة المخاطرة/المكافأة الجيدة (1:{rr:.1f}) ساعدت في الربح")
        
        # 3. توافق الفريمات
        confluence = timeframes.get('confluence', '')
        if 'جميع' in confluence:
            lessons.append(f"✅ توافق الفريمات ({confluence}) عزز الثقة")
        
        # 4. التوقيت
        timing_quality = timing.get('timing_quality', '')
        if 'ممتاز' in timing_quality:
            lessons.append(f"✅ التوقيت كان ممتازاً - الهدف تحقق بسرعة")
        
        if not lessons:
            lessons.append("✅ الصفقة كانت ناجحة، استمر في تطبيق نفس الاستراتيجية")
        
        return lessons
    
    def _extract_loss_lessons(self, trade_data: Dict, indicators: Dict,
                              risk: Dict, timing: Dict, timeframes: Dict) -> List[str]:
        """دروس من صفقة خاسرة"""
        lessons = []
        
        # 1. المؤشرات
        rsi = indicators.get('momentum', {}).get('rsi', 50)
        rsi_zone = indicators.get('momentum', {}).get('rsi_zone', '')
        adx = indicators.get('trend', {}).get('adx', 15)
        macd = indicators.get('momentum', {}).get('macd', 0)
        
        if rsi > 70 and trade_data.get('type') == 'BUY':
            lessons.append(f"🔴 تم الشراء عند RSI مرتفع ({rsi:.0f}) - منطقة ذروة شراء")
        elif rsi < 30 and trade_data.get('type') == 'SELL':
            lessons.append(f"🔴 تم البيع عند RSI منخفض ({rsi:.0f}) - منطقة ذروة بيع")
        
        if adx < 20:
            lessons.append(f"🔴 ADX ضعيف ({adx:.0f}) - الاتجاه غير واضح")
        
        if macd < 0 and trade_data.get('type') == 'BUY':
            lessons.append("🔴 MACD سلبي مع صفقة شراء - تناقض في الزخم")
        elif macd > 0 and trade_data.get('type') == 'SELL':
            lessons.append("🔴 MACD إيجابي مع صفقة بيع - تناقض في الزخم")
        
        # 2. نسبة المخاطرة/المكافأة
        rr = risk.get('rr', 1.0)
        if rr < 1.5:
            lessons.append(f"🔴 نسبة المخاطرة/المكافأة منخفضة (1:{rr:.1f})")
        
        # 3. توافق الفريمات
        confluence = timeframes.get('confluence', '')
        if 'متضارب' in confluence or 'متعارض' in confluence:
            lessons.append(f"🔴 فريمات متضاربة - لم يكن هناك توافق")
        
        # 4. إدارة المخاطر
        sl_distance = risk.get('sl_distance_pct', 0)
        if sl_distance < 0.5:
            lessons.append(f"🔴 وقف الخسارة كان قريباً جداً ({sl_distance:.1f}%)")
        
        # 5. التوقيت
        exit_reason = timing.get('exit_reason', '')
        if 'Stop Loss' in exit_reason:
            lessons.append("🔴 تم ضرب وقف الخسارة - راجع مسافة وقف الخسارة")
        
        if not lessons:
            lessons.append("🔴 خسارة غير واضحة - يوصى بمراجعة جميع المؤشرات")
        
        return lessons
    
    # ═══════════════════════════════════════════════════════════════════════
    # 💡 توصيات للتحسين
    # ═══════════════════════════════════════════════════════════════════════
    
    def _get_recommendations(self, trade_data: Dict, indicators: Dict,
                             risk: Dict, timing: Dict, timeframes: Dict, is_win: bool) -> List[str]:
        """توليد توصيات للتحسين"""
        recommendations = []
        
        if is_win:
            recommendations.extend(self._get_win_recommendations(trade_data, indicators, risk))
        else:
            recommendations.extend(self._get_loss_recommendations(trade_data, indicators, risk, timeframes))
        
        return recommendations[:4]  # حد أقصى 4 توصيات
    
    def _get_win_recommendations(self, trade_data: Dict, indicators: Dict, risk: Dict) -> List[str]:
        """توصيات لتعزيز النجاح"""
        recs = []
        rsi = indicators.get('momentum', {}).get('rsi', 50)
        adx = indicators.get('trend', {}).get('adx', 15)
        rr = risk.get('rr', 1.0)
        
        if rsi < 30:
            recs.append("📌 استمر في استخدام RSI كفلتر للشراء عند مناطق التشبع البيعي")
        elif rsi > 70:
            recs.append("📌 استمر في استخدام RSI كفلتر للبيع عند مناطق التشبع الشرائي")
        
        if adx > 25:
            recs.append("📌 استمر في استخدام ADX لتأكيد قوة الاتجاه")
        
        if rr >= 2.0:
            recs.append("📌 حافظ على نسبة المخاطرة/المكافأة 1:2 على الأقل")
        
        if len(recs) < 2:
            recs.append("📌 استمر في تطبيق نفس الاستراتيجية الناجحة")
            recs.append("📌 راجع نقاط القوة في هذه الصفقة لتطبيقها مستقبلاً")
        
        return recs
    
    def _get_loss_recommendations(self, trade_data: Dict, indicators: Dict, 
                                  risk: Dict, timeframes: Dict) -> List[str]:
        """توصيات لتجنب الخسارة مستقبلاً"""
        recs = []
        rsi = indicators.get('momentum', {}).get('rsi', 50)
        adx = indicators.get('trend', {}).get('adx', 15)
        macd = indicators.get('momentum', {}).get('macd', 0)
        rr = risk.get('rr', 1.0)
        
        if rsi > 70 and trade_data.get('type') == 'BUY':
            recs.append("📌 تجنب الشراء عندما يكون RSI > 70 (ذروة شراء)")
        elif rsi < 30 and trade_data.get('type') == 'SELL':
            recs.append("📌 تجنب البيع عندما يكون RSI < 30 (ذروة بيع)")
        
        if adx < 20:
            recs.append("📌 تجنب الدخول عندما يكون ADX < 20 (ضعف الاتجاه)")
        
        if macd < 0 and trade_data.get('type') == 'BUY':
            recs.append("📌 تأكد من توافق MACD مع اتجاه الصفقة")
        elif macd > 0 and trade_data.get('type') == 'SELL':
            recs.append("📌 تأكد من توافق MACD مع اتجاه الصفقة")
        
        if rr < 1.5:
            recs.append("📌 استخدم نسبة مخاطرة/مكافأة لا تقل عن 1:2")
        
        sl_distance = risk.get('sl_distance_pct', 0)
        if sl_distance < 0.5:
            recs.append(f"📌 زيادة مسافة وقف الخسارة ({sl_distance:.1f}% → 1.5%)")
        
        confluence = timeframes.get('confluence', '')
        if 'متضارب' in confluence or 'متعارض' in confluence:
            recs.append("📌 انتظر توافق الفريمات قبل الدخول")
        
        if len(recs) < 2:
            recs.append("📌 راجع جميع المؤشرات قبل الدخول")
            recs.append("📌 استخدم وقف خسارة أوسع في الصفقات القادمة")
        
        return recs
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 تقييم الصفقة
    # ═══════════════════════════════════════════════════════════════════════
    
    def _calculate_grade(self, trade_data: Dict, is_win: bool) -> str:
        """تقييم الصفقة"""
        if is_win:
            profit = trade_data.get('profit_dollars', 0)
            if profit > 50:
                return "ممتازة 🏆"
            elif profit > 20:
                return "جيدة ✅"
            else:
                return "مقبولة 🟡"
        else:
            loss = abs(trade_data.get('profit_dollars', 0))
            if loss > 30:
                return "سيئة 🔴"
            elif loss > 15:
                return "متوسطة 🟠"
            else:
                return "خفيفة 🟡"
    
    # ═══════════════════════════════════════════════════════════════════════
    # 💾 التسجيل في قاعدة التعلم
    # ═══════════════════════════════════════════════════════════════════════
    
    def _save_to_learning(self, analysis: Dict, trade_data: Dict):
        """حفظ التحليل في قاعدة التعلم"""
        try:
            if self.learning_db:
                if hasattr(self.learning_db, 'save_post_mortem'):
                    self.learning_db.save_post_mortem(analysis)
                    logger.info("💾 تم حفظ تحليل ما بعد الصفقة في قاعدة التعلم")
        except Exception as e:
            logger.error(f"❌ فشل حفظ التحليل: {e}")
    
    def _update_stats(self, analysis: Dict):
        """تحديث إحصائيات الملف"""
        # يمكن تتبع عدد الصفقات المحللة وأنواعها
        pass
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 واجهات عامة
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ التحليلات"""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    def get_summary_stats(self) -> Dict:
        """إحصائيات ملخصة للتحليلات"""
        if not self.analysis_history:
            return {
                "total_analyzed": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0
            }
        
        wins = sum(1 for a in self.analysis_history if a.get('is_win', False))
        total = len(self.analysis_history)
        
        return {
            "total_analyzed": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": (wins / total * 100) if total > 0 else 0
        }
    
    def get_lessons_summary(self) -> Dict[str, List[str]]:
        """ملخص الدروس المستفادة"""
        win_lessons = []
        loss_lessons = []
        
        for analysis in self.analysis_history:
            if analysis.get('is_win', False):
                win_lessons.extend(analysis.get('lessons', []))
            else:
                loss_lessons.extend(analysis.get('lessons', []))
        
        return {
            "win_lessons": list(set(win_lessons))[:5],
            "loss_lessons": list(set(loss_lessons))[:5]
        }


# ═══════════════════════════════════════════════════════════════════════
# 🔧 دالة مساعدة للاستخدام السريع
# ═══════════════════════════════════════════════════════════════════════

def create_post_mortem(learning_db=None) -> TradePostMortem:
    """إنشاء كائن تحليل ما بعد الصفقة"""
    return TradePostMortem(learning_db=learning_db)


# ═══════════════════════════════════════════════════════════════════════
# 🧪 اختبار سريع
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 اختبار Trade Post-Mortem")
    print("=" * 60)
    
    post_mortem = TradePostMortem()
    
    # بيانات صفقة خاسرة
    loss_trade = {
        "trade_id": "test_loss_001",
        "type": "BUY",
        "entry_price": 78.50,
        "exit_price": 77.80,
        "profit_dollars": -14.00,
        "sl_price": 77.80,
        "tp_price": 80.00,
        "rr": 1.5,
        "duration_minutes": 120,
        "exit_reason": "Hit Stop Loss",
        "entry_indicators": {
            "rsi": 72,
            "adx": 22,
            "macd": 0.01,
            "trend": "صاعد",
            "vpt": 1.2,
            "st_line": 78.00
        },
        "volume_ratio": 0.8,
        "atr": 0.5,
        "bb_position": 0.85,
        "bb_width": 0.1,
        "stochastic": 85,
        "fear_greed": 75
    }
    
    # بيانات صفقة رابحة
    win_trade = {
        "trade_id": "test_win_001",
        "type": "BUY",
        "entry_price": 78.50,
        "exit_price": 79.80,
        "profit_dollars": 26.00,
        "sl_price": 77.50,
        "tp_price": 80.00,
        "rr": 2.5,
        "duration_minutes": 90,
        "exit_reason": "Hit Take Profit",
        "entry_indicators": {
            "rsi": 35,
            "adx": 28,
            "macd": 0.02,
            "trend": "صاعد",
            "vpt": 1.5,
            "st_line": 78.00
        },
        "volume_ratio": 1.6,
        "atr": 0.5,
        "bb_position": 0.35,
        "bb_width": 0.1,
        "stochastic": 25,
        "fear_greed": 45
    }
    
    # تحليل الصفقة الخاسرة
    print("\n1️⃣ تحليل صفقة خاسرة:")
    result = post_mortem.analyze(loss_trade)
    print(f"   التقييم: {result['grade']}")
    print("   الدروس:")
    for lesson in result['lessons']:
        print(f"      • {lesson}")
    print("   التوصيات:")
    for rec in result['recommendations']:
        print(f"      • {rec}")
    
    # تحليل الصفقة الرابحة
    print("\n2️⃣ تحليل صفقة رابحة:")
    result = post_mortem.analyze(win_trade)
    print(f"   التقييم: {result['grade']}")
    print("   الدروس:")
    for lesson in result['lessons']:
        print(f"      • {lesson}")
    print("   التوصيات:")
    for rec in result['recommendations']:
        print(f"      • {rec}")
    
    print("\n✅ اختبار Trade Post-Mortem ناجح!")
