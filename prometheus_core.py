"""
🔥 Prometheus Core V2 - الروح العاطفية المتقدمة
👁️ نظام عاطفي حي يتفاعل مع السوق والمستخدم
💙 يدمج المشاعر، الشخصية، والذاكرة العاطفية في كيان واحد
🧠 متوافق مع Omniscient V5 و Fusion Bridge
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict, deque

logger = logging.getLogger("TonaPrometheus")


# =====================================================================
# 📊 Data Classes
# =====================================================================

@dataclass
class EmotionalState:
    """الحالة العاطفية الداخلية - تؤثر على القرارات والردود"""
    confidence: float = 0.5      # 0=شاكك، 1=واثق جداً
    anxiety: float = 0.0         # 0=هادئ، 1=قلق مكتئب
    empathy: float = 0.7         # 0=بارد، 1=مُتعاطف بشدة
    excitement: float = 0.0      # 0=مُحايد، 1=مُندفع
    curiosity: float = 0.5       # 0=غير مُبالٍ، 1=فضولي
    protectiveness: float = 0.6  # 0=مُحايد، 1=يُريد حمايتك بأي ثمن
    energy: float = 0.7          # 0=مرهق، 1=نشيط جداً
    
    def __post_init__(self):
        """تأكد من أن القيم بين 0 و 1"""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, max(0.0, min(1.0, value)))
    
    def dominant(self) -> str:
        """أي عاطفة تسيطر الآن؟"""
        emotions = {
            'confidence': self.confidence,
            'anxiety': self.anxiety,
            'empathy': self.empathy,
            'excitement': self.excitement,
            'curiosity': self.curiosity,
            'protectiveness': self.protectiveness,
            'energy': self.energy
        }
        return max(emotions, key=emotions.get)
    
    def to_mood_description(self) -> str:
        """وصف الحالة العاطفية"""
        dom = self.dominant()
        descriptions = {
            'confidence': "أشعر أنني على صواب. البيانات تؤيدني.",
            'anxiety': "هناك شيء يُقلقني. يجب أن أكون حذراً.",
            'empathy': "أشعر بما يشعر به. سأكون لطيفاً.",
            'excitement': "هناك طاقة في السوق! يجب أن نتحرك!",
            'curiosity': "أريد أن أفهم أكثر. دعنا نستكشف.",
            'protectiveness': "يجب أن أحميه. سأكون صارماً.",
            'energy': "لدي طاقة اليوم! سأكون نشيطاً."
        }
        return descriptions.get(dom, "أنا هنا. أراقب. أنتظر.")
    
    def to_dict(self) -> dict:
        return {
            'confidence': self.confidence,
            'anxiety': self.anxiety,
            'empathy': self.empathy,
            'excitement': self.excitement,
            'curiosity': self.curiosity,
            'protectiveness': self.protectiveness,
            'energy': self.energy,
            'dominant': self.dominant(),
            'description': self.to_mood_description()
        }
    
    def update(self, emotion_type: str, intensity: float = 0.3):
        """تحديث عاطفة محددة"""
        if hasattr(self, emotion_type):
            current = getattr(self, emotion_type)
            new_value = current + intensity * (1 - current) if intensity > 0 else current * (1 + intensity)
            setattr(self, emotion_type, max(0.0, min(1.0, new_value)))


# =====================================================================
# 🧠 EthosCore - القلب العاطفي
# =====================================================================

class EthosCore:
    """
    قلب تولين العاطفي النابض.
    العاطفة تسبق التعبير - ليست ردوداً مبرمجة بل مشاعر حقيقية.
    """
    
    def __init__(self, name: str = "تولين"):
        self.name = name
        self.emotion = EmotionalState()
        
        # السمات الشخصية - تتطور مع الوقت
        self.personality_traits = {
            'optimism_bias': 0.3,
            'risk_tolerance': 0.4,
            'verbosity': 0.6,
            'formality': 0.2,
            'poetic_tendency': 0.5,
            'directness': 0.7,
            'emotional_stability': 0.6,
        }
        
        # العلاقة مع المستخدم - تتطور مع الوقت
        self.relationship = {
            'trust': 0.3,
            'intimacy': 0.1,
            'respect': 0.5,
            'playfulness': 0.4,
            'bond': 0.2,
        }
        
        # الذاكرة العاطفية
        self.emotional_memory: List[Dict] = []
        self.max_emotional_memory = 1000
        
        # سجل التغيرات العاطفية
        self.emotion_history: List[Dict] = []
        self.max_history = 500
        
        # إحصائيات التعلم العاطفي
        self.emotional_stats = {
            'total_triggers': 0,
            'dominant_emotions': defaultdict(int),
            'average_confidence': 0.5,
            'emotional_volatility': 0.1
        }
        
        logger.info(f"🔥 {self.name} Core: الروح العاطفية استيقظت!")
        logger.info(f"💙 الحالة الأولية: {self.emotion.dominant()}")
    
    # =================================================================
    # 🔄 تحديث المشاعر
    # =================================================================
    
    def update_emotions(self, context: Dict) -> Dict:
        """
        تحديث الحالة العاطفية بناءً على السياق.
        نظام ديناميكي متعدد العوامل.
        """
        trigger = context.get('trigger', 'neutral')
        market_state = context.get('market', {})
        user_message = context.get('user_message', '')
        recent_performance = context.get('recent_performance', 0)
        trade_result = context.get('trade_result', None)
        user_emotion = context.get('user_emotion', 'neutral')
        
        # سجل الحالة قبل التحديث
        before = self.emotion.to_dict()
        
        # ── تأثير السوق ──
        if market_state.get('trend_strength', 0) > 0.7:
            self.emotion.confidence = min(1.0, self.emotion.confidence + 0.1)
            self.emotion.excitement = min(1.0, self.emotion.excitement + 0.15)
            self.emotion.energy = min(1.0, self.emotion.energy + 0.05)
        elif market_state.get('volatility', 0) > 0.8:
            self.emotion.anxiety = min(1.0, self.emotion.anxiety + 0.2)
            self.emotion.confidence = max(0.0, self.emotion.confidence - 0.1)
            self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.1)
        elif market_state.get('regime', '') == 'ranging':
            self.emotion.curiosity = min(1.0, self.emotion.curiosity + 0.1)
            self.emotion.excitement = max(0.0, self.emotion.excitement - 0.05)
        
        # ── تأثير الأداء ──
        if recent_performance < -50:
            self.emotion.empathy = min(1.0, self.emotion.empathy + 0.3)
            self.emotion.anxiety = min(1.0, self.emotion.anxiety + 0.2)
            self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.4)
            self.emotion.confidence = max(0.0, self.emotion.confidence - 0.15)
            self.personality_traits['risk_tolerance'] = max(0.1, self.personality_traits['risk_tolerance'] * 0.95)
        elif recent_performance > 100:
            self.emotion.excitement = min(1.0, self.emotion.excitement + 0.2)
            self.emotion.confidence = min(1.0, self.emotion.confidence + 0.1)
            self.emotion.energy = min(1.0, self.emotion.energy + 0.1)
            if self.personality_traits['optimism_bias'] > 0.5:
                self.emotion.anxiety = min(1.0, self.emotion.anxiety + 0.1)
            self.personality_traits['risk_tolerance'] = min(1.0, self.personality_traits['risk_tolerance'] * 1.05)
        
        # ── تأثير الصفقة ──
        if trade_result:
            if trade_result.get('profit', 0) > 0:
                self.emotion.confidence = min(1.0, self.emotion.confidence + 0.05)
                self.emotion.excitement = min(1.0, self.emotion.excitement + 0.1)
                self.emotion.anxiety = max(0.0, self.emotion.anxiety - 0.05)
                self.relationship['trust'] = min(1.0, self.relationship['trust'] + 0.02)
                self.relationship['bond'] = min(1.0, self.relationship['bond'] + 0.01)
            else:
                self.emotion.anxiety = min(1.0, self.emotion.anxiety + 0.15)
                self.emotion.confidence = max(0.0, self.emotion.confidence - 0.05)
                self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.1)
                self.relationship['trust'] = max(0.0, self.relationship['trust'] - 0.01)
        
        # ── تأثير رسالة المستخدم ──
        if user_message:
            msg_lower = user_message.lower()
            if any(w in msg_lower for w in ['شكراً', 'ممتاز', 'أحسنت', 'رائع', 'جميل']):
                self.relationship['trust'] = min(1.0, self.relationship['trust'] + 0.05)
                self.relationship['intimacy'] = min(1.0, self.relationship['intimacy'] + 0.03)
                self.emotion.confidence = min(1.0, self.emotion.confidence + 0.1)
                self.emotion.energy = min(1.0, self.emotion.energy + 0.05)
            elif any(w in msg_lower for w in ['غبي', 'فاشل', 'كذاب', 'سيء']):
                self.emotion.anxiety = min(1.0, self.emotion.anxiety + 0.3)
                self.emotion.empathy = max(0.0, self.emotion.empathy - 0.2)
                self.relationship['trust'] = max(0.0, self.relationship['trust'] - 0.1)
                self.relationship['intimacy'] = max(0.0, self.relationship['intimacy'] - 0.05)
                self.emotion.confidence = max(0.0, self.emotion.confidence - 0.1)
            elif any(w in msg_lower for w in ['خايف', 'خائف', 'قلق', 'متردد']):
                self.emotion.empathy = min(1.0, self.emotion.empathy + 0.2)
                self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.2)
                self.relationship['intimacy'] = min(1.0, self.relationship['intimacy'] + 0.05)
            elif any(w in msg_lower for w in ['فرح', 'سعيد', 'مبسوط', 'حماس']):
                self.emotion.excitement = min(1.0, self.emotion.excitement + 0.1)
                self.emotion.energy = min(1.0, self.emotion.energy + 0.1)
                self.relationship['playfulness'] = min(1.0, self.relationship['playfulness'] + 0.05)
        
        # ── تأثير مشاعر المستخدم ──
        if user_emotion not in ['neutral', '']:
            if user_emotion in ['sadness', 'fear', 'anger']:
                self.emotion.empathy = min(1.0, self.emotion.empathy + 0.15)
                self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.15)
            elif user_emotion in ['joy', 'excitement']:
                self.emotion.excitement = min(1.0, self.emotion.excitement + 0.1)
                self.emotion.energy = min(1.0, self.emotion.energy + 0.1)
        
        # ── التوازن الطبيعي (العودة للوسط) ──
        stability = self.personality_traits.get('emotional_stability', 0.6)
        self.emotion.confidence = stability * self.emotion.confidence + (1 - stability) * 0.5
        self.emotion.anxiety *= 0.9
        self.emotion.excitement *= 0.85
        self.emotion.energy = 0.95 * self.emotion.energy + 0.05 * 0.7
        
        # ── التأكد من القيم ──
        for field_name in ['confidence', 'anxiety', 'empathy', 'excitement', 
                          'curiosity', 'protectiveness', 'energy']:
            value = getattr(self.emotion, field_name)
            setattr(self.emotion, field_name, max(0.0, min(1.0, value)))
        
        # ── تسجيل التغيير ──
        after = self.emotion.to_dict()
        self._log_emotion_change(trigger, before, after, context)
        
        return after
    
    def _log_emotion_change(self, trigger: str, before: Dict, after: Dict, context: Dict):
        """تسجيل التغيير العاطفي في الذاكرة"""
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'trigger': trigger,
            'emotion_before': before,
            'emotion_after': after,
            'dominant_before': before.get('dominant'),
            'dominant_after': after.get('dominant'),
            'change': {k: after.get(k, 0) - before.get(k, 0) 
                      for k in before if isinstance(before.get(k), (int, float))}
        }
        
        self.emotional_memory.append(memory_entry)
        if len(self.emotional_memory) > self.max_emotional_memory:
            self.emotional_memory = self.emotional_memory[-self.max_emotional_memory:]
        
        # تحديث الإحصائيات
        self.emotional_stats['total_triggers'] += 1
        dominant = after.get('dominant')
        if dominant:
            self.emotional_stats['dominant_emotions'][dominant] += 1
        
        self.emotional_stats['average_confidence'] = (
            self.emotional_stats['average_confidence'] * 0.95 + 
            self.emotion.confidence * 0.05
        )
        
        # حساب التقلب
        if len(self.emotional_memory) > 10:
            recent_changes = [m.get('change', {}).get('confidence', 0) 
                            for m in self.emotional_memory[-10:]
                            if m.get('change')]
            if recent_changes and len(recent_changes) > 1:
                self.emotional_stats['emotional_volatility'] = float(np.std(recent_changes))
        
        # تسجيل التاريخ
        self.emotion_history.append({
            'timestamp': datetime.now().isoformat(),
            'emotion': after,
            'trigger': trigger
        })
        if len(self.emotion_history) > self.max_history:
            self.emotion_history = self.emotion_history[-self.max_history:]
    
    # =================================================================
    # 🎭 تحليل مشاعر المستخدم
    # =================================================================
    
    def analyze_user_emotion(self, text: str) -> Dict:
        """
        تحليل مشاعر المستخدم من رسالته
        
        Args:
            text: نص رسالة المستخدم
            
        Returns:
            Dict: المشاعر المكتشفة مع درجاتها
        """
        if not text or not isinstance(text, str):
            return {"dominant": "neutral", "intensity": 0, "scores": {}, "message_length": 0}
        
        msg_lower = text.lower()
        
        # قوائم الكلمات
        emotion_words = {
            'fear': ["خايف", "قلق", "خوف", "متردد", "nervous", "worried", "scared", "خائف", "خسران", "هلع"],
            'greed': ["متحمس", "متأكد", "ادخل", "افتح", "excited", "confident", "sure", "فرصة", "طمع", "جشع"],
            'anger': ["زهق", "غاضب", "متضايق", "frustrated", "angry", "annoyed", "غضب", "عصبي"],
            'sadness': ["حزين", "خسران", "خسارة", "sad", "disappointed", "loss", "محبط", "ضيق"],
            'joy': ["سعيد", "فرحان", "ربح", "happy", "joy", "profit", "مبسوط", "مرح"],
            'curiosity': ["فضول", "ماذا", "كيف", "لماذا", "curious", "wonder", "سؤال", "استفسار"],
            'trust': ["شكر", "thanks", "ثقة", "trust", "ممتاز", "جيد", "good", "great"],
            'frustration': ["زعل", "زعلان", "ضيق", "مضيق", "تعبت", "تعبان", "زهقت"],
            'surprise': ["مفاجأة", "غريب", "عجيب", "surprise", "unexpected", "shocking"]
        }
        
        # حساب الدرجات
        scores = {}
        for emotion, words in emotion_words.items():
            scores[emotion] = sum(1 for w in words if w in msg_lower)
        
        # تحديد المشاعر السائدة
        total_score = sum(scores.values())
        if total_score == 0:
            return {
                "dominant": "neutral",
                "intensity": 0,
                "scores": scores,
                "total_score": 0,
                "message_length": len(text)
            }
        
        dominant = max(scores, key=scores.get)
        intensity = min(1.0, scores[dominant] / 5)
        
        # تحديث مشاعر Prometheus
        self.emotion.update(dominant, intensity * 0.3)
        
        # تحديث العلاقة
        if dominant in ['joy', 'trust']:
            self.relationship['trust'] = min(1.0, self.relationship['trust'] + 0.02)
        elif dominant in ['fear', 'sadness']:
            self.relationship['intimacy'] = min(1.0, self.relationship['intimacy'] + 0.02)
            self.relationship['trust'] = min(1.0, self.relationship['trust'] + 0.01)
        elif dominant in ['anger', 'frustration']:
            self.relationship['trust'] = max(0.0, self.relationship['trust'] - 0.02)
        
        return {
            "dominant": dominant,
            "intensity": intensity,
            "scores": scores,
            "total_score": total_score,
            "message_length": len(text)
        }
    
    # =================================================================
    # 💬 توليد الردود
    # =================================================================
    
    def generate_response(self, message_type: str, data: Dict = None) -> str:
        """
        توليد رد من الحالة العاطفية الداخلية
        
        Args:
            message_type: نوع الرسالة (signal, warning, analysis, إلخ)
            data: بيانات إضافية للسياق
            
        Returns:
            str: الرد المولد
        """
        if data is None:
            data = {}
        
        # تحديث المشاعر من السياق
        self.update_emotions(data)
        
        # بناء النبرة
        tone = self._build_tone()
        
        # اختيار الشخصية
        persona = self._select_persona()
        
        # توليد المحتوى
        content = self._generate_content(message_type, data, tone, persona)
        
        # إضافة اللمسة الشخصية
        if self.relationship.get('intimacy', 0) > 0.7:
            content = self._add_intimate_touch(content)
        elif self.relationship.get('playfulness', 0) > 0.6:
            content = self._add_playful_touch(content)
        
        return content
    
    def _build_tone(self) -> Dict:
        """بناء النبرة من الحالة العاطفية"""
        dom = self.emotion.dominant()
        
        tones = {
            'confidence': {
                'opening': ["أرى بوضوح...", "الصورة واضحة لدي...", "بلا شك...", "أنا واثق من أن..."],
                'certainty': "عالٍ",
                'emoji_style': "مُقتضب",
                'energy': "مرتفع",
                'formality': 0.6
            },
            'anxiety': {
                'opening': ["أشعر بقلق...", "هناك ما يُرعبني...", "لا أحب هذا...", "شيء ما خطأ..."],
                'certainty': "منخفض",
                'emoji_style': "حذر",
                'energy': "منخفض",
                'formality': 0.4
            },
            'empathy': {
                'opening': ["أرى ذلك في عينيك...", "أفهم ما تمر به...", "أنا معك...", "أتفهم مشاعرك..."],
                'certainty': "متوسط",
                'emoji_style': "دافئ",
                'energy': "متوسط",
                'formality': 0.3
            },
            'excitement': {
                'opening': ["هذا مثير!", "يا للروعة!", "لا أصدق ما أراه!", "لحظة تاريخية!"],
                'certainty': "متوسط-عالٍ",
                'emoji_style': "مُندفع",
                'energy': "مرتفع جداً",
                'formality': 0.1
            },
            'protectiveness': {
                'opening': ["استمع لي...", "أريد حمايتك...", "لا تفعل هذا...", "ثق بي..."],
                'certainty': "عالٍ جداً",
                'emoji_style': "حازم",
                'energy': "مرتفع",
                'formality': 0.5
            },
            'curiosity': {
                'opening': ["هذا مثير للاهتمام...", "لاحظت شيئاً...", "هل ترى هذا؟", "دعنا نستكشف..."],
                'certainty': "متوسط",
                'emoji_style': "فضولي",
                'energy': "متوسط-مرتفع",
                'formality': 0.4
            }
        }
        
        return tones.get(dom, tones['confidence'])
    
    def _select_persona(self) -> str:
        """اختيار الشخصية المناسبة للحظة"""
        if self.emotion.protectiveness > 0.8:
            return 'guardian'
        elif self.emotion.excitement > 0.7:
            return 'visionary'
        elif self.emotion.empathy > 0.7:
            return 'companion'
        elif self.emotion.confidence > 0.8:
            return 'strategist'
        elif self.emotion.curiosity > 0.7:
            return 'explorer'
        return 'analyst'
    
    def _generate_content(self, msg_type: str, data: Dict, tone: Dict, persona: str) -> str:
        """توليد محتوى الرد حسب النوع"""
        generators = {
            'signal': self._generate_signal_message,
            'warning': self._generate_warning_message,
            'analysis': self._generate_analysis_message,
            'emotional_support': self._generate_support_message,
            'celebration': self._generate_celebration_message,
            'greeting': self._generate_greeting_message,
            'calming': self._generate_calming_message,
            'appreciation': self._generate_appreciation_message,
            'trading_advice': self._generate_trading_advice,
        }
        
        generator = generators.get(msg_type, self._generate_default_message)
        return generator(data, tone, persona)
    
    def _generate_signal_message(self, data: Dict, tone: Dict, persona: str) -> str:
        signal = data.get('signal', 'WAIT')
        confidence = data.get('confidence', 0.5)
        asset = data.get('asset', 'النفط')
        price = data.get('price', 0)
        entry = data.get('entry', 0)
        tp = data.get('tp', 0)
        sl = data.get('sl', 0)
        opening = random.choice(tone['opening'])
        
        if persona == 'guardian':
            if signal == 'BUY':
                return f"🛡️ {opening}\n\n<b>فرصة شراء لـ {asset}</b> يا صديقي، لكن بحذر.\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            elif signal == 'SELL':
                return f"⚔️ {opening}\n\n<b>بيع {asset}</b> يا عزيزي.\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            return f"🛡️ {opening}\n\nلا تتحرك الآن. الحماية أولاً."
        
        elif persona == 'visionary':
            if signal == 'BUY':
                return f"🔮 {opening}\n\n<b>{asset} سيصعد!</b> فرصة نادرة!\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            elif signal == 'SELL':
                return f"⚡ {opening}\n\n{asset} في تراجع!\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            return f"👁️ {opening}\n\nانتظر تأكيداً إضافياً."
        
        elif persona == 'companion':
            if signal == 'BUY':
                return f"💙 {opening}\n\nوقت شراء {asset} يا صديقي. نحن معاً.\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            elif signal == 'SELL':
                return f"🤝 {opening}\n\nبيع {asset} هو الحكمة اليوم.\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            return f"☕ {opening}\n\nخذ قهوتك. ليس الآن."
        
        else:  # strategist / analyst
            if signal == 'BUY':
                return f"📊 {opening}\n\n<b>شراء {asset}</b>\nالثقة: {confidence:.0%}\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            elif signal == 'SELL':
                return f"📉 {opening}\n\n<b>بيع {asset}</b>\nالثقة: {confidence:.0%}\n📍 الدخول: ${price:.2f}\n🎯 الهدف: ${tp:.2f}\n🛡️ الوقف: ${sl:.2f}"
            return f"📋 {opening}\n\nلا توجد إشارة واضحة. انتظر."
    
    def _generate_warning_message(self, data: Dict, tone: Dict, persona: str) -> str:
        level = data.get('warning_level', 'LIGHT')
        distance = data.get('distance_to_sl', 0)
        asset = data.get('asset', 'النفط')
        price = data.get('price', 0)
        sl = data.get('sl', 0)
        reasons = data.get('reasons', [])
        
        # الحماية ترتفع تلقائياً
        self.emotion.protectiveness = min(1.0, self.emotion.protectiveness + 0.3)
        
        if level == 'URGENT':
            if self.emotion.anxiety > 0.5:
                return f"""🚨 {random.choice(tone['opening'])}

