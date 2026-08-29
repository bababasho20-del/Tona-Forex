"""
🌉 Fusion Bridge V2 - جسر الدمج المتقدم
🔗 يربط بين تولين و Prometheus في تكامل سلس

الميزات:
- دمج المشاعر مع التحليل الفني
- تكامل مع Omniscient V5
- وعي زمني من Chronos
- تنبؤات من Oracle
- ذاكرة سردية من Narrative
- ردود مخصصة حسب المشاعر
"""

import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque

logger = logging.getLogger("TonaPrometheus")


# =====================================================================
# 🌉 FusionBridge - جسر الدمج الرئيسي
# =====================================================================

class FusionBridge:
    """
    جسر الدمج بين تولين و Prometheus
    
    يدمج:
    - المشاعر (Prometheus)
    - الزمن (Chronos)
    - التنبؤات (Oracle)
    - الذاكرة (Narrative)
    - التحليل (Tona)
    """
    
    def __init__(self, prometheus=None, chronos=None, oracle=None, narrative=None):
        self.prometheus = prometheus
        self.chronos = chronos
        self.oracle = oracle
        self.narrative = narrative
        
        # إعدادات الدمج
        self.config = {
            'emotional_weight': 0.4,
            'analytical_weight': 0.6,
            'creativity_threshold': 0.3,
            'risk_tolerance': 0.5,
            'empathy_boost': 0.3,
            'time_awareness': True,
            'narrative_mode': True,
            'max_recommendations': 3
        }
        
        # سجل الدمج
        self.fusion_log: deque = deque(maxlen=100)
        self.fusion_stats = {
            'total_fusions': 0,
            'emotional_contributions': 0,
            'analytical_contributions': 0,
            'creative_contributions': 0,
            'success_rate': 0.5
        }
        
        logger.info("🌉 Fusion Bridge V2: جسر الدمج المتقدم جاهز!")
    
    # =================================================================
    # 🎯 معالجة الإشارات
    # =================================================================
    
    def process_signal(self, asset: str, signal_data: Dict) -> Dict:
        """
        معالجة إشارة من تولين ودمجها مع رؤية Prometheus
        """
        logger.info(f"🌉 معالجة إشارة لـ {asset}")
        
        # 1. تحليل الإشارة
        signal = signal_data.get('signal', 'WAIT')
        confidence = signal_data.get('confidence', 0.5)
        price = signal_data.get('price', 0)
        indicators = signal_data.get('indicators', {})
        
        # 2. تحديث مشاعر Prometheus
        emotional_state = self._update_prometheus('new_signal', {
            'market': signal_data,
            'asset': asset,
            'signal': signal,
            'confidence': confidence
        })
        
        # 3. إضافة السياق الزمني
        temporal_context = self._get_temporal_context()
        
        # 4. توليد التنبؤات (Oracle)
        oracle_vision = self._get_oracle_vision(asset, price, signal, indicators)
        
        # 5. دمج النتائج
        fused_result = self._fuse_signal(
            asset=asset,
            signal=signal,
            confidence=confidence,
            emotional_state=emotional_state,
            temporal_context=temporal_context,
            oracle_vision=oracle_vision,
            indicators=indicators,
            price=price
        )
        
        # 6. تسجيل في الذاكرة السردية
        self._record_narrative('signal_fusion', {
            'asset': asset,
            'signal': signal,
            'fused_result': fused_result
        }, emotional_state)
        
        # 7. تسجيل في السجل
        self._log_fusion('signal', {'asset': asset, 'signal': signal})
        
        return fused_result
    
    # =================================================================
    # ⚠️ معالجة التحذيرات
    # =================================================================
    
    def process_warning(self, asset: str, warning_data: Dict) -> Dict:
        """
        معالجة تحذير من تولين ودمجه مع رؤية Prometheus
        """
        logger.info(f"🌉 معالجة تحذير لـ {asset}")
        
        level = warning_data.get('warning_level', 'LIGHT')
        reasons = warning_data.get('reasons', [])
        price = warning_data.get('price', 0)
        sl = warning_data.get('sl', 0)
        distance = warning_data.get('distance_to_sl', 0)
        
        # تحديث مشاعر Prometheus (الخوف والقلق يرتفعان)
        emotional_state = self._update_prometheus('warning', {
            'asset': asset,
            'level': level,
            'distance': distance,
            'price': price
        })
        
        # السياق الزمني للتحذير
        temporal_context = self._get_temporal_context()
        if level in ['URGENT', 'STRONG'] and temporal_context:
            temporal_context['time_dilation'] = temporal_context.get('time_dilation', 1.0) * 1.5
        
        # دمج النتائج
        fused_result = self._fuse_warning(
            asset=asset,
            level=level,
            reasons=reasons,
            price=price,
            sl=sl,
            distance=distance,
            emotional_state=emotional_state,
            temporal_context=temporal_context
        )
        
        self._record_narrative('warning_fusion', {
            'asset': asset,
            'level': level,
            'fused_result': fused_result
        }, emotional_state)
        
        self._log_fusion('warning', {'asset': asset, 'level': level})
        
        return fused_result
    
    # =================================================================
    # 💬 معالجة رسائل المستخدم
    # =================================================================
    
    def process_user_message(self, message: str, context: Dict = None) -> str:
        """
        معالجة رسالة المستخدم ودمجها مع شخصية Prometheus
        """
        logger.info(f"🌉 معالجة رسالة: {message[:30]}...")
        
        if context is None:
            context = {}
        
        # 1. تحليل مشاعر المستخدم
        user_emotion = self._analyze_user_emotion(message)
        context['user_emotion'] = user_emotion
        
        # 2. تحديث مشاعر Prometheus
        emotional_state = self._update_prometheus('user_message', {
            'user_message': message,
            'user_emotion': user_emotion
        })
        
        # 3. تحديد نوع الرد المناسب
        response_type = self._determine_response_type(message, user_emotion)
        
        # 4. توليد الرد المدمج
        response = self._generate_fused_response(
            message=message,
            user_emotion=user_emotion,
            emotional_state=emotional_state,
            response_type=response_type,
            context=context
        )
        
        # 5. تسجيل في الذاكرة السردية
        self._record_narrative('conversation_fusion', {
            'user_message': message[:100],
            'user_emotion': user_emotion,
            'response': response[:100]
        }, emotional_state)
        
        self._log_fusion('conversation', {'message': message[:50]})
        
        return response
    
    # =================================================================
    # 🔧 دوال مساعدة داخلية
    # =================================================================
    
    def _update_prometheus(self, trigger: str, data: Dict) -> Dict:
        """تحديث Prometheus وإرجاع الحالة العاطفية"""
        if not self.prometheus:
            return {}
        
        try:
            if hasattr(self.prometheus, 'feel'):
                return self.prometheus.feel(trigger, data)
            elif hasattr(self.prometheus, 'update_emotions'):
                data['trigger'] = trigger
                return self.prometheus.update_emotions(data)
            elif hasattr(self.prometheus, '_update_emotions'):
                data['trigger'] = trigger
                return self.prometheus._update_emotions(data)
        except Exception as e:
            logger.warning(f"⚠️ فشل تحديث Prometheus: {e}")
        
        return {}
    
    def _analyze_user_emotion(self, message: str) -> str:
        """تحليل مشاعر المستخدم"""
        if not self.prometheus:
            return 'neutral'
        
        try:
            if hasattr(self.prometheus, 'analyze_user_emotion'):
                result = self.prometheus.analyze_user_emotion(message)
                return result.get('dominant', 'neutral')
            elif hasattr(self.prometheus, 'get_user_emotion'):
                return self.prometheus.get_user_emotion(message)
        except Exception as e:
            logger.warning(f"⚠️ فشل تحليل مشاعر المستخدم: {e}")
        
        return 'neutral'
    
    def _get_temporal_context(self) -> Dict:
        """الحصول على السياق الزمني من Chronos"""
        if not self.chronos or not self.config.get('time_awareness', True):
            return {}
        
        try:
            if hasattr(self.chronos, 'get_temporal_context'):
                return self.chronos.get_temporal_context()
            elif hasattr(self.chronos, 'get_context'):
                return self.chronos.get_context()
        except Exception as e:
            logger.warning(f"⚠️ فشل الحصول على السياق الزمني: {e}")
        
        return {}
    
    def _get_oracle_vision(self, asset: str, price: float, signal: str, indicators: Dict) -> Dict:
        """الحصول على التنبؤات من Oracle"""
        if not self.oracle:
            return {}
        
        try:
            state = {
                'price': price,
                'signal': signal,
                'rsi': indicators.get('rsi', 50),
                'adx': indicators.get('adx', 15),
                'macd': indicators.get('macd', 0),
                'atr_14': indicators.get('atr', 0.5)
            }
            
            if hasattr(self.oracle, 'generate_prediction'):
                return self.oracle.generate_prediction(asset, state, horizon="12h")
            elif hasattr(self.oracle, 'predict'):
                return self.oracle.predict(asset, state)
        except Exception as e:
            logger.warning(f"⚠️ فشل توليد التنبؤ: {e}")
        
        return {}
    
    def _record_narrative(self, event_type: str, data: Dict, emotional_state: Dict):
        """تسجيل في الذاكرة السردية"""
        if not self.narrative or not self.config.get('narrative_mode', True):
            return
        
        try:
            if hasattr(self.narrative, 'record_experience'):
                self.narrative.record_experience(event_type, data, emotional_state)
        except Exception as e:
            logger.warning(f"⚠️ فشل تسجيل في الذاكرة السردية: {e}")
    
    def _log_fusion(self, fusion_type: str, data: Dict):
        """تسجيل عملية الدمج"""
        self.fusion_log.append({
            'timestamp': datetime.now().isoformat(),
            'type': fusion_type,
            'data': data
        })
        
        self.fusion_stats['total_fusions'] += 1
        if fusion_type == 'signal':
            self.fusion_stats['analytical_contributions'] += 1
        elif fusion_type == 'conversation':
            self.fusion_stats['emotional_contributions'] += 1
    
    # =================================================================
    # 🧠 دمج الإشارات
    # =================================================================
    
    def _fuse_signal(self, asset: str, signal: str, confidence: float,
                     emotional_state: Dict, temporal_context: Dict,
                     oracle_vision: Dict, indicators: Dict, price: float) -> Dict:
        """دمج الإشارة مع العناصر الأخرى"""
        
        # 1. تعديل الثقة حسب المشاعر
        adjusted_confidence = confidence
        if emotional_state:
            emotional_conf = emotional_state.get('confidence', 0.5)
            emotional_weight = self.config.get('emotional_weight', 0.4)
            adjusted_confidence = (confidence * (1 - emotional_weight) + 
                                  emotional_conf * emotional_weight)
            
            # تأثير القلق
            anxiety = emotional_state.get('anxiety', 0)
            if anxiety > 0.6:
                adjusted_confidence *= 0.85
            elif anxiety < 0.2:
                adjusted_confidence *= 1.05
        
        # 2. تأثير الزمن
        if temporal_context:
            time_dilation = temporal_context.get('time_dilation', 1.0)
            if time_dilation > 1.5:
                adjusted_confidence *= 0.9
            elif time_dilation < 0.8:
                adjusted_confidence *= 1.05
        
        # 3. تأثير Oracle
        oracle_signal = None
        oracle_confidence = 0
        if oracle_vision:
            scenarios = oracle_vision.get('scenarios', [])
            if scenarios:
                most_likely = max(scenarios, key=lambda x: x.get('probability', 0))
                oracle_signal = most_likely.get('name', 'uncertain')
                oracle_confidence = most_likely.get('probability', 0.3)
        
        # 4. الإشارة النهائية
        final_signal = signal
        final_confidence = adjusted_confidence
        
        if oracle_signal and oracle_confidence > 0.5 and oracle_signal != signal:
            final_confidence = (adjusted_confidence + oracle_confidence) / 2
            if final_confidence < 0.4:
                final_signal = 'WAIT'
        
        # 5. التوصيات
        recommendations = self._build_recommendations(signal, emotional_state, temporal_context, oracle_vision)
        
        return {
            'signal': final_signal,
            'confidence': min(1.0, max(0.0, final_confidence)),
            'original_signal': signal,
            'original_confidence': confidence,
            'emotional_contribution': emotional_state.get('dominant', 'neutral') if emotional_state else 'neutral',
            'temporal_state': temporal_context.get('psychological_time', 'normal') if temporal_context else 'unknown',
            'recommendations': recommendations[:self.config.get('max_recommendations', 3)],
            'decision_makers': self._get_decision_makers(final_signal, final_confidence)
        }
    
    # =================================================================
    # ⚠️ دمج التحذيرات
    # =================================================================
    
    def _fuse_warning(self, asset: str, level: str, reasons: List[str],
                      price: float, sl: float, distance: float,
                      emotional_state: Dict, temporal_context: Dict) -> Dict:
        """دمج التحذير مع العناصر الأخرى"""
        
        # 1. تعديل شدة التحذير
        adjusted_level = level
        
        if emotional_state:
            anxiety = emotional_state.get('anxiety', 0)
            protectiveness = emotional_state.get('protectiveness', 0)
            
            if protectiveness > 0.7:
                if level == 'LIGHT':
                    adjusted_level = 'MEDIUM'
                elif level == 'MEDIUM':
                    adjusted_level = 'STRONG'
            
            if anxiety > 0.7 and level == 'LIGHT':
                adjusted_level = 'MEDIUM'
        
        if temporal_context:
            events = temporal_context.get('event_proximity', [])
            for event in events:
                if event.get('impact') == 'high' and event.get('hours_until', 10) < 2:
                    if adjusted_level == 'LIGHT':
                        adjusted_level = 'MEDIUM'
                    elif adjusted_level == 'MEDIUM':
                        adjusted_level = 'STRONG'
        
        # 2. التوصيات حسب الشدة
        recommendations = self._build_warning_recommendations(adjusted_level, emotional_state)
        
        # 3. الإجراء الموصى به
        action_map = {
            'URGENT': 'close_immediately',
            'STRONG': 'close_if_no_recovery',
            'MEDIUM': 'reduce_position',
            'LIGHT': 'monitor_closely'
        }
        action = action_map.get(adjusted_level, 'monitor_closely')
        
        return {
            'level': adjusted_level,
            'original_level': level,
            'action': action,
            'recommendations': recommendations[:4],
            'emotional_contribution': emotional_state.get('dominant', 'neutral') if emotional_state else 'neutral',
            'urgency_score': self._calculate_urgency(adjusted_level, distance, emotional_state, temporal_context)
        }
    
    # =================================================================
    # 💬 توليد الردود المدمجة
    # =================================================================
    
    def _generate_fused_response(self, message: str, user_emotion: str,
                                  emotional_state: Dict, response_type: str,
                                  context: Dict) -> str:
        """توليد رد مدمج من تولين و Prometheus"""
        
        # 1. توليد رد تولين (المنطق)
        tona_response = self._generate_tona_response(message, user_emotion, context)
        
        # 2. توليد رد Prometheus (المشاعر)
        prometheus_response = self._generate_prometheus_response(response_type, context, emotional_state)
        
        # 3. دمج الردود
        if tona_response and prometheus_response:
            return self._merge_responses(tona_response, prometheus_response, user_emotion)
        elif prometheus_response:
            return prometheus_response
        elif tona_response:
            return tona_response
        
        return "💙 تولين: أنا هنا لمساعدتك يا صديقي. كيف يمكنني خدمتك؟"
    
    def _generate_tona_response(self, message: str, user_emotion: str, context: Dict) -> Optional[str]:
        """توليد رد تولين الأصلي"""
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ['نفط', 'oil', 'تحليل النفط']):
            return "🛢️ **تولين:** التحليل الشامل للنفط جاهز يا صديقي!"
        
        elif any(w in msg_lower for w in ['فضة', 'silver', 'تحليل الفضة']):
            return "🥈 **تولين:** التحليل الشامل للفضة جاهز يا عزيزي!"
        
        elif any(w in msg_lower for w in ['صفقة', 'وضع', 'حالة']):
            return "📊 **تولين:** جاري فحص وضع الصفقات المفتوحة يا صديقي..."
        
        elif any(w in msg_lower for w in ['إحصائيات', 'أداء', 'stats']):
            return "📈 **تولين:** جاري حساب الإحصائيات والأداء يا عزيزي..."
        
        return None
    
    def _generate_prometheus_response(self, response_type: str, context: Dict, emotional_state: Dict) -> Optional[str]:
        """توليد رد Prometheus"""
        if not self.prometheus:
            return None
        
        try:
            if hasattr(self.prometheus, 'think'):
                return self.prometheus.think(response_type, context)
            elif hasattr(self.prometheus, 'generate_response'):
                return self.prometheus.generate_response(response_type, context)
        except Exception as e:
            logger.warning(f"⚠️ فشل توليد رد Prometheus: {e}")
        
        return None
    
    def _merge_responses(self, tona: str, prometheus: str, user_emotion: str) -> str:
        """دمج ردود تولين و Prometheus"""
        if not tona:
            return prometheus
        if not prometheus:
            return tona
        
        # إذا كانت مشاعر المستخدم قوية، نعطي الأولوية لـ Prometheus
        if user_emotion in ['sadness', 'fear', 'anger']:
            return f"{prometheus}\n\n{tona}"
        
        # دمج متوازن
        return f"{prometheus}\n\n{tona}"
    
    # =================================================================
    # 🛠️ دوال مساعدة
    # =================================================================
    
    def _determine_response_type(self, message: str, user_emotion: str) -> str:
        """تحديد نوع الرد المناسب"""
        msg_lower = message.lower()
        
        if user_emotion in ['sadness', 'fear']:
            return 'emotional_support'
        elif user_emotion == 'joy':
            return 'celebration'
        elif user_emotion == 'anger':
            return 'calming'
        
        if any(w in msg_lower for w in ['تحليل', 'analysis', 'توقع']):
            return 'analysis'
        elif any(w in msg_lower for w in ['صفقة', 'trade', 'شراء', 'بيع']):
            return 'trading_advice'
        elif any(w in msg_lower for w in ['مرحبا', 'أهلا']):
            return 'greeting'
        elif any(w in msg_lower for w in ['شكر', 'thank']):
            return 'appreciation'
        
        return 'general'
    
    def _build_recommendations(self, signal: str, emotional_state: Dict,
                               temporal_context: Dict, oracle_vision: Dict) -> List[str]:
        """بناء التوصيات"""
        recommendations = []
        
        if emotional_state:
            dominant = emotional_state.get('dominant', '')
            if dominant == 'anxiety':
                recommendations.append('⚠️ القلق مرتفع - كن حذراً')
            elif dominant == 'confidence':
                recommendations.append('💪 الثقة عالية - استغل الفرصة')
            elif dominant == 'excitement':
                recommendations.append('🔥 حماس - تحرك بحكمة')
        
        if temporal_context:
            for rec in temporal_context.get('recommendations', []):
                if rec not in recommendations:
                    recommendations.append(rec)
        
        if oracle_vision:
            for sc in oracle_vision.get('scenarios', [])[:2]:
                if sc.get('what_to_watch'):
                    recommendations.append(f"👁️ {sc['what_to_watch']}")
        
        return recommendations
    
    def _build_warning_recommendations(self, level: str, emotional_state: Dict) -> List[str]:
        """بناء توصيات التحذير"""
        recommendations = []
        
        if level == 'URGENT':
            recommendations.extend([
                '🚨 تحذير عاجل - تصرف فوراً!',
                '🔒 حماية رأس المال أولاً'
            ])
        elif level == 'STRONG':
            recommendations.extend([
                '⚠️ تحذير قوي - فكر في الإغلاق',
                '🛡️ قلل المخاطر الآن'
            ])
        elif level == 'MEDIUM':
            recommendations.extend([
                '🔍 تحذير متوسط - راقب الوضع'
            ])
        else:
            recommendations.extend([
                '💡 تنبيه خفيف - راقب فقط'
            ])
        
        if emotional_state:
            dominant = emotional_state.get('dominant', '')
            if dominant == 'protectiveness':
                recommendations.insert(0, '🛡️ حماية رأس المال هي الأولوية')
            elif dominant == 'anxiety':
                recommendations.insert(0, '😰 القلق يزداد - كن حذراً جداً')
        
        return recommendations
    
    def _calculate_urgency(self, level: str, distance: float,
                          emotional_state: Dict, temporal_context: Dict) -> float:
        """حساب درجة الإلحاح"""
        urgency = 0.0
        
        level_map = {'LIGHT': 0.2, 'MEDIUM': 0.5, 'STRONG': 0.7, 'URGENT': 0.9}
        urgency += level_map.get(level, 0.3)
        
        if distance > 0 and distance < 0.05:
            urgency += 0.2
        elif distance > 0 and distance < 0.1:
            urgency += 0.1
        
        if emotional_state:
            urgency += emotional_state.get('anxiety', 0) * 0.1
            urgency += emotional_state.get('protectiveness', 0) * 0.1
        
        if temporal_context:
            time_dilation = temporal_context.get('time_dilation', 1.0)
            if time_dilation > 2.0:
                urgency += 0.2
            elif time_dilation > 1.5:
                urgency += 0.1
        
        return min(1.0, urgency)
    
    def _get_decision_makers(self, signal: str, confidence: float) -> List[str]:
        """من هم صناع القرار"""
        decision_makers = ['تولين']
        
        if confidence > 0.7:
            decision_makers.append('المنطق')
        elif confidence < 0.3:
            decision_makers.append('الحدس')
        
        if self.chronos and self.config.get('time_awareness', True):
            decision_makers.append('الوعي الزمني')
        
        if self.oracle:
            decision_makers.append('التنبؤ')
        
        return decision_makers
    
    # =================================================================
    # 📊 واجهات عامة
    # =================================================================
    
    def get_fusion_summary(self) -> str:
        """ملخص الدمج"""
        lines = [
            "🌉 <b>ملخص Fusion Bridge V2</b>",
            "━" * 30,
            f"📊 عدد عمليات الدمج: {self.fusion_stats['total_fusions']}",
            f"💝 مساهمات عاطفية: {self.fusion_stats['emotional_contributions']}",
            f"🧠 مساهمات تحليلية: {self.fusion_stats['analytical_contributions']}",
            f"🎨 مساهمات إبداعية: {self.fusion_stats['creative_contributions']}",
            "",
            "⚙️ <b>إعدادات الدمج:</b>"
        ]
        
        for key, value in self.config.items():
            if isinstance(value, bool):
                lines.append(f"  • {key}: {'مفعل' if value else 'معطل'}")
            else:
                lines.append(f"  • {key}: {value:.2f}" if isinstance(value, float) else f"  • {key}: {value}")
        
        lines.append("━" * 30)
        return "\n".join(lines)
    
    def get_fusion_log(self, limit: int = 10) -> List[Dict]:
        """سجل الدمج"""
        return list(self.fusion_log)[-limit:] if self.fusion_log else []
    
    def get_stats(self) -> Dict:
        """إحصائيات الدمج"""
        return dict(self.fusion_stats)
    
    def update_config(self, config: Dict):
        """تحديث إعدادات الدمج"""
        for key, value in config.items():
            if key in self.config:
                if isinstance(value, (int, float)):
                    self.config[key] = max(0, min(1, value))
                else:
                    self.config[key] = value
        
        logger.info(f"🌉 تم تحديث إعدادات الدمج: {config}")
    
    def get_emotional_state(self) -> Dict:
        """الحصول على الحالة العاطفية من Prometheus"""
        if self.prometheus and hasattr(self.prometheus, 'get_emotional_state'):
            return self.prometheus.get_emotional_state()
        return {}
    
    def get_relationship_status(self) -> Dict:
        """الحصول على حالة العلاقة من Prometheus"""
        if self.prometheus and hasattr(self.prometheus, 'get_relationship_status'):
            return self.prometheus.get_relationship_status()
        return {}


