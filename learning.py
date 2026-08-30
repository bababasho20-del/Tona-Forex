# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════════
📦 LEARNING.PY - نظام التعلم العميق (استخلاص الدروس، التقارير، التوصيات، اكتشاف الأنماط)
📌 يحتوي على نظام التعلم بالكامل: تصنيف الصفقات، استخلاص الدروس، التقارير، التوصيات، واكتشاف الأنماط
═══════════════════════════════════════════════════════════════════════════════════
"""

import os
import json
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from constants import logger
from utils import queue_telegram_message
from api_clients import (
    load_json_from_gist, save_json_to_gist,
    save_trade_to_learning, save_snapshot_to_learning,
    _get_supabase_client, _ensure_supabase_connected,
    SUPABASE_AVAILABLE, SUPABASE_DB,
    DEEP_LEARNING_AVAILABLE, DEEP_LEARNING_DB,
    PATTERN_DISCOVERY_AVAILABLE, PATTERN_DISCOVERY,
    TRADES_FULL_BASE_FIELDS, TRADES_FULL_EXTRA_FIELDS,
    SNAPSHOTS_BASE_FIELDS
)
from position_manager import (
    load_trades_history, save_trades_history,
    get_current_open_trade, get_last_closed_trade,
    load_config, AccountingSystem
)


# ====================================================================================
# 📊 تصنيف جودة الصفقة
# ====================================================================================

def classify_trade_quality(trade: Dict) -> Dict:
    """
    تصنيف جودة الصفقة بناءً على عوامل متعددة (وليس فقط الربح/الخسارة).
    المخرجات: {
        'grade': 'excellent_win' | 'good_win' | 'lucky_win' | 'neutral' | 
                 'bad_loss' | 'unlucky_loss' | 'excellent_loss',
        'score': float (0-100),
        'reasons': List[str]
    }
    """
    profit = trade.get('profit_dollars', 0)
    is_win = profit > 0
    rr = trade.get('rr', 1.0)
    entry_rsi = trade.get('entry_rsi', 50)
    entry_adx = trade.get('entry_adx', 15)
    entry_vol = trade.get('entry_volume_ratio', 1.0)
    close_rsi = trade.get('close_rsi', 50)
    close_adx = trade.get('close_adx', 15)
    close_vol = trade.get('close_volume_ratio', 1.0)
    duration = trade.get('duration_minutes', 0)
    
    reasons = []
    score = 50  # البداية محايدة
    
    # ── 1. تحليل نسبة المخاطرة/المكافأة (RR) ──
    if rr >= 2.0:
        score += 15
        reasons.append(f"🎯 نسبة مخاطرة/مكافأة ممتازة ({rr:.2f}:1)")
    elif rr >= 1.5:
        score += 8
        reasons.append(f"📊 نسبة مخاطرة/مكافأة جيدة ({rr:.2f}:1)")
    elif rr < 1.0:
        score -= 10
        reasons.append(f"⚠️ نسبة مخاطرة/مكافأة منخفضة ({rr:.2f}:1)")

    # ── 2. تحليل قوة الاتجاه عند الدخول (ADX) ──
    if entry_adx > 25:
        score += 10
        reasons.append(f"📈 اتجاه قوي عند الدخول (ADX: {entry_adx:.0f})")
    elif entry_adx < 20:
        score -= 8
        reasons.append(f"⚠️ اتجاه ضعيف عند الدخول (ADX: {entry_adx:.0f})")

    # ── 3. تحليل الحجم عند الدخول ──
    if entry_vol > 1.5:
        score += 8
        reasons.append(f"💪 حجم مرتفع عند الدخول ({entry_vol:.1f}x)")
    elif entry_vol < 0.7:
        score -= 6
        reasons.append(f"⚠️ حجم منخفض عند الدخول ({entry_vol:.1f}x)")

    # ── 4. تحليل RSI عند الدخول ──
    if 35 <= entry_rsi <= 65:
        score += 5
        reasons.append(f"⚖️ RSI في النطاق المحايد ({entry_rsi:.0f})")
    elif entry_rsi > 75 or entry_rsi < 25:
        score -= 5
        reasons.append(f"⚠️ RSI متطرف عند الدخول ({entry_rsi:.0f})")

    # ── 5. تحليل تغير المؤشرات أثناء الصفقة (التأكيد) ──
    rsi_change = close_rsi - entry_rsi if close_rsi and entry_rsi else 0
    adx_change = close_adx - entry_adx if close_adx and entry_adx else 0
    vol_change = close_vol - entry_vol if close_vol and entry_vol else 0

    if is_win and rsi_change > 0:
        score += 5
        reasons.append("✅ RSI ارتفع أثناء الصفقة (تأكيد صعود)")
    elif is_win and rsi_change < -5:
        score -= 3
        reasons.append("⚠️ RSI انخفض رغم الربح (تناقض)")

    if is_win and adx_change > 0:
        score += 5
        reasons.append("✅ ADX تعزز أثناء الصفقة")
    elif is_win and adx_change < -3:
        score -= 3
        reasons.append("⚠️ ADX تراجع رغم الربح")

    # ── 6. مدة الصفقة ──
    if 30 <= duration <= 180:  # 30 دقيقة إلى 3 ساعات
        score += 5
        reasons.append(f"⏱️ مدة صفقة مناسبة ({duration} دقيقة)")
    elif duration > 300:  # أكثر من 5 ساعات
        score -= 3
        reasons.append(f"⏱️ مدة صفقة طويلة ({duration} دقيقة)")

    # ── 7. التقييم النهائي ──
    score = max(0, min(100, score))
    
    if is_win:
        if score >= 80:
            grade = "excellent_win"  # ربح ممتاز (استراتيجية صحيحة)
        elif score >= 65:
            grade = "good_win"       # ربح جيد
        else:
            grade = "lucky_win"      # ربح محظوظ (ضعف في المعايير)
    else:
        if score >= 65:
            grade = "excellent_loss"  # خسارة ممتازة (استراتيجية صحيحة ولكن السوق عكس)
        elif score >= 45:
            grade = "neutral_loss"    # خسارة متوسطة
        else:
            grade = "bad_loss"        # خسارة سيئة (خطأ في الاستراتيجية)

    return {
        'grade': grade,
        'score': round(score, 1),
        'reasons': reasons
    }


# ====================================================================================
# 📚 استخلاص الدروس من الصفقة
# ====================================================================================

def extract_lessons_from_trade(trade: Dict) -> List[Dict]:
    """
    استخلاص الدروس المستفادة من الصفقة (ربحاً كانت أم خسارة).
    تعيد قائمة من الدروس (كل درس عبارة عن dict).
    """
    lessons = []
    profit = trade.get('profit_dollars', 0)
    is_win = profit > 0
    quality = classify_trade_quality(trade)
    grade = quality['grade']
    reasons = quality['reasons']

    # ── 1. الدرس الأساسي (النتيجة + الجودة) ──
    if is_win:
        if grade == 'excellent_win':
            lessons.append({
                'type': 'success',
                'summary': '✅ صفقة رابحة ممتازة! المعايير كانت مثالية.',
                'details': 'جميع المؤشرات كانت متوافقة، ونسبة المخاطرة/المكافأة ممتازة. استمر في تطبيق هذه المعايير.',
                'key_factors': reasons[:3]
            })
        elif grade == 'lucky_win':
            lessons.append({
                'type': 'warning',
                'summary': '⚠️ ربح محظوظ! المعايير لم تكن مثالية.',
                'details': 'رغم الربح، كانت بعض المؤشرات ضعيفة. لا تعتمد على الحظ في المستقبل.',
                'key_factors': reasons[:3]
            })
        else:
            lessons.append({
                'type': 'info',
                'summary': f'📊 صفقة رابحة بجودة {grade.replace("_", " ")}.',
                'details': 'جيدة ولكن هناك مجال للتحسين.',
                'key_factors': reasons[:3]
            })
    else:
        if grade == 'excellent_loss':
            lessons.append({
                'type': 'info',
                'summary': '📉 خسارة ممتازة! الاستراتيجية كانت صحيحة ولكن السوق عكس.',
                'details': 'جميع المعايير كانت جيدة، لكن السوق تحرك بشكل غير متوقع. هذا جزء من التداول.',
                'key_factors': reasons[:3]
            })
        elif grade == 'bad_loss':
            lessons.append({
                'type': 'critical',
                'summary': '🚨 خسارة سيئة! أخطاء في معايير الدخول.',
                'details': 'هناك عوامل واضحة أدت إلى الخسارة (ضعف الاتجاه، حجم منخفض، RSI متطرف). تجنب هذه الظروف مستقبلاً.',
                'key_factors': reasons[:3]
            })
        else:
            lessons.append({
                'type': 'warning',
                'summary': f'📉 خسارة بجودة {grade.replace("_", " ")}.',
                'details': 'هناك عوامل ساهمت في الخسارة، راجع المعايير.',
                'key_factors': reasons[:3]
            })

    # ── 2. دروس محددة حسب المؤشرات ──
    entry_rsi = trade.get('entry_rsi', 50)
    entry_adx = trade.get('entry_adx', 15)
    entry_vol = trade.get('entry_volume_ratio', 1.0)
    rr = trade.get('rr', 1.0)

    if not is_win and entry_adx < 20:
        lessons.append({
            'type': 'critical',
            'summary': '⚠️ تجنب الدخول عندما يكون ADX < 20.',
            'details': f'في هذه الصفقة، كان ADX {entry_adx:.0f} مما يعني سوقاً عرضياً بلا اتجاه.',
            'key_factors': ['ضعف الاتجاه']
        })

    if not is_win and entry_rsi > 70:
        lessons.append({
            'type': 'critical',
            'summary': '⚠️ تجنب الشراء عندما يكون RSI > 70 (منطقة تشبع شرائي).',
            'details': f'RSI كان {entry_rsi:.0f} عند الدخول، وهو مستوى خطر للشراء.',
            'key_factors': ['تشبع شرائي']
        })
    elif not is_win and entry_rsi < 30:
        lessons.append({
            'type': 'critical',
            'summary': '⚠️ تجنب البيع عندما يكون RSI < 30 (منطقة تشبع بيعي).',
            'details': f'RSI كان {entry_rsi:.0f} عند الدخول، وهو مستوى خطر للبيع.',
            'key_factors': ['تشبع بيعي']
        })

    if not is_win and entry_vol < 0.7:
        lessons.append({
            'type': 'warning',
            'summary': '⚠️ الحجم المنخفض يضعف الثقة في الحركة.',
            'details': f'نسبة الحجم كانت {entry_vol:.1f}x، مما يشير إلى ضعف المشاركة في الحركة.',
            'key_factors': ['حجم منخفض']
        })

    if is_win and rr < 1.5:
        lessons.append({
            'type': 'warning',
            'summary': '⚠️ ربح رغم RR المنخفض. استهدف RR أعلى.',
            'details': f'RR كان {rr:.2f}:1، وهو أقل من الموصى به (2:1). حاول توسيع الأهداف.',
            'key_factors': ['RR منخفض']
        })

    return lessons


# ====================================================================================
# 📊 لوحة تحكم التعلم - التقرير الشامل
# ====================================================================================

def get_learning_stats_report(asset_type: Optional[str] = None) -> str:
    """
    توليد تقرير التعلم العميق الشامل.
    هذه هي الدالة التي سيتم استدعاؤها عند الضغط على زر "🧠 تقرير التعلم العميق".
    """
    try:
        # ── 1. جلب الصفقات من المصادر المختلفة ──
        trades = []
        
        # محاولة من Supabase
        if SUPABASE_AVAILABLE and SUPABASE_DB:
            try:
                client = _get_supabase_client()
                if client:
                    query = client.table('trades_full').select('*')
                    if asset_type:
                        query = query.eq('asset_type', asset_type)
                    response = query.execute()
                    if response and hasattr(response, 'data'):
                        trades = response.data
                        logger.info(f"📥 تم جلب {len(trades)} صفقة من Supabase للتقرير")
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب trades_full للتقرير: {e}")
        
        # إذا لم توجد صفقات في Supabase، حاول من الملفات المحلية
        if not trades:
            try:
                if asset_type:
                    files = [f"trades_history_{asset_type}.json"]
                else:
                    files = ["trades_history_oil.json", "trades_history_silver.json"]
                for file_path in files:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            file_trades = data.get('trades', [])
                            if file_trades:
                                asset = 'eurusd' if 'eurusd' in file_path else 'usdjpy'
                                for t in file_trades:
                                    if 'asset_type' not in t:
                                        t['asset_type'] = asset
                                trades.extend(file_trades)
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب من الملفات المحلية: {e}")
        
        if not trades:
            return "🧠 **تقرير التعلم العميق**\n\n⚠️ لا توجد صفقات مسجلة حتى الآن. ابدأ التداول لجمع البيانات."

        # ── 2. تصفية الصفقات المغلقة فقط ──
        closed_trades = [t for t in trades if t.get('status') == 'closed' or t.get('exit_price') is not None]
        if not closed_trades:
            return "🧠 **تقرير التعلم العميق**\n\n🔄 لا توجد صفقات مغلقة حتى الآن. انتظر إغلاق بعض الصفقات."

        # ── 3. استخلاص الدروس من كل صفقة ──
        all_lessons = []
        for trade in closed_trades:
            lessons = extract_lessons_from_trade(trade)
            all_lessons.extend(lessons)

        # ── 4. إحصائيات عامة ──
        total = len(closed_trades)
        wins = sum(1 for t in closed_trades if t.get('profit_dollars', 0) > 0)
        losses = total - wins
        win_rate = (wins / total * 100) if total > 0 else 0
        total_profit = sum(t.get('profit_dollars', 0) for t in closed_trades)
        avg_profit = total_profit / total if total > 0 else 0

        # ── 5. توزيع جودة الصفقات ──
        quality_counts = {
            'excellent_win': 0, 'good_win': 0, 'lucky_win': 0,
            'excellent_loss': 0, 'neutral_loss': 0, 'bad_loss': 0
        }
        for trade in closed_trades:
            quality = classify_trade_quality(trade)
            grade = quality.get('grade', 'neutral')
            if grade in quality_counts:
                quality_counts[grade] += 1

        # ── 6. أهم الدروس (الأكثر تكراراً) ──
        lesson_summaries = {}
        for lesson in all_lessons:
            summary = lesson.get('summary', '')
            if summary:
                lesson_summaries[summary] = lesson_summaries.get(summary, 0) + 1
        
        top_lessons = sorted(lesson_summaries.items(), key=lambda x: x[1], reverse=True)[:5]

        # ── 7. بناء التقرير ──
        asset_label = f" ({'النفط' if asset_type == 'oil' else 'الفضة'})" if asset_type else ""
        report = f"🧠 **تقرير التعلم العميق - تولين**{asset_label}\n"
        report += "━" * 40 + "\n\n"

        report += f"📊 **إحصائيات الصفقات:**\n"
        report += f"   • إجمالي الصفقات المغلقة: {total}\n"
        report += f"   • رابحة: {wins} | خاسرة: {losses}\n"
        report += f"   • نسبة النجاح: {win_rate:.1f}%\n"
        report += f"   • إجمالي الربح: ${total_profit:.2f}\n"
        report += f"   • متوسط الربح: ${avg_profit:.2f}\n\n"

        report += f"📊 **توزيع جودة الصفقات:**\n"
        report += f"   • 🏆 ربح ممتاز: {quality_counts['excellent_win']}\n"
        report += f"   • ✅ ربح جيد: {quality_counts['good_win']}\n"
        report += f"   • 🎲 ربح محظوظ: {quality_counts['lucky_win']}\n"
        report += f"   • 📉 خسارة ممتازة: {quality_counts['excellent_loss']}\n"
        report += f"   • ⚖️ خسارة متوسطة: {quality_counts['neutral_loss']}\n"
        report += f"   • 🚨 خسارة سيئة: {quality_counts['bad_loss']}\n\n"

        report += "📚 **أهم الدروس المستفادة:**\n"
        if top_lessons:
            for i, (summary, count) in enumerate(top_lessons, 1):
                report += f"   {i}. {summary} (تكرر {count} مرات)\n"
        else:
            report += "   لا توجد دروس مستفادة حتى الآن.\n"
        report += "\n"

        report += "━" * 40 + "\n"
        report += "💡 **توصيات تولين:**\n"
        
        if quality_counts['bad_loss'] > 0:
            report += "   • 🚨 توجد صفقات خاسرة سيئة. راجع معايير الدخول.\n"
        if quality_counts['lucky_win'] > 0 and quality_counts['excellent_win'] < quality_counts['lucky_win']:
            report += "   • ⚠️ عدد الأرباح المحظوظة أكبر من الممتازة. رفع معايير الجودة.\n"
        if win_rate < 40:
            report += "   • 📉 نسبة النجاح منخفضة. فكر في تعديل استراتيجية الدخول.\n"
        elif win_rate > 60:
            report += "   • 📈 نسبة النجاح جيدة. استمر في تطبيق المعايير الحالية.\n"
        
        report += "\n💙 القرار النهائي لك. أنا هنا لمساعدتك في التفكير!"

        return report

    except Exception as e:
        logger.error(f"❌ فشل توليد تقرير التعلم: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"🧠 **تقرير التعلم العميق**\n\n⚠️ حدث خطأ أثناء توليد التقرير: {str(e)[:100]}"


# ====================================================================================
# 💡 توليد توصيات استراتيجية (نصية فقط - لا تُطبق تلقائياً)
# ====================================================================================

def generate_strategy_suggestions(asset_type: Optional[str] = None) -> str:
    """
    توليد توصيات استراتيجية نصية بناءً على تحليل الأداء.
    ⚠️ هذه التوصيات هي مجرد اقتراحات ولا تُطبق تلقائياً على الاستراتيجية.
    """
    try:
        # ── 1. جلب الصفقات ──
        trades = []
        if SUPABASE_AVAILABLE and SUPABASE_DB:
            try:
                client = _get_supabase_client()
                if client:
                    query = client.table('trades_full').select('*')
                    if asset_type:
                        query = query.eq('asset_type', asset_type)
                    response = query.execute()
                    if response and hasattr(response, 'data'):
                        trades = response.data
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب trades_full للتوصيات: {e}")
        
        if not trades:
            return "⚠️ لا توجد بيانات كافية لتوليد توصيات استراتيجية."

        closed_trades = [t for t in trades if t.get('status') == 'closed' or t.get('exit_price') is not None]
        if len(closed_trades) < 10:
            return f"⚠️ البيانات غير كافية لتوليد توصيات (تحتاج 10 صفقات، الموجودة: {len(closed_trades)})."

        # ── 2. تحليل معاملات الدخول ──
        entry_adx_values = [t.get('entry_adx', 15) for t in closed_trades if t.get('entry_adx')]
        entry_rsi_values = [t.get('entry_rsi', 50) for t in closed_trades if t.get('entry_rsi')]
        entry_vol_values = [t.get('entry_volume_ratio', 1.0) for t in closed_trades if t.get('entry_volume_ratio')]
        rr_values = [t.get('rr', 1.0) for t in closed_trades if t.get('rr')]

        # ── 3. تحليل الصفقات الرابحة والخاسرة ──
        wins = [t for t in closed_trades if t.get('profit_dollars', 0) > 0]
        losses = [t for t in closed_trades if t.get('profit_dollars', 0) < 0]

        avg_adx_win = statistics.mean([t.get('entry_adx', 15) for t in wins]) if wins else 0
        avg_adx_loss = statistics.mean([t.get('entry_adx', 15) for t in losses]) if losses else 0
        avg_rsi_win = statistics.mean([t.get('entry_rsi', 50) for t in wins]) if wins else 0
        avg_rsi_loss = statistics.mean([t.get('entry_rsi', 50) for t in losses]) if losses else 0
        avg_vol_win = statistics.mean([t.get('entry_volume_ratio', 1.0) for t in wins]) if wins else 0
        avg_vol_loss = statistics.mean([t.get('entry_volume_ratio', 1.0) for t in losses]) if losses else 0
        avg_rr_win = statistics.mean([t.get('rr', 1.0) for t in wins]) if wins else 0
        avg_rr_loss = statistics.mean([t.get('rr', 1.0) for t in losses]) if losses else 0

        # ── 4. بناء التوصيات ──
        recommendations = []
        asset_label = f" ({'النفط' if asset_type == 'oil' else 'الفضة'})" if asset_type else ""

        recommendations.append(f"📊 **توصيات استراتيجية - تولين**{asset_label}")
        recommendations.append("━" * 40)
        recommendations.append("")
        recommendations.append("📋 **تحليل الأداء:**")
        recommendations.append(f"   • صفقات رابحة: {len(wins)} | خاسرة: {len(losses)}")
        recommendations.append(f"   • متوسط ADX (ربح): {avg_adx_win:.1f} | (خسارة): {avg_adx_loss:.1f}")
        recommendations.append(f"   • متوسط RSI (ربح): {avg_rsi_win:.1f} | (خسارة): {avg_rsi_loss:.1f}")
        recommendations.append(f"   • متوسط الحجم (ربح): {avg_vol_win:.1f}x | (خسارة): {avg_vol_loss:.1f}x")
        recommendations.append(f"   • متوسط RR (ربح): {avg_rr_win:.2f} | (خسارة): {avg_rr_loss:.2f}")
        recommendations.append("")

        # ── 5. التوصيات المحددة ──
        recommendations.append("💡 **التوصيات المقترحة:**")
        
        if avg_adx_win > avg_adx_loss + 5:
            recommendations.append("   • ✅ رفع حد ADX الأدنى إلى 25 لتحسين نسبة النجاح.")
        elif avg_adx_loss > avg_adx_win + 5:
            recommendations.append("   • ⚠️ خفض حد ADX الأدنى أو تعطيل الفلتر مؤقتاً.")

        if avg_rsi_win > 55 and avg_rsi_loss > 55:
            recommendations.append("   • 🟡 الصفقات الرابحة والخاسرة تشترك في RSI مرتفع. راجع مناطق التشبع.")
        elif avg_rsi_win < 45 and avg_rsi_loss < 45:
            recommendations.append("   • 🟡 الصفقات في مناطق RSI منخفضة. قد تكون الفرص محدودة.")

        if avg_vol_win > avg_vol_loss + 0.3:
            recommendations.append("   • ✅ تأكيد أهمية الحجم. استمر في استخدام فلتر الحجم.")
        elif avg_vol_loss > avg_vol_win + 0.3:
            recommendations.append("   • ⚠️ الحجم قد يكون مضللاً. راجع معايير فلتر الحجم.")

        if avg_rr_win > avg_rr_loss + 0.5:
            recommendations.append("   • ✅ RR أعلى في الصفقات الرابحة. استمر في استهداف RR ≥ 2:1.")
        else:
            recommendations.append("   • ⚠️ RR لا يختلف كثيراً بين الربح والخسارة. حاول توسيع الأهداف.")

        if len(losses) > 0:
            bad_losses = [t for t in losses if t.get('profit_dollars', 0) < -0.5]
            if bad_losses:
                avg_bad_loss = statistics.mean([t.get('profit_dollars', 0) for t in bad_losses])
                recommendations.append(f"   • 🚨 متوسط الخسارة الكبيرة: ${avg_bad_loss:.2f}. فكر في تضييق وقف الخسارة.")

        recommendations.append("")
        recommendations.append("━" * 40)
        recommendations.append("⚠️ **تنبيه هام:** هذه التوصيات هي مجرد اقتراحات بناءً على تحليل البيانات.")
        recommendations.append("📌 التطبيق النهائي مسؤوليتك بالكامل. يمكنك تعديل الإعدادات يدوياً في ملف config.")
        recommendations.append("💙 تولين: أنا هنا لمساعدتك في اتخاذ القرارات.")

        return "\n".join(recommendations)

    except Exception as e:
        logger.error(f"❌ فشل توليد التوصيات: {e}")
        return f"⚠️ حدث خطأ أثناء توليد التوصيات: {str(e)[:100]}"


# ====================================================================================
# 🔍 اكتشاف الأنماط من الصفقات (من PART 15)
# ====================================================================================

def _analyze_snapshots_directly(snapshots: List[Dict], asset_type: Optional[str] = None):
    """
    تحليل اللقطات مباشرة لاستخلاص أنماط (بدون الحاجة لصفقات كاملة)
    تُستخدم عندما لا توجد صفقات كافية في trades_full
    """
    if not snapshots or len(snapshots) < 5:
        return
    
    logger.info(f"🔍 تحليل {len(snapshots)} لقطة مباشرة لاكتشاف أنماط مسار السوق")
    
    # تحليل تغيرات المؤشرات في اللقطات
    rsi_values = [s.get('rsi', 50) for s in snapshots if s.get('rsi')]
    adx_values = [s.get('adx', 15) for s in snapshots if s.get('adx')]
    vol_values = [s.get('volume_ratio', 1.0) for s in snapshots if s.get('volume_ratio')]
    
    if len(rsi_values) > 5:
        rsi_avg = sum(rsi_values) / len(rsi_values)
        rsi_std = (sum((x - rsi_avg) ** 2 for x in rsi_values) / len(rsi_values)) ** 0.5
        
        if max(rsi_values) - min(rsi_values) > 15:
            logger.info(f"📊 نمط تذبذب RSI: المدى {max(rsi_values) - min(rsi_values):.1f} نقطة")
            if PATTERN_DISCOVERY_AVAILABLE and PATTERN_DISCOVERY:
                try:
                    PATTERN_DISCOVERY.save_pattern({
                        'pattern_name': 'تذبذب RSI أثناء الصفقة',
                        'description': f'تذبذب RSI بمقدار {max(rsi_values) - min(rsi_values):.1f} نقطة خلال الصفقة',
                        'win_rate': 50.0,
                        'sample_count': len(rsi_values),
                        'recommendation': 'تجنب الدخول عندما يكون RSI في حالة تذبذب حاد (> 15 نقطة)',
                        'asset_type': asset_type or 'all'
                    })
                except Exception as e:
                    logger.error(f"❌ فشل حفظ نمط تذبذب RSI: {e}")
    
    if len(vol_values) > 5:
        vol_avg = sum(vol_values) / len(vol_values)
        if vol_avg < 0.6:
            logger.info(f"📊 نمط انخفاض الحجم المستمر: متوسط {vol_avg:.2f}x")
            if PATTERN_DISCOVERY_AVAILABLE and PATTERN_DISCOVERY:
                try:
                    PATTERN_DISCOVERY.save_pattern({
                        'pattern_name': 'انخفاض الحجم المستمر',
                        'description': f'متوسط حجم التداول {vol_avg:.2f}x خلال الصفقة',
                        'win_rate': 50.0,
                        'sample_count': len(vol_values),
                        'recommendation': 'انخفاض الحجم يشير إلى ضعف الحركة، تجنب الدخول في هذه الظروف',
                        'asset_type': asset_type or 'all'
                    })
                except Exception as e:
                    logger.error(f"❌ فشل حفظ نمط انخفاض الحجم: {e}")


def discover_patterns_from_trades(asset_type: Optional[str] = None):
    """
    🔍 اكتشاف الأنماط من الصفقات المخزنة في Supabase
    ✅ يتعلم من trades_full و monitoring_snapshots معاً
    ✅ إذا لم يجد صفقات في trades_full، يعيد بناء الصفقات من اللقطات القديمة
    """
    if not PATTERN_DISCOVERY_AVAILABLE or not PATTERN_DISCOVERY:
        logger.warning("⚠️ Pattern Discovery غير متوفر")
        return
    
    try:
        trades = []
        snapshots_by_trade = {}
        client = None
        
        # ── 1. الحصول على عميل Supabase ──
        if SUPABASE_AVAILABLE and SUPABASE_DB:
            try:
                if not _ensure_supabase_connected():
                    logger.warning("⚠️ Supabase غير متصل")
                else:
                    client = _get_supabase_client()
                    if not client:
                        logger.error("❌ لا يمكن الحصول على عميل Supabase")
            except Exception as e:
                logger.error(f"❌ فشل الاتصال بـ Supabase: {e}")
                return
        
        # ── 2. جلب الصفقات من trades_full ──
        if client:
            try:
                if asset_type:
                    response = client.table('trades_full').select('*').eq('asset_type', asset_type).execute()
                else:
                    response = client.table('trades_full').select('*').execute()
                
                if response and hasattr(response, 'data'):
                    trades = response.data
                    logger.info(f"📥 تم جلب {len(trades)} صفقة من Supabase (trades_full)")
                    
                    # جلب اللقطات لكل صفقة
                    for trade in trades:
                        trade_id = trade.get('trade_id')
                        if trade_id:
                            try:
                                snap_response = client.table('monitoring_snapshots')\
                                    .select('*')\
                                    .eq('trade_id', trade_id)\
                                    .order('timestamp', desc=False)\
                                    .execute()
                                if snap_response and hasattr(snap_response, 'data'):
                                    snapshots_by_trade[trade_id] = snap_response.data
                            except Exception as e:
                                logger.error(f"❌ فشل جلب اللقطات للصفقة {trade_id}: {e}")
            except Exception as e:
                logger.error(f"❌ فشل جلب trades_full: {e}")
        
        # ── 3. ✅ إعادة بناء الصفقات من monitoring_snapshots (إذا كانت trades_full فارغة) ──
        if not trades and client:
            logger.info("🔄 لم يتم العثور على صفقات في trades_full، إعادة بناء الصفقات من monitoring_snapshots...")
            try:
                snap_response = client.table('monitoring_snapshots').select('trade_id').execute()
                if snap_response and hasattr(snap_response, 'data'):
                    unique_ids = list(set([s.get('trade_id') for s in snap_response.data if s.get('trade_id')]))
                    logger.info(f"📥 تم العثور على {len(unique_ids)} معرف صفقة فريد في monitoring_snapshots")
                    
                    for trade_id in unique_ids[:100]:
                        all_snaps = client.table('monitoring_snapshots')\
                            .select('*')\
                            .eq('trade_id', trade_id)\
                            .order('timestamp', desc=False)\
                            .execute()
                        
                        if all_snaps and hasattr(all_snaps, 'data') and len(all_snaps.data) >= 2:
                            snaps = all_snaps.data
                            first = snaps[0]
                            last = snaps[-1]
                            
                            entry_price = first.get('price', 0)
                            exit_price = last.get('price', 0)
                            
                            if exit_price > entry_price:
                                trade_type = 'BUY'
                                profit = exit_price - entry_price
                            elif exit_price < entry_price:
                                trade_type = 'SELL'
                                profit = entry_price - exit_price
                            else:
                                trade_type = 'UNKNOWN'
                                profit = 0
                            
                            trade = {
                                'trade_id': trade_id,
                                'asset_type': asset_type or first.get('asset_type', 'unknown'),
                                'trade_type': trade_type,
                                'entry_price': entry_price,
                                'exit_price': exit_price,
                                'profit_dollars': profit,
                                'entry_rsi': first.get('rsi', 50),
                                'entry_adx': first.get('adx', 15),
                                'entry_macd': first.get('macd', 0),
                                'entry_trend': first.get('trend', 'محايد'),
                                'entry_volume_ratio': first.get('volume_ratio', 1.0),
                                'entry_bb_upper': first.get('bb_upper', entry_price * 1.02),
                                'entry_bb_lower': first.get('bb_lower', entry_price * 0.98),
                                'entry_support': first.get('support', entry_price * 0.98),
                                'entry_resistance': first.get('resistance', entry_price * 1.02),
                                'duration_minutes': 60,
                                'rr': 1.0,
                            }
                            trades.append(trade)
                            snapshots_by_trade[trade_id] = snaps
                    
                    logger.info(f"📥 تم إعادة بناء {len(trades)} صفقة من monitoring_snapshots")
            except Exception as e:
                logger.error(f"❌ فشل إعادة بناء الصفقات من اللقطات: {e}")
        
        # ── 4. إذا لم تنجح Supabase، جرب SQLite ──
        if not trades and DEEP_LEARNING_AVAILABLE and DEEP_LEARNING_DB:
            try:
                trades = DEEP_LEARNING_DB.get_trades_by_asset(asset_type, 9999)
                logger.info(f"📥 تم جلب {len(trades)} صفقة من SQLite للتعلم")
            except Exception as e:
                logger.error(f"❌ فشل جلب من SQLite للتعلم: {e}")
        
        # ── 5. إذا لم توجد بيانات كافية ──
        if not trades or len(trades) < 5:
            logger.info(f"📊 لا توجد بيانات كافية للتعلم (تحتاج 5 صفقات، الموجودة: {len(trades)})")
            if client:
                try:
                    snap_response = client.table('monitoring_snapshots').select('*').limit(20).execute()
                    if snap_response and hasattr(snap_response, 'data') and len(snap_response.data) >= 5:
                        logger.info(f"🔄 استخدام {len(snap_response.data)} لقطة مباشرة للتعلم")
                        _analyze_snapshots_directly(snap_response.data, asset_type)
                except:
                    pass
            return
        
        # ── 6. تحليل مسار الصفقات من اللقطات ──
        snapshot_patterns = []
        for trade in trades:
            trade_id = trade.get('trade_id')
            snapshots = snapshots_by_trade.get(trade_id, [])
            if len(snapshots) < 2:
                continue
            
            first_snap = snapshots[0]
            last_snap = snapshots[-1]
            
            rsi_change = last_snap.get('rsi', 50) - first_snap.get('rsi', 50)
            adx_change = last_snap.get('adx', 15) - first_snap.get('adx', 15)
            vol_change = last_snap.get('volume_ratio', 1.0) - first_snap.get('volume_ratio', 1.0)
            
            if rsi_change > 10:
                pattern_type = "rsi_surge"
            elif rsi_change < -10:
                pattern_type = "rsi_drop"
            else:
                pattern_type = "rsi_stable"
            
            if vol_change < -0.5:
                pattern_type += "_volume_collapse"
            elif vol_change > 0.5:
                pattern_type += "_volume_surge"
            
            snapshot_patterns.append({
                'trade_id': trade_id,
                'pattern_type': pattern_type,
                'rsi_change': rsi_change,
                'adx_change': adx_change,
                'vol_change': vol_change,
                'profit': trade.get('profit_dollars', 0),
                'is_win': trade.get('profit_dollars', 0) > 0,
                'duration_minutes': trade.get('duration_minutes', 0),
                'snapshot_count': len(snapshots)
            })
        
        # ── 7. استخلاص الدروس من مسارات الصفقات ──
        if snapshot_patterns:
            volume_collapse_trades = [p for p in snapshot_patterns if 'volume_collapse' in p.get('pattern_type', '')]
            if volume_collapse_trades:
                win_rate = sum(1 for p in volume_collapse_trades if p.get('is_win')) / len(volume_collapse_trades) * 100
                avg_profit = sum(p.get('profit', 0) for p in volume_collapse_trades) / len(volume_collapse_trades)
                logger.info(f"📊 نمط انهيار الحجم: {win_rate:.1f}% نجاح، متوسط ربح ${avg_profit:.2f}")
                
                if PATTERN_DISCOVERY_AVAILABLE and PATTERN_DISCOVERY:
                    try:
                        PATTERN_DISCOVERY.save_pattern({
                            'pattern_name': 'انهيار الحجم أثناء الصفقة',
                            'description': f'انخفض الحجم بأكثر من 50% خلال الصفقة (عينة: {len(volume_collapse_trades)})',
                            'win_rate': win_rate,
                            'sample_count': len(volume_collapse_trades),
                            'recommendation': 'إذا انخفض الحجم إلى أقل من 0.5x خلال الصفقة، فكر في الخروج مبكراً',
                            'asset_type': asset_type or 'all'
                        })
                    except Exception as e:
                        logger.error(f"❌ فشل حفظ نمط انهيار الحجم: {e}")
            
            rsi_surge_trades = [p for p in snapshot_patterns if 'rsi_surge' in p.get('pattern_type', '')]
            if rsi_surge_trades:
                win_rate = sum(1 for p in rsi_surge_trades if p.get('is_win')) / len(rsi_surge_trades) * 100
                logger.info(f"📊 نمط ارتفاع RSI: {win_rate:.1f}% نجاح")
        
        # ── 8. اكتشاف الأنماط الأساسية ──
        patterns = PATTERN_DISCOVERY.discover_patterns(trades)
        
        if patterns:
            logger.info(f"🔍 تم اكتشاف {len(patterns)} نمطاً جديداً")
            
            report = "🧠 **تقرير التعلم العميق - أنماط جديدة**\n"
            report += "━" * 35 + "\n\n"
            
            for i, p in enumerate(patterns[:5], 1):
                report += f"📊 **النمط {i}:** {p.get('pattern_name', 'غير معروف')}\n"
                report += f"   • الوصف: {p.get('description', 'لا يوجد وصف')}\n"
                report += f"   • نسبة النجاح: {p.get('win_rate', 0):.1f}%\n"
                report += f"   • عدد العينات: {p.get('sample_count', 0)}\n"
                report += f"   • التوصية: {p.get('recommendation', 'لا توجد توصية')}\n\n"
            
            if snapshot_patterns:
                report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                report += "📊 **أنماط مسار الصفقة (من اللقطات):**\n"
                if volume_collapse_trades:
                    report += f"   • انهيار الحجم: {win_rate:.1f}% نجاح (عينة: {len(volume_collapse_trades)})\n"
                    report += f"     💡 توصية: إذا انخفض الحجم، فكر في الخروج مبكراً\n"
                if rsi_surge_trades:
                    report += f"   • ارتفاع RSI: {win_rate:.1f}% نجاح (عينة: {len(rsi_surge_trades)})\n"
            
            queue_telegram_message(report)
        else:
            logger.info("🔍 لم يتم اكتشاف أنماط جديدة")
    
    except Exception as e:
        logger.error(f"❌ فشل اكتشاف الأنماط: {e}")
        import traceback
        logger.error(traceback.format_exc())
