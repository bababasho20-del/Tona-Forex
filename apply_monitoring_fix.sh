#!/bin/bash

# =====================================================================
# 🛠️ تطبيق نظام المراقبة الذكي المتدرج
# =====================================================================

echo "🔧 بدء تطبيق نظام المراقبة الذكي..."

# ============================================================
# 1. عمل نسخة احتياطية إضافية لـ main.py
# ============================================================
echo "📁 عمل نسخة احتياطية لـ main.py..."
cp main.py main.py.monitoring_backup

# ============================================================
# 2. حذف دالة check_and_monitor_positions القديمة
# ============================================================
echo "🗑️ حذف دالة المراقبة القديمة..."

# حذف من بداية الدالة إلى نهايتها (نستخدم awk بدلاً من sed للتعامل مع الأقواس)
awk '
  /^def check_and_monitor_positions/ { skip=1 }
  !skip { print }
  /^def handle_check_position_request/ { skip=0; print }
' main.py > main.py.tmp && mv main.py.tmp main.py

# ============================================================
# 3. إضافة الدوال الجديدة
# ============================================================
echo "📝 إضافة دوال المراقبة الذكية الجديدة..."

cat >> main.py << 'EOF'

# =====================================================================
# 🛡️ 6. نظام المراقبة الذكية والمتدرجة (معدل بالكامل)
# =====================================================================
def check_and_monitor_positions(asset_type, current_price, st_line, current_trend):
    """
    نظام مراقبة ذكي للصفقات المفتوحة يستخدم مؤشرات متعددة:
    - المسافة عن السوبر تريند
    - ADX (قوة الاتجاه)
    - Stochastic (مناطق التشبع)
    - حجم التداول (تأكيد الحركة)
    - اتجاه فريم الساعة (الدعم من الإطار الأعلى)
    """
    open_trade = get_current_open_trade(asset_type)
    if not open_trade:
        return

    entry_p, sl_p, tp_p = open_trade["entry_price"], open_trade["sl"], open_trade["tp"]
    trade_type = open_trade["type"]
    warning_sent = open_trade.get("warning_sent", False)
    strong_warning_sent = open_trade.get("strong_warning_sent", False)

    decimal_format = ".3f" if asset_type == "silver" else ".2f"
    asset_label = "النفط الخام (USOIL)" if asset_type == "oil" else "الفضة (XAG/USD)"
    symbol = "USOIL_USDT" if asset_type == "oil" else "SILVER_USDT"

    # ================================================================
    # 1. جلب البيانات والمؤشرات للمراقبة
    # ================================================================
    data_15m = get_mexc_candles(symbol, interval="Min15", limit=150)
    if not data_15m:
        logging.warning(f"No data for monitoring {asset_type}")
        return

    closes, highs, lows, volumes = data_15m["closes"], data_15m["highs"], data_15m["lows"], data_15m["volumes"]
    
    # المؤشرات الأساسية
    distance_pct = abs(current_price - st_line) / current_price * 100 if st_line != 0 else 0
    
    # ADX (قوة الاتجاه)
    adx = calculate_adx_14(data_15m)
    
    # Stochastic (مناطق التشبع)
    stoch_k = calculate_stochastic(highs, lows, closes)[-1] if len(closes) > 14 else 50
    
    # حجم التداول النسبي
    current_volume = volumes[-1] if volumes else 0
    avg_volume_20 = sum(volumes[-21:-1]) / 20 if len(volumes) > 20 else current_volume
    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
    
    # ================================================================
    # 2. فحص فريم الساعة (الدعم من الإطار الأعلى)
    # ================================================================
    data_1h = get_mexc_candles(symbol, interval="Min60", limit=50)
    hourly_trend = 0
    if data_1h:
        hourly_close = data_1h["closes"][-1]
        hourly_sma_20 = sum(data_1h["closes"][-20:]) / 20 if len(data_1h["closes"]) >= 20 else hourly_close
        hourly_trend = 1 if hourly_close > hourly_sma_20 else -1
    
    # ================================================================
    # 3. مؤشرات إضافية
    # ================================================================
    upper, basis, lower = calculate_bollinger_bands(closes)
    bb_position = "middle"
    if upper and lower:
        if current_price >= upper[-1] * 0.98:
            bb_position = "near_upper"
        elif current_price <= lower[-1] * 1.02:
            bb_position = "near_lower"
    
    rsi = calculate_rsi_7(closes)[-1] if len(closes) > 7 else 50

    # ================================================================
    # 4. تقييم حالة الانعكاس
    # ================================================================
    trend_reversed = False
    if trade_type == "BUY" and current_trend == -1:
        trend_reversed = True
    elif trade_type == "SELL" and current_trend == 1:
        trend_reversed = True

    # ================================================================
    # 5. تصنيف مستوى التحذير
    # ================================================================
    warning_level = "NONE"
    warning_reasons = []

    # 🔴 تحذير قوي
    if trend_reversed and distance_pct > 0.5 and adx > 25 and volume_ratio > 1.2:
        if hourly_trend == current_trend or hourly_trend == 0:
            warning_level = "STRONG"
            warning_reasons = [
                f"✅ اختراق قوي للسوبر تريند ({distance_pct:.2f}%)",
                f"✅ ADX مرتفع ({adx:.1f})",
                f"✅ فوليوم مرتفع ({volume_ratio:.1f}x)",
                f"✅ فريم الساعة يدعم الانعكاس" if hourly_trend == current_trend else ""
            ]

    # 🟡 تحذير متوسط
    elif trend_reversed and distance_pct > 0.3:
        if adx > 20 or stoch_k > 80 or stoch_k < 20 or volume_ratio > 1.0:
            warning_level = "MEDIUM"
            warning_reasons = [
                f"⚠️ اختراق ({distance_pct:.2f}%)",
                f"⚠️ ADX {adx:.1f}",
                f"⚠️ Stochastic {'تشبع' if stoch_k > 80 or stoch_k < 20 else 'طبيعي'}",
                f"⚠️ فوليوم {volume_ratio:.1f}x"
            ]

    # 🟢 تحذير بسيط
    elif distance_pct > 0.15 and not warning_sent:
        if not trend_reversed:
            warning_level = "LIGHT"
            warning_reasons = [
                f"🔍 اقتراب من السوبر تريند ({distance_pct:.2f}%)",
                f"🔍 ADX {adx:.1f}",
                f"🔍 السعر عند {bb_position}"
            ]

    # ================================================================
    # 6. إرسال التحذير المناسب
    # ================================================================
    if warning_level == "STRONG" and not strong_warning_sent:
        _send_strong_warning(asset_type, current_price, trade_type, entry_p, 
                           distance_pct, adx, volume_ratio, hourly_trend, 
                           asset_label, decimal_format, warning_reasons)
        mark_strong_warning_sent(asset_type)
        return

    elif warning_level == "MEDIUM" and not warning_sent:
        _send_medium_warning(asset_type, current_price, trade_type, entry_p,
                           distance_pct, adx, stoch_k, volume_ratio,
                           asset_label, decimal_format, warning_reasons)
        mark_warning_sent(asset_type)
        return

    elif warning_level == "LIGHT" and not warning_sent:
        _send_light_warning(asset_type, current_price, trade_type,
                          distance_pct, adx, bb_position,
                          asset_label, decimal_format, warning_reasons)
        mark_warning_sent(asset_type)
        return

