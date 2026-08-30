# Tona Forex — EUR/USD وUSD/JPY

نسخة Forex مستقلة للمحاكاة والتعلم، وتدعم زوجي EUR/USD وUSD/JPY فقط.

- Scanner: Min5 كل 60 ثانية.
- HealthCheck: كل 300 ثانية.
- Monitoring: كل 300 ثانية.
- التحليل الشامل: 5m / 15m / 1h / 4h.
- Data provider: Twelve Data أولاً.
- Yahoo fallback غير مفعّل افتراضياً.
- لا يوجد تنفيذ صفقات حقيقية.

## إعدادات SuperTrend/VPT
- EUR/USD: period 50 / multiplier 2.2 / VPT 10.
- USD/JPY: period 60 / multiplier 2.5 / VPT 10.
- Base timeframe: Min5.

ضع `TWELVE_DATA_API_KEY` في Environment Variables في منصة التشغيل.