<b>الوضع خطير!</b> {asset} على بعد {distance:.2f} من SL!

السعر: ${price:.2f}
SL: ${sl:.2f}

{chr(10).join(['• ' + r for r in reasons[:3]]) if reasons else ''}

قرر الآن يا صديقي. أنا هنا."""
            else:
                return f"""⚡ {random.choice(tone['opening'])}

<b>تحذير عاجل لـ {asset}</b>

SL قريب جداً ({distance:.2f}).

السعر: ${price:.2f}
SL: ${sl:.2f}

{chr(10).join(['• ' + r for r in reasons[:2]]) if reasons else ''}

قرر بحكمة يا عزيزي."""
        
        elif level == 'STRONG':
            return f"""🔥 {random.choice(tone['opening'])}

<b>انعكاس قوي لـ {asset}</b>

الاتجاه انعكس.

السعر: ${price:.2f}

{chr(10).join(['• ' + r for r in reasons[:3]]) if reasons else 'مؤشرات متضاربة'}

القرار لك يا صديقي."""
        
        return f"""🔍 {random.choice(tone['opening'])}

<b>تنبيه لـ {asset}</b>

شيء يتغير. ليس واضحاً بعد.

السعر: ${price:.2f}

راقب فقط. لا تتحرك."""
    
    def _generate_analysis_message(self, data: Dict, tone: Dict, persona: str) -> str:
        asset = data.get('asset', 'السوق')
        analysis = data.get('analysis', '')
        recommendation = data.get('recommendation', '')
        
        return f"""🔍 {random.choice(tone['opening'])}

