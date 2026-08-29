from advanced_indicators import AdvancedIndicators


def make_data(symbol):
    base = 1.08 if symbol == "eurusd" else 150.0
    step = 0.0001 if symbol == "eurusd" else 0.01
    closes = [base + i * step for i in range(100)]
    return {
        "closes": closes,
        "highs": [x + step * 2 for x in closes],
        "lows": [x - step * 2 for x in closes],
        "volumes": [1000 + i for i in range(100)],
        "timeframe": "Min15",
    }


engine = AdvancedIndicators()
for symbol in ("eurusd", "usdjpy"):
    result = engine.calculate_all(make_data(symbol), symbol)
    assert result["symbol"] in ("EURUSD", "USDJPY")
    assert result["atr"] > 0
    assert 0 <= result["rsi"] <= 100
    assert len(result["atr_series"]) == 100
    assert result["supertrend"]["trend"] in (-1, 1)
    print(symbol, result["symbol"], result["atr"], result["rsi"], result["adx"], result["supertrend"]["trend"])

empty = engine.calculate_all({}, "eurusd")
assert empty["data_quality"]["valid"] is False
assert empty["price"] == 0.0
try:
    engine.calculate_all(make_data("eurusd"), "gold")
except ValueError:
    pass
else:
    raise AssertionError("unsupported instrument was accepted")
print("empty_data=ok")
print("unsupported_instrument=ok")
print("advanced_indicators=ok")
