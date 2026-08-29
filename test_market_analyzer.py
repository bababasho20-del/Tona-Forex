from market_analyzer import MarketAnalyzer


def make_data(instrument):
    if instrument == "eurusd":
        closes = [1.0800 + i * 0.0001 for i in range(100)]
    else:
        closes = [150.0 + i * 0.01 for i in range(100)]
    return {
        "closes": closes,
        "highs": [x + (0.0002 if instrument == "eurusd" else 0.02) for x in closes],
        "lows": [x - (0.0002 if instrument == "eurusd" else 0.02) for x in closes],
        "volumes": [1000.0 + i for i in range(100)],
        "timeframe": "Min15",
    }

analyzer = MarketAnalyzer(min_bars=60)
for instrument in ("eurusd", "usdjpy"):
    result = analyzer.analyze(make_data(instrument), instrument=instrument, spread_pips=0.8)
    assert result["symbol"] in ("EURUSD", "USDJPY")
    assert result["data_quality"]["valid"] is True
    assert result["atr"] > 0
    assert 0 <= result["rsi"] <= 100
    assert result["supertrend"]["trend"] in (-1, 1)
    print(instrument, result["symbol"], result["price"], result["atr"], result["trend"], result["regime"])

short = analyzer.analyze({"closes": [1.0] * 10, "highs": [1.0] * 10, "lows": [1.0] * 10}, "eurusd")
assert short["recommendation"] == "avoid"
print("insufficient_data=ok")
