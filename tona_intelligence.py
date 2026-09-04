"""
Tona Elite Intelligence Engine - Forex Edition
مخصص حصرياً لـ EUR/USD و USD/JPY.

المبدأ:
- الأخبار الاقتصادية/الجيوسياسية ذات الصلة بالزوجين فقط.
- قياس حركة السعر الفعلية بعد الخبر، وعدم اختلاق السببية.
- لا يغيّر استراتيجية SuperTrend/VPT ولا يدخل في قرار الإشارة.
- يستخدم candle_fetcher المحقون من main.py، وبالتالي لا ينشئ مزود سوق مستقل.
- Breaking News Radar يعمل بدورة مستقلة (يحددها main.py، افتراضياً 30 دقيقة).
"""

import os
import time
import json
import re
import hashlib
import logging
import threading
import traceback
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

NEWS_LOOKBACK_HOURS = 6
IMPACT_THRESHOLDS = {
    "low": 0.05,
    "medium": 0.15,
    "high": 0.30,
    "very_high": 0.60,
}

FOREX_ASSETS = ("eurusd", "usdjpy")
FOREX_LABELS = {
    "eurusd": "EUR/USD",
    "usdjpy": "USD/JPY",
}
FOREX_SYMBOLS = {
    "eurusd": "eurusd",
    "usdjpy": "usdjpy",
}

_GLOBAL_ACTIVE_NEWS: List[Dict] = []
_ENGINE_INSTANCE = None


