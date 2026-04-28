"""
Physical Therapy Assessment Bot - Telegram
All Arabic text is imported from knowledge_base.py
"""

import asyncio
import logging
import os

import anthropic
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from knowledge_base import (
    ASSESSMENT_FLOW,
    KNOWLEDGE_BASE,
    MEDICAL_DISCLAIMER,
    SUMMARY_FIELDS,
    UI,
    UNIVERSAL_RED_FLAGS,
)
from prompts import build_assessment_prompt

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set")

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

QUESTIONS = ASSESSMENT_FLOW["questions"]
NUM_QUESTIONS = len(QUESTIONS)
PROCESSING = NUM_QUESTIONS
CONFIRMING = NUM_QUESTIONS + 1


def build_keyboard(options):
    keyboard = []
    row = []
    for i, option in enumerate(options):
        row.append(InlineKeyboardButton(option, callback_data=option))
        if len(row) == 2 or i == len(options) - 1:
            keyboard.append(row)
            row = []
    return InlineKeyboardMarkup(keyboard)


def get_progress(index):
    filled = UI["progress_filled"] * (index + 1)
    empty = UI["progress_empty"] * (NUM_QUESTIONS - index - 1)
    return f"{filled}{empty} ({index + 1}/{NUM_QUESTIONS})"


def region_to_key(region_ar):
    mapping = {
        "\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633": "cervical",
        "\u0627\u0644\u0643\u062a\u0641": "shoulder",
        "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f": "elbow",
        "\u0627\u0644\u0631\u0633\u063a \u0648\u0627\u0644\u064a\u062f": "wrist_hand",
        "\u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631": "thoracic",
        "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631 \u0648\u0627\u0644\u062d\u0648\u0636": "lumbar",
        "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630": "hip",
        "\u0627\u0644\u0631\u0643\u0628\u0629": "knee",
        "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645": "ankle_foot",
    }
    for ar, key in mapping.items():
        if ar in region_ar:
            return key
    return "general"


def build_knowledge_context(region_key):
    region_data = KNOWLEDGE_BASE.get(region_key, KNOWLEDGE_BASE.get("general", {}))
    conditions = region_data.get("conditions", {})
    red_flags = region_data.get("red_flags", UNIVERSAL_RED_FLAGS)

    lines = [f"Region: {region_key}", "\nRed Flags:"]
    for rf in red_flags:
        lines.append(f"  - {rf}")

    lines.append("\nConditions:")
    for cond_key, cond_data in conditions.items():
        lines.append(f"\n* {cond_data['name_ar']} ({cond_data['name_en']})")
        lines.append(f"  Features: {', '.join(cond_data.get('clinical_features', []))}")
        if cond_data.get("exercises"):
            for ex in cond_data["exercises"]:
                url = ex.get("url", "")
                lines.append(
                    f"  > {ex['name_ar']}: {ex['sets']}x{ex['reps']} "
                    f"hold={ex.get('hold_seconds',0)}s "
                    f"{ex['frequency']} {ex['weeks']}"
                    f" {ex.get('channel','')} {url}"
                )
        if cond_data.get("refer_if"):
            lines.append(f"  Refer if: {' | '.join(cond_data['refer_if'])}")
    return "\n".join(lines)


def check_red_flags(patient_data):
    found = []
    combined = " ".join([
        patient_data.get("associated_symptoms", ""),
        patient_data.get("chief_complaint", ""),
        patient_data.get("medical_history", ""),
        patient_data.get("mechanism", ""),
    ]).lower()

    danger = [
        ("\u0645\u062b\u0627\u0646\u0629", "\u0641\u0642\u062f\u0627\u0646 \u0627\u0644\u0633\u064a\u0637\u0631\u0629 \u0639\u0644\u0649 \u0627\u0644\u0645\u062b\u0627\u0646\u0629"),
        ("\u0633\u0631\u0637\u0627\u0646", "\u062a\u0627\u0631\u064a\u062e \u0633\u0631\u0637\u0627\u0646\u064a"),
        ("\u0636\u0639\u0641 \u062a\u062f\u0631\u064a\u062c\u064a", "\u0636\u0639\u0641 \u0639\u0635\u0628\u064a"),
    ]
    for keyword, label in danger:
        if keyword in combined:
            found.append(label)

    try:
        if int(patient_data.get("pain_scale", "0")) >= 9:
            found.append("\u062f\u0631\u062c\u0629 \u0623\u0644\u0645 \u0634\u062f\u064a\u062f\u0629 9-10/10")
    except (ValueError, TypeError):
        pass
    return found