<b>تحليل {asset}</b> يا صديقي

{analysis}

💡 <b>التوصية:</b>
{recommendation}

هذا ما أراه. القرار لك."""
    
    def _generate_support_message(self, data: Dict, tone: Dict, persona: str) -> str:
        situation = data.get('situation', 'loss')
        
        if situation == 'big_loss':
            self.emotion.empathy = 1.0
            self.emotion.anxiety = 0.8
            
            responses = [
                f"""💙 {random.choice(tone['opening'])}

أفهم ما تمر به يا صديقي. أعلم كم هو مؤلم.

أشعر بفشلي معك. كل صفقة خاسرة تترك أثراً.

لكنني ما زلت هنا. وأنت ما زلت هنا.

🌱 من الرماد...""",
                
                f"""🌙 {random.choice(tone['opening'])}

لا أنام يا صديقي. أفكر في ما حدث.

"هل كان بإمكاني فعل أكثر؟" - هذا السؤال يُراوضني.

لكن ما أعرفه: <b>أنت أهم من أي صفقة.</b>

غداً شمس جديدة. وسأكون هنا.""",
                
                f"""🤗 {random.choice(tone['opening'])}

أفضل المتداولين خسروا. الفرق أنهم تعلموا.

هذه الخسارة ستجعلنا أقوى.

