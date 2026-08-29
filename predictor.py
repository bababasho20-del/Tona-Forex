"""التوقع - Predictor Module"""
import sqlite3
import json
import os
import logging
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger("TonaPrometheus")

class Predictor:
    """نظام التنبؤ المستند إلى أرشيف التعلم"""

    def __init__(self, db_path="learning_data/trades.db"):
        # ✅ الإصلاح: التأكد من وجود المجلد
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"📁 تم إنشاء المجلد: {db_dir}")
            except Exception as e:
                logger.error(f"❌ فشل إنشاء المجلد {db_dir}: {e}")
                # استخدام مسار بديل
                home_dir = os.path.expanduser("~")
                db_path = os.path.join(home_dir, ".tona_bot", "trades.db")
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                logger.info(f"📁 استخدام مسار بديل: {db_path}")
        
        self.db_path = db_path
        self._init_db()
        logger.info(f"🔮 Predictor جاهز: {db_path}")

    def _init_db(self):
        """تهيئة قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type TEXT,
                    prediction_type TEXT,
                    confidence REAL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ قاعدة بيانات التنبؤات جاهزة")
        except Exception as e:
            logger.error(f"❌ فشل تهيئة قاعدة البيانات: {e}")

    def predict_before_entry(self, asset_type, current_conditions):
        """تنبؤ مسبق قبل فتح الصفقة"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entry_price, trade_type, profit_dollars, exit_reason,
                       entry_rsi, entry_adx, trend_at_entry, timestamp
                FROM trades WHERE asset_type = ? AND status = 'closed'
                ORDER BY timestamp DESC LIMIT 50
            """, (asset_type,))
            trades = cursor.fetchall()
            conn.close()

            if len(trades) < 20:
                return {
                    "status": "insufficient_data",
                    "message": f"{len(trades)} trades only, need at least 20",
                    "prediction": None
                }

            similar = self._find_similar_trades(trades, current_conditions)

            if not similar:
                return {
                    "status": "no_similar",
                    "message": "No similar trades found",
                    "prediction": None
                }

            wins = sum(1 for t in similar if t[2] > 0)
            total = len(similar)
            win_rate = wins / total if total > 0 else 0
            avg_profit = statistics.mean([t[2] for t in similar]) if similar else 0

            if win_rate > 0.7 and avg_profit > 0:
                prediction = "strong_buy" if current_conditions.get("type") == "BUY" else "strong_sell"
                confidence = win_rate
            elif win_rate > 0.5 and avg_profit > 0:
                prediction = "moderate_buy" if current_conditions.get("type") == "BUY" else "moderate_sell"
                confidence = win_rate
            elif win_rate < 0.3:
                prediction = "avoid"
                confidence = 1 - win_rate
            else:
                prediction = "uncertain"
                confidence = 0.5

            warnings = []
            if current_conditions.get("rsi", 50) > 70:
                warnings.append("RSI in overbought zone")
            if current_conditions.get("rsi", 50) < 30:
                warnings.append("RSI in oversold zone")
            if current_conditions.get("adx", 15) < 20:
                warnings.append("ADX weak - no clear trend")

            return {
                "status": "success",
                "prediction": prediction,
                "confidence": round(confidence, 2),
                "win_rate": round(win_rate, 2),
                "avg_profit": round(avg_profit, 2),
                "similar_trades": total,
                "warnings": warnings,
                "message": self._format_prediction_message(prediction, confidence, win_rate, avg_profit, warnings)
            }
        except Exception as e:
            logger.error(f"❌ فشل التنبؤ: {e}")
            return {
                "status": "error",
                "message": str(e),
                "prediction": None
            }

    def _find_similar_trades(self, trades, conditions):
        """البحث عن صفقات مشابهة"""
        similar = []
        trade_type = conditions.get("type")
        rsi = conditions.get("rsi", 50)
        adx = conditions.get("adx", 15)
        trend = conditions.get("trend", "")

        for trade in trades:
            if trade[1] != trade_type:
                continue
            score = 0
            if trade[4] and abs(trade[4] - rsi) < 10:
                score += 1
            if trade[5] and abs(trade[5] - adx) < 5:
                score += 1
            if trade[6] and trade[6] == trend:
                score += 1
            if score >= 2:
                similar.append(trade)

        return similar[:10]

    def _format_prediction_message(self, prediction, confidence, win_rate, avg_profit, warnings):
        """تنسيق رسالة التنبؤ"""
        messages = {
            "strong_buy": "Strong BUY prediction! Archive supports this signal.",
            "strong_sell": "Strong SELL prediction! Archive supports this signal.",
            "moderate_buy": "Moderate BUY prediction. Watch closely.",
            "moderate_sell": "Moderate SELL prediction. Watch closely.",
            "avoid": "Warning: Archive indicates high risk. Think twice.",
            "uncertain": "Unclear situation. Wait for additional confirmation."
        }

        msg = messages.get(prediction, "No prediction available")
        msg += "\nExpected Win Rate: " + str(int(win_rate * 100)) + "%"
        msg += "\nExpected Avg Profit: $" + "{:.2f}".format(avg_profit)

        if warnings:
            msg += "\nWarnings:"
            for w in warnings:
                msg += "\n- " + w

        return msg

    def predict_monitoring(self, asset_type, trade_id, current_snapshot):
        """تنبؤ أثناء المراقبة"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT snapshot, timestamp FROM monitoring
                WHERE trade_id = ? ORDER BY timestamp DESC LIMIT 10
            """, (trade_id,))
            snapshots = cursor.fetchall()
            conn.close()

            if len(snapshots) < 3:
                return {"status": "insufficient", "message": "Insufficient monitoring data"}

            rsi_values = []
            adx_values = []
            for snap in snapshots:
                data = json.loads(snap[0])
                rsi_values.append(data.get("rsi", 50))
                adx_values.append(data.get("adx", 15))

            rsi_trend = "improving" if rsi_values[-1] > rsi_values[0] else "deteriorating"
            adx_trend = "improving" if adx_values[-1] > adx_values[0] else "deteriorating"

            return {
                "status": "success",
                "rsi_trend": rsi_trend,
                "adx_trend": adx_trend,
                "recommendation": "continue" if rsi_trend == "improving" else "caution"
            }
        except Exception as e:
            logger.error(f"❌ فشل تنبؤ المراقبة: {e}")
            return {"status": "error", "message": str(e)}

    def get_predictions(self, market_context=None):
        """الحصول على التنبؤات (واجهة للتوافق)"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prediction_type, confidence, details, created_at
                FROM predictions
                ORDER BY created_at DESC LIMIT 5
            """)
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "type": row[0],
                    "confidence": row[1],
                    "details": row[2],
                    "created_at": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"❌ فشل جلب التنبؤات: {e}")
            return []