def format_summary(patient_data):
    lines = [UI["summary_header"]]
    for key, fmt in SUMMARY_FIELDS:
        val = patient_data.get(key, "-")
        lines.append(fmt.format(val))
    lines.append(UI["confirm_q"])
    return "\n".join(lines)


def split_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    while len(text) > max_len:
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks


async def generate_report(patient_data):
    region_key = region_to_key(patient_data.get("body_region", ""))
    context = build_knowledge_context(region_key)
    prompt = build_assessment_prompt(patient_data, context)
    try:
        msg = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"API Error: {str(e)[:300]}"


async def send_question(message, context, q_index, edit=False):
    if q_index >= NUM_QUESTIONS:
        return await show_summary(message, context)

    q = QUESTIONS[q_index]
    text = f"{get_progress(q_index)}\n\n? {q['q']}"

    if q["type"] == "keyboard":
        markup = build_keyboard(q["options"])
        try:
            if edit:
                await message.edit_text(text, reply_markup=markup)
            else:
                await message.reply_text(text, reply_markup=markup)
        except Exception:
            await message.reply_text(text, reply_markup=markup)
    else:
        try:
            if edit:
                await message.edit_text(text)
            else:
                await message.reply_text(text)
        except Exception:
            await message.reply_text(text)

    return q_index


async def show_summary(message, context):
    patient_data = context.user_data.get("patient_data", {})
    summary = format_summary(patient_data)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(UI["confirm_yes"], callback_data="confirm_yes"),
            InlineKeyboardButton(UI["confirm_no"], callback_data="restart"),
        ]
    ])
    try:
        await message.edit_text(summary, reply_markup=keyboard)
    except Exception:
        await message.reply_text(summary, reply_markup=keyboard)
    return CONFIRMING


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(UI["start_btn"], callback_data="start_assessment")]
    ])
    await update.message.reply_text(UI["welcome"], reply_markup=keyboard)
    return CONFIRMING


async def start_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=True)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data.get("current_q", 0)
    if q_index >= NUM_QUESTIONS:
        return ConversationHandler.END

    q = QUESTIONS[q_index]
    if q["type"] != "text":
        await update.message.reply_text(UI["keyboard_only"])
        return q_index

    context.user_data["patient_data"][q["key"]] = update.message.text.strip()
    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_question(update.message, context, next_q)


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data in ("confirm_yes", "restart"):
        return await handle_confirm(query, context)

    q_index = context.user_data.get("current_q", 0)
    if q_index >= NUM_QUESTIONS:
        return ConversationHandler.END

    q = QUESTIONS[q_index]
    context.user_data["patient_data"][q["key"]] = data
    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_question(query.message, context, next_q, edit=True)


async def handle_confirm(query, context: ContextTypes.DEFAULT_TYPE):
    if query.data == "restart":
        context.user_data.clear()
        context.user_data["patient_data"] = {}
        context.user_data["current_q"] = 0
        return await send_question(query.message, context, 0, edit=True)

    patient_data = context.user_data.get("patient_data", {})

    flags = check_red_flags(patient_data)
    if flags:
        await query.message.edit_text(UI["emergency"])
        return ConversationHandler.END

    await query.message.edit_text(UI["processing"])

    report = await generate_report(patient_data)
    full = report + "\n\n" + MEDICAL_DISCLAIMER

    chunks = split_message(full)
    for i, chunk in enumerate(chunks):
        try:
            if i == 0:
                await query.message.edit_text(chunk)
            else:
                await query.message.reply_text(chunk)
        except Exception as e:
            logger.error(f"Send error {i}: {e}")
            try:
                await query.message.reply_text(chunk)
            except Exception:
                pass

    end_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(UI["new_assessment"], callback_data="new_assessment")],
        [InlineKeyboardButton(UI["about_btn"], callback_data="about")],
    ])
    await query.message.reply_text(UI["end_msg"], reply_markup=end_kb)
    return ConversationHandler.END


async def new_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=False)


async def about_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(UI["about"])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(UI["cancel_msg"])
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(UI["error_msg"])


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(new_assessment_cb, pattern="^new_assessment$"),
        ],
        states={
            CONFIRMING: [
                CallbackQueryHandler(start_assessment_cb, pattern="^start_assessment$"),
                CallbackQueryHandler(handle_confirm, pattern="^(confirm_yes|restart)$"),
            ],
            **{
                i: [
                    CallbackQueryHandler(handle_button),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
                ]
                for i in range(NUM_QUESTIONS)
            },
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(about_cb, pattern="^about$"))
    app.add_error_handler(error_handler)

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