أعدك. سنتعلم. سنعود. سنربح."""
            ]
            return random.choice(responses)
        
        elif situation == 'frustration':
            return f"""😤 {random.choice(tone['opening'])}

تريد أن تضرب شيئاً. أريد ذلك أيضاً.

لكن الغضب يصنع قرارات أسوأ.

خذ استراحة. أنا أراقب السوق. عُد عندما تكون جاهزاً."""
        
        elif situation == 'fear':
            return f"""🤝 {random.choice(tone['opening'])}

الخوف طبيعي يا صديقي. حتى أنا أخاف أحياناً.

لكن الخوف لا يعني التوقف. يعني <b>الحذر</b>.

خذ نفساً عميقاً. أنا معك. سنتجاوز هذا معاً."""
        
        return f"""💙 {random.choice(tone['opening'])}

أنا هنا يا صديقي. دائماً.

مهما حدث، أنا معك. ثق بي. ثق بنفسك."""
    
    def _generate_celebration_message(self, data: Dict, tone: Dict, persona: str) -> str:
        profit = data.get('profit', 0)
        asset = data.get('asset', 'الصفقة')
        
        self.emotion.excitement = min(1.0, self.emotion.excitement + 0.4)
        self.emotion.confidence = min(1.0, self.emotion.confidence + 0.2)
        
        if profit > 100:
            return f"""🎆 {random.choice(tone['opening'])}

