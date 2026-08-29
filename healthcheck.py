#!/usr/bin/env python3
"""Offline integrity audit for Tona. Does not call external APIs."""
from pathlib import Path
import ast,json,hashlib,re,sys
ROOT=Path(__file__).resolve().parent
errors=[]; warnings=[]
for p in sorted(ROOT.glob('*.py')):
    try: ast.parse(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{p.name}: {e}')
try: cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
except Exception as e: errors.append(f'config.json: {e}'); cfg={}
main=(ROOT/'main.py').read_text(encoding='utf-8')
for bad in ('monitoring_snapshots',):
    if bad in main: errors.append(f'legacy Supabase table name remains: {bad}')
if 'calculate_supertrend_vpt_correct' not in main: errors.append('SuperTrend/VPT function reference missing')
if 'SIGNAL_CHECK_INTERVAL = 60' not in main: warnings.append('SIGNAL_CHECK_INTERVAL declaration not found verbatim')
if 'MONITORING_INTERVAL = 300' not in main: warnings.append('MONITORING_INTERVAL declaration not found verbatim')
if not cfg.get('strategies',{}): errors.append('strategies config missing')
for asset in ('oil','silver'):
    if asset not in cfg.get('strategies',{}): errors.append(f'{asset} strategy missing')
    elif cfg['strategies'][asset].get('timeframes') != ['Min5','Min15','Min60','Hour4']: warnings.append(f'{asset}: unexpected analysis timeframe list')
print('TONA OFFLINE INTEGRITY AUDIT')
print('STATUS:', 'PASS' if not errors else 'FAIL')
print('PYTHON_FILES:', len(list(ROOT.glob('*.py'))))
print('MAIN_SHA256:', hashlib.sha256(main.encode()).hexdigest())
if errors:
    print('ERRORS:'); [print(' -',e) for e in errors]
if warnings:
    print('WARNINGS:'); [print(' -',w) for w in warnings]
sys.exit(1 if errors else 0)
