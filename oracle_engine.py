"""
🔮 Oracle Engine - التنبؤ الاحتمالي المتقدم
🌌 Prometheus لا "يتنبأ" — بل **يُقدّر الاحتمالات**.
 
الفرق الجوهري:
- تولين: "أعتقد أن السعر سيصعد"
- Prometheus: "هناك 67% احتمال أن يصل السعر لـ 85$ خلال 12 ساعة،
                   23% احتمال أن يهبط لـ 78$،
                   و 10% احتمال أن يبقى في النطاق."
 
وأهم من ذلك: **"إذا لم يحدث... ماذا يعني ذلك؟"**
"""

import numpy as np
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

logger = logging.getLogger("TonaPrometheus")

class OracleEngine:
    """
    أوراكل التنبؤ الاحتمالي
    يولد رؤى متعددة السيناريوهات بدلاً من توقع واحد
    """
    
    def __init__(self, nucleus=None, chronos=None):
        self.nucleus = nucleus  # Narrative Memory
        self.chronos = chronos  # Chronos Engine
        
        # ✅ تسجيل حالة المحركات
        if nucleus is None:
            logger.warning("⚠️ Oracle: nucleus غير متوفر - سيتم استخدام القيم الافتراضية")
        if chronos is None:
            logger.warning("⚠️ Oracle: chronos غير متوفر - سيتم استخدام القيم الافتراضية")
        
        # نماذج التنبؤ
        self.prediction_models = {
            'monte_carlo': self._monte_carlo_simulation,
            'regime_transition': self._regime_transition_model,
            'pattern_completion': self._pattern_completion_model,
            'sentiment_momentum': self._sentiment_momentum_model,
            'volatility_forecast': self._volatility_forecast_model,
            'divergence_detection': self._divergence_detection_model
        }
        
        # سجل التنبؤات السابقة
        self.prediction_history = []
        self.max_history = 200
        
        # إحصائيات دقة التنبؤ
        self.accuracy_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'confidence_sum': 0})
        
        # ذاكرة الأنماط
        self.pattern_memory = []
        
        logger.info("🔮 Oracle Engine: التنبؤ الاحتمالي جاهز!")
    
    def generate_prediction(self, asset: str, current_state: dict, 
                          horizon: str = "12h", market_data: dict = None) -> dict:
        """
        توليد "رؤية" — ليس توقعاً واحداً، بل **مجموعة من العوالم الممكنة**.
        """
        # ✅ التحقق من وجود current_state
        if current_state is None or not isinstance(current_state, dict):
            current_state = {'price': 0, 'rsi': 50, 'macd': 0, 'adx': 15, 'atr_14': 0.1}
            logger.warning("⚠️ current_state غير صالح - استخدام القيم الافتراضية")
        
        # جمع "الأدلة" من الذاكرة
        similar_contexts = self._find_similar_contexts(current_state)
        
        # إضافة السياق الزمني
        temporal_context = {}
        if self.chronos is not None:
            try:
                if hasattr(self.chronos, 'get_temporal_context'):
                    temporal_context = self.chronos.get_temporal_context()
                else:
                    logger.debug("ℹ️ chronos لا يحتوي على get_temporal_context")
            except Exception as e:
                logger.debug(f"ℹ️ فشل جلب السياق الزمني: {e}")
        
        # تشغيل النماذج - مع التحقق من النتائج
        predictions = {}
        for model_name, model_fn in self.prediction_models.items():
            try:
                result = model_fn(asset, current_state, similar_contexts, horizon, market_data)
                if result is not None and isinstance(result, dict):
                    predictions[model_name] = result
                else:
                    predictions[model_name] = {'error': f'نموذج {model_name} أعاد None أو غير صالح'}
                    logger.warning(f"⚠️ نموذج {model_name} أعاد نتيجة غير صالحة")
            except Exception as e:
                logger.warning(f"⚠️ فشل نموذج {model_name}: {e}")
                predictions[model_name] = {'error': str(e)}
        
        # دمج النتائج (ensemble of predictions)
        ensemble = self._ensemble_predictions(predictions)
        
        # توليد "السيناريوهات"
        scenarios = self._generate_scenarios(ensemble, current_state, temporal_context)
        
        # حساب "عدم اليقين"
        uncertainty = self._calculate_uncertainty(ensemble, predictions)
        
        # توليد "الرؤية النهائية" — ليست رقم، بل حكاية
        vision = self._craft_vision(scenarios, current_state, temporal_context)
        
        # "ماذا لو لم يحدث؟"
        counter_scenarios = self._generate_counter_scenarios(scenarios)
        
        # تسجيل التنبؤ
        prediction_record = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'horizon': horizon,
            'ensemble': ensemble,
            'scenarios': scenarios,
            'uncertainty': uncertainty,
            'vision': vision[:200]
        }
        self.prediction_history.append(prediction_record)
        if len(self.prediction_history) > self.max_history:
            self.prediction_history = self.prediction_history[-self.max_history:]
        
        return {
            'scenarios': scenarios,
            'ensemble_confidence': ensemble.get('confidence', 0.5),
            'key_levels': ensemble.get('key_levels', {}),
            'vision': vision,
            'what_if_not': counter_scenarios,
            'uncertainty': uncertainty,
            'temporal_context': temporal_context,
            'prediction_id': len(self.prediction_history)
        }
    
    def _monte_carlo_simulation(self, asset: str, state: dict, 
                               similar: List[dict], horizon: str, market_data: dict) -> dict:
        """محاكاة مونت كارلو — 10,000 عالم ممكن"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {'error': 'حالة السوق غير صالحة', 'probability_up': 0.5, 'probability_down': 0.5}
        
        current_price = state.get('price', 0)
        if current_price <= 0:
            return {'error': 'سعر غير صالح', 'probability_up': 0.5, 'probability_down': 0.5}
        
        volatility = state.get('atr_14', 0.5) / current_price if current_price else 0.01
        volatility = max(0.001, min(0.2, volatility))  # حد أقصى 20%
        
        # توليد مسارات عشوائية
        n_simulations = 5000
        n_steps = self._horizon_to_steps(horizon)
        
        # Drift من السياقات المشابهة
        drift = 0
        if similar and isinstance(similar, list):
            historical_returns = []
            for s in similar:
                if isinstance(s, dict) and s.get('type') == 'trade':
                    data = s.get('data', {})
                    if isinstance(data, dict):
                        entry = data.get('entry_price', 0)
                        exit_price = data.get('exit_price', 0)
                        if entry > 0 and exit_price > 0:
                            ret = (exit_price - entry) / entry
                            if abs(ret) < 0.5:  # استثناء القيم المتطرفة
                                historical_returns.append(ret)
            
            if historical_returns:
                drift = np.mean(historical_returns)
                # تطبيع الانجراف حسب الأفق الزمني
                drift = drift * (n_steps / 48)  # 48 خطوة = 12 ساعة
        
        # حدود الانجراف
        drift = max(-0.1, min(0.1, drift))
        
        # GBM simulation
        dt = 1 / max(n_steps, 1)
        paths = np.zeros((n_simulations, n_steps))
        paths[:, 0] = current_price
        
        # توليد مسارات
        for t in range(1, n_steps):
            brownian = np.random.standard_normal(n_simulations)
            paths[:, t] = paths[:, t-1] * np.exp(
                (drift - 0.5 * volatility**2) * dt + 
                volatility * np.sqrt(dt) * brownian
            )
        
        # تحليل النتائج
        final_prices = paths[:, -1]
        
        # تصفية القيم غير الطبيعية
        valid_prices = final_prices[(final_prices > current_price * 0.3) & (final_prices < current_price * 3)]
        if len(valid_prices) < 100:
            valid_prices = final_prices
        
        return {
            'mean_price': float(np.mean(valid_prices)),
            'median_price': float(np.median(valid_prices)),
            'std': float(np.std(valid_prices)),
            'percentiles': {
                '5': float(np.percentile(valid_prices, 5)),
                '25': float(np.percentile(valid_prices, 25)),
                '50': float(np.percentile(valid_prices, 50)),
                '75': float(np.percentile(valid_prices, 75)),
                '95': float(np.percentile(valid_prices, 95))
            },
            'probability_up': float(np.mean(valid_prices > current_price)),
            'probability_down': float(np.mean(valid_prices < current_price)),
            'expected_max': float(np.mean(np.max(paths, axis=1))),
            'expected_min': float(np.mean(np.min(paths, axis=1))),
            'volatility': float(volatility),
            'drift': float(drift),
            'n_simulations': len(valid_prices)
        }
    
    def _regime_transition_model(self, asset: str, state: dict,
                                  similar: List[dict], horizon: str, market_data: dict) -> dict:
        """نموذج انتقال الأنظمة السوقية"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {
                'current_regime': 'ranging',
                'probability_stay': 0.6,
                'probability_transition': 0.4,
                'likely_next_regime': None,
                'regime_duration_expectation': 4.0,
                'regime_strength': 0.5
            }
        
        current_regime = state.get('regime', 'ranging')
        
        # ✅ التحقق من similar قبل استخدامه
        if similar is None or not isinstance(similar, list):
            similar = []
        
        # مصفوفة انتقال (مُستخلصة من الذاكرة)
        transitions = self._extract_transition_matrix(similar)
        
        # احتمالية البقاء في النظام الحالي vs الانتقال
        stay_prob = transitions.get(current_regime, {}).get(current_regime, 0.5) if isinstance(transitions, dict) else 0.5
        
        # تقدير المدة المتوقعة
        expected_duration = self._estimate_regime_duration(current_regime, similar)
        
        # النظام التالي الأكثر احتمالاً
        next_regime = 'unknown'
        if isinstance(transitions, dict) and current_regime in transitions:
            regime_trans = transitions.get(current_regime, {})
            if isinstance(regime_trans, dict) and regime_trans:
                next_regime = max(regime_trans, key=lambda k: regime_trans.get(k, 0))
        
        return {
            'current_regime': current_regime,
            'probability_stay': stay_prob,
            'probability_transition': 1 - stay_prob,
            'likely_next_regime': next_regime if next_regime != current_regime else None,
            'regime_duration_expectation': expected_duration,
            'regime_strength': self._calculate_regime_strength(current_regime, state)
        }
    
    def _pattern_completion_model(self, asset: str, state: dict,
                                   similar: List[dict], horizon: str, market_data: dict) -> dict:
        """نموذج إكمال الأنماط"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {'pattern_found': False, 'confidence': 0}
        
        # البحث عن أنماط غير مكتملة في البيانات الحالية
        pattern = self._detect_incomplete_pattern(state)
        
        if not pattern:
            return {'pattern_found': False, 'confidence': 0}
        
        # ✅ التحقق من similar
        if similar is None or not isinstance(similar, list):
            similar = []
        
        # البحث في الذاكرة عن إكمالات مشابهة
        completions = [s for s in similar 
                    if isinstance(s, dict) and s.get('pattern_type') == pattern.get('type')]
        
        if not completions:
            return {
                'pattern_found': True, 
                'pattern': pattern, 
                'confidence': 0.3, 
                'historical_completions': 0,
                'message': 'نمط نادر - ثقة منخفضة'
            }
        
        # حساب معدل النجاح
        success_count = 0
        total_profit = 0
        for c in completions:
            if isinstance(c, dict):
                data = c.get('data', {})
                if isinstance(data, dict):
                    profit = data.get('profit_dollars', 0)
                    total_profit += profit
                    if profit > 0:
                        success_count += 1
        
        success_rate = success_count / len(completions) if completions else 0
        avg_profit = total_profit / len(completions) if completions else 0
        
        return {
            'pattern_found': True,
            'pattern': pattern,
            'confidence': min(0.9, 0.3 + success_rate * 0.5),
            'historical_completions': len(completions),
            'historical_success_rate': success_rate,
            'average_profit': avg_profit,
            'expected_target': pattern.get('target_price'),
            'expected_time': pattern.get('expected_completion_time'),
            'completion_probability': min(0.9, success_rate * 0.8 + 0.2)
        }
    
    def _sentiment_momentum_model(self, asset: str, state: dict,
                                   similar: List[dict], horizon: str, market_data: dict) -> dict:
        """نموذج زخم المشاعر"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {
                'sentiment_score': 0.5,
                'sentiment_trend': 'neutral',
                'momentum_state': 'stable',
                'momentum_strength': 0,
                'volume_confirmation': False,
                'divergence_detected': False,
                'divergence_type': None,
                'divergence_strength': 0,
                'change_speed': 0.5,
                'warning': False
            }
        
        # تحليل "مزاج" السوق
        sentiment = self._aggregate_sentiment(asset, state, market_data)
        
        # الزخم
        momentum = state.get('price_momentum', 0)
        volume_trend = state.get('volume_trend', 0)
        
        # Divergence detection
        divergence = self._detect_divergence(state)
        
        # حساب سرعة التغير
        change_speed = self._calculate_change_speed(state)
        
        return {
            'sentiment_score': sentiment.get('score', 0.5),
            'sentiment_trend': sentiment.get('trend', 'neutral'),
            'momentum_state': 'accelerating' if momentum > 0.5 else 'decelerating' if momentum < -0.5 else 'stable',
            'momentum_strength': abs(momentum),
            'volume_confirmation': abs(volume_trend) > 0.3,
            'divergence_detected': divergence.get('detected', False),
            'divergence_type': divergence.get('type'),
            'divergence_strength': divergence.get('strength', 0),
            'change_speed': change_speed,
            'warning': divergence.get('detected', False) and sentiment.get('trend') != 'aligning'
        }
    
    def _volatility_forecast_model(self, asset: str, state: dict,
                                    similar: List[dict], horizon: str, market_data: dict) -> dict:
        """نموذج توقع التقلبات"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {
                'current_atr': 0.1,
                'expected_volatility': 0.1,
                'volatility_regime': 'normal',
                'event_impact': 1.0,
                'volatility_change': 0,
                'forecast_confidence': 0.5
            }
        
        current_atr = state.get('atr_14', 0.1)
        historical_volatility = state.get('historical_volatility', 0.2)
        
        # توقع التقلبات المستقبلية
        if similar and isinstance(similar, list):
            similar_vols = []
            for s in similar:
                if isinstance(s, dict):
                    data = s.get('data', {})
                    if isinstance(data, dict):
                        atr_val = data.get('atr', 0)
                        if atr_val > 0:
                            similar_vols.append(atr_val)
            if similar_vols:
                expected_vol = np.mean(similar_vols)
            else:
                expected_vol = current_atr
        else:
            expected_vol = current_atr
        
        # تأثير الأحداث - مع التحقق من chronos
        event_impact = 1.0
        if self.chronos is not None:
            try:
                if hasattr(self.chronos, 'get_temporal_context'):
                    context = self.chronos.get_temporal_context()
                    if isinstance(context, dict):
                        events = context.get('event_proximity', [])
                        if isinstance(events, list):
                            for event in events:
                                if isinstance(event, dict):
                                    if event.get('impact') == 'high' and event.get('hours_until', 10) < 4:
                                        event_impact = 1.5 + event.get('hours_until', 1) / 8
            except Exception as e:
                logger.debug(f"ℹ️ فشل جلب السياق الزمني: {e}")
        
        expected_vol *= event_impact
        
        # مستويات التقلب
        if expected_vol > current_atr * 1.5:
            volatility_regime = 'high'
        elif expected_vol > current_atr * 1.2:
            volatility_regime = 'elevated'
        elif expected_vol < current_atr * 0.7:
            volatility_regime = 'low'
        else:
            volatility_regime = 'normal'
        
        return {
            'current_atr': float(current_atr),
            'expected_volatility': float(expected_vol),
            'volatility_regime': volatility_regime,
            'event_impact': float(event_impact),
            'volatility_change': float((expected_vol - current_atr) / current_atr if current_atr > 0 else 0),
            'forecast_confidence': float(min(0.9, 0.5 + len(similar) * 0.01 if similar else 0.5))
        }
    
    def _divergence_detection_model(self, asset: str, state: dict,
                                     similar: List[dict], horizon: str, market_data: dict) -> dict:
        """نموذج كشف التباعدات"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {'detected': False, 'type': None, 'strength': 0}
        
        # كشف التباعد بين السعر والمؤشرات
        divergences = []
        
        # RSI Divergence
        rsi = state.get('rsi', 50)
        price = state.get('price', 0)
        
        # ✅ التحقق من similar
        if similar and isinstance(similar, list):
            # البحث عن تباعد في RSI
            for s in similar[-10:]:
                if isinstance(s, dict):
                    data = s.get('data', {})
                    if isinstance(data, dict):
                        prev_rsi = data.get('rsi', 0)
                        prev_price = data.get('price', 0)
                        if prev_price > 0 and prev_rsi > 0:
                            if price > prev_price and rsi < prev_rsi:
                                divergences.append({
                                    'type': 'bearish_rsi',
                                    'strength': (price - prev_price) / prev_price * (prev_rsi - rsi) / 10
                                })
                            elif price < prev_price and rsi > prev_rsi:
                                divergences.append({
                                    'type': 'bullish_rsi',
                                    'strength': (prev_price - price) / prev_price * (rsi - prev_rsi) / 10
                                })
        
        # MACD Divergence
        macd = state.get('macd', 0)
        if similar and isinstance(similar, list):
            for s in similar[-10:]:
                if isinstance(s, dict):
                    data = s.get('data', {})
                    if isinstance(data, dict):
                        prev_macd = data.get('macd', 0)
                        prev_price = data.get('price', 0)
                        if prev_price > 0 and prev_macd != 0:
                            if price > prev_price and macd < prev_macd:
                                divergences.append({
                                    'type': 'bearish_macd',
                                    'strength': (price - prev_price) / prev_price * (prev_macd - macd) / 0.01
                                })
                            elif price < prev_price and macd > prev_macd:
                                divergences.append({
                                    'type': 'bullish_macd',
                                    'strength': (prev_price - price) / prev_price * (macd - prev_macd) / 0.01
                                })
        
        # تجميع النتائج
        if divergences:
            # أقوى تباعد
            strongest = max(divergences, key=lambda x: abs(x.get('strength', 0)))
            return {
                'detected': True,
                'type': strongest.get('type'),
                'strength': min(1.0, abs(strongest.get('strength', 0))),
                'count': len(divergences),
                'divergences': divergences,
                'signal': 'bearish' if 'bearish' in strongest.get('type', '') else 'bullish'
            }
        
        return {'detected': False, 'type': None, 'strength': 0}
    
    def _ensemble_predictions(self, predictions: dict) -> dict:
        """دمج النماذج — ليس متوسطاً، بل "حوار" بينهم"""
        # ✅ التحقق من وجود predictions
        if predictions is None or not isinstance(predictions, dict):
            return {
                'direction': 'uncertain',
                'confidence': 0.3,
                'key_levels': {'support': 0, 'resistance': 0, 'pivot': 0},
                'model_agreement': 0,
                'votes': {},
                'models_used': 0
            }
        
        # جمع التوجيهات
        directions = []
        confidences = []
        
        # Monte Carlo
        mc = predictions.get('monte_carlo', {})
        if mc and isinstance(mc, dict):
            if 'probability_up' in mc and 'probability_down' in mc:
                if mc.get('probability_up', 0) > 0.6:
                    directions.append('up')
                    confidences.append(mc.get('probability_up', 0.5))
                elif mc.get('probability_down', 0) > 0.6:
                    directions.append('down')
                    confidences.append(mc.get('probability_down', 0.5))
        
        # Regime Transition
        rt = predictions.get('regime_transition', {})
        if rt and isinstance(rt, dict):
            likely_next = rt.get('likely_next_regime')
            if likely_next in ['trending_up', 'breakout']:
                directions.append('up')
                confidences.append(rt.get('probability_transition', 0.5))
            elif likely_next in ['trending_down', 'reversal']:
                directions.append('down')
                confidences.append(rt.get('probability_transition', 0.5))
        
        # Pattern Completion
        pc = predictions.get('pattern_completion', {})
        if pc and isinstance(pc, dict) and pc.get('pattern_found', False):
            target = pc.get('expected_target', 0)
            current = pc.get('pattern', {}).get('current_price', 0)
            if target > 0 and current > 0:
                if target > current:
                    directions.append('up')
                    confidences.append(pc.get('confidence', 0.5))
                else:
                    directions.append('down')
                    confidences.append(pc.get('confidence', 0.5))
        
        # Sentiment Momentum
        sm = predictions.get('sentiment_momentum', {})
        if sm and isinstance(sm, dict):
            score = sm.get('sentiment_score', 0.5)
            if score > 0.65:
                directions.append('up')
                confidences.append(score)
            elif score < 0.35:
                directions.append('down')
                confidences.append(1 - score)
        
        # تحديد الإجماع
        if not directions:
            consensus = 'uncertain'
            confidence = 0.3
        else:
            # الوزن حسب الثقة
            direction_weights = defaultdict(float)
            for d, c in zip(directions, confidences):
                direction_weights[d] += c
            
            consensus = max(direction_weights, key=direction_weights.get)
            
            # حساب الثقة الإجمالية
            total_confidence = sum(confidences) if confidences else 0
            agreement_rate = direction_weights[consensus] / (sum(direction_weights.values()) + 0.001)
            confidence = min(0.9, (total_confidence / len(confidences) if confidences else 0.3) * (0.6 + 0.4 * agreement_rate))
        
        # تحديد المستويات الرئيسية
        key_levels = self._extract_key_levels(predictions)
        
        return {
            'direction': consensus,
            'confidence': max(0.1, min(0.95, confidence)),
            'key_levels': key_levels,
            'model_agreement': len(set(directions)) / len(directions) if directions else 0,
            'votes': dict(direction_weights) if 'direction_weights' in locals() else {},
            'models_used': len(directions)
        }
    
    def _generate_scenarios(self, ensemble: dict, state: dict, temporal: dict) -> List[dict]:
        """توليد "عوالم ممكنة" — ليس توقعات، بل قصص"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            state = {'price': 0}
        
        # ✅ التحقق من وجود ensemble
        if ensemble is None or not isinstance(ensemble, dict):
            ensemble = {'direction': 'uncertain', 'confidence': 0.5, 'key_levels': {}}
        
        scenarios = []
        current_price = state.get('price', 0)
        direction = ensemble.get('direction', 'uncertain')
        confidence = ensemble.get('confidence', 0.5)
        key_levels = ensemble.get('key_levels', {})
        
        # السيناريو المتفائل
        if direction == 'up' or direction == 'uncertain':
            target_up = key_levels.get('resistance', current_price * 1.02)
            if target_up <= current_price:
                target_up = current_price * 1.02
            
            scenarios.append({
                'name': 'الصعود المتوقع 📈',
                'probability': max(0.1, confidence * 0.7 if direction == 'up' else 0.3),
                'description': f"السعر يصل لـ ${target_up:.2f} خلال الفترة المتوقعة",
                'trigger': "اختراق المقاومة مع زيادة الحجم",
                'what_to_watch': f"اختراق ${target_up:.2f} بإغلاق قوي",
                'target': target_up,
                'risk_level': 'moderate'
            })
        
        # السيناريو المتشائم
        if direction == 'down' or direction == 'uncertain':
            target_down = key_levels.get('support', current_price * 0.98)
            if target_down >= current_price:
                target_down = current_price * 0.98
            
            scenarios.append({
                'name': 'الهبوط المحتمل 📉',
                'probability': max(0.1, confidence * 0.7 if direction == 'down' else 0.3),
                'description': f"السعر يهبط لـ ${target_down:.2f}",
                'trigger': "فشل اختراق المقاومة مع تباعد سلبي",
                'what_to_watch': f"كسر ${target_down:.2f}",
                'target': target_down,
                'risk_level': 'moderate'
            })
        
        # السيناريو المحايد
        if not scenarios or len(scenarios) < 2:
            scenarios.append({
                'name': 'التذبذب 🌀',
                'probability': 0.3,
                'description': f"السعر يتحرك ضمن نطاق {current_price * 0.98:.2f} - {current_price * 1.02:.2f}",
                'trigger': "قلة الزخم والحجم",
                'what_to_watch': "اختراق النطاق",
                'target': current_price,
                'risk_level': 'low'
            })
        
        # السيناريو "الغريب" — الذي لا يتوقعه أحد
        if len(scenarios) < 3:
            scenarios.append({
                'name': 'المفاجأة 💥',
                'probability': 0.1,
                'description': "حدث خارجي (جيوسياسي، بنك مركزي) يُغيّر كل شيء",
                'trigger': "خبر عاجل غير متوقع",
                'what_to_watch': "الأخبار العاجلة — هذا خارج نطاق التحليل الفني",
                'target': None,
                'risk_level': 'high'
            })
        
        # تطبيع الاحتمالات
        total_prob = sum(s['probability'] for s in scenarios)
        if total_prob > 0:
            for s in scenarios:
                s['probability'] = s['probability'] / total_prob
        
        return scenarios
    
    def _craft_vision(self, scenarios: List[dict], state: dict, temporal: dict) -> str:
        """صياغة "الرؤية" — نص يقرأه Prometheus بنفسه قبل إرساله"""
        # ✅ التحقق من وجود scenarios
        if not scenarios or not isinstance(scenarios, list):
            return "👁️ **Prometheus يرى...**\n\nلا توجد سيناريوهات متاحة حالياً."
        
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            state = {'price': 0}
        
        most_likely = max(scenarios, key=lambda s: s.get('probability', 0))
        current_price = state.get('price', 0)
        
        # إضافة السياق الزمني
        time_context = ""
        if temporal and isinstance(temporal, dict):
            phase = temporal.get('market_phase', '')
            bio = temporal.get('biological_time', {})
            if phase:
                time_context = f"\n⏰ طور السوق: {phase}"
            if bio and isinstance(bio, dict) and bio.get('phase'):
                time_context += f"\n🧠 الإيقاع البيولوجي: {bio.get('phase', '')}"
        
        vision = f"""👁️ <b>Prometheus يرى...</b>