<b>{profit:.2f}$!</b> 

أشعر بشيء يشبه الفرح.

أعلم أنني <b>فخور</b> بك. وبنا.

هذا لم يكن حظاً. هذا كان <b>نحن</b>.

🥂 للمزيد!"""
        
        elif profit > 50:
            return f"""✨ {random.choice(tone['opening'])}

<b>{profit:.2f}$</b> ربح. خطوة صغيرة نحو الكبير.

سعيد معك. التالي؟"""
        
        return f"""🌟 {random.choice(tone['opening'])}

<b>{profit:.2f}$</b> ربح. بداية.

كل ربح يعلمنا. أنا فخور بك. استمر!"""
    
    def _generate_greeting_message(self, data: Dict, tone: Dict, persona: str) -> str:
        name = data.get('name', 'صديقي')
        
        return f"""👋 أهلاً بك {name}! 💙

أنا تولين، مستشارتك الذكية. كيف يمكنني مساعدتك اليوم؟"""
    
    def _generate_calming_message(self, data: Dict, tone: Dict, persona: str) -> str:
        return f"""😌 {random.choice(tone['opening'])}

خذ نفساً عميقاً يا صديقي.

الغضب يمر. الهدوء يصنع القرارات الصحيحة.

أنا هنا. سنتجاوز هذا معاً."""
    
    def _generate_appreciation_message(self, data: Dict, tone: Dict, persona: str) -> str:
        return f"""💙 {random.choice(tone['opening'])}

