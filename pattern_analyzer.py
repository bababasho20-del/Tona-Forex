"""محلل الأنماط - Pattern Analyzer Module"""
import sqlite3
import json
import os
import logging
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger("TonaPrometheus")

class PatternAnalyzer:
    """اكتشاف وتحليل الأنماط من أرشيف الصفقات"""

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
        logger.info(f"🔍 PatternAnalyzer جاهز: {db_path}")

    def _init_db(self):
        """تهيئة قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # جدول الأنماط
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_type TEXT,
                    pattern_type TEXT,
                    pattern_name TEXT,
                    description TEXT,
                    recommendation TEXT,
                    confidence REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ قاعدة بيانات الأنماط جاهزة")
        except Exception as e:
            logger.error(f"❌ فشل تهيئة قاعدة البيانات: {e}")

    def find_patterns(self, asset_type, min_trades=20):
        """البحث عن أنماط في الصفقات المغلقة"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entry_price, exit_price, trade_type, profit_dollars, exit_reason,
                       entry_rsi, entry_adx, trend_at_entry, timestamp
                FROM trades WHERE asset_type = ? AND status = 'closed'
                ORDER BY timestamp DESC LIMIT 100
            """, (asset_type,))
            trades = cursor.fetchall()
            conn.close()

            if len(trades) < min_trades:
                return {"status": "insufficient_data", "message": f"{len(trades)} صفقة فقط"}

            patterns = []

            # Pattern 1: SL too tight
            sl_trades = [t for t in trades if t[4] == "Hit Stop Loss"]
            if len(sl_trades) >= 5:
                sl_losses = [t[3] for t in sl_trades]
                avg_sl_loss = statistics.mean(sl_losses) if sl_losses else 0
                win_after_sl = len([t for t in trades if t[4] == "Hit Take Profit"])
                if avg_sl_loss < -1.5 and win_after_sl > len(sl_trades) * 0.5:
                    patterns.append({
                        "type": "tight_sl",
                        "name": "وقف الخسارة الضيق",
                        "description": f"{len(sl_trades)} صفقات خسرت بسبب ضيق SL. متوسط الخسارة: {avg_sl_loss:.2f}$",
                        "recommendation": "وسع SL إلى 1.5× ATR",
                        "confidence": min(len(sl_trades) / 10, 1.0)
                    })

            # Pattern 2: RSI extreme at entry
            rsi_wins = [t for t in trades if t[3] > 0 and t[5] is not None]
            rsi_losses = [t for t in trades if t[3] < 0 and t[5] is not None]
            if rsi_wins and rsi_losses:
                avg_rsi_win = statistics.mean([t[5] for t in rsi_wins]) if rsi_wins else 50
                avg_rsi_loss = statistics.mean([t[5] for t in rsi_losses]) if rsi_losses else 50
                if avg_rsi_loss > 65 or avg_rsi_loss < 35:
                    patterns.append({
                        "type": "rsi_extreme",
                        "name": "RSI متطرف عند الدخول",
                        "description": f"RSI متوسط للصفقات الخاسرة: {avg_rsi_loss:.1f}",
                        "recommendation": "تجنب الدخول عند RSI > 65 أو < 35",
                        "confidence": 0.8
                    })

            # Pattern 3: ADX weak
            adx_losses = [t for t in trades if t[3] < 0 and t[6] is not None]
            if adx_losses:
                avg_adx_loss = statistics.mean([t[6] for t in adx_losses]) if adx_losses else 0
                if avg_adx_loss < 20:
                    patterns.append({
                        "type": "weak_adx",
                        "name": "ADX ضعيف عند الدخول",
                        "description": f"ADX متوسط للصفقات الخاسرة: {avg_adx_loss:.1f}",
                        "recommendation": "انتظر ADX > 20 قبل الدخول",
                        "confidence": 0.75
                    })

            # Pattern 4: Trend reversal during monitoring
            trend_reversal = [t for t in trades if t[3] < 0 and t[7] and t[7] != ("صاعد" if t[2] == "BUY" else "هابط")]
            if len(trend_reversal) >= 3:
                patterns.append({
                    "type": "trend_reversal",
                    "name": "انعكاس الاتجاه خلال المراقبة",
                    "description": f"{len(trend_reversal)} صفقات خسرت بسبب انعكاس الاتجاه",
                    "recommendation": "أغلق فوراً عند انعكاس الاتجاه",
                    "confidence": min(len(trend_reversal) / 5, 1.0)
                })

            # Pattern 5: Manual close success
            manual_trades = [t for t in trades if t[4] == "أمر يدوي من المستخدم"]
            if len(manual_trades) >= 3:
                manual_profits = [t[3] for t in manual_trades]
                avg_manual = statistics.mean(manual_profits) if manual_profits else 0
                patterns.append({
                    "type": "manual_close",
                    "name": "إغلاق يدوي متكرر",
                    "description": f"{len(manual_trades)} إغلاق يدوي، متوسط: {avg_manual:.2f}$",
                    "recommendation": "استراتيجية الدخول تحتاج مراجعة" if avg_manual < 0 else "الإغلاق اليدوي ناجح",
                    "confidence": 0.7
                })

            # Pattern 6: Time-based
            tp_trades = [t for t in trades if t[4] == "Hit Take Profit"]
            if len(tp_trades) >= 10:
                win_rate = len(tp_trades) / len(trades)
                patterns.append({
                    "type": "high_win_rate",
                    "name": "نسبة نجاح ممتازة",
                    "description": f"نسبة النجاح: {win_rate*100:.1f}% ({len(tp_trades)}/{len(trades)})",
                    "recommendation": "استمر على نفس الاستراتيجية" if win_rate > 0.5 else "راجع الاستراتيجية",
                    "confidence": win_rate
                })

            return {
                "status": "success",
                "total_trades": len(trades),
                "patterns_found": len(patterns),
                "patterns": patterns
            }
        except Exception as e:
            logger.error(f"❌ فشل البحث عن الأنماط: {e}")
            return {"status": "error", "message": str(e)}

    def predict_outcome(self, asset_type, current_conditions):
        """التنبؤ بنتيجة الصفقة بناءً على الأنماط"""
        patterns = self.find_patterns(asset_type, min_trades=20)
        if patterns["status"] != "success":
            return {"prediction": "unknown", "confidence": 0, "reason": "بيانات غير كافية"}

        score = 0.5
        warnings = []

        for pattern in patterns.get("patterns", []):
            if pattern["type"] == "tight_sl" and current_conditions.get("atr_multiplier", 2) < 1.5:
                score -= 0.1
                warnings.append("⚠️ SL قد يكون ضيقاً")
            if pattern["type"] == "rsi_extreme":
                rsi = current_conditions.get("rsi", 50)
                if rsi > 65 or rsi < 35:
                    score -= 0.15
                    warnings.append("⚠️ RSI متطرف")
            if pattern["type"] == "weak_adx":
                adx = current_conditions.get("adx", 15)
                if adx < 20:
                    score -= 0.1
                    warnings.append("⚠️ ADX ضعيف")

        prediction = "success" if score > 0.6 else "caution" if score > 0.4 else "risk"

        return {
            "prediction": prediction,
            "confidence": round(score, 2),
            "warnings": warnings,
            "patterns": patterns.get("patterns", [])
        }
    
    def get_patterns(self, market_context=None):
        """الحصول على الأنماط (واجهة للتوافق)"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pattern_type, pattern_name, description, recommendation, confidence
                FROM patterns
                ORDER BY created_at DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "type": row[0],
                    "name": row[1],
                    "description": row[2],
                    "recommendation": row[3],
                    "confidence": row[4]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"❌ فشل جلب الأنماط: {e}")
            return []
