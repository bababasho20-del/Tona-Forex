from risk_master import RiskMaster


def check(profile, name):
    assert not profile.blocked, f"{name}: unexpectedly blocked"
    assert profile.units > 0, f"{name}: no units"
    assert profile.max_loss_dollars <= 0.51, f"{name}: risk too high: {profile.max_loss_dollars}"
    assert profile.effective_leverage <= 10.000001, f"{name}: effective leverage exceeded"
    print(name, profile.symbol, profile.stop_loss_pips, profile.units, profile.max_loss_dollars, profile.effective_leverage)

master = RiskMaster(initial_capital=100.0, max_leverage=200.0, bot_max_effective_leverage=10.0, default_risk_pct=0.01)
regime = master.detect_regime({
    "instrument": "eurusd",
    "closes": [1.0800 + i * 0.0001 for i in range(100)],
    "highs": [1.0802 + i * 0.0001 for i in range(100)],
    "lows": [1.0798 + i * 0.0001 for i in range(100)],
})
check(master.calculate_risk({"instrument": "eurusd", "price": 1.09, "atr": 0.001, "adx": 30, "trend_strength": 0.9, "spread_pips": 0.8}, regime), "eurusd")
check(master.calculate_risk({"instrument": "usdjpy", "price": 150.0, "atr": 0.15, "adx": 30, "trend_strength": 0.9, "spread_pips": 1.0}, regime), "usdjpy")
blocked = master.calculate_risk({"instrument": "eurusd", "price": 1.09, "atr": 0.001, "spread_pips": 9.0}, regime)
assert blocked.blocked and blocked.notional_value == 0.0
print("wide_spread_block=ok")
master.update_after_trade(profit=1.0)
assert master.get_current_status()["capital"] == 101.0
print("capital_update=ok")
