"""
🧠 Confidence Scorer - نظام حساب درجة الثقة للتوصيات
👨‍💻 المطور: بسام الحوباني
💙 جزء من نظام تولين الاستشاري
📊 يعتمد على بيانات حقيقية 100% مع تحليل التوافق
"""

import math
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("TonaPrometheus")

class ConfidenceScorer:
    """نظام حساب درجة الثقة للتوصيات من بيانات حقيقية مع تحليل التوافق"""
    
    def __init__(self):
        self.weight_factors = {
            "trend_alignment": 0.25,      # توافق الإشارة مع الفريمات
            "volume_confirmation": 0.15,   # تأكيد الحجم
            "momentum_strength": 0.15,     # قوة الزخم
            "timeframe_confluence": 0.20,  # توافق الفريمات مع بعضها
            "historical_accuracy": 0.15,   # الدقة التاريخية
            "risk_reward_ratio": 0.10      # نسبة المخاطرة/المكافأة
        }
        
        self.thresholds = {
            "excellent": 0.85,
            "good": 0.70,
            "average": 0.55,
            "fair": 0.40
        }
    
    def calculate(self, analysis: Dict, signal: str, trade_context: Dict, asset_type: str = "eurusd") -> Dict:
        """حساب درجة الثقة الكاملة من بيانات حقيقية مع تحليل التوافق"""
        scores = {}
        
        # ✅ 1. توافق الإشارة مع الفريمات (محسّن)
        scores["trend_alignment"] = self._score_trend_alignment(analysis, signal)
        
        # 2. تأكيد الحجم
        scores["volume_confirmation"] = self._score_volume(analysis)
        
        # 3. قوة الزخم
        scores["momentum_strength"] = self._score_momentum(analysis, signal)
        
        # 4. توافق الفريمات مع بعضها
        scores["timeframe_confluence"] = self._score_timeframe_confluence(analysis, signal)
        
        # 5. الدقة التاريخية - بيانات حقيقية
        scores["historical_accuracy"] = self._score_historical_accuracy(signal, analysis, asset_type)
        
        # 6. نسبة المخاطرة/المكافأة
        scores["risk_reward_ratio"] = self._score_rr_ratio(trade_context)
        
        # حساب المتوسط المرجح
        total = 0
        for factor, weight in self.weight_factors.items():
            if factor in scores:
                total += scores[factor] * weight
        
        total = min(1.0, max(0.0, total))
        
        # ✅ خفض الثقة إذا كان هناك تناقض حاد
        if signal in ["BUY", "SELL"]:
            timeframes = analysis.get("timeframes", {})
            trends = []
            for tf in ["5m", "15m", "1h", "4h"]:
                st = timeframes.get(tf, {}).get("supertrend", {})
                if st:
                    trends.append(st.get("trend", 1))
            
            if trends:
                bullish_count = sum(1 for t in trends if t == 1)
                total_tf = len(trends)
                
                if signal == "SELL" and bullish_count / total_tf > 0.5:
                    total *= 0.6  # خفض 40%
                elif signal == "BUY" and (total_tf - bullish_count) / total_tf > 0.5:
                    total *= 0.6  # خفض 40%
        
        return {
            "total": total * 100,
            "factors": scores,
            "grade": self._get_grade(total),
            "emoji": self._get_emoji(total),
            "breakdown": self._get_breakdown(scores)
        }
    
    # ✅ الدالة المحسنة - تقييم توافق الإشارة مع الفريمات
    def _score_trend_alignment(self, analysis: Dict, signal: str) -> float:
        """تقييم توافق الإشارة مع الفريمات"""
        timeframes = analysis.get("timeframes", {})
        trends = []
        
        for tf in ["5m", "15m", "1h", "4h"]:
            if tf in timeframes:
                st = timeframes[tf].get("supertrend", {})
                if st:
                    trends.append(st.get("trend", 1))
        
        if not trends:
            return 0.5
        
        bullish_count = sum(1 for t in trends if t == 1)
        total = len(trends)
        
        if signal == "SELL":
            # نريد فريمات هابطة
            bearish_count = total - bullish_count
            ratio = bearish_count / total
            return min(1.0, ratio + 0.1)
        elif signal == "BUY":
            # نريد فريمات صاعدة
            ratio = bullish_count / total
            return min(1.0, ratio + 0.1)
        else:  # WAIT
            return 0.5
    
    def _score_volume(self, analysis: Dict) -> float:
        """تقييم تأكيد الحجم"""
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        vol_ratio = tf_15m.get("volume_ratio", 1.0)
        
        if vol_ratio >= 2.0:
            return 1.0
        elif vol_ratio >= 1.5:
            return 0.85
        elif vol_ratio >= 1.0:
            return 0.6
        elif vol_ratio >= 0.5:
            return 0.3
        else:
            return 0.1
    
    def _score_momentum(self, analysis: Dict, signal: str) -> float:
        """تقييم قوة الزخم"""
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        adx = tf_15m.get("adx", 15)
        macd = tf_15m.get("macd", 0)
        
        # تقييم ADX
        if adx >= 40:
            adx_score = 1.0
        elif adx >= 30:
            adx_score = 0.85
        elif adx >= 25:
            adx_score = 0.7
        elif adx >= 20:
            adx_score = 0.5
        else:
            adx_score = 0.3
        
        # تقييم MACD مع الإشارة
        if signal == "SELL":
            macd_score = 1.0 if macd < -0.5 else 0.7 if macd < 0 else 0.3
        elif signal == "BUY":
            macd_score = 1.0 if macd > 0.5 else 0.7 if macd > 0 else 0.3
        else:
            macd_score = 0.5
        
        return (adx_score * 0.6) + (macd_score * 0.4)
    
    def _score_timeframe_confluence(self, analysis: Dict, signal: str) -> float:
        """تقييم توافق الفريمات مع بعضها"""
        timeframes = analysis.get("timeframes", {})
        trends = []
        
        for tf_name, tf_data in timeframes.items():
            st = tf_data.get("supertrend", {})
            if st:
                trends.append(st.get("trend", 1))
        
        if not trends:
            return 0.5
        
        # مدى توافق الفريمات مع بعضها
        bullish_count = sum(1 for t in trends if t == 1)
        total = len(trends)
        
        # كلما كانت الفريمات متوافقة أكثر، زادت الدرجة
        alignment = max(bullish_count, total - bullish_count) / total
        return alignment
    
    def _score_historical_accuracy(self, signal: str, analysis: Dict, asset_type: str) -> float:
        """تقييم الدقة التاريخية من البيانات الحقيقية"""
        try:
            from main import load_trades_history
            
            history = load_trades_history(asset_type)
            all_trades = history.get('trades', [])
            
            if not all_trades:
                return 0.5
            
            closed_trades = [t for t in all_trades if t.get('status') == 'closed']
            
            if not closed_trades:
                return 0.5
            
            signal_trades = [t for t in closed_trades if t.get('type') == signal]
            
            if not signal_trades:
                winning = [t for t in closed_trades if t.get('profit_dollars', 0) > 0]
                win_rate = len(winning) / len(closed_trades) if closed_trades else 0
                return min(1.0, win_rate + 0.1)
            
            winning = [t for t in signal_trades if t.get('profit_dollars', 0) > 0]
            win_rate = len(winning) / len(signal_trades) if signal_trades else 0
            
            return min(1.0, win_rate + 0.1)
            
        except Exception as e:
            logger.error(f"❌ فشل حساب الدقة التاريخية: {e}")
            return 0.5
    
    def _score_rr_ratio(self, trade_context: Dict) -> float:
        """تقييم نسبة المخاطرة/المكافأة"""
        rr = trade_context.get("rr", 1.0)
        
        if rr >= 4.0:
            return 1.0
        elif rr >= 3.0:
            return 0.9
        elif rr >= 2.0:
            return 0.75
        elif rr >= 1.5:
            return 0.6
        elif rr >= 1.0:
            return 0.4
        else:
            return 0.2
    
    def _get_grade(self, score: float) -> str:
        """تحديد الدرجة النصية"""
        if score >= self.thresholds["excellent"]:
            return "ممتازة"
        elif score >= self.thresholds["good"]:
            return "جيدة جداً"
        elif score >= self.thresholds["average"]:
            return "جيدة"
        elif score >= self.thresholds["fair"]:
            return "متوسطة"
        else:
            return "ضعيفة"
    
    def _get_emoji(self, score: float) -> str:
        """تحديد الإيموجي المناسب"""
        if score >= self.thresholds["excellent"]:
            return "🔥"
        elif score >= self.thresholds["good"]:
            return "✅"
        elif score >= self.thresholds["average"]:
            return "📊"
        elif score >= self.thresholds["fair"]:
            return "⚠️"
        else:
            return "🔴"
    
    def _get_breakdown(self, scores: Dict) -> Dict:
        """تفصيل النقاط"""
        breakdown = {}
        for factor, score in scores.items():
            if score >= 0.8:
                breakdown[factor] = "ممتاز"
            elif score >= 0.6:
                breakdown[factor] = "جيد"
            elif score >= 0.4:
                breakdown[factor] = "متوسط"
            else:
                breakdown[factor] = "ضعيف"
        return breakdown
