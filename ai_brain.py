"""
🧠 AI Brain V1.0 - Tona AI Hobany Radar
العقل الخارق: RAG + Chain-of-Thought + Pattern Learning
يعمل بالتوازي مع الكود الأساسي دون تعديله
المطور: بسام الحوباني | الاسم الشخصي: تولين
"""

import json
import sqlite3
import time
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

# =====================================================================
# 📚 نظام RAG (Retrieval Augmented Generation)
# =====================================================================

@dataclass
class TradeContext:
    """سياق صفقة للاسترجاع"""
    trade_id: str
    asset_type: str
    entry_price: float
    exit_price: float
    trade_type: str
    profit_dollars: float
    exit_reason: str
    rsi_at_entry: float
    adx_at_entry: float
    trend: str
    lessons: str
    success_score: int
    timestamp: str


class RAGMemory:
    """
    ذاكرة RAG متقدمة
    تسترجع الصفقات المشابهة بناءً على:
    - نوع الأصل
    - نوع الصفقة (BUY/SELL)
    - نطاق RSI
    - نطاق ADX
    - الاتجاه
    """

    def __init__(self, db_path="learning_data/memory.db"):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # جدول متجهات مبسط (بدون embeddings حقيقية - يستخدم فلترة ذكية)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                asset_type TEXT,
                trade_type TEXT,
                rsi_bucket TEXT,  -- "low", "mid", "high"
                adx_bucket TEXT,  -- "weak", "moderate", "strong"
                trend TEXT,
                profit_bucket TEXT,  -- "loss", "small", "good", "excellent"
                exit_reason TEXT,
                vector_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _get_bucket(self, value: float, buckets: list) -> str:
        """تصنيف القيمة في bucket"""
        for bucket_name, (low, high) in buckets:
            if low <= value < high:
                return bucket_name
        return buckets[-1][0]

    def index_trade(self, trade_context: TradeContext):
        """فهرسة صفقة جديدة في RAG"""
        rsi_buckets = [("oversold", 0, 30), ("low", 30, 45), ("mid", 45, 65), ("high", 65, 80), ("overbought", 80, 100)]
        adx_buckets = [("weak", 0, 20), ("moderate", 20, 35), ("strong", 35, 100)]
        profit_buckets = [("loss", -9999, 0), ("small", 0, 1), ("good", 1, 5), ("excellent", 5, 9999)]

        rsi_b = self._get_bucket(trade_context.rsi_at_entry, rsi_buckets)
        adx_b = self._get_bucket(trade_context.adx_at_entry, adx_buckets)
        profit_b = self._get_bucket(trade_context.profit_dollars, profit_buckets)

        vector = {
            "rsi": trade_context.rsi_at_entry,
            "adx": trade_context.adx_at_entry,
            "profit": trade_context.profit_dollars,
            "entry_price": trade_context.entry_price
        }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO trade_vectors 
            (trade_id, asset_type, trade_type, rsi_bucket, adx_bucket, trend, profit_bucket, exit_reason, vector_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_context.trade_id, trade_context.asset_type, trade_context.trade_type,
            rsi_b, adx_b, trade_context.trend, profit_b, trade_context.exit_reason,
            json.dumps(vector, ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
        logging.info(f"🧠 تولين: تم فهرسة الصفقة {trade_context.trade_id} في الذاكرة")

    def retrieve_similar(self, asset_type: str, trade_type: str, rsi: float, adx: float, 
                         trend: str, top_k: int = 5) -> List[Dict]:
        """استرجاع الصفقات المشابهة"""
        rsi_buckets = [("oversold", 0, 30), ("low", 30, 45), ("mid", 45, 65), ("high", 65, 80), ("overbought", 80, 100)]
        adx_buckets = [("weak", 0, 20), ("moderate", 20, 35), ("strong", 35, 100)]

        rsi_b = self._get_bucket(rsi, rsi_buckets)
        adx_b = self._get_bucket(adx, adx_buckets)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # البحث المتدرج: نفس الأصل + نفس النوع + نفس bucket RSI + نفس bucket ADX
        cursor.execute("""
            SELECT trade_id, vector_json, exit_reason, profit_bucket, created_at
            FROM trade_vectors
            WHERE asset_type = ? AND trade_type = ? AND rsi_bucket = ? AND adx_bucket = ? AND trend = ?
            ORDER BY created_at DESC LIMIT ?
        """, (asset_type, trade_type, rsi_b, adx_b, trend, top_k))

        results = cursor.fetchall()

        # إذا لم نجد نتائج كافية، نوسع البحث
        if len(results) < top_k:
            cursor.execute("""
                SELECT trade_id, vector_json, exit_reason, profit_bucket, created_at
                FROM trade_vectors
                WHERE asset_type = ? AND trade_type = ? AND rsi_bucket = ?
                ORDER BY created_at DESC LIMIT ?
            """, (asset_type, trade_type, rsi_b, top_k * 2))
            results = cursor.fetchall()

        conn.close()

        similar = []
        for row in results[:top_k]:
            vector = json.loads(row[1]) if row[1] else {}
            similar.append({
                "trade_id": row[0],
                "vector": vector,
                "exit_reason": row[2],
                "profit_bucket": row[3],
                "created_at": row[4]
            })

        return similar

    def get_pattern_stats(self, asset_type: str, trade_type: str) -> Dict:
        """إحصائيات الأنماط لنوع محدد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT profit_bucket, COUNT(*) as count
            FROM trade_vectors
            WHERE asset_type = ? AND trade_type = ?
            GROUP BY profit_bucket
        """, (asset_type, trade_type))

        stats = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return stats


# =====================================================================
# 🧩 محرك Chain-of-Thought (CoT)
# =====================================================================

class ChainOfThoughtEngine:
    """
    محرك التفكير المتسلسل
    يجبر AI على التفكير خطوة بخطوة قبل إعطاء النتيجة
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self._request_log = []
        self._last_request_time = 0
        self.min_interval = 3

    def _can_request(self) -> bool:
        now = time.time()
        self._request_log = [t for t in self._request_log if now - t < 60]
        if len(self._request_log) >= 10:  # 10 طلبات/دقيقة
            return False
        if now - self._last_request_time < self.min_interval:
            time.sleep(self.min_interval - (now - self._last_request_time))
        self._request_log.append(time.time())
        return True

    def build_cot_prompt(self, snapshot: dict, similar_trades: List[Dict], 
                       context_mode: str = "monitoring") -> Tuple[str, str]:
        """
        بناء prompt CoT
        يرجع: (system_prompt, user_prompt)
        """

        if context_mode == "monitoring":
            system_prompt = """أنت خبير مراقبة صفقات متخصص في النفط والفضة يا صديقي.
يجب أن تفكر خطوة بخطوة قبل إعطاء التوصية.
اتبع هذه الخطوات بالضبط:
1. تحليل المؤشرات الفنية الحالية (RSI, ADX, MACD, Bollinger, VWAP)
2. مقارنة مع لحظة الدخول (إن وجدت)
3. تحليل الصفقات المشابهة السابقة (ما نسبة نجاحها؟)
4. تقييم المخاطر (هل السعر قرب SL؟ هل الاتجاه تغير؟)
5. التوصية النهائية (استمر / احذر / أغلق)

قواعد:
- إذا ADX < 20 → الاتجاه ضعيف، احذر
- إذا RSI في اتجاه معاكس للصفقة → احذر
- إذا السعر قرب Bollinger Band معاكس → احذر
- إذا نسبة نجاح الصفقات المشابهة < 50% → أغلق
- أعطِ التوصية في سطر واحد واضح
- لا تكتب مقدمات"""

            similar_summary = self._format_similar_trades(similar_trades)

            user_prompt = f"""لقطة مراقبة دورية للصفقة المفتوحة يا عزيزي:

بيانات المؤشرات الحالية:
{json.dumps(snapshot, indent=2, ensure_ascii=False)}

الصفقات المشابهة السابقة:
{similar_summary}

فكر خطوة بخطوة ثم أعطِ التوصية."""

        elif context_mode == "entry":
            system_prompt = """أنت خبير تحليل فني متخصص في النفط والفضة يا صديقي.
يجب أن تفكر خطوة بخطوة قبل إعطاء التوصية.
اتبع هذه الخطوات:
1. تحليل قوة الإشارة (ADX, Volume, Trend Consistency)
2. تقييم المخاطر/العائد (RR, Distance to SL)
3. تحليل الصفقات المشابهة السابقة (نسبة النجاح)
4. تقييم حالة السوق العامة (Fear/Greed, MTF Trend)
5. التوصية النهائية (قوي / متوسط / ضعيف / انتظر)

قواعد:
- إذا نسبة نجاح الصفقات المشابهة > 60% → قوي
- إذا ADX > 25 و Volume قوي → قوي
- إذا RR < 1.5 → ضعيف
- إذا الإشارة معاكسة للاتجاه العام → ضعيف
- أعطِ التوصية في سطر واحد واضح"""

            similar_summary = self._format_similar_trades(similar_trades)

            user_prompt = f"""لقطة فنية لإشارة دخول جديدة يا عزيزي:

بيانات المؤشرات:
{json.dumps(snapshot, indent=2, ensure_ascii=False)}

الصفقات المشابهة السابقة:
{similar_summary}

فكر خطوة بخطوة ثم أعطِ تقييم الإشارة."""

        else:
            system_prompt = "أنت مستشار تداول يا صديقي."
            user_prompt = json.dumps(snapshot, ensure_ascii=False)

        return system_prompt, user_prompt

    def _format_similar_trades(self, trades: List[Dict]) -> str:
        if not trades:
            return "لا توجد صفقات سابقة مشابهة."

        lines = []
        for i, trade in enumerate(trades, 1):
            vector = trade.get("vector", {})
            lines.append(f"""صفقة #{i}:
- النتيجة: {trade.get('profit_bucket', 'غير معروف')}
- سبب الخروج: {trade.get('exit_reason', 'غير معروف')}
- RSI عند الدخول: {vector.get('rsi', 'N/A')}
- ADX عند الدخول: {vector.get('adx', 'N/A')}
- الربح: {vector.get('profit', 'N/A')}$""")

        return "\n".join(lines)

    def analyze(self, snapshot: dict, similar_trades: List[Dict], 
                context_mode: str = "monitoring") -> str:
        """تحليل CoT كامل"""
        if not self.api_key:
            return "⚠️ مفتاح API غير متوفر يا صديقي."

        if not self._can_request():
            return "⏳ تجاوز حد الطلبات. انتظر قليلاً يا عزيزي."

        try:
            import requests
            system_prompt, user_prompt = self.build_cot_prompt(snapshot, similar_trades, context_mode)

            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,  # منخفض للتفكير المنطقي
                "max_tokens": 500
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            self._last_request_time = time.time()

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            return f"⚠️ خطأ API: {response.status_code}"

        except Exception as e:
            logging.error(f"🧠 CoT Engine: خطأ: {e}")
            return "⚠️ تعذر التحليل يا صديقي."


# =====================================================================
# 🎓 متعلم الأنماط (Pattern Learner)
# =====================================================================

class PatternLearner:
    """
    يتعلم من الصفقات المغلقة ويُنشئ قواعد ديناميكية
    مثال: "إذا RSI < 35 و ADX > 25 → نسبة النجاح 75%"
    """

    def __init__(self, db_path="learning_data/memory.db"):
        self.db_path = db_path
        self._rules = []
        self._min_samples = 3  # الحد الأدنى للعينة
        self._confidence_threshold = 0.65  # 65% ثقة

    def learn_from_history(self, asset_type: str = None) -> List[Dict]:
        """تعلم الأنماط من التاريخ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT trade_type, rsi_bucket, adx_bucket, trend, profit_bucket, COUNT(*) as count
            FROM trade_vectors
        """
        params = []
        if asset_type:
            query += " WHERE asset_type = ?"
            params.append(asset_type)
        query += " GROUP BY trade_type, rsi_bucket, adx_bucket, trend, profit_bucket"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # بناء قواعد
        new_rules = []

        # تجميع حسب الشروط
        conditions = {}
        for row in rows:
            trade_type, rsi_b, adx_b, trend, profit_b, count = row
            key = (trade_type, rsi_b, adx_b, trend)
            if key not in conditions:
                conditions[key] = {"total": 0, "wins": 0, "losses": 0}
            conditions[key]["total"] += count
            if profit_b in ["small", "good", "excellent"]:
                conditions[key]["wins"] += count
            else:
                conditions[key]["losses"] += count

        for (trade_type, rsi_b, adx_b, trend), stats in conditions.items():
            if stats["total"] < self._min_samples:
                continue

            win_rate = stats["wins"] / stats["total"]

            if win_rate >= self._confidence_threshold:
                new_rules.append({
                    "type": "positive",
                    "condition": f"{trade_type} + RSI:{rsi_b} + ADX:{adx_b} + Trend:{trend}",
                    "win_rate": win_rate,
                    "samples": stats["total"],
                    "action": "strong_buy" if trade_type == "BUY" else "strong_sell",
                    "confidence": "high" if win_rate > 0.75 else "medium"
                })
            elif win_rate <= (1 - self._confidence_threshold):
                new_rules.append({
                    "type": "negative",
                    "condition": f"{trade_type} + RSI:{rsi_b} + ADX:{adx_b} + Trend:{trend}",
                    "win_rate": win_rate,
                    "samples": stats["total"],
                    "action": "avoid",
                    "confidence": "high" if win_rate < 0.25 else "medium"
                })

        self._rules = sorted(new_rules, key=lambda x: x["win_rate"], reverse=True)
        return self._rules

    def evaluate_signal(self, trade_type: str, rsi: float, adx: float, trend: str) -> Dict:
        """تقييم إشارة بناءً على القواعد المكتسبة"""
        rsi_buckets = [("oversold", 0, 30), ("low", 30, 45), ("mid", 45, 65), ("high", 65, 80), ("overbought", 80, 100)]
        adx_buckets = [("weak", 0, 20), ("moderate", 20, 35), ("strong", 35, 100)]

        rsi_b = self._get_bucket(rsi, rsi_buckets)
        adx_b = self._get_bucket(adx, adx_buckets)

        matching_rules = [r for r in self._rules 
                         if r["condition"] == f"{trade_type} + RSI:{rsi_b} + ADX:{adx_b} + Trend:{trend}"]

        if matching_rules:
            best = matching_rules[0]
            return {
                "has_rule": True,
                "win_rate": best["win_rate"],
                "action": best["action"],
                "confidence": best["confidence"],
                "samples": best["samples"],
                "recommendation": f"📊 نمط مكتشف يا صديقي: نسبة نجاح {best['win_rate']*100:.0f}% ({best['samples']} عينة)"
            }

        return {
            "has_rule": False,
            "win_rate": 0.5,
            "action": "neutral",
            "confidence": "low",
            "samples": 0,
            "recommendation": "📊 لا يوجد نمط تاريخي كافٍ لهذه الشروط يا عزيزي."
        }

    def _get_bucket(self, value: float, buckets: list) -> str:
        for bucket_name, (low, high) in buckets:
            if low <= value < high:
                return bucket_name
        return buckets[-1][0]

    def get_rules_summary(self) -> str:
        """ملخص القواعد المكتسبة"""
        if not self._rules:
            return "🧠 لا توجد قواعد مكتسبة بعد يا صديقي."

        lines = ["🧠 **القواعد المكتسبة من التاريخ:**", ""]
        for rule in self._rules[:10]:
            emoji = "✅" if rule["type"] == "positive" else "❌"
            lines.append(f"{emoji} {rule['condition']}")
            lines.append(f"   نسبة النجاح: {rule['win_rate']*100:.0f}% | عينات: {rule['samples']} | ثقة: {rule['confidence']}")

        return "\n".join(lines)


# =====================================================================
# 🧠 العقل الخارق الموحد (AI Brain Facade)
# =====================================================================

class AIBrain:
    """
    الواجهة الرئيسية للعقل الخارق
    تجمع RAG + CoT + Pattern Learning في مكان واحد

    الاستخدام:
    from ai_brain import AIBrain
    brain = AIBrain(groq_api_key="...")

    # عند فتح صفقة
    result = brain.evaluate_entry(snapshot)

    # عند مراقبة
    result = brain.evaluate_monitoring(snapshot, trade_id)

    # تعلم من صفقة مغلقة
    brain.learn(trade_data)
    """

    def __init__(self, groq_api_key: str = "", db_path="learning_data/memory.db"):
        self.rag = RAGMemory(db_path=db_path)
        self.cot = ChainOfThoughtEngine(api_key=groq_api_key)
        self.learner = PatternLearner(db_path=db_path)
        self.db_path = db_path
        self._last_learn_time = 0

    def evaluate_entry(self, snapshot: dict) -> Dict:
        """تقييم إشارة دخول جديدة"""
        asset = snapshot.get("asset", "oil")
        trade_type = snapshot.get("type", "BUY")
        rsi = snapshot.get("rsi_fast_7", 50)
        adx = snapshot.get("adx_14", 15)
        trend = snapshot.get("trend", "صاعد")

        # 1. استرجاع الصفقات المشابهة (RAG)
        similar = self.rag.retrieve_similar(asset, trade_type, rsi, adx, trend, top_k=5)

        # 2. تقييم بناءً على الأنماط المكتسبة
        pattern_eval = self.learner.evaluate_signal(trade_type, rsi, adx, trend)

        # 3. تحليل CoT (إذا كان API متوفراً)
        cot_advice = ""
        if self.cot.api_key:
            cot_advice = self.cot.analyze(snapshot, similar, context_mode="entry")

        return {
            "signal_strength": pattern_eval["action"],
            "confidence": pattern_eval["confidence"],
            "historical_win_rate": pattern_eval["win_rate"],
            "similar_trades_count": len(similar),
            "pattern_recommendation": pattern_eval["recommendation"],
            "ai_advice": cot_advice,
            "rag_context": similar
        }

    def evaluate_monitoring(self, snapshot: dict, trade_id: str = "") -> Dict:
        """تقييم لقطة مراقبة دورية"""
        asset = snapshot.get("asset", "oil")
        trade_type = snapshot.get("trade_type", "BUY")
        rsi = snapshot.get("rsi", 50)
        adx = snapshot.get("adx", 15)
        trend = snapshot.get("trend", "صاعد")

        # 1. استرجاع الصفقات المشابهة
        similar = self.rag.retrieve_similar(asset, trade_type, rsi, adx, trend, top_k=3)

        # 2. تحليل CoT
        cot_advice = ""
        if self.cot.api_key:
            cot_advice = self.cot.analyze(snapshot, similar, context_mode="monitoring")

        return {
            "ai_advice": cot_advice,
            "similar_trades": similar,
            "timestamp": datetime.now().isoformat()
        }

    def learn(self, trade_data: dict):
        """تعلم من صفقة مغلقة"""
        try:
            context = TradeContext(
                trade_id=trade_data.get("trade_id", str(time.time())),
                asset_type=trade_data.get("asset_type", "oil"),
                entry_price=trade_data.get("entry_price", 0),
                exit_price=trade_data.get("exit_price", 0),
                trade_type=trade_data.get("type", "UNKNOWN"),
                profit_dollars=trade_data.get("profit_dollars", 0),
                exit_reason=trade_data.get("exit_reason", "unknown"),
                rsi_at_entry=trade_data.get("rsi_at_entry", 50),
                adx_at_entry=trade_data.get("adx_at_entry", 15),
                trend=trade_data.get("trend", "neutral"),
                lessons=trade_data.get("lessons", ""),
                success_score=1 if trade_data.get("profit_dollars", 0) > 0 else 0,
                timestamp=trade_data.get("timestamp", datetime.now().isoformat())
            )

            # فهرسة في RAG
            self.rag.index_trade(context)

            # إعادة تعلم الأنماط كل 5 صفقات
            if time.time() - self._last_learn_time > 300:  # كل 5 دقائق على الأقل
                self.learner.learn_from_history(context.asset_type)
                self._last_learn_time = time.time()

            logging.info(f"🧠 تولين: تم تعلم صفقة {context.trade_id}")

        except Exception as e:
            logging.error(f"🧠 تولين: خطأ في التعلم: {e}")

    def get_learning_report(self) -> str:
        """تقرير التعلم"""
        return self.learner.get_rules_summary()

    def refresh_patterns(self, asset_type: str = None):
        """تحديث الأنماط يدوياً"""
        self.learner.learn_from_history(asset_type)
        logging.info("🧠 تولين: تم تحديث الأنماط")


# =====================================================================
# 🔌 مثال على الاستخدام
# =====================================================================

if __name__ == "__main__":
    brain = AIBrain(groq_api_key="test")

    # مثال تقييم دخول
    snapshot = {
        "asset": "oil",
        "type": "BUY",
        "rsi_fast_7": 35,
        "adx_14": 28,
        "trend": "صاعد",
        "entry_price": 75.5
    }

    result = brain.evaluate_entry(snapshot)
    print(json.dumps(result, indent=2, ensure_ascii=False))