# =====================================================================
# 📨 دوال إرسال التحذيرات المتدرجة
# =====================================================================

def mark_strong_warning_sent(asset_type):
    """تسجيل إرسال تحذير قوي"""
    open_trade = get_current_open_trade(asset_type)
    if open_trade:
        open_trade["strong_warning_sent"] = True
        open_trade["warning_sent"] = True
        pos_file = get_position_file(asset_type)
        with open(pos_file, 'w', encoding='utf-8') as f:
            json.dump(open_trade, f, indent=2, ensure_ascii=False)

def _send_light_warning(asset_type, current_price, trade_type, distance_pct, adx, bb_position, asset_label, decimal_format, reasons):
    """إرسال تحذير بسيط"""
    reason_text = "\n".join([f"• {r}" for r in reasons if r])
    msg = f"""
🔍 **تنبيه - راقب الصفقة** 🔍
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **الأصل:** {asset_label}
📈 **الصفقة:** {trade_type}
💰 **السعر الحالي:** {current_price:{decimal_format}}$

📊 **التحليل الفني:**
{reason_text}

💡 **توصيتي:**
• راقب الصفقة عن كثب
• لا تتخذ إجراءً حالياً
• سأرسل تحديثاً إذا تغير الوضع

📌 **لا تعتبر الصفقة مغلقة.** فقط انتبه.
"""
    send_telegram_message(msg)

