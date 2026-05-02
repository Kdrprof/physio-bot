"""
PhysioAssist Oracle v8.0 - Smart Hybrid Bot
One bot with Admin/User mode selection
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
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', 'test_provider')

# Admin ID - Replace with your Telegram ID
ADMIN_ID = 8660311978

# Pricing
PRICES = {
    'basic': {'usd': 199, 'name': 'Basic Plan', 'duration': '1 month'},
    'premium': {'usd': 499, 'name': 'Premium Plan', 'duration': '3 months'},
    'pro': {'usd': 999, 'name': 'Pro Plan', 'duration': '1 year'}
}

FREE_ASSESSMENTS_LIMIT = 1


class HybridSmartBot:
    """Smart hybrid bot with mode selection"""
    
    def __init__(self):
        self.user_sessions = {}
        self.treatment_plans = {}
        self.user_subscriptions = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command with mode selection"""
        user_id = update.effective_user.id
        is_admin = user_id == ADMIN_ID
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'language': None,
            'stage': 'mode_selection',
            'mode': None,  # 'admin' or 'user'
            'condition': None,
            'severity': None,
            'messages': [],
            'is_admin': is_admin,
            'subscription_level': 'premium' if is_admin else 'free',
            'free_assessments': 0,
            'subscription_expires': None
        }
        
        # Welcome message
        welcome_msg = (
            "🏥 **PhysioAssist Oracle v8.0**\n\n"
            "Welcome! Please select your testing mode:\n\n"
            "👨‍💼 **Admin Mode** - Full access, debug enabled, no payment\n"
            "👤 **User Mode** - Regular experience with payment system\n\n"
            "Choose one to get started:"
        )
        
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
            [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')],
            [InlineKeyboardButton("ℹ️ About Modes", callback_data='mode_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    
    async def mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mode selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == 'mode_info':
            await self.show_mode_info(query)
            return
        
        # Set mode
        mode = 'admin' if query.data == 'mode_admin' else 'user'
        self.user_sessions[user_id]['mode'] = mode
        
        # Check if user is actually admin
        if mode == 'admin' and user_id != ADMIN_ID:
            await query.answer("❌ Admin mode is only for administrators!", show_alert=True)
            return
        
        # Move to language selection
        await self.show_language_selection(query, user_id, mode)
    
    async def show_mode_info(self, query):
        """Show information about modes"""
        
        info_msg = """
🔍 **Mode Comparison:**

**👨‍💼 Admin Mode:**
✅ Full access to all features
✅ No payment required
✅ Unlimited assessments
✅ Debug information displayed
✅ Error details shown
✅ Perfect for testing and development

**👤 User Mode:**
✅ Regular user experience
✅ 1 free assessment
✅ Payment system active
✅ Subscription management
✅ Feature restrictions based on plan
✅ Real-world testing

**Choose Admin Mode if:** You want to test everything
**Choose User Mode if:** You want to test the payment system

Which mode would you like?
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
            [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=info_msg, reply_markup=reply_markup)
    
    async def show_language_selection(self, query, user_id: int, mode: str):
        """Show language selection"""
        
        mode_label = "ADMIN MODE" if mode == 'admin' else "USER MODE"
        
        msg = f"""
🏥 **PhysioAssist Oracle v8.0**

Mode: {mode_label}
User ID: {user_id}

Please select your language:
        """
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=msg, reply_markup=reply_markup)
    
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
        
        mode = self.user_sessions[user_id]['mode']
        is_admin = self.user_sessions[user_id]['is_admin']
        
        if is_admin and mode == 'admin':
            greeting += "\n\n🐛 **DEBUG MODE ENABLED**\n"
            greeting += f"Language: {language}\n"
            greeting += f"Mode: ADMIN\n"
            greeting += f"Session ID: {user_id}\n"
        
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
        mode = session.get('mode')
        is_admin = session.get('is_admin', False)
        
        # Free chat stage
        if session['stage'] == 'free_chat':
            await self.free_chat_handler(update, context, user_id, user_message, language, mode, is_admin)
        
        # Assessment stage
        elif session['stage'] == 'assessment':
            await self.assessment_handler(update, context, user_id, user_message, language, mode, is_admin)
    
    async def free_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               user_id: int, message: str, language: str, mode: str, is_admin: bool):
        """Handle free chat with AI"""
        
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
            
            self.user_sessions[user_id]['messages'].append({
                'role': 'assistant',
                'content': ai_message
            })
            
            # Add debug info for admin
            if is_admin and mode == 'admin':
                ai_message += "\n\n🐛 **DEBUG INFO:**\n"
                ai_message += f"Messages: {len(self.user_sessions[user_id]['messages'])}\n"
                ai_message += f"Mode: ADMIN\n"
                ai_message += f"Tokens: ~{len(ai_message.split())}\n"
            
            await update.message.reply_text(ai_message)
            
            # Check if we should move to assessment
            if len(self.user_sessions[user_id]['messages']) >= 6:
                await self.move_to_assessment(update, context, user_id, language, mode, is_admin)
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_msg = f"Sorry, I encountered an error: {str(e)}" if language == 'English' else f"عذراً، حدث خطأ: {str(e)}"
            if is_admin and mode == 'admin':
                error_msg += f"\n\n🐛 **ERROR:** {str(e)}"
            await update.message.reply_text(error_msg)
    
    async def move_to_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, language: str, mode: str, is_admin: bool):
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
        
        if is_admin and mode == 'admin':
            msg += "\n\n🐛 **DEBUG:** Assessment stage activated"
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ Mild" if language == 'English' else "1️⃣ خفيف", callback_data='severity_mild')],
            [InlineKeyboardButton("2️⃣ Moderate" if language == 'English' else "2️⃣ متوسط", callback_data='severity_moderate')],
            [InlineKeyboardButton("3️⃣ Severe" if language == 'English' else "3️⃣ شديد", callback_data='severity_severe')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(msg, reply_markup=reply_markup)
    
    async def assessment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, message: str, language: str, mode: str, is_admin: bool):
        """Handle assessment questions"""
        
        self.user_sessions[user_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        msg = "Thank you for your response. Analyzing your condition..." if language == 'English' else "شكراً على إجابتك. جاري تحليل حالتك..."
        
        if is_admin and mode == 'admin':
            msg += "\n\n🐛 **DEBUG:** Assessment response recorded"
        
        await update.message.reply_text(msg)
    
    async def severity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle severity selection"""
        query = update.callback_query
        user_id = query.from_user.id
        language = self.user_sessions[user_id]['language']
        mode = self.user_sessions[user_id]['mode']
        is_admin = self.user_sessions[user_id]['is_admin']
        
        severity_map = {
            'severity_mild': 'mild',
            'severity_moderate': 'moderate',
            'severity_severe': 'severe'
        }
        
        severity = severity_map.get(query.data, 'moderate')
        self.user_sessions[user_id]['severity'] = severity
        
        # Check access based on mode
        if mode == 'admin':
            # Admin mode - always allow
            await self.generate_treatment_plan(query, user_id, language, severity, mode, is_admin)
        else:
            # User mode - check subscription
            free_assessments = self.user_sessions[user_id]['free_assessments']
            subscription = self.user_sessions[user_id]['subscription_level']
            
            if free_assessments >= FREE_ASSESSMENTS_LIMIT and subscription == 'free':
                # User needs to subscribe
                await self.show_payment_options(query, user_id, language)
            else:
                # User can proceed
                self.user_sessions[user_id]['free_assessments'] += 1
                await self.generate_treatment_plan(query, user_id, language, severity, mode, is_admin)
    
    async def show_payment_options(self, query, user_id: int, language: str):
        """Show payment options"""
        
        if language == 'English':
            msg = (
                "💳 **Upgrade Your Plan**\n\n"
                "You've used your free assessment. Choose a plan:\n\n"
                "🔹 **Basic** - $1.99/month\n"
                "🔹 **Premium** - $4.99/3 months\n"
                "🔹 **Pro** - $9.99/year"
            )
        else:
            msg = (
                "💳 **ترقية خطتك**\n\n"
                "لقد استخدمت تقييمك المجاني. اختر خطة:\n\n"
                "🔹 **أساسية** - 1.99 دولار/شهر\n"
                "🔹 **مميزة** - 4.99 دولار/3 أشهر\n"
                "🔹 **برو** - 9.99 دولار/سنة"
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
        
        # Extract plan
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
        description = f"PhysioAssist {PRICES[plan]['name']}"
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
            logger.info(f"Invoice sent to {user_id} for {plan}")
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            error_msg = f"Error: {str(e)}" if language == 'English' else f"خطأ: {str(e)}"
            await query.message.reply_text(error_msg)
    
    async def pre_checkout_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pre-checkout query"""
        query = update.pre_checkout_query
        
        if query.invoice_payload.startswith('physio_'):
            await query.answer(ok=True)
        else:
            await query.answer(ok=False, error_message="Invalid payment")
    
    async def successful_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle successful payment"""
        user_id = update.message.from_user.id
        language = self.user_sessions[user_id]['language']
        payment = update.message.successful_payment
        
        # Extract plan
        payload_parts = payment.invoice_payload.split('_')
        plan = payload_parts[1] if len(payload_parts) > 1 else 'basic'
        
        # Update subscription
        self.user_sessions[user_id]['subscription_level'] = plan
        
        # Calculate expiration
        if plan == 'basic':
            expires = datetime.now() + timedelta(days=30)
        elif plan == 'premium':
            expires = datetime.now() + timedelta(days=90)
        else:
            expires = datetime.now() + timedelta(days=365)
        
        self.user_sessions[user_id]['subscription_expires'] = expires
        
        # Confirm
        msg = (
            f"✅ **Payment Successful!**\n\n"
            f"Plan: {PRICES[plan]['name']}\n"
            f"Valid until: {expires.strftime('%Y-%m-%d')}\n\n"
            f"Type /start to continue!"
        ) if language == 'English' else (
            f"✅ **تم الدفع بنجاح!**\n\n"
            f"الخطة: {PRICES[plan]['name']}\n"
            f"صالح حتى: {expires.strftime('%Y-%m-%d')}\n\n"
            f"اكتب /start للمتابعة!"
        )
        
        await update.message.reply_text(msg)
    
    async def generate_treatment_plan(self, query, user_id: int, language: str, severity: str, mode: str, is_admin: bool):
        """Generate treatment plan"""
        
        try:
            plan = self._generate_plan(severity, language)
            
            msg = plan
            if is_admin and mode == 'admin':
                msg += "\n\n🐛 **DEBUG INFO:**\n"
                msg += f"Severity: {severity}\n"
                msg += f"Mode: ADMIN\n"
                msg += f"Access: UNLIMITED\n"
            
            await query.edit_message_text(text=msg[:4096])
            
            # Additional message
            additional_msg = (
                "✅ **Treatment plan generated!**\n\n"
                "You can now:\n"
                "1️⃣ Download PDF\n"
                "2️⃣ View Videos\n"
                "3️⃣ Start Exercises"
            ) if language == 'English' else (
                "✅ **تم إنشاء الخطة!**\n\n"
                "يمكنك الآن:\n"
                "1️⃣ تحميل PDF\n"
                "2️⃣ مشاهدة الفيديوهات\n"
                "3️⃣ بدء التمارين"
            )
            
            if is_admin and mode == 'admin':
                additional_msg += "\n\n🐛 **ADMIN:** Full access granted"
            
            await query.message.reply_text(additional_msg)
            
            self.treatment_plans[user_id] = plan
            logger.info(f"Treatment plan generated for {user_id}")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            error_msg = "Error generating plan" if language == 'English' else "خطأ في إنشاء الخطة"
            await query.message.reply_text(error_msg)
    
    def _generate_plan(self, severity: str, language: str) -> str:
        """Generate treatment plan"""
        
        if language == 'Arabic':
            return f"""
📋 **خطة العلاج (شدة: {severity})**

🛡️ **1. منع التفاقم:**
• راحة منتظمة
• وضعية صحيحة
• تجنب الحركات المفاجئة

🏥 **2. العلاجات:**
• كمادات دافئة
• تدليك برفق
• حمام دافئ

💪 **3. التمارين:**
• تمدد خفيف
• تقوية تدريجية
• تمارين وظيفية

⚠️ **4. التحذيرات:**
• توقف عند الألم الشديد
• استشر الطبيب

🛒 **5. المنتجات:**
• وسائد دعم
• أجهزة تدليك

💊 **6. الأدوية:**
• Paracetamol
• Ibuprofen
            """
        else:
            return f"""
📋 **Treatment Plan (Severity: {severity})**

🛡️ **1. Prevention:**
• Regular rest
• Good posture
• Avoid sudden movements

🏥 **2. Remedies:**
• Warm compress
• Gentle massage
• Warm bath

💪 **3. Exercises:**
• Light stretching
• Gradual strengthening
• Functional exercises

⚠️ **4. Warnings:**
• Stop if severe pain
• Consult doctor

🛒 **5. Products:**
• Support pillows
• Massage devices

💊 **6. Medications:**
• Paracetamol
• Ibuprofen
            """
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt"""
        
        if language == 'Arabic':
            return """أنت مساعد طبي متخصص في العلاج الطبيعي. استمع بعناية واسأل أسئلة توضيحية."""
        else:
            return """You are a medical assistant specializing in physical therapy. Listen carefully and ask clarifying questions."""
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Error: {context.error}")


async def main():
    """Main function"""
    
    app = Application.builder().token(BOT_TOKEN).build()
    bot = HybridSmartBot()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.mode_selection, pattern='^mode_'))
    app.add_handler(CallbackQueryHandler(bot.language_selection, pattern='^lang_'))
    app.add_handler(CallbackQueryHandler(bot.severity_selection, pattern='^severity_'))
    app.add_handler(CallbackQueryHandler(bot.handle_payment, pattern='^(pay_|cancel_)'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_handler(PreCheckoutQueryHandler(bot.pre_checkout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, bot.successful_payment_handler))
    app.add_error_handler(bot.error_handler)
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ HYBRID BOT STARTED!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
