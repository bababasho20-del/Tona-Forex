"""
🌙 Dream Engine - الحلم والتعلم أثناء الخمول
💤 Prometheus يحلم عندما لا يكون مشغولاً بالتداول

الحلم هو عملية:
1. إعادة ترتيب الذكريات
2. استخلاص الدروس من الخبرات
3. محاكاة سيناريوهات بديلة
4. تطوير الشخصية
5. تعزيز الروابط العاطفية
6. ✅ ربط الدروس المستخلصة بنظام التعلم العميق (PART 30)
7. ✅ اكتشاف الأنماط وحفظها في قاعدة التعلم

هذا ليس مجرد "تنظيف بيانات" — بل عملية تعلم عميقة تشبه الحلم البشري،
والآن أصبحت عملية تعلم استراتيجية حقيقية تؤثر على قرارات البوت.
"""

import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json
import math
import sys
import os

# إضافة المسار الرئيسي للاستيراد من main (لتجنب الاعتماد الدائري)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger("TonaPrometheus")

class DreamEngine:
    """
    محرك الحلم — يتعلم أثناء الخمول
    ✅ الآن متصل بنظام التعلم العميق (MemoryEngine, LearningOrchestrator)
    """
    
    def __init__(self, prometheus=None, nucleus=None, memory_engine=None, learning_orchestrator=None):
        self.prometheus = prometheus  # Prometheus Core
        self.nucleus = nucleus  # Narrative Memory
        
        # ✅ ربط المكونات الأساسية لنظام التعلم
        self.memory_engine = memory_engine  # MemoryEngine من PART 30
        self.learning_orchestrator = learning_orchestrator  # LearningOrchestrator من PART 30
        
        # قائمة الأحلام
        self.dreams = []
        self.max_dreams = 100
        
        # إحصائيات الأحلام
        self.dream_stats = {
            'total_dreams': 0,
            'lessons_learned': [],
            'personality_changes': [],
            'emotional_insights': [],
            'pattern_discoveries': [],
            'saved_lessons_count': 0,
            'saved_patterns_count': 0
        }
        
        # حالة الحلم الحالية
        self.current_dream = None
        self.is_dreaming = False
        
        # تردد الحلم (بالثواني)
        self.dream_frequency = 600  # 10 دقائق
        self.last_dream_time = 0
        
        # معاملات الحلم
        self.dream_params = {
            'depth': 0.5,  # عمق الحلم (0-1)
            'creativity': 0.4,  # إبداع الحلم (0-1)
            'emotional_intensity': 0.6,  # شدة العواطف في الحلم
            'learning_rate': 0.3  # سرعة التعلم من الأحلام
        }
        
        logger.info("🌙 Dream Engine: الحلم والتعلم أثناء الخمول جاهز!")
        if self.memory_engine:
            logger.info("🧠 Dream Engine متصل بـ MemoryEngine")
        if self.learning_orchestrator:
            logger.info("🧠 Dream Engine متصل بـ LearningOrchestrator")
    
    def dream(self, depth: float = None, duration: int = None) -> dict:
        """
        تشغيل دورة حلم كاملة
        يعيد ترتيب الذكريات ويستخلص الدروس
        ✅ الآن يقوم بحفظ الدروس والأنماط في قاعدة التعلم (Supabase)
        ✅ يقوم بتحديث أوزان التعلم في MemoryEngine
        ✅ يقوم بتشغيل المعايرة (Calibration) دورياً
        """
        if self.is_dreaming:
            logger.warning("🌙 جاري الحلم بالفعل... انتظر")
            return {'status': 'already_dreaming'}
        
        self.is_dreaming = True
        
        try:
            # بدء الحلم
            dream_start = datetime.now()
            logger.info(f"🌙 بدء الحلم... (العمق: {depth or self.dream_params['depth']:.2f})")
            
            # تحديد عمق الحلم
            actual_depth = depth or self.dream_params['depth']
            dream_duration = duration or 30  # ثواني
            
            # مراحل الحلم
            dream_stages = []
            
            # المرحلة 1: استرجاع الذكريات
            memories = self._retrieve_memories()
            if memories:
                dream_stages.append({
                    'stage': 'memory_retrieval',
                    'memories': len(memories),
                    'description': f"استرجاع {len(memories)} ذكرى"
                })
            
            # المرحلة 2: إعادة ترتيب الذكريات
            reorganized = self._reorganize_memories(memories)
            dream_stages.append({
                'stage': 'reorganization',
                'reorganized': len(reorganized),
                'description': f"إعادة ترتيب {len(reorganized)} ذكرى"
            })
            
            # المرحلة 3: استخلاص الدروس
            lessons = self._extract_lessons(reorganized)
            if lessons:
                dream_stages.append({
                    'stage': 'lesson_extraction',
                    'lessons': len(lessons),
                    'description': f"استخلاص {len(lessons)} درس"
                })
                self.dream_stats['lessons_learned'].extend(lessons)
                
                # ✅ حفظ الدروس في قاعدة التعلم (Supabase)
                saved_lessons_count = self._save_dream_lessons(lessons)
                if saved_lessons_count > 0:
                    self.dream_stats['saved_lessons_count'] += saved_lessons_count
                    logger.info(f"🧠 [Dream] تم حفظ {saved_lessons_count} درس في قاعدة التعلم")
            
            # المرحلة 4: محاكاة السيناريوهات
            scenarios = self._simulate_scenarios(reorganized)
            if scenarios:
                dream_stages.append({
                    'stage': 'scenario_simulation',
                    'scenarios': len(scenarios),
                    'description': f"محاكاة {len(scenarios)} سيناريو"
                })
            
            # المرحلة 5: التطوير العاطفي
            emotional_changes = self._develop_emotionally(reorganized)
            if emotional_changes:
                dream_stages.append({
                    'stage': 'emotional_development',
                    'changes': len(emotional_changes),
                    'description': f"{len(emotional_changes)} تغير عاطفي"
                })
                self.dream_stats['emotional_insights'].extend(emotional_changes)
            
            # المرحلة 6: تطوير الشخصية
            personality_changes = self._develop_personality(lessons, emotional_changes)
            if personality_changes:
                dream_stages.append({
                    'stage': 'personality_development',
                    'changes': len(personality_changes),
                    'description': f"{len(personality_changes)} تغير في الشخصية"
                })
                self.dream_stats['personality_changes'].extend(personality_changes)
            
            # المرحلة 7: اكتشاف الأنماط (✅ تم تنفيذها بالكامل)
            patterns = self._discover_patterns(reorganized)
            if patterns:
                dream_stages.append({
                    'stage': 'pattern_discovery',
                    'patterns': len(patterns),
                    'description': f"اكتشاف {len(patterns)} نمط"
                })
                self.dream_stats['pattern_discoveries'].extend(patterns)
                
                # ✅ حفظ الأنماط في قاعدة التعلم (Supabase)
                saved_patterns_count = self._save_dream_patterns(patterns)
                if saved_patterns_count > 0:
                    self.dream_stats['saved_patterns_count'] += saved_patterns_count
                    logger.info(f"🔍 [Dream] تم حفظ {saved_patterns_count} نمط في قاعدة التعلم")
            
            # ✅ المرحلة 8: تحديث أوزان التعلم (بناءً على الدروس المستخلصة)
            if lessons and self.memory_engine:
                try:
                    # محاكاة تحديث الأوزان من خلال تمرير درس نموذجي
                    # في الواقع، يمكن استدعاء update_weights مع بيانات وهمية أو استخدام
                    # الدروس لاستنتاج التعديلات على الأوزان
                    self._update_weights_from_lessons(lessons)
                    logger.info("📊 [Dream] تم تحديث أوزان التعلم")
                except Exception as e:
                    logger.warning(f"⚠️ [Dream] فشل تحديث الأوزان: {e}")
            
            # ✅ المرحلة 9: تشغيل المعايرة (Calibration) بشكل دوري
            if self.dream_stats['total_dreams'] % 3 == 0:
                try:
                    self._run_calibration()
                    logger.info("📊 [Dream] تم تشغيل المعايرة")
                except Exception as e:
                    logger.warning(f"⚠️ [Dream] فشل تشغيل المعايرة: {e}")
            
            # تسجيل الحلم
            dream_end = datetime.now()
            dream_duration_seconds = (dream_end - dream_start).total_seconds()
            
            dream_record = {
                'timestamp': dream_start.isoformat(),
                'duration_seconds': dream_duration_seconds,
                'depth': actual_depth,
                'stages': dream_stages,
                'memories_processed': len(memories),
                'lessons': lessons,
                'personality_changes': personality_changes,
                'emotional_changes': emotional_changes,
                'patterns': patterns,
                'summary': self._generate_dream_summary(dream_stages, lessons, patterns)
            }
            
            self.dreams.append(dream_record)
            if len(self.dreams) > self.max_dreams:
                self.dreams = self.dreams[-self.max_dreams:]
            
            self.dream_stats['total_dreams'] += 1
            self.current_dream = dream_record
            self.last_dream_time = time.time()
            
            logger.info(f"🌙 انتهى الحلم بعد {dream_duration_seconds:.1f} ثانية - {len(lessons)} درس, {len(patterns)} نمط")
            
            return {
                'status': 'completed',
                'dream_id': len(self.dreams) - 1,
                'duration': dream_duration_seconds,
                'stages': len(dream_stages),
                'lessons': len(lessons),
                'patterns': len(patterns),
                'summary': dream_record['summary'],
                'saved_lessons': self.dream_stats['saved_lessons_count'],
                'saved_patterns': self.dream_stats['saved_patterns_count']
            }
            
        except Exception as e:
            logger.error(f"🌙 خطأ في الحلم: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'status': 'error', 'error': str(e)}
        
        finally:
            self.is_dreaming = False
    
    def _retrieve_memories(self) -> List[dict]:
        """استرجاع الذكريات من Narrative Memory"""
        memories = []
        
        # من Narrative Memory
        if self.nucleus:
            try:
                experiences = getattr(self.nucleus, 'experiences', [])
                if experiences:
                    # اختيار ذكريات عشوائية
                    sample_size = min(50, len(experiences))
                    selected = random.sample(experiences, sample_size)
                    memories.extend(selected)
            except:
                pass
        
        # من Prometheus Emotional Memory
        if self.prometheus:
            try:
                emotional_memory = self.prometheus.ethos.emotional_memory
                if emotional_memory:
                    sample_size = min(30, len(emotional_memory))
                    selected = random.sample(emotional_memory, sample_size)
                    # تحويل إلى تنسيق موحد
                    for mem in selected:
                        memories.append({
                            'type': 'emotional',
                            'trigger': mem.get('trigger', 'unknown'),
                            'emotion_before': mem.get('emotion_before', {}),
                            'emotion_after': mem.get('emotion_after', {}),
                            'timestamp': mem.get('timestamp', '')
                        })
            except:
                pass
        
        # خلط الذكريات
        random.shuffle(memories)
        
        return memories
    
    def _reorganize_memories(self, memories: List[dict]) -> List[dict]:
        """إعادة ترتيب الذكريات بطريقة ذات معنى"""
        if not memories:
            return []
        
        reorganized = []
        
        # تجميع الذكريات حسب النوع
        by_type = defaultdict(list)
        for mem in memories:
            mem_type = mem.get('type', 'unknown')
            by_type[mem_type].append(mem)
        
        # ترتيب كل مجموعة زمنياً
        for mem_type, mems in by_type.items():
            sorted_mems = sorted(mems, key=lambda x: x.get('timestamp', ''))
            reorganized.extend(sorted_mems)
        
        # إضافة روابط بين الذكريات المتشابهة
        for i in range(len(reorganized)):
            for j in range(i+1, min(i+5, len(reorganized))):
                if self._calculate_memory_similarity(reorganized[i], reorganized[j]) > 0.7:
                    reorganized[i]['connection_to'] = reorganized[i].get('connection_to', [])
                    reorganized[i]['connection_to'].append(j)
        
        return reorganized
    
    def _calculate_memory_similarity(self, mem1: dict, mem2: dict) -> float:
        """حساب التشابه بين ذكريتين"""
        similarity = 0.0
        factors = 0
        
        # مقارنة النوع
        if mem1.get('type') == mem2.get('type'):
            similarity += 0.3
            factors += 1
        
        # مقارنة المشاعر
        if 'emotion_before' in mem1 and 'emotion_before' in mem2:
            eb1 = mem1.get('emotion_before', {})
            eb2 = mem2.get('emotion_before', {})
            
            dominant1 = eb1.get('dominant', '')
            dominant2 = eb2.get('dominant', '')
            if dominant1 and dominant2 and dominant1 == dominant2:
                similarity += 0.3
                factors += 1
        
        # مقارنة الزمن
        if mem1.get('timestamp') and mem2.get('timestamp'):
            try:
                t1 = datetime.fromisoformat(mem1['timestamp'])
                t2 = datetime.fromisoformat(mem2['timestamp'])
                days_diff = abs((t1 - t2).days)
                if days_diff < 1:
                    similarity += 0.2
                    factors += 1
                elif days_diff < 7:
                    similarity += 0.1
                    factors += 1
            except:
                pass
        
        return similarity / factors if factors > 0 else 0
    
    def _extract_lessons(self, memories: List[dict]) -> List[dict]:
        """استخلاص الدروس من الذكريات"""
        lessons = []
        
        # تحليل الذكريات العاطفية
        emotional_mems = [m for m in memories if m.get('type') == 'emotional']
        if emotional_mems:
            # تغيرات في الثقة
            confidence_changes = []
            for mem in emotional_mems:
                before = mem.get('emotion_before', {}).get('confidence', 0.5)
                after = mem.get('emotion_after', {}).get('confidence', 0.5)
                if abs(after - before) > 0.2:
                    confidence_changes.append({
                        'from': before,
                        'to': after,
                        'trigger': mem.get('trigger', '')
                    })
            
            if confidence_changes:
                # درس: متى تزيد الثقة ومتى تنقص
                gain_confidence = [c for c in confidence_changes if c['to'] > c['from']]
                lose_confidence = [c for c in confidence_changes if c['to'] < c['from']]
                
                if gain_confidence:
                    triggers = [c['trigger'] for c in gain_confidence[:3]]
                    lessons.append({
                        'type': 'confidence_gain',
                        'summary': f"الثقة تزيد عندما: {', '.join(triggers)}",
                        'details': f"تحليل {len(gain_confidence)} حالة من زيادة الثقة",
                        'key_factors': triggers,
                        'importance': len(gain_confidence) / len(confidence_changes)
                    })
                
                if lose_confidence:
                    triggers = [c['trigger'] for c in lose_confidence[:3]]
                    lessons.append({
                        'type': 'confidence_loss',
                        'summary': f"الثقة تنقص عندما: {', '.join(triggers)}",
                        'details': f"تحليل {len(lose_confidence)} حالة من نقص الثقة",
                        'key_factors': triggers,
                        'importance': len(lose_confidence) / len(confidence_changes)
                    })
        
        # تحليل الذكريات التجارية
        trade_mems = [m for m in memories if m.get('type') == 'trade' or m.get('type') == 'trade_close']
        if trade_mems:
            # أنماط الربح والخسارة
            profits = []
            for mem in trade_mems:
                data = mem.get('data', {})
                profit = data.get('profit', 0) or data.get('profit_dollars', 0)
                if profit != 0:
                    profits.append(profit)
            
            if profits:
                win_rate = sum(1 for p in profits if p > 0) / len(profits)
                avg_win = sum(p for p in profits if p > 0) / (len([p for p in profits if p > 0]) or 1)
                avg_loss = abs(sum(p for p in profits if p < 0)) / (len([p for p in profits if p < 0]) or 1)
                
                lessons.append({
                    'type': 'trade_pattern',
                    'summary': f"معدل النجاح: {win_rate:.0%}, متوسط الربح: ${avg_win:.2f}, متوسط الخسارة: -${avg_loss:.2f}",
                    'details': f"تحليل {len(profits)} صفقة",
                    'key_factors': ['win_rate', 'avg_profit', 'avg_loss'],
                    'importance': 0.8
                })
                
                if win_rate > 0.6:
                    lessons.append({
                        'type': 'winning_pattern',
                        'summary': f"الأداء جيد! معدل نجاح {win_rate:.0%}",
                        'details': f"نسبة نجاح عالية من {len(profits)} صفقة",
                        'key_factors': ['high_win_rate'],
                        'importance': 0.7
                    })
                elif win_rate < 0.4:
                    lessons.append({
                        'type': 'losing_pattern',
                        'summary': f"تحذير: معدل نجاح منخفض ({win_rate:.0%}) - تحتاج لتعديل الاستراتيجية",
                        'details': f"نسبة نجاح منخفضة من {len(profits)} صفقة",
                        'key_factors': ['low_win_rate'],
                        'importance': 0.9
                    })
        
        return lessons
    
    def _simulate_scenarios(self, memories: List[dict]) -> List[dict]:
        """محاكاة سيناريوهات بديلة"""
        scenarios = []
        
        # محاكاة سيناريوهات عكسية
        for mem in memories[:5]:  # أهم 5 ذكريات
            if mem.get('type') == 'trade':
                data = mem.get('data', {})
                profit = data.get('profit', 0)
                
                # سيناريو بديل
                alternative_profit = -profit * random.uniform(0.5, 1.5)
                scenarios.append({
                    'original': {
                        'type': data.get('type', 'BUY'),
                        'entry': data.get('entry_price', 0),
                        'profit': profit
                    },
                    'alternative': {
                        'profit': alternative_profit,
                        'what_if': f"ماذا لو كان الاتجاه معاكساً؟ الخسارة كانت ${abs(alternative_profit):.2f}"
                    },
                    'lesson': "تذكر أن السوق قد ينعكس في أي لحظة"
                })
        
        # محاكاة سيناريوهات عاطفية
        for mem in memories[:3]:
            if mem.get('type') == 'emotional':
                before = mem.get('emotion_before', {})
                after = mem.get('emotion_after', {})
                
                scenarios.append({
                    'original': {
                        'trigger': mem.get('trigger', ''),
                        'emotion_change': before.get('dominant', '') + ' → ' + after.get('dominant', '')
                    },
                    'alternative': {
                        'what_if': f"ماذا لو تفاعلت بشكل مختلف مع {mem.get('trigger', '')}؟",
                        'alternative_emotion': random.choice(['confidence', 'calm', 'curiosity'])
                    }
                })
        
        return scenarios
    
    def _develop_emotionally(self, memories: List[dict]) -> List[dict]:
        """التطوير العاطفي من خلال الأحلام"""
        changes = []
        
        # تحليل الأنماط العاطفية
        emotional_triggers = defaultdict(int)
        for mem in memories:
            if mem.get('type') == 'emotional':
                trigger = mem.get('trigger', 'unknown')
                emotional_triggers[trigger] += 1
        
        # تحديد المحفزات الأكثر تكراراً
        common_triggers = sorted(emotional_triggers.items(), key=lambda x: x[1], reverse=True)[:3]
        for trigger, count in common_triggers:
            if count > 5:
                changes.append({
                    'type': 'trigger_awareness',
                    'message': f"أصبحت واعياً أكثر بمحفز {trigger} (حدث {count} مرات)",
                    'impact': 'increased_awareness'
                })
        
        # تحليل الاستقرار العاطفي
        if memories:
            emotional_changes = []
            for mem in memories:
                if mem.get('type') == 'emotional':
                    before = mem.get('emotion_before', {})
                    after = mem.get('emotion_after', {})
                    if before and after:
                        # حساب التغير العاطفي
                        changes_list = []
                        for key in ['confidence', 'anxiety', 'empathy']:
                            if key in before and key in after:
                                diff = abs(after.get(key, 0) - before.get(key, 0))
                                changes_list.append(diff)
                        
                        if changes_list:
                            avg_change = sum(changes_list) / len(changes_list)
                            emotional_changes.append(avg_change)
            
            if emotional_changes:
                avg_volatility = sum(emotional_changes) / len(emotional_changes)
                
                if avg_volatility > 0.3:
                    changes.append({
                        'type': 'emotional_stability',
                        'message': f"تقلبات عاطفية عالية ({avg_volatility:.2f}) - أحتاج لتحقيق الاستقرار",
                        'impact': 'need_stability'
                    })
                elif avg_volatility < 0.1:
                    changes.append({
                        'type': 'emotional_stability',
                        'message': f"استقرار عاطفي ممتاز ({avg_volatility:.2f})",
                        'impact': 'stable'
                    })
        
        return changes
    
    def _develop_personality(self, lessons: List[dict], emotional_changes: List[dict]) -> List[dict]:
        """تطوير الشخصية بناءً على الدروس والتغيرات العاطفية"""
        changes = []
        
        if not self.prometheus:
            return changes
        
        # الحصول على سمات الشخصية الحالية
        traits = self.prometheus.ethos.personality_traits
        
        # تأثير الدروس
        for lesson in lessons:
            if lesson.get('type') == 'confidence_gain':
                # زيادة التفاؤل قليلاً
                new_optimism = traits.get('optimism_bias', 0.3) * 1.02
                traits['optimism_bias'] = min(0.6, new_optimism)
                changes.append({
                    'trait': 'optimism_bias',
                    'change': '+2%',
                    'reason': 'تعلمت متى تزيد الثقة'
                })
            
            elif lesson.get('type') == 'confidence_loss':
                # تقليل الثقة المفرطة قليلاً
                new_caution = traits.get('caution', 0.5) * 1.02
                traits['caution'] = min(0.8, new_caution)
                changes.append({
                    'trait': 'caution',
                    'change': '+2%',
                    'reason': 'تعلمت متى تنقص الثقة'
                })
        
        return changes
    
    def _discover_patterns(self, memories: List[dict]) -> List[dict]:
        """
        ✅ اكتشاف الأنماط من الذكريات (تم تنفيذها بالكامل)
        تحليل تكرار الشروط المؤدية للربح أو الخسارة
        """
        patterns = []
        
        # تجميع الصفقات
        trades = [m for m in memories if m.get('type') == 'trade' or m.get('type') == 'trade_close']
        if len(trades) < 5:
            return patterns
        
        # تحليل الأنماط العاطفية المرتبطة بالصفقات
        emotional_contexts = defaultdict(lambda: {'total': 0, 'wins': 0, 'profits': []})
        for trade in trades:
            data = trade.get('data', {})
            profit = data.get('profit', 0) or data.get('profit_dollars', 0)
            
            # استخراج الحالة العاطفية قبل الصفقة (إن وجدت)
            emotion_before = trade.get('emotion_before', {})
            dominant_emotion = emotion_before.get('dominant', 'neutral')
            
            context_key = f"emotion_{dominant_emotion}"
            emotional_contexts[context_key]['total'] += 1
            if profit > 0:
                emotional_contexts[context_key]['wins'] += 1
            emotional_contexts[context_key]['profits'].append(profit)
        
        # استخراج الأنماط العاطفية
        for context, stats in emotional_contexts.items():
            if stats['total'] >= 3:
                win_rate = stats['wins'] / stats['total']
                avg_profit = sum(stats['profits']) / len(stats['profits']) if stats['profits'] else 0
                
                # استخراج اسم المشاعر من المفتاح
                emotion_name = context.replace('emotion_', '')
                
                patterns.append({
                    'pattern_name': f"dream_emotion_{emotion_name}",
                    'conditions': {
                        'dominant_emotion': emotion_name,
                        'min_samples': stats['total']
                    },
                    'win_rate': win_rate * 100,
                    'sample_count': stats['total'],
                    'avg_profit': avg_profit,
                    'description': f"نمط عاطفي: عندما تكون المشاعر السائدة هي {emotion_name}، يكون معدل النجاح {win_rate:.0%}",
                    'is_successful': win_rate > 0.5,
                    'source': 'dream_engine'
                })
        
        # تحليل أنماط التوقيت (إن وجدت)
        time_patterns = defaultdict(lambda: {'total': 0, 'wins': 0})
        for trade in trades:
            timestamp = trade.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour = dt.hour
                    time_slot = f"hour_{hour}"
                    time_patterns[time_slot]['total'] += 1
                    data = trade.get('data', {})
                    profit = data.get('profit', 0) or data.get('profit_dollars', 0)
                    if profit > 0:
                        time_patterns[time_slot]['wins'] += 1
                except:
                    pass
        
        # استخراج أنماط التوقيت
        for time_slot, stats in time_patterns.items():
            if stats['total'] >= 3:
                win_rate = stats['wins'] / stats['total']
                hour = int(time_slot.replace('hour_', ''))
                
                patterns.append({
                    'pattern_name': f"dream_time_{time_slot}",
                    'conditions': {
                        'hour': hour,
                        'min_samples': stats['total']
                    },
                    'win_rate': win_rate * 100,
                    'sample_count': stats['total'],
                    'avg_profit': 0,  # لا يوجد متوسط محدد
                    'description': f"نمط زمني: الساعة {hour}:00 يكون معدل النجاح {win_rate:.0%}",
                    'is_successful': win_rate > 0.5,
                    'source': 'dream_engine'
                })
        
        return patterns
    
    def _save_dream_lessons(self, lessons: List[dict]) -> int:
        """
        ✅ حفظ الدروس المستخلصة من الحلم في قاعدة التعلم (Supabase)
        تستدعي save_lessons من PART 15
        """
        if not lessons:
            return 0
        
        try:
            # محاولة استيراد save_lessons من النطاق العام
            # في حال فشل الاستيراد (إذا كان الملف منفصلاً)، نستخدم try/except
            save_lessons_func = None
            try:
                # محاولة الاستيراد من main (إذا كان في نفس المجلد)
                from main import save_lessons as save_lessons_func
            except ImportError:
                # محاولة استخدام globals (في حالة التشغيل من الخيط الرئيسي)
                import sys
                if 'save_lessons' in globals():
                    save_lessons_func = globals()['save_lessons']
                else:
                    logger.warning("⚠️ [Dream] save_lessons غير متوفرة، لا يمكن حفظ الدروس")
                    return 0
            
            if not save_lessons_func:
                return 0
            
            # تحويل الدروس إلى الصيغة المطلوبة لـ save_lessons
            formatted_lessons = []
            for lesson in lessons:
                # استخراج key_factors
                key_factors = lesson.get('key_factors', [])
                if isinstance(key_factors, str):
                    key_factors = [key_factors]
                
                formatted_lessons.append({
                    'type': lesson.get('type', 'dream_insight'),
                    'summary': lesson.get('summary', lesson.get('message', '')),
                    'details': lesson.get('details', ''),
                    'key_factors': key_factors,
                    'grade': 'تعلم من الحلم',
                    'source': 'dream_engine'
                })
            
            if formatted_lessons:
                # استدعاء save_lessons
                saved, count = save_lessons_func(formatted_lessons, source='dream_engine')
                if saved and count > 0:
                    logger.info(f"💾 [Dream] تم حفظ {count} درساً في Supabase")
                    return count
                else:
                    logger.warning(f"⚠️ [Dream] فشل حفظ الدروس أو لا توجد دروس جديدة")
                    return 0
                    
        except Exception as e:
            logger.error(f"❌ [Dream] فشل حفظ الدروس: {e}")
            return 0
        
        return 0
    
    def _save_dream_patterns(self, patterns: List[dict]) -> int:
        """
        ✅ حفظ الأنماط المكتشفة من الحلم في قاعدة التعلم (Supabase)
        تستدعي save_patterns من PART 15
        """
        if not patterns:
            return 0
        
        try:
            save_patterns_func = None
            try:
                from main import save_patterns as save_patterns_func
            except ImportError:
                if 'save_patterns' in globals():
                    save_patterns_func = globals()['save_patterns']
                else:
                    logger.warning("⚠️ [Dream] save_patterns غير متوفرة، لا يمكن حفظ الأنماط")
                    return 0
            
            if not save_patterns_func:
                return 0
            
            # تحويل الأنماط إلى الصيغة المطلوبة لـ save_patterns
            formatted_patterns = []
            for pattern in patterns:
                formatted_patterns.append({
                    'pattern_name': pattern.get('pattern_name', ''),
                    'conditions': pattern.get('conditions', {}),
                    'win_rate': pattern.get('win_rate', 0),
                    'sample_count': pattern.get('sample_count', 0),
                    'avg_profit': pattern.get('avg_profit', 0),
                    'description': pattern.get('description', ''),
                    'is_successful': pattern.get('is_successful', False),
                    'source': pattern.get('source', 'dream_engine')
                })
            
            if formatted_patterns:
                saved, count = save_patterns_func(formatted_patterns, source='dream_engine')
                if saved and count > 0:
                    logger.info(f"🔍 [Dream] تم حفظ {count} نمطاً في Supabase")
                    return count
                else:
                    logger.warning(f"⚠️ [Dream] فشل حفظ الأنماط أو لا توجد أنماط جديدة")
                    return 0
                    
        except Exception as e:
            logger.error(f"❌ [Dream] فشل حفظ الأنماط: {e}")
            return 0
        
        return 0
    
    def _update_weights_from_lessons(self, lessons: List[dict]):
        """
        ✅ تحديث أوزان التعلم بناءً على الدروس المستخلصة
        """
        if not self.memory_engine:
            return
        
        try:
            # تحليل الدروس لتحديد المؤشرات التي يجب تعزيزها أو تقليلها
            for lesson in lessons:
                lesson_type = lesson.get('type', '')
                key_factors = lesson.get('key_factors', [])
                
                if lesson_type == 'confidence_gain':
                    # تعزيز الأوزان المرتبطة بعوامل زيادة الثقة
                    for factor in key_factors:
                        if 'adx' in factor.lower():
                            # زيادة وزن ADX
                            self.memory_engine._learning_weights['adx_weight'] = min(
                                0.25, 
                                self.memory_engine._learning_weights.get('adx_weight', 0.10) * 1.05
                            )
                        elif 'rsi' in factor.lower():
                            self.memory_engine._learning_weights['rsi_weight'] = min(
                                0.25,
                                self.memory_engine._learning_weights.get('rsi_weight', 0.12) * 1.05
                            )
                
                elif lesson_type == 'confidence_loss':
                    # تقليل الأوزان المرتبطة بعوامل نقص الثقة
                    for factor in key_factors:
                        if 'low_volume' in factor.lower() or 'volume' in factor.lower():
                            self.memory_engine._learning_weights['volume_weight'] = max(
                                0.01,
                                self.memory_engine._learning_weights.get('volume_weight', 0.08) * 0.95
                            )
            
            # حفظ الأوزان المحدثة
            self.memory_engine._save_learning_weights()
            
        except Exception as e:
            logger.warning(f"⚠️ [Dream] فشل تحديث الأوزان من الدروس: {e}")
    
    def _run_calibration(self):
        """
        ✅ تشغيل عملية المعايرة (Calibration) لتحسين دقة التوقعات
        """
        try:
            # محاولة استيراد _update_calibration من النطاق العام
            calibration_func = None
            try:
                from main import _update_calibration as calibration_func
            except ImportError:
                if '_update_calibration' in globals():
                    calibration_func = globals()['_update_calibration']
                else:
                    logger.debug("ℹ️ [Dream] _update_calibration غير متوفرة")
                    return
            
            if calibration_func:
                calibration_func()
                logger.info("📊 [Dream] تم تنفيذ المعايرة بنجاح")
                
        except Exception as e:
            logger.warning(f"⚠️ [Dream] فشل تشغيل المعايرة: {e}")
    
    def _generate_dream_summary(self, stages: List[dict], lessons: List[dict], patterns: List[dict]) -> str:
        """توليد ملخص الحلم"""
        parts = []
        parts.append(f"حلم استمر {len(stages)} مراحل")
        if lessons:
            parts.append(f"استخلص {len(lessons)} درساً")
        if patterns:
            parts.append(f"اكتشف {len(patterns)} نمطاً")
        return " - ".join(parts)
