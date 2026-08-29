"""Forex Learning Database
========================
قاعدة تعلم محلية مستقلة لـ EUR/USD وUSD/JPY.
تخزن الصفقات واللقطات والأنماط والدروس مع عزل واضح بين الزوجين.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

logger = logging.getLogger("TonaPrometheus")
_SQLITE_LOCK = threading.RLock()

SUPPORTED_INSTRUMENTS = {
    "eurusd": {"symbol": "EURUSD", "display": "EUR/USD", "pip_size": 0.0001},
    "usdjpy": {"symbol": "USDJPY", "display": "USD/JPY", "pip_size": 0.01},
}


def normalize_instrument(value: Any = "eurusd") -> str:
    key = str(value or "eurusd").strip().lower().replace("/", "")
    key = {"eur_usd": "eurusd", "eurusd=x": "eurusd", "usd_jpy": "usdjpy", "jpy=x": "usdjpy"}.get(key, key)
    if key not in SUPPORTED_INSTRUMENTS:
        raise ValueError(f"Unsupported Forex instrument: {value}")
    return key


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    try:
        return json.dumps(value if value is not None else {}, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "{}"


class LearningDatabase:
    """تخزين تعلم متزامن وآمن نسبيًا لبيئة المحاكاة المحلية."""

    def __init__(self, db_path: str = "learning_data/deep_learning.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info("Forex LearningDatabase initialized at %s", self.db_path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        with _SQLITE_LOCK:
            conn = sqlite3.connect(self.db_path, timeout=15.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout = 15000")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS trades_full (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL UNIQUE,
                instrument TEXT NOT NULL CHECK (instrument IN ('eurusd','usdjpy')),
                asset_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL CHECK (trade_type IN ('BUY','SELL')),
                entry_price REAL NOT NULL,
                exit_price REAL,
                profit_dollars REAL DEFAULT 0,
                profit_pct REAL DEFAULT 0,
                profit_after_cost REAL,
                trading_cost REAL DEFAULT 0,
                exit_reason TEXT,
                entry_time TEXT,
                exit_time TEXT,
                duration_minutes INTEGER,
                max_profit REAL,
                max_loss REAL,
                max_drawdown REAL,
                recovery_time INTEGER,
                entry_rsi REAL,
                entry_adx REAL,
                entry_macd REAL,
                entry_trend TEXT,
                session TEXT,
                timeframe TEXT,
                provider TEXT,
                spread_pips REAL,
                slippage_pips REAL,
                pip_size REAL,
                stop_distance_pips REAL,
                target_distance_pips REAL,
                margin_used REAL,
                notional_value REAL,
                effective_leverage REAL,
                risk_amount REAL,
                sl_price REAL,
                tp_price REAL,
                context_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                instrument TEXT NOT NULL CHECK (instrument IN ('eurusd','usdjpy')),
                timestamp TEXT NOT NULL,
                price REAL,
                bid REAL,
                ask REAL,
                spread_pips REAL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                rsi REAL,
                adx REAL,
                macd REAL,
                st_trend TEXT,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                vwap REAL,
                volume_ratio REAL,
                profit_dollars REAL,
                profit_pct REAL,
                warning_level INTEGER,
                market_regime TEXT,
                session TEXT,
                indicators_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS discovered_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT NOT NULL CHECK (instrument IN ('eurusd','usdjpy')),
                pattern_name TEXT NOT NULL,
                pattern_type TEXT,
                description TEXT,
                conditions TEXT NOT NULL DEFAULT '{}',
                win_rate REAL DEFAULT 0,
                sample_count INTEGER DEFAULT 0,
                avg_profit REAL DEFAULT 0,
                confidence REAL DEFAULT 0,
                session TEXT,
                regime TEXT,
                last_updated TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                UNIQUE(instrument, pattern_name)
            );
            CREATE TABLE IF NOT EXISTS lessons_deep (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instrument TEXT,
                lesson_type TEXT,
                lesson_text TEXT NOT NULL,
                recommendation TEXT,
                importance REAL DEFAULT 0.5,
                evidence_count INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                applied_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0,
                context_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_trades_instrument_time ON trades_full(instrument, entry_time DESC);
            CREATE INDEX IF NOT EXISTS idx_snapshots_trade_time ON monitoring_snapshots(trade_id, timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_patterns_instrument_active ON discovered_patterns(instrument, is_active);
            CREATE INDEX IF NOT EXISTS idx_lessons_instrument ON lessons_deep(instrument, created_at DESC);
            """)

    def save_trade_full(self, trade_data: Dict[str, Any]) -> bool:
        try:
            instrument = normalize_instrument(trade_data.get("instrument", trade_data.get("asset_type", "eurusd")))
            trade_type = str(trade_data.get("trade_type", trade_data.get("type", "BUY"))).upper()
            if trade_type not in ("BUY", "SELL"):
                raise ValueError("trade_type must be BUY or SELL")
            trade_id = str(trade_data.get("trade_id") or f"{instrument}-{int(datetime.now().timestamp() * 1000)}")
            spec = SUPPORTED_INSTRUMENTS[instrument]
            values = (
                trade_id, instrument, instrument, spec["symbol"], trade_type,
                trade_data.get("entry_price", 0), trade_data.get("exit_price"), trade_data.get("profit_dollars", 0),
                trade_data.get("profit_pct", 0), trade_data.get("profit_after_cost", trade_data.get("profit_dollars", 0)),
                trade_data.get("trading_cost", 0), trade_data.get("exit_reason"), trade_data.get("entry_time"), trade_data.get("exit_time"),
                trade_data.get("duration_minutes"), trade_data.get("max_profit"), trade_data.get("max_loss"), trade_data.get("max_drawdown"),
                trade_data.get("recovery_time"), trade_data.get("entry_rsi"), trade_data.get("entry_adx"), trade_data.get("entry_macd"),
                trade_data.get("entry_trend"), trade_data.get("session"), trade_data.get("timeframe"), trade_data.get("provider"),
                trade_data.get("spread_pips", 0), trade_data.get("slippage_pips", 0), trade_data.get("pip_size", spec["pip_size"]),
                trade_data.get("stop_distance_pips"), trade_data.get("target_distance_pips"), trade_data.get("margin_used"),
                trade_data.get("notional_value"), trade_data.get("effective_leverage"), trade_data.get("risk_amount"),
                trade_data.get("sl_price"), trade_data.get("tp_price"), _json(trade_data.get("context", trade_data.get("indicators", {}))), _now(),
            )
            columns = """trade_id,instrument,asset_type,symbol,trade_type,entry_price,exit_price,profit_dollars,profit_pct,
                profit_after_cost,trading_cost,exit_reason,entry_time,exit_time,duration_minutes,max_profit,max_loss,
                max_drawdown,recovery_time,entry_rsi,entry_adx,entry_macd,entry_trend,session,timeframe,provider,
                spread_pips,slippage_pips,pip_size,stop_distance_pips,target_distance_pips,margin_used,notional_value,
                effective_leverage,risk_amount,sl_price,tp_price,context_json,created_at"""
            placeholders = ",".join("?" for _ in values)
            with self._connect() as conn:
                conn.execute(f"""INSERT INTO trades_full ({columns}) VALUES ({placeholders})
                ON CONFLICT(trade_id) DO UPDATE SET
                    exit_price=excluded.exit_price, profit_dollars=excluded.profit_dollars, profit_pct=excluded.profit_pct,
                    profit_after_cost=excluded.profit_after_cost, trading_cost=excluded.trading_cost, exit_reason=excluded.exit_reason,
                    exit_time=excluded.exit_time, duration_minutes=excluded.duration_minutes, max_profit=excluded.max_profit,
                    max_loss=excluded.max_loss, max_drawdown=excluded.max_drawdown, context_json=excluded.context_json""", values)
            return True
        except Exception as exc:
            logger.exception("Failed to save Forex trade: %s", exc)
            return False

    def save_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        try:
            instrument = normalize_instrument(snapshot_data.get("instrument", snapshot_data.get("asset_type", "eurusd")))
            with self._connect() as conn:
                conn.execute("""INSERT INTO monitoring_snapshots (
                    trade_id,instrument,timestamp,price,bid,ask,spread_pips,open_price,high_price,low_price,rsi,adx,macd,
                    st_trend,bb_upper,bb_middle,bb_lower,vwap,volume_ratio,profit_dollars,profit_pct,warning_level,
                    market_regime,session,indicators_json,created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    str(snapshot_data.get("trade_id", "")), instrument, snapshot_data.get("timestamp", _now()),
                    snapshot_data.get("price"), snapshot_data.get("bid"), snapshot_data.get("ask"), snapshot_data.get("spread_pips"),
                    snapshot_data.get("open_price"), snapshot_data.get("high_price"), snapshot_data.get("low_price"), snapshot_data.get("rsi"),
                    snapshot_data.get("adx"), snapshot_data.get("macd"), snapshot_data.get("st_trend"), snapshot_data.get("bb_upper"),
                    snapshot_data.get("bb_middle"), snapshot_data.get("bb_lower"), snapshot_data.get("vwap"), snapshot_data.get("volume_ratio"),
                    snapshot_data.get("profit_dollars"), snapshot_data.get("profit_pct"), snapshot_data.get("warning_level"),
                    snapshot_data.get("market_regime"), snapshot_data.get("session"), _json(snapshot_data.get("indicators", {})), _now(),
                ))
            return True
        except Exception as exc:
            logger.exception("Failed to save snapshot: %s", exc)
            return False

    def get_trades_by_asset(self, asset_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            instrument = normalize_instrument(asset_type)
            limit = max(1, min(int(limit), 5000))
            with self._connect() as conn:
                rows = conn.execute("SELECT * FROM trades_full WHERE instrument = ? ORDER BY COALESCE(entry_time, created_at) DESC LIMIT ?", (instrument, limit)).fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            logger.exception("Failed to read trades: %s", exc)
            return []

    def get_statistics(self, asset_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            with self._connect() as conn:
                if asset_type is None:
                    row = conn.execute("""SELECT COUNT(*) total_trades, SUM(profit_dollars > 0) winning_trades,
                        SUM(profit_dollars < 0) losing_trades, AVG(COALESCE(profit_after_cost, profit_dollars)) avg_profit,
                        AVG(profit_pct) avg_profit_pct, MAX(profit_dollars) max_profit, MIN(profit_dollars) max_loss,
                        AVG(duration_minutes) avg_duration FROM trades_full""").fetchone()
                else:
                    instrument = normalize_instrument(asset_type)
                    row = conn.execute("""SELECT COUNT(*) total_trades, SUM(profit_dollars > 0) winning_trades,
                        SUM(profit_dollars < 0) losing_trades, AVG(COALESCE(profit_after_cost, profit_dollars)) avg_profit,
                        AVG(profit_pct) avg_profit_pct, MAX(profit_dollars) max_profit, MIN(profit_dollars) max_loss,
                        AVG(duration_minutes) avg_duration FROM trades_full WHERE instrument = ?""", (instrument,)).fetchone()
            total = int(row["total_trades"] or 0)
            winning = int(row["winning_trades"] or 0)
            return {"total_trades": total, "winning_trades": winning, "losing_trades": int(row["losing_trades"] or 0), "win_rate": winning / total * 100 if total else 0.0, "avg_profit": float(row["avg_profit"] or 0), "avg_profit_pct": float(row["avg_profit_pct"] or 0), "max_profit": float(row["max_profit"] or 0), "max_loss": float(row["max_loss"] or 0), "avg_duration": float(row["avg_duration"] or 0)}
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Failed to calculate statistics: %s", exc)
            return {}

    def save_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        try:
            instrument = normalize_instrument(pattern_data.get("instrument", pattern_data.get("asset_type", "eurusd")))
            with self._connect() as conn:
                conn.execute("""INSERT INTO discovered_patterns (instrument,pattern_name,pattern_type,description,conditions,win_rate,sample_count,avg_profit,confidence,session,regime,last_updated,is_active)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(instrument,pattern_name) DO UPDATE SET pattern_type=excluded.pattern_type,description=excluded.description,conditions=excluded.conditions,win_rate=excluded.win_rate,sample_count=excluded.sample_count,avg_profit=excluded.avg_profit,confidence=excluded.confidence,session=excluded.session,regime=excluded.regime,last_updated=excluded.last_updated,is_active=excluded.is_active""", (
                    instrument, str(pattern_data.get("pattern_name", "unnamed")), pattern_data.get("pattern_type"), pattern_data.get("description"), _json(pattern_data.get("conditions", {})), pattern_data.get("win_rate", 0), pattern_data.get("sample_count", 0), pattern_data.get("avg_profit", 0), pattern_data.get("confidence", 0), pattern_data.get("session"), pattern_data.get("regime"), _now(), 1 if pattern_data.get("is_active", True) else 0))
            return True
        except Exception as exc:
            logger.exception("Failed to save pattern: %s", exc)
            return False

    def save_lesson(self, lesson_data: Dict[str, Any]) -> bool:
        try:
            instrument = normalize_instrument(lesson_data["instrument"]) if lesson_data.get("instrument") else None
            with self._connect() as conn:
                conn.execute("""INSERT INTO lessons_deep (instrument,lesson_type,lesson_text,recommendation,importance,evidence_count,created_at,success_rate,context_json) VALUES (?,?,?,?,?,?,?,?,?)""", (
                    instrument, lesson_data.get("lesson_type"), str(lesson_data.get("lesson_text", "")), lesson_data.get("recommendation"), lesson_data.get("importance", 0.5), lesson_data.get("evidence_count", 1), _now(), lesson_data.get("success_rate", 0), _json(lesson_data.get("context", {}))))
            return True
        except Exception as exc:
            logger.exception("Failed to save lesson: %s", exc)
            return False

    def get_learning_report(self, asset_type: Optional[str] = None) -> str:
        stats = self.get_statistics(asset_type)
        label = SUPPORTED_INSTRUMENTS[normalize_instrument(asset_type)]["display"] if asset_type else "EUR/USD وUSD/JPY"
        return "\n".join([
            "🧠 **تقرير تعلم Forex**", "━" * 30, f"📊 الأزواج: {label}",
            f"📈 إجمالي الصفقات: {stats.get('total_trades', 0)}", f"✅ الرابحة: {stats.get('winning_trades', 0)}",
            f"❌ الخاسرة: {stats.get('losing_trades', 0)}", f"📊 نسبة النجاح: {stats.get('win_rate', 0):.1f}%",
            f"💰 متوسط صافي النتيجة: ${stats.get('avg_profit', 0):.4f}", f"📈 أكبر ربح: ${stats.get('max_profit', 0):.4f}",
            f"📉 أكبر خسارة: ${stats.get('max_loss', 0):.4f}", f"⏱️ متوسط المدة: {stats.get('avg_duration', 0):.0f} دقيقة",
        ])

    def get_patterns(self, instrument: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        try:
            clauses, params = [], []
            if instrument:
                clauses.append("instrument = ?"); params.append(normalize_instrument(instrument))
            if active_only:
                clauses.append("is_active = 1")
            where = " WHERE " + " AND ".join(clauses) if clauses else ""
            with self._connect() as conn:
                rows = conn.execute("SELECT * FROM discovered_patterns" + where + " ORDER BY confidence DESC, sample_count DESC", params).fetchall()
            return [dict(row) for row in rows]
        except Exception as exc:
            logger.exception("Failed to read patterns: %s", exc)
            return []

    def close(self) -> None:
        """الاتصالات قصيرة العمر؛ الدالة موجودة للتوافق."""
        return None
