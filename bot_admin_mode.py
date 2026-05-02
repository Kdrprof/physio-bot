"""
PhysioAssist Oracle - Admin Mode v8.0
Full access, no payment restrictions, debug mode enabled
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from anthropic import Anthropic
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Debug mode
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = Anthropic()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'PhysioAssistBot')

# Admin IDs (add your Telegram ID here)
ADMIN_IDS = [123456789]  # Replace with your Telegram ID


class AdminModeBot:
    """Admin mode bot with full access"""
    
    def __init__(self):
        self.user_sessions = {}
        self.treatment_plans = {}
        self.admin_mode = True
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id
        is_admin = user_id in ADMIN_IDS
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'language': None,
            'stage': 'language_selection',
            'condition': None,
            'severity': None,
            'messages': [],
            'is_admin': is_admin,
            'subscription_level': 'premium' if is_admin else 'free',  # Admin has premium
            'free_assessments': 0
        }
        
        # Welcome message
        welcome_msg = (
            "🏥 **Welcome to PhysioAssist Oracle v8.0**\n\n"
            f"👤 User ID: {user_id}\n"
            f"🔐 Mode: {'ADMIN' if is_admin else 'USER'}\n"
            f"💎 Access: {'PREMIUM (No Limits)' if is_admin else 'FREE (Limited)'}\n\n"
            "Please select your language:"
        ) if not is_admin else (
            "🏥 **Welcome to PhysioAssist Oracle v8.0 - ADMIN MODE**\n\n"
            f"👤 Admin ID: {user_id}\n"
            f"🔐 Mode: ADMIN\n"
            f"💎 Access: PREMIUM (UNLIMITED)\n"
            f"🐛 Debug: ENABLED\n\n"
            "Select your language:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        
        # Log in debug mode
        if is_admin:
            logger.info(f"✅ ADMIN LOGGED IN: {user_id}")
    
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
        
        # Add debug info for admin
        if self.user_sessions[user_id]['is_admin']:
            greeting += "\n\n🐛 **DEBUG INFO:**\n"
            greeting += f"Language: {language}\n"
            greeting += f"Stage: free_chat\n"
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
        is_admin = session.get('is_admin', False)
        
        # Log message in debug mode
        if is_admin:
            logger.info(f"📨 ADMIN MESSAGE: {user_message[:50]}...")
        
        # Free chat stage
        if session['stage'] == 'free_chat':
            await self.free_chat_handler(update, context, user_id, user_message, language, is_admin)
        
        # Assessment stage
        elif session['stage'] == 'assessment':
            await self.assessment_handler(update, context, user_id, user_message, language, is_admin)
    
    async def free_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               user_id: int, message: str, language: str, is_admin: bool):
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
            
            # Add debug info for admin
            if is_admin:
                ai_message += "\n\n🐛 **DEBUG INFO:**\n"
                ai_message += f"Messages: {len(self.user_sessions[user_id]['messages'])}\n"
                ai_message += f"Model: claude-3-5-sonnet-20241022\n"
                ai_message += f"Tokens Used: ~{len(ai_message.split())}\n"
            
            # Send response
            await update.message.reply_text(ai_message)
            
            # Check if we should move to assessment
            if len(self.user_sessions[user_id]['messages']) >= 6:
                await self.move_to_assessment(update, context, user_id, language, is_admin)
        
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            error_msg = f"Sorry, I encountered an error: {str(e)}" if language == 'English' else f"عذراً، حدث خطأ: {str(e)}"
            if is_admin:
                error_msg += f"\n\n🐛 **ERROR DETAILS:**\n{str(e)}"
            await update.message.reply_text(error_msg)
    
    async def move_to_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, language: str, is_admin: bool):
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
        
        if is_admin:
            msg += "\n\n🐛 **DEBUG:** Assessment stage activated"
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ Mild" if language == 'English' else "1️⃣ خفيف", callback_data='severity_mild')],
            [InlineKeyboardButton("2️⃣ Moderate" if language == 'English' else "2️⃣ متوسط", callback_data='severity_moderate')],
            [InlineKeyboardButton("3️⃣ Severe" if language == 'English' else "3️⃣ شديد", callback_data='severity_severe')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(msg, reply_markup=reply_markup)
    
    async def assessment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                user_id: int, message: str, language: str, is_admin: bool):
        """Handle assessment questions"""
        
        self.user_sessions[user_id]['messages'].append({
            'role': 'user',
            'content': message
        })
        
        msg = "Thank you for your response. Analyzing your condition..." if language == 'English' else "شكراً على إجابتك. جاري تحليل حالتك..."
        
        if is_admin:
            msg += "\n\n🐛 **DEBUG:** Assessment response recorded"
        
        await update.message.reply_text(msg)
    
    async def severity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle severity selection"""
        query = update.callback_query
        user_id = query.from_user.id
        language = self.user_sessions[user_id]['language']
        is_admin = self.user_sessions[user_id]['is_admin']
        
        severity_map = {
            'severity_mild': 'mild',
            'severity_moderate': 'moderate',
            'severity_severe': 'severe'
        }
        
        severity = severity_map.get(query.data, 'moderate')
        self.user_sessions[user_id]['severity'] = severity
        
        # Generate treatment plan
        await self.generate_treatment_plan(query, user_id, language, severity, is_admin)
    
    async def generate_treatment_plan(self, query, user_id: int, language: str, severity: str, is_admin: bool):
        """Generate complete treatment plan"""
        
        try:
            # Create treatment plan
            plan = self._generate_plan(severity, language)
            
            # Send plan
            msg = plan
            if is_admin:
                msg += "\n\n🐛 **DEBUG INFO:**\n"
                msg += f"Severity: {severity}\n"
                msg += f"Language: {language}\n"
                msg += f"Subscription: {self.user_sessions[user_id]['subscription_level']}\n"
                msg += f"Access: UNLIMITED (Admin)\n"
            
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
            
            if is_admin:
                additional_msg += "\n\n🐛 **ADMIN:** Full access granted - no payment required"
            
            await query.message.reply_text(additional_msg)
            
            # Store plan
            self.treatment_plans[user_id] = plan
            
            if is_admin:
                logger.info(f"✅ ADMIN: Treatment plan generated for {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Error generating treatment plan: {e}")
            error_msg = f"Sorry, I couldn't generate your treatment plan: {str(e)}" if language == 'English' else f"عذراً، لم أتمكن من إنشاء خطة العلاج: {str(e)}"
            if is_admin:
                error_msg += f"\n\n🐛 **ERROR:** {str(e)}"
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
2. اسأل أسئلة توضيحية لفهم الحالة بشكل أفضل
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
        logger.error(f"❌ Update {update} caused error {context.error}")
        
        try:
            await update.message.reply_text(
                "❌ An error occurred. Please try again.\n\n"
                "🐛 Error logged for debugging."
            )
        except:
            pass


async def main():
    """Main function"""
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Create bot instance
    bot = AdminModeBot()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.language_selection, pattern='^lang_'))
    app.add_handler(CallbackQueryHandler(bot.severity_selection, pattern='^severity_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_error_handler(bot.error_handler)
    
    # Start bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ ADMIN BOT STARTED SUCCESSFULLY!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
