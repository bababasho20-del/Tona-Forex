# =====================================================================
# 🧠 market_intelligence.py - المحلل الشامل لتولين
# =====================================================================

import logging
import time
from datetime import datetime
from threading import Thread

# استيراد الدوال من utils.py بدلاً من main.py
from utils import (
    get_mexc_candles,
    calculate_adx_14,
    calculate_rsi_7,
    calculate_atr_14,
    calculate_vpt_supertrend_v5_corrected,
    calculate_vwap
)


class MarketIntelligence:
    """
    المحلل الشامل للسوق.
    يقوم بتحليل النفط والفضة في الخلفية ويولد ملخصاً تنفيذياً محدثاً.
    """
    
    def __init__(self):
        self.intelligence = {
            "oil": {},
            "silver": {},
            "summary": {},
            "last_update": None,
            "market_health": 0,
            "market_status": "neutral"
        }
        self._running = True
        self._update_interval = 300  # 5 دقائق
    
    def start(self):
        """بدء التحليل الدوري في الخلفية"""
        logging.info("🧠 بدء المحلل الشامل (تحديث كل 5 دقائق)")
        Thread(target=self._update_loop, daemon=True).start()
    
    def _update_loop(self):
        """حلقة التحديث الدورية"""
        while self._running:
            try:
                self._update_intelligence()
                time.sleep(self._update_interval)
            except Exception as e:
                logging.error(f"❌ خطأ في تحديث المحلل الشامل: {e}")
                time.sleep(60)
    
    def _update_intelligence(self):
        """تحديث جميع التحليلات"""
        try:
            oil_data = get_mexc_candles("USOIL_USDT", interval="Min15", limit=100)
            silver_data = get_mexc_candles("SILVER_USDT", interval="Min15", limit=100)
            
            if not oil_data or not silver_data:
                logging.warning("⚠️ تعذر جلب بيانات السوق للمحلل الشامل")
                return
            
            oil = self._analyze_asset(oil_data, "oil")
            self.intelligence["oil"] = oil
            
            silver = self._analyze_asset(silver_data, "silver")
            self.intelligence["silver"] = silver
            
            self.intelligence["summary"] = self._generate_summary(oil, silver)
            self.intelligence["last_update"] = datetime.now().isoformat()
            self.intelligence["market_health"] = self._calculate_market_health(oil, silver)
            self.intelligence["market_status"] = self._get_market_status()
            
            logging.info(f"✅ تم تحديث المحلل الشامل - صحة السوق: {self.intelligence['market_health']}/10")
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحديث التحليل: {e}")
    
    def _analyze_asset(self, data, asset_type):
        """تحليل أصل واحد بشكل شامل"""
        closes = data["closes"]
        highs = data["highs"]
        lows = data["lows"]
        volumes = data["volumes"]
        
        if not closes:
            return {}
        
        current_price = closes[-1]
        
        st_multiplier = 2.5 if asset_type == "oil" else 1.5
        st_line_arr, trend = calculate_vpt_supertrend_v5_corrected(data, st_mult=st_multiplier)
        trend_value = trend[-1] if trend else 1
        trend_text = "صاعد" if trend_value == 1 else "هابط" if trend_value == -1 else "عرضي"
        
        rsi = calculate_rsi_7(closes)[-1] if len(closes) > 7 else 50
        adx = calculate_adx_14(data) if data else 15
        atr = calculate_atr_14(data) if data else 0.1
        vwap = calculate_vwap(data)[-1] if data else current_price
        
        current_volume = volumes[-1] if volumes else 0
        avg_volume = sum(volumes[-21:-1]) / 20 if len(volumes) > 20 else current_volume
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        pressure = self._analyze_pressure(rsi, trend_value, adx)
        
        return {
            "price": current_price,
            "trend": trend_text,
            "trend_value": trend_value,
            "supertrend_line": st_line_arr[-1] if st_line_arr else current_price,
            "rsi": round(rsi, 1),
            "adx": round(adx, 1),
            "atr": round(atr, 3),
            "vwap": round(vwap, 2),
            "volume_ratio": round(volume_ratio, 2),
            "current_volume": round(current_volume, 0),
            "avg_volume": round(avg_volume, 0),
            "pressure": pressure,
            "pressure_text": self._get_pressure_text(pressure)
        }
    
    def _analyze_pressure(self, rsi, trend_value, adx):
        if rsi > 70:
            return "شراء قوي (تشبع)"
        elif rsi < 30:
            return "بيع قوي (تشبع)"
        elif rsi > 55 and trend_value == 1:
            return "شراء"
        elif rsi < 45 and trend_value == -1:
            return "بيع"
        else:
            return "محايد"
    
    def _get_pressure_text(self, pressure):
        mapping = {
            "شراء قوي (تشبع)": "🟢 ضغط شراء قوي - احتمال تصحيح",
            "بيع قوي (تشبع)": "🔴 ضغط بيع قوي - احتمال ارتداد",
            "شراء": "📈 ضغط شراء - اتجاه صاعد",
            "بيع": "📉 ضغط بيع - اتجاه هابط",
            "محايد": "🔄 محايد - لا ضغط واضح"
        }
        return mapping.get(pressure, "🔄 محايد")
    
    def _calculate_market_health(self, oil, silver):
        score = 0
        if oil.get("trend_value") == 1:
            score += 2
        if oil.get("adx", 0) > 25:
            score += 1
        if oil.get("volume_ratio", 0) > 1.2:
            score += 1
        if oil.get("rsi", 50) < 70 and oil.get("rsi", 50) > 30:
            score += 0.5
        
        if silver.get("trend_value") == 1:
            score += 2
        if silver.get("adx", 0) > 25:
            score += 1
        if silver.get("volume_ratio", 0) > 1.2:
            score += 1
        if silver.get("rsi", 50) < 70 and silver.get("rsi", 50) > 30:
            score += 0.5
        
        return min(10, round(score, 1))
    
    def _generate_summary(self, oil, silver):
        return f"""
📊 **ملخص السوق - {datetime.now().strftime('%H:%M')}**

🛢️ **النفط:**
• الاتجاه: {oil.get('trend', 'عرضي')}
• الضغط: {oil.get('pressure_text', 'محايد')}
• السعر: {oil.get('price', 0):.2f}$
• ADX: {oil.get('adx', 0)}

🥈 **الفضة:**
• الاتجاه: {silver.get('trend', 'عرضي')}
• الضغط: {silver.get('pressure_text', 'محايد')}
• السعر: {silver.get('price', 0):.3f}$
• ADX: {silver.get('adx', 0)}
"""
    
    def _get_market_status(self):
        health = self.intelligence.get("market_health", 0)
        if health >= 7:
            return "ممتاز 🔥"
        elif health >= 5:
            return "جيد ✅"
        elif health >= 3:
            return "متوسط 🟡"
        else:
            return "ضعيف ❌"
    
    def stop(self):
        self._running = False
        logging.info("🛑 تم إيقاف المحلل الشامل")
