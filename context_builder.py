"""بناء السياق - Context Builder Module"""
import json
from datetime import datetime

class ContextBuilder:
    """بناء سياق شامل للتحليل والمحادثة"""

    @staticmethod
    def build_trade_context(trade_data, market_data, user_profile=None):
        """بناء سياق الصفقة"""
        context = {
            "trade": trade_data,
            "market": market_data,
            "user": user_profile or {},
            "timestamp": datetime.now().isoformat()
        }
        return context

    @staticmethod
    def build_analysis_context(asset_type, timeframes_data, indicators_summary):
        """بناء سياق التحليل الفني"""
        context = {
            "asset": asset_type,
            "timeframes": timeframes_data,
            "indicators": indicators_summary,
            "timestamp": datetime.now().isoformat()
        }
        return context

    @staticmethod
    def build_alert_context(alert_level, trade_data, current_analysis, recommendations):
        """بناء سياق التحذير"""
        context = {
            "level": alert_level,
            "trade": trade_data,
            "analysis": current_analysis,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        return context

    @staticmethod
    def build_learning_context(trade_history, patterns, predictions):
        """بناء سياق التعلم"""
        context = {
            "history": trade_history,
            "patterns": patterns,
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
        return context

    @staticmethod
    def format_for_groq(context, mode="analysis"):
        """تنسيق السياق لـ Groq API"""
        if mode == "analysis":
            return json.dumps(context, indent=2, ensure_ascii=False)
        elif mode == "alert":
            return f"""
تحذير مستوى: {context['level']}
الصفقة: {json.dumps(context['trade'], ensure_ascii=False)}
التحليل: {json.dumps(context['analysis'], ensure_ascii=False)}
التوصيات: {json.dumps(context['recommendations'], ensure_ascii=False)}
"""
        elif mode == "learning":
            return f"""
أرشيف التعلم:
الصفقات السابقة: {len(context['history'])}
الأنماط المكتشفة: {len(context['patterns'])}
التوقعات: {json.dumps(context['predictions'], ensure_ascii=False)}
"""
        return json.dumps(context, ensure_ascii=False)
