"""
PhysioAssist Oracle - User Mode v8.0
Regular user experience with working payment system
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, PreCheckoutQueryHandler
from anthropic import Anthropic
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = Anthropic()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'PhysioAssistBot')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', 'test_provider')  # Use real token in production

# Pricing
PRICES = {
    'basic': {'usd': 199, 'name': 'Basic Plan', 'duration': '1 month'},  # $1.99 in cents
    'premium': {'usd': 499, 'name': 'Premium Plan', 'duration': '3 months'},  # $4.99
    'pro': {'usd': 999, 'name': 'Pro Plan', 'duration': '1 year'}  # $9.99
}

# Free assessment limit
FREE_ASSESSMENTS_LIMIT = 1


class UserModeBot:
    """User mode bot with payment system"""
    
    def __init__(self):
        self.user_sessions = {}
        self.treatment_plans = {}
        self.user_subscriptions = {}  # Track subscriptions
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id
        
        # Initialize user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'language': None,
                'stage': 'language_selection',
                'condition': None,
                'severity': None,
                'messages': [],
                'free_assessments': 0,
                'subscription_level': 'free',
                'subscription_expires': None
            }
        
        # Welcome message
        welcome_msg = (
            "🏥 **Welcome to PhysioAssist Oracle v8.0**\n\n"
            "Get personalized physical therapy guidance!\n\n"
            "📊 Your Status:\n"
            f"• Free Assessments: {self.user_sessions[user_id]['free_assessments']}/{FREE_ASSESSMENTS_LIMIT}\n"
            f"• Subscription: {self.user_sessions[user_id]['subscription_level'].upper()}\n\n"
            "Select your language:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    
    async def language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == 'lang_en':
            language = 'English'
            greeting = (
                "Great! Let's start your assessment.\n\n"
                "Tell me: What brings you here today? What pain or discomfort are you experiencing?"
            )
        else:
            language = 'Arabic'
            greeting = (
                "رائع! لنبدأ التقييم.\n\n"
                "أخبرني: ما الذي يجعلك هنا اليوم؟ ما نوع الألم أو الانزعاج الذي تشعر به؟"
            )
        
        self.user_sessions[user_id]['language'] = language
        self.user_sessions[user_id]['stage'] = 'free_chat'
        
        await query.edit_message_text(text=greeting)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if user_id not in self.user_sessions:
            await self.start(update, context)
            return
        
        session = self.user_sessions[user_id]
        language = session.get('language', 'English')
        
        # Free chat stage
        if session['stage'] == 'free_chat':
            await self.free_chat_handler(update, context, user_id, user_message, language)
        
        # Assessment stage
        elif session['stage'] == 'assessment':
            await self.assessment_handler(update, context, user_id, user_message, language)
    
    async def free_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               user_id: int, message: str, language: str):
        """Handle free chat with AI"""
        
        # Store message
        self.user_sessions[user_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        try:
            system_prompt = self._get_system_prompt(language)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=system_prompt,
                messages=self.user_sessions[user_id]['messages']
            )
            
            ai_message = response.content[0].text
            
            # Store AI response
            self.user_sessions[user_id]['messages'].append({
                'role': 'assistant',
                'content': ai_message
            })
            
            # Send response
            await update.message.reply_text(ai_message)
            
            # Check if we should move to assessment
            if len(self.user_sessions[user_id]['messages']) >= 6:
                await self.move_to_assessment(update, context, user_id, language)
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_msg = "Sorry, I encountered an error. Please try again." if language == 'English' else "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى."
            await update.message.reply_text(error_msg)
    
    async def move_to_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, language: str):
        """Move to assessment stage"""
        
        self.user_sessions[user_id]['stage'] = 'assessment'
        
        if language == 'English':
            msg = (
                "📋 **Now let's do a proper assessment.**\n\n"
                "On a scale of 1-10, how severe is your pain?\n\n"
                "1️⃣ Mild (1-3)\n"
                "2️⃣ Moderate (4-6)\n"
                "3️⃣ Severe (7-10)"
            )
        else:
            msg = (
                "📋 **الآن دعنا نجري تقييماً صحيحاً.**\n\n"
                "على مقياس من 1-10، ما مدى شدة الألم؟\n\n"
                "1️⃣ خفيف (1-3)\n"
                "2️⃣ متوسط (4-6)\n"
                "3️⃣ شديد (7-10)"
            )
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ Mild" if language == 'English' else "1️⃣ خفيف", callback_data='severity_mild')],
            [InlineKeyboardButton("2️⃣ Moderate" if language == 'English' else "2️⃣ متوسط", callback_data='severity_moderate')],
            [InlineKeyboardButton("3️⃣ Severe" if language == 'English' else "3️⃣ شديد", callback_data='severity_severe')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(msg, reply_markup=reply_markup)
    
    async def assessment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, message: str, language: str):
        """Handle assessment questions"""
        
        self.user_sessions[user_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        msg = "Thank you for your response. Analyzing your condition..." if language == 'English' else "شكراً على إجابتك. جاري تحليل حالتك..."
        await update.message.reply_text(msg)
    
    async def severity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle severity selection"""
        query = update.callback_query
        user_id = query.from_user.id
        language = self.user_sessions[user_id]['language']
        
        severity_map = {
            'severity_mild': 'mild',
            'severity_moderate': 'moderate',
            'severity_severe': 'severe'
        }
        
        severity = severity_map.get(query.data, 'moderate')
        self.user_sessions[user_id]['severity'] = severity
        
        # Check if user has free assessment available
        free_assessments = self.user_sessions[user_id]['free_assessments']
        subscription = self.user_sessions[user_id]['subscription_level']
        
        if free_assessments >= FREE_ASSESSMENTS_LIMIT and subscription == 'free':
            # User needs to subscribe
            await self.show_payment_options(query, user_id, language)
        else:
            # User can proceed
            self.user_sessions[user_id]['free_assessments'] += 1
            await self.generate_treatment_plan(query, user_id, language, severity)
    
    async def show_payment_options(self, query, user_id: int, language: str):
        """Show payment options"""
        
        if language == 'English':
            msg = (
                "💳 **Upgrade Your Plan**\n\n"
                "You've used your free assessment. Choose a plan to continue:\n\n"
                "🔹 **Basic Plan** - $1.99/month\n"
                "   • Unlimited assessments\n"
                "   • Treatment plans\n"
                "   • 1 month access\n\n"
                "🔹 **Premium Plan** - $4.99/3 months\n"
                "   • Everything in Basic\n"
                "   • Priority support\n"
                "   • 3 months access\n\n"
                "🔹 **Pro Plan** - $9.99/year\n"
                "   • Everything in Premium\n"
                "   • Exclusive content\n"
                "   • 1 year access"
            )
        else:
            msg = (
                "💳 **ترقية خطتك**\n\n"
                "لقد استخدمت تقييمك المجاني. اختر خطة للمتابعة:\n\n"
                "🔹 **الخطة الأساسية** - 1.99 دولار/شهر\n"
                "   • تقييمات غير محدودة\n"
                "   • خطط العلاج\n"
                "   • دخول لمدة شهر\n\n"
                "🔹 **الخطة المميزة** - 4.99 دولار/3 أشهر\n"
                "   • كل شيء في الأساسية\n"
                "   • دعم أولوي\n"
                "   • دخول لمدة 3 أشهر\n\n"
                "🔹 **خطة برو** - 9.99 دولار/سنة\n"
                "   • كل شيء في المميزة\n"
                "   • محتوى حصري\n"
                "   • دخول لمدة سنة"
            )
        
        keyboard = [
            [InlineKeyboardButton("💳 Basic - $1.99" if language == 'English' else "💳 أساسية - 1.99$", callback_data='pay_basic')],
            [InlineKeyboardButton("💳 Premium - $4.99" if language == 'English' else "💳 مميزة - 4.99$", callback_data='pay_premium')],
            [InlineKeyboardButton("💳 Pro - $9.99" if language == 'English' else "💳 برو - 9.99$", callback_data='pay_pro')],
            [InlineKeyboardButton("❌ Cancel" if language == 'English' else "❌ إلغاء", callback_data='cancel_payment')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=msg, reply_markup=reply_markup)
    
    async def handle_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment button clicks"""
        query = update.callback_query
        user_id = query.from_user.id
        language = self.user_sessions[user_id]['language']
        
        if query.data == 'cancel_payment':
            await query.edit_message_text(text="Payment cancelled." if language == 'English' else "تم إلغاء الدفع.")
            return
        
        # Extract plan from callback
        plan_map = {
            'pay_basic': 'basic',
            'pay_premium': 'premium',
            'pay_pro': 'pro'
        }
        
        plan = plan_map.get(query.data)
        if not plan:
            return
        
        # Prepare invoice
        title = PRICES[plan]['name']
        description = f"PhysioAssist {PRICES[plan]['name']} - {PRICES[plan]['duration']}"
        payload = f"physio_{plan}_{user_id}_{datetime.now().timestamp()}"
        currency = "USD"
        price = PRICES[plan]['usd']
        
        prices = [LabeledPrice(label=title, amount=price)]
        
        try:
            await context.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token=PAYMENT_PROVIDER_TOKEN,
                currency=currency,
                prices=prices,
                start_parameter=f"pay_{plan}"
            )
            logger.info(f"✅ Invoice sent to {user_id} for {plan} plan")
        except Exception as e:
            logger.error(f"❌ Error sending invoice: {e}")
            error_msg = f"Error processing payment: {str(e)}" if language == 'English' else f"خطأ في معالجة الدفع: {str(e)}"
            await query.message.reply_text(error_msg)
    
    async def pre_checkout_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pre-checkout query"""
        query = update.pre_checkout_query
        
        # Verify the payment
        if query.invoice_payload.startswith('physio_'):
            await query.answer(ok=True)
            logger.info(f"✅ Pre-checkout verified for {query.from_user.id}")
        else:
            await query.answer(ok=False, error_message="Invalid payment")
            logger.error(f"❌ Invalid payment from {query.from_user.id}")
    
    async def successful_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle successful payment"""
        user_id = update.message.from_user.id
        language = self.user_sessions[user_id]['language']
        payment = update.message.successful_payment
        
        # Extract plan from payload
        payload_parts = payment.invoice_payload.split('_')
        plan = payload_parts[1] if len(payload_parts) > 1 else 'basic'
        
        # Update subscription
        self.user_sessions[user_id]['subscription_level'] = plan
        
        # Calculate expiration date
        if plan == 'basic':
            expires = datetime.now() + timedelta(days=30)
        elif plan == 'premium':
            expires = datetime.now() + timedelta(days=90)
        else:  # pro
            expires = datetime.now() + timedelta(days=365)
        
        self.user_sessions[user_id]['subscription_expires'] = expires
        
        # Confirm payment
        msg = (
            f"✅ **Payment Successful!**\n\n"
            f"Thank you for upgrading to {PRICES[plan]['name']}!\n"
            f"Valid until: {expires.strftime('%Y-%m-%d')}\n\n"
            f"Now you can:\n"
            f"• Get unlimited assessments\n"
            f"• Download full treatment plans\n"
            f"• Access all features\n\n"
            f"Type /start to continue!"
        ) if language == 'English' else (
            f"✅ **تم الدفع بنجاح!**\n\n"
            f"شكراً لترقيتك إلى {PRICES[plan]['name']}!\n"
            f"صالح حتى: {expires.strftime('%Y-%m-%d')}\n\n"
            f"الآن يمكنك:\n"
            f"• الحصول على تقييمات غير محدودة\n"
            f"• تحميل خطط العلاج الكاملة\n"
            f"• الوصول إلى جميع الميزات\n\n"
            f"اكتب /start للمتابعة!"
        )
        
        await update.message.reply_text(msg)
        logger.info(f"✅ Payment confirmed for {user_id}: {plan} plan")
    
    async def generate_treatment_plan(self, query, user_id: int, language: str, severity: str):
        """Generate complete treatment plan"""
        
        try:
            # Create treatment plan
            plan = self._generate_plan(severity, language)
            
            # Send plan
            msg = plan
            await query.edit_message_text(text=msg[:4096])
            
            # Send additional info
            additional_msg = (
                "✅ **Treatment plan generated successfully!**\n\n"
                "📥 You can now:\n"
                "1️⃣ Download PDF Report\n"
                "2️⃣ View Diagnostic Videos\n"
                "3️⃣ Start Exercise Program\n"
                "4️⃣ Get Medication Recommendations"
            ) if language == 'English' else (
                "✅ **تم إنشاء خطة العلاج بنجاح!**\n\n"
                "📥 يمكنك الآن:\n"
                "1️⃣ تحميل تقرير PDF\n"
                "2️⃣ عرض الفيديوهات التشخيصية\n"
                "3️⃣ بدء برنامج التمارين\n"
                "4️⃣ الحصول على توصيات الأدوية"
            )
            
            await query.message.reply_text(additional_msg)
            
            # Store plan
            self.treatment_plans[user_id] = plan
            logger.info(f"✅ Treatment plan generated for {user_id}")
        
        except Exception as e:
            logger.error(f"Error generating treatment plan: {e}")
            error_msg = f"Sorry, I couldn't generate your treatment plan." if language == 'English' else f"عذراً، لم أتمكن من إنشاء خطة العلاج."
            await query.message.reply_text(error_msg)
    
    def _generate_plan(self, severity: str, language: str) -> str:
        """Generate treatment plan"""
        
        if language == 'Arabic':
            return f"""
📋 **خطة العلاج الشاملة (شدة: {severity})**

🛡️ **1. نصائح منع التفاقم:**
• خذ فترات راحة منتظمة كل ساعة
• حافظ على وضعية صحيحة
• تجنب الحركات المفاجئة
• استخدم كمادات دافئة

🏥 **2. العلاجات المنزلية:**
• كمادات دافئة (15-20 دقيقة)
• تدليك برفق
• حمام دافئ للاسترخاء
• رفع الطرف المصاب

💪 **3. برنامج التمارين:**
• المرحلة 1: تمارين تمدد خفيفة
• المرحلة 2: تقوية تدريجية
• المرحلة 3: تمارين وظيفية

⚠️ **4. التحذيرات:**
• توقف إذا شعرت بألم شديد
• لا ترفع أشياء ثقيلة
• استشر الطبيب إذا استمر الألم

🛒 **5. منتجات موصى بها:**
• وسائد دعم
• أجهزة تدليك
• كمادات حرارية

💊 **6. أدوية آمنة:**
• Paracetamol (500-1000 ملغ)
• Ibuprofen (200-400 ملغ)
• مرخيات العضلات (بوصفة طبية)

📞 **تنبيه:** هذا ليس تشخيصاً طبياً. استشر طبيبك دائماً!
            """
        else:
            return f"""
📋 **Your Comprehensive Treatment Plan (Severity: {severity})**

🛡️ **1. Prevention Tips:**
• Take regular breaks every hour
• Maintain good posture
• Avoid sudden movements
• Use warm compresses

🏥 **2. Home Remedies:**
• Warm compress (15-20 minutes)
• Gentle massage
• Warm bath for relaxation
• Elevate affected limb

💪 **3. Exercise Program:**
• Phase 1: Light stretching
• Phase 2: Gradual strengthening
• Phase 3: Functional exercises

⚠️ **4. Warnings:**
• Stop if severe pain occurs
• Don't lift heavy objects
• Consult doctor if pain persists

🛒 **5. Recommended Products:**
• Support pillows
• Massage devices
• Heating pads

💊 **6. Safe Medications:**
• Paracetamol (500-1000 mg)
• Ibuprofen (200-400 mg)
• Muscle relaxants (prescription only)

📞 **Disclaimer:** This is not a medical diagnosis. Always consult your doctor!
            """
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for AI"""
        
        if language == 'Arabic':
            return """أنت مساعد طبي ذكي متخصص في العلاج الطبيعي. 
            
قواعدك:
1. استمع بعناية لأعراض المريض
2. اسأ أسئلة توضيحية لفهم الحالة بشكل أفضل
3. تجنب المصطلحات الطبية المعقدة
4. كن متعاطفاً وداعماً
5. لا تعطي تشخيصاً نهائياً - أنت تساعد فقط
6. استخدم لغة بسيطة وسهلة الفهم
7. ركز على الأعراض والتاريخ الطبي
            """
        else:
            return """You are an intelligent medical assistant specializing in physical therapy.
            
Your rules:
1. Listen carefully to patient symptoms
2. Ask clarifying questions to better understand the condition
3. Avoid complex medical terminology
4. Be empathetic and supportive
5. Don't give final diagnosis - you're just helping
6. Use simple and easy-to-understand language
7. Focus on symptoms and medical history
            """
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")


async def main():
    """Main function"""
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Create bot instance
    bot = UserModeBot()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.language_selection, pattern='^lang_'))
    app.add_handler(CallbackQueryHandler(bot.severity_selection, pattern='^severity_'))
    app.add_handler(CallbackQueryHandler(bot.handle_payment, pattern='^(pay_|cancel_)'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_handler(PreCheckoutQueryHandler(bot.pre_checkout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, bot.successful_payment_handler))
    app.add_error_handler(bot.error_handler)
    
    # Start bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ USER BOT STARTED SUCCESSFULLY!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
