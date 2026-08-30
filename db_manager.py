"""
🗄️ db_manager.py - مدير قاعدة البيانات الموحد
👨‍💻 المطور: بسام الحوباني
💙 الاسم الشخصي: تولين

يدير جميع اتصالات قاعدة البيانات في مكان واحد
"""

import os
import sqlite3
import logging
from datetime import datetime
from threading import Lock

logger = logging.getLogger("TonaPrometheus")

class DatabaseManager:
    """
    مدير قاعدة البيانات الموحد - يضمن عمل جميع قواعد البيانات بشكل صحيح
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.base_dir = "learning_data"
        self.connections = {}
        self._ensure_directories()
        self._init_all_databases()
        logger.info("🗄️ Database Manager: مدير قاعدة البيانات جاهز!")
    
    def _ensure_directories(self):
        """إنشاء المجلدات المطلوبة"""
        folders = [
            self.base_dir,
            os.path.join(self.base_dir, "exports"),
            os.path.join(self.base_dir, "backups")
        ]
        
        for folder in folders:
            try:
                if not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
                    logger.info(f"📁 تم إنشاء المجلد: {folder}")
            except Exception as e:
                logger.error(f"❌ فشل إنشاء المجلد {folder}: {e}")
    
    def _init_all_databases(self):
        """تهيئة جميع قواعد البيانات"""
        databases = {
            "memory": self._init_memory_db,
            "trades": self._init_trades_db,
            "context": self._init_context_db,
            "learning": self._init_learning_db
        }
        
        for name, init_func in databases.items():
            try:
                init_func()
                logger.info(f"✅ قاعدة البيانات {name} جاهزة")
            except Exception as e:
                logger.error(f"❌ فشل تهيئة قاعدة البيانات {name}: {e}")
    
    def _get_db_path(self, filename):
        """الحصول على مسار قاعدة البيانات"""
        return os.path.join(self.base_dir, filename)
    
    def _init_memory_db(self):
        """تهيئة قاعدة بيانات الذاكرة"""
        db_path = self._get_db_path("memory.db")
        
        # ✅ الإصلاح: التأكد من وجود الملف والصلاحيات
        try:
            # اختبار الكتابة
            with open(db_path, 'a') as f:
                pass
        except Exception as e:
            logger.warning(f"⚠️ مشكلة في صلاحيات {db_path}: {e}")
            # استخدام مسار بديل
            db_path = os.path.join(os.path.expanduser("~"), ".tona_bot", "memory.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            logger.info(f"📁 استخدام مسار بديل: {db_path}")
        
        conn = sqlite3.connect(db_path, timeout=30)
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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
        self.connections["memory"] = db_path
        logger.info(f"💾 قاعدة بيانات الذاكرة: {db_path}")
    
    def _init_trades_db(self):
        """تهيئة قاعدة بيانات الصفقات"""
        db_path = self._get_db_path("trades.db")
        
        try:
            with open(db_path, 'a') as f:
                pass
        except:
            db_path = os.path.join(os.path.expanduser("~"), ".tona_bot", "trades.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # جدول الصفقات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                asset_type TEXT,
                trade_type TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_dollars REAL,
                entry_rsi REAL,
                entry_adx REAL,
                trend_at_entry TEXT,
                exit_reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exit_timestamp DATETIME,
                status TEXT DEFAULT 'open',
                warnings_log TEXT,
                entry_indicators TEXT
            )
        """)
        
        # جدول المراقبة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT,
                snapshot_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                rsi REAL,
                adx REAL,
                macd REAL,
                trend TEXT,
                volume_ratio REAL,
                warning_level INTEGER DEFAULT 0
            )
        """)
        
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
        self.connections["trades"] = db_path
        logger.info(f"📊 قاعدة بيانات الصفقات: {db_path}")
    
    def _init_context_db(self):
        """تهيئة قاعدة بيانات السياق"""
        db_path = self._get_db_path("context_memory.db")
        
        try:
            with open(db_path, 'a') as f:
                pass
        except:
            db_path = os.path.join(os.path.expanduser("~"), ".tona_bot", "context_memory.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # جدول سياق السوق
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT,
                timeframe TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                indicators TEXT,
                price REAL,
                trend TEXT,
                volatility REAL,
                sentiment TEXT
            )
        """)
        
        # جدول نظام السوق
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_regime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_type TEXT,
                date TEXT,
                regime TEXT,
                confidence REAL,
                features TEXT
            )
        """)
        
        # جدول الأحداث
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                asset_type TEXT,
                description TEXT,
                impact TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        self.connections["context"] = db_path
        logger.info(f"📖 قاعدة بيانات السياق: {db_path}")
    
    def _init_learning_db(self):
        """تهيئة قاعدة بيانات التعلم"""
        db_path = self._get_db_path("learning.db")
        
        try:
            with open(db_path, 'a') as f:
                pass
        except:
            db_path = os.path.join(os.path.expanduser("~"), ".tona_bot", "learning.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path, timeout=30)
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
        self.connections["learning"] = db_path
        logger.info(f"🧠 قاعدة بيانات التعلم: {db_path}")
    
    def get_connection(self, db_name):
        """الحصول على اتصال بقاعدة البيانات"""
        db_path = self.connections.get(db_name)
        if not db_path:
            logger.error(f"❌ قاعدة البيانات {db_name} غير موجودة")
            return None
        
        try:
            conn = sqlite3.connect(db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"❌ فشل الاتصال بقاعدة البيانات {db_name}: {e}")
            return None
    
    def execute_query(self, db_name, query, params=None):
        """تنفيذ استعلام على قاعدة البيانات"""
        conn = self.get_connection(db_name)
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"❌ فشل تنفيذ الاستعلام: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_paths(self):
        """الحصول على جميع مسارات قواعد البيانات"""
        return self.connections.copy()


# =====================================================================
# ✅ إنشاء كائن واحد للاستخدام في جميع الملفات
# =====================================================================

db_manager = DatabaseManager()

def get_db_manager():
    """الحصول على مدير قاعدة البيانات"""
    return db_manager
