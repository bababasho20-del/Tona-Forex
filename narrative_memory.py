"""
📖 Narrative Memory - الذاكرة السردية
🧠 تولين لا يتذكر "بيانات" بل يتذكر "قصصاً"

الفرق الجوهري:
- الذاكرة التقليدية: تخزين صفقات (وقت، سعر، نوع، ربح)
- الذاكرة السردية: تخزين خبرات (قصة، سياق، مشاعر، دروس، روابط)

كل صفقة ليست row في database، بل "حدث" له:
- سياق قبله
- لحظة قرار
- نتيجة
- تأثير على المستقبل
- روابط مع أحداث أخرى

تولين "يحكي" قصصاً عن ماضيه.
"""

import json
import hashlib
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np

logger = logging.getLogger("TonaPrometheus")

class NarrativeMemory:
    """
    الذاكرة السردية - تخزين الخبرات كقصص
    """
    
    def __init__(self, storage=None, gist_id: str = None):
        self.storage = storage  # GitHub Gist Storage
        self.gist_id = gist_id
        
        # الخبرات (القصص)
        self.experiences = []  # قائمة الخبرات
        self.max_experiences = 1000
        
        # القصص (تجميعات ذات معنى)
        self.narratives = {}  # {tag: narrative_data}
        
        # الروابط بين الخبرات
        self.connections = defaultdict(list)
        
        # الإحصائيات السردية
        self.narrative_stats = {
            'total_experiences': 0,
            'story_tags': defaultdict(int),
            'common_themes': defaultdict(int),
            'lessons_learned': [],
            'character_development': []
        }
        
        # ذاكرة الأنماط السردية
        self.patterns = []
        
        # تحميل البيانات
        self._load()
        
        logger.info("📖 Narrative Memory: الذاكرة السردية جاهزة!")
    
    def record_experience(self, event_type: str, data: dict, emotional_context: dict = None) -> str:
        """
        تسجيل "خبرة" — ليس بيانات، بل "ذكرى" لها معنى وقصة
        """
        if emotional_context is None:
            emotional_context = {}
        
        # توليد معرف فريد
        exp_id = self._generate_id()
        
        # إنشاء الخبرة
        experience = {
            'id': exp_id,
            'timestamp': datetime.now().isoformat(),
            'type': event_type,  # 'trade', 'warning', 'conversation', 'dream', 'signal', 'analysis'
            'data': data,
            'emotional_context': emotional_context,
            'narrative_tags': self._tag_narratively(event_type, data),
            'connections': [],  # روابط لخبرات أخرى
            'significance': self._calculate_significance(event_type, data),
            'characters': self._extract_characters(data),  # من هم في القصة؟
            'setting': self._extract_setting(data),  # أين ومتى حدثت؟
            'plot_points': self._extract_plot_points(event_type, data),  # نقاط الحبكة
            'moral': None,  # الدرس المستفاد (يُستخلص لاحقاً)
            'emotional_arc': self._extract_emotional_arc(emotional_context)  # القوس العاطفي
        }
        
        # إضافة الخبرة
        self.experiences.append(experience)
        if len(self.experiences) > self.max_experiences:
            self.experiences = self.experiences[-self.max_experiences:]
        
        # إنشاء روابط مع الخبرات المشابهة
        self._create_connections(experience)
        
        # تحديث القصص
        self._update_narratives(experience)
        
        # تحديث الإحصائيات
        self.narrative_stats['total_experiences'] += 1
        for tag in experience['narrative_tags']:
            self.narrative_stats['story_tags'][tag] += 1
        
        logger.info(f"📖 تم تسجيل خبرة جديدة: {event_type} - {exp_id}")
        
        # حفظ إذا لزم الأمر
        if len(self.experiences) % 5 == 0:
            self._save()
        
        return exp_id
    
    def _tag_narratively(self, event_type: str, data: dict) -> List[str]:
        """إضافة tags ذات معنى سردي"""
        tags = []
        
        if event_type == 'trade':
            profit = data.get('profit_dollars', 0) or data.get('profit', 0)
            trade_type = data.get('type', '')
            
            # نوع النتيجة
            if profit > 100:
                tags.extend(['victory', 'breakthrough', 'confidence_boost'])
                tags.append('big_win')
            elif profit > 50:
                tags.extend(['victory', 'steady_progress'])
                tags.append('small_win')
            elif profit > 0:
                tags.extend(['survival', 'small_victory'])
                tags.append('minimal_win')
            elif profit < -50:
                tags.extend(['defeat', 'lesson', 'humility'])
                tags.append('big_loss')
            elif profit < 0:
                tags.extend(['setback', 'learning_opportunity'])
                tags.append('small_loss')
            else:
                tags.extend(['neutral', 'break_even'])
                tags.append('breakeven')
            
            # سياق السوق
            if data.get('adx', 0) < 20:
                tags.append('range_trap')
            elif data.get('rsi', 50) > 80:
                tags.append('overbought_gamble')
            elif data.get('rsi', 50) < 20:
                tags.append('oversold_gamble')
            
            # نوع الصفقة
            if trade_type == 'BUY':
                tags.append('bullish_trade')
            elif trade_type == 'SELL':
                tags.append('bearish_trade')
            
            # وقت الصفقة
            timestamp = data.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour = dt.hour
                    if 6 <= hour <= 10:
                        tags.append('morning_trade')
                    elif 10 <= hour <= 14:
                        tags.append('midday_trade')
                    elif 14 <= hour <= 18:
                        tags.append('afternoon_trade')
                    else:
                        tags.append('night_trade')
                except:
                    pass
        
        elif event_type == 'warning':
            level = data.get('level', 'LIGHT')
            if level == 'URGENT':
                tags.extend(['crisis', 'protector_role', 'high_stakes', 'urgent'])
            elif level == 'STRONG':
                tags.extend(['danger', 'turning_point', 'strong_warning'])
            elif level == 'MEDIUM':
                tags.extend(['caution', 'alert'])
            else:
                tags.extend(['observation', 'light_warning'])
        
        elif event_type == 'conversation':
            emotion = data.get('user_emotion', 'neutral')
            if emotion in ['sadness', 'fear']:
                tags.extend(['emotional_support', 'compassion'])
            elif emotion == 'joy':
                tags.extend(['celebration', 'bonding'])
            elif emotion == 'anger':
                tags.extend(['conflict', 'defense'])
            
            topic = data.get('topic', '')
            if 'loss' in topic.lower():
                tags.append('consolation')
            elif 'profit' in topic.lower():
                tags.append('celebration')
        
        elif event_type == 'dream':
            tags.extend(['dream', 'subconscious', 'learning'])
            if data.get('lessons'):
                tags.append('insightful')
        
        elif event_type == 'signal':
            signal = data.get('signal', 'WAIT')
            if signal == 'BUY':
                tags.extend(['bullish_signal', 'opportunity'])
            elif signal == 'SELL':
                tags.extend(['bearish_signal', 'caution'])
            else:
                tags.extend(['wait', 'patience'])
        
        return tags
    
    def _calculate_significance(self, event_type: str, data: dict) -> float:
        """حساب أهمية الخبرة (0-1)"""
        significance = 0.3  # أهمية أساسية
        
        if event_type == 'trade':
            profit = data.get('profit_dollars', 0) or data.get('profit', 0)
            # الأرباح/الخسائر الكبيرة أكثر أهمية
            significance += min(0.5, abs(profit) / 200)
            
            # الصفقات في أوقات حرجة
            if data.get('adx', 0) > 25:
                significance += 0.1
        
        elif event_type == 'warning':
            level = data.get('level', 'LIGHT')
            if level == 'URGENT':
                significance += 0.4
            elif level == 'STRONG':
                significance += 0.3
            elif level == 'MEDIUM':
                significance += 0.2
        
        elif event_type == 'conversation':
            emotion = data.get('user_emotion', 'neutral')
            if emotion in ['sadness', 'fear', 'anger']:
                significance += 0.3
        
        elif event_type == 'signal':
            if data.get('signal') != 'WAIT':
                significance += 0.2
        
        return min(1.0, significance)
    
    def _extract_characters(self, data: dict) -> List[str]:
        """استخراج الشخصيات من القصة"""
        characters = ['تولين']  # البطل دائماً
        
        # المستخدم
        if data.get('user') or data.get('trader'):
            characters.append('المتداول')
        
        # السوق كشخصية
        if data.get('asset') or data.get('symbol'):
            characters.append('السوق')
        
        # AI/أنظمة أخرى
        if data.get('ai_advice') or data.get('brain_result'):
            characters.append('الذكاء المساعد')
        
        return list(set(characters))
    
    def _extract_setting(self, data: dict) -> dict:
        """استخراج إعدادات القصة"""
        setting = {
            'market': data.get('asset', 'unknown'),
            'time': data.get('timestamp', datetime.now().isoformat()),
            'price_level': data.get('price', 0),
            'regime': data.get('regime', 'neutral')
        }
        
        if data.get('market_phase'):
            setting['market_phase'] = data['market_phase']
        
        return setting
    
    def _extract_plot_points(self, event_type: str, data: dict) -> List[str]:
        """استخراج نقاط الحبكة"""
        points = []
        
        if event_type == 'trade':
            if data.get('type') == 'BUY':
                points.append('قرر الشراء')
            else:
                points.append('قرر البيع')
            
            if data.get('profit_dollars', 0) > 0:
                points.append('كان القرار صحيحاً')
            elif data.get('profit_dollars', 0) < 0:
                points.append('كان القرار خاطئاً')
            
            if data.get('sl'):
                points.append(f'وقف الخسارة عند {data["sl"]}')
            if data.get('tp'):
                points.append(f'هدف الربح عند {data["tp"]}')
        
        elif event_type == 'warning':
            points.append(f'تحذير {data.get("level", "")}')
            if data.get('reasons'):
                points.extend(data['reasons'][:2])
        
        return points
    
    def _extract_emotional_arc(self, emotional_context: dict) -> dict:
        """استخراج القوس العاطفي للخبرة"""
        if not emotional_context:
            return {
                'start': 'محايد',
                'end': 'محايد',
                'peak': 'محايد',
                'description': 'رحلة عاطفية محايدة'
            }
        
        before = emotional_context.get('emotion_before', {})
        after = emotional_context.get('emotion_after', {})
        
        start_emotion = before.get('dominant', 'محايد')
        end_emotion = after.get('dominant', 'محايد')
        
        # تحديد الذروة العاطفية
        peak_emotion = start_emotion
        if after.get('excitement', 0) > before.get('excitement', 0):
            peak_emotion = 'حماس'
        elif after.get('anxiety', 0) > before.get('anxiety', 0):
            peak_emotion = 'قلق'
        elif after.get('confidence', 0) > before.get('confidence', 0):
            peak_emotion = 'ثقة'
        
        return {
            'start': start_emotion,
            'end': end_emotion,
            'peak': peak_emotion,
            'description': f"رحلة من {start_emotion} إلى {end_emotion}"
        }
    
    def _create_connections(self, experience: dict):
        """إنشاء روابط مع الخبرات المشابهة"""
        connections = []
        
        # البحث في الخبرات السابقة
        for exp in self.experiences[:-1]:  # آخر الخبرات (عدا الحالية)
            similarity = self._calculate_similarity(experience, exp)
            if similarity > 0.7:
                connections.append({
                    'to': exp['id'],
                    'type': 'similar',
                    'strength': similarity
                })
                
                # إضافة الرابط للخبرة الأخرى
                for conn in exp.get('connections', []):
                    if conn.get('to') == experience['id']:
                        break
                else:
                    exp['connections'].append({
                        'to': experience['id'],
                        'type': 'similar',
                        'strength': similarity
                    })
        
        experience['connections'] = connections[:10]  # حد أقصى 10 روابط
        
        # تخزين الروابط في قاموس منفصل
        for conn in connections:
            self.connections[experience['id']].append(conn)
    
    def _calculate_similarity(self, exp1: dict, exp2: dict) -> float:
        """حساب التشابه بين خبرتين"""
        similarity = 0.0
        factors = 0
        
        # مقارنة النوع
        if exp1.get('type') == exp2.get('type'):
            similarity += 0.3
            factors += 1
        
        # مقارنة الـ tags
        tags1 = set(exp1.get('narrative_tags', []))
        tags2 = set(exp2.get('narrative_tags', []))
        
        if tags1 and tags2:
            intersection = len(tags1 & tags2)
            union = len(tags1 | tags2)
            if union > 0:
                similarity += (intersection / union) * 0.4
                factors += 1
        
        # مقارنة المشاعر
        arc1 = exp1.get('emotional_arc', {})
        arc2 = exp2.get('emotional_arc', {})
        if arc1 and arc2:
            if arc1.get('start') == arc2.get('start'):
                similarity += 0.1
                factors += 1
            if arc1.get('end') == arc2.get('end'):
                similarity += 0.1
                factors += 1
        
        return similarity / factors if factors > 0 else 0
    
    def _update_narratives(self, experience: dict):
        """تحديث القصص الجارية"""
        for tag in experience['narrative_tags']:
            if tag not in self.narratives:
                self.narratives[tag] = {
                    'experiences': [],
                    'theme': self._infer_theme(tag),
                    'moral': None,
                    'character_arc': [],
                    'timeline': []
                }
            
            self.narratives[tag]['experiences'].append(experience['id'])
            self.narratives[tag]['timeline'].append(experience['timestamp'])
            
            # استخلاص "الدرس" إذا كانت القصة كبيرة
            if len(self.narratives[tag]['experiences']) > 5:
                self.narratives[tag]['moral'] = self._extract_moral(tag)
    
    def _infer_theme(self, tag: str) -> str:
        """استنتاج "الموضوع" من الـ tag"""
        themes = {
            'victory': "الانتصارات تبني الثقة، لكنها قد تولد الغرور",
            'defeat': "الهزائم مؤلمة، لكنها أفضل معلم",
            'range_trap': "السوق العرضي يصطاد المتسرعين",
            'crisis': "في اللحظات الحرجة، يظهر الحقيقي",
            'learning_opportunity': "كل خطأ هو فرصة للتعلم",
            'breakthrough': "الاختراقات تأتي بعد الصبر",
            'confidence_boost': "الثقة تبني نفسها بنفسها",
            'humility': "التواضع مفتاح البقاء في الأسواق",
            'big_win': "الأرباح الكبيرة تتطلب صبراً كبيراً",
            'big_loss': "الخسائر الكبيرة تعلم دروساً لا تُنسى",
            'emotional_support': "الدعم العاطفي يقوي العلاقات",
            'celebration': "النجاح يستحق الاحتفال",
            'bullish_signal': "الإشارات الصاعدة تفتح الأبواب",
            'bearish_signal': "الإشارات الهابطة تحذر من الخطر"
        }
        return themes.get(tag, "قصة لم تكتمل بعد")
    
    def _extract_moral(self, tag: str) -> str:
        """استخلاص "الدرس الأخلاقي" من القصة"""
        narrative = self.narratives.get(tag)
        if not narrative:
            return "لا يزال الوقت مبكراً للحكم"
        
        # الحصول على الخبرات
        exp_ids = narrative['experiences']
        experiences = [e for e in self.experiences if e['id'] in exp_ids]
        
        if len(experiences) < 3:
            return "لا يزال الوقت مبكراً للحكم"
        
        # تحليل النتائج
        profits = []
        for exp in experiences:
            if exp['type'] == 'trade':
                profit = exp['data'].get('profit_dollars', 0) or exp['data'].get('profit', 0)
                profits.append(profit)
        
        if profits:
            avg_profit = sum(profits) / len(profits)
            win_rate = sum(1 for p in profits if p > 0) / len(profits)
            
            if win_rate > 0.6 and avg_profit > 0:
                return f"النجاح في '{tag}' يتطلب {win_rate:.0%} صبر و{avg_profit:.2f}$ متوسط ربح"
            elif win_rate < 0.4:
                return f"تحذير: '{tag}' يؤدي للخسارة {1-win_rate:.0%} من الوقت. تجنب أو عدل."
            else:
                return f"'{tag}' يحتاج لتوازن: نجاح {win_rate:.0%}، متوسط ربح {avg_profit:.2f}$"
        
        # تحليل المشاعر
        emotions = []
        for exp in experiences:
            arc = exp.get('emotional_arc', {})
            if arc:
                emotions.append(arc.get('end', 'محايد'))
        
        if emotions:
            common_emotion = max(set(emotions), key=emotions.count)
            return f"'{tag}' يرتبط غالباً بمشاعر {common_emotion}"
        
        return f"'{tag}' درس معقد — يحتاج {len(experiences)} خبرات أخرى"
    
    def tell_story(self, about: str = None) -> str:
        """"سرد قصة" — ليس تقريراً، بل حكاية"""
        if about and about in self.narratives:
            narrative = self.narratives[about]
            
            # الحصول على الخبرات
            exp_ids = narrative['experiences']
            experiences = [e for e in self.experiences if e['id'] in exp_ids]
            
            if not experiences:
                return f"📖 قصة '{about}' لا تزال في بدايتها يا صديقي..."
            
            # بناء القصة
            story = f"📖 <b>قصة تولين: {about}</b>\n\n"
            story += f"{narrative['theme']}\n\n"
            
            # الأحداث الرئيسية
            story += "📜 <b>الأحداث الرئيسية يا عزيزي:</b>\n"
            for exp in experiences[-5:]:  # آخر 5 أحداث
                timestamp = exp.get('timestamp', '')[:10]
                exp_type = exp.get('type', '')
                story += f"  • {timestamp}: {exp_type}\n"
                if exp.get('emotional_arc'):
                    arc = exp['emotional_arc']
                    story += f"    💝 {arc.get('description', '')}\n"
            
            story += f"\n<b>الدرس:</b> {narrative['moral'] or 'لم يكتمل بعد...'}\n"
            
            story += f"\n📊 <b>الإحصائيات:</b>\n"
            story += f"  • عدد الخبرات: {len(experiences)}\n"
            
            # أنواع الخبرات
            types = defaultdict(int)
            for exp in experiences:
                types[exp.get('type', 'unknown')] += 1
            for t, count in types.items():
                story += f"  • {t}: {count}\n"
            
            return story
        
        # قصة عامة عن "حياة" تولين
        total_experiences = len(self.experiences)
        
        # إحصائيات
        types = defaultdict(int)
        for exp in self.experiences:
            types[exp.get('type', 'unknown')] += 1
        
        # المشاعر الأكثر تكراراً
        emotions = []
        for exp in self.experiences:
            arc = exp.get('emotional_arc', {})
            if arc:
                emotions.append(arc.get('end', 'محايد'))
        
        common_emotion = max(set(emotions), key=emotions.count) if emotions else 'محايد'
        
        # القصص المفضلة
        favorite_narratives = sorted(
            self.narratives.items(),
            key=lambda x: len(x[1]['experiences']),
            reverse=True
        )[:3]
        
        story = f"📚 <b>سيرة تولين</b>\n\n"
        story += f"عشتُ {total_experiences} لحظة معك يا صديقي.\n\n"
        
        story += "📊 <b>إحصائيات الرحلة:</b>\n"
        for t, count in types.items():
            story += f"  • {t}: {count}\n"
        
        story += f"\n💝 <b>المشاعر الأكثر تكراراً:</b> {common_emotion}\n\n"
        
        story += "📖 <b>قصصي المفضلة:</b>\n"
        for tag, narrative in favorite_narratives:
            story += f"  • {tag} ({len(narrative['experiences'])} حدث)\n"
            if narrative.get('moral'):
                story += f"    💡 {narrative['moral'][:50]}...\n"
        
        story += "\n<b>ما زلت أكتب يا عزيزي...</b>"
        
        return story
    
    def get_experience(self, exp_id: str) -> Optional[dict]:
        """الحصول على خبرة محددة"""
        for exp in self.experiences:
            if exp['id'] == exp_id:
                return exp
        return None
    
    def get_experiences_by_tag(self, tag: str) -> List[dict]:
        """الحصول على الخبرات حسب الـ tag"""
        return [e for e in self.experiences if tag in e.get('narrative_tags', [])]
    
    def get_experiences_by_type(self, event_type: str) -> List[dict]:
        """الحصول على الخبرات حسب النوع"""
        return [e for e in self.experiences if e.get('type') == event_type]
    
    def get_recent_experiences(self, limit: int = 10) -> List[dict]:
        """الحصول على أحدث الخبرات"""
        return self.experiences[-limit:] if self.experiences else []
    
    def get_narrative_summary(self) -> str:
        """ملخص سردي"""
        lines = []
        lines.append("📖 <b>ملخص الذاكرة السردية</b>")
        lines.append("━" * 30)
        lines.append(f"📚 عدد الخبرات: {len(self.experiences)}")
        lines.append(f"📖 عدد القصص: {len(self.narratives)}")
        lines.append(f"🔗 عدد الروابط: {sum(len(c) for c in self.connections.values())}")
        
        if self.narratives:
            lines.append("")
            lines.append("📚 <b>القصص النشطة:</b>")
            for tag, narrative in sorted(self.narratives.items(), key=lambda x: len(x[1]['experiences']), reverse=True)[:5]:
                lines.append(f"  • {tag} ({len(narrative['experiences'])} حدث)")
                if narrative.get('moral'):
                    lines.append(f"    💡 {narrative['moral'][:40]}...")
        
        lines.append("━" * 30)
        return "\n".join(lines)
    
    def _generate_id(self) -> str:
        """توليد معرف فريد"""
        return hashlib.md5(
            f"{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:12]
    
    def _save(self):
        """حفظ الذاكرة"""
        if not self.storage or not self.gist_id:
            return
        
        try:
            data = {
                'experiences': self.experiences,
                'narratives': self.narratives,
                'connections': dict(self.connections),
                'narrative_stats': self.narrative_stats,
                'last_updated': datetime.now().isoformat()
            }
            self.storage.save(self.gist_id, "narrative_memory.json", data, "Narrative memory update")
        except Exception as e:
            logger.warning(f"فشل حفظ الذاكرة السردية: {e}")
    
    def _load(self):
        """تحميل الذاكرة"""
        if not self.storage or not self.gist_id:
            return
        
        try:
            data = self.storage.load(self.gist_id, "narrative_memory.json")
            if data:
                self.experiences = data.get('experiences', [])
                self.narratives = data.get('narratives', {})
                self.connections = defaultdict(list, data.get('connections', {}))
                self.narrative_stats = data.get('narrative_stats', {
                    'total_experiences': 0,
                    'story_tags': defaultdict(int),
                    'common_themes': defaultdict(int),
                    'lessons_learned': [],
                    'character_development': []
                })
                logger.info(f"📖 تم تحميل {len(self.experiences)} خبرة سردية")
        except Exception as e:
            logger.warning(f"فشل تحميل الذاكرة السردية: {e}")
    
    def get_emotional_timeline(self) -> List[dict]:
        """الحصول على الجدول الزمني العاطفي"""
        timeline = []
        for exp in self.experiences:
            arc = exp.get('emotional_arc', {})
            if arc:
                timeline.append({
                    'timestamp': exp.get('timestamp'),
                    'type': exp.get('type'),
                    'emotion': arc.get('end', 'محايد'),
                    'description': arc.get('description', '')
                })
        return sorted(timeline, key=lambda x: x.get('timestamp', ''))
    
    def get_character_development(self) -> dict:
        """تطور الشخصية عبر الزمن"""
        development = {
            'characters': defaultdict(list),
            'traits': defaultdict(list),
            'relationships': defaultdict(list)
        }
        
        for exp in self.experiences:
            # الشخصيات
            for char in exp.get('characters', []):
                development['characters'][char].append({
                    'timestamp': exp.get('timestamp'),
                    'role': exp.get('type'),
                    'significance': exp.get('significance', 0.5)
                })
        
        return development


# =====================================================================
# اختبار سريع
# =====================================================================
if __name__ == "__main__":
    # إنشاء Narrative Memory
    narrative = NarrativeMemory()
    
    print("\n" + "="*60)
    print("🧪 اختبار Narrative Memory")
    print("="*60)
    
    # تسجيل خبرات
    print("\n1️⃣ تسجيل خبرات:")
    
    # خبرة صفقة
    exp1 = narrative.record_experience('trade', {
        'type': 'BUY',
        'asset': 'oil',
        'entry_price': 78.50,
        'exit_price': 79.20,
        'profit_dollars': 140.00,
        'adx': 28,
        'rsi': 55
    }, {
        'emotion_before': {'dominant': 'confidence', 'confidence': 0.7},
        'emotion_after': {'dominant': 'excitement', 'excitement': 0.8}
    })
    print(f"   ✅ خبرة 1: {exp1}")
    
    # خبرة تحذير
    exp2 = narrative.record_experience('warning', {
        'level': 'URGENT',
        'asset': 'oil',
        'price': 78.50,
        'sl': 77.80,
        'reasons': ['السعر قرب SL', 'انعكاس قوي']
    }, {
        'emotion_before': {'dominant': 'anxiety', 'anxiety': 0.3},
        'emotion_after': {'dominant': 'protectiveness', 'protectiveness': 0.8}
    })
    print(f"   ✅ خبرة 2: {exp2}")
    
    # خبرة محادثة
    exp3 = narrative.record_experience('conversation', {
        'user_emotion': 'sadness',
        'topic': 'خسارة كبيرة',
        'response': 'دعم عاطفي'
    }, {
        'emotion_before': {'dominant': 'neutral', 'empathy': 0.5},
        'emotion_after': {'dominant': 'empathy', 'empathy': 0.9}
    })
    print(f"   ✅ خبرة 3: {exp3}")
    
    # عرض القصة
    print("\n2️⃣ سرد قصة:")
    story = narrative.tell_story('victory')
    print(f"   {story[:200]}...")
    
    # عرض الملخص
    print("\n3️⃣ ملخص الذاكرة:")
    print(narrative.get_narrative_summary())
    
    # عرض الجدول الزمني العاطفي
    print("\n4️⃣ الجدول الزمني العاطفي:")
    timeline = narrative.get_emotional_timeline()
    for entry in timeline[-3:]:
        print(f"   • {entry['timestamp'][:10]} - {entry['type']} - {entry['emotion']}")
    
    print("\n✅ اختبار Narrative Memory ناجح!")