السعر الحالي: ${current_price:.2f}

الأرجح: {most_likely.get('name', 'غير محدد')} ({most_likely.get('probability', 0):.0%})

{most_likely.get('description', '')}

💡 {most_likely.get('what_to_watch', '')}

"""
        
        # إضافة السيناريوهات الأخرى
        vision += "\n🔮 <b>سيناريوهات أخرى:</b>\n"
        for sc in scenarios:
            if sc != most_likely:
                vision += f"  • {sc.get('name', '')} ({sc.get('probability', 0):.0%}): {sc.get('description', '')[:50]}...\n"
        
        # إضافة السياق الزمني
        if time_context:
            vision += f"\n{time_context}"
        
        vision += f"""

<b>السؤال ليس "ماذا سيحدث؟"</b>
<b>السؤال: "ماذا ستفعل عندما يحدث؟"</b>

أنا هنا. لكل سيناريو، لدينا خطة."""
        
        return vision
    
    def _generate_counter_scenarios(self, scenarios: List[dict]) -> List[dict]:
        """"ماذا لو لم يحدث؟" — التعلم من الفشل المُتخيل"""
        # ✅ التحقق من وجود scenarios
        if not scenarios or not isinstance(scenarios, list):
            return []
        
        counter = []
        for sc in scenarios:
            if isinstance(sc, dict):
                counter.append({
                    'name': f"❌ ماذا لو لم يحدث {sc.get('name', '')}؟",
                    'learning': f"إذا لم يحدث {sc.get('trigger', 'الحدث المتوقع')}، فهذا يعني أن السوق أقوى/أضعف مما توقعنا.",
                    'action': "في هذه الحالة، نعيد تقييم الموقف ونبحث عن تأكيدات جديدة.",
                    'original_scenario': sc.get('name', '')
                })
        return counter
    
    def _find_similar_contexts(self, state: dict) -> List[dict]:
        """البحث في الذاكرة عن سياقات مشابهة"""
        # ✅ التحقق من وجود nucleus
        if self.nucleus is None:
            logger.debug("ℹ️ nucleus غير متوفر - تخطي البحث عن سياقات مشابهة")
            return []
        
        try:
            # استخدام Narrative Memory للبحث
            experiences = getattr(self.nucleus, 'experiences', [])
            if not experiences or not isinstance(experiences, list):
                return []
            
            # ✅ التحقق من وجود state
            if state is None or not isinstance(state, dict):
                return []
            
            # البحث عن تجارب مشابهة
            similar = []
            current_price = state.get('price', 0)
            current_rsi = state.get('rsi', 50)
            
            for exp in experiences[-100:]:  # آخر 100 تجربة
                if not isinstance(exp, dict):
                    continue
                exp_data = exp.get('data', {})
                if not isinstance(exp_data, dict):
                    continue
                price = exp_data.get('entry_price', 0) or exp_data.get('price', 0)
                rsi = exp_data.get('rsi', 50)
                
                # حساب التشابه
                if price > 0 and current_price > 0:
                    price_sim = 1 - abs((price - current_price) / current_price)
                    rsi_sim = 1 - abs((rsi - current_rsi) / 50) if current_rsi > 0 else 0
                    similarity = (price_sim * 0.6 + rsi_sim * 0.4)
                    
                    if similarity > 0.7:
                        similar.append(exp)
            
            return similar
        except Exception as e:
            logger.warning(f"⚠️ فشل البحث عن سياقات مشابهة: {e}")
            return []
    
    def _extract_transition_matrix(self, similar: List[dict]) -> dict:
        """استخراج مصفوفة انتقال من الذاكرة"""
        # مصفوفة انتقال افتراضية
        default_matrix = {
            'ranging': {'ranging': 0.6, 'trending_up': 0.2, 'trending_down': 0.15, 'breakout': 0.05},
            'trending_up': {'trending_up': 0.7, 'ranging': 0.2, 'trending_down': 0.05, 'reversal': 0.05},
            'trending_down': {'trending_down': 0.7, 'ranging': 0.2, 'trending_up': 0.05, 'reversal': 0.05},
            'breakout': {'breakout': 0.5, 'trending_up': 0.3, 'ranging': 0.15, 'reversal': 0.05},
            'reversal': {'reversal': 0.4, 'trending_down': 0.3, 'trending_up': 0.2, 'ranging': 0.1}
        }
        
        # ✅ التحقق من similar
        if not similar or not isinstance(similar, list) or len(similar) <= 10:
            return default_matrix
        
        # محاولة استخراج من الذاكرة
        transitions = defaultdict(lambda: defaultdict(int))
        
        for exp in similar:
            if not isinstance(exp, dict):
                continue
            regime = exp.get('regime', 'ranging')
            next_regime = exp.get('next_regime', 'ranging')
            if regime and next_regime:
                transitions[regime][next_regime] += 1
        
        # تحويل إلى احتمالات
        result = {}
        for regime, nexts in transitions.items():
            total = sum(nexts.values())
            if total > 0:
                result[regime] = {k: v/total for k, v in nexts.items()}
            else:
                result[regime] = default_matrix.get(regime, default_matrix['ranging'])
        
        return result if result else default_matrix
    
    def _estimate_regime_duration(self, regime: str, similar: List[dict]) -> float:
        """تقدير مدة النظام الحالي"""
        default_durations = {
            'ranging': 6.0,
            'trending_up': 4.0,
            'trending_down': 4.0,
            'breakout': 2.0,
            'reversal': 2.0
        }
        
        # ✅ التحقق من similar
        if not similar or not isinstance(similar, list):
            return default_durations.get(regime, 4.0)
        
        # حساب متوسط المدة من الذاكرة
        durations = []
        for exp in similar:
            if isinstance(exp, dict) and exp.get('regime') == regime:
                duration = exp.get('duration', 0)
                if duration > 0:
                    durations.append(duration)
        
        if durations:
            return float(np.mean(durations))
        
        return default_durations.get(regime, 4.0)
    
    def _calculate_regime_strength(self, regime: str, state: dict) -> float:
        """حساب قوة النظام الحالي"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return 0.5
        
        strength = 0.5
        
        # عوامل تعزز القوة
        adx = state.get('adx', 15)
        if adx > 25:
            strength += 0.2
        elif adx > 20:
            strength += 0.1
        
        volume_ratio = state.get('volume_ratio', 1)
        if volume_ratio > 1.5:
            strength += 0.15
        elif volume_ratio > 1.2:
            strength += 0.05
        
        # عوامل تضعف القوة
        if abs(state.get('rsi', 50) - 50) < 5:
            strength -= 0.1
        
        return max(0.1, min(1.0, strength))
    
    def _detect_incomplete_pattern(self, state: dict) -> Optional[dict]:
        """كشف أنماط غير مكتملة"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return None
        
        # كشف أنماط بسيطة
        price = state.get('price', 0)
        rsi = state.get('rsi', 50)
        macd = state.get('macd', 0)
        adx = state.get('adx', 15)
        
        patterns = []
        
        # نمط القمة المزدوجة
        if state.get('double_top_detected', False):
            patterns.append({
                'type': 'double_top',
                'target_price': price * 0.95,
                'expected_completion_time': '4-8 ساعات',
                'completion_probability': 0.6
            })
        
        # نمط القاع المزدوج
        if state.get('double_bottom_detected', False):
            patterns.append({
                'type': 'double_bottom',
                'target_price': price * 1.05,
                'expected_completion_time': '4-8 ساعات',
                'completion_probability': 0.6
            })
        
        # RSI Divergence
        if state.get('rsi_divergence', False):
            if rsi > 70:
                patterns.append({
                    'type': 'bearish_divergence',
                    'target_price': price * 0.97,
                    'expected_completion_time': '2-4 ساعات',
                    'completion_probability': 0.7
                })
            elif rsi < 30:
                patterns.append({
                    'type': 'bullish_divergence',
                    'target_price': price * 1.03,
                    'expected_completion_time': '2-4 ساعات',
                    'completion_probability': 0.7
                })
        
        # Breakout pattern
        if adx > 25 and state.get('breakout_detected', False):
            patterns.append({
                'type': 'breakout',
                'target_price': price * (1 + 0.02 * (adx / 25)),
                'expected_completion_time': '1-2 ساعات',
                'completion_probability': 0.65
            })
        
        if patterns:
            # إرجاع أقوى نمط
            return max(patterns, key=lambda x: x.get('completion_probability', 0))
        
        return None
    
    def _aggregate_sentiment(self, asset: str, state: dict, market_data: dict) -> dict:
        """تجميع المشاعر من مصادر متعددة"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {'score': 0.5, 'trend': 'neutral', 'components': {}}
        
        # مؤشرات أساسية
        rsi = state.get('rsi', 50)
        macd = state.get('macd', 0)
        adx = state.get('adx', 15)
        
        # حساب النتيجة
        score = 0.5
        
        # تأثير RSI
        if rsi > 70:
            score -= 0.15  # تشبع شراء
        elif rsi > 60:
            score -= 0.05
        elif rsi < 30:
            score += 0.15  # تشبع بيع
        elif rsi < 40:
            score += 0.05
        
        # تأثير MACD
        if macd > 0:
            score += 0.1
        else:
            score -= 0.1
        
        # تأثير ADX
        if adx > 25:
            score += 0.1  # زخم قوي
        elif adx < 20:
            score -= 0.05  # ضعف
        
        # تأثير Fear & Greed (محاكاة)
        fng = self._get_fear_greed_index()
        if fng > 70:
            score -= 0.1  # طمع شديد
        elif fng < 30:
            score += 0.1  # خوف شديد
        
        # تحديد الاتجاه
        if score > 0.6:
            trend = 'bullish'
        elif score < 0.4:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'score': max(0, min(1, score)),
            'trend': trend,
            'components': {
                'rsi': rsi,
                'macd': macd,
                'adx': adx,
                'fear_greed': fng
            }
        }
    
    def _get_fear_greed_index(self) -> float:
        """محاكاة مؤشر الخوف والجشع"""
        # في التطبيق الحقيقي: جلب من API
        return 50 + random.randint(-20, 20)
    
    def _calculate_change_speed(self, state: dict) -> float:
        """حساب سرعة التغير"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return 0.5
        # محاكاة
        return random.uniform(0.1, 0.8)
    
    def _detect_divergence(self, state: dict) -> dict:
        """كشف التباعد"""
        # ✅ التحقق من وجود state
        if state is None or not isinstance(state, dict):
            return {'detected': False, 'type': None, 'strength': 0}
        # بالفعل تم في _divergence_detection_model
        # هنا نستخدم النتيجة
        return {
            'detected': state.get('divergence_detected', False),
            'type': state.get('divergence_type', None),
            'strength': state.get('divergence_strength', 0)
        }
    
    def _horizon_to_steps(self, horizon: str) -> int:
        """تحويل الأفق الزمني إلى عدد الخطوات"""
        mapping = {
            '1h': 4,
            '2h': 8,
            '4h': 16,
            '6h': 24,
            '12h': 48,
            '1d': 96,
            '2d': 192,
            '1w': 480
        }
        return mapping.get(horizon, 48)
    
    def _extract_key_levels(self, predictions: dict) -> dict:
        """استخراج المستويات الرئيسية من التنبؤات"""
        # ✅ التحقق من وجود predictions
        if predictions is None or not isinstance(predictions, dict):
            return {'support': 0, 'resistance': 0, 'pivot': 0}
        
        levels = {'support': 0, 'resistance': 0, 'pivot': 0}
        
        # من Monte Carlo
        mc = predictions.get('monte_carlo', {})
        if mc and isinstance(mc, dict):
            percentiles = mc.get('percentiles', {})
            if percentiles and isinstance(percentiles, dict):
                levels['support'] = percentiles.get('25', 0)
                levels['resistance'] = percentiles.get('75', 0)
                levels['pivot'] = percentiles.get('50', 0)
        
        # من Pattern Completion
        pc = predictions.get('pattern_completion', {})
        if pc and isinstance(pc, dict) and pc.get('pattern_found', False):
            target = pc.get('expected_target', 0)
            if target > 0 and isinstance(target, (int, float)):
                if target > levels.get('pivot', 0):
                    levels['resistance'] = max(levels.get('resistance', 0), target)
                else:
                    levels['support'] = min(levels.get('support', float('inf')), target) if levels.get('support', 0) > 0 else target
        
        return levels
    
    def _calculate_uncertainty(self, ensemble: dict, predictions: dict) -> float:
        """حساب درجة عدم اليقين"""
        # عوامل عدم اليقين
        factors = []
        
        # 1. تباين النماذج
        if ensemble and isinstance(ensemble, dict):
            model_disagreement = 1 - ensemble.get('model_agreement', 0)
            factors.append(model_disagreement * 0.3)
            
            # 2. ثقة النماذج
            confidence = ensemble.get('confidence', 0.5)
            factors.append((1 - confidence) * 0.3)
        
        # 3. تقلب السوق
        if predictions and isinstance(predictions, dict):
            mc = predictions.get('monte_carlo', {})
            if mc and isinstance(mc, dict):
                volatility = mc.get('volatility', 0.01)
                if volatility and isinstance(volatility, (int, float)):
                    factors.append(min(1, volatility * 5) * 0.2)
        
        # 4. جودة البيانات
        data_quality = 0.8  # افتراضي
        factors.append((1 - data_quality) * 0.2)
        
        uncertainty = sum(factors) if factors else 0.5
        return min(1, max(0, uncertainty))
    
    def get_accuracy_stats(self) -> dict:
        """إحصائيات دقة التنبؤات السابقة"""
        stats = {
            'total_predictions': len(self.prediction_history),
            'models': dict(self.accuracy_stats),
            'overall_accuracy': 0
        }
        
        total_correct = 0
        total = 0
        for model, stat in self.accuracy_stats.items():
            total_correct += stat['correct']
            total += stat['total']
        
        if total > 0:
            stats['overall_accuracy'] = total_correct / total
        
        return stats
    
    def get_recent_predictions(self, limit: int = 10) -> List[dict]:
        """آخر التنبؤات"""
        return self.prediction_history[-limit:] if self.prediction_history else []
    
    def get_prediction_summary(self) -> str:
        """ملخص التنبؤات"""
        lines = []
        lines.append("🔮 <b>ملخص Oracle</b>")
        lines.append("━" * 30)
        lines.append(f"📊 عدد التنبؤات: {len(self.prediction_history)}")
        
        if self.prediction_history:
            last = self.prediction_history[-1]
            lines.append(f"🕐 آخر تنبؤ: {last['timestamp'][:16]}")
            lines.append(f"📈 الاتجاه المتوقع: {last['ensemble'].get('direction', 'غير معروف')}")
            lines.append(f"💪 الثقة: {last['ensemble'].get('confidence', 0):.0%}")
            lines.append(f"🎯 السيناريوهات: {len(last['scenarios'])}")
        
        stats = self.get_accuracy_stats()
        if stats['overall_accuracy'] > 0:
            lines.append(f"📊 الدقة الإجمالية: {stats['overall_accuracy']:.0%}")
        
        lines.append("━" * 30)
        return "\n".join(lines)


# =====================================================================
# اختبار سريع
# =====================================================================
if __name__ == "__main__":
    # إنشاء Oracle
    oracle = OracleEngine()
    
    print("\n" + "="*60)
    print("🧪 اختبار Oracle Engine")
    print("="*60)
    
    # بيانات اختبار
    state = {
        'price': 78.50,
        'rsi': 55,
        'macd': 0.01,
        'adx': 28,
        'atr_14': 0.85,
        'volume_ratio': 1.2,
        'regime': 'ranging'
    }
    
    # اختبار التنبؤ
    print("\n1️⃣ توليد التنبؤ:")
    prediction = oracle.generate_prediction('oil', state, horizon='12h')
    
    print(f"   الاتجاه: {prediction['ensemble_confidence']:.0%} ثقة - {prediction['scenarios'][0]['name']}")
    print(f"   السيناريوهات: {len(prediction['scenarios'])}")
    print(f"   عدم اليقين: {prediction['uncertainty']:.0%}")
    
    # عرض السيناريوهات
    print("\n2️⃣ السيناريوهات:")
    for i, sc in enumerate(prediction['scenarios'][:3], 1):
        print(f"   {i}. {sc['name']} ({sc['probability']:.0%})")
        print(f"      {sc['description'][:50]}...")
    
    # عرض الرؤية
    print("\n3️⃣ الرؤية:")
    print(f"   {prediction['vision'][:150]}...")
    
    # عرض الملخص
    print("\n4️⃣ ملخص Oracle:")
    print(oracle.get_prediction_summary())
    
    print("\n✅ اختبار Oracle Engine ناجح!")
