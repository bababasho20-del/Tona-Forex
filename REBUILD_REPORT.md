# Tona AI — Full Rebuild Audit

## Architecture policy
- SuperTrend/VPT remains the protected signal engine.
- The 60-second scanner and 300-second monitoring cadence remain operational constants.
- AI/learning/intelligence layers are advisory and cannot mutate the scanner signal.
- Market intelligence now has a deterministic state/contradiction layer (`superbrain.py`).

## Repairs applied
1. Removed invalid legacy `omniscient_core_v5.py` and unreferenced patch artifacts.
2. Replaced invalid JSON comments in `config.json` with strict JSON.
3. Unified Supabase snapshot table references to `snapshots`.
4. Fixed SELL MAE/MFE directionality.
5. Added `asset_type` to the snapshot write allow-list.
6. Preserved real 5m/15m/1h/4h analysis configuration.
7. Added offline integrity audit (`healthcheck.py`).
8. Added market-state + contradiction intelligence without authority over the signal engine.

## Important runtime boundary
External services (MEXC, Supabase, Telegram, Groq/Gemini/Gist) cannot be fully integration-tested without the deployment environment and credentials. The included healthcheck intentionally performs only offline checks.

## Deployment recommendation
Run `python healthcheck.py` first, then deploy. Keep the previous project and database backup until live smoke tests confirm API credentials, Supabase schema, and message delivery.
