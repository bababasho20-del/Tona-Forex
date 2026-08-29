"""
Forex Risk Master
=================
مدير مخاطر مخصص لمحاكاة EUR/USD وUSD/JPY.

المبادئ:
- الرافعة المتاحة لا تحدد حجم الصفقة؛ المخاطرة ووقف الخسارة هما الأساس.
- position_size هو قيمة المركز الاسمية للحفاظ على توافق الواجهة القديمة.
- margin_required هو الهامش المحاكى، وrisk_amount_at_stop هو الخطر الحقيقي المتوقع.
- لا يعتمد هذا الملف على مزود بيانات أو مكتبة تداول خارجية.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, Any, List


@dataclass(frozen=True)
class ForexInstrument:
    key: str
    symbol: str
    display: str
    pip_size: float
    digits: int
    contract_units: int
    base_currency: str
    quote_currency: str
    default_max_spread_pips: float


FOREX_INSTRUMENTS: Dict[str, ForexInstrument] = {
    "eurusd": ForexInstrument(
        key="eurusd", symbol="EURUSD", display="EUR/USD", pip_size=0.0001,
        digits=5, contract_units=100_000, base_currency="EUR",
        quote_currency="USD", default_max_spread_pips=1.5,
    ),
    "usdjpy": ForexInstrument(
        key="usdjpy", symbol="USDJPY", display="USD/JPY", pip_size=0.01,
        digits=3, contract_units=100_000, base_currency="USD",
        quote_currency="JPY", default_max_spread_pips=2.0,
    ),
}


def resolve_instrument(value: Any = "eurusd") -> ForexInstrument:
    key = str(value or "eurusd").strip().lower().replace("/", "")
    aliases = {
        "eurusd": "eurusd", "eur_usd": "eurusd", "eurusd=x": "eurusd",
        "usdjpy": "usdjpy", "usd_jpy": "usdjpy", "jpy=x": "usdjpy",
    }
    key = aliases.get(key, key)
    if key.upper() == "EURUSD":
        key = "eurusd"
    if key.upper() == "USDJPY":
        key = "usdjpy"
    if key not in FOREX_INSTRUMENTS:
        raise ValueError(f"Unsupported Forex instrument: {value}")
    return FOREX_INSTRUMENTS[key]


@dataclass
class MarketRegime:
    regime: str
    strength: float
    adx: float
    bollinger_width: float
    atr_ratio: float
    trend_direction: int
    volatility_class: str
    recommendation: str
    instrument: str = "eurusd"


class RegimeDetector:
    """كاشف نظام سوق يستخدم مقاييس مطبّعة مناسبة لزوجي الفوركس."""

    def __init__(self, min_bars: int = 50, max_history: int = 100):
        self.min_bars = max(30, int(min_bars))
        self._history: List[MarketRegime] = []
        self._max_history = max(10, int(max_history))

    @staticmethod
    def _clean_series(data: dict) -> Tuple[List[float], List[float], List[float]]:
        closes = [float(x) for x in data.get("closes", [])]
        highs = [float(x) for x in data.get("highs", [])]
        lows = [float(x) for x in data.get("lows", [])]
        n = min(len(closes), len(highs), len(lows))
        return closes[-n:], highs[-n:], lows[-n:]

    def detect(self, data: dict) -> MarketRegime:
        instrument = str((data or {}).get("instrument", "eurusd")).lower()
        closes, highs, lows = self._clean_series(data or {})
        if len(closes) < self.min_bars:
            return MarketRegime("unknown", 0.0, 0.0, 0.0, 0.0, 0, "unknown", "avoid", instrument)

        adx = self._calculate_adx(highs, lows, closes, period=14)
        bb_width = self._calculate_bb_width(closes, period=20)
        atr_ratio = self._calculate_atr_ratio(highs, lows, closes, period=14)
        sma_20 = sum(closes[-20:]) / 20
        sma_50 = sum(closes[-50:]) / 50
        # نسبة 0.5% ثابتة معقولة كمرشح أولي، لكن يجب معايرتها خارج العينة.
        trend_dir = 1 if sma_20 > sma_50 * 1.005 else -1 if sma_20 < sma_50 * 0.995 else 0
        regime, strength, recommendation = self._classify_regime(adx, bb_width, atr_ratio, trend_dir)
        vol_class = self._classify_volatility(atr_ratio, bb_width)
        result = MarketRegime(regime, strength, adx, bb_width, atr_ratio, trend_dir, vol_class, recommendation, instrument)
        self._history.append(result)
        del self._history[:-self._max_history]
        return result

    @staticmethod
    def _calculate_adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        if len(closes) < period * 2 + 1:
            return 0.0
        trs, plus_dm, minus_dm = [], [], []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
            up = highs[i] - highs[i - 1]
            down = lows[i - 1] - lows[i]
            trs.append(max(0.0, tr))
            plus_dm.append(up if up > down and up > 0 else 0.0)
            minus_dm.append(down if down > up and down > 0 else 0.0)
        if len(trs) < period:
            return 0.0
        # متوسطات متحركة بسيطة مستقرة وقابلة لإعادة الإنتاج للباك تست.
        adx_values = []
        for end in range(period, len(trs) + 1):
            tr_sum = sum(trs[end - period:end])
            if tr_sum <= 0:
                adx_values.append(0.0)
                continue
            pdi = 100.0 * sum(plus_dm[end - period:end]) / tr_sum
            mdi = 100.0 * sum(minus_dm[end - period:end]) / tr_sum
            denom = pdi + mdi
            adx_values.append(100.0 * abs(pdi - mdi) / denom if denom else 0.0)
        return max(0.0, min(100.0, sum(adx_values[-period:]) / min(period, len(adx_values)))) if adx_values else 0.0

    @staticmethod
    def _calculate_bb_width(closes: List[float], period: int = 20) -> float:
        if len(closes) < period:
            return 0.0
        window = closes[-period:]
        mean = sum(window) / period
        if mean <= 0:
            return 0.0
        variance = sum((x - mean) ** 2 for x in window) / period
        return max(0.0, (4.0 * math.sqrt(variance)) / mean)

    @staticmethod
    def _calculate_atr_ratio(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        if len(closes) < period * 2 + 1:
            return 1.0
        trs = []
        for i in range(1, len(closes)):
            trs.append(max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])))
        current = sum(trs[-period:]) / period
        previous = sum(trs[-period * 2:-period]) / period
        return current / previous if previous > 0 else 1.0

    @staticmethod
    def _classify_regime(adx: float, bb_width: float, atr_ratio: float, trend_dir: int) -> Tuple[str, float, str]:
        if atr_ratio >= 2.5 or bb_width >= 0.06:
            return "volatile", min(1.0, atr_ratio / 3.0), "avoid"
        if adx < 18 and bb_width < 0.015:
            return "ranging", 0.45, "caution"
        if adx >= 25 and trend_dir:
            return ("trending_up" if trend_dir > 0 else "trending_down"), min(1.0, adx / 50.0), "trade"
        if adx >= 20 and trend_dir:
            return ("trending_up" if trend_dir > 0 else "trending_down"), min(1.0, adx / 45.0), "caution"
        return "ranging", 0.35, "caution"

    @staticmethod
    def _classify_volatility(atr_ratio: float, bb_width: float) -> str:
        score = atr_ratio + bb_width * 10.0
        if score >= 3.0:
            return "extreme"
        if score >= 2.0:
            return "high"
        if score >= 1.2:
            return "normal"
        return "low"

    def get_regime_description(self, regime: MarketRegime) -> str:
        labels = {
            "trending_up": "سوق صاعد",
            "trending_down": "سوق هابط",
            "ranging": "سوق عرضي",
            "volatile": "سوق شديد التقلب",
            "unknown": "حالة غير معروفة",
        }
        return f"{labels.get(regime.regime, 'غير معروف')} | تقلب: {regime.volatility_class} | توصية: {regime.recommendation}"


@dataclass
class RiskProfile:
    # الحقول الأصلية للحفاظ على التوافق.
    leverage: float
    position_size: float
    stop_loss_pct: float
    take_profit_pct: float
    max_loss_dollars: float
    risk_reward: float
    confidence: str
    reason: str
    # حقول Forex الجديدة.
    instrument: str = "eurusd"
    symbol: str = "EURUSD"
    pip_size: float = 0.0001
    stop_loss_pips: float = 0.0
    take_profit_pips: float = 0.0
    risk_amount: float = 0.0
    risk_percent: float = 0.0
    notional_value: float = 0.0
    margin_required: float = 0.0
    units: float = 0.0
    lots: float = 0.0
    spread_pips: float = 0.0
    estimated_cost: float = 0.0
    effective_leverage: float = 0.0
    blocked: bool = False


class KellyOptimizer:
    """إحصاء مساعد فقط؛ لا يرفع المخاطرة تلقائيًا."""

    def __init__(self, max_samples: int = 200):
        self._trades: List[float] = []
        self._max_samples = max(20, int(max_samples))

    def add_trade(self, profit: float, loss: float = 0.0):
        value = float(profit) - abs(float(loss))
        self._trades.append(value)
        del self._trades[:-self._max_samples]

    def calculate_kelly(self) -> Dict[str, float]:
        if len(self._trades) < 20:
            return {"kelly": 0.0, "half_kelly": 0.0, "win_rate": 0.5, "avg_win": 0.0, "avg_loss": 0.0, "odds": 0.0, "confidence": "insufficient", "samples": len(self._trades)}
        wins = [x for x in self._trades if x > 0]
        losses = [-x for x in self._trades if x < 0]
        p = len(wins) / len(self._trades)
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        b = avg_win / avg_loss if avg_loss > 0 else 0.0
        kelly = max(0.0, min(0.25, (p * b - (1 - p)) / b)) if b > 0 else 0.0
        return {"kelly": kelly, "half_kelly": min(0.01, kelly / 2.0), "win_rate": p, "avg_win": avg_win, "avg_loss": avg_loss, "odds": b, "confidence": "measured", "samples": len(self._trades)}

    def suggest_position_size(self, capital: float, kelly_result: Dict[str, float]) -> float:
        return max(0.0, float(capital) * min(0.01, float(kelly_result.get("half_kelly", 0.0))))


class DynamicRiskManager:
    def __init__(self, initial_capital: float = 100.0, max_leverage: float = 200.0,
                 bot_max_effective_leverage: float = 10.0, default_risk_pct: float = 0.01):
        self.initial_capital = max(0.0, float(initial_capital))
        self.max_leverage = max(1.0, float(max_leverage))
        self.bot_max_effective_leverage = max(1.0, float(bot_max_effective_leverage))
        self.default_risk_pct = min(0.02, max(0.0001, float(default_risk_pct)))
        self._capital = self.initial_capital
        self._profits: List[float] = []
        self._max_history = 100

    def get_win_rate(self) -> float:
        if not self._profits:
            return 0.5
        return sum(1 for x in self._profits if x > 0) / len(self._profits)

    def update_win_rate(self, profit: float):
        self._profits.append(float(profit))
        del self._profits[:-self._max_history]

    def calculate(self, signal_snapshot: dict, regime: MarketRegime, win_rate: float = 0.5) -> RiskProfile:
        snapshot = signal_snapshot or {}
        instrument = resolve_instrument(snapshot.get("instrument", snapshot.get("asset", "eurusd")))
        price = float(snapshot.get("price", 0.0) or 0.0)
        atr = max(0.0, float(snapshot.get("atr", 0.0) or 0.0))
        if price <= 0:
            return self._blocked_profile(instrument, "سعر غير صالح")

        spread_pips = max(0.0, float(snapshot.get("spread_pips", 0.0) or 0.0))
        slippage_pips = max(0.0, float(snapshot.get("slippage_pips", 0.2) or 0.2))
        max_spread = float(snapshot.get("max_spread_pips", instrument.default_max_spread_pips))
        signal_score = self._signal_score(snapshot, regime)
        risk_pct = min(self.default_risk_pct, max(0.0001, float(snapshot.get("risk_pct", self.default_risk_pct))))
        if regime.recommendation == "avoid":
            risk_pct *= 0.25
        elif regime.recommendation == "caution":
            risk_pct *= 0.5
        risk_amount = self._capital * risk_pct

        sl_multiplier = float(snapshot.get("sl_atr_multiplier", 2.0))
        stop_distance = float(snapshot.get("stop_distance_price", 0.0) or 0.0)
        if stop_distance <= 0:
            stop_distance = atr * sl_multiplier if atr > 0 else price * 0.0015
        stop_pips = stop_distance / instrument.pip_size
        effective_cost_pips = spread_pips + slippage_pips
        pip_value_per_unit = instrument.pip_size if instrument.quote_currency == "USD" else instrument.pip_size / price
        total_risk_pips = max(1.0, stop_pips + effective_cost_pips)
        units = risk_amount / (total_risk_pips * pip_value_per_unit)

        # سقف الرافعة الفعلية، مستقل عن الرافعة القصوى التي يعلنها الوسيط.
        max_notional = self._capital * self.bot_max_effective_leverage
        units = min(units, max_notional / price if price > 0 else 0.0)
        notional = units * price
        margin = notional / self.max_leverage
        estimated_cost = units * effective_cost_pips * pip_value_per_unit
        risk_at_stop = units * stop_pips * pip_value_per_unit + estimated_cost
        rr = max(1.0, float(snapshot.get("risk_reward", 2.0)))
        tp_pips = stop_pips * rr
        confidence = "high" if signal_score >= 0.70 and regime.recommendation == "trade" else "medium" if signal_score >= 0.45 else "low"
        blocked = spread_pips > max_spread or regime.recommendation == "avoid" or units <= 0
        if blocked:
            reason = "تم حظر الصفقة بسبب السبريد أو حالة السوق أو عدم كفاية البيانات"
            units = notional = margin = estimated_cost = risk_at_stop = 0.0
        else:
            reason = f"{instrument.display}: مخاطرة {risk_pct * 100:.2f}%، وقف {stop_pips:.1f} pip، وتكلفة مقدرة {estimated_cost:.4f}"

        return RiskProfile(
            leverage=self.max_leverage,
            position_size=notional,
            stop_loss_pct=stop_distance / price,
            take_profit_pct=(tp_pips * instrument.pip_size) / price,
            max_loss_dollars=risk_at_stop,
            risk_reward=rr,
            confidence=confidence,
            reason=reason,
            instrument=instrument.key,
            symbol=instrument.symbol,
            pip_size=instrument.pip_size,
            stop_loss_pips=stop_pips,
            take_profit_pips=tp_pips,
            risk_amount=risk_at_stop,
            risk_percent=(risk_at_stop / self._capital if self._capital > 0 else 0.0),
            notional_value=notional,
            margin_required=margin,
            units=units,
            lots=units / instrument.contract_units,
            spread_pips=spread_pips,
            estimated_cost=estimated_cost,
            effective_leverage=(notional / self._capital if self._capital > 0 else 0.0),
            blocked=blocked,
        )

    def _signal_score(self, snapshot: dict, regime: MarketRegime) -> float:
        adx = max(0.0, min(100.0, float(snapshot.get("adx", regime.adx) or 0.0)))
        trend = max(0.0, min(1.0, float(snapshot.get("trend_strength", regime.strength) or 0.0)))
        volume = max(0.0, min(1.0, (float(snapshot.get("volume_ratio", 1.0) or 1.0) - 0.8) / 1.2))
        score = (min(1.0, adx / 40.0) * 0.40) + (trend * 0.40) + (volume * 0.20)
        if regime.recommendation == "avoid":
            score *= 0.25
        elif regime.recommendation == "caution":
            score *= 0.75
        return max(0.0, min(1.0, score))

    def _blocked_profile(self, instrument: ForexInstrument, reason: str) -> RiskProfile:
        return RiskProfile(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "low", reason, instrument.key, instrument.symbol, instrument.pip_size, blocked=True)


class RiskMaster:
    """واجهة التوافق الرئيسية المستخدمة من main_forex.py."""

    def __init__(self, initial_capital: float = 100.0, max_leverage: float = 200.0,
                 bot_max_effective_leverage: float = 10.0, default_risk_pct: float = 0.01):
        self.regime_detector = RegimeDetector()
        self.risk_manager = DynamicRiskManager(initial_capital, max_leverage, bot_max_effective_leverage, default_risk_pct)
        self.kelly = KellyOptimizer()
        self._capital = max(0.0, float(initial_capital))

    def detect_regime(self, data: dict) -> MarketRegime:
        return self.regime_detector.detect(data)

    def calculate_risk(self, signal_snapshot: dict, regime: Optional[MarketRegime] = None,
                       data: Optional[dict] = None) -> RiskProfile:
        if regime is None:
            regime = self.detect_regime(data) if data else MarketRegime("unknown", 0.0, 0.0, 0.0, 0.0, 0, "unknown", "avoid")
        return self.risk_manager.calculate(signal_snapshot or {}, regime, self.risk_manager.get_win_rate())

    def update_after_trade(self, profit: float, loss: float = 0.0, **_: Any):
        net = float(profit or 0.0) - abs(float(loss or 0.0))
        self.risk_manager.update_win_rate(net)
        self.kelly.add_trade(net)
        self._capital = max(0.0, self._capital + net)
        self.risk_manager._capital = self._capital

    def get_status(self) -> Dict[str, Any]:
        return {
            "capital": self._capital,
            "win_rate": self.risk_manager.get_win_rate(),
            "kelly": self.kelly.calculate_kelly(),
            "broker_max_leverage": self.risk_manager.max_leverage,
            "bot_max_effective_leverage": self.risk_manager.bot_max_effective_leverage,
            "default_risk_pct": self.risk_manager.default_risk_pct,
            "regime_detector": "active",
            "instruments": [spec.symbol for spec in FOREX_INSTRUMENTS.values()],
        }

    def get_current_status(self) -> Dict[str, Any]:
        return self.get_status()

    def format_risk_report(self, risk: RiskProfile, regime: MarketRegime) -> str:
        return (
            f"\n🛡️ تقرير مخاطر {risk.symbol}\n"
            f"حالة السوق: {self.regime_detector.get_regime_description(regime)}\n"
            f"الرافعة المتاحة: {risk.leverage:.1f}x | الرافعة الفعلية: {risk.effective_leverage:.2f}x\n"
            f"القيمة الاسمية: ${risk.notional_value:.4f} | الهامش: ${risk.margin_required:.4f}\n"
            f"الحجم: {risk.units:.2f} وحدة ({risk.lots:.5f} lot)\n"
            f"وقف الخسارة: {risk.stop_loss_pips:.1f} pip | الهدف: {risk.take_profit_pips:.1f} pip\n"
            f"الخسارة المتوقعة عند الوقف: ${risk.max_loss_dollars:.4f}\n"
            f"الحالة: {'محظور' if risk.blocked else 'مسموح بحثيًا'} | السبب: {risk.reason}\n"
        )


# الاسم القديم إن كانت أجزاء قديمة من المشروع تستورده مباشرة.
MarketRegimeDetector = RegimeDetector


if __name__ == "__main__":
    master = RiskMaster(initial_capital=100.0, max_leverage=200.0)
    data = {
        "instrument": "eurusd",
        "closes": [1.0800 + i * 0.0001 for i in range(100)],
        "highs": [1.0802 + i * 0.0001 for i in range(100)],
        "lows": [1.0798 + i * 0.0001 for i in range(100)],
        "volumes": [1000.0] * 100,
    }
    regime = master.detect_regime(data)
    profile = master.calculate_risk({
        "instrument": "eurusd", "price": 1.09, "atr": 0.0010,
        "adx": 28, "trend_strength": 0.8, "volume_ratio": 1.1,
        "spread_pips": 0.8,
    }, regime)
    print(master.format_risk_report(profile, regime))