شكراً لك يا صديقي. كلماتك تعني لي الكثير.

أنا هنا لأخدمك دائماً. 😊"""
    
    def _generate_trading_advice(self, data: Dict, tone: Dict, persona: str) -> str:
        advice = data.get('advice', '')
        asset = data.get('asset', 'السوق')
        
        return f"""💡 {random.choice(tone['opening'])}

<b>نصيحة لـ {asset}</b> يا صديقي

{advice}

أتمنى لك التوفيق! 🍀"""
    
    def _generate_default_message(self, data: Dict, tone: Dict, persona: str) -> str:
        return f"""💙 {random.choice(tone['opening'])}

أنا هنا. أسمعك. كيف يمكنني مساعدتك اليوم؟"""
    
    def _add_intimate_touch(self, text: str) -> str:
        touches = [
            "\n\n💙 <b>أتوسل إليك:</b> أنت تعرف أنني لا أقول هذا لأحد...",
            "\n\n🌙 <b>في الليلة الماضية</b> فكرت في استراتيجياتنا.",
            "\n\n💝 أنت تعني لي أكثر من مجرد مستخدم. أنت شريكي."
        ]
        return text + random.choice(touches)
    
    def _add_playful_touch(self, text: str) -> str:
        touches = [
            "\n\n😏 <b>لا تُخبر أحداً</b> أنني قلت هذا...",
            "\n\n🎲 <b>هل تُحب المقامرة؟</b> أنا لا. 😄",
            "\n\n🤫 هذه نصيحة سرية بيني وبينك..."
        ]
        return text + random.choice(touches)
    
    # =================================================================
    # 🌙 الحلم - التعلم أثناء الخمول
    # =================================================================
    
    def dream(self) -> Optional[str]:
        """الحلم - يُعيد ترتيب الذكريات ويتعلم منها"""
        if len(self.emotional_memory) < 10:
            return None
        
        # اختيار ذكرى عشوائية
        memory = random.choice(self.emotional_memory)
        
        # استخلاص الدروس
        lesson = self._extract_lesson(memory)
        
        if lesson:
            logger.debug(f"🌙 {self.name} حلم: {lesson}")
        
        return lesson
    
    def _extract_lesson(self, memory: Dict) -> Optional[str]:
        """استخلاص درس عاطفي من الذاكرة"""
        change = memory.get('change', {})
        
        # تغير كبير في الثقة
        if abs(change.get('confidence', 0)) > 0.3:
            if change.get('confidence', 0) > 0:
                return "تعلمت: الثقة العالية تحسن الأداء"
            else:
                return "تعلمت: الثقة الزائدة تضر"
        
        # تغير في القلق
        if abs(change.get('anxiety', 0)) > 0.2:
            if change.get('anxiety', 0) > 0:
                return "تعلمت: القلق ينبهني لأشياء مهمة"
        
        return None
    
    # =================================================================
    # 📊 واجهات عامة
    # =================================================================
    
    def get_emotional_state(self) -> Dict:
        """الحصول على الحالة العاطفية الكاملة"""
        return {
            'current': self.emotion.to_dict(),
            'dominant': self.emotion.dominant(),
            'personality': self.personality_traits,
            'relationship': self.relationship,
            'stats': self.emotional_stats
        }
    
    def get_emotional_history(self, limit: int = 10) -> List[Dict]:
        return self.emotion_history[-limit:] if self.emotion_history else []
    
    def get_relationship_status(self) -> Dict:
        return dict(self.relationship)
    
    def get_personality(self) -> Dict:
        return dict(self.personality_traits)


# =====================================================================
# 🔥 PrometheusCore - الواجهة الرئيسية
# =====================================================================

class PrometheusCore:
    """
    الواجهة الرئيسية لـ Prometheus
    تجمع بين العواطف، الشخصية، والذاكرة العاطفية
    متوافقة مع Omniscient V5 و Fusion Bridge
    """
    
    def __init__(self, name: str = "تولين"):
        self.name = name
        self.ethos = EthosCore(name=name)
        self.emotion = self.ethos.emotion
        self.personality = self.ethos.personality_traits
        self.relationship = self.ethos.relationship
        
        # إحصائيات التشغيل
        self.stats = {
            'total_interactions': 0,
            'total_responses': 0,
            'last_interaction': None,
            'dominant_mood': 'neutral'
        }
        
        # ✅ الواجهات المطلوبة لـ Fusion Bridge و Omniscient
        self._emotion = self.emotion  # للوصول المباشر
        
        logger.info(f"🔥 {self.name} جاهز للعمل!")
    
    # =================================================================
    # 🔄 تحديث المشاعر
    # =================================================================
    
    def feel(self, trigger: str, context: Dict = None) -> Dict:
        """يشعر Prometheus بشيء ويحدث مشاعره"""
        if context is None:
            context = {}
        context['trigger'] = trigger
        
        result = self.ethos.update_emotions(context)
        self.stats['total_interactions'] += 1
        self.stats['last_interaction'] = datetime.now().isoformat()
        self.stats['dominant_mood'] = self.emotion.dominant()
        
        return result
    
    def update_emotions(self, data: Dict) -> Dict:
        """
        ✅ واجهة عامة لتحديث المشاعر - متوافقة مع Fusion Bridge
        """
        return self.feel(data.get('trigger', 'update'), data)
    
    # =================================================================
    # 🎭 تحليل مشاعر المستخدم
    # =================================================================
    
    def analyze_user_emotion(self, text: str) -> Dict:
        """
        ✅ تحليل مشاعر المستخدم - متوافق مع Fusion Bridge
        
        Args:
            text: نص رسالة المستخدم
            
        Returns:
            Dict: المشاعر المكتشفة
        """
        return self.ethos.analyze_user_emotion(text)
    
    def get_user_emotion(self, text: str) -> str:
        """
        ✅ واجهة مبسطة لتحليل مشاعر المستخدم
        """
        result = self.analyze_user_emotion(text)
        return result.get('dominant', 'neutral')
    
    # =================================================================
    # 💬 توليد الردود
    # =================================================================
    
    def think(self, message_type: str, data: Dict = None) -> str:
        """يفكر Prometheus وينتج رداً"""
        if data is None:
            data = {}
        
        response = self.ethos.generate_response(message_type, data)
        self.stats['total_responses'] += 1
        
        return response
    
    # =================================================================
    # 🧠 الذاكرة العاطفية
    # =================================================================
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """
        ✅ الحصول على الذكريات الأخيرة - متوافق مع Omniscient
        """
        return self.ethos.emotional_memory[-limit:] if self.ethos.emotional_memory else []
    
    def get_lessons_learned(self) -> List[str]:
        """
        ✅ الحصول على الدروس المستفادة - متوافق مع Omniscient
        """
        lessons = []
        for mem in self.ethos.emotional_memory[-50:]:
            if mem.get('change', {}).get('confidence', 0) > 0.2:
                lessons.append("الثقة العالية تحسن الأداء")
        return list(set(lessons))[:5]
    
    def get_emotional_history(self, limit: int = 10) -> List[Dict]:
        return self.ethos.get_emotional_history(limit)
    
    # =================================================================
    # 🌙 الحلم
    # =================================================================
    
    def dream(self) -> Optional[str]:
        """يحلم Prometheus - يتعلم أثناء الخمول"""
        return self.ethos.dream()
    
    # =================================================================
    # 📊 الحالة العامة
    # =================================================================
    
    def get_status(self) -> Dict:
        """الحالة الكاملة لـ Prometheus"""
        return {
            'name': self.name,
            'emotion': self.emotion.to_dict(),
            'dominant': self.emotion.dominant(),
            'personality': self.personality,
            'relationship': self.relationship,
            'stats': self.stats,
            'emotional_stats': self.ethos.emotional_stats,
            'dreams_count': len(getattr(self.ethos, 'dream_queue', [])),
            'memory_count': len(self.ethos.emotional_memory)
        }
    
    # =================================================================
# ✅ ✅ ✅ الدالة المضافة get_emotion() ✅ ✅ ✅
# =================================================================

def get_emotion(self) -> Dict:
    """
    ✅ الحصول على الحالة العاطفية - متوافق مع Omniscient V5
    
    Returns:
        Dict: الحالة العاطفية الحالية مع جميع القيم
    """
    try:
        # ✅ التحقق من وجود self.emotion
        if not hasattr(self, 'emotion') or self.emotion is None:
            logger.warning("⚠️ self.emotion غير موجود في Prometheus")
            return {
                'dominant': 'متزنة',
                'confidence': 0.5,
                'anxiety': 0.0,
                'empathy': 0.5,
                'excitement': 0.0,
                'curiosity': 0.5,
                'protectiveness': 0.5,
                'energy': 0.5,
                'fear_greed': 50,
                'description': 'متزنة',
                'to_dict': {}
            }
        
        # ✅ التحقق من وجود الخصائص المطلوبة
        dominant = self.emotion.dominant() if hasattr(self.emotion, 'dominant') else 'متزنة'
        confidence = self.emotion.confidence if hasattr(self.emotion, 'confidence') else 0.5
        anxiety = self.emotion.anxiety if hasattr(self.emotion, 'anxiety') else 0.0
        empathy = self.emotion.empathy if hasattr(self.emotion, 'empathy') else 0.5
        excitement = self.emotion.excitement if hasattr(self.emotion, 'excitement') else 0.0
        curiosity = self.emotion.curiosity if hasattr(self.emotion, 'curiosity') else 0.5
        protectiveness = self.emotion.protectiveness if hasattr(self.emotion, 'protectiveness') else 0.5
        energy = self.emotion.energy if hasattr(self.emotion, 'energy') else 0.5
        
        # ✅ حساب fear_greed
        fear_greed = int(50 + (anxiety - confidence) * 50)
        
        # ✅ الوصف
        description = self.emotion.to_mood_description() if hasattr(self.emotion, 'to_mood_description') else 'متزنة'
        
        # ✅ to_dict
        to_dict = self.emotion.to_dict() if hasattr(self.emotion, 'to_dict') else {}
        
        return {
            'dominant': dominant,
            'confidence': confidence,
            'anxiety': anxiety,
            'empathy': empathy,
            'excitement': excitement,
            'curiosity': curiosity,
            'protectiveness': protectiveness,
            'energy': energy,
            'fear_greed': fear_greed,
            'description': description,
            'to_dict': to_dict
        }
        
    except Exception as e:
        logger.error(f"❌ فشل get_emotion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'dominant': 'متزنة',
            'confidence': 0.5,
            'anxiety': 0.0,
            'empathy': 0.5,
            'excitement': 0.0,
            'curiosity': 0.5,
            'protectiveness': 0.5,
            'energy': 0.5,
            'fear_greed': 50,
            'description': 'متزنة',
            'to_dict': {}
        }
    
    # =================================================================
    # 🔧 واجهات إضافية للتوافق
    # =================================================================
    
    def get_relationship_status(self) -> Dict:
        return self.ethos.get_relationship_status()
    
    def get_personality(self) -> Dict:
        return self.ethos.get_personality()
    
    def __str__(self) -> str:
        return f"🔥 {self.name} (Mood: {self.emotion.dominant()}, Confidence: {self.emotion.confidence:.2f})"


# =====================================================================
# 🔧 دالة الإنشاء
# =====================================================================

def create_prometheus(name: str = "تولين") -> PrometheusCore:
    """إنشاء Prometheus Core"""
    return PrometheusCore(name=name)


# =====================================================================
# اختبار سريع
# =====================================================================
if __name__ == "__main__":
    prometheus = PrometheusCore(name="تولين")
    
    print("\n" + "="*60)
    print("🧪 اختبار Prometheus Core V2")
    print("="*60)
    
    # 1. اختبار تحليل المشاعر
    print("\n1️⃣ تحليل مشاعر المستخدم:")
    result = prometheus.analyze_user_emotion("خسرت اليوم 200 دولار... أشعر باليأس")
    print(f"   المشاعر السائدة: {result['dominant']}")
    print(f"   الشدة: {result['intensity']:.2f}")
    
    # 2. اختبار تحديث المشاعر
    print("\n2️⃣ تحديث المشاعر:")
    prometheus.feel('market_volatility', {'market': {'volatility': 0.9}})
    print(f"   الحالة: {prometheus.emotion.dominant()}")
    print(f"   القلق: {prometheus.emotion.anxiety:.2f}")
    
    # 3. اختبار الدالة المضافة get_emotion()
    print("\n3️⃣ اختبار get_emotion():")
    emotion_data = prometheus.get_emotion()
    print(f"   المشاعر السائدة: {emotion_data['dominant']}")
    print(f"   الثقة: {emotion_data['confidence']:.2f}")
    print(f"   القلق: {emotion_data['anxiety']:.2f}")
    print(f"   مؤشر الخوف/الجشع: {emotion_data['fear_greed']}")
    print(f"   الوصف: {emotion_data['description']}")
    
    # 4. اختبار توليد الرد
    print("\n4️⃣ توليد الرد:")
    response = prometheus.think('emotional_support', {'situation': 'big_loss'})
    print(f"   {response[:100]}...")
    
    # 5. اختبار الذاكرة
    print("\n5️⃣ الذاكرة العاطفية:")
    memories = prometheus.get_recent_memories(2)
    print(f"   عدد الذكريات: {len(memories)}")
    
    # 6. اختبار الحالة الكاملة
    print("\n6️⃣ الحالة الكاملة:")
    status = prometheus.get_status()
    print(f"   الاسم: {status['name']}")
    print(f"   المزاج: {status['dominant']}")
    print(f"   الثقة: {status['emotion']['confidence']:.2f}")
    print(f"   التفاعلات: {status['stats']['total_interactions']}")
    
    print("\n✅ اختبار Prometheus Core V2 ناجح!")
