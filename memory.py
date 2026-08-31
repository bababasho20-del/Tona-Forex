"""
💾 الذاكرة الأساسية - Memory Module
🧠 تولين: تخزين المحادثات وملفات المستخدمين والبيانات الأساسية
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger("TonaPrometheus")

class Memory:
    """
    ذاكرة المحادثة والبيانات الأساسية
    
    تقوم بتخزين:
    - سجل المحادثات لكل مستخدم
    - ملفات تعريف المستخدمين
    - تفضيلات التداول
    - الحالة المزاجية
    """
    
    def __init__(self, db_path: str = "learning_data/memory.db"):
        """
        تهيئة الذاكرة
        
        Args:
            db_path: مسار قاعدة البيانات
        """
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
                db_path = os.path.join(home_dir, ".tona_bot", "memory.db")
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                logger.info(f"📁 استخدام مسار بديل: {db_path}")
        
        self.db_path = db_path
        self._init_db()
        logger.info(f"💾 Memory: الذاكرة جاهزة يا صديقي! (مسار: {db_path})")
    
    def _init_db(self):
        """تهيئة قاعدة البيانات مع معالجة الأخطاء"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # جدول المحادثات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    trading_style TEXT,
                    user_mood TEXT,
                    intent TEXT,
                    sentiment_score REAL
                )
            """)
            
            # جدول ملفات المستخدمين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    trading_style TEXT DEFAULT 'neutral',
                    risk_tolerance TEXT DEFAULT 'moderate',
                    preferred_assets TEXT DEFAULT 'eurusd,usdjpy',
                    message_count INTEGER DEFAULT 0,
                    last_mood TEXT DEFAULT 'neutral',
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    experience_level TEXT DEFAULT 'beginner',
                    preferred_timeframe TEXT DEFAULT '1h'
                )
            """)
            
            # جدول التعليمات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_teachings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    trigger_phrase TEXT,
                    teaching TEXT,
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
                )
            """)
            
            # جدول إحصائيات يومية
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date TEXT,
                    messages_count INTEGER DEFAULT 0,
                    trades_count INTEGER DEFAULT 0,
                    profit_loss REAL DEFAULT 0,
                    mood TEXT,
                    UNIQUE(user_id, date)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ قاعدة البيانات جاهزة يا عزيزي")
            
        except Exception as e:
            logger.error(f"❌ فشل تهيئة قاعدة البيانات: {e}")
            raise
    
    # =================================================================
    # دوال المحادثة
    # =================================================================
    
    def add_message(self, user_id: str, role: str, content: str, 
                   trading_style: Optional[str] = None, 
                   user_mood: Optional[str] = None,
                   intent: Optional[str] = None,
                   sentiment_score: Optional[float] = None) -> bool:
        """
        إضافة رسالة إلى الذاكرة
        
        Args:
            user_id: معرف المستخدم
            role: دور المرسل (user/assistant)
            content: نص الرسالة
            trading_style: أسلوب التداول (اختياري)
            user_mood: مزاج المستخدم (اختياري)
            intent: نية المستخدم (اختياري)
            sentiment_score: درجة المشاعر (اختياري)
        
        Returns:
            bool: نجاح العملية
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations 
                (user_id, role, content, trading_style, user_mood, intent, sentiment_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, role, content, trading_style, user_mood, intent, sentiment_score))
            
            # الحفاظ على آخر 50 رسالة فقط لكل مستخدم
            cursor.execute("""
                DELETE FROM conversations WHERE id NOT IN (
                    SELECT id FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50
                )
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            # تحديث ملف المستخدم
            self._update_user_profile(user_id, trading_style, user_mood)
            
            # تحديث الإحصائيات اليومية
            self._update_daily_stats(user_id, user_mood)
            
            logger.debug(f"✅ تم إضافة رسالة للمستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل إضافة الرسالة: {e}")
            return False
    
    def get_conversation(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        جلب المحادثة الأخيرة
        
        Args:
            user_id: معرف المستخدم
            limit: عدد الرسائل المطلوبة
        
        Returns:
            List[Dict]: قائمة الرسائل
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role, content, timestamp, user_mood, intent
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in reversed(rows):  # ترتيب زمني
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "user_mood": row[3],
                    "intent": row[4]
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ فشل جلب المحادثة: {e}")
            return []
    
    def get_last_message(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        جلب آخر رسالة للمستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            Optional[Dict]: آخر رسالة
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role, content, timestamp, user_mood, intent
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "user_mood": row[3],
                    "intent": row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ فشل جلب آخر رسالة: {e}")
            return None
    
    # =================================================================
    # دوال حفظ واسترجاع
    # =================================================================
    
    def save(self, user_id: str, user_message: str, bot_response: str, context: dict = None) -> bool:
        """
        حفظ محادثة كاملة (واجهة للتوافق)
        
        Args:
            user_id: معرف المستخدم
            user_message: رسالة المستخدم
            bot_response: رد البوت
            context: سياق إضافي (اختياري)
        
        Returns:
            bool: نجاح العملية
        """
        try:
            # حفظ رسالة المستخدم
            self.add_message(
                user_id=user_id,
                role="user",
                content=user_message,
                intent=context.get("intent") if context else None,
                sentiment_score=context.get("sentiment_score") if context else None
            )
            
            # حفظ رد البوت
            self.add_message(
                user_id=user_id,
                role="assistant",
                content=bot_response,
                trading_style=context.get("trading_style") if context else None,
                user_mood=context.get("user_mood") if context else None
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ المحادثة: {e}")
            return False
    
    def get_recent(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        جلب المحادثة الأخيرة (واجهة للتوافق)
        
        Args:
            user_id: معرف المستخدم
            limit: عدد الرسائل المطلوبة
        
        Returns:
            List[Dict]: قائمة الرسائل
        """
        return self.get_conversation(user_id, limit)
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        جلب ملف المستخدم (واجهة للتوافق)
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            Dict: ملف المستخدم
        """
        return self.get_user_profile(user_id)
    
    # =================================================================
    # دوال ملفات المستخدمين
    # =================================================================
    
    def _update_user_profile(self, user_id: str, trading_style: Optional[str], mood: Optional[str]):
        """تحديث ملف المستخدم"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_profiles (user_id, trading_style, last_mood, message_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    trading_style = COALESCE(?, trading_style),
                    last_mood = COALESCE(?, last_mood),
                    message_count = message_count + 1,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, trading_style, mood, trading_style, mood))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ فشل تحديث ملف المستخدم: {e}")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        جلب ملف المستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            Dict: ملف المستخدم
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT trading_style, risk_tolerance, preferred_assets, 
                       message_count, last_mood, experience_level, preferred_timeframe
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "trading_style": row[0] or "neutral",
                    "risk_tolerance": row[1] or "moderate",
                    "preferred_assets": row[2].split(",") if row[2] else ["eurusd", "usdjpy"],
                    "message_count": row[3] or 0,
                    "last_mood": row[4] or "neutral",
                    "experience_level": row[5] or "beginner",
                    "preferred_timeframe": row[6] or "1h"
                }
            
            # إنشاء ملف جديد للمستخدم
            return {
                "trading_style": "neutral",
                "risk_tolerance": "moderate",
                "preferred_assets": ["eurusd", "usdjpy"],
                "message_count": 0,
                "last_mood": "neutral",
                "experience_level": "beginner",
                "preferred_timeframe": "1h"
            }
            
        except Exception as e:
            logger.error(f"❌ فشل جلب ملف المستخدم: {e}")
            return {
                "trading_style": "neutral",
                "risk_tolerance": "moderate",
                "preferred_assets": ["eurusd", "usdjpy"],
                "message_count": 0,
                "last_mood": "neutral"
            }
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        تحديث تفضيلات المستخدم
        
        Args:
            user_id: معرف المستخدم
            preferences: التفضيلات الجديدة
        
        Returns:
            bool: نجاح العملية
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # بناء استعلام التحديث
            updates = []
            values = []
            
            for key, value in preferences.items():
                if key in ["trading_style", "risk_tolerance", "preferred_assets", 
                          "experience_level", "preferred_timeframe"]:
                    updates.append(f"{key} = ?")
                    if key == "preferred_assets" and isinstance(value, list):
                        values.append(",".join(value))
                    else:
                        values.append(value)
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            query = f"UPDATE user_profiles SET {', '.join(updates)} WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم تحديث تفضيلات المستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل تحديث التفضيلات: {e}")
            return False
    
    # =================================================================
    # دوال التعليم
    # =================================================================
    
    def save_user_teaching(self, user_id: str, trigger: str, teaching: str, context: str = "محادثة") -> bool:
        """
        حفظ تعليم المستخدم
        
        Args:
            user_id: معرف المستخدم
            trigger: الكلمة المفتاحية
            teaching: التعليم
            context: السياق
        
        Returns:
            bool: نجاح العملية
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_teachings (user_id, trigger_phrase, teaching, context)
                VALUES (?, ?, ?, ?)
            """, (user_id, trigger, teaching, context))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ تم حفظ تعليم للمستخدم {user_id}: '{trigger}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ التعليم: {e}")
            return False
    
    def get_user_teachings(self, user_id: str) -> List[Dict[str, str]]:
        """
        جلب تعليمات المستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            List[Dict]: قائمة التعليمات
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT trigger_phrase, teaching, context, timestamp
                FROM user_teachings
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "trigger": row[0],
                    "teaching": row[1],
                    "context": row[2],
                    "timestamp": row[3]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"❌ فشل جلب التعليمات: {e}")
            return []
    
    def clear_user_teachings(self, user_id: str) -> bool:
        """
        حذف تعليمات المستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            bool: نجاح العملية
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_teachings WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ تم حذف تعليمات المستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حذف التعليمات: {e}")
            return False
    
    # =================================================================
    # دوال الإحصائيات
    # =================================================================
    
    def _update_daily_stats(self, user_id: str, mood: Optional[str]):
        """تحديث الإحصائيات اليومية"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO daily_stats (user_id, date, messages_count, mood)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    messages_count = messages_count + 1,
                    mood = COALESCE(?, mood)
            """, (user_id, today, mood, mood))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ فشل تحديث الإحصائيات اليومية: {e}")
    
    def get_user_stats(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        جلب إحصائيات المستخدم
        
        Args:
            user_id: معرف المستخدم
            days: عدد الأيام الماضية
        
        Returns:
            Dict: الإحصائيات
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            # جلب الإحصائيات اليومية
            cursor.execute("""
                SELECT date, messages_count, mood
                FROM daily_stats
                WHERE user_id = ? AND date >= date('now', ?)
                ORDER BY date DESC
            """, (user_id, f"-{days} days"))
            
            daily_rows = cursor.fetchall()
            
            # جلب الإحصائيات العامة
            cursor.execute("""
                SELECT COUNT(*) as total_messages,
                       COUNT(DISTINCT date) as active_days,
                       (SELECT mood FROM daily_stats 
                        WHERE user_id = ? AND date = (SELECT MAX(date) FROM daily_stats WHERE user_id = ?)) as last_mood
                FROM daily_stats
                WHERE user_id = ?
            """, (user_id, user_id, user_id))
            
            stats_row = cursor.fetchone()
            conn.close()
            
            daily_stats = [
                {
                    "date": row[0],
                    "messages": row[1],
                    "mood": row[2]
                }
                for row in daily_rows
            ]
            
            return {
                "total_messages": stats_row[0] if stats_row else 0,
                "active_days": stats_row[1] if stats_row else 0,
                "last_mood": stats_row[2] if stats_row else "neutral",
                "daily_stats": daily_stats
            }
            
        except Exception as e:
            logger.error(f"❌ فشل جلب الإحصائيات: {e}")
            return {
                "total_messages": 0,
                "active_days": 0,
                "last_mood": "neutral",
                "daily_stats": []
            }
    
    # =================================================================
    # دوال مساعدة
    # =================================================================
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        مسح محادثة المستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            bool: نجاح العملية
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️ تم مسح محادثة المستخدم {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل مسح المحادثة: {e}")
            return False
    
    def get_all_users(self) -> List[str]:
        """
        جلب قائمة بجميع المستخدمين
        
        Returns:
            List[str]: قائمة معرفات المستخدمين
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM user_profiles")
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"❌ فشل جلب المستخدمين: {e}")
            return []


# =====================================================================
# دالة مساعدة للاستخدام السريع
# =====================================================================

def create_memory(db_path: str = "learning_data/memory.db") -> Memory:
    """إنشاء كائن ذاكرة جديد"""
    return Memory(db_path)


# =====================================================================
# اختبار سريع
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 اختبار Memory")
    print("=" * 60)
    
    # إنشاء ذاكرة
    memory = Memory("learning_data/test_memory.db")
    
    # اختبار إضافة رسالة
    print("\n1️⃣ إضافة رسائل:")
    memory.add_message("user_001", "user", "مرحباً، كيف حالك؟", user_mood="neutral")
    memory.add_message("user_001", "assistant", "أهلاً بك يا صديقي! أنا بخير.", user_mood="happy")
    memory.add_message("user_001", "user", "أريد تحليل النفط", user_mood="confident")
    print("   ✅ تم إضافة 3 رسائل")
    
    # اختبار جلب المحادثة
    print("\n2️⃣ جلب المحادثة:")
    conversation = memory.get_conversation("user_001")
    for msg in conversation:
        print(f"   {msg['role']}: {msg['content']}")
    
    # اختبار ملف المستخدم
    print("\n3️⃣ ملف المستخدم:")
    profile = memory.get_user_profile("user_001")
    print(f"   أسلوب التداول: {profile['trading_style']}")
    print(f"   المخاطرة: {profile['risk_tolerance']}")
    print(f"   الأصول المفضلة: {profile['preferred_assets']}")
    print(f"   عدد الرسائل: {profile['message_count']}")
    print(f"   المزاج الأخير: {profile['last_mood']}")
    
    print("\n✅ اختبار Memory ناجح!")
