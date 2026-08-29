"""التعلم الآلي - Learner Module"""
import sqlite3
import json
import os
import logging
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger("TonaPrometheus")

class Learner:
    """نظام التعلم الآلي من الصفقات"""

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
        logger.info(f"🧠 Learner جاهز: {db_path}")

    def _init_db(self):
        """تهيئة قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # جدول الدروس
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT,
                    lesson_type TEXT,
                    lesson_text TEXT,
                    recommendation TEXT,
                    importance REAL DEFAULT 0.5,
                    applied BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول الإحصائيات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ قاعدة بيانات التعلم جاهزة")
        except Exception as e:
            logger.error(f"❌ فشل تهيئة قاعدة البيانات: {e}")

    def learn_from_trade(self, trade_data):
        """التعلم من صفقة مغلقة"""
        lessons = []
        
        try:
            entry_price = trade_data.get("entry_price", 0)
            exit_price = trade_data.get("exit_price", 0)
            profit = trade_data.get("profit_dollars", 0)
            exit_reason = trade_data.get("exit_reason", "")
            rsi = trade_data.get("entry_rsi", 50)
            adx = trade_data.get("entry_adx", 15)
            trend = trade_data.get("trend_at_entry", "")
            trade_type = trade_data.get("type", "")
            trade_id = trade_data.get("trade_id", "")

            # Lesson 1: RSI extreme
            if rsi > 70 and profit < 0:
                lesson = {
                    "type": "rsi_overbought_loss",
                    "message": "RSI > 70 at entry led to loss",
                    "recommendation": "Avoid entry when RSI > 65"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)
                
            elif rsi < 30 and profit > 0:
                lesson = {
                    "type": "rsi_oversold_win",
                    "message": "RSI < 30 at entry led to profit",
                    "recommendation": "RSI < 30 is good buying opportunity"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

            # Lesson 2: ADX weak
            if adx < 20 and profit < 0:
                lesson = {
                    "type": "weak_adx_loss",
                    "message": "ADX < 20 at entry led to loss",
                    "recommendation": "Wait for ADX > 20 before entry"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)
                
            elif adx > 25 and profit > 0:
                lesson = {
                    "type": "strong_adx_win",
                    "message": "ADX > 25 at entry led to profit",
                    "recommendation": "ADX > 25 confirms strong trend"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

            # Lesson 3: Trend mismatch
            expected_trend = "Bullish" if trade_type == "BUY" else "Bearish"
            if trend != expected_trend and profit < 0:
                lesson = {
                    "type": "trend_mismatch",
                    "message": "Trend opposite to trade led to loss",
                    "recommendation": "Ensure trend aligns with trade type"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

            # Lesson 4: SL too tight
            if exit_reason == "Hit Stop Loss" and profit < -1:
                lesson = {
                    "type": "tight_sl",
                    "message": "Tight stop loss caused loss",
                    "recommendation": "Widen SL to 1.5x ATR"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

            # Lesson 5: Manual close
            if exit_reason == "Manual order":
                if profit > 0:
                    lesson = {
                        "type": "manual_close_win",
                        "message": "Manual close was successful",
                        "recommendation": "Your judgment is good"
                    }
                else:
                    lesson = {
                        "type": "manual_close_loss",
                        "message": "Manual close was premature",
                        "recommendation": "Review entry strategy"
                    }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

            # Lesson 6: Strong warning
            if exit_reason == "Strong warning - auto close":
                lesson = {
                    "type": "strong_warning",
                    "message": "Strong warning saved from bigger loss",
                    "recommendation": "Trust strong warnings"
                }
                lessons.append(lesson)
                self._save_lesson(trade_id, lesson)

        except Exception as e:
            logger.error(f"❌ فشل التعلم من الصفقة: {e}")

        return lessons

    def _save_lesson(self, trade_id, lesson):
        """حفظ درس في قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO lessons (trade_id, lesson_type, lesson_text, recommendation, importance)
                VALUES (?, ?, ?, ?, ?)
            """, (
                trade_id,
                lesson.get("type", ""),
                lesson.get("message", ""),
                lesson.get("recommendation", ""),
                0.7
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ تم حفظ درس للصفقة {trade_id}")
        except Exception as e:
            logger.error(f"❌ فشل حفظ الدرس: {e}")

    def generate_weekly_report(self, asset_type):
        """تقرير أسبوعي للتعلم"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()

            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*), AVG(profit_dollars), SUM(profit_dollars),
                       COUNT(CASE WHEN profit_dollars > 0 THEN 1 END),
                       COUNT(CASE WHEN profit_dollars < 0 THEN 1 END)
                FROM trades WHERE asset_type = ? AND timestamp > ? AND status = 'closed'
            """, (asset_type, week_ago))
            row = cursor.fetchone()
            
            # جلب الدروس المستفادة
            cursor.execute("""
                SELECT lesson_type, lesson_text, recommendation
                FROM lessons
                WHERE created_at > ?
                ORDER BY created_at DESC LIMIT 5
            """, (week_ago,))
            lessons = cursor.fetchall()
            
            conn.close()

            if not row or row[0] == 0:
                return "No closed trades this week"

            total, avg_profit, total_profit, wins, losses = row
            win_rate = (wins / total * 100) if total > 0 else 0

            report = "=== WEEKLY LEARNING REPORT - " + asset_type.upper() + " ==="
            report += "\n" + "=" * 40
            report += "\nTotal Trades: " + str(total)
            report += "\nWins: " + str(wins) + " | Losses: " + str(losses)
            report += "\nWin Rate: " + "{:.1f}".format(win_rate) + "%"
            report += "\nAvg Profit: $" + "{:.2f}".format(avg_profit)
            report += "\nTotal P/L: $" + "{:.2f}".format(total_profit)
            report += "\n" + "=" * 40 + "\n"

            if win_rate > 60:
                report += "✅ Excellent performance! Keep the same approach.\n"
            elif win_rate > 45:
                report += "🟡 Acceptable performance. Review losing trades.\n"
            else:
                report += "🔴 Weak performance. Strategy review needed.\n"

            if lessons:
                report += "\n📚 Lessons learned this week:\n"
                for lesson in lessons:
                    report += f"• {lesson[1]}\n"
                    report += f"  💡 {lesson[2]}\n"

            return report
        except Exception as e:
            logger.error(f"❌ فشل إنشاء التقرير: {e}")
            return "❌ حدث خطأ في إنشاء التقرير"

    def suggest_improvements(self, asset_type):
        """اقتراحات تحسين"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT exit_reason, COUNT(*), AVG(profit_dollars)
                FROM trades WHERE asset_type = ? AND status = 'closed'
                GROUP BY exit_reason
            """, (asset_type,))
            reasons = cursor.fetchall()
            conn.close()

            suggestions = []

            for reason, count, avg_profit in reasons:
                if reason == "Hit Stop Loss" and avg_profit < -1:
                    suggestions.append("🛡️ Stop loss too tight: Try 1.5x ATR")
                elif reason == "Reverse Signal" and avg_profit < 0:
                    suggestions.append("🔄 Reverse signals: Wait for additional confirmation")
                elif reason == "Liquidation":
                    suggestions.append("⚠️ Liquidation: Reduce leverage or increase margin")

            return suggestions
        except Exception as e:
            logger.error(f"❌ فشل جلب الاقتراحات: {e}")
            return ["❌ حدث خطأ في جلب الاقتراحات"]
