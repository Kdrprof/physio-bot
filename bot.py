"""
=============================================================
Physical Therapy Assessment Bot — Telegram
Based on APTA, NICE, McKenzie, WHO Protocols
=============================================================
"""

import asyncio
import json
import logging
import os
import re

import anthropic
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from knowledge_base import ASSESSMENT_FLOW, KNOWLEDGE_BASE, MEDICAL_DISCLAIMER, UNIVERSAL_RED_FLAGS
from prompts import build_assessment_prompt

load_dotenv()

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─────────────────────────────────────────────
# CONVERSATION STATES
# ─────────────────────────────────────────────
QUESTIONS = ASSESSMENT_FLOW["questions"]
NUM_QUESTIONS = len(QUESTIONS)

# State = current question index (0 to NUM_QUESTIONS-1), then PROCESSING
PROCESSING = NUM_QUESTIONS
CONFIRMING = NUM_QUESTIONS + 1


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def build_keyboard(options: list) -> InlineKeyboardMarkup:
    """Build inline keyboard from list of options."""
    keyboard = []
    row = []
    for i, option in enumerate(options):
        row.append(InlineKeyboardButton(option, callback_data=option))
        if len(row) == 2 or i == len(options) - 1:
            keyboard.append(row)
            row = []
    return InlineKeyboardMarkup(keyboard)


def get_question_progress(index: int) -> str:
    """Return progress bar string."""
    filled = "🟢" * (index + 1)
    empty = "⚪" * (NUM_QUESTIONS - index - 1)
    return f"{filled}{empty} ({index + 1}/{NUM_QUESTIONS})"


def extract_region_key(region_ar: str) -> str:
    """Map Arabic region name to knowledge base key."""
    mapping = {
        "الرقبة والرأس": "cervical",
        "الكتف": "shoulder",
        "الكوع والساعد": "elbow",
        "الرسغ واليد": "wrist_hand",
        "أعلى الظهر": "thoracic",
        "أسفل الظهر والحوض": "lumbar",
        "الورك والفخذ": "hip",
        "الركبة": "knee",
        "الكاحل والقدم": "ankle_foot",
        "أكثر من منطقة": "general",
    }
    for ar, key in mapping.items():
        if ar in region_ar:
            return key
    return "general"


def build_knowledge_context(region_key: str) -> str:
    """Extract relevant knowledge base context for the AI prompt."""
    region_data = KNOWLEDGE_BASE.get(region_key, KNOWLEDGE_BASE.get("general", {}))
    conditions = region_data.get("conditions", {})
    red_flags = region_data.get("red_flags", UNIVERSAL_RED_FLAGS)

    context_lines = [f"منطقة التقييم: {region_key}"]
    context_lines.append("\nعلامات الخطر لهذه المنطقة:")
    for rf in red_flags:
        context_lines.append(f"  - {rf}")

    context_lines.append("\nالحالات الشائعة المعروفة لهذه المنطقة:")
    for cond_key, cond_data in conditions.items():
        context_lines.append(f"\n• {cond_data['name_ar']} ({cond_data['name_en']})")
        context_lines.append(f"  الميزات السريرية: {', '.join(cond_data.get('clinical_features', []))}")

        if cond_data.get("exercises"):
            context_lines.append("  التمارين المتاحة:")
            for ex in cond_data["exercises"]:
                url_info = f" | {ex['url']}" if ex.get("url") else ""
                context_lines.append(
                    f"    ▸ {ex['name_ar']}: {ex['sets']}×{ex['reps']} "
                    f"| احتفاظ {ex.get('hold_seconds', 0)}ث "
                    f"| {ex['frequency']} "
                    f"| {ex['weeks']}"
                    f" | {ex.get('channel', '')}{url_info}"
                )
        if cond_data.get("home_advice"):
            context_lines.append(f"  التعليمات المنزلية: {' | '.join(cond_data['home_advice'][:3])}")
        if cond_data.get("refer_if"):
            context_lines.append(f"  أحل إذا: {' | '.join(cond_data['refer_if'])}")

    return "\n".join(context_lines)


def check_quick_red_flags(patient_data: dict) -> list:
    """Fast local red flag screening before calling AI."""
    found = []
    text_fields = [
        patient_data.get("associated_symptoms", ""),
        patient_data.get("chief_complaint", ""),
        patient_data.get("medical_history", ""),
        patient_data.get("mechanism", ""),
    ]
    combined = " ".join(text_fields).lower()

    danger_keywords = [
        ("مثانة", "فقدان السيطرة على المثانة"),
        ("أمعاء", "مشكلة في السيطرة على الأمعاء"),
        ("سرطان", "تاريخ سرطاني"),
        ("ضعف تدريجي", "ضعف عصبي تدريجي"),
        ("تنميل الوجه", "تنميل في الوجه"),
        ("صعوبة بلع", "صعوبة في البلع"),
        ("ألم الصدر", "ألم في الصدر"),
    ]
    pain_score = patient_data.get("pain_scale", "0")
    try:
        if int(pain_scale) >= 9:
            found.append("درجة ألم شديدة جداً (9-10/10)")
    except (ValueError, TypeError):
        pass

    for keyword, label in danger_keywords:
        if keyword in combined:
            found.append(label)

    return found


