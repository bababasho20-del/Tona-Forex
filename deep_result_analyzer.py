"""
🔍 Deep Result Analyzer - التحليل العميق لنتائج الصفقات
👨‍💻 المطور: بسام الحوباني
💙 جزء من نظام تولين الاستشاري

⚠️ تنبيه هام: هذا المحلل يعمل فقط على بيانات حقيقية
❌ لا يستخدم أي بيانات وهمية أو محاكاة تحت أي ظرف
✅ إذا لم توجد بيانات كافية، يعيد رسالة واضحة للمستخدم
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import statistics
import json
import os
import logging

logger = logging.getLogger("TonaPrometheus")

class DeepResultAnalyzer:
    """
    تحليل عميق لنتائج الصفقات واستخلاص الأنماط
    يعمل فقط على بيانات حقيقية من قاعدة البيانات
    """
    
    def __init__(self, learning_db=None, supabase_db=None):
        self.learning_db = learning_db
        self.supabase_db = supabase_db
        self._trades_cache = {}
        logger.info("🔍 Deep Result Analyzer: جاهز للتحليل على بيانات حقيقية فقط")
    
    def analyze_all_trades(self, asset_type: Optional[str] = None) -> Dict:
        """
        تحليل جميع الصفقات واستخلاص الأنماط
        
        Args:
            asset_type: نوع الأصل (oil/silver) أو None للكل
        
        Returns:
            dict: التحليل الكامل أو رسالة خطأ واضحة
        """
        # جلب البيانات الحقيقية فقط
        trades = self._get_real_trades(asset_type)
        
        # التحقق الصارم من وجود بيانات
        if not trades:
            return self._no_data_response(asset_type)
        
        if len(trades) < 10:
            return self._insufficient_data_response(asset_type, len(trades))
        
        # تحليل البيانات الحقيقية
        return self._analyze_real_trades(trades, asset_type)
    
    def _get_real_trades(self, asset_type: Optional[str]) -> List[Dict]:
        """
        جلب الصفقات الحقيقية من قاعدة البيانات
        ❌ لا تستخدم أي بيانات وهمية تحت أي ظرف
        """
        # استخدام الكاش لتجنب جلب متكرر
        cache_key = asset_type or "all"
        if cache_key in self._trades_cache:
            return self._trades_cache[cache_key]
        
        trades = []
        
        # 1. محاولة جلب من Supabase
        if self._has_supabase():
            try:
                trades = self.supabase_db.get_trades(asset_type, limit=500)
                if trades and len(trades) > 0:
                    logger.info(f"✅ تم جلب {len(trades)} صفقة من Supabase")
                    self._trades_cache[cache_key] = trades
                    return trades
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب من Supabase: {e}")
        
        # 2. محاولة جلب من قاعدة التعلم المحلية
        if self._has_learning_db():
            try:
                if hasattr(self.learning_db, 'get_trades_by_asset'):
                    trades = self.learning_db.get_trades_by_asset(asset_type, limit=500)
                elif hasattr(self.learning_db, 'get_all_trades'):
                    trades = self.learning_db.get_all_trades(asset_type)
                elif hasattr(self.learning_db, 'get_trades'):
                    trades = self.learning_db.get_trades(asset_type, limit=500)
                
                if trades and len(trades) > 0:
                    logger.info(f"✅ تم جلب {len(trades)} صفقة من Learning DB")
                    self._trades_cache[cache_key] = trades
                    return trades
            except Exception as e:
                logger.warning(f"⚠️ فشل جلب من Learning DB: {e}")
        
        # 3. محاولة جلب من ملفات JSON المحلية
        trades = self._get_trades_from_files(asset_type)
        if trades and len(trades) > 0:
            logger.info(f"✅ تم جلب {len(trades)} صفقة من الملفات المحلية")
            self._trades_cache[cache_key] = trades
            return trades
        
        # 4. ❌ لا توجد بيانات
        logger.warning("❌ لا توجد بيانات حقيقية للتحليل")
        self._trades_cache[cache_key] = []
        return []
    
    def _has_supabase(self) -> bool:
        """التحقق من وجود اتصال بـ Supabase"""
        return (self.supabase_db is not None and 
                hasattr(self.supabase_db, 'connected') and 
                self.supabase_db.connected)
    
    def _has_learning_db(self) -> bool:
        """التحقق من وجود قاعدة تعلم محلية"""
        return self.learning_db is not None
    
    def _get_trades_from_files(self, asset_type: Optional[str]) -> List[Dict]:
        """جلب الصفقات من ملفات JSON المحلية"""
        trades = []
        
        try:
            if asset_type:
                files = [self._get_asset_file(asset_type)]
            else:
                files = ["trades_history_oil.json", "trades_history_silver.json"]
            
            for file_path in files:
                if not os.path.exists(file_path):
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_trades = data.get('trades', [])
                    if file_trades:
                        # إضافة نوع الأصل للصفقات
                        asset = 'eurusd' if 'eurusd' in file_path else 'usdjpy'
                        for t in file_trades:
                            if 'asset_type' not in t:
                                t['asset_type'] = asset
                        trades.extend(file_trades)
                        logger.info(f"📁 تم قراءة {len(file_trades)} صفقة من {file_path}")
            
            # تصفية حسب نوع الأصل إذا لزم الأمر
            if asset_type and trades:
                trades = [t for t in trades if t.get('asset_type') == asset_type]
            
            return trades
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ خطأ في قراءة ملف JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع في قراءة الملفات: {e}")
            return []
    
    def _get_asset_file(self, asset_type: str) -> str:
        """الحصول على اسم ملف الأصول"""
        return "trades_history_eurusd.json" if asset_type == "eurusd" else "trades_history_usdjpy.json"
    
    def _no_data_response(self, asset_type: Optional[str]) -> Dict:
        """رد عند عدم وجود بيانات"""
        asset_label = self._get_asset_label(asset_type)
        return {
            'status': 'no_data',
            'error': 'لا توجد بيانات',
            'message': f'لم يتم تنفيذ أي صفقات {asset_label} بعد. البوت لا يزال جديداً.',
            'trades_count': 0,
            'asset_type': asset_type or 'all'
        }
    
    def _insufficient_data_response(self, asset_type: Optional[str], count: int) -> Dict:
        """رد عند وجود بيانات غير كافية"""
        asset_label = self._get_asset_label(asset_type)
        return {
            'status': 'insufficient_data',
            'error': 'بيانات غير كافية',
            'message': f'لديك {count} صفقة {asset_label} فقط. يلزم 10 صفقات على الأقل للتحليل العميق.',
            'trades_count': count,
            'asset_type': asset_type or 'all'
        }
    
    def _get_asset_label(self, asset_type: Optional[str]) -> str:
        """الحصول على تسمية الأصل"""
        if not asset_type or asset_type == 'all':
            return ''
        return 'لليورو/دولار' if asset_type == 'eurusd' else 'للدولار/ين'
    
    def _analyze_real_trades(self, trades: List[Dict], asset_type: Optional[str]) -> Dict:
        """
        تحليل البيانات الحقيقية
        ✅ هذه هي الدالة الوحيدة التي تقوم بالتحليل الفعلي
        """
        return {
            "status": "success",
            "asset_type": asset_type or "all",
            "trades_count": len(trades),
            "total_stats": self._get_total_stats(trades),
            "best_entry_rsi": self._find_best_entry_rsi(trades),
            "best_sl_distance": self._find_best_sl_distance(trades),
            "best_timeframe_alignment": self._find_best_tf_alignment(trades),
            "worst_conditions": self._find_worst_conditions(trades),
            "best_trading_hours": self._find_best_trading_hours(trades),
            "correlations": self._find_correlations(trades),
            "success_patterns": self._find_success_patterns(trades),
            "failure_patterns": self._find_failure_patterns(trades)
        }
    
    def _get_total_stats(self, trades: List[Dict]) -> Dict:
        """إحصائيات عامة"""
        if not trades:
            return self._empty_stats()
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        losing = [t for t in trades if t.get('profit_dollars', 0) < 0]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(profitable),
            'losing_trades': len(losing),
            'win_rate': round(len(profitable) / len(trades) * 100, 1) if trades else 0,
            'avg_profit': round(sum(t.get('profit_dollars', 0) for t in trades) / len(trades), 2) if trades else 0,
            'avg_win': round(sum(t.get('profit_dollars', 0) for t in profitable) / len(profitable), 2) if profitable else 0,
            'avg_loss': round(sum(t.get('profit_dollars', 0) for t in losing) / len(losing), 2) if losing else 0,
            'max_profit': round(max((t.get('profit_dollars', 0) for t in trades), default=0), 2),
            'max_loss': round(min((t.get('profit_dollars', 0) for t in trades), default=0), 2)
        }
    
    def _empty_stats(self) -> Dict:
        """إحصائيات فارغة"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'max_profit': 0,
            'max_loss': 0
        }
    
    def _find_best_entry_rsi(self, trades: List[Dict]) -> Dict:
        """العثور على أفضل نطاق RSI للدخول"""
        if not trades:
            return {'error': 'لا توجد بيانات'}
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        losing = [t for t in trades if t.get('profit_dollars', 0) < 0]
        
        if not profitable:
            return {'error': 'لا توجد صفقات رابحة'}
        
        # تقسيم RSI إلى نطاقات
        ranges = {
            'oversold': (0, 30),
            'neutral_low': (30, 45),
            'neutral': (45, 55),
            'neutral_high': (55, 70),
            'overbought': (70, 100)
        }
        
        best_range = None
        best_win_rate = 0
        range_stats = {}
        
        for range_name, (low, high) in ranges.items():
            in_range = [t for t in trades if low <= t.get('entry_rsi', 50) < high]
            if in_range:
                wins = sum(1 for t in in_range if t.get('profit_dollars', 0) > 0)
                win_rate = round(wins / len(in_range) * 100, 1)
                range_stats[range_name] = {
                    'count': len(in_range),
                    'wins': wins,
                    'win_rate': win_rate
                }
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_range = range_name
        
        # حساب متوسط RSI للصفقات الرابحة والخاسرة
        avg_rsi_winning = round(sum(t.get('entry_rsi', 50) for t in profitable) / len(profitable), 1) if profitable else 0
        avg_rsi_losing = round(sum(t.get('entry_rsi', 50) for t in losing) / len(losing), 1) if losing else 0
        
        return {
            'best_range': best_range,
            'best_win_rate': best_win_rate,
            'avg_rsi_winning': avg_rsi_winning,
            'avg_rsi_losing': avg_rsi_losing,
            'range_stats': range_stats
        }
    
    def _find_best_sl_distance(self, trades: List[Dict]) -> Dict:
        """العثور على أفضل مسافة لوقف الخسارة"""
        if not trades:
            return {'error': 'لا توجد بيانات'}
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        losing = [t for t in trades if t.get('profit_dollars', 0) < 0]
        
        result = {}
        
        if profitable:
            avg_sl = sum(t.get('sl_distance', 1) for t in profitable) / len(profitable)
            result['avg_sl_winning'] = round(avg_sl, 2)
        else:
            result['avg_sl_winning'] = 0
        
        if losing:
            avg_sl = sum(t.get('sl_distance', 1) for t in losing) / len(losing)
            result['avg_sl_losing'] = round(avg_sl, 2)
        else:
            result['avg_sl_losing'] = 0
        
        if result.get('avg_sl_winning', 0) > 0 and result.get('avg_sl_losing', 0) > 0:
            result['recommendation'] = f'استخدم وقف خسارة بين {min(result["avg_sl_winning"], result["avg_sl_losing"]):.2f} و {max(result["avg_sl_winning"], result["avg_sl_losing"]):.2f}'
        else:
            result['recommendation'] = 'لا توجد بيانات كافية للتوصية'
        
        return result
    
    def _find_best_tf_alignment(self, trades: List[Dict]) -> Dict:
        """العثور على أفضل توافق للفريمات"""
        if not trades:
            return {'error': 'لا توجد بيانات'}
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        
        if not profitable:
            return {'error': 'لا توجد صفقات رابحة'}
        
        alignments = [t.get('tf_alignment', 0.5) for t in profitable]
        avg_alignment = round(sum(alignments) / len(alignments) * 100, 1)
        
        return {
            'avg_alignment_winning': avg_alignment,
            'recommendation': f'استهدف توافق فريمات > {avg_alignment:.1f}%' if avg_alignment > 0 else 'لا توجد بيانات كافية'
        }
    
    def _find_worst_conditions(self, trades: List[Dict]) -> Dict:
        """العثور على أسوأ الظروف للتداول"""
        if not trades:
            return {'error': 'لا توجد بيانات'}
        
        losing = [t for t in trades if t.get('profit_dollars', 0) < 0]
        
        if not losing:
            return {'error': 'لا توجد صفقات خاسرة'}
        
        # تحليل ظروف الخسارة
        phases = {}
        for t in losing:
            phase = t.get('market_phase', 'unknown')
            phases[phase] = phases.get(phase, 0) + 1
        
        worst_phase = max(phases, key=phases.get) if phases else 'unknown'
        avg_loss = round(sum(t.get('profit_dollars', 0) for t in losing) / len(losing), 2)
        
        return {
            'worst_phase': worst_phase,
            'avg_loss': avg_loss,
            'recommendation': f'تجنب التداول في ظروف {worst_phase}' if worst_phase != 'unknown' else 'لا توجد بيانات كافية'
        }
    
    def _find_best_trading_hours(self, trades: List[Dict]) -> Dict:
        """العثور على أفضل ساعات التداول"""
        if not trades:
            return {'error': 'لا توجد بيانات'}
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        
        if not profitable:
            return {'error': 'لا توجد صفقات رابحة'}
        
        # توزيع الساعات
        hour_stats = {}
        for t in profitable:
            hour = t.get('hour', 0)
            hour_stats[hour] = hour_stats.get(hour, 0) + 1
        
        if hour_stats:
            best_hour = max(hour_stats, key=hour_stats.get)
            top_hours = sorted(hour_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        else:
            best_hour = 0
            top_hours = []
        
        return {
            'best_hour': best_hour,
            'best_hour_trades': hour_stats.get(best_hour, 0),
            'top_hours': top_hours
        }
    
    def _find_correlations(self, trades: List[Dict]) -> List[str]:
        """العثور على ارتباطات بين العوامل والنتائج"""
        if not trades or len(trades) < 5:
            return ['لا توجد بيانات كافية لحساب الارتباطات']
        
        correlations = []
        
        # RSI vs Profit
        try:
            rsi_values = [t.get('entry_rsi', 50) for t in trades]
            profits = [t.get('profit_dollars', 0) for t in trades]
            if len(rsi_values) > 2 and len(profits) > 2:
                corr = statistics.correlation(rsi_values, profits)
                correlations.append(f"RSI والربح: {corr:.2f}")
        except:
            correlations.append("RSI والربح: غير قابل للحساب")
        
        # ADX vs Profit
        try:
            adx_values = [t.get('entry_adx', 15) for t in trades]
            if len(adx_values) > 2 and len(profits) > 2:
                corr = statistics.correlation(adx_values, profits)
                correlations.append(f"ADX والربح: {corr:.2f}")
        except:
            correlations.append("ADX والربح: غير قابل للحساب")
        
        # Volume vs Profit
        try:
            vol_values = [t.get('vol_ratio', 1) for t in trades]
            if len(vol_values) > 2 and len(profits) > 2:
                corr = statistics.correlation(vol_values, profits)
                correlations.append(f"الحجم والربح: {corr:.2f}")
        except:
            correlations.append("الحجم والربح: غير قابل للحساب")
        
        return correlations
    
    def _find_success_patterns(self, trades: List[Dict]) -> List[str]:
        """العثور على أنماط النجاح"""
        if not trades or len(trades) < 5:
            return ['لا توجد بيانات كافية']
        
        profitable = [t for t in trades if t.get('profit_dollars', 0) > 0]
        
        if len(profitable) < 3:
            return ['لا توجد صفقات رابحة كافية للتحليل']
        
        patterns = []
        
        # تحليل RSI
        try:
            avg_rsi = round(sum(t.get('entry_rsi', 50) for t in profitable) / len(profitable), 1)
            if 35 < avg_rsi < 55:
                patterns.append(f"RSI متوسط ({avg_rsi:.0f}) يعطي نتائج جيدة")
        except:
            pass
        
        # تحليل ADX
        try:
            avg_adx = round(sum(t.get('entry_adx', 15) for t in profitable) / len(profitable), 1)
            if avg_adx > 25:
                patterns.append(f"ADX قوي ({avg_adx:.0f}) يزيد فرص النجاح")
        except:
            pass
        
        # تحليل الحجم
        try:
            avg_vol = round(sum(t.get('vol_ratio', 1) for t in profitable) / len(profitable), 1)
            if avg_vol > 1.2:
                patterns.append(f"حجم تداول مرتفع ({avg_vol:.1f}x) يعزز النجاح")
        except:
            pass
        
        return patterns if patterns else ['لا توجد أنماط واضحة']
    
    def _find_failure_patterns(self, trades: List[Dict]) -> List[str]:
        """العثور على أنماط الفشل"""
        if not trades or len(trades) < 5:
            return ['لا توجد بيانات كافية']
        
        losing = [t for t in trades if t.get('profit_dollars', 0) < 0]
        
        if len(losing) < 3:
            return ['لا توجد صفقات خاسرة كافية للتحليل']
        
        patterns = []
        
        # تحليل ظروف الفشل
        try:
            phases = {}
            for t in losing:
                phase = t.get('market_phase', 'unknown')
                phases[phase] = phases.get(phase, 0) + 1
            
            worst_phase = max(phases, key=phases.get) if phases else 'unknown'
            if worst_phase != 'unknown' and worst_phase != 'trending':
                patterns.append(f"تجنب التداول في ظروف {worst_phase}")
        except:
            pass
        
        # تحليل RSI المتطرف
        try:
            extreme_rsi = [t for t in losing if t.get('entry_rsi', 50) > 70 or t.get('entry_rsi', 50) < 30]
            if extreme_rsi and len(extreme_rsi) >= 2:
                patterns.append("تجنب الدخول عند قيم RSI متطرفة (>70 أو <30)")
        except:
            pass
        
        return patterns if patterns else ['لا توجد أنماط واضحة للفشل']
