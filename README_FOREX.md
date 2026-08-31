# Forex Advisor Bot — EUR/USD وUSD/JPY

هذه حزمة مستقلة مبنية من المشروع السابق. تم استبدال الطبقات الأساسية التالية بنسخ Forex جديدة:

- `main.py`
- `risk_master.py`
- `market_analyzer.py`
- `advanced_indicators.py`
- `learning_db.py`
- `pattern_discovery.py`

تدعم النسخة الزوجين `EUR/USD` و`USD/JPY` فقط، وتعمل حاليًا في نطاق التحليل والمحاكاة. لا تحتوي الحزمة على تنفيذ صفقات حقيقية.

## الاختبارات

```bash
python3 -m py_compile main.py risk_master.py market_analyzer.py advanced_indicators.py learning_db.py pattern_discovery.py
python3 test_risk_master.py
python3 test_market_analyzer.py
python3 test_advanced_indicators.py
python3 test_learning_db.py
python3 test_pattern_discovery.py
```

## الحالة الحالية

الملفات الخارجية الأخرى مرفقة من الأرشيف الأصلي ولم تُحوّل كلها بعد. يجب تعديلها أو استبدالها قبل اعتبار البوت متوافقًا بالكامل مع Forex، خصوصًا:

```text
adaptive_learning_engine.py
pattern_analyzer.py
predictor.py
decision_matrix.py
db_manager.py
supabase_bridge.py
memory.py
context_memory.py
context_builder.py
learner.py
learning_system.py
```

كما أن ملفات المحادثة والمحركات الذكية تحتوي في النسخ الأصلية على افتراضات ورسائل قديمة، وستأتي بعد تثبيت طبقات البيانات والمخاطر والتحليل والتعلم.

## البيانات والذاكرة

لا تنقل قواعد البيانات أو ملفات الصفقات القديمة إلى هذه الحزمة. يجب استخدام قاعدة Forex جديدة، وتخزين كل سجل مع `instrument` و`symbol` و`session` و`provider` و`spread_pips` و`profit_after_cost`.

## الأسرار

ضع القيم الفعلية في متغيرات بيئة منصة التشغيل، ولا تضعها داخل Git. استخدم `.env.example` كمرجع للأسماء فقط.

## تحذير التشغيل

هذه الحزمة ليست جاهزة للتداول الحقيقي. يجب أولًا تعديل المحركات المتبقية، توحيد مزود البيانات، إضافة الأخبار والجلسات والتكاليف، ثم إجراء اختبارات تكامل وPaper Trading قبل أي قرار آخر.
