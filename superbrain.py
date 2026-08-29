# -*- coding: utf-8 -*-
"""Tona SuperBrain: deterministic market-state and contradiction layer.
This module is advisory only; it never generates or mutates the SuperTrend/VPT signal.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class BrainAssessment:
    regime: str
    volatility: str
    directional_bias: str
    contradiction_level: str
    contradiction_count: int
    confidence: float
    uncertainty: float
    reasons: List[str]
    warnings: List[str]


def _num(v, default=None):
    try:
        x=float(v)
        return x if x == x and abs(x) != float('inf') else default
    except (TypeError,ValueError):
        return default

def _tf(analysis, name):
    t=analysis.get('timeframes',{}) if isinstance(analysis,dict) else {}
    return t.get(name,{}) if isinstance(t,dict) and isinstance(t.get(name,{}),dict) else {}

def assess(analysis: Dict[str,Any], signal: Optional[str]=None) -> Dict[str,Any]:
    """Build a market-state assessment from independent observations."""
    a=analysis or {}; tf5=_tf(a,'5m'); tf15=_tf(a,'15m'); tf1=_tf(a,'1h'); tf4=_tf(a,'4h')
    rsi=_num(tf15.get('rsi')); adx=_num(tf15.get('adx')); vol=_num(tf15.get('volume_ratio'))
    atr=_num(tf15.get('atr')); price=_num(a.get('price'));
    atr_pct=(atr/price*100) if atr is not None and price else None
    trends=[str(x.get('trend','')).lower() for x in (tf5,tf15,tf1,tf4) if x.get('trend') is not None]
    bull=sum(('up' in t or 'صاعد' in t or t in ('1','bullish')) for t in trends)
    bear=sum(('down' in t or 'هابط' in t or t in ('-1','bearish')) for t in trends)
    if bull>=3: bias='bullish'
    elif bear>=3: bias='bearish'
    elif bull==bear: bias='neutral'
    else: bias='mixed'
    if adx is not None and adx>=30: regime='trending'
    elif adx is not None and adx<=18: regime='ranging'
    else: regime='transition'
    if atr_pct is not None and atr_pct>=2.5: volatility='high'
    elif atr_pct is not None and atr_pct<=0.5: volatility='low'
    else: volatility='normal'
    reasons=[]; warnings=[]; contradictions=[]
    if len(set(trends))>1: contradictions.append('multi-timeframe trend disagreement')
    if signal in ('BUY','SELL'):
        expected='bullish' if signal=='BUY' else 'bearish'
        if bias not in (expected,'neutral'): contradictions.append('market bias conflicts with signal')
        if rsi is not None and ((signal=='BUY' and rsi>=70) or (signal=='SELL' and rsi<=30)):
            contradictions.append('momentum is extended against continuation')
        if adx is not None and adx<15: warnings.append('trend strength is very weak')
        if vol is not None and vol<0.7: warnings.append('volume confirmation is weak')
    reasons.append(f'market bias={bias}')
    reasons.append(f'regime={regime}')
    reasons.append(f'volatility={volatility}')
    c=len(contradictions)
    level='high' if c>=3 else 'medium' if c==2 else 'low' if c==1 else 'none'
    base=0.72
    if bias=='mixed': base-=0.12
    if regime=='ranging': base-=0.06
    if adx is not None and adx<15: base-=0.08
    base-=min(0.25,c*0.07)
    confidence=max(0.05,min(0.95,base)); uncertainty=1-confidence
    warnings.extend(contradictions)
    out=BrainAssessment(regime,volatility,bias,level,c,confidence,uncertainty,reasons,warnings)
    d=asdict(out); d['signal']=signal; d['strategy_locked']=True; d['strategy_engine']='SuperTrend/VPT-original'
    return d
