# =====================================================================
# 📊 market_analyzer_advanced.py - المحلل المتقدم باستخدام ta
# =====================================================================

import pandas as pd
import numpy as np
import logging
from datetime import datetime

# استيراد المكتبات
try:
    import ta
    from ta import add_all_ta_features
    from ta.volatility import AverageTrueRange
    from ta.trend import MACD, ADXIndicator, EMAIndicator
    from ta.momentum import RSIIndicator
    from ta.volume import VolumeWeightedAveragePrice
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    logging.warning("⚠️ مكتبة ta غير مثبتة. قم بتشغيل: pip install ta pandas")

class MarketAnalyzerAdvanced:
    """
    محلل متقدم يستخدم مكتبة ta لاستخراج الدعم والمقاومة والمؤشرات.
    """
    
    def __init__(self):
        self.data = None
        self.support_levels = []
        self.resistance_levels = []
        self.last_update = None
        self.current_price = 0
        
        if not TA_AVAILABLE:
            logging.error("❌ مكتبة ta غير متوفرة. لن يعمل المحلل المتقدم.")
    
    def load_data(self, closes, highs, lows, volumes):
        """تحميل البيانات في DataFrame وتحليلها"""
        if not TA_AVAILABLE:
            return False
        
        if len(closes) < 30:
            logging.warning("⚠️ البيانات غير كافية للتحليل (تحتاج 30 شمعة على الأقل)")
            return False
        
        try:
            self.data = pd.DataFrame({
                'close': closes,
                'high': highs,
                'low': lows,
                'volume': volumes
            })
            
            self.current_price = closes[-1]
            self._calculate_indicators()
            self._find_support_resistance()
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحميل البيانات: {e}")
            return False
    
    def _calculate_indicators(self):
        """حساب جميع المؤشرات باستخدام ta"""
        if self.data is None or len(self.data) < 30:
            return
        
        try:
            # إضافة جميع المؤشرات الأساسية
            self.data = add_all_ta_features(
                self.data,
                open="close",
                high="high",
                low="low",
                close="close",
                volume="volume",
                fillna=True
            )
            
            # إضافة مؤشرات إضافية
            self.data['rsi'] = RSIIndicator(self.data['close'], window=14).rsi()
            self.data['adx'] = ADXIndicator(
                self.data['high'], 
                self.data['low'], 
                self.data['close'], 
                window=14
            ).adx()
            self.data['atr'] = AverageTrueRange(
                self.data['high'], 
                self.data['low'], 
                self.data['close'], 
                window=14
            ).average_true_range()
            self.data['macd'] = MACD(self.data['close']).macd()
            self.data['vwap'] = VolumeWeightedAveragePrice(
                self.data['high'],
                self.data['low'],
                self.data['close'],
                self.data['volume']
            ).volume_weighted_average_price()
            
        except Exception as e:
            logging.error(f"❌ خطأ في حساب المؤشرات: {e}")
    
    def _find_support_resistance(self, window=20, threshold=0.02):
        """
        اكتشاف مناطق الدعم والمقاومة باستخدام القمم والقيعان.
        """
        if self.data is None or len(self.data) < window:
            return
        
        highs = self.data['high'].values
        lows = self.data['low'].values
        closes = self.data['close'].values
        
        # البحث عن القمم (Resistance)
        resistance = []
        for i in range(window, len(highs) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                is_duplicate = False
                for r in resistance:
                    if abs(r - highs[i]) / r < threshold:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    resistance.append(highs[i])
        
        # البحث عن القيعان (Support)
        support = []
        for i in range(window, len(lows) - window):
            if lows[i] == min(lows[i-window:i+window+1]):
                is_duplicate = False
                for s in support:
                    if abs(s - lows[i]) / s < threshold:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    support.append(lows[i])
        
        # ترتيب وتحديث
        self.resistance_levels = sorted(resistance, reverse=True)[:5]
        self.support_levels = sorted(support)[:5]
    
    def get_support_resistance(self):
        """استرجاع مناطق الدعم والمقاومة"""
        return {
            "support": self.support_levels,
            "resistance": self.resistance_levels
        }
    
    def get_nearest_levels(self, current_price=None):
        """أقرب مناطق الدعم والمقاومة للسعر الحالي"""
        if current_price is None:
            current_price = self.current_price
        
        nearest_support = None
        nearest_resistance = None
        
        for s in self.support_levels:
            if s < current_price:
                if nearest_support is None or s > nearest_support:
                    nearest_support = s
        
        for r in self.resistance_levels:
            if r > current_price:
                if nearest_resistance is None or r < nearest_resistance:
                    nearest_resistance = r
        
        return {
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance
        }
    
    def get_current_indicators(self):
        """استرجاع المؤشرات الحالية"""
        if self.data is None or len(self.data) == 0:
            return {}
        
        latest = self.data.iloc[-1]
        return {
            "rsi": float(latest.get('rsi', 50)),
            "adx": float(latest.get('adx', 15)),
            "atr": float(latest.get('atr', 0.1)),
            "macd": float(latest.get('macd', 0)),
            "vwap": float(latest.get('vwap', latest.get('close', 0))),
            "close": float(latest.get('close', 0))
        }
    
    def analyze_price_position(self, current_price=None):
        """تحليل موقع السعر بالنسبة للدعم والمقاومة"""
        if current_price is None:
            current_price = self.current_price
        
        levels = self.get_nearest_levels(current_price)
        support = levels.get("nearest_support")
        resistance = levels.get("nearest_resistance")
        
        analysis = ""
        if support and resistance:
            distance_to_support = ((current_price - support) / current_price) * 100
            distance_to_resistance = ((resistance - current_price) / current_price) * 100
            
            if distance_to_support < 1:
                analysis = f"🟢 السعر **قريب جداً من الدعم** ({support:.2f})، احتمال ارتداد."
            elif distance_to_resistance < 1:
                analysis = f"🔴 السعر **قريب جداً من المقاومة** ({resistance:.2f})، احتمال اختراق أو تراجع."
            elif distance_to_support < distance_to_resistance:
                analysis = f"🟡 السعر **أقرب إلى الدعم** ({support:.2f}) منه إلى المقاومة ({resistance:.2f})."
            else:
                analysis = f"🟡 السعر **أقرب إلى المقاومة** ({resistance:.2f}) منه إلى الدعم ({support:.2f})."
        else:
            analysis = "⚠️ لا توجد مناطق دعم أو مقاومة واضحة حالياً."
        
        return {
            "support": support,
            "resistance": resistance,
            "analysis": analysis,
            "distance_to_support": f"{distance_to_support:.2f}%" if support else None,
            "distance_to_resistance": f"{distance_to_resistance:.2f}%" if resistance else None
        }
    
    def get_detailed_report(self, current_price=None):
        """تقرير مفصل عن السوق"""
        if current_price is None:
            current_price = self.current_price
        
        indicators = self.get_current_indicators()
        levels = self.get_support_resistance()
        position = self.analyze_price_position(current_price)
        
        if not indicators:
            return "⚠️ لا توجد بيانات كافية للتحليل."
        
        report = f"""
📊 **تحليل السوق المتقدم**
⏰ آخر تحديث: {self.last_update.strftime('%H:%M') if self.last_update else 'غير محدث'}

💰 **السعر الحالي:** {current_price:.2f}$

📈 **المؤشرات الفنية:**
• RSI: {indicators.get('rsi', 50):.1f}
• ADX: {indicators.get('adx', 15):.1f}
• ATR: {indicators.get('atr', 0.1):.3f}
• MACD: {indicators.get('macd', 0):.4f}
• VWAP: {indicators.get('vwap', 0):.2f}

📊 **مناطق الدعم والمقاومة:**
• **الدعم:** {', '.join([f'{s:.2f}' for s in levels.get('support', [])]) if levels.get('support') else 'غير محدد'}
• **المقاومة:** {', '.join([f'{r:.2f}' for r in levels.get('resistance', [])]) if levels.get('resistance') else 'غير محدد'}

📍 **موقع السعر:**
{position.get('analysis', 'لا يوجد تحليل')}

📌 **الخلاصة:**
• قوة الاتجاه (ADX): {'قوي ⚡' if indicators.get('adx', 0) > 25 else 'ضعيف ❌' if indicators.get('adx', 0) < 20 else 'متوسط 🟡'}
• الزخم (RSI): {'تشبع شراء 🔴' if indicators.get('rsi', 50) > 70 else 'تشبع بيع 🟢' if indicators.get('rsi', 50) < 30 else 'طبيعي'}
"""
        return report
