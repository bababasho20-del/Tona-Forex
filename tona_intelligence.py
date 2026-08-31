"""
🧠 Tona Elite Intelligence Engine - V5.5 (النسخة النهائية المستقرة)
محرك الاستخبارات - جلب وتحليل الأخبار وتأثيرها على النفط والفضة مع ربط زمني دقيق

✅ التحسينات الجذورية في V5.5:
- إصلاح فقدان الذاكرة النشطة (جعـل _active_news متغيراً على مستوى الوحدة)
- تقليل طلبات MEXC API عبر جلب الشموع مرة واحدة لكل دورة تحليل
- حل مشكلة الاستيراد الدائري عبر حقن التبعية (candle_fetcher)
- جعل التقرير يعتمد على الأرقام الفعلية من الشارت بدلاً من تفسيرات Groq النصية
- إضافة فحص صارم لحداثة الأخبار (تجاهل الأخبار الأقدم من ساعتين قبل التحليل)
- ✅ إصلاح خطأ تواريخ Python: can't subtract offset-naive and offset-aware datetimes
- ✅ إزالة الجداول والرموز الغريبة من التقرير، واستخدام نصوص واضحة ومباشرة
- ✅ تحسين صياغة التقرير ليكون مفيداً وقابلاً للقراءة
- إزالة التحليل النصي للأخبار الذي يسبب تفسيرات وهمية
- عرض التأثير الفعلي فقط (التغير المئوي خلال 15 و 60 دقيقة)
- تحسين إدارة الذاكرة المؤقتة مع تنظيف تلقائي
- إضافة دالة get_engine() لاستخدام مثيل واحد فقط من المحرك
- حماية كاملة من None وقيم فارغة مع سجلات تشخيصية مفصلة
"""

import os
import time
import json
import requests
import logging
import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import xml.etree.ElementTree as ET
import traceback
import threading
import threading

# =====================================================================
# ⚙️ الإعدادات الأساسية
# =====================================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# =====================================================================
# 🗂️ ذاكرة الترجمة المؤقتة
# =====================================================================

TRANSLATION_CACHE = {}
CACHE_TTL = 3600

# عتبات التأثير: نفصل بين أهمية الخبر وبين الحركة السعرية المقاسة.
IMPACT_THRESHOLDS = {
    "low": 0.15,
    "medium": 0.30,
    "high": 0.50,
    "very_high": 1.00,
}
NEWS_LOOKBACK_HOURS = 6
MIN_SOURCE_CONSENSUS = 2

# =====================================================================
# 📦 الذاكرة العامة للأخبار المؤثرة (مشتركة بين جميع المثيلات)
# =====================================================================
_GLOBAL_ACTIVE_NEWS = []  # ✅ متغير على مستوى الوحدة لمنع فقدان البيانات

# =====================================================================
# 🏭 مثيل واحد من المحرك (Singleton)
# =====================================================================
_ENGINE_INSTANCE = None


