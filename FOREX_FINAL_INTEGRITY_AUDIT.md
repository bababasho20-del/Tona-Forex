# Tona Forex – Final Integrity Audit

- Signal scanner: every 60 seconds.
- Signal timeframe: Min5.
- Analysis timeframes: Min5, Min15, Min60, Hour4.
- Canonical market data provider: Twelve Data.
- Instruments: EUR/USD and USD/JPY only.
- Trading mode: virtual/simulation.
- EUR/USD SuperTrend: period 50, multiplier 2.2, VPT length 10.
- USD/JPY SuperTrend: period 60, multiplier 2.5, VPT length 10.
- One closed candle confirmation.
- Learning/AI layers remain advisory and do not alter the SuperTrend/VPT entry engine.

Cold start: when there is no Forex history, the learning layer does not query legacy oil/silver data and reports learned probability/model confidence as unavailable until real Forex outcomes exist.

Validation:
- All Python files: py_compile PASS
- test_learning_db.py: PASS
- test_advanced_indicators.py: PASS
- test_market_analyzer.py: PASS
- test_pattern_discovery.py: PASS
- test_risk_master.py: PASS
- healthcheck.py: PASS

External services require Render environment variables and cannot be fully exercised offline.