def format_summary(patient_data: dict) -> str:
    """Format patient data as readable summary for confirmation."""
    lines = [
        "📋 *ملخص بياناتك قبل التحليل:*\n",
        f"👤 الاسم: {patient_data.get('name', '-')}",
        f"🎂 العمر: {patient_data.get('age', '-')} سنة",
        f"⚧ الجنس: {patient_data.get('gender', '-')}",
        f"💼 المهنة: {patient_data.get('occupation', '-')}",
        f"🤕 الشكوى: {patient_data.get('chief_complaint', '-')}",
        f"📍 منطقة الألم: {patient_data.get('body_region', '-')}",
        f"⏱️ المدة: {patient_data.get('onset_duration', '-')}",
        f"🔴 درجة الألم: {patient_data.get('pain_scale', '-')}/10",
        f"💊 التاريخ الطبي: {patient_data.get('medical_history', '-')}",
        "\n✅ هل هذه البيانات صحيحة؟",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────

async def generate_assessment(patient_data: dict) -> str:
    """Call Claude API to generate full PT assessment report."""
    region_key = extract_region_key(patient_data.get("body_region", ""))
    knowledge_context = build_knowledge_context(region_key)
    prompt = build_assessment_prompt(patient_data, knowledge_context)

    try:
        message = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return f"⚠️ خطأ في الاتصال بالذكاء الاصطناعي: {str(e)[:200]}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"⚠️ خطأ غير متوقع: {str(e)[:200]}"


def split_long_message(text: str, max_length: int = 4000) -> list:
    """Split message into Telegram-compatible chunks."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while len(text) > max_length:
        # Try to split at section headers or newlines
        split_at = text.rfind("\n###", 0, max_length)
        if split_at == -1:
            split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    if text:
        chunks.append(text)
    return chunks


# ─────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation."""
    context.user_data.clear()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0

    welcome_text = (
        "🏥 *مرحباً بك في بوت تقييم العلاج الطبيعي*\n\n"
        "سأساعدك على:\n"
        "✅ تقييم حالتك بناءً على بروتوكولات دولية\n"
        "✅ الحصول على برنامج تمارين علاجية منزلية مخصصة\n"
        "✅ تعليمات طبية وإرشادات سلوكية دقيقة\n\n"
        "⚠️ *هذا البوت مخصص للحالات التي يمكن علاجها منزلياً فقط*\n"
        "🚨 *في حال الألم الشديد جداً أو الحوادث: توجه للطوارئ فوراً*\n\n"
        "🕒 التقييم يستغرق حوالي 5 دقائق\n\n"
            "✅ انتهى التقرير - هل تريد تقييماً جديداً؟",
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚀 ابدأ التقييم", callback_data="start_assessment")]]
    )

    await update.message.reply_text(
        welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )
    return CONFIRMING


async def start_assessment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle start button click — send first question."""
    query = update.callback_query
    await query.answer()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=True)


async def send_question(message, context: ContextTypes.DEFAULT_TYPE, q_index: int, edit: bool = False) -> int:
    """Send question at given index."""
    if q_index >= NUM_QUESTIONS:
        return await confirm_data(message, context)

    q = QUESTIONS[q_index]
    progress = get_question_progress(q_index)
    text = f"{progress}\n\n❓ *{q['q']}*"

    if q["type"] == "keyboard":
        markup = build_keyboard(q["options"])
        if edit:
            try:
                await message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)
            except Exception:
                await message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)
        else:
            await message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)
    else:
        if edit:
            try:
                await message.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    return q_index


async def handle_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle free text answers."""
    q_index = context.user_data.get("current_q", 0)

    if q_index >= NUM_QUESTIONS:
        return ConversationHandler.END

    q = QUESTIONS[q_index]
    if q["type"] != "text":
        await update.message.reply_text("⚠️ يرجى الاختيار من الأزرار أدناه.")
        return q_index

    answer = update.message.text.strip()
    context.user_data["patient_data"][q["key"]] = answer

    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_question(update.message, context, next_q)


async def handle_keyboard_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    if query.data in ("confirm_yes", "confirm_no", "restart"):
        return await handle_confirmation(query, context)

    q_index = context.user_data.get("current_q", 0)

    if q_index >= NUM_QUESTIONS:
        return ConversationHandler.END

    q = QUESTIONS[q_index]
    answer = query.data
    context.user_data["patient_data"][q["key"]] = answer

    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_question(query.message, context, next_q, edit=True)


async def confirm_data(message, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show collected data for confirmation."""
    patient_data = context.user_data.get("patient_data", {})
    summary = format_summary(patient_data)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ صحيح، ابدأ التحليل", callback_data="confirm_yes"),
            InlineKeyboardButton("🔄 أعد من البداية", callback_data="restart"),
        ]
    ])

    try:
        await message.edit_text(summary, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    except Exception:
        await message.reply_text(summary, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    return CONFIRMING


async def handle_confirmation(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirm/restart buttons."""
    if query.data == "restart":
        context.user_data.clear()
        context.user_data["patient_data"] = {}
        context.user_data["current_q"] = 0
        return await send_question(query.message, context, 0, edit=True)

    if query.data == "confirm_yes":
        patient_data = context.user_data.get("patient_data", {})

        # Quick local red flag check
        quick_flags = check_quick_red_flags(patient_data)
        if quick_flags:
            emergency_text = (
                "🚨 *تحذير: تم اكتشاف علامات تحتاج تقييماً طبياً فورياً*\n\n"
                + "\n".join(f"⛔ {f}" for f in quick_flags)
                + "\n\n*يرجى التوجه فوراً لأقرب مركز طبي أو غرفة طوارئ*\n"
                "📞 اتصل بخدمات الطوارئ: 911 / 997\n\n"
                "⚠️ لا تؤجل طلب الرعاية الطبية."
            )
            await query.message.edit_text(emergency_text, parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

        # Show processing message
        processing_text = (
            "⚙️ *جارٍ تحليل بياناتك...*\n\n"
            "🔬 التحقق من علامات الخطر\n"
            "🧠 استخلاص التشخيص الأرجح\n"
            "🏋️ تصميم برنامج التمارين\n"
            "📝 إعداد التقرير الكامل\n\n"
            "_قد يستغرق هذا 30-60 ثانية..._"
        )
        await query.message.edit_text(processing_text)

        # Generate AI report
        report = await generate_assessment(patient_data)

        # Add disclaimer
        full_report = report + "\n\n" + MEDICAL_DISCLAIMER

        # Split and send report
        chunks = split_long_message(full_report)

        for i, chunk in enumerate(chunks):
            if i == 0:
                try:
                    await query.message.edit_text(
                        chunk,
                        
                    )
                except Exception:
                    await query.message.reply_text(chunk)
            else:
                await query.message.reply_text(chunk)

        # End keyboard
        end_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تقييم جديد", callback_data="new_assessment")],
            [InlineKeyboardButton("ℹ️ حول البوت", callback_data="about")],
        ])
        await query.message.reply_text(
            "✅ انتهى التقرير - هل تريد تقييماً جديداً؟",
            
            reply_markup=end_keyboard,
        )

        return ConversationHandler.END

    return CONFIRMING


async def new_assessment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new assessment request from end keyboard."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=False)


async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show about info."""
    query = update.callback_query
    await query.answer()
    about_text = (
        "🏥 *بوت تقييم العلاج الطبيعي*\n\n"
        "📚 *المراجع العلمية:*\n"
        "• APTA Clinical Practice Guidelines\n"
        "• NICE Musculoskeletal Guidelines\n"
        "• McKenzie Method (MDT)\n"
        "• Cochrane Reviews\n"
        "• WHO Rehabilitation Guidelines 2023\n"
        "• IFOMPT Red Flag Screening Standards\n\n"
        "🎬 *مصادر الفيديوهات:*\n"
        "• Doctor Jo (YouTube)\n"
        "• Physiotutors (YouTube)\n"
        "• E3 Rehab (YouTube)\n\n"
        "⚠️ هذا البوت لأغراض تعليمية فقط ولا يغني عن زيارة أخصائي علاج طبيعي مرخص."
    )
    await query.message.reply_text(about_text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ تم إلغاء التقييم.\n\nاكتب /start للبدء من جديد."
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler."""
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ حدث خطأ. اكتب /start للمحاولة مرة أخرى."
        )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(new_assessment_callback, pattern="^new_assessment$"),
        ],
        states={
            CONFIRMING: [
                CallbackQueryHandler(start_assessment_callback, pattern="^start_assessment$"),
                CallbackQueryHandler(handle_confirmation, pattern="^(confirm_yes|confirm_no|restart)$"),
            ],
            **{
                i: [
                    CallbackQueryHandler(handle_keyboard_answer),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_answer),
                ]
                for i in range(NUM_QUESTIONS)
            },
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(about_callback, pattern="^about$"))
    application.add_error_handler(error_handler)

    logger.info("🏥 Physical Therapy Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