class TonaEliteEngine:
    def __init__(self, memory=None, market_analyzer=None, groq_api_key=None, news_api_key=None, candle_fetcher=None):
        self.memory = memory
        self.market_analyzer = market_analyzer
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.news_api_key = news_api_key or NEWS_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # ✅ ربط الذاكرة العامة (بدلاً من إنشاء قائمة جديدة)
        self._active_news = _GLOBAL_ACTIVE_NEWS

        # ✅ تخزين دالة جلب الشموع (حقن التبعية لحل الاستيراد الدائري)
        self.candle_fetcher = candle_fetcher
        self._radar_alert_history = {}
        self._radar_alert_times = []
        self._radar_lock = threading.Lock()
        self._last_fetch_stats = {"sources_total":0,"sources_ok":0,"sources_failed":0,"raw_items":0,"filtered_items":0,"unique_items":0,"errors":[]}
        self._last_report_status = {"provider":"none","reason":"not_run"}
        self._last_candles_data = {}
        self._last_candles_data = {}

        self.trusted_sources = [
            "Reuters", "Bloomberg", "CNBC", "Financial Times", "Wall Street Journal",
            "The Economist", "Forbes", "Business Insider", "MarketWatch",
            "Oil Price", "Energy Voice", "Platts", "Argus Media",
            "FT", "WSJ", "BBC", "CNN", "Al Jazeera", "Sky News",
            "الجزيرة", "العربية", "سكاي نيوز عربية", "واس", "وام"
        ]

        self.exclude_keywords = [
            "sport", "football", "cricket", "tennis", "basketball",
            "entertainment", "celebrity", "movie", "music", "concert",
            "hollywood", "oscar", "wedding", "gift", "party", "birthday",
            "royal", "king", "queen", "prince", "princess",
            "fashion", "style", "beauty", "makeup"
        ]

        self.required_keywords = [
            "oil", "crude", "petroleum", "brent", "wti", "opec",
            "silver", "gold", "precious metals", "xag", "xau",
            "inflation", "federal reserve", "fed", "interest rate",
            "dollar", "usd", "economy", "recession", "growth",
            "geopolitical", "war", "conflict", "crisis", "tension",
            "sanctions", "embargo", "houthi", "red sea", "suez",
            "hormuz", "strait", "middle east", "iran", "russia",
            "ukraine", "israel", "gaza", "yemen", "arabia",
            "نفط", "بترول", "خام", "برنت", "أوبك",
            "فضة", "ذهب", "معادن ثمينة",
            "جيوسياسي", "حرب", "صراع", "أزمة", "توتر",
            "ترمب", "بايدن", "البيت الأبيض", "الكونغرس",
            "أوكرانيا", "روسيا", "إيران", "إسرائيل", "غزة", "الحوثي"
        ]

        logging.info("✅ Tona Elite Intelligence Engine V5.5 initialized (تقرير نظيف وقابل للقراءة)")

    # =====================================================================
    # 📰 جلب الأخبار
    # =====================================================================

    def _fetch_rss_feed(self, feed_url, max_items=8):
        try:
            response = requests.get(feed_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = []
                for item in root.findall('.//item')[:max_items]:
                    title = item.find('title')
                    desc = item.find('description')
                    pub_date = item.find('pubDate')
                    link = item.find('link')
                    if title is not None and title.text:
                        items.append({
                            "title": str(title.text) if title.text is not None else "",
                            "description": str(desc.text) if desc is not None and desc.text is not None else "",
                            "url": str(link.text) if link is not None and link.text is not None else "",
                            "source": feed_url.split('/')[2],
                            "published_at": str(pub_date.text) if pub_date is not None and pub_date.text is not None else datetime.now().isoformat(),
                            "is_trusted": True
                        })
                return items
            return []
        except Exception as e:
            logging.debug(f"RSS error {feed_url}: {e}")
            return []

    def fetch_targeted_intelligence(self, hours=10):
        all_news = []

        rss_feeds = [
            # مصادر إنجليزية
            "https://feeds.reuters.com/reuters/commoditiesNews",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.ft.com/commodities?format=rss",
            "https://oilprice.com/rss/energy-news",
            "https://oilprice.com/rss/geopolitics",
            "https://www.marketwatch.com/rss/commodities",
            "https://www.bloomberg.com/feed/commodities",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://www.dw.com/en/english-news/rss",
            "https://feeds.skynews.com/feeds/rss/world.xml",
            # مصادر عربية
            "https://www.aljazeera.net/feeds/rss",
            "https://www.alarabiya.net/feed/rss",
            "https://www.skynewsarabia.com/rss",
            "https://www.saudigazette.com.sa/rss/feed",
            "https://www.wam.ae/ar/feed"
        ]

        for feed_url in rss_feeds:
            items = self._fetch_rss_feed(feed_url)
            for item in items:
                if not item:
                    continue
                text = (str(item.get("title", "")) + " " + str(item.get("description", ""))).lower()
                if any(k in text for k in self.exclude_keywords):
                    continue
                if any(k in text for k in self.required_keywords):
                    all_news.append(item)

        if self.news_api_key and self.news_api_key != "":
            queries = [
                ("oil OR crude OR petroleum OR OPEC", "oil"),
                ("silver OR XAG OR gold", "silver"),
                ("Middle East OR Iran OR Israel OR Gaza OR Houthi", "geopolitical"),
                ("Federal Reserve OR inflation OR interest rate", "economic"),
                ("Russia OR Ukraine OR sanctions", "geopolitical")
            ]
            for query, _ in queries:
                try:
                    from_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%S')
                    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=relevance&language=en&apiKey={self.news_api_key}&pageSize=10"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get("articles", []):
                            if not article:
                                continue
                            title = str(article.get("title")) if article.get("title") is not None else ""
                            description = str(article.get("description")) if article.get("description") is not None else ""
                            text = (title + " " + description).lower()
                            if any(k in text for k in self.exclude_keywords):
                                continue
                            if any(k in text for k in self.required_keywords):
                                all_news.append({
                                    "title": title,
                                    "description": description,
                                    "url": str(article.get("url")) if article.get("url") is not None else "",
                                    "source": str(article.get("source", {}).get("name")) if article.get("source", {}).get("name") is not None else "NewsAPI",
                                    "published_at": str(article.get("publishedAt")) if article.get("publishedAt") is not None else datetime.now().isoformat(),
                                    "is_trusted": True
                                })
                except Exception as e:
                    logging.debug(f"NewsAPI error: {e}")

        # إزالة التكرارات
        seen = set()
        unique = []
        for news in all_news:
            if not news:
                continue
            key = str(news.get("title", ""))[:50] or str(hashlib.md5(str(news).encode()).hexdigest())[:10]
            if key not in seen:
                seen.add(key)
                unique.append(news)

        logging.info(f"📰 تم جلب {len(unique)} خبراً فريداً")
        return unique[:40]

    # =====================================================================
    # 📊 ربط الأخبار بالشارت (محسّن بنقاط زمنية متعددة واستخدام كاش)
    # =====================================================================

    def _get_price_at_time(self, asset_type: str, minutes_ago: int = 5, candles_data: Dict = None) -> Optional[float]:
        """
        الحصول على سعر الأصل عند نقطة زمنية محددة.
        - إذا تم تمرير candles_data، نستخدمه مباشرة (لا طلب API).
        - وإلا نستخدم candle_fetcher إن وُجد.
        - وإلا نستخدم الاستيراد المحلي كحل أخير مع تحذير.
        """
        # ✅ 1. استخدام البيانات المخزنة مسبقاً (الأفضل)
        if candles_data and asset_type in candles_data:
            data = candles_data[asset_type]
            if data and data.get("closes") and len(data["closes"]) >= abs(minutes_ago) + 1:
                if minutes_ago >= 0:
                    idx = min(minutes_ago, len(data["closes"]) - 1)
                    return data["closes"][-idx - 1] if idx < len(data["closes"]) else data["closes"][-1]
                return data["closes"][-1]
            return None

        # ✅ 2. استخدام دالة الجلب المحقونة (حقن التبعية)
        if self.candle_fetcher:
            try:
                return self.candle_fetcher(asset_type, minutes_ago)
            except Exception as e:
                logging.debug(f"⚠️ فشل candle_fetcher: {e}")

        # ✅ 3. الحل الاحتياطي النهائي (مع تحذير لتجنب الاستيراد الدائري)
        try:
            from main import get_forex_candles as get_mexc_candles
            symbol = "USOIL_USDT" if asset_type == "oil" else "SILVER_USDT"
            limit = abs(minutes_ago) + 5
            if limit > 500:
                limit = 500
            data = get_mexc_candles(symbol, "Min1", limit)
            if data and data.get("closes") and len(data["closes"]) >= abs(minutes_ago) + 1:
                if minutes_ago >= 0:
                    idx = min(minutes_ago, len(data["closes"]) - 1)
                    return data["closes"][-idx - 1] if idx < len(data["closes"]) else data["closes"][-1]
                return data["closes"][-1]
        except Exception as e:
            logging.debug(f"⚠️ فشل جلب السعر (حل احتياطي): {e}")
        return None

    def _parse_published_time(self, published_at: str) -> Optional[datetime]:
        """تحويل النص الزمني إلى كائن datetime مع دعم تنسيقات متعددة"""
        if not published_at:
            return None
        try:
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%d %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(published_at, fmt)
                except:
                    continue
            match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', published_at)
            if match:
                return datetime.fromisoformat(match.group(1))
            return None
        except Exception as e:
            logging.debug(f"⚠️ فشل تحويل الوقت: {e}")
            return None

    def _ensure_naive(self, dt: datetime) -> datetime:
        """تحويل datetime إلى naive (بدون منطقة زمنية) لتجنب أخطاء الطرح"""
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

    def _news_asset(self, news_item: Dict) -> str:
        """تحديد الأصل الأكثر ارتباطاً بالخبر دون افتراض أن كل خبر للنفط."""
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        silver_terms = ["silver", "xag", "precious metal", "فضة", "ذهب", "معادن ثمينة"]
        oil_terms = ["oil", "crude", "brent", "wti", "opec", "petroleum", "نفط", "خام", "أوبك", "برنت"]
        geo_terms = ["iran", "hormuz", "strait of hormuz", "houthi", "red sea", "suez", "middle east", "iran", "israel", "gaza", "yemen", "russia", "ukraine", "sanctions", "إيران", "مضيق هرمز", "البحر الأحمر", "غزة", "اليمن"]
        ss = sum(1 for k in silver_terms if k in text)
        oo = sum(1 for k in oil_terms if k in text)
        gg = sum(1 for k in geo_terms if k in text)
        if ss > oo and ss > 0:
            return "silver"
        if oo > 0 or gg > 0:
            return "oil"
        return "oil/silver"


    def _news_potential(self, news_item: Dict) -> Dict:
        """
        تقدير القوة الأساسية للخبر قبل النظر إلى حركة السعر.
        هذا ليس دليلاً على التأثير؛ بل طبقة "قابلية تأثير" مستقلة.
        """
        title = self._safe_str(news_item.get("title"))
        desc = self._safe_str(news_item.get("description"))
        text = f"{title} {desc}".lower()

        high = [
            "opec", "opec+", "fed", "federal reserve", "interest rate", "rate cut",
            "sanctions", "embargo", "hormuz", "strait of hormuz", "war", "attack",
            "ceasefire", "iran", "israel", "russia", "ukraine", "tariff", "inflation",
            "central bank", "emergency", "pipeline", "outage", "production cut",
            "أوبك", "الفيدرالي", "الفائدة", "عقوبات", "حظر", "هرمز", "حرب", "هجوم",
            "هدنة", "إيران", "إسرائيل", "روسيا", "أوكرانيا", "تضخم", "بنك مركزي",
            "خط أنابيب", "تعطل", "خفض الإنتاج"
        ]
        medium = [
            "inventory", "stockpile", "production", "exports", "imports", "demand",
            "supply", "employment", "gdp", "cpi", "pmi", "refinery", "shipping",
            "مخزونات", "إنتاج", "صادرات", "واردات", "طلب", "عرض", "وظائف", "ناتج",
            "تضخم", "مصافي", "شحن"
        ]
        market_words = [
            "surprise", "unexpected", "record", "largest", "cut", "increase", "decrease",
            "قفزة", "مفاجئ", "غير متوقع", "قياسي", "أكبر", "خفض", "زيادة", "انخفاض"
        ]
        h = sum(1 for k in high if k in text)
        m = sum(1 for k in medium if k in text)
        mw = sum(1 for k in market_words if k in text)
        score = min(100, 25 + h * 10 + m * 5 + mw * 4)
        level = "مرتفع جداً" if score >= 80 else "مرتفع" if score >= 65 else "متوسط" if score >= 45 else "منخفض"
        return {"score": score, "level": level, "high_terms": h, "medium_terms": m, "market_terms": mw}


    def _event_window_status(self, age_min: float, has_15: bool, has_60: bool) -> str:
        if age_min < 15:
            return "مبكر - لم تكتمل نافذة 15 دقيقة"
        if age_min < 60:
            return "جزئي - نافذة 15 دقيقة مكتملة و60 دقيقة غير مكتملة" if has_15 else "غير مكتمل"
        if has_60:
            return "مكتمل 15/60 دقيقة"
        return "غير مكتمل - لا توجد بيانات كافية لـ60 دقيقة"


    def _expected_news_direction(self, news_item: Dict, asset: str) -> Dict:
        """تقدير الاتجاه الأساسي المتوقع للخبر قبل النظر إلى السعر؛ ليست إشارة تداول."""
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        bull_oil = ["opec cut", "production cut", "supply disruption", "outage", "sanctions", "embargo", "hormuz", "attack", "war", "خفض الإنتاج", "تعطل الإمدادات", "عقوبات", "حظر", "هرمز", "هجوم", "حرب"]
        bear_oil = ["production increase", "output increase", "supply increase", "ceasefire", "demand slowdown", "inventory build", "زيادة الإنتاج", "زيادة المعروض", "هدنة", "تباطؤ الطلب", "ارتفاع المخزونات"]
        bull_silver = ["rate cut", "dovish", "weak dollar", "inflation rise", "safe haven", "خفض الفائدة", "دولار ضعيف", "ملاذ آمن", "ارتفاع التضخم"]
        bear_silver = ["rate hike", "hawkish", "strong dollar", "yield increase", "رفع الفائدة", "دولار قوي", "تشدد نقدي", "ارتفاع العوائد"]
        bull = sum(1 for x in (bull_oil if asset == "oil" else bull_silver) if x in text)
        bear = sum(1 for x in (bear_oil if asset == "oil" else bear_silver) if x in text)
        if bull > bear:
            return {"direction": "صعود", "strength": min(100, 50 + (bull-bear)*15), "bull_terms": bull, "bear_terms": bear}
        if bear > bull:
            return {"direction": "هبوط", "strength": min(100, 50 + (bear-bull)*15), "bull_terms": bull, "bear_terms": bear}
        return {"direction": "محايد", "strength": 40, "bull_terms": bull, "bear_terms": bear}


    def _news_relevance(self, news_item: Dict, asset: str) -> int:
        """درجة ارتباط الخبر بالأصل حتى لا يحصل الخبر العام على وزن خبر مباشر."""
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        direct = {"oil": ["oil", "crude", "wti", "brent", "opec", "petroleum", "نفط", "خام", "أوبك", "برنت", "إنتاج النفط", "مخزونات النفط"], "silver": ["silver", "xag", "precious metal", "industrial metals", "فضة", "المعادن الثمينة"]}[asset]
        geo = ["iran", "hormuz", "red sea", "middle east", "israel", "gaza", "yemen", "russia", "ukraine", "sanctions", "إيران", "هرمز", "البحر الأحمر", "الشرق الأوسط", "إسرائيل", "غزة", "اليمن", "روسيا", "أوكرانيا", "عقوبات"]
        d, g = sum(1 for x in direct if x in text), sum(1 for x in geo if x in text)
        return min(100, 35 + d*18 + g*8) if (d or g) else 20


    def _compare_news_hypothesis(self, expected: Dict, actual_change: float) -> Dict:
        """مقارنة فرضية الاتجاه الأساسية بالاستجابة السعرية المقاسة."""
        if not actual_change:
            return {"match": "غير قابل للحكم", "score": 0}
        actual = "صعود" if actual_change > 0 else "هبوط"
        if expected.get("direction") == "محايد":
            return {"match": "محايد/غير حاسم", "score": 40}
        if actual == expected.get("direction"):
            return {"match": "متوافق", "score": min(100, 60 + int(expected.get("strength", 0)*0.4))}
        return {"match": "متعارض", "score": max(0, 40 - int(expected.get("strength", 0)*0.3))}


    def _complete_report_text(self, content, finish_reason=None):
        """يتحقق من أن التقرير صالح للإرسال وغير فارغ أو مبتور."""
        content = self._safe_str(content).strip()
        if not content:
            return ""
        if finish_reason in {"length", "max_tokens"}:
            return ""
        # منع إرسال عنوان فقط أو نص قصير غير مفيد.
        normalized = re.sub(r"[\s\n]+", " ", content).strip()
        if len(normalized) < 80:
            return ""
        return content


    def _current_market_state(self, candles_data: Dict, asset: str) -> Dict:
        """تحديد الاتجاه الحالي للأصل من حركة السعر الفعلية، مستقل عن الأخبار."""
        data = (candles_data or {}).get(asset) or {}
        closes = data.get("closes") or []
        try:
            vals=[float(x) for x in closes if x is not None and float(x)>0]
            if len(vals)<15:
                return {"direction":"غير معروف","strength":"غير كافٍ","change_15m":0.0,"change_60m":0.0}
            cur=vals[-1]; p15=vals[-16]; p60=vals[-61] if len(vals)>=61 else vals[0]
            c15=(cur-p15)/p15*100 if p15 else 0.0; c60=(cur-p60)/p60*100 if p60 else 0.0
            score=c15*0.4+c60*0.6
            direction="صعود" if score>0.03 else "هبوط" if score<-0.03 else "محايد"
            mag=abs(score); strength="قوي" if mag>=0.30 else "متوسط" if mag>=0.12 else "ضعيف" if mag>=0.03 else "محايد"
            return {"direction":direction,"strength":strength,"change_15m":round(c15,3),"change_60m":round(c60,3),"score":round(score,3)}
        except Exception:
            return {"direction":"غير معروف","strength":"غير كافٍ","change_15m":0.0,"change_60m":0.0}

    def analyze_news_impact(self, news_item: Dict, candles_data: Dict = None) -> Dict:
        """قياس نافذة الخبر من لحظة النشر، مع تمييز القابلية الأساسية عن الأثر الفعلي."""
        asset_hint = self._news_asset(news_item)
        potential = self._news_potential(news_item)
        result = {
            "title": self._safe_str(news_item.get("title")),
            "description": self._safe_str(news_item.get("description")),
            "source": self._safe_str(news_item.get("source")),
            "published_at": self._safe_str(news_item.get("published_at")),
            "oil_change_15m": 0.0, "oil_change_60m": 0.0,
            "silver_change_15m": 0.0, "silver_change_60m": 0.0,
            "oil_price_before": 0.0, "oil_price_at_news": 0.0, "oil_price_15min": 0.0, "oil_price_60min": 0.0,
            "silver_price_before": 0.0, "silver_price_at_news": 0.0, "silver_price_15min": 0.0, "silver_price_60min": 0.0,
            "is_significant": False, "direction": "محايد", "classification": "غير مؤثر",
            "change_pct": 0.0, "asset": asset_hint,
            "news_potential_score": potential["score"], "news_potential": potential["level"],
            "measurement_status": "غير مقاس", "causality": "غير مثبت",
        }
        try:
            pub_time = self._parse_published_time(news_item.get("published_at"))
            if pub_time is None:
                result["measurement_status"] = "وقت الخبر غير صالح"
                return result
            pub_utc = pub_time.replace(tzinfo=timezone.utc) if pub_time.tzinfo is None else pub_time.astimezone(timezone.utc)
            now_utc = datetime.now(timezone.utc)
            age_min = (now_utc - pub_utc).total_seconds() / 60.0
            if age_min < -10:
                result["measurement_status"] = "الخبر مستقبلي/وقت غير متزامن"
                return result
            age_min = max(0.0, age_min)
            result["news_age_minutes"] = round(age_min, 1)

            completed_15 = False
            completed_60 = False
            measured_assets = []
            for asset in ("eurusd", "usdjpy"):
                data = (candles_data or {}).get(asset) or {}
                closes = data.get("closes") or []
                # يتطلب القياس أن تكون السلسلة دقيقة واحدة. إذا كان هناك timestamp نستخدمه بدلاً من افتراض الفهرس.
                if len(closes) < 20:
                    continue
                n = len(closes)
                event_idx = n - 1 - int(round(age_min))
                if event_idx < 0 or event_idx >= n:
                    continue
                p_event = float(closes[event_idx]) if closes[event_idx] is not None else 0.0
                if p_event <= 0:
                    continue
                before_idx = max(0, event_idx - 30)
                p_before = float(closes[before_idx]) if closes[before_idx] is not None else p_event
                result[f"{asset}_price_before"] = round(p_before, 4)
                result[f"{asset}_price_at_news"] = round(p_event, 4)

                idx15 = event_idx + 15
                idx60 = event_idx + 60
                if idx15 < n and closes[idx15] is not None:
                    p15 = float(closes[idx15])
                    if p15 > 0:
                        result[f"{asset}_price_15min"] = round(p15, 4)
                        result[f"{asset}_change_15m"] = round((p15 - p_event) / p_event * 100, 4)
                        completed_15 = True
                        measured_assets.append(asset)
                if idx60 < n and closes[idx60] is not None:
                    p60 = float(closes[idx60])
                    if p60 > 0:
                        result[f"{asset}_price_60min"] = round(p60, 4)
                        result[f"{asset}_change_60m"] = round((p60 - p_event) / p_event * 100, 4)
                        completed_60 = True
                        measured_assets.append(asset)

            result["measurement_status"] = self._event_window_status(age_min, completed_15, completed_60)
            if not measured_assets:
                return result

            # نستخدم أكبر حركة مكتملة، لكن لا نسميها "سببية"؛ هي ارتباط زمني مقاس فقط.
            changes = []
            for asset in ("eurusd", "usdjpy"):
                for window in ("15m", "60m"):
                    v = float(result.get(f"{asset}_change_{window}", 0) or 0)
                    if v != 0:
                        changes.append((abs(v), asset, v, window))
            if not changes:
                return result
            _, best_asset, best_change, best_window = max(changes, key=lambda x: x[0])
            result["asset"] = best_asset
            result["change_pct"] = best_change
            result["direction"] = "صعود" if best_change > 0 else "هبوط" if best_change < 0 else "محايد"
            result["max_measured_change"] = round(abs(best_change), 4)
            result["measurement_window"] = best_window

            max_change = abs(best_change)
            relevance = self._news_relevance(news_item, best_asset)
            expected = self._expected_news_direction(news_item, best_asset)
            hypothesis = self._compare_news_hypothesis(expected, best_change)
            result["asset_relevance_score"] = relevance
            result["expected_direction"] = expected["direction"]
            result["expected_direction_strength"] = expected["strength"]
            result["direction_hypothesis_match"] = hypothesis["match"]
            result["direction_hypothesis_score"] = hypothesis["score"]
            result["bullish_event_terms"] = expected["bull_terms"]
            result["bearish_event_terms"] = expected["bear_terms"]
            measured_score = min(100, int(max_change / max(IMPACT_THRESHOLDS["high"], 0.0001) * 70))
            result["intelligence_confidence"] = max(0, min(100, round(
                0.35*potential["score"] + 0.25*relevance + 0.20*hypothesis["score"] + 0.20*measured_score)))
            if max_change >= IMPACT_THRESHOLDS["very_high"]:
                result["classification"] = "قوي جداً"; result["is_significant"] = True
            elif max_change >= IMPACT_THRESHOLDS["high"]:
                result["classification"] = "مرتفع"; result["is_significant"] = True
            elif max_change >= IMPACT_THRESHOLDS["medium"]:
                result["classification"] = "متوسط"; result["is_significant"] = True
            elif max_change >= IMPACT_THRESHOLDS["low"]:
                result["classification"] = "ضعيف"
            else:
                result["classification"] = "غير مؤثر"

            # القابلية العالية + حركة صغيرة = خبر محتمل الأهمية لكن بلا تأكيد سعري.
            if potential["score"] >= 65 and relevance >= 45 and max_change < IMPACT_THRESHOLDS["medium"]:
                result["classification"] = "مهم أساسياً - تأثير سعري غير مؤكد"
            elif potential["score"] >= 65 and relevance < 45:
                result["classification"] = "مهم إعلامياً - ارتباط الأصل ضعيف"
            elif expected["direction"] != "محايد" and hypothesis["match"] == "متعارض" and max_change >= IMPACT_THRESHOLDS["low"]:
                result["classification"] = "خبر مهم - استجابة السوق معاكسة"
            if result["is_significant"]:
                result["causality"] = "ارتباط زمني قوي، السببية غير مثبتة"
            elif completed_15 or completed_60:
                result["causality"] = "لم يثبت تأثير سعري ملموس"
            return result
        except Exception as e:
            result["measurement_status"] = f"خطأ: {type(e).__name__}"
            logging.error(f"❌ خطأ في تحليل الخبر: {e}")
            logging.debug(traceback.format_exc())
            return result


    def _safe_str(self, value):
        """تحويل أي قيمة إلى سلسلة نصية آمنة"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, list) or isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    # =====================================================================
    # 🗂️ إدارة الأخبار المؤثرة النشطة (بذاكرة مشتركة)
    # =====================================================================

    def store_active_news(self, impact: Dict):
        """تخزين خبر مؤثر في الذاكرة النشطة مع وقت انتهاء صلاحية (ساعتين)"""
        if not impact or not impact.get("is_significant", False):
            return

        expiry = datetime.now() + timedelta(hours=2)
        news_entry = {
            "title": impact.get("title", "خبر غير معروف"),
            "direction": impact.get("direction", "محايد"),
            "change_pct": impact.get("change_pct", 0.0),
            "asset": impact.get("asset", "oil"),
            "classification": impact.get("classification", "غير مؤثر"),
            "expiry": expiry,
            "timestamp": datetime.now().isoformat(),
            "source": impact.get("source", "غير معروف")
        }

        # إزالة أي تكرار (نفس العنوان)
        self._active_news = [n for n in self._active_news if n.get("title") != news_entry["title"]]
        self._active_news.append(news_entry)

        # تنظيف المنتهية صلاحيتها
        self.clear_expired_news()

        logging.info(f"📰 تم تخزين خبر مؤثر: {news_entry['title'][:50]}... (تأثير: {news_entry['change_pct']:.2f}%)")

    def get_active_news(self, asset_type: str = None) -> List[Dict]:
        """استرجاع الأخبار المؤثرة النشطة (غير منتهية الصلاحية)"""
        self.clear_expired_news()
        if asset_type:
            return [n for n in self._active_news if n.get("asset") == asset_type]
        return self._active_news.copy()

    def clear_expired_news(self):
        """حذف الأخبار المنتهية صلاحيتها"""
        now = datetime.now()
        self._active_news = [n for n in self._active_news if n.get("expiry", now) > now]
        if len(self._active_news) > 50:
            self._active_news = self._active_news[-50:]

    def get_strongest_news(self, asset_type: str = None) -> Optional[Dict]:
        """الحصول على أقوى خبر مؤثر حالياً (أكبر تغير مئوي)"""
        active = self.get_active_news(asset_type)
        if not active:
            return None
        return max(active, key=lambda x: abs(x.get("change_pct", 0)))

    # =====================================================================
    # 🧠 صياغة التقرير (معتمد على الأرقام فقط، بدون جداول أو رموز غريبة)
    # =====================================================================

    def _groq_report(self, analyzed_news: List[Dict], oil_price: float, silver_price: float, fetch_stats: Optional[Dict] = None) -> str:
        """صياغة التقرير عبر Groq مع فصل واضح بين غياب الأخبار وفشل النموذج.
        لا نسمح بقطع التقرير عند نهاية نافذة التوليد؛ وإذا أعاد المزود
        استجابة ناقصة نعيد الطلب بصيغة أقصر ومكتملة.
        """
        fetch_stats = fetch_stats or self._last_fetch_stats or {}
        try:
            # الحالة الحالية للسوق مستقلة عن أثر الأخبار، وتظهر صراحة في الحكم النهائي.
            candles_for_state = getattr(self, "_last_candles_data", {}) or {}
            oil_state = self._current_market_state(candles_for_state, "oil")
            silver_state = self._current_market_state(candles_for_state, "silver")
            significant_news = [n for n in analyzed_news if n and n.get("is_significant", False)]
            candidate_news = [n for n in analyzed_news if n]

            # لا نمنع النموذج من العمل عند عدم وجود خبر مؤثر؛ بل نعطيه حالة البيانات كاملة.
            news_lines = []
            for news in candidate_news[:8]:
                title = self._safe_str(news.get("title"))[:140]
                asset = "النفط" if news.get("asset") == "oil" else "الفضة" if news.get("asset") == "silver" else "النفط/الفضة"
                c15 = float(news.get("oil_change_15m", 0) or news.get("silver_change_15m", 0) or 0)
                c60 = float(news.get("oil_change_60m", 0) or news.get("silver_change_60m", 0) or 0)
                news_lines.append(f"- {title} | المصدر: {self._safe_str(news.get('source'))} | الأصل: {asset} | 15د={c15:+.3f}% | 60د={c60:+.3f}% | التصنيف={self._safe_str(news.get('classification'))} | أهمية={news.get('news_potential_score',0)} | ارتباط الأصل={news.get('asset_relevance_score',0)} | الاتجاه المتوقع={self._safe_str(news.get('expected_direction'))} | توافق الاتجاه={self._safe_str(news.get('direction_hypothesis_match'))} | الثقة الاستخباراتية={news.get('intelligence_confidence',0)} | القياس={self._safe_str(news.get('measurement_status'))}")
            news_text = "\n".join(news_lines) if news_lines else "لا توجد أخبار اجتازت مرحلة التحليل السعري."

            prompt = f"""أنت محرك صياغة استخباراتي يعمل داخل Tona Intelligence. لا تخترع أخباراً أو أسباباً أو أرقاماً.

حالة جمع البيانات:
- المصادر الكلية: {fetch_stats.get('sources_total', 0)}
- المصادر الناجحة: {fetch_stats.get('sources_ok', 0)}
- المصادر الفاشلة: {fetch_stats.get('sources_failed', 0)}
- الأخبار الفريدة: {fetch_stats.get('unique_items', 0)}
- الأخبار التي دخلت التحليل: {len(candidate_news)}
- الأخبار ذات التأثير المقاس الذي تجاوز العتبة: {len(significant_news)}
- الأخبار ذات القابلية الأساسية المرتفعة: {sum(1 for n in candidate_news if n.get("news_potential_score", 0) >= 65)}
- متوسط الثقة الاستخباراتية: {round(sum(float(n.get("intelligence_confidence", 0) or 0) for n in candidate_news) / len(candidate_news), 1) if candidate_news else 0}
- الأخبار ذات الفرضية الاتجاهية المتوافقة مع حركة السعر: {sum(1 for n in candidate_news if n.get("direction_hypothesis_match") == "متوافق")}
- الأخبار ذات الفرضية الاتجاهية المتعارضة مع حركة السعر: {sum(1 for n in candidate_news if n.get("direction_hypothesis_match") == "متعارض")}

الأسعار الحالية: النفط={float(oil_price or 0):.3f}، الفضة={float(silver_price or 0):.3f}
الاتجاه الحالي الفعلي للنفط: {oil_state["direction"]} {oil_state["strength"]} | 15د={oil_state["change_15m"]:+.3f}% | 60د={oil_state["change_60m"]:+.3f}%
الاتجاه الحالي الفعلي للفضة: {silver_state["direction"]} {silver_state["strength"]} | 15د={silver_state["change_15m"]:+.3f}% | 60د={silver_state["change_60m"]:+.3f}%

الأخبار والقياسات:
{news_text}

اكتب تقريراً عربياً مهنياً كاملاً، واضحاً ومترابطاً، من 10-16 سطراً تقريباً.
ابدأ بملخص حالة المصادر والتغطية، ثم حلل أهم الأخبار، ثم قدم حكماً استخباراتياً نهائياً. يجب أن يتضمن الحكم النهائي صراحةً الاتجاه الحالي الفعلي للنفط والفضة (صعود/هبوط/محايد مع قوي/متوسط/ضعيف)، ثم اتجاه الأخبار، ثم مستوى الثقة، ولا تستبدل الاتجاه الحالي بعبارة عامة مثل "السوق ينتظر".
لكل خبر مهم، عند توفر البيانات، اذكر باختصار: أهمية الخبر، ارتباطه بالأصل، الاتجاه المتوقع، حركة 15 دقيقة، حركة 60 دقيقة، وتوافق الفرضية مع السوق.
- افصل دائماً بين أهمية الخبر المحتملة وبين التأثير السعري المقاس.
- إذا كان الخبر عالي الأهمية أساسياً لكن الحركة السعرية صغيرة أو النافذة غير مكتملة، قل "مهم أساسياً لكن التأثير السعري غير مؤكد" ولا تقل "غير مؤثر" بشكل مطلق.
- إذا فشلت مصادر كثيرة: اذكر أن تغطية المصادر جزئية، ولا تجعل ذلك دليلاً على غياب الأخبار.
- إذا كانت نافذة القياس غير مكتملة، اذكر ذلك صراحة ولا تعاملها كصفر.
- ميّز بين الخبر المنشور وبين التأثير الذي تم قياسه فعلياً.
- لا تحوّل الارتباط الزمني إلى سببية مؤكدة.
- لا تقدم أرقاماً غير موجودة في البيانات، ولا تعتبر تغير السعر الحالي دليلاً على تأثير خبر قديم.
- لا تختم التقرير قبل اكتمال الخلاصة العملية.
- لا تخلط بين الاتجاه الحالي للسعر وبين اتجاه الخبر؛ اذكرهما منفصلين.
- لا تستخدم عبارات حشو أو تكرر نفس الخبر.
- مهم جداً: لا تتوقف في منتصف جملة أو فقرة. يجب أن تكون الاستجابة مكتملة لغوياً وتنتهي بخلاصة واضحة.
"""

            if not self.groq_api_key:
                self._last_report_status = {"provider": "fallback", "reason": "missing_groq_api_key"}
                logging.error("❌ Groq غير متاح: GROQ_API_KEY مفقود")
                return self._fallback_report(analyzed_news, oil_price, silver_price, reason="missing_groq_api_key", fetch_stats=fetch_stats)

            headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": "أنت طبقة صياغة فقط. التزم بالأرقام والأخبار المقدمة ولا تخترع معلومات."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.12, "max_tokens": 1800
            }
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                choice = (data.get("choices") or [{}])[0]
                first_content = self._safe_str(((choice.get("message") or {}).get("content"))).strip()
                first_finish = self._safe_str(choice.get("finish_reason"))

                # المسار الأول: الاستجابة مكتملة.
                complete = self._complete_report_text(first_content, first_finish)
                if complete:
                    self._last_report_status = {"provider": "groq", "reason": "success"}
                    logging.info("✅ Tona: تم توليد تقرير مكتمل بواسطة Groq")
                    return complete

                # المسار الثاني: إعادة توليد قصيرة ومضمونة البنية.
                retry_payload = {
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "أنت طبقة صياغة فقط. اكتب تقريراً استخباراتياً عربياً "
                                "مكتمل الجمل، موجزاً، ولا تخترع أي رقم أو خبر. "
                                "يجب أن ينتهي التقرير بخلاصة عملية كاملة."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt + """
تعليمات طارئة للطول:
اكتب نسخة مختصرة من 7 إلى 10 فقرات قصيرة.
لا تتجاوز 900 كلمة.
احتفظ فقط بأهم الأخبار والأرقام والاستنتاج النهائي.
يجب أن تنتهي بجملة كاملة، ولا تستخدم علامة الحذف (...).
"""
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1600
                }

                retry_ok = False
                retry_content = ""
                retry_finish = ""
                try:
                    retry = requests.post(self.api_url, headers=headers, json=retry_payload, timeout=25)
                    if retry.status_code == 200:
                        rd = retry.json()
                        rchoice = (rd.get("choices") or [{}])[0]
                        retry_content = self._safe_str(
                            ((rchoice.get("message") or {}).get("content"))
                        ).strip()
                        retry_finish = self._safe_str(rchoice.get("finish_reason"))
                        retry_ok = bool(self._complete_report_text(retry_content, retry_finish))
                        if retry_ok:
                            self._last_report_status = {
                                "provider": "groq",
                                "reason": "success_after_retry"
                            }
                            logging.warning(
                                "⚠️ Tona: تمت إعادة صياغة التقرير بنجاح بعد عدم اكتمال الاستجابة الأولى"
                            )
                            return retry_content
                        logging.warning(
                            "⚠️ Tona: إعادة الصياغة الثانية لم تنتج تقريراً مكتملًا "
                            f"(finish_reason={retry_finish or 'unknown'})"
                        )
                    else:
                        logging.warning(
                            f"⚠️ Tona: فشلت إعادة الصياغة HTTP {retry.status_code}"
                        )
                except Exception as retry_error:
                    logging.warning(f"⚠️ Tona: فشلت إعادة محاولة التقرير: {retry_error}")

                # المسار الثالث: لا نرسل أبداً عنواناً فارغاً أو نصاً مبتوراً.
                reason = "incomplete_model_response"
                logging.warning(
                    "⚠️ Tona: تم تفعيل التقرير الاحتياطي لأن جميع محاولات النموذج "
                    "لم تنتج استجابة مكتملة"
                )
            else:
                reason = f"http_{response.status_code}"
                logging.error(
                    f"❌ Groq HTTP {response.status_code}: "
                    f"{self._safe_str(response.text)[:500]}"
                )

        except Exception as e:
            reason = f"{type(e).__name__}: {e}"
            logging.error(f"❌ Groq فشل: {reason}")
            logging.debug(traceback.format_exc())

        self._last_report_status = {"provider": "fallback", "reason": reason}
        return self._fallback_report(analyzed_news, oil_price, silver_price, reason=reason, fetch_stats=fetch_stats)


    def _fallback_report(self, analyzed_news, oil_price, silver_price, reason="no_significant_news", fetch_stats=None) -> str:
        """تقرير احتياطي في حال فشل Groq أو عدم وجود أخبار مؤثرة"""
        try:
            lines = []
            lines.append("🧠 تقرير تولين الاستخباراتي")
            lines.append("")
            lines.append(f"الساعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            lines.append("━" * 40)
            lines.append("")

            if oil_price:
                lines.append(f"سعر النفط: {float(oil_price):.2f} دولار")
            if silver_price:
                lines.append(f"سعر الفضة: {float(silver_price):.3f} دولار")

            oil_state = self._current_market_state(getattr(self, "_last_candles_data", {}) or {}, "oil")
            silver_state = self._current_market_state(getattr(self, "_last_candles_data", {}) or {}, "silver")
            lines.append(f"الاتجاه الحالي للنفط: {oil_state['direction']} {oil_state['strength']} | 15د {oil_state['change_15m']:+.3f}% | 60د {oil_state['change_60m']:+.3f}%")
            lines.append(f"الاتجاه الحالي للفضة: {silver_state['direction']} {silver_state['strength']} | 15د {silver_state['change_15m']:+.3f}% | 60د {silver_state['change_60m']:+.3f}%")

            fetch_stats = fetch_stats or self._last_fetch_stats or {}
            significant = [n for n in analyzed_news if n and n.get("is_significant", False)] if analyzed_news else []

            if significant:
                lines.append("")
                lines.append("أخبار مؤثرة (تأثير فعلي مقاس):")
                for news in significant[:3]:
                    if not news:
                        continue
                    title = self._safe_str(news.get("title"))
                    change_60m = news.get("oil_change_60m", 0) or news.get("silver_change_60m", 0) or 0
                    change_15m = news.get("oil_change_15m", 0) or news.get("silver_change_15m", 0) or 0
                    direction = "ارتفاع" if change_60m > 0 else "هبوط" if change_60m < 0 else "استقرار"
                    classification = news.get("classification", "غير مؤثر")
                    lines.append(f"• {title[:60]}...")
                    lines.append(f"  → {direction} بنسبة {abs(change_60m):.2f}% خلال 60 دقيقة (فوري: {change_15m:+.2f}%) - {classification}")
            else:
                lines.append("")
                if reason == "no_significant_news":
                    if fetch_stats.get("sources_ok", 0) > 0:
                        lines.append("تم فحص مصادر الأخبار المتاحة، ولم يظهر تأثير سعري مقاس يتجاوز عتبة التأثير حالياً.")
                    else:
                        lines.append("تعذر التحقق من الأخبار بشكل كافٍ بسبب فشل مصادر الجمع.")
                else:
                    lines.append(f"⚠️ تعذر توليد التقرير الذكي ({reason}). تم استخدام التقرير الاحتياطي دون اختلاق أخبار.")

            lines.append("")
            lines.append("التوصيات:")
            if significant:
                avg_change = sum(n.get("oil_change_60m", 0) or n.get("silver_change_60m", 0) for n in significant[:3]) / len(significant[:3]) if significant else 0
                if avg_change > 0.5:
                    lines.append("• الاتجاه العام صاعد مدعوم بالأخبار.")
                elif avg_change < -0.5:
                    lines.append("• الاتجاه العام هابط تحت ضغط الأخبار.")
                else:
                    lines.append("• السوق متقلب، انتظر تأكيداً إضافياً.")
                lines.append("• راقب الصفقات المفتوحة بحذر.")
            else:
                lines.append("• استمر في متابعة المؤشرات الفنية.")
                lines.append("• ابحث عن فرص الدخول بناءً على التحليل الفني.")

            lines.append("")
            lines.append("━" * 40)
            lines.append("💙 تولين: أنا هنا لمساعدتك!")

            report = "\n".join(lines).strip()
            # ضمان عدم رجوع نص فارغ مهما كان سبب الفشل.
            if len(report) < 80:
                report = (
                    "🧠 تقرير تولين الاستخباراتي\n\n"
                    "تعذر توليد التقرير الذكي حالياً، لذلك تم استخدام ملخص احتياطي.\n"
                    "التوصية: لا تعتمد على الأخبار وحدها، وانتظر تأكيد التحليل الفني.\n\n"
                    "💙 تولين: أنا هنا لمساعدتك!"
                ).strip()
            return report

        except Exception as e:
            logging.error(f"❌ فشل التقرير الاحتياطي: {e}")
            logging.debug(traceback.format_exc())
            return (
                "🧠 تقرير تولين الاستخباراتي\n\n"
                "تعذر توليد التقرير حالياً. يرجى الاعتماد مؤقتاً على التحليل الفني "
                "وانتظار المحاولة التالية.\n\n"
                "💙 تولين: أنا هنا لمساعدتك!"
            )



    # =====================================================================
    # 🚨 Breaking News Radar V1.0 - التحذير العاجل القائم على الخبر + السعر
    # =====================================================================
    # الفكرة: لا يصدر تحذير عاجل لمجرد وجود خبر مهم. يجب أن يترافق الخبر
    # مع حركة سعرية مفاجئة ومتزامنة معه ومتوافقة مع اتجاه الخبر.
    # الرادار خفيف: لا يستخدم Groq في الفحص الأولي ولا يعيد تحليل الأخبار
    # القديمة، ويمكن تشغيله كل 15 دقيقة مع إعادة تحقق سريعة فقط للمرشحين.

    RADAR_INTERVAL_SECONDS = 15 * 60
    RADAR_CONFIRMATION_SECONDS = 60
    RADAR_MAX_ALERTS_PER_HOUR = 3
    RADAR_DUPLICATE_COOLDOWN_SECONDS = 6 * 3600
    RADAR_MIN_ABSOLUTE_MOVE_PCT = {"oil": 0.45, "silver": 0.60}
    RADAR_MIN_RELATIVE_MOVE = 1.8
    RADAR_MIN_NEWS_SCORE = 55
    RADAR_STRONG_SCORE = 82

    def _radar_news_score(self, news: Dict, asset: str, change_pct: float, timing_score: float) -> Tuple[int, Dict]:
        """تقييم حتمي خفيف قبل أي نموذج لغوي."""
        text = (self._safe_str(news.get("title")) + " " + self._safe_str(news.get("description"))).lower()
        source = self._safe_str(news.get("source", ""))
        score = 0
        reasons = []

        direct_terms = {
            "oil": ["oil", "crude", "brent", "wti", "opec", "production", "supply", "export", "pipeline", "refinery", "hormuz", "strait", "نفط", "خام", "أوبك", "إمدادات", "هرمز"],
            "silver": ["silver", "xag", "precious metal", "metals", "gold", "fed", "interest rate", "inflation", "فضة", "ذهب", "الفيدرالي", "الفائدة", "التضخم"]
        }
        crisis_terms = ["shutdown", "closed", "closure", "attack", "strike", "blocked", "blockade", "sanction", "embargo", "disruption", "halt", "cut", "emergency", "war", "invasion", "explosion", "إغلاق", "هجوم", "ضربة", "حصار", "عقوبات", "حظر", "تعطل", "توقف", "خفض", "حرب"]
        terms = direct_terms.get(asset, [])
        direct_hits = sum(1 for t in terms if t in text)
        crisis_hits = sum(1 for t in crisis_terms if t in text)

        if direct_hits >= 2:
            score += 25
            reasons.append("ارتباط مباشر بالأصل")
        elif direct_hits == 1:
            score += 15
            reasons.append("ارتباط محتمل بالأصل")
        if crisis_hits:
            score += min(25, 10 + crisis_hits * 5)
            reasons.append("حدث جوهري/طارئ")
        if source in self.trusted_sources or any(x.lower() in source.lower() for x in self.trusted_sources if x):
            score += 10
            reasons.append("مصدر موثوق")

        abs_move = abs(change_pct)
        base = self.RADAR_MIN_ABSOLUTE_MOVE_PCT[asset]
        if abs_move >= base:
            score += 20
            reasons.append(f"حركة سعرية مفاجئة {change_pct:+.2f}%")
        if timing_score >= 0.8:
            score += 15
            reasons.append("تزامن زمني قوي")
        elif timing_score >= 0.55:
            score += 8
            reasons.append("تزامن زمني متوسط")

        return min(100, score), {"direct_hits": direct_hits, "crisis_hits": crisis_hits, "reasons": reasons}

    def _radar_extract_price_window(self, asset: str, candles: Dict) -> Optional[Dict]:
        """استخراج حركة قصيرة المدى من شموع Min1 دون طلب شبكة إضافي."""
        data = candles.get(asset) if isinstance(candles, dict) else None
        if not isinstance(data, dict):
            return None
        closes = data.get("closes") or []
        if len(closes) < 6:
            return None
        try:
            current = float(closes[-1])
            # مقارنة 5 دقائق، وهي مناسبة للرادار الخفيف وليست إشارة تداول.
            before = float(closes[-6])
            if before <= 0 or current <= 0:
                return None
            change = (current - before) / before * 100.0
            return {"current": current, "before": before, "change_pct": change}
        except (TypeError, ValueError, IndexError):
            return None

    def _radar_alert_fingerprint(self, news: Dict, asset: str) -> str:
        raw = f"{asset}|{news.get('url','')}|{news.get('title','')}|{news.get('published_at','')}"
        return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()

    def _fetch_radar_news(self, hours=1):
        """فحص خفيف: مصادر أولوية فقط، بدل إعادة طلب جميع المصادر الـ17."""
        feeds = [
            "https://feeds.reuters.com/reuters/commoditiesNews",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://oilprice.com/rss/energy-news",
            "https://oilprice.com/rss/geopolitics",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.skynews.com/feeds/rss/world.xml",
            "https://www.aljazeera.net/feeds/rss",
            "https://www.alarabiya.net/feed/rss",
        ]
        all_news = []
        for feed in feeds:
            for item in self._fetch_rss_feed(feed, max_items=5):
                text = (self._safe_str(item.get("title")) + " " + self._safe_str(item.get("description"))).lower()
                if any(k in text for k in self.exclude_keywords):
                    continue
                if any(k in text for k in self.required_keywords):
                    pub = self._parse_published_time(item.get("published_at"))
                    if pub:
                        age = (datetime.now(timezone.utc) - pub.astimezone(timezone.utc)).total_seconds()
                        if 0 <= age <= hours * 3600:
                            all_news.append(item)
        seen, unique = set(), []
        for item in all_news:
            key = self._radar_alert_fingerprint(item, "news")
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique

    def _radar_price_change_since_news(self, asset: str, candles: Dict, age_seconds: float) -> Optional[Dict]:
        """يقيس الحركة من قرب لحظة الخبر إلى الآن، لا حركة عشوائية قبل الخبر."""
        data = candles.get(asset) if isinstance(candles, dict) else None
        closes = data.get("closes", []) if isinstance(data, dict) else []
        if len(closes) < 8:
            return None
        try:
            age_min = max(1, int(round(age_seconds / 60.0)))
            # نحتاج شمعة قبل الخبر تقريباً + شمعة عند/بعد الخبر.
            idx = min(age_min, len(closes) - 2)
            before_news = float(closes[-idx - 1])
            current = float(closes[-1])
            if before_news <= 0 or current <= 0:
                return None
            change = (current - before_news) / before_news * 100.0
            return {"before": before_news, "current": current, "change_pct": change, "age_min": age_min}
        except (TypeError, ValueError, IndexError):
            return None

    def evaluate_breaking_news(self, news: Dict, candles_data: Dict = None) -> Optional[Dict]:
        """يفحص خبرًا واحدًا ويعيد التحذير فقط إذا اجتاز شروط الخبر والسعر والتزامن."""
        if not isinstance(news, dict):
            return None
        pub = self._parse_published_time(news.get("published_at"))
        if not pub:
            return None
        age = (datetime.now(timezone.utc) - pub.astimezone(timezone.utc)).total_seconds()
        if age < -120 or age > 15 * 60:
            return None

        candidates = []
        for asset in ("eurusd", "usdjpy"):
            window = self._radar_price_change_since_news(asset, candles_data or {}, max(age, 0.0))
            if not window:
                continue
            # التزامن هنا مرتبط مباشرة بعمر الخبر والحركة منذ قرب لحظة نشره.
            timing = max(0.0, 1.0 - max(age, 0.0) / 900.0)
            score, meta = self._radar_news_score(news, asset, window["change_pct"], timing)
            if abs(window["change_pct"]) < self.RADAR_MIN_ABSOLUTE_MOVE_PCT[asset]:
                continue
            # اتجاه الخبر: نبحث عن إشارات الاتجاه الواضحة فقط؛ الخبر المحايد لا يكفي.
            text = (self._safe_str(news.get("title")) + " " + self._safe_str(news.get("description"))).lower()
            bullish_terms = ["cut production", "supply disruption", "attack", "closure", "closed", "sanction", "embargo", "war", "إغلاق", "هجوم", "عقوبات", "حظر", "توقف", "تعطل", "خفض الإنتاج"]
            bearish_terms = ["increase production", "supply restored", "ceasefire", "production rises", "استئناف الإمدادات", "زيادة الإنتاج", "وقف إطلاق النار"]
            bull = sum(1 for x in bullish_terms if x in text)
            bear = sum(1 for x in bearish_terms if x in text)
            expected = "up" if bull > bear else "down" if bear > bull else None
            actual = "up" if window["change_pct"] > 0 else "down"
            direction_match = expected is not None and expected == actual
            if direction_match:
                score = min(100, score + 15)
                meta["reasons"].append("اتجاه الخبر متوافق مع حركة السعر")
            elif expected is not None:
                score = max(0, score - 15)
                meta["reasons"].append("اتجاه الخبر لا يتوافق مع حركة السعر")

            if score >= self.RADAR_STRONG_SCORE and direction_match:
                candidates.append({
                    "asset": asset,
                    "score": score,
                    "change_pct": window["change_pct"],
                    "price_before": window["before"],
                    "price_current": window["current"],
                    "expected_direction": expected,
                    "timing_score": timing,
                    "source": news.get("source", "غير معروف"),
                    "title": news.get("title", ""),
                    "title_ar": news.get("title_ar", ""),
                    "published_at": news.get("published_at", ""),
                    "url": news.get("url", ""),
                    "reasons": meta["reasons"],
                    "fingerprint": self._radar_alert_fingerprint(news, asset),
                    "requires_confirmation": True,
                })
        if not candidates:
            return None
        return max(candidates, key=lambda x: x["score"])

    def format_breaking_alert(self, alert: Dict, open_trades: Dict = None) -> str:
        """صياغة قصيرة ومختلفة جذريًا عن التقرير الاستخباراتي اليدوي."""
        asset_label = "النفط" if alert.get("asset") == "oil" else "الفضة"
        direction = "ارتفاع" if alert.get("change_pct", 0) > 0 else "هبوط"
        p0 = alert.get("price_before", 0)
        p1 = alert.get("price_current", 0)
        change = alert.get("change_pct", 0)
        risk_line = ""
        trades = open_trades or {}
        trade = trades.get(alert.get("asset")) if isinstance(trades, dict) else None
        if isinstance(trade, dict):
            side = str(trade.get("type", "")).upper()
            if (change > 0 and side == "SELL") or (change < 0 and side == "BUY"):
                risk_line = "\n⚠️ لديك صفقة مفتوحة في الاتجاه المعاكس للحركة الحالية؛ راجعها فورًا وفق إدارة المخاطر."

        persistence = "يرجّح استمرار الحركة مؤقتًا مع ضرورة مراقبة التثبيت" if alert.get("timing_score", 0) >= 0.75 else "استمرار الحركة غير مؤكد وتحتاج إلى متابعة التأكيد"
        reasons = "، ".join(alert.get("reasons", [])[:4])
        return (
            f"🚨 **تحذير عاجل — {asset_label}**\n\n"
            f"تحرك {asset_label} من {p0:.3f} إلى {p1:.3f}، أي {direction} بنسبة {abs(change):.2f}%، "
            f"بالتزامن مع خبر: **{self._safe_str(alert.get('title_ar') or alert.get('title'))[:180]}**.\n\n"
            f"🧠 تقييم Tona: {alert.get('score', 0)}/100\n"
            f"📰 المصدر: {self._safe_str(alert.get('source', 'غير معروف'))}\n"
            f"🔎 أسباب التأكيد: {reasons}\n\n"
            f"📈 التوقع القريب: {persistence}.\n"
            f"{risk_line}\n\n"
            f"💙 **Tona Intelligence**"
        )

    def run_breaking_news_radar(self, notify_callback=None, open_trades=None) -> Optional[Dict]:
        """دورة رادار خفيفة واحدة. يمكن استدعاؤها كل 15 دقيقة من المضيف."""
        try:
            candles = {}
            if self.candle_fetcher:
                for asset, symbol in (("oil", "USOIL_USDT"), ("silver", "SILVER_USDT")):
                    try:
                        data = self.candle_fetcher(symbol, "Min1", 8)
                        if data:
                            candles[asset] = data
                    except Exception as e:
                        logging.debug(f"Radar candle fetch {asset}: {e}")
            if not candles:
                return None

            news = self._fetch_radar_news(hours=1)
            if not news:
                return None

            # الأخبار الأحدث أولًا؛ لا نمرر كل الأخبار إلى النموذج.
            alerts = []
            for item in sorted(news, key=lambda x: str(x.get("published_at", "")), reverse=True)[:20]:
                alert = self.evaluate_breaking_news(item, candles)
                if alert:
                    alerts.append(alert)

            if not alerts:
                return None
            alert = max(alerts, key=lambda x: x.get("score", 0))
            now_ts = time.time()
            with self._radar_lock:
                self._radar_alert_times = [t for t in self._radar_alert_times if now_ts - t < 3600]
                fingerprint = alert.get("fingerprint")
                if fingerprint and now_ts - self._radar_alert_history.get(fingerprint, 0) < self.RADAR_DUPLICATE_COOLDOWN_SECONDS:
                    return None
                if len(self._radar_alert_times) >= self.RADAR_MAX_ALERTS_PER_HOUR:
                    logging.warning("⚠️ Radar alert rate limit reached; suppressing alert")
                    return None
                if fingerprint:
                    self._radar_alert_history[fingerprint] = now_ts
                self._radar_alert_times.append(now_ts)
            self.store_active_news({**alert, "is_significant": True, "direction": "صعود" if alert["change_pct"] > 0 else "هبوط", "classification": "تحذير عاجل", "change_pct": alert["change_pct"]})
            message = self.format_breaking_alert(alert, open_trades=open_trades)
            alert["message"] = message
            if callable(notify_callback):
                try:
                    notify_callback(message, alert)
                except TypeError:
                    notify_callback(message)
            return alert
        except Exception as e:
            logging.error(f"❌ Breaking News Radar failed: {e}")
            logging.debug(traceback.format_exc())
            return None

    def start_breaking_news_radar(self, notify_callback=None, open_trades_provider=None, interval_seconds=None):
        """تشغيل عامل واحد دائم؛ الافتراضي 15 دقيقة، بدون إنشاء عامل لكل دورة."""
        if getattr(self, "_radar_thread", None) and self._radar_thread.is_alive():
            return self._radar_thread
        interval = int(interval_seconds or self.RADAR_INTERVAL_SECONDS)
        self._radar_stop = threading.Event()

        def worker():
            logging.info(f"🚨 Tona Breaking News Radar started (interval={interval}s)")
            while not self._radar_stop.is_set():
                try:
                    trades = open_trades_provider() if callable(open_trades_provider) else None
                    self.run_breaking_news_radar(notify_callback=notify_callback, open_trades=trades)
                except Exception as e:
                    logging.error(f"❌ Radar worker error: {e}")
                self._radar_stop.wait(interval)

        self._radar_thread = threading.Thread(target=worker, name="TonaBreakingNewsRadar", daemon=True)
        self._radar_thread.start()
        return self._radar_thread

    def stop_breaking_news_radar(self):
        stop = getattr(self, "_radar_stop", None)
        if stop:
            stop.set()

    # =====================================================================
    # 🚀 الدالة الرئيسية (محسّنة مع كاش الشموع وفحص الحداثة)
    # =====================================================================

    def generate_elite_analysis(self, news_list=None):
        """الدورة الرئيسية: جمع -> تحقق زمني -> قياس تأثير -> صياغة، مع تشخيص كامل."""
        try:
            supplied = news_list is not None
            if news_list is None:
                news_list = self.fetch_targeted_intelligence(hours=10)
            elif not isinstance(news_list, list):
                news_list = []

            if not news_list:
                self._last_report_status = {"provider": "fallback", "reason": "no_news_returned"}
                return self._fallback_report([], 0, 0, reason="no_news_returned", fetch_stats=self._last_fetch_stats)

            candles_data = {}
            try:
                from main import get_forex_candles as get_mexc_candles
                oil_data = get_mexc_candles("EURUSD", "Min1", 420)
                silver_data = get_mexc_candles("USDJPY", "Min1", 420)
                if oil_data and oil_data.get("closes"): candles_data["oil"] = oil_data
                if silver_data and silver_data.get("closes"): candles_data["silver"] = silver_data
                self._last_candles_data = candles_data
                logging.info(f"📊 Tona: تم تحميل الشموع | oil={bool(candles_data.get('oil'))} silver={bool(candles_data.get('silver'))}")
            except Exception as e:
                logging.warning(f"⚠️ Tona: فشل تحميل الشموع: {e}")

            analyzed = []
            now_utc = datetime.now(timezone.utc)
            skipped_old = skipped_future = skipped_bad_time = 0

            for news in news_list[:60]:
                if not news:
                    continue
                pub_time = self._parse_published_time(news.get("published_at"))
                if pub_time is None:
                    skipped_bad_time += 1
                    continue
                pub_utc = pub_time.replace(tzinfo=timezone.utc) if pub_time.tzinfo is None else pub_time.astimezone(timezone.utc)
                age_hours = (now_utc - pub_utc).total_seconds() / 3600
                if age_hours < -0.10:
                    skipped_future += 1
                    continue
                if age_hours > NEWS_LOOKBACK_HOURS:
                    skipped_old += 1
                    continue
                try:
                    impact = self.analyze_news_impact(news, candles_data=candles_data)
                    impact["news_age_minutes"] = round(max(0, age_hours * 60), 1)
                    analyzed.append(impact)
                    if impact.get("is_significant", False):
                        self.store_active_news(impact)
                except Exception as e:
                    logging.warning(f"⚠️ Tona: فشل تحليل خبر '{self._safe_str(news.get('title'))[:80]}': {e}")

            self._last_fetch_stats["analyzed_items"] = len(analyzed)
            self._last_fetch_stats["skipped_old"] = skipped_old
            self._last_fetch_stats["skipped_future"] = skipped_future
            self._last_fetch_stats["skipped_bad_time"] = skipped_bad_time
            logging.info(f"🧠 Tona analysis: input={len(news_list)} analyzed={len(analyzed)} significant={sum(1 for n in analyzed if n.get('is_significant'))} old={skipped_old} future={skipped_future}")

            oil_price = 0; silver_price = 0
            if candles_data.get("oil", {}).get("closes"): oil_price = candles_data["oil"]["closes"][-1]
            if candles_data.get("silver", {}).get("closes"): silver_price = candles_data["silver"]["closes"][-1]

            # حتى عند عدم وجود خبر مؤثر، نرسل الحالة إلى النموذج بدلاً من إخفائها خلف fallback.
            return self._groq_report(analyzed, oil_price, silver_price, fetch_stats=self._last_fetch_stats)

        except Exception as e:
            logging.error(f"❌ فشل توليد التقرير الاستخباراتي: {e}")
            logging.debug(traceback.format_exc())
            self._last_report_status = {"provider": "error", "reason": f"{type(e).__name__}: {e}"}
            return f"⚠️ حدث خطأ أثناء توليد التقرير الاستخباراتي: {str(e)}"



# =====================================================================
# 🚀 دوال مساعدة للاستخدام الخارجي (باستخدام مثيل واحد)
# =====================================================================

def get_engine() -> TonaEliteEngine:
    """الحصول على مثيل واحد من المحرك (Singleton)"""
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = TonaEliteEngine()
    return _ENGINE_INSTANCE


def generate_intelligence_report():
    try:
        engine = get_engine()
        return engine.generate_elite_analysis()
    except Exception as e:
        logging.error(f"❌ فشل في generate_intelligence_report: {e}")
        logging.debug(traceback.format_exc())
        return f"⚠️ حدث خطأ أثناء توليد التقرير: {str(e)}"


def get_active_news(asset_type: str = None) -> List[Dict]:
    """استرجاع الأخبار المؤثرة النشطة (باستخدام المثيل الوحيد)"""
    try:
        engine = get_engine()
        return engine.get_active_news(asset_type)
    except Exception as e:
        logging.error(f"❌ فشل في get_active_news: {e}")
        return []


def get_strongest_news(asset_type: str = None) -> Optional[Dict]:
    """استرجاع أقوى خبر مؤثر حالياً (باستخدام المثيل الوحيد)"""
    try:
        engine = get_engine()
        return engine.get_strongest_news(asset_type)
    except Exception as e:
        logging.error(f"❌ فشل في get_strongest_news: {e}")
        return None
