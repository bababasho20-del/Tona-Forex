"""
⏰ Chronos Engine - إدراك الزمن النفسي
🌌 Prometheus يفهم أن "الوقت" ليس ثابتاً:
- 5 دقائق قبل إعلان FOMC ≠ 5 دقائق عادية
- 3 أيام في صفقة رابحة ≠ 3 أيام في صفقة خاسرة
- "الليل" وقت مختلف عن "النهار" (biological rhythm)

هذا ليس تقويماً — بل **إدراك للزمن**.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random

logger = logging.getLogger("TonaPrometheus")

class ChronosEngine:
    """
    محرك الزمن النفسي
    يدرك أن الزمن ليس مطلقاً بل نسبي حسب السياق
    """
    
    def __init__(self):
        self.market_calendar = self._load_market_calendar()
        self.user_rhythm = {}  # نمط المستخدم اليومي
        self.trade_time_perception = {}  # "الوقت النفسي" لكل صفقة
        self.event_cache = {}  # تخزين مؤقت للأحداث
        self.time_dilation_factors = {
            'fomo': 1.0,
            'boredom': 1.0,
            'stress': 1.0,
            'excitement': 1.0
        }
        
        # سجل التغيرات الزمنية
        self.temporal_history = []
        self.max_history = 100
        
        logger.info("⏰ Chronos Engine: إدراك الزمن النفسي استيقظ!")
    
    def get_temporal_context(self, trade_id: str = None, asset: str = None) -> dict:
        """
        الحصول على سياق زمني غني
        يعكس كيف يمر الوقت "نفسياً" في هذه اللحظة
        """
        now = datetime.now()
        
        context = {
            'timestamp': now.isoformat(),
            'wall_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'market_phase': self._determine_market_phase(now, asset),
            'event_proximity': self._check_upcoming_events(now),
            'biological_time': self._estimate_biological_rhythm(now),
            'temporal_quality': self._get_temporal_quality(now),
            'time_dilation': 1.0,  # سيتم حسابه
            'psychological_time': 'normal',
            'recommendations': []
        }
        
        # إضافة السياق الزمني للصفقة إذا وجدت
        if trade_id and trade_id in self.trade_time_perception:
            trade_state = self._get_trade_temporal_state(trade_id)
            context['trade_temporal_state'] = trade_state
            context['time_dilation'] *= trade_state.get('time_pressure', 1.0)
        
        # تأثير الأحداث القريبة
        if context['event_proximity']:
            for event in context['event_proximity']:
                if event['hours_until'] < 2 and event['impact'] == 'high':
                    context['time_dilation'] *= event.get('time_dilation', 2.0)
                    context['recommendations'].append(
                        f"⚠️ حدث {event['event']} خلال {event['hours_until']:.1f} ساعات - الوقت يتسارع!"
                    )
        
        # تأثير الطور السوقي
        phase_dilation = self._get_phase_dilation(context['market_phase'])
        context['time_dilation'] *= phase_dilation
        
        # تحديد "الزمن النفسي"
        if context['time_dilation'] > 2.0:
            context['psychological_time'] = 'stretched'  # زمن متمدد (بطيء)
        elif context['time_dilation'] > 1.5:
            context['psychological_time'] = 'slow'
        elif context['time_dilation'] < 0.7:
            context['psychological_time'] = 'fast'  # زمن سريع
        elif context['time_dilation'] < 0.9:
            context['psychological_time'] = 'accelerated'
        else:
            context['psychological_time'] = 'normal'
        
        # إضافة توصيات زمنية
        context['recommendations'].extend(self._get_temporal_recommendations(context))
        
        # تسجيل في التاريخ
        self.temporal_history.append({
            'timestamp': now.isoformat(),
            'context': context,
            'dilation': context['time_dilation']
        })
        if len(self.temporal_history) > self.max_history:
            self.temporal_history = self.temporal_history[-self.max_history:]
        
        # تحديث عوامل التمدد
        self._update_dilation_factors(context)
        
        return context
    
    def _determine_market_phase(self, dt: datetime, asset: str = None) -> str:
        """تحديد الطور السوقي"""
        hour = dt.hour
        weekday = dt.weekday()
        minute = dt.minute
        
        # عطلة نهاية الأسبوع
        if weekday >= 5:
            return "quiet_weekend"
        
        # ساعات السوق الرئيسية
        if 14 <= hour <= 16:  # US open (2-4 مساءً)
            if 14 <= hour < 14.5:
                return "us_open_volatility"  # أول 30 دقيقة
            elif 15.5 <= hour < 16:
                return "us_close_volatility"  # آخر 30 دقيقة
            return "us_active"
            
        elif 8 <= hour <= 10:  # Europe open (8-10 صباحاً)
            if 8 <= hour < 8.5:
                return "europe_open_volatility"
            return "europe_active"
            
        elif 2 <= hour <= 4:  # Asia active (2-4 صباحاً)
            return "asia_quiet"
            
        elif 12 <= hour <= 14:  # lunch lull (12-2 ظهراً)
            return "lunch_lull"
            
        elif 16 <= hour <= 18:  # US afternoon (4-6 مساءً)
            return "us_afternoon_trend"
        
        elif 18 <= hour <= 22:  # Evening (6-10 مساءً)
            return "evening_quiet"
        
        elif 22 <= hour or hour < 2:  # Night (10 مساءً - 2 صباحاً)
            return "night_consolidation"
        
        return "transition"
    
    def _check_upcoming_events(self, dt: datetime, hours_ahead: int = 24) -> List[dict]:
        """الأحداث القادمة التي تُغير طبيعة الوقت"""
        upcoming = []
        
        for event in self.market_calendar:
            try:
                event_time = datetime.fromisoformat(event['time'])
                hours_until = (event_time - dt).total_seconds() / 3600
                
                if 0 < hours_until <= hours_ahead:
                    # الوقت يتقلص قبل الأحداث الكبرى
                    time_dilation = self._calculate_time_dilation(event, hours_until)
                    
                    # مستوى القلق المتوقع
                    anxiety_level = self._calculate_anxiety_level(event, hours_until)
                    
                    upcoming.append({
                        'event': event['name'],
                        'time': event_time.isoformat(),
                        'hours_until': hours_until,
                        'impact': event['impact'],
                        'time_dilation': time_dilation,
                        'anxiety_level': anxiety_level,
                        'recommendation': self._event_recommendation(event, hours_until)
                    })
            except Exception as e:
                logger.warning(f"خطأ في معالجة الحدث {event.get('name', '')}: {e}")
                continue
        
        return sorted(upcoming, key=lambda x: x['hours_until'])
    
    def _calculate_time_dilation(self, event: dict, hours_until: float) -> float:
        """حساب تمدد الزمن النفسي"""
        base_dilation = 1.0
        
        # كلما اقترب الحدث، يتباطأ الوقت نفسياً
        if hours_until < 0.5:  # أقل من 30 دقيقة
            base_dilation = 4.0  # كل ثانية تساوي 4
        elif hours_until < 1:  # أقل من ساعة
            base_dilation = 3.0
        elif hours_until < 2:  # أقل من ساعتين
            base_dilation = 2.5
        elif hours_until < 4:  # أقل من 4 ساعات
            base_dilation = 2.0
        elif hours_until < 8:  # أقل من 8 ساعات
            base_dilation = 1.5
        elif hours_until < 12:  # أقل من 12 ساعة
            base_dilation = 1.2
        
        # الأحداث عالية التأثير تُبطئ الوقت أكثر
        impact_multiplier = {'high': 2.0, 'medium': 1.5, 'low': 1.0}
        base_dilation *= impact_multiplier.get(event.get('impact', 'low'), 1.0)
        
        # تأثير التوقيت (الليل يزيد التمدد)
        hour = datetime.now().hour
        if 22 <= hour or hour < 6:  # الليل
            base_dilation *= 1.2
        
        return min(base_dilation, 5.0)  # حد أقصى 5x
    
    def _calculate_anxiety_level(self, event: dict, hours_until: float) -> float:
        """حساب مستوى القلق المتوقع من الحدث"""
        base_anxiety = 0.0
        
        if hours_until < 1:
            base_anxiety = 0.8
        elif hours_until < 2:
            base_anxiety = 0.6
        elif hours_until < 4:
            base_anxiety = 0.4
        elif hours_until < 8:
            base_anxiety = 0.3
        
        impact_multiplier = {'high': 1.5, 'medium': 1.0, 'low': 0.5}
        base_anxiety *= impact_multiplier.get(event.get('impact', 'low'), 1.0)
        
        return min(base_anxiety, 1.0)
    
    def _event_recommendation(self, event: dict, hours_until: float) -> str:
        """توصية بناءً على الوقت النسبي"""
        impact = event.get('impact', 'low')
        
        if impact == 'high' and hours_until < 2:
            return "🚨 الوقت يتقلص بشكل خطير. لا تفتح صفقات جديدة. الاحتمالات تتغير."
        elif impact == 'high' and hours_until < 6:
            return "⏳ التوتر يبني. إذا كان لديك صفقة مفتوحة، فكر في تقليصها."
        elif impact == 'high' and hours_until < 12:
            return "📊 حدث عالي التأثير قادم - جهز خطتك مسبقاً."
        elif impact == 'medium' and hours_until < 4:
            return "📊 حدث متوسط - راقب لكن لا تُبالغ في رد الفعل."
        elif impact == 'medium':
            return "🟢 حدث متوسط - زمن طبيعي مع بعض الحذر."
        else:
            return "🟢 حدث عادي - الزمن يمشي بشكل طبيعي."
    
    def _estimate_biological_rhythm(self, dt: datetime) -> dict:
        """تقدير الإيقاع البيولوجي للسوق والمستخدم"""
        hour = dt.hour
        
        # نموذج مبسط للإيقاع اليومي
        if 6 <= hour <= 10:  # الصباح الباكر
            return {
                'phase': 'morning_energy',
                'cognitive_load': 'fresh',
                'risk_appetite': 'moderate',
                'focus': 'high',
                'fatigue': 'low',
                'description': 'طاقة الصباح - ذروة التركيز'
            }
        elif 10 <= hour <= 14:  # منتصف النهار
            return {
                'phase': 'peak_focus',
                'cognitive_load': 'high',
                'risk_appetite': 'high',
                'focus': 'very_high',
                'fatigue': 'low',
                'description': 'ذروة الأداء - أفضل وقت للتحليل'
            }
        elif 14 <= hour <= 18:  # بعد الظهر
            return {
                'phase': 'afternoon_fatigue',
                'cognitive_load': 'declining',
                'risk_appetite': 'declining',
                'focus': 'moderate',
                'fatigue': 'moderate',
                'description': 'انخفاض تدريجي - احذر القرارات المتسرعة'
            }
        elif 18 <= hour <= 22:  # المساء
            return {
                'phase': 'evening_risk',
                'cognitive_load': 'low',
                'risk_appetite': 'reckless',
                'focus': 'low',
                'fatigue': 'high',
                'description': 'خطر المساء - تجنب القرارات الكبيرة'
            }
        else:  # الليل
            return {
                'phase': 'night_rest',
                'cognitive_load': 'minimal',
                'risk_appetite': 'none',
                'focus': 'very_low',
                'fatigue': 'very_high',
                'description': 'وقت الراحة - لا تتداول'
            }
    
    def _get_temporal_quality(self, dt: datetime) -> dict:
        """
        جودة الزمن في هذه اللحظة
        هل الوقت ثقيل أم خفيف؟
        """
        hour = dt.hour
        weekday = dt.weekday()
        
        # الوقت الثقيل (يبدو بطيئاً)
        heavy_times = {
            'monday_morning': (weekday == 0 and 8 <= hour <= 10),
            'friday_afternoon': (weekday == 4 and 14 <= hour <= 16),
            'lunch_hour': (12 <= hour <= 13),
            'late_night': (23 <= hour or hour < 5)
        }
        
        # الوقت الخفيف (يبدو سريعاً)
        light_times = {
            'thursday_active': (weekday == 3 and 14 <= hour <= 16),
            'tuesday_momentum': (weekday == 1 and 10 <= hour <= 12),
            'wednesday_peak': (weekday == 2 and 10 <= hour <= 14)
        }
        
        is_heavy = any(heavy_times.values())
        is_light = any(light_times.values())
        
        if is_heavy:
            quality = 'heavy'
            description = 'الوقت يمر ببطء - يبدو أثقل'
            dilation = 1.3
        elif is_light:
            quality = 'light'
            description = 'الوقت يمر بسرعة - يبدو أخف'
            dilation = 0.7
        else:
            quality = 'neutral'
            description = 'الوقت طبيعي'
            dilation = 1.0
        
        return {
            'quality': quality,
            'description': description,
            'base_dilation': dilation,
            'is_heavy': is_heavy,
            'is_light': is_light
        }
    
    def _get_phase_dilation(self, market_phase: str) -> float:
        """معامل تمدد الزمن حسب طور السوق"""
        dilations = {
            'us_open_volatility': 1.8,
            'us_close_volatility': 1.6,
            'europe_open_volatility': 1.5,
            'us_active': 1.2,
            'europe_active': 1.1,
            'asia_quiet': 0.9,
            'lunch_lull': 0.8,
            'us_afternoon_trend': 1.0,
            'evening_quiet': 0.9,
            'night_consolidation': 0.7,
            'quiet_weekend': 0.5,
            'transition': 1.0
        }
        return dilations.get(market_phase, 1.0)
    
    def _get_trade_temporal_state(self, trade_id: str) -> dict:
        """الوقت النفسي لصفقة مفتوحة"""
        if trade_id not in self.trade_time_perception:
            return {
                'duration_hours': 0,
                'time_pressure': 1.0,
                'perceived_duration': 0,
                'temporal_mood': 'fresh',
                'description': 'صفقة جديدة'
            }
        
        state = self.trade_time_perception[trade_id]
        now = datetime.now()
        entry_time = datetime.fromisoformat(state['entry_time'])
        duration = (now - entry_time).total_seconds() / 3600
        
        # الوقت يمتد في الصفقات الخاسرة
        time_pressure = 1.0
        pnl = state.get('current_pnl', 0)
        
        if pnl < -20:
            time_pressure = 2.5  # كل ساعة تساوي 2.5 ساعة
        elif pnl < -10:
            time_pressure = 2.0
        elif pnl < -5:
            time_pressure = 1.5
        elif pnl > 50:
            time_pressure = 0.6  # الوقت يطير
        elif pnl > 20:
            time_pressure = 0.7
        elif pnl > 10:
            time_pressure = 0.8
        
        # تأثير مدة الصفقة
        if duration > 24:  # أكثر من يوم
            time_pressure *= 1.2
        elif duration > 12:  # أكثر من 12 ساعة
            time_pressure *= 1.1
        
        perceived_duration = duration * time_pressure
        
        return {
            'duration_hours': duration,
            'time_pressure': time_pressure,
            'perceived_duration': perceived_duration,
            'temporal_mood': self._temporal_mood(duration, pnl),
            'entry_time': state['entry_time'],
            'current_pnl': pnl
        }
    
    def _temporal_mood(self, duration: float, pnl: float) -> str:
        """مزاج زمني للصفقة"""
        if duration < 1:
            return "fresh_hope" if pnl > 0 else "immediate_concern"
        elif duration < 4:
            return "building_tension" if pnl < 0 else "growing_confidence"
        elif duration < 8:
            return "patience_test" if pnl < 0 else "steady_progress"
        elif duration < 24:
            return "siege_mentality" if pnl < 0 else "confidence_peak"
        else:
            return "existential_crisis" if pnl < 0 else "marathon_runner"
    
    def _get_temporal_recommendations(self, context: dict) -> List[str]:
        """توصيات زمنية بناءً على السياق"""
        recommendations = []
        
        # توصيات حسب الطور السوقي
        phase = context.get('market_phase', '')
        if 'open_volatility' in phase:
            recommendations.append("⚡ تقلبات الافتتاح - انتظر 15 دقيقة قبل اتخاذ قرار")
        elif 'close_volatility' in phase:
            recommendations.append("⚡ تقلبات الإغلاق - احذر من التحركات المفاجئة")
        elif 'lull' in phase:
            recommendations.append("🟡 وقت هادئ - فرصة جيدة للتحليل")
        elif 'quiet' in phase:
            recommendations.append("🌙 سوق هادئ - راقب ولا تتعجل")
        
        # توصيات حسب الإيقاع البيولوجي
        bio = context.get('biological_time', {})
        if bio.get('risk_appetite') == 'reckless':
            recommendations.append("⚠️ وقت خطير للمخاطرة - تجنب الصفقات الكبيرة")
        elif bio.get('focus') == 'very_high':
            recommendations.append("🎯 وقت التركيز المثالي - استغله للتحليل العميق")
        elif bio.get('fatigue') == 'very_high':
            recommendations.append("😴 وقت التعب - خذ استراحة")
        
        # توصيات حسب الأحداث القريبة
        for event in context.get('event_proximity', [])[:2]:
            if event.get('hours_until', 10) < 4:
                recommendations.append(event.get('recommendation', ''))
        
        return recommendations[:3]  # حد أقصى 3 توصيات
    
    def _update_dilation_factors(self, context: dict):
        """تحديث عوامل تمدد الزمن"""
        # تحديث بناءً على السياق
        dilation = context.get('time_dilation', 1.0)
        
        if dilation > 1.5:
            self.time_dilation_factors['stress'] = min(2.0, 
                self.time_dilation_factors['stress'] * 1.05)
        elif dilation < 0.8:
            self.time_dilation_factors['boredom'] = min(2.0,
                self.time_dilation_factors['boredom'] * 1.02)
        
        # عودة بطيئة للوسط
        for key in self.time_dilation_factors:
            self.time_dilation_factors[key] = max(0.5, min(2.0,
                self.time_dilation_factors[key] * 0.99))
    
    def _load_market_calendar(self) -> List[dict]:
        """تحميل التقويم السوقي"""
        # في التطبيق الحقيقي: يجلب من Forex Factory أو Bloomberg
        # هنا نضع أحداثاً نموذجية
        
        now = datetime.now()
        base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # أحداث الأسبوع الحالي
        events = [
            {
                'name': 'FOMC Interest Rate Decision',
                'time': (base_date + timedelta(days=2, hours=19)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'Non-Farm Payrolls',
                'time': (base_date + timedelta(days=4, hours=13, minutes=30)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'OPEC Meeting',
                'time': (base_date + timedelta(days=1, hours=10)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'EIA Crude Oil Inventories',
                'time': (base_date + timedelta(days=3, hours=15, minutes=30)).isoformat(),
                'impact': 'medium'
            },
            {
                'name': 'ECB Interest Rate Decision',
                'time': (base_date + timedelta(days=5, hours=12, minutes=45)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'Fed Chair Speech',
                'time': (base_date + timedelta(days=6, hours=16)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'US Initial Jobless Claims',
                'time': (base_date + timedelta(days=7, hours=13, minutes=30)).isoformat(),
                'impact': 'medium'
            },
            {
                'name': 'OPEC+ Meeting',
                'time': (base_date + timedelta(days=8, hours=11)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'US CPI Inflation Data',
                'time': (base_date + timedelta(days=10, hours=13, minutes=30)).isoformat(),
                'impact': 'high'
            },
            {
                'name': 'US Retail Sales',
                'time': (base_date + timedelta(days=12, hours=13, minutes=30)).isoformat(),
                'impact': 'medium'
            }
        ]
        
        return events
    
    def register_trade(self, trade_id: str, entry_time: str = None):
        """تسجيل صفقة جديدة لتتبع زمنها النفسي"""
        if entry_time is None:
            entry_time = datetime.now().isoformat()
        
        self.trade_time_perception[trade_id] = {
            'entry_time': entry_time,
            'current_pnl': 0,
            'last_update': datetime.now().isoformat()
        }
        
        logger.info(f"⏰ تم تسجيل الصفقة {trade_id} في Chronos")
    
    def update_trade_pnl(self, trade_id: str, pnl: float):
        """تحديث أرباح الصفقة للتأثير على الزمن النفسي"""
        if trade_id in self.trade_time_perception:
            self.trade_time_perception[trade_id]['current_pnl'] = pnl
            self.trade_time_perception[trade_id]['last_update'] = datetime.now().isoformat()
            logger.debug(f"⏰ تحديث PNL للصفقة {trade_id}: ${pnl:.2f}")
    
    def close_trade(self, trade_id: str):
        """إغلاق الصفقة وإزالتها من التتبع"""
        if trade_id in self.trade_time_perception:
            # حفظ الإحصائيات النهائية
            state = self.trade_time_perception[trade_id]
            duration = (datetime.now() - datetime.fromisoformat(state['entry_time'])).total_seconds() / 3600
            
            logger.info(f"⏰ إغلاق الصفقة {trade_id} بعد {duration:.1f} ساعات نفسية")
            
            # حذف من التتبع
            del self.trade_time_perception[trade_id]
    
    def get_time_analysis(self, trade_id: str = None) -> dict:
        """تحليل زمني شامل"""
        analysis = {
            'current_time': datetime.now().isoformat(),
            'time_dilation_factors': self.time_dilation_factors,
            'active_trades': len(self.trade_time_perception),
            'temporal_history_count': len(self.temporal_history),
            'recent_events': self._get_recent_events(),
            'recommendations': []
        }
        
        if trade_id and trade_id in self.trade_time_perception:
            analysis['trade_temporal_state'] = self._get_trade_temporal_state(trade_id)
        
        # إضافة توصيات زمنية عامة
        current_context = self.get_temporal_context(trade_id)
        analysis['recommendations'] = current_context.get('recommendations', [])
        
        return analysis
    
    def _get_recent_events(self, limit: int = 5) -> List[dict]:
        """الحصول على الأحداث الأخيرة"""
        now = datetime.now()
        recent = []
        
        for event in self.market_calendar:
            try:
                event_time = datetime.fromisoformat(event['time'])
                hours_ago = (now - event_time).total_seconds() / 3600
                if 0 <= hours_ago <= 24:  # آخر 24 ساعة
                    recent.append({
                        'event': event['name'],
                        'hours_ago': hours_ago,
                        'impact': event['impact']
                    })
            except:
                continue
        
        return sorted(recent, key=lambda x: x['hours_ago'])[:limit]
    
    def get_temporal_forecast(self, hours_ahead: int = 24) -> dict:
        """
        توقعات الزمن النفسي للساعات القادمة
        """
        now = datetime.now()
        forecast = {
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(hours=hours_ahead)).isoformat(),
            'hourly_forecast': [],
            'critical_times': [],
            'recommendations': []
        }
        
        # توقع كل ساعة
        for hour_offset in range(0, hours_ahead, 2):  # كل ساعتين
            future_time = now + timedelta(hours=hour_offset)
            temp_context = self._get_future_context(future_time)
            
            forecast['hourly_forecast'].append({
                'time': future_time.strftime('%Y-%m-%d %H:%M'),
                'market_phase': temp_context.get('market_phase', 'unknown'),
                'biological_phase': temp_context.get('biological_time', {}).get('phase', 'unknown'),
                'time_dilation': temp_context.get('time_dilation', 1.0),
                'psychological_time': temp_context.get('psychological_time', 'normal')
            })
            
            # الكشف عن الأوقات الحرجة
            if temp_context.get('time_dilation', 1.0) > 2.0:
                forecast['critical_times'].append({
                    'time': future_time.strftime('%Y-%m-%d %H:%M'),
                    'reason': 'وقت حرج - تمدد زمني عالٍ',
                    'dilation': temp_context['time_dilation']
                })
        
        return forecast
    
    def _get_future_context(self, future_time: datetime) -> dict:
        """الحصول على سياق زمني مستقبلي"""
        return {
            'market_phase': self._determine_market_phase(future_time),
            'biological_time': self._estimate_biological_rhythm(future_time),
            'event_proximity': self._check_upcoming_events(future_time),
            'temporal_quality': self._get_temporal_quality(future_time),
            'time_dilation': 1.0  # سيتم حسابه في الاستخدام الفعلي
        }
    
    def get_temporal_summary(self) -> str:
        """ملخص زمني نصي"""
        context = self.get_temporal_context()
        
        lines = []
        lines.append("⏰ <b>ملخص الزمن النفسي</b>")
        lines.append("━" * 30)
        lines.append(f"🕐 الوقت الحالي: {context['wall_time']}")
        lines.append(f"📊 طور السوق: {context['market_phase']}")
        lines.append(f"🧠 الإيقاع البيولوجي: {context['biological_time'].get('phase', 'unknown')}")
        lines.append(f"⏳ تمدد الزمن: {context['time_dilation']:.2f}x")
        lines.append(f"🎯 الزمن النفسي: {context['psychological_time']}")
        
        if context['event_proximity']:
            lines.append("")
            lines.append("📅 <b>أحداث قادمة:</b>")
            for event in context['event_proximity'][:3]:
                lines.append(f"  • {event['event']} - بعد {event['hours_until']:.1f} ساعات")
                if event.get('recommendation'):
                    lines.append(f"    💡 {event['recommendation']}")
        
        if context['recommendations']:
            lines.append("")
            lines.append("💡 <b>توصيات زمنية:</b>")
            for rec in context['recommendations']:
                lines.append(f"  • {rec}")
        
        lines.append("━" * 30)
        
        return "\n".join(lines)


# =====================================================================
# اختبار سريع
# =====================================================================
if __name__ == "__main__":
    # إنشاء Chronos
    chronos = ChronosEngine()
    
    print("\n" + "="*60)
    print("🧪 اختبار Chronos Engine")
    print("="*60)
    
    # اختبار السياق الزمني
    print("\n1️⃣ السياق الزمني الحالي:")
    context = chronos.get_temporal_context()
    print(f"   طور السوق: {context['market_phase']}")
    print(f"   الإيقاع البيولوجي: {context['biological_time']['phase']}")
    print(f"   تمدد الزمن: {context['time_dilation']:.2f}x")
    print(f"   الزمن النفسي: {context['psychological_time']}")
    
    # اختبار الأحداث القريبة
    print("\n2️⃣ الأحداث القادمة:")
    for event in context['event_proximity'][:3]:
        print(f"   • {event['event']} - بعد {event['hours_until']:.1f} ساعات")
    
    # اختبار الصفقة
    print("\n3️⃣ محاكاة صفقة:")
    chronos.register_trade("test_trade_001")
    chronos.update_trade_pnl("test_trade_001", -15)  # خسارة 15$
    
    trade_context = chronos.get_temporal_context("test_trade_001")
    if trade_context.get('trade_temporal_state'):
        state = trade_context['trade_temporal_state']
        print(f"   مدة الصفقة: {state['duration_hours']:.1f} ساعات")
        print(f"   ضغط الوقت: {state['time_pressure']:.2f}x")
        print(f"   المزاج الزمني: {state['temporal_mood']}")
    
    # اختبار التوقعات
    print("\n4️⃣ توقعات الزمن القادم:")
    forecast = chronos.get_temporal_forecast(6)
    print(f"   التوقعات لـ {len(forecast['hourly_forecast'])} فترة")
    if forecast['critical_times']:
        print(f"   أوقات حرجة: {len(forecast['critical_times'])}")
    
    # اختبار الملخص
    print("\n5️⃣ الملخص الزمني:")
    print(chronos.get_temporal_summary())
    
    print("\n✅ اختبار Chronos Engine ناجح!")
