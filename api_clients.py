# -*- coding: utf-8 -*-
"""
API_CLIENTS.PY - دوال الاتصال بالـ APIs الخارجية
"""

import os
import time
import json
import requests
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

from constants import (
    logger, GITHUB_TOKEN, GIST_BASE_URL, GIST_IDS, GIST_HEADERS,
    FEAR_GREED_CACHE, FEAR_GREED_CACHE_TTL,
    TELEGRAM_TOKEN
)
from utils import queue_telegram_message


# ====================================================================
# GitHub Gist
# ====================================================================

def _get_gist(gist_id):
    if not gist_id or not GITHUB_TOKEN:
        return None
    try:
        resp = requests.get(f"{GIST_BASE_URL}/{gist_id}", headers=GIST_HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 403:
            reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(0, reset_time - int(time.time()))
            time.sleep(wait + 1)
            return _get_gist(gist_id)
        return None
    except:
        return None

def _update_gist(gist_id, filename, content):
    if not gist_id or not GITHUB_TOKEN:
        return False
    try:
        payload = {"files": {filename: {"content": json.dumps(content, indent=2, ensure_ascii=False)}}}
        resp = requests.patch(f"{GIST_BASE_URL}/{gist_id}", headers=GIST_HEADERS, json=payload, timeout=10)
        if resp.status_code == 200:
            return True
        elif resp.status_code == 403:
            reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(0, reset_time - int(time.time()))
            time.sleep(wait + 1)
            return _update_gist(gist_id, filename, content)
        return False
    except:
        return False

def load_json_from_gist(key, default=None):
    if default is None:
        default = {}
    gist_id = GIST_IDS.get(key)
    if not gist_id:
        return default
    gist = _get_gist(gist_id)
    if not gist:
        return default
    files = gist.get("files", {})
    if not files:
        return default
    filename = list(files.keys())[0]
    content = files[filename].get("content", "{}")
    try:
        return json.loads(content)
    except:
        return default

def save_json_to_gist(key, data):
    gist_id = GIST_IDS.get(key)
    if not gist_id:
        try:
            local_file = f"{key}_backup.json"
            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ تم حفظ {key} محلياً (Gist غير متوفر)")
        except:
            pass
        return False
    gist = _get_gist(gist_id)
    if not gist:
        return False
    filename = list(gist.get("files", {}).keys())[0]
    return _update_gist(gist_id, filename, data)


# ====================================================================
# MEXC API
# ====================================================================

def get_mexc_candles(symbol, interval="Min15", limit=1000):
    url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval={interval}&limit={limit}"
    try:
        response = requests.get(url, headers={"User-Agent": "TonaPrometheus/13.0"}, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                raw = data['data']
                closes = raw.get('close', [])
                if closes and len(closes) >= 5:
                    return {
                        "closes": [float(x) for x in closes],
                        "highs": [float(x) for x in raw.get('high', [])],
                        "lows": [float(x) for x in raw.get('low', [])],
                        "opens": [float(x) for x in raw.get('open', [])],
                        "volumes": [float(x) for x in raw.get('vol', [])]
                    }
        return None
    except:
        return None

def fetch_multiple_timeframes(symbol, timeframes):
    results = {}
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(get_mexc_candles, symbol, tf["interval"], tf["limit"]): name for name, tf in timeframes.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except:
                results[name] = None
    return results


# ====================================================================
# Fear & Greed Index
# ====================================================================

def get_fear_greed_index(force_refresh=False):
    global FEAR_GREED_CACHE
    now = time.time()
    
    if not force_refresh and (now - FEAR_GREED_CACHE["timestamp"] < FEAR_GREED_CACHE_TTL):
        return FEAR_GREED_CACHE["value"]
    
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        data = response.json()
        if data.get('data'):
            val = int(data['data'][0].get('value', '50'))
            if val > 75:
                result = f"طمع شديد 🔥 ({val}/100)"
            elif val > 55:
                result = f"تفاؤل وطمع 📈 ({val}/100)"
            elif val > 45:
                result = f"محايد ومتزن ⚖️ ({val}/100)"
            elif val > 25:
                result = f"خوف وقلق ⚠️ ({val}/100)"
            else:
                result = f"خوف شديد وهلع 🚨 ({val}/100)"
            
            FEAR_GREED_CACHE["value"] = result
            FEAR_GREED_CACHE["timestamp"] = now
            return result
    except:
        pass
    
    return "محايد ومتزن ⚖️ (50/100)"


# ====================================================================
# Telegram Webhook (مطورة مع طباعة تفصيلية وإعادة محاولة ضمنية)
# ====================================================================

def set_webhook():
    """تسجيل Webhook في Telegram مع طباعة تفصيلية"""
    if not TELEGRAM_TOKEN:
        print("❌ set_webhook: TELEGRAM_TOKEN غير موجود")
        return False

    render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    if not render_url:
        service_name = os.environ.get('RENDER_SERVICE_NAME', '')
        render_url = f"https://{service_name}.onrender.com" if service_name else os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
        if render_url:
            render_url = f"https://{render_url}"

    if not render_url:
        print("❌ set_webhook: لا يمكن تحديد رابط Render")
        print("   - تحقق من متغيرات البيئة: RENDER_EXTERNAL_URL أو RENDER_SERVICE_NAME")
        return False

    webhook_url = f"{render_url}/webhook"
    print(f"🔗 set_webhook: محاولة تسجيل Webhook إلى: {webhook_url}")

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        response = requests.post(url, json={"url": webhook_url, "allowed_updates": ["message"]}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ set_webhook: تم التسجيل بنجاح إلى {webhook_url}")
                return True
            else:
                print(f"❌ set_webhook: فشل التسجيل - {data}")
                return False
        else:
            print(f"❌ set_webhook: خطأ HTTP {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ set_webhook: استثناء - {e}")
        return False

def remove_webhook():
    if not TELEGRAM_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
        response = requests.get(url, timeout=5)
        print(f"🗑️ Webhook removed: {response.json()}")
    except Exception as e:
        print(f"❌ خطأ في إزالة Webhook: {e}")


# ====================================================================
# Supabase (قاعدة البيانات السحابية)
# ====================================================================

SUPABASE_AVAILABLE = False
SUPABASE_DB = None
DEEP_LEARNING_AVAILABLE = False
DEEP_LEARNING_DB = None
PATTERN_DISCOVERY_AVAILABLE = False
PATTERN_DISCOVERY = None

def _get_supabase_client():
    global SUPABASE_DB, SUPABASE_AVAILABLE
    if not SUPABASE_AVAILABLE or not SUPABASE_DB:
        return None
    if hasattr(SUPABASE_DB, 'client') and SUPABASE_DB.client:
        return SUPABASE_DB.client
    if hasattr(SUPABASE_DB, 'supabase') and SUPABASE_DB.supabase:
        return SUPABASE_DB.supabase
    if hasattr(SUPABASE_DB, '_client') and SUPABASE_DB._client:
        return SUPABASE_DB._client
    if hasattr(SUPABASE_DB, 'table'):
        return SUPABASE_DB
    return None

def _ensure_supabase_connected():
    global SUPABASE_DB, SUPABASE_AVAILABLE
    if not SUPABASE_AVAILABLE or not SUPABASE_DB:
        return False
    if hasattr(SUPABASE_DB, 'connected') and not SUPABASE_DB.connected:
        try:
            SUPABASE_DB.connect()
            logger.info("🔄 تم إعادة الاتصال بـ Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ فشل إعادة الاتصال بـ Supabase: {e}")
            return False
    return True

TRADES_FULL_BASE_FIELDS = [
    'trade_id', 'asset_type', 'trade_type', 'entry_price', 'exit_price',
    'profit_dollars', 'profit_pct', 'exit_reason', 'entry_time', 'exit_time',
    'duration_minutes', 'sl_price', 'tp_price', 'rr', 'confidence'
]

TRADES_FULL_EXTRA_FIELDS = [
    'entry_rsi', 'entry_adx', 'entry_macd', 'entry_trend',
    'entry_volume_ratio', 'entry_vwap', 'entry_bb_upper', 'entry_bb_lower',
    'entry_support', 'entry_resistance', 'entry_comprehensive_score', 'entry_comprehensive_grade',
    'close_rsi', 'close_adx', 'close_macd', 'close_trend',
    'close_volume_ratio', 'close_vwap', 'close_bb_upper', 'close_bb_lower',
    'close_support', 'close_resistance', 'close_comprehensive_score', 'close_comprehensive_grade'
]

TRADES_FULL_JSON_FIELDS = [
    'full_entry_analysis',
    'full_exit_analysis'
]

SNAPSHOTS_BASE_FIELDS = [
    'trade_id', 'asset_type', 'timestamp', 'price', 'rsi', 'adx', 'macd',
    'st_trend', 'volume_ratio', 'profit_dollars', 'profit_pct',
    'warning_level', 'fear_greed_index', 'market_regime',
    'bb_upper', 'bb_middle', 'bb_lower', 'vwap', 'support', 'resistance', 'trend'
]

def save_trade_to_learning(trade_data: Dict) -> bool:
    global SUPABASE_AVAILABLE, SUPABASE_DB, DEEP_LEARNING_AVAILABLE, DEEP_LEARNING_DB
    success = False
    trade_id = trade_data.get('trade_id', 'unknown')
    logger.info(f"📤 [save_trade_to_learning] بدء حفظ الصفقة {trade_id}")

    if not SUPABASE_AVAILABLE or not SUPABASE_DB:
        logger.warning("⚠️ [save_trade_to_learning] Supabase غير متوفر، تخطي")
    else:
        try:
            if not _ensure_supabase_connected():
                logger.warning("⚠️ [save_trade_to_learning] Supabase غير متصل، تخطي")
            else:
                client = _get_supabase_client()
                if not client:
                    logger.error("❌ [save_trade_to_learning] لا يمكن الحصول على عميل Supabase")
                else:
                    insert_data = {}
                    default_values = {
                        'trade_id': trade_id,
                        'asset_type': trade_data.get('asset_type', 'unknown'),
                        'trade_type': trade_data.get('trade_type', 'BUY'),
                        'entry_price': trade_data.get('entry_price', 0.0),
                        'exit_price': trade_data.get('exit_price', 0.0),
                        'profit_dollars': trade_data.get('profit_dollars', 0.0),
                        'profit_pct': trade_data.get('profit_pct', 0.0),
                        'exit_reason': trade_data.get('exit_reason', ''),
                        'entry_time': trade_data.get('entry_time', datetime.now().isoformat()),
                        'exit_time': trade_data.get('exit_time', None),
                        'duration_minutes': trade_data.get('duration_minutes', 0),
                        'sl_price': trade_data.get('sl_price', 0.0),
                        'tp_price': trade_data.get('tp_price', 0.0),
                        'rr': trade_data.get('rr', 1.0),
                        'confidence': trade_data.get('confidence', 70),
                    }
                    for key in default_values:
                        if key in trade_data and trade_data[key] is not None:
                            insert_data[key] = trade_data[key]
                        else:
                            insert_data[key] = default_values[key]
                    for field in TRADES_FULL_EXTRA_FIELDS:
                        if field in trade_data and trade_data[field] is not None:
                            insert_data[field] = trade_data[field]
                    for json_field in TRADES_FULL_JSON_FIELDS:
                        if json_field in trade_data and trade_data[json_field] is not None:
                            try:
                                if isinstance(trade_data[json_field], (dict, list)):
                                    insert_data[json_field] = json.dumps(trade_data[json_field], ensure_ascii=False, default=str)
                                else:
                                    insert_data[json_field] = str(trade_data[json_field])
                            except Exception as json_err:
                                logger.warning(f"⚠️ [save_trade_to_learning] فشل تحويل {json_field} إلى JSON: {json_err}")
                                insert_data[json_field] = str(trade_data[json_field])
                    logger.info(f"📤 [save_trade_to_learning] محاولة إدراج في trades_full مع {len(insert_data)} حقلاً")
                    try:
                        response = client.table('trades_full').insert(insert_data).execute()
                        if response and hasattr(response, 'data'):
                            logger.info(f"✅ [save_trade_to_learning] تم حفظ الصفقة في Supabase (trades_full) - trade_id: {trade_id}")
                            success = True
                        else:
                            logger.error(f"❌ [save_trade_to_learning] فشل الإدراج: {response}")
                            minimal_data = {
                                'trade_id': trade_id,
                                'asset_type': trade_data.get('asset_type', 'unknown'),
                                'trade_type': trade_data.get('trade_type', 'BUY'),
                                'entry_price': trade_data.get('entry_price', 0),
                                'entry_time': trade_data.get('entry_time', datetime.now().isoformat())
                            }
                            try:
                                response2 = client.table('trades_full').insert(minimal_data).execute()
                                if response2 and hasattr(response2, 'data'):
                                    logger.info(f"✅ [save_trade_to_learning] تم حفظ الصفقة (تبسيط) في Supabase - trade_id: {trade_id}")
                                    success = True
                            except Exception as e3:
                                logger.error(f"❌ [save_trade_to_learning] فشل الإدراج المبسط: {e3}")
                    except Exception as e1:
                        logger.error(f"❌ [save_trade_to_learning] استثناء أثناء الإدراج: {e1}")
        except Exception as e:
            logger.error(f"❌ [save_trade_to_learning] فشل حفظ في Supabase: {e}")

    if DEEP_LEARNING_AVAILABLE and DEEP_LEARNING_DB:
        try:
            DEEP_LEARNING_DB.save_trade_full(trade_data)
            success = True
            logger.info(f"💾 [save_trade_to_learning] تم حفظ الصفقة في SQLite - trade_id: {trade_id}")
        except Exception as e:
            logger.error(f"❌ [save_trade_to_learning] فشل حفظ في SQLite: {e}")

    if not success:
        try:
            backup_file = "learning_data/backup_trades.json"
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            existing = []
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = []
            existing.append(trade_data)
            if len(existing) > 100:
                existing = existing[-100:]
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            success = True
            logger.info(f"💾 [save_trade_to_learning] تم حفظ الصفقة في النسخة الاحتياطية - trade_id: {trade_id}")
        except Exception as e:
            logger.error(f"❌ [save_trade_to_learning] فشل حفظ النسخة الاحتياطية: {e}")

    logger.info(f"📤 [save_trade_to_learning] انتهى حفظ الصفقة {trade_id} - النتيجة: {'نجاح' if success else 'فشل'}")
    return success

def save_snapshot_to_learning(snapshot_data: Dict) -> bool:
    global SUPABASE_AVAILABLE, SUPABASE_DB, DEEP_LEARNING_AVAILABLE, DEEP_LEARNING_DB
    success = False
    if SUPABASE_AVAILABLE and SUPABASE_DB:
        try:
            if not _ensure_supabase_connected():
                logger.warning("⚠️ Supabase غير متصل، تخطي حفظ اللقطة")
            else:
                client = _get_supabase_client()
                if not client:
                    logger.error("❌ لا يمكن الحصول على عميل Supabase")
                else:
                    filtered_data = {k: v for k, v in snapshot_data.items() if k in SNAPSHOTS_BASE_FIELDS}
                    if 'trade_id' not in filtered_data or 'timestamp' not in filtered_data:
                        logger.error("❌ بيانات اللقطة تفتقد trade_id أو timestamp")
                    else:
                        response = client.table('snapshots').insert(filtered_data).execute()
                        if response and hasattr(response, 'data'):
                            success = True
                            logger.info("💾 تم حفظ اللقطة في Supabase (snapshots)")
                        else:
                            logger.error(f"❌ فشل حفظ اللقطة في Supabase: {response}")
        except Exception as e:
            logger.error(f"❌ فشل حفظ اللقطة في Supabase: {e}")
    if DEEP_LEARNING_AVAILABLE and DEEP_LEARNING_DB:
        try:
            DEEP_LEARNING_DB.save_snapshot(snapshot_data)
            success = True
        except Exception as e:
            logger.error(f"❌ فشل حفظ اللقطة في قاعدة التعلم: {e}")
    if not success:
        try:
            backup_file = "learning_data/backup_snapshots.json"
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            existing = []
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = []
            existing.append(snapshot_data)
            if len(existing) > 50:
                existing = existing[-50:]
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            success = True
        except Exception as e:
            logger.error(f"❌ فشل حفظ نسخة اللقطات الاحتياطية: {e}")
    return success
