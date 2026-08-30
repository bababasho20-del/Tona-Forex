"""
📚 Similar Cases Analyzer - تحليل الحالات المشابهة من قاعدة التعلم
👨‍💻 المطور: بسام الحوباني
💙 جزء من نظام تولين الاستشاري
📊 يعتمد على بيانات حقيقية 100%
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("TonaPrometheus")

class SimilarCasesAnalyzer:
    """تحليل الحالات المشابهة من قاعدة التعلم - بيانات حقيقية فقط"""
    
    def __init__(self, learning_db=None):
        self.db = learning_db
        self.cache = {}
    
    def find_similar(self, current_analysis: Dict, signal: str, 
                     asset_type: str = "eurusd", limit: int = 50) -> Optional[Dict]:
        """
        البحث عن حالات مشابهة من قاعدة التعلم الحقيقية
        
        Args:
            current_analysis: تحليل السوق الحالي
            signal: نوع الإشارة (BUY/SELL)
            asset_type: نوع الأصل (oil/silver)
            limit: الحد الأقصى للنتائج
        
        Returns:
            dict: إحصائيات الحالات المشابهة من البيانات الحقيقية
        """
        try:
            from main import load_trades_history
            
            # 1. تحميل تاريخ الصفقات الحقيقي
            history = load_trades_history(asset_type)
            all_trades = history.get('trades', [])
            
            if not all_trades:
                logger.info("ℹ️ لا توجد صفقات مسجلة لـ %s", asset_type)
                return None
            
            # 2. فلترة الصفقات المغلقة
            closed_trades = [t for t in all_trades if t.get('status') == 'closed']
            
            if not closed_trades:
                logger.info("ℹ️ لا توجد صفقات مغلقة لـ %s", asset_type)
                return None
            
            # 3. استخراج ملامح الحالة الحالية
            features = self._extract_features(current_analysis, signal)
            
            # 4. البحث عن صفقات مشابهة
            similar_trades = self._filter_similar_trades(closed_trades, features, limit)
            
            if not similar_trades:
                return {
                    "count": 0,
                    "winning_count": 0,
                    "losing_count": 0,
                    "win_rate": 0,
                    "avg_profit": 0,
                    "max_profit": 0,
                    "max_loss": 0,
                    "avg_duration": 0,
                    "lessons": ["لا توجد صفقات مشابهة في السجل"],
                    "data_source": f"سجل الصفقات ({len(closed_trades)} صفقة)"
                }
            
            # 5. تحليل النتائج
            winning = [t for t in similar_trades if t.get('profit_dollars', 0) > 0]
            losing = [t for t in similar_trades if t.get('profit_dollars', 0) < 0]
            
            # 6. استخلاص الدروس
            lessons = self._extract_real_lessons(similar_trades, winning, losing)
            
            return {
                "count": len(similar_trades),
                "winning_count": len(winning),
                "losing_count": len(losing),
                "win_rate": len(winning) / len(similar_trades) * 100 if similar_trades else 0,
                "avg_profit": sum(t.get('profit_dollars', 0) for t in similar_trades) / len(similar_trades) if similar_trades else 0,
                "max_profit": max((t.get('profit_dollars', 0) for t in similar_trades), default=0),
                "max_loss": min((t.get('profit_dollars', 0) for t in similar_trades), default=0),
                "avg_duration": sum(t.get('duration_minutes', 0) for t in similar_trades) / len(similar_trades) if similar_trades else 0,
                "lessons": lessons[:3],
                "data_source": f"سجل الصفقات ({len(similar_trades)} صفقة مشابهة)"
            }
            
        except Exception as e:
            logger.error(f"❌ فشل البحث عن حالات مشابهة: {e}")
            return None
    
    def _extract_features(self, analysis: Dict, signal: str) -> Dict:
        """استخراج ملامح الحالة الحالية"""
        tf_15m = analysis.get("timeframes", {}).get("15m", {})
        
        return {
            "signal": signal,
            "rsi": tf_15m.get("rsi", 50),
            "adx": tf_15m.get("adx", 15),
            "macd": tf_15m.get("macd", 0),
            "vol_ratio": tf_15m.get("volume_ratio", 1),
            "trend": self._get_trend_summary(analysis)
        }
    
    def _get_trend_summary(self, analysis: Dict) -> str:
        """الحصول على ملخص الاتجاه"""
        timeframes = analysis.get("timeframes", {})
        trends = []
        
        for tf in ["5m", "15m", "1h", "4h"]:
            if tf in timeframes:
                st = timeframes[tf].get("supertrend", {})
                if st:
                    trends.append(st.get("trend", 1))
        
        if not trends:
            return "محايد"
        
        bullish = sum(1 for t in trends if t == 1)
        if bullish >= 3:
            return "صاعد قوي"
        elif bullish >= 2:
            return "صاعد ضعيف"
        elif bullish <= 1:
            return "هابط قوي"
        else:
            return "محايد"
    
    def _filter_similar_trades(self, trades: List[Dict], features: Dict, limit: int) -> List[Dict]:
        """فلترة الصفقات المشابهة بناءً على الملامح"""
        similar = []
        
        for trade in trades:
            # نفس الإشارة
            if trade.get('type') != features['signal']:
                continue
            
            # RSI قريب
            trade_rsi = trade.get('entry_rsi', 50)
            if abs(trade_rsi - features['rsi']) > 20:
                continue
            
            # ADX قريب
            trade_adx = trade.get('entry_adx', 15)
            if abs(trade_adx - features['adx']) > 15:
                continue
            
            similar.append(trade)
        
        # ترتيب حسب الأكثر تشابهاً (أقرب RSI)
        similar.sort(key=lambda t: abs(t.get('entry_rsi', 50) - features['rsi']))
        
        return similar[:limit]
    
    def _extract_real_lessons(self, trades: List[Dict], winning: List[Dict], losing: List[Dict]) -> List[str]:
        """استخلاص الدروس من البيانات الحقيقية"""
        lessons = []
        
        if len(trades) < 5:
            return ["عدد الصفقات المشابهة قليل (أقل من 5) - لا توجد دروس كافية"]
        
        # تحليل أسباب النجاح
        if winning and len(winning) >= 3:
            avg_rsi = sum(t.get('entry_rsi', 50) for t in winning) / len(winning)
            avg_adx = sum(t.get('entry_adx', 15) for t in winning) / len(winning)
            
            if 30 < avg_rsi < 50:
                lessons.append(f"✅ RSI كان في منطقة {avg_rsi:.0f} (مثالي)")
            if avg_adx > 25:
                lessons.append(f"✅ ADX كان قوياً ({avg_adx:.0f})")
        
        # تحليل أسباب الفشل
        if losing and len(losing) >= 3:
            avg_rsi = sum(t.get('entry_rsi', 50) for t in losing) / len(losing)
            avg_adx = sum(t.get('entry_adx', 15) for t in losing) / len(losing)
            
            if avg_rsi > 65 or avg_rsi < 35:
                lessons.append(f"⚠️ RSI كان {avg_rsi:.0f} (قيم متطرفة)")
            if avg_adx < 20:
                lessons.append(f"⚠️ ADX كان ضعيفاً ({avg_adx:.0f})")
        
        return lessons if lessons else ["لا توجد دروس واضحة من الصفقات المشابهة"]