def _send_medium_warning(asset_type, current_price, trade_type, entry_price, distance_pct, adx, stoch_k, volume_ratio, asset_label, decimal_format, reasons):
    """إرسال تحذير متوسط"""
    profit_loss = (current_price - entry_price) if trade_type == "BUY" else (entry_price - current_price)
    reason_text = "\n".join([f"• {r}" for r in reasons if r])
    
    msg = f"""
⚠️ **تحذير - حركة غير طبيعية** ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **الأصل:** {asset_label}
📈 **الصفقة:** {trade_type}
💰 **سعر الدخول:** {entry_price:{decimal_format}}$
💰 **السعر الحالي:** {current_price:{decimal_format}}$
📊 **الربح/الخسارة:** {profit_loss:+.2f}$

📊 **مؤشرات الانعكاس:**
{reason_text}

💡 **توصيتي:**
• أنصحك بتضييق وقف الخسارة
• أو تأمين جزء من الأرباح
• لا أعتبر الصفقة مغلقة بعد

📌 **القرار النهائي لك.**
"""
    send_telegram_message(msg)

def _send_strong_warning(asset_type, current_price, trade_type, entry_price, distance_pct, adx, volume_ratio, hourly_trend, asset_label, decimal_format, reasons):
    """إرسال تحذير قوي"""
    profit_loss = (current_price - entry_price) if trade_type == "BUY" else (entry_price - current_price)
    reason_text = "\n".join([f"• {r}" for r in reasons if r])
    new_signal = "SELL" if trade_type == "BUY" else "BUY"
    
    msg = f"""
🚨 **⚠️ تحذير فوري - انعكاس قاطع ⚠️** 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **الأصل:** {asset_label}
📉 **الصفقة:** {trade_type}
💰 **سعر الدخول:** {entry_price:{decimal_format}}$
💵 **السعر الحالي:** {current_price:{decimal_format}}$
📉 **الخسارة الحالية:** {profit_loss:+.2f}$

📊 **أسباب الانعكاس القاطع:**
{reason_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **قرار الحوباني:**
أعتبر هذه الصفقة **مغلقة** افتراضياً.

💡 **توصيتي القوية:**
• **أغلق الصفقة فوراً**
• لا تنتظر عودة السعر
• الإشارة الجديدة: {new_signal}

✅ **بعد الإغلاق، أرسل لي "تم الإغلاق"**
"""
    send_telegram_message(msg)
EOF

# ============================================================
# ✅ الانتهاء
# ============================================================
echo ""
echo "✅ ✅ ✅ تم تطبيق نظام المراقبة الذكي بنجاح!"
echo ""
echo "📋 تم عمل نسخة احتياطية إضافية: main.py.monitoring_backup"
echo ""
echo "🚀 يمكنك الآن تشغيل البوت: python main.py"
