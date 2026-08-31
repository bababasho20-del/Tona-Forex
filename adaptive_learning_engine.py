"""
Adaptive Learning Engine - Tona

طبقة تعلم طويلة المدى لا تغيّر إشارة SuperTrend نفسها.
وظيفتها: تقدير احتمال نجاح/فشل الإشارة اعتماداً على تاريخ الصفقات
والحالات المشابهة، مع أوزان حديثة/تاريخية ومعايرة وثبات إحصائي.
"""
from __future__ import annotations

import math
import logging
import statistics
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("TonaPrometheus")
CANONICAL_TIMEFRAMES = ("5m", "15m", "1h", "4h")


def _num(v, default=None):
    try:
        if v is None or v == "":
            return default
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _sigmoid(x):
    try:
        return 1.0 / (1.0 + math.exp(-max(-40, min(40, x))))
    except Exception:
        return 0.5


class AdaptiveLearningEngine:
    """
    محرك التعلم طويل المدى.

    قواعد صارمة:
    1) لا يغيّر SuperTrend ولا الماسح ولا إشارة الدخول الأصلية.
    2) يتعلم من جميع الصفقات المغلقة المتاحة، مع أوزان للحداثة والتشابه.
    3) لا يعتبر عينة صغيرة حقيقة؛ الثقة مرتبطة بحجم الدليل واستقراره.
    4) يميّز بين احتمال النجاح وبين درجة الثقة في هذا الاحتمال.
    5) يستخدم التوقعات السابقة فقط للمعايرة بعد تحققها، وليس كبيانات مستقبلية.
    """

    FEATURE_WEIGHTS = {
        "rsi": 0.11, "adx": 0.12, "macd_alignment": 0.11,
        "trend_alignment": 0.14, "volume": 0.08, "rr": 0.07,
        "regime": 0.09, "direction": 0.07, "asset": 0.04,
        "vpt_alignment": 0.08, "stochastic": 0.05,
        "bollinger": 0.04, "vwap": 0.04, "timeframe_alignment": 0.10,
        "support_resistance": 0.05,
    }
    FEATURE_ALIASES = {
        "vpt": ("entry_vpt", "vpt", "vpt_value"),
        "vpt_slope": ("entry_vpt_slope", "vpt_slope", "vpt_change"),
        "stochastic": ("entry_stochastic", "stochastic", "stoch_k", "stochastic_k"),
        "bollinger_position": ("entry_bollinger_position", "bollinger_position", "bb_position"),
        "vwap_distance": ("entry_vwap_distance", "vwap_distance", "price_vwap_pct"),
        "timeframe_alignment": ("entry_timeframe_alignment", "timeframe_alignment", "tf_alignment", "trend_alignment_score"),
        "support_distance": ("entry_support_distance", "support_distance", "support_distance_pct"),
        "resistance_distance": ("entry_resistance_distance", "resistance_distance", "resistance_distance_pct"),
    }

    def _first_num(self, row: Dict[str, Any], aliases, default=None):
        for key in aliases:
            v = _num(row.get(key), None)
            if v is not None:
                return v
        return default

    def _directional_quality(self, f: Dict[str, Any], direction: str) -> Dict[str, float]:
        """تحويل حالة المؤشرات إلى درجات قابلة للتعلم، دون تغيير إشارة SuperTrend."""
        buy = direction.upper() == "BUY"
        rsi = f["rsi"]
        rsi_q = 1.0 - min(1.0, abs(rsi - (45 if buy else 55)) / 45.0)
        adx_q = min(1.0, max(0.0, (f["adx"] - 12.0) / 25.0))
        macd_q = 1.0 if f["macd_aligned"] else 0.0
        trend_q = 1.0 if f["trend_aligned"] else 0.0
        vol_q = max(0.0, min(1.0, 1.0 - abs(f["volume"] - 1.0) / 1.5))
        rr_q = max(0.0, min(1.0, f["rr"] / 2.0))
        regime_q = 1.0 if f["regime"] == "trending" else 0.65 if f["regime"] == "transitional" else 0.45
        vpt_q = 1.0 if f.get("vpt_aligned") else 0.0 if f.get("vpt_available") else 0.5
        st = f.get("stochastic")
        st_q = 0.5 if st is None else (max(0.0, min(1.0, (st - 20) / 60)) if buy else max(0.0, min(1.0, (80 - st) / 60)))
        bb = f.get("bollinger_position")
        bb_q = 0.5 if bb is None else (1.0 - abs(bb - (0.35 if buy else 0.65)) / 0.65)
        vwap = f.get("vwap_distance")
        vwap_q = 0.5 if vwap is None else max(0.0, min(1.0, 1.0 - abs(vwap) / 1.0))
        tf_q = f.get("timeframe_alignment", 0.5)
        sr_q = 0.5
        sd, rd = f.get("support_distance"), f.get("resistance_distance")
        if sd is not None or rd is not None:
            if buy and rd is not None: sr_q = max(0.0, min(1.0, rd / 1.5))
            elif not buy and sd is not None: sr_q = max(0.0, min(1.0, sd / 1.5))
        return {
            "rsi": rsi_q, "adx": adx_q, "macd_alignment": macd_q,
            "trend_alignment": trend_q, "volume": vol_q, "rr": rr_q,
            "regime": regime_q, "vpt_alignment": vpt_q, "stochastic": st_q,
            "bollinger": max(0.0, min(1.0, bb_q)), "vwap": vwap_q,
            "timeframe_alignment": max(0.0, min(1.0, tf_q)),
            "support_resistance": sr_q,
        }

    def _learned_weights(self, history: List[Dict], asset: str, direction: str) -> Dict[str, float]:
        """أوزان تكيفية تُستخرج من نتائج التاريخ؛ لا تُحفظ كحالة عابرة ولا تغيّر SuperTrend."""
        rows = []
        for t in history:
            f = self._feature_row(t)
            if f["asset"] == asset and f["direction"] == direction:
                rows.append((self._directional_quality(f, direction), f["win"]))
        if len(rows) < 12:
            return dict(self.FEATURE_WEIGHTS)
        learned = {}
        for key, base in self.FEATURE_WEIGHTS.items():
            if key not in rows[0][0]:
                learned[key] = base
                continue
            vals_w = [q[key] for q, win in rows if win]
            vals_l = [q[key] for q, win in rows if not win]
            if not vals_w or not vals_l:
                learned[key] = base
                continue
            lift = statistics.mean(vals_w) - statistics.mean(vals_l)
            strength = min(1.0, abs(lift) / 0.35)
            # وزن أعلى فقط عندما يثبت العامل تمييزه بين النجاح والفشل.
            learned[key] = base * (0.70 + 0.90 * strength)
        total = sum(learned.values()) or 1.0
        target = sum(self.FEATURE_WEIGHTS.values())
        return {k: v * target / total for k, v in learned.items()}

    def __init__(self, learning_db=None, supabase=None):
        self.learning_db = learning_db
        self.supabase = supabase
        self.cache: Dict[str, Tuple[float, Any]] = {}
        logger.info("🧠 AdaptiveLearningEngine جاهز")

    # ------------------------- data access -------------------------
    def _fetch_trades(self, asset_type: Optional[str] = None, limit: int = 2000) -> List[Dict]:
        trades: List[Dict] = []
        try:
            if self.supabase and getattr(self.supabase, "connected", False):
                client = getattr(self.supabase, "client", None)
                if client:
                    page = 1000
                    offset = 0
                    while len(trades) < limit:
                        q = client.table("trades_full").select("*").order("entry_time", desc=True).range(offset, offset + page - 1)
                        if asset_type:
                            q = q.eq("asset_type", asset_type)
                        res = q.execute()
                        batch = res.data or []
                        if not batch:
                            break
                        trades.extend(batch)
                        if len(batch) < page:
                            break
                        offset += page
                        if len(trades) >= limit:
                            break
        except Exception as e:
            logger.warning("⚠️ تعذر جلب التاريخ من Supabase: %s", e)

        if not trades and self.learning_db:
            try:
                if asset_type:
                    trades = self.learning_db.get_trades_by_asset(asset_type, limit)
                else:
                    # Forex-only project: with no asset specified, aggregate only supported
                    # Forex instruments. Legacy oil/silver history is intentionally ignored.
                    trades = []
                    for asset in ("eurusd", "usdjpy"):
                        trades.extend(self.learning_db.get_trades_by_asset(asset, limit))
            except Exception as e:
                logger.warning("⚠️ تعذر جلب التاريخ من SQLite: %s", e)

        return [t for t in trades if self._is_closed(t) and _num(t.get("profit_dollars"), 0) != 0]

    def _fetch_predictions(self, asset_type=None, limit=2000) -> List[Dict]:
        try:
            if self.supabase and getattr(self.supabase, "connected", False):
                client = getattr(self.supabase, "client", None)
                if client:
                    q = client.table("trade_predictions").select("*").order("created_at", desc=True).limit(limit)
                    if asset_type:
                        q = q.eq("asset_type", asset_type)
                    res = q.execute()
                    return res.data or []
        except Exception as e:
            logger.warning("⚠️ تعذر قراءة سجل التوقعات: %s", e)
        return []

    @staticmethod
    def _is_closed(t: Dict) -> bool:
        return bool(t.get("exit_time") or t.get("exit_price"))

    # ------------------------- feature engineering -------------------------
    def _feature_row(self, t: Dict) -> Dict[str, Any]:
        direction = str(t.get("trade_type", t.get("type", "BUY"))).upper()
        asset = str(t.get("asset_type", "unknown")).lower()
        rsi = _num(t.get("entry_rsi"), 50.0)
        adx = _num(t.get("entry_adx"), 20.0)
        macd = _num(t.get("entry_macd"), 0.0)
        volume = _num(t.get("entry_volume_ratio"), None)
        if volume is None:
            volume = _num(t.get("volume_ratio"), 1.0)
        rr = _num(t.get("rr"), None)
        if rr is None:
            entry = _num(t.get("entry_price"), 0)
            sl = _num(t.get("sl_price"), 0)
            tp = _num(t.get("tp_price"), 0)
            if entry and sl and tp:
                risk = entry - sl if direction == "BUY" else sl - entry
                reward = tp - entry if direction == "BUY" else entry - tp
                rr = reward / risk if risk > 0 else 1.0
            else:
                rr = 1.0
        trend = str(t.get("entry_trend", t.get("trend", "محايد")))
        aligned_trend = (direction == "BUY" and "صاعد" in trend) or (direction == "SELL" and "هابط" in trend)
        macd_aligned = (direction == "BUY" and macd > 0) or (direction == "SELL" and macd < 0)
        regime = str(t.get("regime", ""))
        if not regime:
            regime = "trending" if adx >= 25 else "ranging"
        profit = _num(t.get("profit_dollars"), 0.0)
        vpt_slope = self._first_num(t, self.FEATURE_ALIASES["vpt_slope"], None)
        vpt = self._first_num(t, self.FEATURE_ALIASES["vpt"], None)
        stochastic = self._first_num(t, self.FEATURE_ALIASES["stochastic"], None)
        bb = self._first_num(t, self.FEATURE_ALIASES["bollinger_position"], None)
        vwap = self._first_num(t, self.FEATURE_ALIASES["vwap_distance"], None)
        tf_align = self._first_num(t, self.FEATURE_ALIASES["timeframe_alignment"], None)
        if tf_align is None:
            entry_analysis = t.get("full_entry_analysis") or {}
            tfs = entry_analysis.get("timeframes", {}) if isinstance(entry_analysis, dict) else {}
            support_count = 0
            known_count = 0
            for tf_name in CANONICAL_TIMEFRAMES:
                item = tfs.get(tf_name) if isinstance(tfs, dict) else None
                if not isinstance(item, dict):
                    continue
                tr = item.get("trend")
                if tr in ("صاعد", "هابط"):
                    known_count += 1
                    if (direction == "BUY" and tr == "صاعد") or (direction == "SELL" and tr == "هابط"):
                        support_count += 1
            if known_count:
                tf_align = support_count / known_count
        sd = self._first_num(t, self.FEATURE_ALIASES["support_distance"], None)
        rd = self._first_num(t, self.FEATURE_ALIASES["resistance_distance"], None)
        vpt_aligned = ((direction == "BUY" and ((vpt_slope is not None and vpt_slope > 0) or (vpt is not None and vpt > 0))) or
                       (direction == "SELL" and ((vpt_slope is not None and vpt_slope < 0) or (vpt is not None and vpt < 0))))
        if tf_align is None: tf_align = 1.0 if aligned_trend else 0.5
        return {
            "asset": asset,
            "direction": direction,
            "rsi": rsi,
            "adx": adx,
            "macd": macd,
            "volume": volume,
            "rr": rr,
            "trend": trend,
            "trend_aligned": aligned_trend,
            "macd_aligned": macd_aligned,
            "vpt_aligned": bool(vpt_aligned), "vpt_available": vpt is not None or vpt_slope is not None,
            "stochastic": stochastic, "bollinger_position": bb, "vwap_distance": vwap,
            "timeframe_alignment": tf_align, "support_distance": sd, "resistance_distance": rd,
            "timeframe_support_count": sum(1 for tf_name in CANONICAL_TIMEFRAMES if isinstance(tfs.get(tf_name), dict) and ((direction == "BUY" and tfs[tf_name].get("trend") == "صاعد") or (direction == "SELL" and tfs[tf_name].get("trend") == "هابط"))),
            "timeframe_known_count": sum(1 for tf_name in CANONICAL_TIMEFRAMES if isinstance(tfs.get(tf_name), dict) and tfs[tf_name].get("trend") in ("صاعد", "هابط")),
            "regime": regime,
            "profit": profit,
            "win": profit > 0,
            "entry_time": t.get("entry_time"),
        }

    def _current_features(self, analysis: Dict, asset: str, direction: str, entry_price=None, sl=None, tp=None) -> Dict[str, Any]:
        tfs = analysis.get("timeframes", {}) or {}
        tf = tfs.get("15m") or tfs.get("5m") or next(iter(tfs.values()), {})
        ind = analysis.get("indicators", {}) or {}
        trend_data = ind.get("trend", {}) or {}
        volume_data = ind.get("volume", {}) or {}
        rsi = _num(tf.get("rsi"), _num(ind.get("momentum", {}).get("rsi"), 50))
        adx = _num(tf.get("adx"), _num(trend_data.get("adx"), 20))
        macd = _num(tf.get("macd"), _num(ind.get("momentum", {}).get("macd"), 0))
        volume = _num(tf.get("volume_ratio"), _num(volume_data.get("ratio"), 1.0))
        trend = str(tf.get("trend", trend_data.get("current_trend", "محايد")))
        rr = 1.0
        e = _num(entry_price, 0)
        s = _num(sl, 0)
        p = _num(tp, 0)
        if e and s and p:
            risk = e - s if direction == "BUY" else s - e
            reward = p - e if direction == "BUY" else e - p
            if risk > 0:
                rr = reward / risk
        regime = "trending" if adx >= 25 else "ranging"
        if 20 <= adx < 25:
            regime = "transitional"
        vpt_slope = self._first_num(analysis, self.FEATURE_ALIASES["vpt_slope"], None)
        if vpt_slope is None:
            vpt_data = ind.get("vpt", {}) or {}
            vpt_slope = _num(vpt_data.get("slope"), _num(vpt_data.get("change"), None))
        vpt = self._first_num(analysis, self.FEATURE_ALIASES["vpt"], None)
        vpt_aligned = ((direction.upper() == "BUY" and vpt_slope is not None and vpt_slope > 0) or
                       (direction.upper() == "SELL" and vpt_slope is not None and vpt_slope < 0))
        stoch = self._first_num(analysis, self.FEATURE_ALIASES["stochastic"], None)
        if stoch is None: stoch = _num(ind.get("momentum", {}).get("stochastic"), None)
        bb = self._first_num(analysis, self.FEATURE_ALIASES["bollinger_position"], None)
        vwap_distance = self._first_num(analysis, self.FEATURE_ALIASES["vwap_distance"], None)
        tf_align = self._first_num(analysis, self.FEATURE_ALIASES["timeframe_alignment"], None)
        if tf_align is None:
            support_count = 0
            known_count = 0
            for tf_name in CANONICAL_TIMEFRAMES:
                item = tfs.get(tf_name) if isinstance(tfs, dict) else None
                if not isinstance(item, dict):
                    continue
                tr = item.get("trend")
                if tr in ("صاعد", "هابط"):
                    known_count += 1
                    if (direction == "BUY" and tr == "صاعد") or (direction == "SELL" and tr == "هابط"):
                        support_count += 1
            tf_align = (support_count / known_count) if known_count else (1.0 if ((direction == "BUY" and "صاعد" in trend) or (direction == "SELL" and "هابط" in trend)) else 0.5)
        sd = self._first_num(analysis, self.FEATURE_ALIASES["support_distance"], None)
        rd = self._first_num(analysis, self.FEATURE_ALIASES["resistance_distance"], None)
        return {
            "asset": asset.lower(),
            "direction": direction.upper(),
            "rsi": rsi,
            "adx": adx,
            "macd": macd,
            "volume": volume,
            "rr": rr,
            "trend": trend,
            "trend_aligned": (direction == "BUY" and "صاعد" in trend) or (direction == "SELL" and "هابط" in trend),
            "macd_aligned": (direction == "BUY" and macd > 0) or (direction == "SELL" and macd < 0),
            "vpt_aligned": bool(vpt_aligned), "vpt_available": vpt is not None or vpt_slope is not None,
            "stochastic": stoch, "bollinger_position": bb, "vwap_distance": vwap_distance,
            "timeframe_alignment": tf_align, "support_distance": sd, "resistance_distance": rd,
            "regime": regime,
        }

    # ------------------------- similarity -------------------------
    def _similarity(self, cur: Dict, old: Dict, weights: Optional[Dict[str, float]] = None) -> float:
        score = 0.0
        w = weights or self.FEATURE_WEIGHTS
        if cur["asset"] == old["asset"]: score += w["asset"]
        if cur["direction"] == old["direction"]: score += w["direction"]
        score += w["rsi"] * max(0, 1 - abs(cur["rsi"] - old["rsi"]) / 35)
        score += w["adx"] * max(0, 1 - abs(cur["adx"] - old["adx"]) / 25)
        score += w["macd_alignment"] * (1 if cur["macd_aligned"] == old["macd_aligned"] else 0)
        score += w["trend_alignment"] * (1 if cur["trend_aligned"] == old["trend_aligned"] else 0)
        score += w["volume"] * max(0, 1 - abs(cur["volume"] - old["volume"]) / 1.5)
        score += w["rr"] * max(0, 1 - abs(cur["rr"] - old["rr"]) / 2.0)
        score += w["regime"] * (1 if cur["regime"] == old["regime"] else 0.25 if {cur["regime"], old["regime"]} == {"transitional", "trending"} else 0)
        score += w.get("vpt_alignment", 0) * (1 if cur.get("vpt_aligned") == old.get("vpt_aligned") else 0.25)
        for key, scale in (("stochastic", 50.0), ("bollinger_position", 1.0), ("vwap_distance", 1.0), ("timeframe_alignment", 1.0), ("support_distance", 1.5), ("resistance_distance", 1.5)):
            if key not in old or old.get(key) is None or cur.get(key) is None: continue
            wk = {"stochastic":"stochastic","bollinger_position":"bollinger","vwap_distance":"vwap","timeframe_alignment":"timeframe_alignment","support_distance":"support_resistance","resistance_distance":"support_resistance"}[key]
            score += w.get(wk, 0) * max(0, 1 - abs(float(cur[key]) - float(old[key])) / scale)
        return _clamp(score)

    def _recency_weight(self, entry_time: Any) -> float:
        try:
            dt = datetime.fromisoformat(str(entry_time).replace("Z", "+00:00"))
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            age_days = max(0.0, (datetime.now() - dt).total_seconds() / 86400)
            return 0.35 + 0.65 * math.exp(-age_days / 45.0)
        except Exception:
            return 0.5

    def _historical_prior(self, history: List[Dict], asset: str, direction: str) -> Tuple[float, float]:
        """Prior خاص بالأصل/الاتجاه مع fallback عالمي؛ يمنع تضخيم عينة صغيرة."""
        scoped = [t for t in history if str(t.get("asset_type", "")).lower() == asset and str(t.get("trade_type", "")).upper() == direction]
        wins = sum(1 for t in scoped if _num(t.get("profit_dollars"), 0) > 0)
        # Beta(2,2) prior
        p_scoped = (wins + 2.0) / (len(scoped) + 4.0) if scoped else 0.5
        global_wins = sum(1 for t in history if _num(t.get("profit_dollars"), 0) > 0)
        p_global = (global_wins + 2.0) / (len(history) + 4.0) if history else 0.5
        blend = min(0.70, len(scoped) / 40.0)
        return p_scoped * blend + p_global * (1.0 - blend), float(len(scoped))

    def _calibration_info(self, asset_type: str, current_probability: float = 0.5) -> Dict[str, float]:
        rows = [r for r in self._fetch_predictions(asset_type, 2000) if r.get("was_correct") is not None]
        if not rows:
            return {"factor": 1.0, "bias": 0.0, "samples": 0, "accuracy": 0.5, "reliability": 0.0}
        vals = []
        for r in rows:
            p = self._first_num(r, ("probability", "success_probability", "predicted_probability", "prediction_probability"), None)
            if p is None: continue
            if p > 1: p /= 100.0
            vals.append((_clamp(p), 1.0 if r.get("was_correct") is True else 0.0))
        if len(vals) < 12:
            return {"factor": 1.0, "bias": 0.0, "samples": len(vals), "accuracy": sum(y for _,y in vals)/len(vals) if vals else 0.5, "reliability": 0.0}
        acc = sum(1 for _, y in vals if y == 1.0) / len(vals)
        global_bias = statistics.mean(y-p for p,y in vals)
        # Local reliability around the current probability; shrink heavily when sparse.
        local = [(p,y) for p,y in vals if abs(p-current_probability) <= 0.15]
        if len(local) >= 6:
            local_bias = statistics.mean(y-p for p,y in local)
            reliability = min(1.0, len(local)/25.0)
        else:
            local_bias, reliability = global_bias, min(0.5, len(vals)/50.0)
        bias = _clamp((0.35*global_bias + 0.65*local_bias) * (0.45 + 0.55*min(1.0,len(vals)/100.0)), -0.12, 0.12)
        return {"factor": 1.0, "bias": bias, "samples": len(vals), "accuracy": acc, "reliability": reliability}

    def _calibration_factor_from_predictions(self, asset_type: str) -> float:
        # Compatibility wrapper: calibration is now bias-based and data-aware.
        return self._calibration_info(asset_type).get("factor", 1.0)

    # ------------------------- prediction -------------------------
    def predict(self, analysis: Dict, asset_type: str, direction: str, entry_price=None, sl=None, tp=None) -> Dict:
        cur = self._current_features(analysis, asset_type, direction, entry_price, sl, tp)
        history = self._fetch_trades(asset_type, 2000)
        learned_weights = self._learned_weights(history, cur["asset"], cur["direction"])
        candidates = []
        for t in history:
            old = self._feature_row(t)
            if old["direction"] != cur["direction"]:
                continue
            sim = self._similarity(cur, old, learned_weights)
            if sim >= 0.48:
                candidates.append((sim, self._recency_weight(old.get("entry_time")), old, t))
        candidates.sort(key=lambda x: x[0] * x[1], reverse=True)
        candidates = candidates[:80]

        # Bayesian posterior. Breakeven is deliberately treated as non-win: the
        # model is asked to predict profitable outcomes, not merely non-losses.
        prior_p, scoped_n = self._historical_prior(history, cur["asset"], cur["direction"])
        prior_strength = 4.0 + min(12.0, scoped_n / 8.0)
        alpha = prior_p * prior_strength
        beta = (1.0 - prior_p) * prior_strength
        weighted_profit = []
        for sim, recency, old, raw in candidates:
            weight = max(0.05, sim * recency)
            if old["win"]:
                alpha += weight
            else:
                beta += weight
            weighted_profit.append((weight, old["profit"]))
        posterior = alpha / max(0.001, alpha + beta)
        evidence = sum(max(0.05, s * r) for s, r, _, _ in candidates)
        effective_n = max(0.0, alpha + beta - prior_strength)

        # Shrink toward an asset+direction prior when evidence is weak.
        probability = posterior
        if effective_n < 12:
            probability = posterior * (effective_n / 12.0) + prior_p * (1.0 - effective_n / 12.0)
        global_trades = history
        global_wins = sum(1 for t in global_trades if _num(t.get("profit_dollars"), 0) > 0)
        global_wr = (global_wins + 2.0) / (len(global_trades) + 4.0) if global_trades else 0.5

        # Post-hoc calibration from already resolved predictions only.
        cal_info = self._calibration_info(cur["asset"], probability)
        probability = _clamp(probability + cal_info["bias"], 0.02, 0.98)

        wins = [x for x in candidates if x[2]["win"]]
        losses = [x for x in candidates if not x[2]["win"]]
        weighted_win = sum(s * r for s, r, o, _ in candidates if o["win"])
        weighted_loss = sum(s * r for s, r, o, _ in candidates if not o["win"])

        risk_flags = []
        if cur["adx"] < 18:
            risk_flags.append("ADX ضعيف جداً")
        elif cur["adx"] < 22:
            risk_flags.append("ADX ضعيف")
        if direction == "BUY" and cur["rsi"] > 70:
            risk_flags.append("RSI مرتفع ضد الشراء")
        if direction == "SELL" and cur["rsi"] < 30:
            risk_flags.append("RSI منخفض ضد البيع")
        if not cur["trend_aligned"]:
            risk_flags.append("الاتجاه العام يعاكس الإشارة")
        if not cur["macd_aligned"]:
            risk_flags.append("MACD لا يؤيد الاتجاه")
        if cur["volume"] < 0.7:
            risk_flags.append("سيولة ضعيفة")
        if cur["rr"] < 1.2:
            risk_flags.append("RR منخفض")

        # False-signal score is independent from the SuperTrend signal itself.
        false_score = 0
        false_reasons = []
        for flag in risk_flags:
            false_score += {"ADX ضعيف جداً": 24, "ADX ضعيف": 15, "RSI مرتفع ضد الشراء": 14,
                             "RSI منخفض ضد البيع": 14, "الاتجاه العام يعاكس الإشارة": 24,
                             "MACD لا يؤيد الاتجاه": 13, "سيولة ضعيفة": 10, "RR منخفض": 8}.get(flag, 8)
            false_reasons.append(flag)
        if candidates:
            similarity_loss_rate = weighted_loss / max(0.01, weighted_win + weighted_loss)
            if similarity_loss_rate >= 0.60:
                false_score += 15
                false_reasons.append("الحالات المشابهة تميل تاريخياً للخسارة")
            elif similarity_loss_rate >= 0.52:
                false_score += 8
                false_reasons.append("ميل تاريخي ضعيف لصالح النجاح")
        false_score = int(max(0, min(100, false_score)))

        # Confidence is evidence quality + separation from 50%, not just win rate.
        separation = abs(probability - 0.5) * 2
        evidence_factor = min(1.0, math.sqrt(max(0.0, effective_n)) / 10.0)
        similarity_factor = min(1.0, evidence / 10.0)
        confidence = 50 + 45 * separation * (0.25 + 0.50 * evidence_factor + 0.25 * similarity_factor)
        confidence *= (1 - 0.35 * false_score / 100)
        confidence = int(round(max(25, min(95, confidence))))
        if not history:
            # A cold-start model has no empirical Forex evidence. Do not expose
            # the neutral Bayesian prior as learned confidence.
            probability = 0.50
            confidence = 0
            false_score = 0

        # Conservative verdict: require both probability and evidence.
        if probability >= 0.60 and confidence >= 55:
            verdict = "win"
        elif probability <= 0.40 and confidence >= 55:
            verdict = "loss"
        else:
            verdict = "uncertain"

        # Explain the actual historical evidence.
        similar_win_rate = None
        if candidates:
            similar_win_rate = weighted_win / max(0.01, weighted_win + weighted_loss)
        pattern = self._micro_pattern(cur, history)
        reasoning = self._reasoning(cur, probability, confidence, candidates, similar_win_rate, risk_flags)
        if pattern:
            reasoning += f" | النمط المتعلم: {pattern['name']} ({pattern['win_rate']:.0f}% نجاح، {pattern['samples']} حالة)"

        return {
            "verdict": verdict,
            "probability": round(probability * 100, 1),
            "confidence": confidence,
            "similar_count": len(candidates),
            "effective_sample": round(effective_n, 2),
            "similar_win_rate": round(similar_win_rate * 100, 1) if similar_win_rate is not None else None,
            "global_win_rate": round(global_wr * 100, 1),
            "expected_profit": round(sum(w * p for w, p in weighted_profit) / max(0.01, sum(w for w, _ in weighted_profit)), 4) if weighted_profit else 0.0,
            "calibration_factor": round(cal_info["factor"], 4),
            "calibration_bias": round(cal_info["bias"] * 100, 2),
            "calibration_samples": int(cal_info["samples"]),
            "learned_weights": {k: round(v, 4) for k, v in learned_weights.items()},
            "learned_pattern": pattern,
            "asset_direction_sample": int(scoped_n),
            "historical_count": int(len(history)),
            "has_historical_data": bool(history),
            "false_signal_score": false_score,
            "false_signal_reasons": false_reasons,
            "red_flags": risk_flags,
            "regime": cur["regime"],
            "indicator_scores": {
                "rsi": self._rsi_score(cur["rsi"], direction),
                "adx": min(100, max(10, cur["adx"] / 35 * 100)),
                "macd": 100 if cur["macd_aligned"] else 25,
                "trend_alignment": 100 if cur["trend_aligned"] else 15,
                "volume": min(100, max(15, cur["volume"] / 1.5 * 100)),
                "rr": min(100, max(15, cur["rr"] / 2 * 100)),
            },
            "reasoning": reasoning,
        }

    @staticmethod
    def _rsi_score(rsi, direction):
        if direction == "BUY":
            return 100 if 30 <= rsi <= 55 else 65 if rsi < 70 else 25
        return 100 if 45 <= rsi <= 70 else 65 if rsi > 30 else 25

    def _micro_pattern(self, cur: Dict[str, Any], history: List[Dict]) -> Optional[Dict[str, Any]]:
        """اكتشاف نمط صغير متكرر من البيانات الحالية دون الحاجة إلى جدول جديد."""
        def bucket(f):
            return (
                f["asset"], f["direction"], f["regime"],
                "rsi_low" if f["rsi"] < 40 else "rsi_mid" if f["rsi"] < 60 else "rsi_high",
                "adx_weak" if f["adx"] < 20 else "adx_mid" if f["adx"] < 25 else "adx_strong",
                "macd_yes" if f["macd_aligned"] else "macd_no",
                "trend_yes" if f["trend_aligned"] else "trend_no",
                "vpt_yes" if f.get("vpt_aligned") else "vpt_no",
            )
        target = bucket(cur); wins = total = 0
        for t in history:
            f = self._feature_row(t)
            if bucket(f) == target:
                total += 1; wins += int(f["win"])
        if total < 8: return None
        wr = 100.0 * wins / total
        return {"name": " | ".join(target[2:]), "win_rate": wr, "samples": total}

    @staticmethod
    def _reasoning(cur, probability, confidence, candidates, sim_wr, flags):
        parts = [f"التاريخ المشابه يشير إلى احتمال نجاح {probability * 100:.0f}%"]
        if sim_wr is not None:
            parts.append(f"نجاح الحالات المشابهة {sim_wr * 100:.0f}% ({len(candidates)} حالة)")
        else:
            parts.append("لا توجد عينة مشابهة كافية")
        parts.append(f"ADX {cur['adx']:.1f}، RSI {cur['rsi']:.1f}، نظام السوق {cur['regime']}")
        if flags:
            parts.append("تحذيرات: " + "، ".join(flags[:3]))
        parts.append(f"الثقة الإحصائية {confidence}%")
        return "تولين: " + " | ".join(parts)

    # ------------------------- calibration -------------------------
    def calibration(self, asset_type=None) -> Dict:
        rows = self._fetch_predictions(asset_type, 2000)
        evaluated = [r for r in rows if r.get("was_correct") is not None]
        if not evaluated:
            return {"samples": 0, "accuracy": None, "calibration_factor": 1.0}
        correct = sum(1 for r in evaluated if r.get("was_correct") is True)
        acc = correct / len(evaluated)
        info = self._calibration_info(asset_type, 0.5)
        return {"samples": len(evaluated), "accuracy": round(acc * 100, 2),
                "calibration_factor": round(info.get("factor", 1.0), 4),
                "calibration_bias": round(info.get("bias", 0.0) * 100, 2),
                "reliability": round(info.get("reliability", 0.0) * 100, 2)}
