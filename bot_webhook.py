#!/usr/bin/env python3
"""
PhysioAssist Oracle v8.0 - COMPLETE WEBHOOK VERSION
Combines the full HybridSmartBot logic with FastAPI webhook for Railway
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, PreCheckoutQueryHandler
from anthropic import Anthropic
import asyncio
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ADMIN_ID = 8660311978
PORT = int(os.getenv('PORT', 8000))
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL', 'https://physio-bot.up.railway.app')
PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN', 'test_provider')

logger.info("="*80)
logger.info("🚀 COMPLETE WEBHOOK BOT STARTING")
logger.info("="*80)

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN is missing!")
    sys.exit(1)

if not ANTHROPIC_API_KEY:
    logger.warning("⚠️ ANTHROPIC_API_KEY is missing! AI features will fail.")

# Initialize FastAPI app and Anthropic client
app = FastAPI()
bot = Bot(token=BOT_TOKEN)
client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Store application instance
application = None

# Pricing
PRICES = {
    'basic': {'usd': 199, 'name': 'Basic Plan', 'duration': '1 month'},
    'premium': {'usd': 499, 'name': 'Premium Plan', 'duration': '3 months'},
    'pro': {'usd': 999, 'name': 'Pro Plan', 'duration': '1 year'}
}

class HybridSmartBot:
    """Smart hybrid bot with mode selection - Adapted for Webhook"""
    
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
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {'is_admin': user_id == ADMIN_ID}
            
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
        
        if user_id not in self.user_sessions:
            await query.answer("Session expired. Please send /start again.", show_alert=True)
            return
            
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
        
        mode = self.user_sessions[user_id].get('mode', 'user')
        is_admin = self.user_sessions[user_id].get('is_admin', False)
        
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
        mode = session.get('mode', 'user')
        is_admin = session.get('is_admin', False)
        
        # Free chat stage
        if session.get('stage') == 'free_chat':
            await self.free_chat_handler(update, context, user_id, user_message, language, mode, is_admin)
        
        # Assessment stage
        elif session.get('stage') == 'assessment':
            await self.assessment_handler(update, context, user_id, user_message, language, mode, is_admin)
    
    async def free_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               user_id: int, message: str, language: str, mode: str, is_admin: bool):
        """Handle free chat with AI"""
        
        if 'messages' not in self.user_sessions[user_id]:
            self.user_sessions[user_id]['messages'] = []
            
        self.user_sessions[user_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        try:
            if not client:
                raise Exception("Anthropic API key not configured")
                
            system_prompt = self._get_system_prompt(language)
            
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=user_id, action='typing')
            
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
            
            # Check if we should move to assessment (after 4 messages to make it faster)
            if len(self.user_sessions[user_id]['messages']) >= 4:
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
            
        keyboard = [
            [InlineKeyboardButton("1️⃣", callback_data='severity_mild'),
             InlineKeyboardButton("2️⃣", callback_data='severity_moderate'),
             InlineKeyboardButton("3️⃣", callback_data='severity_severe')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(msg, reply_markup=reply_markup)
    
    async def assessment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, message: str, language: str, mode: str, is_admin: bool):
        """Handle text during assessment"""
        msg = "Please use the buttons to select severity." if language == 'English' else "الرجاء استخدام الأزرار لاختيار شدة الألم."
        await update.message.reply_text(msg)
    
    async def severity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle severity selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.user_sessions:
            await query.answer("Session expired", show_alert=True)
            return
            
        session = self.user_sessions[user_id]
        language = session.get('language', 'English')
        mode = session.get('mode', 'user')
        is_admin = session.get('is_admin', False)
        
        severity = query.data.split('_')[1]
        session['severity'] = severity
        
        # Check if user needs to pay
        if mode == 'user' and session.get('free_assessments', 0) >= FREE_ASSESSMENTS_LIMIT:
            await self.show_payment_options(query, language)
            return
            
        # Generate treatment plan
        await self.generate_treatment_plan(query, user_id, severity, language, mode, is_admin)
    
    async def show_payment_options(self, query, language: str):
        """Show payment options for user mode"""
        if language == 'English':
            msg = (
                "🔒 **Premium Feature**\n\n"
                "You have used your free assessment. To get your personalized treatment plan, "
                "please subscribe to one of our plans:\n\n"
                "🔹 **Basic ($1.99/mo)** - 5 assessments/month\n"
                "🔹 **Premium ($4.99/3mo)** - Unlimited assessments\n"
                "🔹 **Pro ($9.99/yr)** - Unlimited + Priority support"
            )
            keyboard = [
                [InlineKeyboardButton("Basic - $1.99", callback_data='pay_basic')],
                [InlineKeyboardButton("Premium - $4.99", callback_data='pay_premium')],
                [InlineKeyboardButton("Pro - $9.99", callback_data='pay_pro')]
            ]
        else:
            msg = (
                "🔒 **ميزة مدفوعة**\n\n"
                "لقد استنفدت التقييم المجاني. للحصول على خطة العلاج المخصصة، "
                "يرجى الاشتراك في إحدى باقاتنا:\n\n"
                "🔹 **الأساسية ($1.99/شهر)** - 5 تقييمات/شهر\n"
                "🔹 **المميزة ($4.99/3أشهر)** - تقييمات غير محدودة\n"
                "🔹 **الاحترافية ($9.99/سنة)** - غير محدودة + دعم أولوية"
            )
            keyboard = [
                [InlineKeyboardButton("الأساسية - $1.99", callback_data='pay_basic')],
                [InlineKeyboardButton("المميزة - $4.99", callback_data='pay_premium')],
                [InlineKeyboardButton("الاحترافية - $9.99", callback_data='pay_pro')]
            ]
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=msg, reply_markup=reply_markup)
    
    async def handle_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment button clicks"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data.startswith('pay_'):
            plan_id = query.data.split('_')[1]
            plan = PRICES[plan_id]
            
            chat_id = query.message.chat_id
            title = plan['name']
            description = f"Subscription for {plan['duration']}"
            payload = f"sub_{plan_id}_{user_id}"
            currency = "USD"
            price = plan['usd']
            prices = [LabeledPrice("Subscription", price)]
            
            # Send invoice
            await context.bot.send_invoice(
                chat_id, title, description, payload,
                PAYMENT_PROVIDER_TOKEN, currency, prices
            )
            await query.answer()
    
    async def pre_checkout_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Answer the PreQecheckoutQuery"""
        query = update.pre_checkout_query
        if query.invoice_payload.startswith('sub_'):
            await query.answer(ok=True)
        else:
            await query.answer(ok=False, error_message="Something went wrong...")
            
    async def successful_payment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle successful payment"""
        user_id = update.effective_user.id
        payload = update.message.successful_payment.invoice_payload
        
        if payload.startswith('sub_'):
            plan_id = payload.split('_')[1]
            
            # Update user subscription
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['subscription_level'] = plan_id
                self.user_sessions[user_id]['free_assessments'] = 0  # Reset
                
            language = self.user_sessions.get(user_id, {}).get('language', 'English')
            
            if language == 'English':
                msg = f"✅ Payment successful! You are now subscribed to the {PRICES[plan_id]['name']}."
            else:
                msg = f"✅ تم الدفع بنجاح! أنت الآن مشترك في {PRICES[plan_id]['name']}."
                
            await update.message.reply_text(msg)
            
            # Continue with treatment plan
            severity = self.user_sessions.get(user_id, {}).get('severity', 'moderate')
            mode = self.user_sessions.get(user_id, {}).get('mode', 'user')
            is_admin = self.user_sessions.get(user_id, {}).get('is_admin', False)
            
            # We need a dummy query object for generate_treatment_plan
            class DummyQuery:
                def __init__(self, message):
                    self.message = message
            
            await self.generate_treatment_plan(DummyQuery(update.message), user_id, severity, language, mode, is_admin)
    
    async def generate_treatment_plan(self, query, user_id: int, severity: str, language: str, mode: str, is_admin: bool):
        """Generate and send treatment plan"""
        
        # Increment assessment count for user mode
        if mode == 'user':
            self.user_sessions[user_id]['free_assessments'] = self.user_sessions[user_id].get('free_assessments', 0) + 1
            
        try:
            # Show typing indicator
            await query.message.chat.send_action(action='typing')
            
            plan = self._generate_plan(severity, language)
            
            await query.message.reply_text(plan)
            
            # Next steps
            additional_msg = (
                "What would you like to do next?\n\n"
                "1️⃣ Download PDF\n"
                "2️⃣ Watch Videos\n"
                "3️⃣ Start Exercises"
            ) if language == 'English' else (
                "ماذا تريد أن تفعل بعد ذلك؟\n\n"
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
            return """أنت مساعد طبي متخصص في العلاج الطبيعي. استمع بعناية واسأل أسئلة توضيحية. كن متعاطفاً ومحترفاً. لا تقدم تشخيصاً نهائياً بل نصائح عامة."""
        else:
            return """You are a medical assistant specializing in physical therapy. Listen carefully and ask clarifying questions. Be empathetic and professional. Do not provide a final diagnosis, only general advice."""
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Error: {context.error}", exc_info=context.error)


# Initialize bot logic
bot_logic = HybridSmartBot()

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming updates from Telegram"""
    try:
        data = await request.json()
        logger.info(f"📨 Received webhook update: {json.dumps(data, indent=2)[:200]}")
        
        update = Update.de_json(data, bot)
        if update:
            await application.process_update(update)
            logger.info("✅ Update processed")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "bot": "running"}

