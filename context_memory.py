"""سياق السوق - Context Memory Module"""
import sqlite3
import json
from datetime import datetime
import os

class ContextMemory:
    """إدارة سياق السوق والمؤشرات التاريخية"""

    def __init__(self, db_path="learning_data/context_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

    def save_context(self, asset_type, timeframe, indicators, price, trend, volatility, sentiment):
        """حفظ سياق السوق"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO market_context (asset_type, timeframe, indicators, price, trend, volatility, sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_type, timeframe, json.dumps(indicators), price, trend, volatility, sentiment))
        conn.commit()
        conn.close()

    def get_recent_context(self, asset_type, timeframe, limit=50):
        """جلب السياق الأخير"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT indicators, price, trend, volatility, sentiment, timestamp 
            FROM market_context 
            WHERE asset_type = ? AND timeframe = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (asset_type, timeframe, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{
            "indicators": json.loads(row[0]),
            "price": row[1],
            "trend": row[2],
            "volatility": row[3],
            "sentiment": row[4],
            "timestamp": row[5]
        } for row in rows]

    def save_regime(self, asset_type, regime, confidence, features):
        """حفظ نظام السوق (trending/ranging/volatile)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO market_regime (asset_type, date, regime, confidence, features)
            VALUES (?, ?, ?, ?, ?)
        """, (asset_type, datetime.now().strftime("%Y-%m-%d"), regime, confidence, json.dumps(features)))
        conn.commit()
        conn.close()

    def get_current_regime(self, asset_type):
        """جلب نظام السوق الحالي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT regime, confidence, features FROM market_regime
            WHERE asset_type = ? ORDER BY date DESC LIMIT 1
        """, (asset_type,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"regime": row[0], "confidence": row[1], "features": json.loads(row[2])}
        return {"regime": "unknown", "confidence": 0, "features": {}}
