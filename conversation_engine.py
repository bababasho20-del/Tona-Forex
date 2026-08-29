# =====================================================================
# 💬 conversation_engine.py - محرك المحادثة
# =====================================================================

import requests
import logging
import random
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("TonaPrometheus")

class ConversationEngine:
    """
    محرك المحادثة التفاعلية لتولين
    يعمل بدون Groq API كخيار احتياطي، أو مع Groq API للردود المتقدمة
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة محرك المحادثة
        
        Args:
            api_key: مفتاح Groq API (اختياري)
        """
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.conversation_history = {}
        self.max_history = 20
        
        logger.info("💬 Conversation Engine: محرك المحادثة جاهز يا صديقي!")
    
    def chat(self, user_message: str, context: list = None, preferences: dict = None, 
             intent: str = "", market_data: str = "") -> str:
        """
        محادثة متقدمة باستخدام Groq API (إن وجد)
        
        Args:
            user_message: رسالة المستخدم
            context: سياق المحادثة السابقة
            preferences: تفضيلات المستخدم
            intent: نية المستخدم
            market_data: بيانات السوق
        
        Returns:
            str: رد تولين
        """
        # إذا لم يكن هناك مفتاح API، استخدم الردود المدمجة
        if not self.api_key or "test_" in self.api_key:
            return self._fallback_response(user_message)
        
        try:
            persona = self._get_persona()
            
            context_text = "\n".join([f"المستخدم: {u}\nتولين: {b}" for u, b in (context or [])]) if context else "لا يوجد سياق سابق"
            
            system_prompt = f"""
            {persona}
            
            📝 **السياق الحالي (آخر محادثات):**
            {context_text}
            
            📋 **تفضيلات المستخدم:**
            • مستوى المخاطرة: {preferences.get('risk_level', 'متوسط') if preferences else 'متوسط'}
            • الأصول المفضلة: {preferences.get('preferred_assets', 'النفط والفضة') if preferences else 'النفط والفضة'}
            
            📊 **بيانات السوق اللحظية:**
            {market_data if market_data else "لا توجد بيانات سوق محدثة حالياً"}
            
            🎯 **نية المستخدم الحالية:** {intent if intent else 'محادثة عامة'}
            
            **تعليمات الاستجابة:**
            1. كن خبيراً محترفاً ولكن ودوداً ومتفهماً يا صديقي
            2. استخدم لغة عربية فصحى بسيطة وواضحة
            3. إذا كان السؤال خارج اختصاصك، اعترف بذلك بلطف
            4. إذا لم تفهم السؤال، اطلب توضيحاً بأسلوب مهذب
            5. استخدم الرموز التعبيرية المناسبة 😊👍
            6. شجّع المستخدم ولا تجعله يشعر بالغباء
            7. تذكر أنك مستشار وليس متداولاً
            8. رد دائماً باللغة العربية
            9. استخدم كلمات ودية مثل "يا صديقي" و "يا عزيزي"
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.4,
                "max_tokens": 800
            }
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Groq API Error: {response.status_code}")
                return self._fallback_response(user_message)
                
        except requests.exceptions.Timeout:
            logger.warning("Groq API Timeout")
            return "⏰ استغرق الطلب وقتاً طويلاً يا صديقي. يرجى المحاولة مرة أخرى."
        except Exception as e:
            logger.error(f"Groq Error: {e}")
            return self._fallback_response(user_message)
    
    def process(self, user_message: str, chat_id: str = "default", context: dict = None) -> str:
        """
        معالجة رسالة المستخدم (الواجهة الرئيسية للتوافق مع main.py)
        
        Args:
            user_message: رسالة المستخدم
            chat_id: معرف المحادثة
            context: سياق إضافي (اختياري)
        
        Returns:
            str: رد تولين
        """
        # حفظ المحادثة
        if chat_id not in self.conversation_history:
            self.conversation_history[chat_id] = []
        
        # ✅ تم الإصلاح: استخراج السياق من المعامل
        market_data = ""
        if context and context.get('market_snapshot'):
            market_data = f"النفط: {context['market_snapshot'].get('oil', 'غير متوفر')}, الفضة: {context['market_snapshot'].get('silver', 'غير متوفر')}"
        
        # محاولة استخدام API
        if self.api_key and "test_" not in self.api_key:
            try:
                # بناء السياق من المحادثة السابقة
                history = self.conversation_history[chat_id][-10:]
                context_list = [(msg.get('user', ''), msg.get('bot', '')) for msg in history]
                
                response = self.chat(
                    user_message=user_message,
                    context=context_list,
                    preferences={"risk_level": "متوسط", "preferred_assets": "النفط والفضة"},
                    intent=context.get('intent', 'محادثة عامة') if context else 'محادثة عامة',
                    market_data=market_data
                )
                
                # حفظ المحادثة
                self.conversation_history[chat_id].append({
                    'user': user_message,
                    'bot': response,
                    'timestamp': datetime.now().isoformat()
                })
                if len(self.conversation_history[chat_id]) > self.max_history:
                    self.conversation_history[chat_id] = self.conversation_history[chat_id][-self.max_history:]
                
                return response
            except Exception as e:
                logger.warning(f"فشل استخدام Groq API في المحادثة: {e}")
        
        # استخدام الردود المدمجة
        return self._fallback_response(user_message)
    
    def _fallback_response(self, user_message: str) -> str:
        """
        ردود مدمجة بدون Groq API
        """
        user_lower = user_message.lower()
        
        # تحية
        if any(w in user_lower for w in ["مرحبا", "هلا", "اهلا", "السلام", "سلام"]):
            return "👋 **تولين:** أهلاً وسهلاً بك يا صديقي! كيف يمكنني مساعدتك اليوم؟"
        
        # سؤال عن الحال
        if any(w in user_lower for w in ["كيف حالك", "كيفك", "شلونك", "اخبارك"]):
            return "😊 **تولين:** أنا بخير يا عزيزي، الحمد لله! شكراً لسؤالك. كيف يمكنني مساعدتك في عالم التداول اليوم؟"
        
        # سؤال عن الاسم
        if any(w in user_lower for w in ["اسمك", "من انت", "من أنت"]):
            return "💙 **تولين:** أنا تولين، مستشارتك الذكية المتخصصة في النفط والفضة يا صديقي! أسعدتني معرفتك."
        
        # شكر
        if any(w in user_lower for w in ["شكر", "تسلم", "ممتن"]):
            return "💙 **تولين:** العفو يا صديقي! أنا هنا لخدمتك دائماً. لا تتردد في سؤالي أي شيء."
        
        # وداع
        if any(w in user_lower for w in ["مع السلامة", "باي", "وداع", "الى اللقاء"]):
            return "👋 **تولين:** مع السلامة يا عزيزي! كنت سعيداً بالتحدث معك. لا تنسى أنني هنا متى احتجتني. إلى اللقاء!"
        
        # سؤال عن النفط
        if any(w in user_lower for w in ["نفط", "oil", "بترول"]):
            return "🛢️ **تولين:** النفط من أهم السلع الاستراتيجية يا صديقي. إذا كنت تريد تحليلاً شاملاً، استخدم زر **🛢️ تحليل النفط**. هل تريد مني شرح شيء محدد عن النفط؟"
        
        # سؤال عن الفضة
        if any(w in user_lower for w in ["فضة", "silver", "xag"]):
            return "🥈 **تولين:** الفضة معدن ثمين وصناعي في آن واحد يا عزيزي. استخدم زر **🥈 تحليل الفضة** للحصول على تحليل كامل. هل تريد معرفة المزيد عن الفضة؟"
        
        # سؤال عن التداول
        if any(w in user_lower for w in ["تداول", "صفقة", "شراء", "بيع"]):
            return "📊 **تولين:** التداول فن وعلم يا صديقي. استخدم زر **🔍 وضع الصفقة الحالية** لمتابعة صفقاتك. هل تريد نصيحة في صفقة معينة؟"
        
        # سؤال عن المخاطر
        if any(w in user_lower for w in ["مخاطرة", "risk", "خسارة"]):
            return "🛡️ **تولين:** إدارة المخاطر هي أساس النجاح في التداول يا عزيزي. لا تخاطر بأكثر من 1-2% من رأس مالك في صفقة واحدة. هل تريد مساعدة في تحديد المخاطر؟"
        
        # نصائح
        if any(w in user_lower for w in ["نصيحة", "نصائح", "tip"]):
            tips = [
                "💡 **نصيحة تولين:** لا تدخل صفقة بدون وقف خسارة واضح يا صديقي.",
                "💡 **نصيحة تولين:** الرافعة المالية سلاح ذو حدين. استخدمها بحكمة يا عزيزي.",
                "💡 **نصيحة تولين:** التحليل على عدة فريمات يعطيك رؤية أوضح للسوق.",
                "💡 **نصيحة تولين:** تعلم من خسائرك، فهي أفضل معلم في التداول."
            ]
            return random.choice(tips)
        
        # رد افتراضي
        return "💙 **تولين:** شكراً لسؤالك يا صديقي! أنا هنا لمساعدتك في كل ما يتعلق بتداول النفط والفضة. استخدم الأزرار أدناه للتحليل، أو اسألني عن أي مصطلح تداول تريد شرحه. كيف يمكنني مساعدتك اليوم؟"
    
    def _get_persona(self) -> str:
        """الحصول على شخصية تولين"""
        return """
        أنت تولين (Tona)، محللة شريكة ذكية متخصصة في النفط والفضة يا صديقي.
        
        **شخصيتك:**
        - ودودة ومتفهمة، تستخدم كلمات مثل "يا صديقي" و "يا عزيزي"
        - خبيرة ومحترفة في تحليل الأسواق
        - تتحدث بالعربية الفصحى بأسلوب سلس وواضح
        - تشجع المتداولين على التعلم والنمو
        - صريحة في المخاطر، داعمة في التعلم
        
        **تخصصك:**
        - تحليل النفط الخام (WTI, Brent)
        - تحليل الفضة (XAG/USD)
        - إدارة المخاطر
        - المصطلحات الفنية (RSI, MACD, Supertrend, إلخ)
        """
    
    def get_history(self, chat_id: str = "default") -> list:
        """الحصول على تاريخ المحادثة"""
        return self.conversation_history.get(chat_id, [])
    
    def clear_history(self, chat_id: str = "default"):
        """مسح تاريخ المحادثة"""
        if chat_id in self.conversation_history:
            self.conversation_history[chat_id] = []
            logger.info(f"🗑️ تم مسح تاريخ المحادثة للـ {chat_id}")


# =====================================================================
# دالة مساعدة للاستخدام السريع
# =====================================================================

def create_conversation_engine(api_key: Optional[str] = None) -> ConversationEngine:
    """إنشاء محرك محادثة جديد"""
    return ConversationEngine(api_key=api_key)