async def setup_webhook():
    """Setup webhook with Telegram"""
    try:
        webhook_url = f"{RAILWAY_STATIC_URL}/webhook"
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        await bot.set_webhook(url=webhook_url)
        logger.info("✅ Webhook set successfully")
    except Exception as e:
        logger.error(f"❌ Error setting webhook: {e}", exc_info=True)

async def main():
    """Main entry point"""
    global application, bot
    
    try:
        logger.info("🔧 Initializing Application...")
        
        # Initialize bot first
        logger.info("🔧 Initializing Bot...")
        await bot.initialize()
        logger.info("✅ Bot initialized")
        
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Application created")
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot_logic.start))
        application.add_handler(CallbackQueryHandler(bot_logic.mode_selection, pattern='^mode_'))
        application.add_handler(CallbackQueryHandler(bot_logic.language_selection, pattern='^lang_'))
        application.add_handler(CallbackQueryHandler(bot_logic.severity_selection, pattern='^severity_'))
        application.add_handler(CallbackQueryHandler(bot_logic.handle_payment, pattern='^(pay_|cancel_)'))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic.handle_message))
        application.add_handler(PreCheckoutQueryHandler(bot_logic.pre_checkout_handler))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, bot_logic.successful_payment_handler))
        application.add_error_handler(bot_logic.error_handler)
        
        logger.info("✅ Handlers added")
        
        # Initialize application
        await application.initialize()
        logger.info("✅ App initialized")
        
        # Setup webhook
        await setup_webhook()
        
        logger.info("✅ BOT READY FOR WEBHOOKS!")
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in main(): {e}", exc_info=True)
        raise

# Startup event
@app.on_event("startup")
async def startup():
    """Run on startup"""
    logger.info("🚀 FastAPI startup")
    await main()

if __name__ == '__main__':
    import uvicorn
    logger.info(f"🚀 Starting Uvicorn server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
