"""مصفوفة القرار - Decision Matrix Module"""
import json
from datetime import datetime

class DecisionMatrix:
    """مصفوفة قرار متقدمة للتداول"""

    WEIGHTS = {
        "trend_alignment": 0.25,
        "momentum": 0.20,
        "volume": 0.15,
        "volatility": 0.10,
        "sentiment": 0.10,
        "pattern_strength": 0.10,
        "learning_score": 0.10
    }

    @classmethod
    def evaluate_signal(cls, indicators, market_regime, learning_data=None):
        """تقييم إشارة الدخول"""
        scores = {}

        # Trend alignment
        trend_score = 0
        if indicators.get("supertrend_trend") == 1 and indicators.get("hourly_trend") == 1:
            trend_score = 1.0
        elif indicators.get("supertrend_trend") == -1 and indicators.get("hourly_trend") == -1:
            trend_score = 1.0
        elif indicators.get("supertrend_trend") == indicators.get("hourly_trend"):
            trend_score = 0.5
        scores["trend_alignment"] = trend_score

        # Momentum
        rsi = indicators.get("rsi", 50)
        macd = indicators.get("macd", 0)
        if 30 < rsi < 70 and abs(macd) > 0:
            scores["momentum"] = 0.8
        elif rsi < 30 or rsi > 70:
            scores["momentum"] = 0.3
        else:
            scores["momentum"] = 0.5

        # Volume
        vol_ratio = indicators.get("volume_ratio", 1)
        if vol_ratio > 1.5:
            scores["volume"] = 1.0
        elif vol_ratio > 1.0:
            scores["volume"] = 0.7
        else:
            scores["volume"] = 0.3

        # Volatility
        atr = indicators.get("atr", 0)
        price = indicators.get("price", 1)
        atr_pct = (atr / price) * 100 if price > 0 else 0
        if 0.5 < atr_pct < 3.0:
            scores["volatility"] = 0.8
        elif atr_pct > 3.0:
            scores["volatility"] = 0.4
        else:
            scores["volatility"] = 0.5

        # Sentiment
        fear_greed = indicators.get("fear_greed", 50)
        if 40 < fear_greed < 60:
            scores["sentiment"] = 0.7
        elif fear_greed > 75 or fear_greed < 25:
            scores["sentiment"] = 0.3
        else:
            scores["sentiment"] = 0.5

        # Pattern strength
        pattern_score = 0.5
        if indicators.get("divergence") == "bullish" and indicators.get("supertrend_trend") == 1:
            pattern_score = 0.9
        elif indicators.get("divergence") == "bearish" and indicators.get("supertrend_trend") == -1:
            pattern_score = 0.9
        scores["pattern_strength"] = pattern_score

        # Learning score
        learning_score = 0.5
        if learning_data:
            similar_wins = learning_data.get("similar_wins", 0)
            similar_total = learning_data.get("similar_total", 1)
            learning_score = similar_wins / similar_total if similar_total > 0 else 0.5
        scores["learning_score"] = learning_score

        # Calculate weighted score
        total_score = sum(scores[k] * cls.WEIGHTS[k] for k in cls.WEIGHTS)

        return {
            "total_score": round(total_score, 3),
            "scores": scores,
            "confidence": "high" if total_score > 0.7 else "medium" if total_score > 0.5 else "low",
            "recommendation": "strong" if total_score > 0.75 else "moderate" if total_score > 0.55 else "weak"
        }

    @classmethod
    def evaluate_warning(cls, current_analysis, trade_type):
        """تقييم مستوى التحذير"""
        warning_score = 0
        factors = []

        # Trend reversal
        if current_analysis.get("trend") != ("صاعد" if trade_type == "BUY" else "هابط"):
            warning_score += 3
            factors.append("انعكاس اتجاه")

        # RSI extreme
        rsi = current_analysis.get("rsi", 50)
        if (trade_type == "BUY" and rsi > 75) or (trade_type == "SELL" and rsi < 25):
            warning_score += 2
            factors.append("RSI متطرف")

        # MACD divergence
        if current_analysis.get("macd_divergence"):
            warning_score += 2
            factors.append("دايفرجنس MACD")

        # Volume anomaly
        if current_analysis.get("volume_ratio", 1) > 2.0:
            warning_score += 1
            factors.append("حجم غير طبيعي")

        # Bollinger breakout
        bb_position = current_analysis.get("bollinger_position", "middle")
        if bb_position in ["upper", "lower"]:
            warning_score += 1
            factors.append("اختراق بولينجر")

        # Ichimoku cloud
        if current_analysis.get("ichimoku_cloud", "inside") != "inside":
            warning_score += 1
            factors.append("سحابة إيشيموكو")

        # Determine level
        if warning_score >= 6:
            level = "STRONG"
        elif warning_score >= 4:
            level = "MEDIUM"
        elif warning_score >= 2:
            level = "LIGHT"
        else:
            level = "NONE"

        return {
            "level": level,
            "score": warning_score,
            "factors": factors,
            "urgency": "immediate" if level == "STRONG" else "soon" if level == "MEDIUM" else "monitor"
        }
