# =====================================================================
# 🧠 learning_system.py - نظام التعلم الذكي لتولين (بأمر)
# =====================================================================

import re
import logging
import sqlite3
import os
from datetime import datetime

logger = logging.getLogger("TonaPrometheus")

class LearningSystem:
    """
    نظام التعلم الذكي يا صديقي.
    يتعلم فقط عندما تطلب ذلك بشكل صريح.
    """
    
    def __init__(self, memory=None, db_path=None):
        """
        تهيئة نظام التعلم.
        يمكن استقبال memory (للتوافق القديم) أو db_path (للتوافق الجديد).
        """
        # ✅ الإصلاح: التأكد من وجود المجلد
        if db_path:
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                    logger.info(f"📁 تم إنشاء المجلد: {db_dir}")
                except Exception as e:
                    logger.error(f"❌ فشل إنشاء المجلد {db_dir}: {e}")
                    # استخدام مسار بديل
                    home_dir = os.path.expanduser("~")
                    db_path = os.path.join(home_dir, ".tona_bot", "learning.db")
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
                    logger.info(f"📁 استخدام مسار بديل: {db_path}")
            
            self.db_path = db_path
            self._init_db()
            self.memory = None
        else:
            self.memory = memory
            self.db_path = None
        
        self.learning_mode = False  # وضع التعلم مغلق افتراضياً
        self.pending_teaching = None
        logger.info(f"✅ LearningSystem جاهز يا صديقي (db_path={db_path}, memory={memory is not None})")
    
    def _init_db(self):
        """إنشاء قاعدة البيانات إذا كانت غير موجودة"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # جدول التعليمات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_teachings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_phrase TEXT,
                    teaching TEXT,
                    context TEXT,
                    timestamp TEXT
                )
            ''')
            
            # جدول الصفقات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE,
                    asset_type TEXT,
                    trade_type TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    profit REAL,
                    entry_rsi REAL,
                    entry_adx REAL,
                    trend_at_entry TEXT,
                    exit_reason TEXT,
                    timestamp TEXT
                )
            ''')
            
            # جدول المراقبة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT,
                    snapshot_time TEXT,
                    price REAL,
                    rsi REAL,
                    adx REAL,
                    macd REAL,
                    trend TEXT
                )
            ''')
            
            # جدول الدروس
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT,
                    lesson_type TEXT,
                    lesson_text TEXT,
                    recommendation TEXT,
                    importance REAL DEFAULT 0.5,
                    applied BOOLEAN DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"✅ قاعدة البيانات جاهزة يا عزيزي: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ فشل إنشاء قاعدة البيانات: {e}")
    
    def _get_conn(self):
        """الحصول على اتصال بقاعدة البيانات"""
        if self.db_path:
            return sqlite3.connect(self.db_path, timeout=30)
        elif self.memory and hasattr(self.memory, 'conn'):
            return self.memory.conn
        else:
            # إنشاء قاعدة بيانات افتراضية
            home_dir = os.path.expanduser("~")
            self.db_path = os.path.join(home_dir, ".tona_bot", "learning.db")
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self._init_db()
            return sqlite3.connect(self.db_path, timeout=30)
    
    def learn_from_message(self, user_message):
        """
        تحليل الرسالة ومعالجتها.
        إذا كان في وضع التعلم، يحفظ التعليم.
        إذا طلب بدء أو إنهاء التعلم، ينفذ الأمر.
        """
        # 1. بدء وضع التعلم
        if re.search(r'(تعلم وافهم|ابدأ التعلم|علمني|دخل وضع التعلم)', user_message):
            self.learning_mode = True
            self.pending_teaching = None
            return "✅ **دخلت وضع التعلم يا صديقي.** 📚\nأخبرني ما تريد تعليمي إياه، ثم قل **'هذا يكفي'** أو **'انتهى'** أو **'حفظ'**."
        
        # 2. إنهاء وضع التعلم
        if re.search(r'(هذا يكفي|انتهى|حفظ|خروج|كفاية)', user_message):
            if self.learning_mode and self.pending_teaching:
                # حفظ التعليم
                trigger, teaching = self.pending_teaching
                self.save_user_teaching(trigger, teaching, "محادثة")
                self.learning_mode = False
                self.pending_teaching = None
                return f"✅ **تم حفظ التعليم يا عزيزي!** 📝\nعندما تقول **'{trigger}'**، سأفهم أنها تعني: {teaching}."
            else:
                self.learning_mode = False
                self.pending_teaching = None
                return "✅ **تم الخروج من وضع التعلم.**"
        
        # 3. إذا كان في وضع التعلم
        if self.learning_mode:
            # استخراج التعليم
            match = re.search(r'([^\s]+)\s*(?:يعني|تعني|معناها|معناه|تعتبر|تعد|هي|هو)\s*(.+)', user_message)
            if match:
                trigger = match.group(1).strip()
                teaching = match.group(2).strip()
                self.pending_teaching = (trigger, teaching)
                return f"📖 **فهمت يا صديقي!** تريد تعليمي أن: **'{trigger}'** تعني **'{teaching}'**.\nقل **'هذا يكفي'** لتأكيد الحفظ، أو قل شيئاً آخر لتعديل التعليم."
            else:
                return "🤔 **لم أفهم ما تريد تعليمي إياه يا عزيزي.**\nقل مثلاً: **'مرحبا تعني تحية'** أو **'RSI تعني مؤشر القوة النسبية'**."
        
        # 4. ليس في وضع التعلم
        return None
    
    def save_user_teaching(self, trigger, teaching, context="محادثة"):
        """حفظ التعليم في قاعدة البيانات"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_teachings (trigger_phrase, teaching, context, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (trigger, teaching, context, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ فشل حفظ التعليم: {e}")
            return False
    
    def get_teachings_summary(self):
        """ملخص التعليمات"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            teachings = cursor.execute('''
                SELECT trigger_phrase, teaching, context, timestamp FROM user_teachings
                ORDER BY id DESC
            ''').fetchall()
            
            conn.close()
            
            if not teachings:
                return "📭 **لا توجد تعليمات مسجلة بعد يا صديقي.**"
            
            summary = "🧠 **ما تعلمته منك يا عزيزي:**\n\n"
            for trigger, teaching, context, timestamp in teachings:
                summary += f"• **'{trigger}'** → {teaching}\n"
            return summary
        except Exception as e:
            logger.error(f"❌ فشل جلب التعليمات: {e}")
            return "❌ حدث خطأ في جلب التعليمات يا صديقي."
    
    def clear_teachings(self):
        """حذف جميع التعليمات"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_teachings")
            conn.commit()
            conn.close()
            return "🗑️ **تم حذف جميع التعليمات يا عزيزي.**"
        except Exception as e:
            logger.error(f"❌ فشل حذف التعليمات: {e}")
            return "❌ حدث خطأ في حذف التعليمات يا صديقي."
    
    # ================================================================
    # دوال إضافية للتوافق مع main.py
    # ================================================================
    
    def record_new_trade(self, asset_type, trade_data, indicators):
        """تسجيل صفقة جديدة (للتوافق)"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trades 
                (trade_id, asset_type, trade_type, entry_price, 
                 entry_rsi, entry_adx, trend_at_entry, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('trade_id'),
                asset_type,
                trade_data.get('type'),
                trade_data.get('entry_price'),
                indicators.get('rsi'),
                indicators.get('adx'),
                indicators.get('trend'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ فشل تسجيل الصفقة: {e}")
            return False
    
    def save_monitoring_snapshot(self, trade_id, asset_type, snapshot):
        """حفظ لقطة مراقبة (للتوافق)"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring 
                (trade_id, snapshot_time, price, rsi, adx, macd, trend)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_id,
                datetime.now().isoformat(),
                snapshot.get('price'),
                snapshot.get('rsi'),
                snapshot.get('adx'),
                snapshot.get('macd'),
                snapshot.get('trend_15m')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ فشل حفظ المراقبة: {e}")
            return False
    
    def record_trade_lesson(self, lesson_data):
        """تسجيل درس مستفاد (للتوافق)"""
        try:
            profit = lesson_data.get('profit_dollars', 0)
            trade_type = lesson_data.get('trade_type', '')
            exit_reason = lesson_data.get('exit_reason', '')
            
            if profit > 0:
                lesson_text = f"صفقة {trade_type} ناجحة يا صديقي: {exit_reason}. استمر بنفس الاستراتيجية."
            else:
                lesson_text = f"صفقة {trade_type} خاسرة يا عزيزي: {exit_reason}. راجع نقاط الدخول والخروج."
            
            return self.save_user_teaching(
                f"درس_صفقة_{lesson_data.get('trade_id', '')}",
                lesson_text,
                "تعلم_تلقائي"
            )
        except Exception as e:
            logger.error(f"❌ فشل تسجيل الدرس: {e}")
            return False
    
    def learn_from_trade(self, trade_data):
        """تعلم من صفقة (للتوافق)"""
        lessons = []
        profit = trade_data.get('profit_dollars', 0)
        
        if profit > 0:
            lessons.append({
                'message': f"✅ صفقة رابحة يا صديقي: استمر في البحث عن إشارات مشابهة (ربح ${profit:.2f})"
            })
        else:
            lessons.append({
                'message': f"❌ صفقة خاسرة يا عزيزي: تجنب الدخول في ظروف مشابهة (خسارة ${abs(profit):.2f})"
            })
        
        return lessons
    
    def generate_weekly_report(self, asset_type=None):
        """تقرير أسبوعي (للتوافق)"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            query = "SELECT * FROM trades"
            params = []
            if asset_type:
                query += " WHERE asset_type = ?"
                params.append(asset_type)
            
            cursor.execute(query, params)
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return "📊 لا توجد صفقات مسجلة يا صديقي."
            
            total = len(trades)
            winning = len([t for t in trades if t[6] and t[6] > 0])
            losing = len([t for t in trades if t[6] and t[6] < 0])
            win_rate = (winning / total * 100) if total > 0 else 0
            
            report = f"📊 <b>تقرير التعلم</b>\n"
            report += f"📈 إجمالي الصفقات: {total}\n"
            report += f"✅ الصفقات الرابحة: {winning}\n"
            report += f"❌ الصفقات الخاسرة: {losing}\n"
            report += f"📊 نسبة النجاح: {win_rate:.1f}%\n"
            
            return report
        except Exception as e:
            logger.error(f"❌ فشل إنشاء التقرير: {e}")
            return "❌ حدث خطأ في إنشاء التقرير يا صديقي."

# ================================================================
# ✅ تصدير الاسم المطلوب من main.py
# ================================================================

TradeLearningSystem = LearningSystem
