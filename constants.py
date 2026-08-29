# -*- coding: utf-8 -*-
"""
constants.py - المتغيرات العامة، الثوابت، وإعدادات التسجيل (Logging)
يحتوي على جميع التعريفات العامة المستخدمة في جميع أنحاء البوت.
"""

import os
import time
import logging
import threading
import queue
from logging.handlers import RotatingFileHandler
from datetime import datetime

# =====================================================================
# مفاتيح API والمتغيرات البيئية
# =====================================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# =====================================================================
# GitHub Gist
# =====================================================================

GIST_BASE_URL = "https://api.github.com/gists"
GIST_IDS = {
    "trades_oil": os.getenv("GIST_TRADES_OIL", ""),
    "trades_silver": os.getenv("GIST_TRADES_SILVER", ""),
    "config": os.getenv("GIST_CONFIG", ""),
    "narrative": os.getenv("GIST_NARRATIVE", ""),
}
GIST_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

# =====================================================================
# ملفات البيانات
# =====================================================================

TRADES_FILE_OIL = "trades_history_oil.json"
TRADES_FILE_SILVER = "trades_history_silver.json"
CURRENT_POSITION_FILE_OIL = "current_position_oil.json"
CURRENT_POSITION_FILE_SILVER = "current_position_silver.json"

# =====================================================================
# الأقفال (Locks) للعمليات المتزامنة
# =====================================================================

FILE_LOCKS = {"oil": threading.Lock(), "silver": threading.Lock()}
GROQ_REQUEST_LOG = []
GROQ_MAX_REQUESTS_PER_MINUTE = 20
GROQ_REQUEST_LOCK = threading.Lock()
TELEGRAM_QUEUE = queue.Queue()
MONITOR_TRIGGER = {"oil": None, "silver": None}
MONITOR_TRIGGER_LOCK = threading.Lock()
CURRENT_OFFSET = 0
OFFSET_LOCK = threading.Lock()
last_signal_states = {"oil": {"signal": "WAIT", "time": 0}, "silver": {"signal": "WAIT", "time": 0}}
last_signal_time = {"oil": 0, "silver": 0}
LAST_SIGNAL_LOCK = threading.Lock()
SIGNAL_COOLDOWN = 3600

# =====================================================================
# التخزين المؤقت
# =====================================================================

ANALYSIS_CACHE = {}
ANALYSIS_CACHE_TTL = 15  # ثانية

# =====================================================================
# سياق المحادثة
# =====================================================================

CONVERSATION_CONTEXTS = {}  # chat_id -> list of messages (max 20)
CONVERSATION_CONTEXT_LIMIT = 20

# =====================================================================
# التقارير والتصدير
# =====================================================================

LAST_DAILY_REPORT = None
LAST_MARKET_REPORT = None
LAST_EXPORT = datetime.now().isoformat()
DAILY_REPORT_TIME = "08:00"
SIGNAL_CHECK_INTERVAL = 60
MONITORING_INTERVAL = 300
EXPORT_INTERVAL_DAYS = 10

# =====================================================================
# مؤشر الخوف والطمع (Fear & Greed)
# =====================================================================

FEAR_GREED_CACHE = {
    "value": "محايد ومتزن (50/100)",
    "timestamp": 0
}
FEAR_GREED_CACHE_TTL = 300

# =====================================================================
# تعريفات المحركات (تُستخدم في chat.py وملفات أخرى)
# =====================================================================

# Prometheus
PROMETHEUS_AVAILABLE = False
PROMETHEUS = None

# Chronos
CHRONOS_AVAILABLE = False
CHRONOS = None

# Oracle
ORACLE_AVAILABLE = False
ORACLE = None

# Dream
DREAM_AVAILABLE = False
DREAM = None

# Narrative
NARRATIVE_AVAILABLE = False
NARRATIVE = None

# Fusion
FUSION_AVAILABLE = False
FUSION = None

# TCN (شبكة الوعي)
TCN_AVAILABLE = False
TCN = None

# Memory
MEMORY_AVAILABLE = False
MEMORY = None

# Hybrid Orchestrator
HYBRID_ORCHESTRATOR = None

# أنظمة إضافية (قد تستخدم في المستقبل)
ANALYZER_AVAILABLE = False
MARKET_ANALYZER = None

INDICATORS_AVAILABLE = False
ADVANCED_INDICATORS = None

PATTERN_AVAILABLE = False
PATTERN_ANALYZER = None

PREDICTOR_AVAILABLE = False
PREDICTOR = None

LEARNER_AVAILABLE = False
LEARNER = None

RISK_MASTER_AVAILABLE = False
RISK_MASTER = None

DECISION_AVAILABLE = False
DECISION_MATRIX = None

CONFIDENCE_AVAILABLE = False
CONFIDENCE_SCORER = None

CONVICTION_AVAILABLE = False
CONVICTION_REPORT = None

POST_MORTEM_AVAILABLE = False
POST_MORTEM = None

SIMILAR_AVAILABLE = False
SIMILAR_ANALYZER = None

DEEP_ANALYZER_AVAILABLE = False
DEEP_ANALYZER = None

ADVISOR_AVAILABLE = False
ADVISOR = None

PERSONA_AVAILABLE = False
PERSONA = None

INTENT_AVAILABLE = False
INTENT_CLASSIFIER = None

LANGUAGE_AVAILABLE = False
LANGUAGE_UNDERSTANDING = None

CONTEXT_AVAILABLE = False
CONTEXT_MEMORY = None

CONTEXT_BUILDER_AVAILABLE = False
CONTEXT_BUILDER = None

CONVERSATION_AVAILABLE = False
CONVERSATION_ENGINE = None

AI_BRAIN_AVAILABLE = False
AI_BRAIN = None

TONA_ELITE_AVAILABLE = False
TONA_ELITE_ENGINE = None

LEARNING_AVAILABLE = False
LEARNING_SYSTEM = None

# =====================================================================
# إعدادات التسجيل (Logging)
# =====================================================================

logger = logging.getLogger("TonaPrometheus")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(threadName)s] - [%(filename)s:%(lineno)d] - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = RotatingFileHandler(
    "hobany_radar.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# =====================================================================
# إشعارات بدء التشغيل (للتأكد من تحميل المتغيرات)
# =====================================================================

print(f"✅ TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10] if TELEGRAM_TOKEN else 'غير موجود'}...")
print(f"✅ CHAT_ID: {CHAT_ID if CHAT_ID else 'غير موجود'}")
print(f"✅ GROQ_API_KEY: {'موجود' if GROQ_API_KEY else 'غير موجود'}")
print(f"✅ GEMINI_API_KEY: {'موجود' if GEMINI_API_KEY else 'غير موجود'}")
print(f"✅ NEWS_API_KEY: {'موجود' if NEWS_API_KEY else 'غير موجود'}")
print(f"✅ GITHUB_TOKEN: {'موجود' if GITHUB_TOKEN else 'غير موجود'}")
