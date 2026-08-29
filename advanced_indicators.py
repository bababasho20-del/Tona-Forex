"""Advanced Forex Indicators
==========================
طبقة مؤشرات مستقلة لـ EUR/USD و USD/JPY.
تستقبل OHLCV وتعيد سلاسل كاملة وآخر قيمة، ولا تجلب البيانات أو تنفّذ الصفقات.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

INSTRUMENTS = {
    "eurusd": {"symbol": "EURUSD", "pip_size": 0.0001, "digits": 5},
    "usdjpy": {"symbol": "USDJPY", "pip_size": 0.01, "digits": 3},
}


def _key(value: Any) -> str:
    key = str(value or "eurusd").lower().replace("/", "")
    key = {"eur_usd": "eurusd", "usd_jpy": "usdjpy", "jpy=x": "usdjpy", "eurusd=x": "eurusd"}.get(key, key)
    if key not in INSTRUMENTS:
        raise ValueError(f"Unsupported Forex instrument: {value}")
    return key


def _series(values: Iterable[Any]) -> List[float]:
    out = []
    for value in values or []:
        try:
            number = float(value)
            out.append(number if math.isfinite(number) else 0.0)
        except (TypeError, ValueError):
            out.append(0.0)
    return out


def _ema(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    period = max(1, int(period))
    alpha = 2.0 / (period + 1.0)
    result = [values[0]]
    for value in values[1:]:
        result.append(alpha * value + (1.0 - alpha) * result[-1])
    return result


def _sma(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    period = max(1, int(period))
    result = []
    for i in range(len(values)):
        window = values[max(0, i - period + 1):i + 1]
        result.append(sum(window) / len(window))
    return result


class AdvancedIndicators:
    """مؤشرات حتمية، خالية من الآثار الجانبية، مناسبة للباك تست والمحاكاة."""

    def __init__(self, default_instrument: str = "eurusd", default_timeframe: str = "Min15"):
        self.default_instrument = _key(default_instrument)
        self.default_timeframe = default_timeframe

    def calculate_all(self, data: Dict[str, Any], instrument: Optional[str] = None, **params: Any) -> Dict[str, Any]:
        key = _key(instrument or data.get("instrument", self.default_instrument))
        closes = _series(data.get("closes", data.get("close", [])))
        highs = _series(data.get("highs", data.get("high", [])))
        lows = _series(data.get("lows", data.get("low", [])))
        volumes = _series(data.get("volumes", data.get("volume", [])))
        n = min(len(closes), len(highs), len(lows))
        if n == 0:
            return self._empty(key, data.get("timeframe", self.default_timeframe))
        closes, highs, lows = closes[-n:], highs[-n:], lows[-n:]
        volumes = (volumes[-n:] if len(volumes) >= n else [0.0] * (n - len(volumes)) + volumes[-n:])
        atr = self.atr(highs, lows, closes, int(params.get("atr_period", 14)))
        st_line, st_trend = self.supertrend(highs, lows, closes, int(params.get("st_period", 10)), float(params.get("st_multiplier", 2.5)))
        rsi = self.rsi(closes, int(params.get("rsi_period", 14)))
        macd = self.macd(closes)
        adx, di = self.adx(highs, lows, closes, int(params.get("adx_period", 14)))
        bb = self.bollinger(closes, int(params.get("bb_period", 20)), float(params.get("bb_std", 2.0)))
        vpt = self.vpt(closes, volumes)
        vwap = self.vwap(highs, lows, closes, volumes)
        volume_ratio = self.volume_ratio(volumes, 20)
        return {
            "instrument": key, "symbol": INSTRUMENTS[key]["symbol"], "timeframe": data.get("timeframe", self.default_timeframe),
            "price": closes[-1], "closes": closes, "atr": atr[-1], "atr_series": atr,
            "rsi": rsi[-1], "rsi_series": rsi, "macd": macd,
            "adx": adx[-1], "adx_series": adx, "di_direction": di[-1] if di else 0,
            "supertrend": {"line": st_line[-1], "trend": st_trend[-1], "line_series": st_line, "trend_series": st_trend},
            "bollinger": {"upper": bb["upper"][-1], "middle": bb["middle"][-1], "lower": bb["lower"][-1], "width": bb["width"][-1]},
            "vpt": vpt[-1], "vpt_series": vpt, "vpt_slope": self.slope(vpt, 5),
            "vwap": vwap[-1], "vwap_series": vwap, "volume_ratio": volume_ratio,
            "pip_size": INSTRUMENTS[key]["pip_size"], "data_quality": {"valid": True, "bars": n},
        }

    def analyze(self, data: Dict[str, Any], instrument: Optional[str] = None, **params: Any) -> Dict[str, Any]:
        return self.calculate_all(data, instrument, **params)

    def compute(self, data: Dict[str, Any], instrument: Optional[str] = None, **params: Any) -> Dict[str, Any]:
        return self.calculate_all(data, instrument, **params)

    def get_indicators(self, data: Dict[str, Any], instrument: Optional[str] = None, **params: Any) -> Dict[str, Any]:
        return self.calculate_all(data, instrument, **params)

    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        if not closes:
            return []
        trs = [highs[0] - lows[0]]
        for i in range(1, len(closes)):
            trs.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
        return _sma(trs, period)

    @classmethod
    def supertrend(cls, highs: List[float], lows: List[float], closes: List[float], period: int = 10, multiplier: float = 2.5) -> Tuple[List[float], List[int]]:
        if not closes:
            return [], []
        atr = cls.atr(highs, lows, closes, period)
        upper = [(h + l) / 2.0 + multiplier * a for h, l, a in zip(highs, lows, atr)]
        lower = [(h + l) / 2.0 - multiplier * a for h, l, a in zip(highs, lows, atr)]
        line, trend = [], []
        direction = 1
        for i, close in enumerate(closes):
            if i and close < lower[i - 1]:
                direction = -1
            elif i and close > upper[i - 1]:
                direction = 1
            trend.append(direction)
            line.append(lower[i] if direction > 0 else upper[i])
        return line, trend

    @staticmethod
    def rsi(closes: List[float], period: int = 14) -> List[float]:
        result = [50.0] * len(closes)
        if len(closes) <= period:
            return result
        for i in range(period, len(closes)):
            changes = [closes[j] - closes[j - 1] for j in range(i - period + 1, i + 1)]
            gain = sum(max(x, 0.0) for x in changes) / period
            loss = sum(max(-x, 0.0) for x in changes) / period
            result[i] = 100.0 if loss == 0 and gain > 0 else 50.0 if loss == 0 else 100.0 - 100.0 / (1.0 + gain / loss)
        return result

    @staticmethod
    def macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        fast_line, slow_line = _ema(closes, fast), _ema(closes, slow)
        line = [a - b for a, b in zip(fast_line, slow_line)]
        sig = _ema(line, signal)
        return {"macd_line": line[-1] if line else 0.0, "signal_line": sig[-1] if sig else 0.0, "histogram": (line[-1] - sig[-1]) if line and sig else 0.0, "series": line, "signal_series": sig}

    @staticmethod
    def adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Tuple[List[float], List[int]]:
        n = len(closes); adx, direction = [0.0] * n, [0] * n
        for i in range(1, n):
            start = max(1, i - period + 1)
            tr = sum(max(highs[j] - lows[j], abs(highs[j] - closes[j - 1]), abs(lows[j] - closes[j - 1])) for j in range(start, i + 1))
            plus = sum(max(highs[j] - highs[j - 1], 0.0) for j in range(start, i + 1))
            minus = sum(max(lows[j - 1] - lows[j], 0.0) for j in range(start, i + 1))
            pdi, mdi = (100.0 * plus / tr, 100.0 * minus / tr) if tr > 0 else (0.0, 0.0)
            adx[i] = 100.0 * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi else 0.0
            direction[i] = 1 if pdi > mdi else -1 if mdi > pdi else 0
        return adx, direction

    @staticmethod
    def bollinger(closes: List[float], period: int = 20, deviations: float = 2.0) -> Dict[str, List[float]]:
        middle, upper, lower, width = [], [], [], []
        for i in range(len(closes)):
            w = closes[max(0, i - period + 1):i + 1]; mean = sum(w) / len(w); std = math.sqrt(sum((x - mean) ** 2 for x in w) / len(w))
            middle.append(mean); upper.append(mean + deviations * std); lower.append(mean - deviations * std); width.append(2.0 * deviations * std / mean if mean else 0.0)
        return {"upper": upper, "middle": middle, "lower": lower, "width": width}

    @staticmethod
    def vpt(closes: List[float], volumes: List[float]) -> List[float]:
        total, result = 0.0, []
        for i, close in enumerate(closes):
            if i and closes[i - 1] != 0:
                total += (close - closes[i - 1]) / closes[i - 1] * (volumes[i] if i < len(volumes) else 0.0)
            result.append(total)
        return result

    @staticmethod
    def vwap(highs: List[float], lows: List[float], closes: List[float], volumes: List[float]) -> List[float]:
        total_pv = total_v = 0.0; result = []
        for h, l, c, v in zip(highs, lows, closes, volumes):
            v = max(0.0, v); total_pv += ((h + l + c) / 3.0) * v; total_v += v
            result.append(total_pv / total_v if total_v else c)
        return result

    @staticmethod
    def volume_ratio(volumes: List[float], period: int = 20) -> float:
        if len(volumes) < 2:
            return 1.0
        baseline = volumes[-period - 1:-1]; avg = sum(baseline) / len(baseline) if baseline else 0.0
        return volumes[-1] / avg if avg > 0 else 1.0

    @staticmethod
    def slope(values: List[float], period: int = 5) -> float:
        if len(values) < 2:
            return 0.0
        w = values[-period:]
        return (w[-1] - w[0]) / max(1, len(w) - 1)

    @staticmethod
    def _empty(key: str, timeframe: str) -> Dict[str, Any]:
        return {"instrument": key, "symbol": INSTRUMENTS[key]["symbol"], "timeframe": timeframe, "price": 0.0, "atr": 0.0, "rsi": 50.0, "adx": 0.0, "macd": {"macd_line": 0.0, "signal_line": 0.0, "histogram": 0.0}, "supertrend": {"line": 0.0, "trend": 0}, "bollinger": {"upper": 0.0, "middle": 0.0, "lower": 0.0, "width": 0.0}, "vpt": 0.0, "vwap": 0.0, "volume_ratio": 1.0, "data_quality": {"valid": False, "bars": 0, "reason": "no_data"}}