class TonaEliteEngine:
    def __init__(self, memory=None, market_analyzer=None, groq_api_key=None,
                 news_api_key=None, candle_fetcher=None):
        self.memory = memory
        self.market_analyzer = market_analyzer
        self.groq_api_key = groq_api_key or GROQ_API_KEY
        self.news_api_key = news_api_key or NEWS_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.candle_fetcher = candle_fetcher
        self._active_news = _GLOBAL_ACTIVE_NEWS
        self._radar_alert_history = {}
        self._radar_alert_times = []
        self._radar_lock = threading.Lock()
        self._radar_thread = None
        self._radar_stop = threading.Event()
        self._last_fetch_stats = {
            "sources_total": 0, "sources_ok": 0, "sources_failed": 0,
            "raw_items": 0, "filtered_items": 0, "unique_items": 0, "errors": []
        }
        self._last_report_status = {"provider": "none", "reason": "not_run"}

        self.trusted_sources = [
            "Reuters", "Bloomberg", "CNBC", "Financial Times", "Wall Street Journal",
            "The Economist", "MarketWatch", "BBC", "CNN", "Al Jazeera", "Sky News",
            "الجزيرة", "العربية", "سكاي نيوز عربية", "ECB", "European Central Bank",
            "Federal Reserve", "Fed", "Bank of Japan", "BoJ", "日本銀行", "MOF Japan"
        ]
        self.exclude_keywords = [
            "sport", "football", "cricket", "tennis", "basketball", "entertainment",
            "celebrity", "movie", "music", "concert", "hollywood", "fashion", "beauty",
            "makeup", "wedding", "birthday", "recipe", "gaming"
        ]

        logging.info("✅ Tona Elite Intelligence Engine — Forex Edition initialized (EUR/USD + USD/JPY)")

    # ------------------------------------------------------------------
    # RSS / News collection
    # ------------------------------------------------------------------
    def _fetch_rss_feed(self, feed_url, max_items=10):
        try:
            response = requests.get(
                feed_url, timeout=10,
                headers={"User-Agent": "Mozilla/5.0 Tona-Forex-Intelligence/1.0"}
            )
            if response.status_code != 200:
                return []
            root = ET.fromstring(response.content)
            items = []
            for item in root.findall('.//item')[:max_items]:
                title = item.find('title')
                desc = item.find('description')
                pub_date = item.find('pubDate')
                link = item.find('link')
                if title is not None and title.text:
                    items.append({
                        "title": self._safe_str(title.text),
                        "description": self._safe_str(desc.text if desc is not None else ""),
                        "url": self._safe_str(link.text if link is not None else ""),
                        "source": feed_url.split('/')[2],
                        "published_at": self._safe_str(pub_date.text if pub_date is not None else "") or datetime.now(timezone.utc).isoformat(),
                        "is_trusted": True,
                    })
            return items
        except Exception as exc:
            logging.debug(f"Tona Forex RSS error {feed_url}: {exc}")
            return []

    def _forex_rss_feeds(self):
        queries = [
            "EUR USD euro ECB Fed interest rates inflation CPI PMI",
            "USD JPY yen Bank of Japan BoJ Ueda intervention Japan inflation wages",
            "Federal Reserve Fed dollar Treasury yields inflation jobs GDP EUR USD JPY",
            "ECB euro interest rates Lagarde eurozone inflation GDP PMI EUR USD",
            "US dollar yen safe haven risk aversion geopolitical USD JPY",
        ]
        return [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://feeds.skynews.com/feeds/rss/business.xml",
            "https://feeds.skynews.com/feeds/rss/world.xml",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://www.dw.com/en/english-news/rss",
        ] + [
            "https://news.google.com/rss/search?q=" + quote_plus(q) + "&hl=en-US&gl=US&ceid=US:en"
            for q in queries
        ]

    def fetch_targeted_intelligence(self, hours=NEWS_LOOKBACK_HOURS):
        """جمع أخبار اقتصادية/جيوسياسية تخص EUR/USD أو USD/JPY فقط."""
        all_news = []
        stats = {"sources_total": 0, "sources_ok": 0, "sources_failed": 0,
                 "raw_items": 0, "filtered_items": 0, "unique_items": 0, "errors": []}

        feeds = self._forex_rss_feeds()
        stats["sources_total"] = len(feeds)
        for feed_url in feeds:
            try:
                items = self._fetch_rss_feed(feed_url)
                if items:
                    stats["sources_ok"] += 1
                    stats["raw_items"] += len(items)
                else:
                    stats["sources_failed"] += 1
                for item in items:
                    text = (self._safe_str(item.get("title")) + " " + self._safe_str(item.get("description"))).lower()
                    if any(k in text for k in self.exclude_keywords):
                        continue
                    if self._is_target_news(item):
                        item["collection_method"] = "rss"
                        item["target_assets"] = self._news_target_assets(item)
                        all_news.append(item)
                        stats["filtered_items"] += 1
            except Exception as exc:
                stats["sources_failed"] += 1
                stats["errors"].append(f"RSS:{type(exc).__name__}")

        if self.news_api_key:
            queries = [
                "EUR USD ECB eurozone inflation interest rates PMI GDP",
                "USD JPY Bank of Japan yen Ueda intervention Japan inflation wages",
                "Federal Reserve dollar inflation interest rates jobs Treasury yields",
                "euro ECB Fed EUR USD",
                "yen BoJ Fed USD JPY",
            ]
            stats["sources_total"] += len(queries)
            from_date = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
            for query in queries:
                try:
                    url = (
                        "https://newsapi.org/v2/everything?"
                        f"q={quote_plus(query)}&from={from_date}&sortBy=publishedAt&language=en"
                        f"&apiKey={self.news_api_key}&pageSize=15"
                    )
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        stats["sources_failed"] += 1
                        stats["errors"].append(f"NewsAPI:{response.status_code}")
                        continue
                    stats["sources_ok"] += 1
                    articles = (response.json() or {}).get("articles", []) or []
                    stats["raw_items"] += len(articles)
                    for article in articles:
                        candidate = {
                            "title": self._safe_str(article.get("title")),
                            "description": self._safe_str(article.get("description")),
                            "url": self._safe_str(article.get("url")),
                            "source": self._safe_str((article.get("source") or {}).get("name")) or "NewsAPI",
                            "published_at": self._safe_str(article.get("publishedAt")) or datetime.now(timezone.utc).isoformat(),
                            "is_trusted": True,
                            "collection_method": "newsapi",
                        }
                        text = (candidate["title"] + " " + candidate["description"]).lower()
                        if not candidate["title"] or any(k in text for k in self.exclude_keywords):
                            continue
                        if self._is_target_news(candidate):
                            candidate["target_assets"] = self._news_target_assets(candidate)
                            all_news.append(candidate)
                            stats["filtered_items"] += 1
                except Exception as exc:
                    stats["sources_failed"] += 1
                    stats["errors"].append(f"NewsAPI:{type(exc).__name__}")
        else:
            logging.debug("Tona Forex: NEWS_API_KEY غير موجود؛ الاعتماد على RSS")

        seen = set()
        unique = []
        for news in all_news:
            title = re.sub(r"\s+", " ", self._safe_str(news.get("title"))).strip().lower()
            key = hashlib.sha256(title.encode("utf-8")).hexdigest() if title else hashlib.sha256(self._safe_str(news).encode("utf-8")).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(news)

        stats["unique_items"] = len(unique)
        self._last_fetch_stats = stats
        logging.info(
            f"📰 Tona Forex sources: {stats['sources_ok']}/{stats['sources_total']} OK | "
            f"raw={stats['raw_items']} | relevant={stats['filtered_items']} | unique={stats['unique_items']}"
        )
        if stats["errors"]:
            logging.warning(f"⚠️ Tona Forex news source errors: {stats['errors'][:5]}")
        return unique[:80]

    # ------------------------------------------------------------------
    # Asset targeting: strict Forex logic
    # ------------------------------------------------------------------
    def _news_target_assets(self, news_item: Dict) -> List[str]:
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()

        euro_direct = [
            "eur/usd", "eurusd", "euro dollar", "euro-dollar", "euro",
            "ecb", "european central bank", "eurozone", "euro area",
            "lagarde", "germany inflation", "german inflation", "eurozone inflation",
            "eurozone pmi", "eurozone gdp", "eurozone jobs", "eurozone unemployment",
            "اليورو", "البنك المركزي الأوروبي", "منطقة اليورو", "التضخم الأوروبي"
        ]
        yen_direct = [
            "usd/jpy", "usdjpy", "dollar yen", "dollar-yen", "yen",
            "jpy", "boj", "bank of japan", "bank of japan governor", "ueda",
            "japan inflation", "japan cpi", "japan wages", "japan gdp", "japan pmi",
            "japan unemployment", "fx intervention", "currency intervention", "mof japan",
            "الين", "بنك اليابان", "اليابان", "تدخل العملة"
        ]
        usd_macro = [
            "us dollar", "usd", "dollar", "federal reserve", "fed", "powell",
            "us interest rate", "u.s. interest rate", "rate cut", "rate hike",
            "us inflation", "us cpi", "core cpi", "pce", "nonfarm payroll", "nfp",
            "payrolls", "us jobs", "unemployment rate", "us gdp", "us pmi",
            "treasury yield", "us yields", "bond yields", "العائد الأمريكي", "الفيدرالي",
            "الدولار", "الوظائف الأمريكية", "التضخم الأمريكي"
        ]
        risk_euro = [
            "european risk", "europe sanctions", "european energy", "european recession",
            "european political crisis", "eurozone political", "euro area crisis"
        ]
        risk_yen = [
            "risk aversion", "safe haven yen", "flight to safety", "market turmoil",
            "geopolitical escalation", "geopolitical risk", "war", "conflict", "crisis",
            "التوتر الجيوسياسي", "العزوف عن المخاطرة", "ملاذ آمن", "حرب", "أزمة"
        ]

        eur = any(k in text for k in euro_direct) or any(k in text for k in risk_euro)
        jpy = any(k in text for k in yen_direct)

        # أخبار الدولار/الفيدرالي تؤثر على جانبي الزوجين، لذلك تُربط بهما معاً.
        usd = any(k in text for k in usd_macro)
        if usd:
            eur = True
            jpy = True

        # الأخبار الجيوسياسية العامة لا تُربط تلقائياً بالزوجين؛ يجب وجود قناة FX واضحة.
        if any(k in text for k in risk_yen) and any(k in text for k in ["yen", "jpy", "dollar", "usd", "safe haven", "risk aversion", "الين", "الدولار"]):
            jpy = True
        if any(k in text for k in ["europe", "european", "euro", "eur", "eurozone", "اليورو", "أوروبا"]) and any(k in text for k in ["risk", "crisis", "war", "sanctions", "energy", "التوتر", "أزمة", "عقوبات"]):
            eur = True

        return (["eurusd"] if eur else []) + (["usdjpy"] if jpy else [])

    def _is_target_news(self, news_item: Dict) -> bool:
        title = self._safe_str(news_item.get("title")).strip()
        if not title:
            return False
        text = (title + " " + self._safe_str(news_item.get("description"))).lower()
        if any(k in text for k in self.exclude_keywords):
            return False
        return bool(self._news_target_assets(news_item))

    def _news_asset(self, news_item: Dict) -> str:
        targets = self._news_target_assets(news_item)
        return targets[0] if len(targets) == 1 else "eurusd/usdjpy"

    # ------------------------------------------------------------------
    # Event scoring
    # ------------------------------------------------------------------
    def _news_potential(self, news_item: Dict) -> Dict:
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        high = [
            "federal reserve", "fed", "powell", "interest rate", "rate cut", "rate hike",
            "ecb", "european central bank", "lagarde", "bank of japan", "boj", "ueda",
            "intervention", "currency intervention", "nfp", "nonfarm payroll", "cpi", "pce",
            "emergency", "surprise", "unexpected", "central bank", "الفيدرالي", "البنك المركزي الأوروبي",
            "بنك اليابان", "تدخل العملة", "الوظائف الأمريكية", "التضخم"
        ]
        medium = [
            "gdp", "pmi", "employment", "unemployment", "wages", "retail sales", "ppi",
            "consumer confidence", "manufacturing", "services", "treasury yield", "bond yields",
            "eurozone", "japan", "euro", "yen", "dollar"
        ]
        market_words = ["surprise", "unexpected", "record", "largest", "cut", "increase", "decrease", "مفاجئ", "غير متوقع", "قياسي", "خفض", "زيادة", "انخفاض"]
        h = sum(1 for k in high if k in text)
        m = sum(1 for k in medium if k in text)
        mw = sum(1 for k in market_words if k in text)
        score = min(100, 20 + h * 11 + m * 4 + mw * 3)
        level = "مرتفع جداً" if score >= 80 else "مرتفع" if score >= 60 else "متوسط" if score >= 40 else "منخفض"
        return {"score": score, "level": level, "high_terms": h, "medium_terms": m, "market_terms": mw}

    def _event_window_status(self, age_min: float, has_15: bool, has_60: bool) -> str:
        if age_min < 15:
            return "مبكر - لم تكتمل نافذة 15 دقيقة"
        if age_min < 60:
            return "جزئي - نافذة 15 دقيقة مكتملة و60 دقيقة غير مكتملة" if has_15 else "غير مكتمل"
        return "مكتمل 15/60 دقيقة" if has_60 else "غير مكتمل - لا توجد بيانات كافية لـ60 دقيقة"

    def _expected_news_direction(self, news_item: Dict, asset: str) -> Dict:
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        bull = []
        bear = []
        if asset == "eurusd":
            bull = ["ecb hike", "ecb hawkish", "rate hike", "eurozone growth", "eurozone inflation", "strong euro", "eur strength", "تشدد المركزي الأوروبي", "رفع الفائدة", "قوة اليورو"]
            bear = ["ecb cut", "ecb dovish", "rate cut", "eurozone recession", "weak euro", "eur weakness", "خفض الفائدة", "ضعف اليورو", "ركود منطقة اليورو"]
        else:
            # الاتجاه هنا هو USD/JPY نفسه: قوة الدولار/ضعف الين تميل للصعود.
            bull = ["fed hawkish", "rate hike", "higher yields", "strong dollar", "weak yen", "yen weakness", "dovish boj", "تشدد الفيدرالي", "رفع الفائدة", "ارتفاع العوائد", "قوة الدولار", "ضعف الين"]
            bear = ["fed dovish", "rate cut", "lower yields", "weak dollar", "strong yen", "yen strength", "hawkish boj", "خفض الفائدة", "انخفاض العوائد", "ضعف الدولار", "قوة الين"]
        b = sum(1 for x in bull if x in text)
        s = sum(1 for x in bear if x in text)
        if b > s:
            return {"direction": "صعود", "strength": min(100, 50 + (b - s) * 15), "bull_terms": b, "bear_terms": s}
        if s > b:
            return {"direction": "هبوط", "strength": min(100, 50 + (s - b) * 15), "bull_terms": b, "bear_terms": s}
        return {"direction": "محايد", "strength": 40, "bull_terms": b, "bear_terms": s}

    def _news_relevance(self, news_item: Dict, asset: str) -> int:
        text = (self._safe_str(news_item.get("title")) + " " + self._safe_str(news_item.get("description"))).lower()
        if asset == "eurusd":
            direct = ["eur/usd", "eurusd", "euro dollar", "euro", "ecb", "eurozone", "euro area", "lagarde", "اليورو", "البنك المركزي الأوروبي", "منطقة اليورو"]
            indirect = ["fed", "federal reserve", "dollar", "usd", "us inflation", "us jobs", "treasury yields", "الفيدرالي", "الدولار"]
        else:
            direct = ["usd/jpy", "usdjpy", "dollar yen", "yen", "jpy", "boj", "bank of japan", "ueda", "japan inflation", "japan wages", "intervention", "الين", "بنك اليابان", "اليابان"]
            indirect = ["fed", "federal reserve", "dollar", "usd", "us inflation", "us jobs", "treasury yields", "risk aversion", "الفيدرالي", "الدولار"]
        d = sum(1 for x in direct if x in text)
        i = sum(1 for x in indirect if x in text)
        return min(100, 45 + d * 10 + i * 5)

    def _compare_news_hypothesis(self, expected: Dict, actual_change: float) -> Dict:
        if actual_change is None or abs(actual_change) < 1e-12:
            return {"match": "غير قابل للحكم", "score": 0}
        actual = "صعود" if actual_change > 0 else "هبوط"
        if expected.get("direction") == "محايد":
            return {"match": "محايد/غير حاسم", "score": 40}
        if actual == expected.get("direction"):
            return {"match": "متوافق", "score": min(100, 60 + int(expected.get("strength", 0) * 0.4))}
        return {"match": "متعارض", "score": max(0, 40 - int(expected.get("strength", 0) * 0.3))}

    # ------------------------------------------------------------------
    # Price measurement
    # ------------------------------------------------------------------
    def _get_price_at_time(self, asset_type: str, minutes_ago: int = 5, candles_data: Dict = None) -> Optional[float]:
        if asset_type not in FOREX_ASSETS:
            return None
        if candles_data and asset_type in candles_data:
            data = candles_data[asset_type] or {}
            closes = data.get("closes") or []
            if not closes:
                return None
            idx = min(max(0, int(minutes_ago)), len(closes) - 1)
            try:
                return float(closes[-idx - 1])
            except (TypeError, ValueError):
                return None
        if self.candle_fetcher:
            try:
                data = self.candle_fetcher(FOREX_SYMBOLS[asset_type], "Min1", min(500, max(20, abs(minutes_ago) + 5)))
                closes = (data or {}).get("closes") or []
                if closes:
                    idx = min(max(0, int(minutes_ago)), len(closes) - 1)
                    return float(closes[-idx - 1])
            except Exception as exc:
                logging.debug(f"Tona Forex price fetch failed: {exc}")
        return None

    def analyze_news_impact(self, news_item: Dict, candles_data: Dict = None) -> Dict:
        targets = self._news_target_assets(news_item)
        potential = self._news_potential(news_item)
        result = {
            "title": self._safe_str(news_item.get("title")),
            "description": self._safe_str(news_item.get("description")),
            "source": self._safe_str(news_item.get("source")),
            "published_at": self._safe_str(news_item.get("published_at")),
            "target_assets": targets,
            "is_significant": False, "direction": "محايد", "classification": "غير مؤثر",
            "change_pct": None, "asset": targets[0] if len(targets) == 1 else "eurusd/usdjpy",
            "news_potential_score": potential["score"], "news_potential": potential["level"],
            "measurement_status": "غير مقاس", "causality": "غير مثبت",
        }
        for asset in FOREX_ASSETS:
            result[f"{asset}_change_15m"] = None
            result[f"{asset}_change_60m"] = None
            result[f"{asset}_price_before"] = None
            result[f"{asset}_price_at_news"] = None
            result[f"{asset}_price_15min"] = None
            result[f"{asset}_price_60min"] = None

        try:
            pub_time = self._parse_published_time(news_item.get("published_at"))
            if pub_time is None:
                result["measurement_status"] = "وقت الخبر غير صالح"
                return result
            pub_utc = pub_time.replace(tzinfo=timezone.utc) if pub_time.tzinfo is None else pub_time.astimezone(timezone.utc)
            age_min = max(0.0, (datetime.now(timezone.utc) - pub_utc).total_seconds() / 60.0)
            result["news_age_minutes"] = round(age_min, 1)

            measured = []
            has15 = has60 = False
            for asset in targets:
                closes = ((candles_data or {}).get(asset) or {}).get("closes") or []
                if len(closes) < 20:
                    continue
                n = len(closes)
                event_idx = n - 1 - int(round(age_min))
                if not (0 <= event_idx < n):
                    continue
                try:
                    p_event = float(closes[event_idx])
                    p_before = float(closes[max(0, event_idx - 30)])
                except (TypeError, ValueError):
                    continue
                if p_event <= 0 or p_before <= 0:
                    continue
                result[f"{asset}_price_before"] = round(p_before, 6)
                result[f"{asset}_price_at_news"] = round(p_event, 6)

                idx15, idx60 = event_idx + 15, event_idx + 60
                if idx15 < n:
                    try:
                        p15 = float(closes[idx15])
                        ch15 = (p15 - p_event) / p_event * 100
                        result[f"{asset}_price_15min"] = round(p15, 6)
                        result[f"{asset}_change_15m"] = round(ch15, 5)
                        measured.append((asset, "15m", ch15))
                        has15 = True
                    except (TypeError, ValueError):
                        pass
                if idx60 < n:
                    try:
                        p60 = float(closes[idx60])
                        ch60 = (p60 - p_event) / p_event * 100
                        result[f"{asset}_price_60min"] = round(p60, 6)
                        result[f"{asset}_change_60m"] = round(ch60, 5)
                        measured.append((asset, "60m", ch60))
                        has60 = True
                    except (TypeError, ValueError):
                        pass

            result["measurement_status"] = self._event_window_status(age_min, has15, has60)
            if not measured:
                return result

            best_asset, best_window, best_change = max(measured, key=lambda x: abs(x[2]))
            result["asset"] = best_asset
            result["change_pct"] = round(best_change, 5)
            result["direction"] = "صعود" if best_change > 0 else "هبوط" if best_change < 0 else "محايد"
            result["measurement_window"] = best_window
            result["max_measured_change"] = round(abs(best_change), 5)

            relevance = self._news_relevance(news_item, best_asset)
            expected = self._expected_news_direction(news_item, best_asset)
            hypothesis = self._compare_news_hypothesis(expected, best_change)
            confidence = 0.30 * potential["score"] + 0.25 * relevance + 0.15 * hypothesis["score"] + 0.30 * min(100, abs(best_change) / IMPACT_THRESHOLDS["very_high"] * 70)
            result.update({
                "asset_relevance_score": relevance,
                "expected_direction": expected["direction"],
                "expected_direction_strength": expected["strength"],
                "direction_hypothesis_match": hypothesis["match"],
                "direction_hypothesis_score": hypothesis["score"],
                "intelligence_confidence": max(0, min(100, round(confidence))),
            })
            mc = abs(best_change)
            if mc >= IMPACT_THRESHOLDS["very_high"]:
                result["classification"], result["is_significant"] = "قوي جداً", True
            elif mc >= IMPACT_THRESHOLDS["high"]:
                result["classification"], result["is_significant"] = "قوي", True
            elif mc >= IMPACT_THRESHOLDS["medium"]:
                result["classification"], result["is_significant"] = "متوسط", True
            elif mc >= IMPACT_THRESHOLDS["low"]:
                result["classification"] = "ضعيف"
            result["causality"] = "ارتباط زمني قوي، السببية غير مثبتة" if result["is_significant"] else "لا توجد حركة سعرية قوية كافية لإسناد أثر مباشر"
            return result
        except Exception as exc:
            result["measurement_status"] = f"خطأ: {type(exc).__name__}"
            logging.error(f"❌ Tona Forex news analysis error: {exc}")
            return result

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------
    def _safe_str(self, value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    def _parse_published_time(self, published_at: str) -> Optional[datetime]:
        if not published_at:
            return None
        formats = [
            "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(published_at, fmt)
            except Exception:
                pass
        try:
            return datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
        except Exception:
            return None

    def store_active_news(self, impact: Dict):
        if not impact or not impact.get("is_significant") or impact.get("asset") not in FOREX_ASSETS:
            return
        expiry = datetime.now() + timedelta(hours=2)
        entry = {
            "title": impact.get("title", "خبر غير معروف"),
            "direction": impact.get("direction", "محايد"),
            "change_pct": impact.get("change_pct", 0.0),
            "asset": impact.get("asset"),
            "classification": impact.get("classification", "غير مؤثر"),
            "expiry": expiry, "timestamp": datetime.now().isoformat(),
            "source": impact.get("source", "غير معروف")
        }
        self._active_news[:] = [n for n in self._active_news if n.get("title") != entry["title"]]
        self._active_news.append(entry)
        self.clear_expired_news()

    def get_active_news(self, asset_type: str = None) -> List[Dict]:
        self.clear_expired_news()
        if asset_type:
            if asset_type not in FOREX_ASSETS:
                return []
            return [n for n in self._active_news if n.get("asset") == asset_type]
        return self._active_news.copy()

    def clear_expired_news(self):
        now = datetime.now()
        self._active_news[:] = [n for n in self._active_news if n.get("expiry", now) > now]
        if len(self._active_news) > 50:
            del self._active_news[:-50]

    def get_strongest_news(self, asset_type: str = None) -> Optional[Dict]:
        items = self.get_active_news(asset_type)
        return max(items, key=lambda x: abs(float(x.get("change_pct", 0) or 0)), default=None)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def _arabic_title(self, item: Dict) -> str:
        for key in ("title_ar", "arabic_title", "summary_ar"):
            value = self._safe_str(item.get(key)).strip()
            if value and not re.search(r"[A-Za-z]{3,}", value):
                return value[:180]
        raw = self._safe_str(item.get("title")).lower()
        mappings = [
            (("federal reserve",), "تطورات السياسة النقدية الأمريكية"),
            (("ecb",), "تطورات السياسة النقدية للبنك المركزي الأوروبي"),
            (("bank of japan",), "تطورات السياسة النقدية لبنك اليابان"),
            (("boj",), "تطورات السياسة النقدية لبنك اليابان"),
            (("inflation", "euro"), "تطورات التضخم في منطقة اليورو وتأثيرها المحتمل على اليورو"),
            (("inflation", "japan"), "تطورات التضخم الياباني وتأثيرها المحتمل على الين"),
            (("yen", "intervention"), "تطورات تدخل السلطات اليابانية في سوق العملات"),
            (("nfp",), "بيانات الوظائف الأمريكية وتأثيرها المحتمل على الدولار"),
            (("treasury", "yield"), "تحرك عوائد السندات الأمريكية وتأثيره على الدولار"),
        ]
        for keys, title in mappings:
            if all(k in raw for k in keys):
                return title
        return self._safe_str(item.get("title"))[:180] or "حدث اقتصادي مرتبط بسوق العملات"

    def _format_price(self, asset: str, value: Any) -> str:
        if not isinstance(value, (int, float)):
            return "غير متاح"
        decimals = 5 if asset == "eurusd" else 3
        return f"{value:.{decimals}f}"

    def _fallback_report(self, analyzed_news, eurusd_price=None, usdjpy_price=None, reason="no_significant_news", fetch_stats=None) -> str:
        try:
            significant = [x for x in (analyzed_news or []) if x and x.get("is_significant") and x.get("asset") in FOREX_ASSETS]
            lines = ["🧠 تقرير تولين الاستخباراتي — Forex", ""]
            if significant:
                lines.append("📰 الأخبار المؤثرة المقاسة سعرياً")
                for x in sorted(significant, key=lambda z: abs(float(z.get("change_pct") or 0)), reverse=True)[:6]:
                    asset = x["asset"]
                    label = FOREX_LABELS[asset]
                    change = x.get("change_pct")
                    direction = "ارتفع" if change > 0 else "انخفض" if change < 0 else "تحرك بشكل محدود"
                    p0 = x.get(f"{asset}_price_at_news")
                    plast = x.get(f"{asset}_price_60min") if isinstance(x.get(f"{asset}_price_60min"), (int, float)) else x.get(f"{asset}_price_15min")
                    title = self._arabic_title(x)
                    if isinstance(p0, (int, float)) and isinstance(plast, (int, float)):
                        lines.append(f"• {label}: {title}. بعد الخبر {direction} السعر من {self._format_price(asset,p0)} إلى {self._format_price(asset,plast)} ({change:+.3f}%).")
                    else:
                        lines.append(f"• {label}: {title}. {direction} السعر بنحو {abs(change):.3f}%.")
                lines.extend(["", "⚖️ الحكم النهائي"])
                for asset in FOREX_ASSETS:
                    rows = [x for x in significant if x.get("asset") == asset]
                    if not rows:
                        continue
                    vals = [float(x["change_pct"]) for x in rows if isinstance(x.get("change_pct"), (int, float))]
                    if not vals:
                        continue
                    avg = sum(vals) / len(vals)
                    label = FOREX_LABELS[asset]
                    trend = "يميل إلى الصعود" if avg >= IMPACT_THRESHOLDS["medium"] else "يميل إلى الهبوط" if avg <= -IMPACT_THRESHOLDS["medium"] else "متباين/محايد"
                    lines.append(f"• {label}: {trend} وفق الحركة السعرية المقاسة بعد الأخبار.")
            else:
                stats = fetch_stats or self._last_fetch_stats or {}
                if stats.get("sources_total") and not stats.get("sources_ok"):
                    lines.append("⚠️ تعذر الوصول إلى مصادر الأخبار في هذه الدورة، لذلك لا يمكن إصدار حكم استخباراتي موثوق.")
                else:
                    lines.append("📭 لم يظهر خبر اقتصادي أو جيوسياسي مرتبط مباشرة بـ EUR/USD أو USD/JPY ورافقته حركة سعرية كافية للقياس.")
                lines.extend(["", "⚖️ الحكم النهائي: لا توجد أدلة خبرية وسعرية كافية لاتجاه واضح حالياً."])
            lines.extend([
                "",
                "💡 يعتمد الحكم على الخبر المرتبط بالزوج وحركة السعر الفعلية بعده، ولا يفترض السببية من التزامن وحده.",
                "💙 هذا المحرك استشاري ولا يغيّر استراتيجية SuperTrend/VPT."
            ])
            return "\n".join(lines).strip()
        except Exception as exc:
            logging.error(f"❌ Tona Forex fallback report failed: {exc}")
            return "🧠 تقرير تولين الاستخباراتي — Forex\n\nتعذر توليد التقرير حالياً."

    def _groq_report(self, analyzed_news: List[Dict], eurusd_price=None, usdjpy_price=None, fetch_stats=None) -> str:
        if not self.groq_api_key:
            return self._fallback_report(analyzed_news, eurusd_price, usdjpy_price, "missing_groq_api_key", fetch_stats)

        rows = []
        for x in analyzed_news or []:
            if x.get("asset") not in FOREX_ASSETS or not x.get("is_significant"):
                continue
            asset = x["asset"]
            rows.append(
                f"الزوج={FOREX_LABELS[asset]} | الخبر={self._arabic_title(x)} | "
                f"التغير={float(x.get('change_pct') or 0):+.3f}% | "
                f"الاتجاه={x.get('direction')} | السببية={x.get('causality')}"
            )
        data_text = "\n".join(rows) if rows else "لا توجد أخبار مؤثرة مقاسة سعرياً."
        prompt = f"""أنت طبقة صياغة لمحرك استخبارات فوركس. لا تخترع أخباراً أو أرقاماً أو أسباباً.\n"
""الأصول الوحيدة هي EUR/USD وUSD/JPY.\n"
"استخدم فقط البيانات التالية، ووضح أن السببية غير مثبتة عندما تكون كذلك.\n"
"EUR/USD الحالي={self._format_price('eurusd', eurusd_price)}\n"
"USD/JPY الحالي={self._format_price('usdjpy', usdjpy_price)}\n"
"البيانات:\n{data_text}\n"
"اكتب تقريراً عربياً واضحاً ومختصراً، ثم حكماً منفصلاً لكل زوج: صاعد/هابط/محايد."""
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": "أنت محرر استخباراتي مالي دقيق؛ لا تخترع أي معلومة."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 1200,
        }
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=25,
            )
            if response.status_code == 200:
                body = response.json()
                choice = (body.get("choices") or [{}])[0]
                content = self._safe_str((choice.get("message") or {}).get("content")).strip()
                if self._complete_report_text(content, choice.get("finish_reason")):
                    self._last_report_status = {"provider": "groq", "reason": "success"}
                    return content
            logging.warning(f"⚠️ Tona Forex Groq failed HTTP {response.status_code}")
        except Exception as exc:
            logging.warning(f"⚠️ Tona Forex Groq exception: {exc}")
        self._last_report_status = {"provider": "fallback", "reason": "groq_failed"}
        return self._fallback_report(analyzed_news, eurusd_price, usdjpy_price, "groq_failed", fetch_stats)

    def _complete_report_text(self, content, finish_reason=None):
        content = self._safe_str(content).strip()
        if not content or finish_reason in {"length", "max_tokens"}:
            return False
        return len(re.sub(r"\s+", " ", content)) >= 80

    def generate_elite_analysis(self, news_list=None):
        """إنشاء تقرير استخباراتي Forex مستقل عن ماسح SuperTrend/VPT."""
        try:
            news_list = self.fetch_targeted_intelligence(hours=NEWS_LOOKBACK_HOURS) if news_list is None else (news_list if isinstance(news_list, list) else [])
            candles = {}
            for asset in FOREX_ASSETS:
                try:
                    if self.candle_fetcher:
                        data = self.candle_fetcher(FOREX_SYMBOLS[asset], "Min1", 420)
                    else:
                        from main import get_forex_candles
                        data = get_forex_candles(FOREX_SYMBOLS[asset], "Min1", 420)
                    if data and data.get("closes"):
                        candles[asset] = data
                except Exception as exc:
                    logging.warning(f"⚠️ Tona Forex: فشل تحميل بيانات {FOREX_LABELS[asset]}: {exc}")

            analyzed = []
            for item in news_list[:80]:
                if isinstance(item, dict) and self._is_target_news(item):
                    analyzed.append(self.analyze_news_impact(item, candles))

            eurusd_price = (candles.get("eurusd") or {}).get("closes", [None])[-1]
            usdjpy_price = (candles.get("usdjpy") or {}).get("closes", [None])[-1]

            # تخزين الأحداث القوية فقط.
            for impact in analyzed:
                if impact.get("is_significant"):
                    self.store_active_news(impact)

            # لا نعرض إلا ما تم قياس أثره فعلياً.
            significant = [x for x in analyzed if x.get("is_significant") and x.get("asset") in FOREX_ASSETS]
            if self.groq_api_key and significant:
                return self._groq_report(significant, eurusd_price, usdjpy_price, self._last_fetch_stats)
            self._last_report_status = {"provider": "fallback", "reason": "no_groq_or_no_significant_news"}
            return self._fallback_report(analyzed, eurusd_price, usdjpy_price, "no_significant_news", self._last_fetch_stats)
        except Exception as exc:
            logging.error(f"❌ Tona Forex elite analysis failed: {exc}")
            logging.debug(traceback.format_exc())
            return "🧠 تقرير تولين الاستخباراتي — Forex\n\nتعذر توليد التقرير حالياً، لذلك لا يوجد حكم استخباراتي موثوق في هذه الدورة."

    # ------------------------------------------------------------------
    # Breaking News Radar — مستقل عن دورة 60 ثانية
    # ------------------------------------------------------------------
    def _radar_once(self, notify_callback=None, open_trades_provider=None):
        try:
            news = self.fetch_targeted_intelligence(hours=2)
            if not news:
                return
            candles = {}
            for asset in FOREX_ASSETS:
                try:
                    if self.candle_fetcher:
                        data = self.candle_fetcher(FOREX_SYMBOLS[asset], "Min1", 180)
                    else:
                        from main import get_forex_candles
                        data = get_forex_candles(FOREX_SYMBOLS[asset], "Min1", 180)
                    if data and data.get("closes"):
                        candles[asset] = data
                except Exception:
                    pass

            open_trades = open_trades_provider() if callable(open_trades_provider) else {}
            for item in news[:50]:
                pub = self._parse_published_time(item.get("published_at"))
                if pub is None:
                    continue
                pub_utc = pub.replace(tzinfo=timezone.utc) if pub.tzinfo is None else pub.astimezone(timezone.utc)
                age = (datetime.now(timezone.utc) - pub_utc).total_seconds() / 60
                if age < 0 or age > 45:
                    continue
                impact = self.analyze_news_impact(item, candles)
                if not impact.get("is_significant"):
                    continue
                key = hashlib.sha256((self._safe_str(item.get("title")) + str(impact.get("asset"))).encode("utf-8")).hexdigest()
                with self._radar_lock:
                    if key in self._radar_alert_history:
                        continue
                    self._radar_alert_history[key] = time.time()
                asset = impact.get("asset")
                label = FOREX_LABELS.get(asset, asset)
                msg = (
                    f"🚨 Tona Forex Breaking Radar\n\n"
                    f"📌 الزوج: {label}\n"
                    f"📰 الخبر: {self._arabic_title(impact)}\n"
                    f"📊 الحركة المقاسة بعد الخبر: {impact.get('change_pct', 0):+.3f}% ({impact.get('direction')})\n"
                    f"⚠️ السببية: {impact.get('causality', 'غير مثبتة')}\n"
                    f"💙 هذا تنبيه استخباراتي ولا يغيّر استراتيجية SuperTrend/VPT."
                )
                if asset in open_trades:
                    msg += "\n🔎 توجد صفقة افتراضية مفتوحة على هذا الزوج؛ يجب مراقبتها فقط، دون تعديل آلي للاستراتيجية."
                if callable(notify_callback):
                    notify_callback(msg, impact)
        except Exception as exc:
            logging.warning(f"⚠️ Tona Forex Radar cycle failed: {exc}")

    def start_breaking_news_radar(self, notify_callback=None, open_trades_provider=None, interval_seconds=1800):
        """بدء عامل واحد فقط للرادار؛ لا يعمل كل 60 ثانية."""
        if self._radar_thread and self._radar_thread.is_alive():
            return self._radar_thread
        interval_seconds = max(300, int(interval_seconds or 1800))
        self._radar_stop.clear()

        def worker():
            logging.info(f"🚨 Tona Forex Breaking Radar بدأ (كل {interval_seconds // 60} دقيقة)")
            while not self._radar_stop.is_set():
                self._radar_once(notify_callback, open_trades_provider)
                self._radar_stop.wait(interval_seconds)
            logging.info("🛑 Tona Forex Breaking Radar توقف")

        self._radar_thread = threading.Thread(target=worker, name="TonaForexBreakingRadar", daemon=True)
        self._radar_thread.start()
        return self._radar_thread

    def stop_breaking_news_radar(self):
        self._radar_stop.set()


def get_engine() -> TonaEliteEngine:
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = TonaEliteEngine()
    return _ENGINE_INSTANCE


def generate_intelligence_report():
    try:
        return get_engine().generate_elite_analysis()
    except Exception as exc:
        logging.error(f"❌ فشل في generate_intelligence_report: {exc}")
        return "⚠️ حدث خطأ أثناء توليد التقرير الاستخباراتي."


def get_active_news(asset_type: str = None) -> List[Dict]:
    try:
        return get_engine().get_active_news(asset_type)
    except Exception as exc:
        logging.error(f"❌ فشل في get_active_news: {exc}")
        return []


def get_strongest_news(asset_type: str = None) -> Optional[Dict]:
    try:
        return get_engine().get_strongest_news(asset_type)
    except Exception as exc:
        logging.error(f"❌ فشل في get_strongest_news: {exc}")
        return None
