"""
☁️ Supabase Bridge - التخزين السحابي الدائم
📊 يحفظ جميع البيانات في Supabase بشكل دائم
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger("TonaPrometheus")

try:
    from supabase import create_client, Client
    SUPABASE_LIB_AVAILABLE = True
except ImportError:
    SUPABASE_LIB_AVAILABLE = False
    logger.warning("⚠️ مكتبة supabase غير مثبتة")

class SupabaseBridge:
    """جسر التخزين السحابي - يحفظ جميع البيانات في Supabase"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        self.client = None
        self.connected = False
        
        if not SUPABASE_LIB_AVAILABLE:
            logger.error("❌ مكتبة supabase غير مثبتة")
            return
        
        if not self.url or not self.key:
            logger.warning("⚠️ SUPABASE_URL أو SUPABASE_KEY غير موجودة")
            return
        
        try:
            self.client = create_client(self.url, self.key)
            self.connected = True
            logger.info("✅ تم الاتصال بـ Supabase بنجاح")
            self._test_connection()
        except Exception as e:
            logger.error(f"❌ فشل الاتصال بـ Supabase: {e}")
            self.connected = False
    
    def _test_connection(self):
        """اختبار الاتصال"""
        try:
            self.client.table('trades_full').select('id').limit(1).execute()
            logger.info("✅ تم التحقق من الاتصال - الجداول موجودة")
        except Exception as e:
            logger.warning(f"⚠️ فشل اختبار الاتصال: {e}")
    
    # ============================================================
    # ✅ حفظ الصفقات
    # ============================================================
    
    def save_trade(self, trade_data: Dict) -> bool:
        """حفظ صفقة في Supabase"""
        if not self.connected:
            logger.warning("⚠️ Supabase غير متصل")
            return False
        
        try:
            record = {
                'trade_id': trade_data.get('trade_id', ''),
                'asset_type': trade_data.get('asset_type', ''),
                'trade_type': trade_data.get('trade_type', ''),
                'entry_price': trade_data.get('entry_price', 0),
                'exit_price': trade_data.get('exit_price', 0),
                'profit_dollars': trade_data.get('profit_dollars', 0),
                'profit_pct': trade_data.get('profit_pct', 0),
                'exit_reason': trade_data.get('exit_reason', ''),
                'entry_time': trade_data.get('entry_time', datetime.now().isoformat()),
                'exit_time': trade_data.get('exit_time', ''),
                'duration_minutes': trade_data.get('duration_minutes', 0),
                'entry_rsi': trade_data.get('entry_rsi', 0),
                'entry_adx': trade_data.get('entry_adx', 0),
                'entry_macd': trade_data.get('entry_macd', 0),
                'entry_trend': trade_data.get('entry_trend', ''),
                'sl_price': trade_data.get('sl_price', 0),
                'tp_price': trade_data.get('tp_price', 0),
                'rr': trade_data.get('rr', 0)
            }
            
            result = self.client.table('trades_full').upsert(record).execute()
            logger.info(f"✅ تم حفظ الصفقة {trade_data.get('trade_id')} في Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ الصفقة: {e}")
            return False
    
    # ============================================================
    # ✅ حفظ اللقطات (هذه هي الدالة المهمة)
    # ============================================================
    
    def save_snapshot(self, snapshot_data: Dict) -> bool:
        """حفظ لقطة مراقبة في Supabase"""
        if not self.connected:
            logger.warning("⚠️ Supabase غير متصل")
            return False
        
        try:
            # تحويل indicators_json إلى string إذا كان dict
            indicators = snapshot_data.get('indicators', {})
            if isinstance(indicators, dict):
                indicators_json = json.dumps(indicators)
            else:
                indicators_json = str(indicators)
            
            record = {
                'trade_id': snapshot_data.get('trade_id', ''),
                'timestamp': snapshot_data.get('timestamp', datetime.now().isoformat()),
                'price': float(snapshot_data.get('price', 0)),
                'open_price': float(snapshot_data.get('open_price', 0)),
                'high_price': float(snapshot_data.get('high_price', 0)),
                'low_price': float(snapshot_data.get('low_price', 0)),
                'rsi': float(snapshot_data.get('rsi', 0)),
                'adx': float(snapshot_data.get('adx', 0)),
                'macd': float(snapshot_data.get('macd', 0)),
                'st_trend': snapshot_data.get('st_trend', 'neutral'),
                'bb_upper': float(snapshot_data.get('bb_upper', 0)),
                'bb_middle': float(snapshot_data.get('bb_middle', 0)),
                'bb_lower': float(snapshot_data.get('bb_lower', 0)),
                'vwap': float(snapshot_data.get('vwap', 0)),
                'volume_ratio': float(snapshot_data.get('volume_ratio', 0)),
                'profit_dollars': float(snapshot_data.get('profit_dollars', 0)),
                'profit_pct': float(snapshot_data.get('profit_pct', 0)),
                'warning_level': int(snapshot_data.get('warning_level', 0)),
                'fear_greed_index': int(snapshot_data.get('fear_greed_index', 0)),
                'market_regime': snapshot_data.get('market_regime', 'unknown'),
                'indicators_json': indicators_json
            }
            
            result = self.client.table('snapshots').insert(record).execute()
            logger.info(f"✅ تم حفظ اللقطة للصفقة {snapshot_data.get('trade_id')} في Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ اللقطة في Supabase: {e}")
            return False
    
    # ============================================================
    # ✅ دوال أخرى
    # ============================================================
    
    def save_pattern(self, pattern_data: Dict) -> bool:
        """حفظ نمط مكتشف"""
        if not self.connected:
            return False
        
        try:
            record = {
                'pattern_name': pattern_data.get('pattern_name', ''),
                'pattern_type': pattern_data.get('pattern_type', ''),
                'description': pattern_data.get('description', ''),
                'conditions': json.dumps(pattern_data.get('conditions', {})),
                'win_rate': pattern_data.get('win_rate', 0),
                'sample_count': pattern_data.get('sample_count', 0),
                'avg_profit': pattern_data.get('avg_profit', 0),
                'confidence': pattern_data.get('confidence', 0),
                'is_active': pattern_data.get('is_active', True)
            }
            
            result = self.client.table('discovered_patterns').upsert(record).execute()
            logger.info(f"✅ تم حفظ النمط {pattern_data.get('pattern_name')} في Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ النمط: {e}")
            return False
    
    def save_lesson(self, lesson_data: Dict) -> bool:
        """حفظ درس مستفاد"""
        if not self.connected:
            return False
        
        try:
            record = {
                'lesson_type': lesson_data.get('lesson_type', ''),
                'lesson_text': lesson_data.get('lesson_text', ''),
                'recommendation': lesson_data.get('recommendation', ''),
                'importance': lesson_data.get('importance', 0.5),
                'evidence_count': lesson_data.get('evidence_count', 1),
                'success_rate': lesson_data.get('success_rate', 0)
            }
            
            result = self.client.table('lessons_deep').insert(record).execute()
            logger.info(f"✅ تم حفظ الدرس في Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ الدرس: {e}")
            return False
    
    # ============================================================
    # ✅ استرجاع البيانات
    # ============================================================
    
    def get_trades(self, asset_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """استرجاع الصفقات"""
        if not self.connected:
            return []
        
        try:
            query = self.client.table('trades_full').select('*').order('entry_time', desc=True).limit(limit)
            if asset_type:
                query = query.eq('asset_type', asset_type)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ فشل استرجاع الصفقات: {e}")
            return []
    
    def get_snapshots(self, trade_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """استرجاع اللقطات"""
        if not self.connected:
            return []
        
        try:
            query = self.client.table('snapshots').select('*').order('timestamp', desc=True).limit(limit)
            if trade_id:
                query = query.eq('trade_id', trade_id)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ فشل استرجاع اللقطات: {e}")
            return []
    
    def get_statistics(self, asset_type: Optional[str] = None) -> Dict:
        """استرجاع الإحصائيات"""
        trades = self.get_trades(asset_type, 1000)
        
        if not trades:
            return {'total_trades': 0, 'win_rate': 0, 'total_profit': 0}
        
        total = len(trades)
        winning = len([t for t in trades if t.get('profit_dollars', 0) > 0])
        profits = [t.get('profit_dollars', 0) for t in trades]
        
        return {
            'total_trades': total,
            'winning_trades': winning,
            'losing_trades': total - winning,
            'win_rate': (winning / total * 100) if total > 0 else 0,
            'avg_profit': sum(profits) / total if total > 0 else 0,
            'max_profit': max(profits) if profits else 0,
            'max_loss': min(profits) if profits else 0,
            'total_profit': sum(profits)
        }
