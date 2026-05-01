"""
PhysioAssist Oracle v7.0 - Complete Overhaul
Advanced AI-powered physiotherapy bot with:
- Smart conversation & diagnostic engine
- Comprehensive 6-part treatment plans
- Professional bilingual UX (Arabic/English)
- Freemium subscription system
- Smart paywall strategy
- Red flag detection
- Quick win exercises

Author: PhysioAssist Team
Version: 7.0
"""

import logging
import os
import re
from io import BytesIO
from datetime import datetime, timedelta

import anthropic
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    PreCheckoutQueryHandler, filters,
)

# Import new modules
from diagnostic_engine import DiagnosticEngine, FreemiumStrategy
from ux_formatter import UXFormatter
from subscription_system import SubscriptionSystem, ConversionOptimizer

# Import existing modules
from database import (
    init_db, get_or_create_user, update_user_email, update_user_lang,
    can_use_free, mark_free_used, mark_paid, save_assessment,
    get_user_points, redeem_points_for_free, get_referral_code,
    generate_one_time_code, use_one_time_code, record_referral_share,
    process_start_referral, add_points, mark_user_rated, has_user_rated,
)
from pdf_gen import generate_full_pdf, generate_quick_card_pdf
from prompts import build_full_prompt
from youtube_api import search_exercise_videos, format_videos_for_prompt
from clinical_tests import get_tests_for_region, format_assessment_results, get_watch_url

load_dotenv()
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN         = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BOT_USERNAME      = os.getenv("BOT_USERNAME", "PhysioAssistBot")

if not BOT_TOKEN:         raise ValueError("BOT_TOKEN not set")
if not ANTHROPIC_API_KEY: raise ValueError("ANTHROPIC_API_KEY not set")

# Initialize AI clients
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Pricing
PRICE_STARS      = 150
PRICE_LABEL      = "$1.99"
POINTS_PER_SHARE = 25
POINTS_PER_JOIN  = 25
POINTS_FOR_FREE  = 50

# ── STATES ────────────────────────────────────────
LANG_SELECT = 0
CHAT_MODE = 1
ASSESSMENT_PHASE = 2
TREATMENT_PLAN_PHASE = 3
PAYWALL_PHASE = 4
SUBSCRIPTION_PHASE = 5
FINISHED = 6
SELF_ASSESS = 7