# =====================================================================
# 🔧 دالة الإنشاء
# =====================================================================

def create_fusion_bridge(prometheus=None, chronos=None, oracle=None, narrative=None) -> FusionBridge:
    """إنشاء Fusion Bridge"""
    return FusionBridge(
        prometheus=prometheus,
        chronos=chronos,
        oracle=oracle,
        narrative=narrative
    )


# =====================================================================
# اختبار سريع
# =====================================================================
if __name__ == "__main__":
    # إنشاء Fusion Bridge (بدون تبعيات)
    bridge = FusionBridge()
    
    print("\n" + "="*60)
    print("🧪 اختبار Fusion Bridge V2")
    print("="*60)
    
    # 1. اختبار معالجة إشارة
    print("\n1️⃣ معالجة إشارة:")
    result = bridge.process_signal('oil', {
        'signal': 'BUY',
        'confidence': 0.75,
        'price': 78.50,
        'indicators': {'rsi': 55, 'adx': 28, 'macd': 0.01, 'atr': 0.85}
    })
    print(f"   الإشارة النهائية: {result['signal']}")
    print(f"   الثقة: {result['confidence']:.2f}")
    print(f"   التوصيات: {len(result['recommendations'])}")
    print(f"   صناع القرار: {result['decision_makers']}")
    
    # 2. اختبار معالجة رسالة
    print("\n2️⃣ معالجة رسالة مستخدم:")
    response = bridge.process_user_message("خسرت اليوم 200 دولار... أشعر باليأس")
    print(f"   الرد: {response[:100]}...")
    
    # 3. عرض الملخص
    print("\n3️⃣ ملخص Fusion Bridge:")
    print(bridge.get_fusion_summary())
    
    print("\n✅ اختبار Fusion Bridge V2 ناجح!")
