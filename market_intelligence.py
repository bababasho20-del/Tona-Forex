# -*- coding: utf-8 -*-
"""Forex market intelligence worker. Uses the canonical provider from main.py."""
import logging, time
from datetime import datetime
from threading import Thread

class MarketIntelligence:
    """Background 5-minute intelligence for EUR/USD and USD/JPY only."""
    def __init__(self):
        self.intelligence = {"eurusd": {}, "usdjpy": {}, "summary": {}, "last_update": None,
                             "market_health": 0, "market_status": "neutral"}
        self._running = True
        self._update_interval = 300

    def start(self):
        logging.info("🧠 بدء المحلل الشامل للفوركس (تحديث كل 5 دقائق)")
        Thread(target=self._update_loop, daemon=True).start()

    def _update_loop(self):
        while self._running:
            try:
                self._update_intelligence()
                time.sleep(self._update_interval)
            except Exception as e:
                logging.error("❌ خطأ في تحديث المحلل الشامل: %s", e)
                time.sleep(self._update_interval)

    def _update_intelligence(self):
        try:
            from main import get_forex_candles
            data = {}
            for asset, symbol in (("eurusd", "EURUSD"), ("usdjpy", "USDJPY")):
                candles = get_forex_candles(symbol, "Min15", 150)
                if candles:
                    data[asset] = self._analyze_asset(candles, asset)
                    self.intelligence[asset] = data[asset]
            if data:
                self.intelligence["summary"] = self._generate_summary(data)
                self.intelligence["last_update"] = datetime.now().isoformat()
                self.intelligence["market_health"] = self._calculate_market_health(data)
                self.intelligence["market_status"] = self._get_market_status()
                logging.info("✅ تم تحديث محلل الفوركس - صحة السوق: %s/10", self.intelligence["market_health"])
        except Exception as e:
            logging.error("❌ خطأ في تحديث تحليل الفوركس: %s", e)

    def _analyze_asset(self, data, asset_type):
        from main import calculate_adx_14, calculate_rsi_7, calculate_atr_14, calculate_vpt_supertrend_v5_corrected, calculate_vwap
        closes, volumes = data["closes"], data.get("volumes", [])
        if not closes: return {}
        price = closes[-1]
        cfg = {"eurusd": (2.2, 50), "usdjpy": (2.5, 60)}[asset_type]
        st, trend = calculate_vpt_supertrend_v5_corrected(data, st_mult=cfg[0], st_period=cfg[1])
        tv = trend[-1] if trend else 0
        rsi = calculate_rsi_7(closes)[-1] if len(closes) > 7 else 50
        adx = calculate_adx_14(data) if data else 15
        atr = calculate_atr_14(data) if data else 0
        vwap_arr = calculate_vwap(data) if data else [price]
        vwap = vwap_arr[-1] if vwap_arr else price
        curvol = volumes[-1] if volumes else 0
        avg = sum(volumes[-21:-1]) / 20 if len(volumes) > 20 else curvol
        ratio = curvol / avg if avg > 0 else 1
        return {"price":price,"trend":"صاعد" if tv==1 else "هابط" if tv==-1 else "عرضي",
                "trend_value":tv,"supertrend_line":st[-1] if st else price,"rsi":round(rsi,1),
                "adx":round(adx,1),"atr":atr,"vwap":vwap,"volume_ratio":round(ratio,2)}

    def _calculate_market_health(self, data):
        score = 0
        for a in data.values():
            if a.get("trend_value") == 1: score += 2
            if a.get("adx",0) > 25: score += 1
            if 30 < a.get("rsi",50) < 70: score += .5
        return min(10, round(score,1))

    def _generate_summary(self, data):
        parts = [f"📊 **ملخص سوق الفوركس - {datetime.now().strftime('%H:%M')}**"]
        for asset in ("eurusd","usdjpy"):
            a=data.get(asset,{})
            if a: parts.append(f"• {asset.upper()}: {a.get('trend','عرضي')} | RSI {a.get('rsi',0)} | ADX {a.get('adx',0)}")
        return "\n".join(parts)

    def _get_market_status(self):
        h=self.intelligence.get("market_health",0)
        return "ممتاز 🔥" if h>=7 else "جيد ✅" if h>=5 else "متوسط 🟡" if h>=3 else "ضعيف ❌"

    def stop(self):
        self._running=False
        logging.info("🛑 تم إيقاف محلل الفوركس")
