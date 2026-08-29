"""Forex Pattern Discovery
========================
اكتشاف أنماط الصفقات المغلقة مع عزل EUR/USD عن USD/JPY.
لا يعدّ النمط صالحًا إلا بعد حد أدنى من العينات والدعم والارتفاع الإحصائي.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

try:
    from learning_db import normalize_instrument
except ImportError:
    def normalize_instrument(value: Any = "eurusd") -> str:
        key = str(value or "eurusd").lower().replace("/", "")
        if key not in {"eurusd", "usdjpy"}:
            raise ValueError(f"Unsupported Forex instrument: {value}")
        return key

logger = logging.getLogger("TonaPrometheus")

PATTERN_CONFIG = {
    "min_samples": 8,
    "min_win_rate": 0.40,
    "min_support": 0.03,
    "min_lift": 1.15,
    "max_patterns": 100,
}


class PatternDiscovery:
    def __init__(self, learning_db=None, supabase=None, config: Optional[Dict[str, Any]] = None):
        self.learning_db = learning_db
        self.supabase = supabase
        self.config = {**PATTERN_CONFIG, **(config or {})}
        self.patterns: List[Dict[str, Any]] = []
        logger.info("Forex PatternDiscovery initialized")

    @staticmethod
    def _number(value: Any, default: float) -> float:
        try:
            number = float(value)
            return number if number == number else default
        except (TypeError, ValueError):
            return default

    def _extract_context(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        for field in ("context", "indicators", "entry_indicators", "full_entry_analysis", "holistic_entry_analysis"):
            candidate = trade.get(field)
            if isinstance(candidate, dict):
                context.update(candidate)
        nested = context.get("15m") or context.get("Min15") or context.get("timeframes", {}).get("15m", {}) if isinstance(context.get("timeframes", {}), dict) else {}
        if isinstance(nested, dict):
            context.update(nested)
        instrument = trade.get("instrument", trade.get("asset_type", "eurusd"))
        return {
            "instrument": normalize_instrument(instrument),
            "trade_type": str(trade.get("trade_type", trade.get("type", "BUY"))).upper(),
            "rsi": self._number(context.get("rsi", trade.get("entry_rsi", 50)), 50.0),
            "adx": self._number(context.get("adx", trade.get("entry_adx", 20)), 20.0),
            "trend": str(context.get("trend", trade.get("entry_trend", "neutral"))),
            "vol_ratio": self._number(context.get("volume_ratio", context.get("vol_ratio", trade.get("entry_volume_ratio", 1.0))), 1.0),
            "session": str(context.get("session", trade.get("session", "unknown"))),
            "regime": str(context.get("regime", trade.get("market_regime", "unknown"))),
            "spread_pips": self._number(context.get("spread_pips", trade.get("spread_pips", 0.0)), 0.0),
        }

    @staticmethod
    def _net_profit(trade: Dict[str, Any]) -> float:
        value = trade.get("profit_after_cost")
        if value is None:
            value = trade.get("profit_dollars", trade.get("profit", 0.0))
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _classify(self, context: Dict[str, Any]) -> Tuple[str, ...]:
        rsi = context["rsi"]; adx = context["adx"]; vol = context["vol_ratio"]
        rsi_class = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
        adx_class = "strong" if adx >= 25 else "weak"
        vol_class = "high" if vol >= 1.5 else "normal" if vol >= 0.7 else "low"
        direction = "long" if context["trade_type"] == "BUY" else "short"
        return context["instrument"], direction, context["trend"], rsi_class, adx_class, vol_class, context["session"], context["regime"]

    def discover_patterns(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        closed = [t for t in (trades or []) if isinstance(t, dict) and (t.get("exit_time") is not None or t.get("exit_price") is not None)]
        for trade in closed:
            normalize_instrument(trade.get("instrument", trade.get("asset_type", "eurusd")))
        minimum = int(self.config["min_samples"])
        if len(closed) < minimum:
            logger.info("Not enough closed Forex trades: %s/%s", len(closed), minimum)
            return []
        overall_wins = sum(1 for trade in closed if self._net_profit(trade) > 0)
        baseline = overall_wins / len(closed) if closed else 0.0
        groups: Dict[Tuple[str, ...], List[Tuple[Dict[str, Any], Dict[str, Any]]]] = defaultdict(list)
        skipped = 0
        for trade in closed:
            try:
                context = self._extract_context(trade)
                if context["trade_type"] not in {"BUY", "SELL"}:
                    skipped += 1; continue
                groups[self._classify(context)].append((trade, context))
            except (ValueError, TypeError, KeyError):
                skipped += 1
        discovered: List[Dict[str, Any]] = []
        for key, members in groups.items():
            if len(members) < minimum:
                continue
            instrument, direction, trend, rsi_class, adx_class, vol_class, session, regime = key
            wins = sum(1 for trade, _ in members if self._net_profit(trade) > 0)
            win_rate = wins / len(members)
            support = len(members) / len(closed)
            lift = win_rate / baseline if baseline > 0 else 0.0
            if win_rate < float(self.config["min_win_rate"]) or support < float(self.config["min_support"]) or lift < float(self.config["min_lift"]):
                continue
            avg_profit = sum(self._net_profit(trade) for trade, _ in members) / len(members)
            name = f"{instrument}_{direction}_{trend}_{rsi_class}_{adx_class}_{vol_class}_{session}_{regime}"[:120]
            pattern = {
                "pattern_name": name,
                "pattern_type": "forex_entry_pattern",
                "description": f"نمط {instrument} {direction} في جلسة {session} وحالة {regime}",
                "conditions": {"instrument": instrument, "asset_type": instrument, "direction": direction, "trend": trend, "rsi_class": rsi_class, "adx_class": adx_class, "vol_class": vol_class, "session": session, "regime": regime},
                "instrument": instrument, "asset_type": instrument, "session": session, "regime": regime,
                "win_rate": round(win_rate * 100, 2), "sample_count": len(members), "avg_profit": round(avg_profit, 6),
                "support": round(support, 6), "lift": round(lift, 6), "score": round(win_rate * lift * 100, 6),
                "confidence": round(min(1.0, win_rate * min(1.0, len(members) / (minimum * 3))), 6), "is_successful": win_rate > baseline, "is_active": True,
            }
            discovered.append(pattern)
        discovered.sort(key=lambda item: (item["score"], item["sample_count"]), reverse=True)
        discovered = discovered[:int(self.config["max_patterns"])]
        self.patterns = [p for p in self.patterns if p.get("instrument") not in {x.get("instrument") for x in discovered}] + discovered
        for pattern in discovered:
            if self.learning_db and hasattr(self.learning_db, "save_pattern"):
                try:
                    self.learning_db.save_pattern(pattern)
                except Exception as exc:
                    logger.warning("Learning DB pattern save failed: %s", exc)
            if self.supabase and hasattr(self.supabase, "save_patterns"):
                try:
                    self.supabase.save_patterns([pattern])
                except Exception as exc:
                    logger.warning("Supabase pattern save failed: %s", exc)
        logger.info("Discovered %s Forex patterns; skipped %s trades", len(discovered), skipped)
        return discovered

    def get_best_patterns(self, limit: int = 5, instrument: Optional[str] = None) -> List[Dict[str, Any]]:
        key = normalize_instrument(instrument) if instrument else None
        patterns = [p for p in self.patterns if key is None or p.get("instrument") == key]
        return sorted(patterns, key=lambda p: p.get("score", 0), reverse=True)[:max(0, int(limit))]

    def get_pattern_by_name(self, pattern_name: str, instrument: Optional[str] = None) -> Optional[Dict[str, Any]]:
        key = normalize_instrument(instrument) if instrument else None
        return next((p for p in self.patterns if p.get("pattern_name") == pattern_name and (key is None or p.get("instrument") == key)), None)

    def get_patterns(self, instrument: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.get_best_patterns(limit=len(self.patterns), instrument=instrument)
