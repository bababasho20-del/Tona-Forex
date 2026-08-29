"""Forex Market Analyzer
=====================
محلل فني مستقل لـ EUR/USD و USD/JPY.
لا يجلب البيانات بنفسه؛ يستقبل سلسلة شموع موحّدة من طبقة البيانات.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple


INSTRUMENTS = {
    "eurusd": {"symbol": "EURUSD", "display": "EUR/USD", "pip_size": 0.0001, "digits": 5, "max_spread_pips": 1.5},
    "usdjpy": {"symbol": "USDJPY", "display": "USD/JPY", "pip_size": 0.01, "digits": 3, "max_spread_pips": 2.0},
}


def _instrument(value: Any) -> Dict[str, Any]:
    key = str(value or "eurusd").lower().replace("/", "")
    aliases = {"eur_usd": "eurusd", "eurusd=x": "eurusd", "usd_jpy": "usdjpy", "jpy=x": "usdjpy"}
    key = aliases.get(key, key)
    if key not in INSTRUMENTS:
        raise ValueError(f"Unsupported Forex instrument: {value}")
    return {"key": key, **INSTRUMENTS[key]}


def _floats(values: Iterable[Any]) -> List[float]:
    result = []
    for value in values or []:
        try:
            number = float(value)
            if math.isfinite(number):
                result.append(number)
        except (TypeError, ValueError):
            continue
    return result


@dataclass
class AnalysisResult:
    instrument: str
    symbol: str
    timeframe: str
    price: float
    rsi: float
    macd: Dict[str, float]
    adx: float
    atr: float
    vpt: float
    vpt_slope: float
    supertrend: Dict[str, Any]
    bollinger: Dict[str, float]
    vwap: float
    volume_ratio: float
    spread_pips: float
    trend: str
    regime: str
    recommendation: str
    data_quality: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        value = asdict(self)
        # مفاتيح توافق مع المحركات القديمة.
        value["indicators"] = {
            "rsi": self.rsi,
            "macd": self.macd,
            "adx": self.adx,
            "atr": self.atr,
            "vpt": self.vpt,
            "vpt_slope": self.vpt_slope,
            "volume_ratio": self.volume_ratio,
        }
        value["market_context"] = {
            "instrument": self.instrument,
            "symbol": self.symbol,
            "trend": self.trend,
            "regime": self.regime,
            "recommendation": self.recommendation,
            "spread_pips": self.spread_pips,
            "timeframe": self.timeframe,
        }
        return value


class MarketAnalyzer:
    """محلل لا يعتمد على أصل بعينه، لكنه يقبل زوجي الفوركس المحددين فقط."""

    def __init__(self, default_timeframe: str = "Min15", min_bars: int = 60,
                 supertrend_period: int = 10, supertrend_multiplier: float = 2.5):
        self.default_timeframe = default_timeframe
        self.min_bars = max(30, int(min_bars))
        self.supertrend_period = max(2, int(supertrend_period))
        self.supertrend_multiplier = max(0.5, float(supertrend_multiplier))
        self.last_results: Dict[str, Dict[str, Any]] = {}

    def analyze(self, data: Dict[str, Any], instrument: str = "eurusd",
                timeframe: Optional[str] = None, spread_pips: Optional[float] = None) -> Dict[str, Any]:
        spec = _instrument(instrument)
        closes, highs, lows, volumes, quality = self._normalize_data(data)
        tf = timeframe or (data or {}).get("timeframe") or self.default_timeframe
        if len(closes) < self.min_bars:
            return self._insufficient(spec, tf, len(closes), quality)

        spread = float(spread_pips if spread_pips is not None else (data or {}).get("spread_pips", 0.0) or 0.0)
        atr = self._atr(highs, lows, closes, 14)
        rsi = self._rsi(closes, 14)
        macd = self._macd(closes)
        adx, di_direction = self._adx(highs, lows, closes, 14)
        st_line, st_direction = self._supertrend(highs, lows, closes, self.supertrend_period, self.supertrend_multiplier)
        bb = self._bollinger(closes, 20, 2.0)
        vpt_series = self._vpt(closes, volumes)
        vpt = vpt_series[-1] if vpt_series else 0.0
        vpt_slope = self._slope(vpt_series, 5)
        vwap = self._session_vwap(data, highs, lows, closes, volumes)
        volume_ratio = self._volume_ratio(volumes, 20)
        price = closes[-1]

        if st_direction > 0 and di_direction > 0:
            trend = "up"
        elif st_direction < 0 and di_direction < 0:
            trend = "down"
        else:
            trend = "neutral"
        regime, recommendation = self._regime(adx, atr, closes, trend, spread, spec["max_spread_pips"])
        quality.update({"bars": len(closes), "spread_ok": spread <= spec["max_spread_pips"] if spread > 0 else True})
        result = AnalysisResult(
            instrument=spec["key"], symbol=spec["symbol"], timeframe=str(tf), price=price,
            rsi=rsi, macd=macd, adx=adx, atr=atr, vpt=vpt, vpt_slope=vpt_slope,
            supertrend={"line": st_line, "trend": st_direction, "multiplier": self.supertrend_multiplier},
            bollinger=bb, vwap=vwap, volume_ratio=volume_ratio, spread_pips=spread,
            trend=trend, regime=regime, recommendation=recommendation, data_quality=quality,
        ).to_dict()
        self.last_results[spec["key"]] = result
        return result

    def analyze_market(self, data: Dict[str, Any], instrument: str = "eurusd", **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(data, instrument=instrument, **kwargs)

    def get_analysis(self, data: Dict[str, Any], instrument: str = "eurusd", **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(data, instrument=instrument, **kwargs)

    def get_market_context(self, data: Dict[str, Any], instrument: str = "eurusd", **kwargs: Any) -> Dict[str, Any]:
        return self.analyze(data, instrument=instrument, **kwargs).get("market_context", {})

    def _normalize_data(self, data: Dict[str, Any]) -> Tuple[List[float], List[float], List[float], List[float], Dict[str, Any]]:
        data = data or {}
        closes = _floats(data.get("closes", data.get("close", [])))
        highs = _floats(data.get("highs", data.get("high", [])))
        lows = _floats(data.get("lows", data.get("low", [])))
        volumes = _floats(data.get("volumes", data.get("volume", [])))
        n = min(len(closes), len(highs), len(lows))
        quality = {"valid": True, "removed_non_finite": False, "aligned": len({len(closes), len(highs), len(lows)}) == 1}
        if n == 0:
            return [], [], [], [], {"valid": False, "reason": "no_ohlc"}
        closes, highs, lows = closes[-n:], highs[-n:], lows[-n:]
        if len(volumes) != n:
            volumes = (volumes[-n:] if len(volumes) >= n else [0.0] * (n - len(volumes)) + volumes)
            quality["volume_fallback"] = True
        if any(h < l or c <= 0 for h, l, c in zip(highs, lows, closes)):
            quality.update({"valid": False, "reason": "invalid_ohlc"})
        return closes, highs, lows, volumes, quality

    def _insufficient(self, spec: Dict[str, Any], timeframe: str, bars: int, quality: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "instrument": spec["key"], "symbol": spec["symbol"], "timeframe": str(timeframe), "price": 0.0,
            "rsi": 50.0, "macd": {"macd_line": 0.0, "signal_line": 0.0, "histogram": 0.0}, "adx": 0.0,
            "atr": 0.0, "vpt": 0.0, "vpt_slope": 0.0, "supertrend": {"line": 0.0, "trend": 0},
            "bollinger": {"upper": 0.0, "middle": 0.0, "lower": 0.0}, "vwap": 0.0, "volume_ratio": 1.0,
            "spread_pips": 0.0, "trend": "unknown", "regime": "unknown", "recommendation": "avoid",
            "data_quality": {**quality, "valid": False, "bars": bars, "reason": "insufficient_bars"},
            "indicators": {}, "market_context": {"instrument": spec["key"], "symbol": spec["symbol"], "regime": "unknown"},
        }

    @staticmethod
    def _atr(highs: List[float], lows: List[float], closes: List[float], period: int) -> float:
        if len(closes) < 2:
            return 0.0
        trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(1, len(closes))]
        return sum(trs[-period:]) / min(period, len(trs)) if trs else 0.0

    @staticmethod
    def _ema(values: List[float], period: int) -> List[float]:
        if not values:
            return []
        alpha = 2.0 / (period + 1.0)
        result = [values[0]]
        for value in values[1:]:
            result.append(alpha * value + (1.0 - alpha) * result[-1])
        return result

    def _rsi(self, closes: List[float], period: int) -> float:
        if len(closes) <= period:
            return 50.0
        gains, losses = [], []
        for a, b in zip(closes[-period - 1:-1], closes[-period:]):
            change = b - a
            gains.append(max(change, 0.0)); losses.append(max(-change, 0.0))
        avg_gain, avg_loss = sum(gains) / period, sum(losses) / period
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        return max(0.0, min(100.0, 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)))

    def _macd(self, closes: List[float]) -> Dict[str, float]:
        fast, slow, signal = self._ema(closes, 12), self._ema(closes, 26), 9
        macd_series = [a - b for a, b in zip(fast[-len(slow):], slow)]
        signal_series = self._ema(macd_series, signal)
        line = macd_series[-1] if macd_series else 0.0
        sig = signal_series[-1] if signal_series else 0.0
        return {"macd_line": line, "signal_line": sig, "histogram": line - sig}

    def _adx(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> Tuple[float, int]:
        if len(closes) < period * 2 + 1:
            return 0.0, 0
        tr, plus, minus = [], [], []
        for i in range(1, len(closes)):
            tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
            up, down = highs[i] - highs[i - 1], lows[i - 1] - lows[i]
            plus.append(up if up > down and up > 0 else 0.0); minus.append(down if down > up and down > 0 else 0.0)
        values = []
        for end in range(period, len(tr) + 1):
            total = sum(tr[end - period:end])
            pdi = 100.0 * sum(plus[end - period:end]) / total if total else 0.0
            mdi = 100.0 * sum(minus[end - period:end]) / total if total else 0.0
            values.append(100.0 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi else 0.0)
        adx = sum(values[-period:]) / min(period, len(values)) if values else 0.0
        direction = 1 if sum(plus[-period:]) > sum(minus[-period:]) else -1 if sum(minus[-period:]) > sum(plus[-period:]) else 0
        return max(0.0, min(100.0, adx)), direction

    def _supertrend(self, highs: List[float], lows: List[float], closes: List[float], period: int, multiplier: float) -> Tuple[float, int]:
        if not closes:
            return 0.0, 0
        atr = self._atr(highs, lows, closes, period)
        mid = (highs[-1] + lows[-1]) / 2.0
        upper, lower = mid + multiplier * atr, mid - multiplier * atr
        return (lower, 1) if closes[-1] >= mid else (upper, -1)

    @staticmethod
    def _bollinger(closes: List[float], period: int, deviations: float) -> Dict[str, float]:
        window = closes[-period:]
        mean = sum(window) / len(window) if window else 0.0
        std = math.sqrt(sum((x - mean) ** 2 for x in window) / len(window)) if window else 0.0
        return {"upper": mean + deviations * std, "middle": mean, "lower": mean - deviations * std, "width": (2 * deviations * std / mean if mean else 0.0)}

    @staticmethod
    def _vpt(closes: List[float], volumes: List[float]) -> List[float]:
        result, total = [], 0.0
        for i, close in enumerate(closes):
            if i > 0 and closes[i - 1] != 0:
                total += ((close - closes[i - 1]) / closes[i - 1]) * (volumes[i] if i < len(volumes) else 0.0)
            result.append(total)
        return result

    @staticmethod
    def _slope(values: List[float], period: int) -> float:
        if len(values) < 2:
            return 0.0
        window = values[-period:]
        return (window[-1] - window[0]) / max(1, len(window) - 1)

    @staticmethod
    def _volume_ratio(volumes: List[float], period: int) -> float:
        if not volumes:
            return 1.0
        baseline = volumes[-period - 1:-1]
        avg = sum(baseline) / len(baseline) if baseline else 0.0
        return volumes[-1] / avg if avg > 0 else 1.0

    @staticmethod
    def _session_vwap(data: Dict[str, Any], highs: List[float], lows: List[float], closes: List[float], volumes: List[float]) -> float:
        typical = [(h + l + c) / 3.0 for h, l, c in zip(highs, lows, closes)]
        total_volume = sum(max(0.0, v) for v in volumes)
        if total_volume <= 0:
            return typical[-1] if typical else 0.0
        return sum(p * max(0.0, v) for p, v in zip(typical, volumes)) / total_volume

    @staticmethod
    def _regime(adx: float, atr: float, closes: List[float], trend: str, spread: float, max_spread: float) -> Tuple[str, str]:
        if spread > max_spread > 0:
            return "execution_blocked", "avoid"
        mean = sum(closes[-20:]) / min(20, len(closes))
        width = (max(closes[-20:]) - min(closes[-20:])) / mean if mean else 0.0
        if adx >= 25 and trend in ("up", "down"):
            return ("trending_up" if trend == "up" else "trending_down"), "trade"
        if width < 0.004 or adx < 18:
            return "ranging", "caution"
        if atr > 0 and width > 0.02:
            return "volatile", "avoid"
        return "transitional", "caution"


# أسماء توافقية محتملة مع المحركات القديمة.
ForexMarketAnalyzer = MarketAnalyzer
