from pattern_discovery import PatternDiscovery


def trade(instrument, i, profit):
    return {
        "trade_id": f"{instrument}-{i}", "instrument": instrument, "trade_type": "BUY",
        "entry_price": 1.08 if instrument == "eurusd" else 150.0, "exit_price": 1.081 if instrument == "eurusd" else 150.1,
        "exit_time": "2026-01-01T00:00:00Z", "profit_dollars": profit, "profit_after_cost": profit,
        "entry_rsi": 50, "entry_adx": 30, "entry_trend": "up", "session": "london", "market_regime": "trending_up",
        "entry_volume_ratio": 1.0,
    }

engine = PatternDiscovery(config={"min_samples": 4, "min_support": 0.03, "min_lift": 1.0})
trades = [trade("eurusd", i, 1.0 if i < 4 else -1.0) for i in range(8)]
trades += [trade("usdjpy", i, 1.0 if i < 4 else -1.0) for i in range(8)]
patterns = engine.discover_patterns(trades)
assert all(p["instrument"] in {"eurusd", "usdjpy"} for p in patterns)
assert len(engine.get_best_patterns(instrument="eurusd")) >= 1
assert len(engine.get_best_patterns(instrument="usdjpy")) >= 1
try:
    engine.discover_patterns([trade("oil", i, 1.0) for i in range(8)])
except Exception:
    pass
else:
    raise AssertionError("legacy instrument was accepted")
print("pattern_discovery=ok")
