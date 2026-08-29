import tempfile
from pathlib import Path
from learning_db import LearningDatabase

with tempfile.TemporaryDirectory() as tmp:
    db = LearningDatabase(str(Path(tmp) / "forex_learning.db"))
    assert db.save_trade_full({"trade_id": "e1", "instrument": "eurusd", "trade_type": "BUY", "entry_price": 1.08, "exit_price": 1.081, "profit_dollars": 1.0, "profit_after_cost": 0.9})
    assert db.save_trade_full({"trade_id": "j1", "asset_type": "usdjpy", "trade_type": "SELL", "entry_price": 150.0, "exit_price": 149.9, "profit_dollars": 0.8})
    assert len(db.get_trades_by_asset("eurusd")) == 1
    assert len(db.get_trades_by_asset("usdjpy")) == 1
    assert db.get_statistics("eurusd")["total_trades"] == 1
    assert db.get_statistics("usdjpy")["total_trades"] == 1
    assert db.save_pattern({"instrument": "eurusd", "pattern_name": "trend_a", "conditions": {"adx": 30}, "sample_count": 10})
    assert db.save_pattern({"instrument": "usdjpy", "pattern_name": "trend_a", "conditions": {"adx": 25}, "sample_count": 12})
    assert len(db.get_patterns("eurusd")) == 1
    assert len(db.get_patterns("usdjpy")) == 1
    assert db.save_snapshot({"trade_id": "e1", "instrument": "eurusd", "price": 1.08})
    assert db.save_lesson({"instrument": "usdjpy", "lesson_text": "اختبار", "importance": 0.7})
    try:
        db.get_statistics("oil")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported instrument accepted")
    print("learning_db=ok")