# ── QUESTIONS (Original) ──────────────────────────
QUESTIONS = {
    "en": [
        {"key": "name", "q": "What is your full name?", "type": "text"},
        {"key": "age", "q": "How old are you?", "type": "text"},
        {"key": "gender", "q": "Gender:", "type": "keyboard", "options": ["Male", "Female"]},
        {"key": "occupation", "q": "What is your occupation?", "type": "text"},
        {"key": "chief_complaint", "q": "Describe your main complaint:", "type": "text"},
        {"key": "body_region", "q": "Where is the primary pain?", "type": "keyboard",
         "options": ["Neck / Head", "Shoulder", "Elbow / Forearm", "Wrist / Hand",
                     "Upper Back", "Lower Back / Pelvis", "Hip / Thigh",
                     "Knee", "Ankle / Foot", "Multiple areas"]},
        {"key": "laterality", "q": "Which side is affected?", "type": "keyboard",
         "options": ["Left", "Right", "Both sides", "Center / Spine"]},
        {"key": "onset_duration", "q": "How long have you had this problem?", "type": "text"},
        {"key": "mechanism", "q": "How did it start?", "type": "keyboard",
         "options": ["Sudden (clear event)", "Gradual (no clear cause)", "After injury / accident",
                     "After exertion / overuse", "Repetitive movement", "After long sitting / posture"]},
        {"key": "pain_scale", "q": "Rate your pain RIGHT NOW (0 = none, 10 = worst):", "type": "keyboard",
         "options": ["0","1","2","3","4","5","6","7","8","9","10"]},
    ],
    "ar": [
        {"key": "name", "q": "ما هو اسمك الكامل؟", "type": "text"},
        {"key": "age", "q": "كم عمرك؟", "type": "text"},
        {"key": "gender", "q": "الجنس:", "type": "keyboard", "options": ["ذكر", "أنثى"]},
        {"key": "occupation", "q": "ما هي مهنتك؟", "type": "text"},
        {"key": "chief_complaint", "q": "صف شكواك الرئيسية:", "type": "text"},
        {"key": "body_region", "q": "أين الألم الأساسي؟", "type": "keyboard",
         "options": ["الرقبة / الرأس", "الكتف", "الكوع / الساعد", "المعصم / اليد",
                     "الظهر العلوي", "الظهر السفلي / الحوض", "الورك / الفخذ",
                     "الركبة", "الكاحل / القدم", "مناطق متعددة"]},
        {"key": "laterality", "q": "أي جانب متأثر؟", "type": "keyboard",
         "options": ["الجانب الأيسر", "الجانب الأيمن", "كلا الجانبين", "المركز / العمود الفقري"]},
        {"key": "onset_duration", "q": "كم من الوقت لديك هذه المشكلة؟", "type": "text"},
        {"key": "mechanism", "q": "كيف بدأ الألم؟", "type": "keyboard",
         "options": ["مفاجئ (حدث واضح)", "تدريجي (بدون سبب واضح)", "بعد إصابة / حادث",
                     "بعد مجهود / إفراط في الاستخدام", "حركة متكررة", "بعد جلوس طويل / وضعية خاطئة"]},
        {"key": "pain_scale", "q": "قيّم ألمك الآن (0 = لا ألم، 10 = أسوأ ألم):", "type": "keyboard",
         "options": ["0","1","2","3","4","5","6","7","8","9","10"]},
    ]
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Initialize bot"""
    
    user_id = update.effective_user.id
    user = get_or_create_user(user_id)
    
    # Language selection
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = """
👋 <b>Welcome to PhysioAssist Oracle v7.0</b>

Your AI-powered physiotherapy companion!

🏥 Get personalized treatment plans
💪 Progressive exercise programs
🎯 Professional guidance

Choose your language:
"""
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    return LANG_SELECT


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = "en" if "en" in query.data else "ar"
    
    # Update user language
    update_user_lang(user_id, language)
    
    # Initialize formatters
    context.user_data["language"] = language
    context.user_data["formatter"] = UXFormatter(language=language)
    context.user_data["diagnostic_engine"] = DiagnosticEngine(api_key=ANTHROPIC_API_KEY)
    context.user_data["subscription_system"] = SubscriptionSystem(language=language)
    context.user_data["conversation_history"] = []
    
    formatter = context.user_data["formatter"]
    
    if language == "ar":
        msg = """✅ <b>تم اختيار اللغة العربية</b>

مرحباً بك في PhysioAssist Oracle v7.0

🏥 احصل على خطط علاج شخصية
💪 برامج تمارين متدرجة
🎯 إرشادات احترافية

الآن، دعنا نبدأ بفهم حالتك الطبية...

اكتب رسالة حرة تصف ما تشعر به:"""
    else:
        msg = """✅ <b>English Selected</b>

Welcome to PhysioAssist Oracle v7.0

🏥 Get personalized treatment plans
💪 Progressive exercise programs
🎯 Professional guidance

Now, let's understand your condition...

Send a free message describing how you feel:"""
    
    await query.edit_message_text(msg, parse_mode=ParseMode.HTML)
    return CHAT_MODE


async def chat_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free chat mode - Build trust"""
    
    user_id = update.effective_user.id
    user_message = update.message.text
    language = context.user_data.get("language", "en")
    
    # Initialize if needed
    if "diagnostic_engine" not in context.user_data:
        context.user_data["diagnostic_engine"] = DiagnosticEngine(api_key=ANTHROPIC_API_KEY)
    if "conversation_history" not in context.user_data:
        context.user_data["conversation_history"] = []
    if "formatter" not in context.user_data:
        context.user_data["formatter"] = UXFormatter(language=language)
    
    engine = context.user_data["diagnostic_engine"]
    formatter = context.user_data["formatter"]
    
    # Get AI response in chat mode
    response = engine.free_chat_mode(
        user_message,
        context.user_data["conversation_history"],
        language=language
    )
    
    # Format and send response
    formatted_response = formatter.format_chat_message("PhysioAssist", response, is_user=False)
    await update.message.reply_text(formatted_response, parse_mode=ParseMode.HTML)
    
    # After 3 exchanges, suggest moving to assessment
    if len(context.user_data["conversation_history"]) >= 6:
        if language == "ar":
            suggestion = """
🎯 <b>هل تريد خطة علاج شاملة؟</b>

سأطرح عليك بعض الأسئلة الطبية لفهم حالتك بشكل أفضل، ثم سأعد لك خطة علاج شاملة مخصصة.

اضغط على الزر أدناه للمتابعة:"""
        else:
            suggestion = """
🎯 <b>Ready for a Treatment Plan?</b>

I'll ask you some clinical questions to better understand your condition, then create a personalized treatment plan.

Click below to continue:"""
        
        keyboard = [[InlineKeyboardButton("✅ Let's Go" if language == "en" else "✅ هيا بنا", 
                                         callback_data="start_assessment")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(suggestion, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    return CHAT_MODE


async def start_assessment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start formal assessment"""
    
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get("language", "en")
    
    if language == "ar":
        msg = "🏥 <b>بدء التقييم السريري</b>\n\nسأطرح عليك أسئلة مهمة لفهم حالتك بشكل أفضل..."
    else:
        msg = "🏥 <b>Starting Clinical Assessment</b>\n\nI'll ask important questions to understand your condition better..."
    
    await query.edit_message_text(msg, parse_mode=ParseMode.HTML)
    
    # Store patient data
    context.user_data["patient_data"] = {}
    context.user_data["question_index"] = 0
    
    # Start asking questions
    return await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask next assessment question"""
    
    language = context.user_data.get("language", "en")
    question_index = context.user_data.get("question_index", 0)
    questions = QUESTIONS.get(language, QUESTIONS["en"])
    
    if question_index >= len(questions):
        # Assessment complete - generate treatment plan
        return await generate_treatment_plan(update, context)
    
    question = questions[question_index]
    
    if question["type"] == "text":
        if update.message:
            await update.message.reply_text(question["q"], parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(question["q"], parse_mode=ParseMode.HTML)
    
    elif question["type"] == "keyboard":
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"q_{question_index}_{i}")] 
                    for i, opt in enumerate(question["options"])]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(question["q"], reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(question["q"], reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    return ASSESSMENT_PHASE


async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle question answer"""
    
    language = context.user_data.get("language", "en")
    question_index = context.user_data.get("question_index", 0)
    questions = QUESTIONS.get(language, QUESTIONS["en"])
    
    if question_index >= len(questions):
        return ASSESSMENT_PHASE
    
    question = questions[question_index]
    
    # Store answer
    if update.message:
        answer = update.message.text
    else:
        query = update.callback_query
        await query.answer()
        answer = query.data.split("_")[2]
    
    context.user_data["patient_data"][question["key"]] = answer
    context.user_data["question_index"] = question_index + 1
    
    return await ask_next_question(update, context)


async def generate_treatment_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate comprehensive treatment plan"""
    
    language = context.user_data.get("language", "en")
    formatter = context.user_data.get("formatter")
    engine = context.user_data.get("diagnostic_engine")
    subscription_system = context.user_data.get("subscription_system")
    
    patient_data = context.user_data.get("patient_data", {})
    user_id = update.effective_user.id
    user = get_or_create_user(user_id)
    
    # Generate assessment
    assessment = engine.generate_comprehensive_assessment(patient_data, language=language)
    
    # Check for red flags
    has_flags, flags = engine.detect_red_flags(patient_data, language=language)
    
    if has_flags:
        if language == "ar":
            msg = f"""🚨 <b>تحذير: علامات خطر مكتشفة!</b>

{', '.join(flags)}

⚠️ يجب عليك التوجه للطبيب فوراً!"""
        else:
            msg = f"""🚨 <b>WARNING: Red Flags Detected!</b>

{', '.join(flags)}

⚠️ Please see a doctor immediately!"""
        
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return FINISHED
    
    # Generate quick win exercise
    quick_win = engine.generate_quick_win_exercise(patient_data, language=language)
    formatted_exercise = formatter.format_quick_win_exercise(quick_win)
    
    await update.message.reply_text(formatted_exercise, parse_mode=ParseMode.HTML)
    
    # Store for later
    context.user_data["assessment"] = assessment
    context.user_data["quick_win"] = quick_win
    
    # Check subscription
    tier = subscription_system.get_user_tier(user)
    
    if tier.value == "free":
        # Show paywall
        if language == "ar":
            paywall_msg = """🔐 <b>الخطة الكاملة محمية</b>

لقد أعددت لك خطة علاج شاملة مدة 8 أسابيع تتضمن:

✅ برنامج تمارين متدرج
✅ وسائل علاجية منزلية
✅ منتجات أمازون موصى بها
✅ أدوية آمنة مقترحة
✅ فيديوهات YouTube
✅ متابعة يومية

💳 <b>للوصول للخطة الكاملة:</b>
اشترك الآن بـ <b>$4.99/شهر</b> (الشهر الأول فقط)"""
        else:
            paywall_msg = """🔐 <b>Full Plan Unlocked</b>

I've prepared a comprehensive 8-week treatment plan including:

✅ Progressive exercise program
✅ Home modalities
✅ Recommended Amazon products
✅ Safe medications
✅ YouTube videos
✅ Daily follow-up

💳 <b>To access the full plan:</b>
Subscribe now for <b>$4.99/month</b> (first month only)"""
        
        keyboard = [[InlineKeyboardButton("💳 Subscribe" if language == "en" else "💳 اشترك الآن", 
                                         callback_data="subscribe_basic")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(paywall_msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        # Generate full plan
        plan = engine.generate_comprehensive_treatment_plan(patient_data, assessment, language=language)
        formatted_plan = formatter.format_treatment_plan(plan)
        await update.message.reply_text(formatted_plan, parse_mode=ParseMode.HTML)
    
    return FINISHED


async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription"""
    
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get("language", "en")
    
    if language == "ar":
        msg = "جاري معالجة الاشتراك... سيتم تحويلك لصفحة الدفع."
    else:
        msg = "Processing subscription... You'll be redirected to payment."
    
    await query.edit_message_text(msg, parse_mode=ParseMode.HTML)
    
    # TODO: Integrate with Stripe/Telegram Stars payment
    
    return FINISHED


async def main():
    """Main function - Start bot"""
    
    # Initialize database
    init_db()
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG_SELECT: [CallbackQueryHandler(language_selected)],
            CHAT_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_mode_handler),
                CallbackQueryHandler(start_assessment, pattern="^start_assessment$"),
            ],
            ASSESSMENT_PHASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question),
                CallbackQueryHandler(answer_question, pattern="^q_"),
            ],
            FINISHED: [
                CallbackQueryHandler(subscribe_handler, pattern="^subscribe_"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    # Add handlers
    app.add_handler(conv_handler)
    
    # Start bot
    logger.info(f"🚀 PhysioAssist Oracle v7.0 started as @{BOT_USERNAME}")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
