import os
import json
import time
import requests

# =====================================================================
# 🗂️ GitHub Gist Storage — قرص سحابي مجاني
# =====================================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GIST_BASE_URL = "https://api.github.com/gists"

# IDs من الخطوة 3
GIST_IDS = {
    "trades_oil": os.getenv("GIST_TRADES_OIL", ""),
    "trades_silver": os.getenv("GIST_TRADES_SILVER", ""),
    "config": os.getenv("GIST_CONFIG", ""),
}

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

def _get_gist(gist_id):
    """جلب محتوى Gist"""
    if not gist_id or not GITHUB_TOKEN:
        return None
    try:
        resp = requests.get(f"{GIST_BASE_URL}/{gist_id}", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 403:
            # Rate limit — انتظر
            reset_time = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(0, reset_time - int(time.time()))
            time.sleep(wait + 1)
            return _get_gist(gist_id)
        else:
            return None
    except:
        return None

def _update_gist(gist_id, filename, content):
    """تحديث ملف داخل Gist"""
    if not gist_id or not GITHUB_TOKEN:
        return False
    try:
        payload = {
            "files": {
                filename: {
                    "content": json.dumps(content, indent=2, ensure_ascii=False)
                }
            }
        }
        resp = requests.patch(f"{GIST_BASE_URL}/{gist_id}", headers=HEADERS, json=payload, timeout=10)
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

# =====================================================================
# دوال بسيطة للبوت
# =====================================================================

def load_json_from_gist(key, default=None):
    """جلب JSON من Gist"""
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
    """حفظ JSON في Gist"""
    gist_id = GIST_IDS.get(key)
    if not gist_id:
        return False
    gist = _get_gist(gist_id)
    if not gist:
        return False
    filename = list(gist.get("files", {}).keys())[0]
    return _update_gist(gist_id, filename, data)

# --- بدائل دوال البوت الموجودة ---

def load_trades_history_cloud(asset_type):
    key = f"trades_{asset_type}"
    data = load_json_from_gist(key, {"trades": [], "last_cleanup": None})
    if data.get("last_cleanup") is None:
        from datetime import datetime
        data["last_cleanup"] = datetime.now().isoformat()
    return data

def save_trades_history_cloud(asset_type, history):
    key = f"trades_{asset_type}"
    from datetime import datetime
    history["last_cleanup"] = datetime.now().isoformat()
    return save_json_to_gist(key, history)

def load_config_cloud():
    key = "config"
    default = {
        "strategies": {
            "oil": {"st_multiplier": 2.5, "vpt_ema_length": 10, "use_rsi_filter": False, "use_macd_filter": False, "rsi_min": 35, "rsi_max": 65},
            "silver": {"st_multiplier": 1.5, "vpt_ema_length": 10, "use_rsi_filter": True, "use_macd_filter": True, "rsi_min": 35, "rsi_max": 65}
        },
        "system": {"bot_name": "تولين", "developer": "بسام الحوباني", "version": "V11.1"}
    }
    return load_json_from_gist(key, default)

def test_connection():
    """اختبار الاتصال"""
    print("🔍 اختبار الاتصال بـ GitHub Gist...")
    for key, gid in GIST_IDS.items():
        if gid:
            data = load_json_from_gist(key)
            print(f"✅ {key}: نجح ({len(str(data))} حرف)")
        else:
            print(f"⚠️ {key}: لا يوجد ID")
