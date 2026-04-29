"""
PhysioAssist Bot v4.0 — Complete Build
Features:
- Free first assessment, paid ($1.99 / 150 Stars) after
- Referral system with personal links + one-time codes
- Points: 10pts/share, 50pts = free assessment
- Email collection (mandatory mid-assessment)
- HTML formatting throughout
- Two PDF reports (full + quick card)
- Physical therapy modalities in every report
- EN/AR bilingual
- Back button navigation
- Edit previous answers
- Extra notes box
- SQLite user database
"""

import logging
import os
import re
from io import BytesIO

import anthropic
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, ConversationHandler, MessageHandler,
    PreCheckoutQueryHandler, filters,
)

from database import (
    init_db, get_or_create_user, update_user_email, update_user_lang,
    can_use_free, mark_free_used, mark_paid, save_assessment,
    get_user_points, redeem_points_for_free, get_referral_code,
    generate_one_time_code, use_one_time_code, record_referral_share,
    process_start_referral, add_points,
)
from pdf_gen import generate_full_pdf, generate_quick_card_pdf
from prompts import build_full_prompt

load_dotenv()
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN         = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BOT_USERNAME      = os.getenv("BOT_USERNAME", "PhysioAssistBot")

if not BOT_TOKEN:         raise ValueError("BOT_TOKEN not set")
if not ANTHROPIC_API_KEY: raise ValueError("ANTHROPIC_API_KEY not set")

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PRICE_STARS = 150
PRICE_LABEL = "$1.99"
POINTS_PER_SHARE = 10
POINTS_FOR_FREE  = 50

# ── STATES ────────────────────────────────────────
LANG_SELECT  = 0
ANSWERING    = 1
EMAIL_STEP   = 2
EXTRA_NOTES  = 3
CODE_ENTRY   = 4
CONFIRMING   = 5
PAYING       = 6

# ── UI STRINGS ────────────────────────────────────
UI = {
    "en": {
        "welcome": (
            "<b>\U0001f3e5 Welcome to PhysioAssist</b>\n\n"
            "\u2705 Evidence-based physiotherapy assessment\n"
            "\u2705 Personalized home exercise program\n"
            "\u2705 Home PT modalities guide\n"
            "\u2705 Activity modifications &amp; precautions\n\n"
            "<i>\u26a0\ufe0f For home-manageable conditions only.\n"
            "\U0001f6a8 Severe pain or accidents: Emergency immediately.</i>\n\n"
            "\U0001f3c6 <b>Your first assessment is FREE!</b>\n"
            "\u23f1 Takes about 5 minutes"
        ),
        "start_btn":      "\U0001f680 Start Free Assessment",
        "back_btn":       "\u2b05 Back",
        "skip_btn":       "\u23e9 Skip",
        "processing":     (
            "\u2699\ufe0f <b>Analyzing your data...</b>\n\n"
            "\U0001f52c Screening for red flags\n"
            "\U0001f9e0 Generating clinical diagnosis\n"
            "\U0001f3cb Designing exercise program\n"
            "\U0001f4dd Preparing modalities guide\n\n"
            "<i>Please wait 30-60 seconds...</i>"
        ),
        "confirm_yes":    "\u2705 Correct \u2014 Run Analysis",
        "confirm_edit":   "\u270f Edit Answers",
        "end_full_pdf":   "\U0001f4d6 Download Full Report (PDF)",
        "end_quick_pdf":  "\U0001f4cb Download Quick Card (PDF)",
        "end_share":      "\U0001f4e4 Share Bot \u2192 Earn Points",
        "end_new":        "\U0001f504 New Assessment",
        "end_points":     "\u2b50 My Points",
        "error_msg":      "\u26a0 Error. Type /start to restart.",
        "cancel_msg":     "Cancelled. Type /start to begin.",
        "kb_only":        "\u26a0 Please use the buttons below.",
        "emergency":      (
            "\U0001f6a8 <b>RED FLAGS DETECTED</b>\n\n"
            "Please go to the nearest emergency room now.\n"
            "\U0001f4de Emergency: 911 / 997\n\n"
            "<i>Do not delay seeking medical care.</i>"
        ),
        "email_q":        (
            "\U0001f4e7 <b>Enter your email address</b>\n\n"
            "We'll send your report and recovery tips.\n"
            "<i>Example: name@gmail.com</i>"
        ),
        "email_invalid":  "\u26a0 Invalid email. Please try again:",
        "extra_notes_q":  (
            "\U0001f4dd <b>Anything else to add?</b>\n\n"
            "Help us personalize your assessment:\n"
            "\u2022 Symptoms not mentioned\n"
            "\u2022 Previous surgeries or injuries\n"
            "\u2022 Medications you take\n"
            "\u2022 Work demands or sports\n"
            "\u2022 Any other relevant information\n\n"
            "Type below or press <b>Skip</b>:"
        ),
        "payment_intro":  (
            "\U0001f4b3 <b>Get Your Full Report</b>\n\n"
            "\u2705 Clinical diagnosis\n"
            "\u2705 4 personalized exercises with video links\n"
            "\u2705 Home PT modalities guide\n"
            "\u2705 Activity modifications\n"
            "\u2705 Precautions &amp; contraindications\n"
            "\u2705 Full PDF + Quick Reference Card\n\n"
            "\U0001f4b0 <b>Price: {price}</b> (one-time per assessment)\n\n"
            "Or enter a <b>FREE code</b> if you have one:"
        ),
        "pay_stars_btn":  "\u2b50 Pay {stars} Stars ({price})",
        "enter_code_btn": "\U0001f511 I Have a Free Code",
        "use_points_btn": "\U0001f4af Use Points ({pts} pts)",
        "code_prompt":    "\U0001f511 Enter your free assessment code:",
        "code_invalid":   "\u274c Invalid or already used code. Try again or pay:",
        "share_msg":      (
            "\U0001f4e4 <b>Share PhysioAssist &amp; Earn Points!</b>\n\n"
            "\u2b50 <b>{pts} points</b> earned so far\n"
            "\U0001f3af <b>{needed} more points</b> = FREE assessment\n\n"
            "Share your personal link:\n"
            "<code>{link}</code>\n\n"
            "Every person who uses your link = <b>+10 points</b>\n"
            "Every time you share = <b>+10 points</b>\n"
            "\U0001f3c6 <b>50 points = 1 free assessment</b>\n\n"
            "Or share a one-time FREE code:\n"
            "<code>{code}</code>\n"
            "<i>(valid for 1 person only)</i>"
        ),
        "points_msg":     (
            "\u2b50 <b>Your Points</b>\n\n"
            "Current balance: <b>{pts} points</b>\n"
            "Threshold for free assessment: <b>50 points</b>\n"
            "Points needed: <b>{needed}</b>\n\n"
            "Earn points by:\n"
            "\u2022 Sharing your link (+10 pts each)\n"
            "\u2022 Friends who join via your link (+10 pts)\n\n"
            "Your referral link:\n"
            "<code>{link}</code>"
        ),
        "summary_header": "<b>\U0001f4cb Assessment Summary:</b>\n\n",
        "confirm_q":      "\n\u2705 <b>Is this correct?</b>",
        "summary_fields": [
            ("name",             "\U0001f464 <b>Name:</b> {}"),
            ("age",              "\U0001f382 <b>Age:</b> {} years"),
            ("gender",           "<b>Gender:</b> {}"),
            ("occupation",       "\U0001f4bc <b>Occupation:</b> {}"),
            ("chief_complaint",  "\U0001f915 <b>Complaint:</b> {}"),
            ("body_region",      "\U0001f4cd <b>Region:</b> {}"),
            ("onset_duration",   "\u23f1 <b>Duration:</b> {}"),
            ("pain_scale",       "\U0001f534 <b>Pain:</b> {}/10"),
            ("medical_history",  "\U0001f48a <b>Medical Hx:</b> {}"),
        ],
        "disclaimer": (
            "\n\n<i>\u26a0 <b>Disclaimer:</b> Educational purposes only. "
            "Not a substitute for professional physiotherapy assessment. "
            "Consult a licensed physiotherapist for full evaluation.</i>"
        ),
        "lang_select": "\U0001f310 Select your language:",
        "report_done": "\u2705 <b>Report Complete!</b>",
        "free_badge":  "\U0001f3c6 Free assessment used",
        "paid_badge":  "\U0001f4b3 Paid assessment",
    },
    "ar": {
        "welcome": (
            "<b>\U0001f3e5 \u0645\u0631\u062d\u0628\u0627\u064b \u0628\u0643 \u0641\u064a PhysioAssist</b>\n\n"
            "\u2705 \u062a\u0642\u064a\u064a\u0645 \u0641\u064a\u0632\u064a\u0648\u062b\u064a\u0631\u0627\u0628\u064a \u0645\u062f\u0639\u0648\u0645 \u0628\u0627\u0644\u0623\u062f\u0644\u0629\n"
            "\u2705 \u0628\u0631\u0646\u0627\u0645\u062c \u062a\u0645\u0627\u0631\u064a\u0646 \u0645\u0646\u0632\u0644\u064a \u0645\u062e\u0635\u0635\n"
            "\u2705 \u062f\u0644\u064a\u0644 \u0627\u0644\u0639\u0644\u0627\u062c\u0627\u062a \u0627\u0644\u0641\u064a\u0632\u064a\u0627\u0626\u064a\u0629 \u0627\u0644\u0645\u0646\u0632\u0644\u064a\u0629\n"
            "\u2705 \u062a\u0639\u0644\u064a\u0645\u0627\u062a \u0627\u0644\u0623\u0646\u0634\u0637\u0629 \u0648\u0627\u0644\u0645\u062d\u0627\u0630\u064a\u0631\n\n"
            "<i>\u26a0\ufe0f \u0644\u0644\u062d\u0627\u0644\u0627\u062a \u0627\u0644\u0645\u0646\u0632\u0644\u064a\u0629 \u0641\u0642\u0637.\n"
            "\U0001f6a8 \u0644\u0644\u062d\u0648\u0627\u062f\u062b: \u0627\u0630\u0647\u0628 \u0644\u0644\u0637\u0648\u0627\u0631\u0626 \u0641\u0648\u0631\u0627\u064b</i>\n\n"
            "\U0001f3c6 <b>\u0627\u0644\u062a\u0642\u064a\u064a\u0645 \u0627\u0644\u0623\u0648\u0644 \u0645\u062c\u0627\u0646\u064a!</b>\n"
            "\u23f1 \u0645\u062f\u062a\u0647 5 \u062f\u0642\u0627\u0626\u0642"
        ),
        "start_btn":      "\U0001f680 \u0627\u0628\u062f\u0623 \u0627\u0644\u062a\u0642\u064a\u064a\u0645 \u0627\u0644\u0645\u062c\u0627\u0646\u064a",
        "back_btn":       "\u2b05 \u0631\u062c\u0648\u0639",
        "skip_btn":       "\u23e9 \u062a\u062e\u0637\u064a",
        "processing":     (
            "\u2699\ufe0f <b>\u062c\u0627\u0631\u064d \u062a\u062d\u0644\u064a\u0644 \u0628\u064a\u0627\u0646\u0627\u062a\u0643...</b>\n\n"
            "\U0001f52c \u0641\u062d\u0635 \u0639\u0644\u0627\u0645\u0627\u062a \u0627\u0644\u062e\u0637\u0631\n"
            "\U0001f9e0 \u0627\u0633\u062a\u062e\u0644\u0627\u0635 \u0627\u0644\u062a\u0634\u062e\u064a\u0635\n"
            "\U0001f3cb \u062a\u0635\u0645\u064a\u0645 \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u062a\u0645\u0627\u0631\u064a\u0646\n"
            "\U0001f4dd \u0625\u0639\u062f\u0627\u062f \u062f\u0644\u064a\u0644 \u0627\u0644\u0639\u0644\u0627\u062c\u0627\u062a\n\n"
            "<i>\u0627\u0646\u062a\u0638\u0631 30-60 \u062b\u0627\u0646\u064a\u0629...</i>"
        ),
        "confirm_yes":    "\u2705 \u0635\u062d\u064a\u062d \u2014 \u0627\u0628\u062f\u0623 \u0627\u0644\u062a\u062d\u0644\u064a\u0644",
        "confirm_edit":   "\u270f \u062a\u0639\u062f\u064a\u0644 \u0627\u0644\u0625\u062c\u0627\u0628\u0627\u062a",
        "end_full_pdf":   "\U0001f4d6 \u062a\u062d\u0645\u064a\u0644 \u0627\u0644\u062a\u0642\u0631\u064a\u0631 \u0627\u0644\u0643\u0627\u0645\u0644 (PDF)",
        "end_quick_pdf":  "\U0001f4cb \u062a\u062d\u0645\u064a\u0644 \u0627\u0644\u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0633\u0631\u064a\u0639\u0629 (PDF)",
        "end_share":      "\U0001f4e4 \u0634\u0627\u0631\u0643 \u0648\u0627\u0643\u0633\u0628 \u0646\u0642\u0627\u0637\u0627\u064b",
        "end_new":        "\U0001f504 \u062a\u0642\u064a\u064a\u0645 \u062c\u062f\u064a\u062f",
        "end_points":     "\u2b50 \u0646\u0642\u0627\u0637\u064a",
        "error_msg":      "\u26a0 \u062e\u0637\u0623. \u0627\u0643\u062a\u0628 /start.",
        "cancel_msg":     "\u062a\u0645 \u0627\u0644\u0625\u0644\u063a\u0627\u0621. \u0627\u0643\u062a\u0628 /start.",
        "kb_only":        "\u26a0 \u064a\u0631\u062c\u0649 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 \u0627\u0644\u0623\u0632\u0631\u0627\u0631.",
        "emergency":      (
            "\U0001f6a8 <b>\u0639\u0644\u0627\u0645\u0627\u062a \u062e\u0637\u0631 \u0645\u0643\u062a\u0634\u0641\u0629</b>\n\n"
            "\u062a\u0648\u062c\u0647 \u0641\u0648\u0631\u0627\u064b \u0644\u0623\u0642\u0631\u0628 \u0645\u0631\u0643\u0632 \u0637\u0628\u064a.\n"
            "\U0001f4de 911 / 997"
        ),
        "email_q":        (
            "\U0001f4e7 <b>\u0623\u062f\u062e\u0644 \u0628\u0631\u064a\u062f\u0643 \u0627\u0644\u0625\u0644\u0643\u062a\u0631\u0648\u0646\u064a</b>\n\n"
            "\u0633\u0646\u0631\u0633\u0644 \u0644\u0643 \u062a\u0642\u0631\u064a\u0631\u0643 \u0648\u0646\u0635\u0627\u0626\u062d \u0627\u0644\u062a\u0639\u0627\u0641\u064a.\n"
            "<i>\u0645\u062b\u0627\u0644: name@gmail.com</i>"
        ),
        "email_invalid":  "\u26a0 \u0628\u0631\u064a\u062f \u063a\u064a\u0631 \u0635\u062d\u064a\u062d. \u062d\u0627\u0648\u0644 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649:",
        "extra_notes_q":  (
            "\U0001f4dd <b>\u0647\u0644 \u062a\u0631\u064a\u062f \u0625\u0636\u0627\u0641\u0629 \u0634\u064a\u0621\u061f</b>\n\n"
            "\u0633\u0627\u0639\u062f\u0646\u0627 \u0639\u0644\u0649 \u062a\u062e\u0635\u064a\u0635 \u062a\u0642\u064a\u064a\u0645\u0643:\n"
            "\u2022 \u0623\u0639\u0631\u0627\u0636 \u0623\u062e\u0631\u0649 \u0644\u0645 \u062a\u0630\u0643\u0631\u0647\u0627\n"
            "\u2022 \u0639\u0645\u0644\u064a\u0627\u062a \u0633\u0627\u0628\u0642\u0629 \u0623\u0648 \u0625\u0635\u0627\u0628\u0627\u062a\n"
            "\u2022 \u0627\u0644\u0623\u062f\u0648\u064a\u0629 \u0627\u0644\u062a\u064a \u062a\u062a\u0646\u0627\u0648\u0644\u0647\u0627\n"
            "\u2022 \u0623\u064a \u0634\u064a\u0621 \u0622\u062e\u0631 \u0645\u0641\u064a\u062f\n\n"
            "\u0627\u0643\u062a\u0628 \u0623\u062f\u0646\u0627\u0647 \u0623\u0648 <b>\u062a\u062e\u0637\u064a</b>:"
        ),
        "payment_intro":  (
            "\U0001f4b3 <b>\u0627\u062d\u0635\u0644 \u0639\u0644\u0649 \u062a\u0642\u0631\u064a\u0631\u0643 \u0627\u0644\u0643\u0627\u0645\u0644</b>\n\n"
            "\u2705 \u062a\u0634\u062e\u064a\u0635 \u0633\u0631\u064a\u0631\u064a\n"
            "\u2705 4 \u062a\u0645\u0627\u0631\u064a\u0646 \u0645\u0639 \u0631\u0648\u0627\u0628\u0637 \u0641\u064a\u062f\u064a\u0648\n"
            "\u2705 \u062f\u0644\u064a\u0644 \u0627\u0644\u0639\u0644\u0627\u062c\u0627\u062a \u0627\u0644\u0645\u0646\u0632\u0644\u064a\u0629\n"
            "\u2705 \u062a\u0639\u062f\u064a\u0644\u0627\u062a \u0627\u0644\u0623\u0646\u0634\u0637\u0629\n"
            "\u2705 \u0645\u062d\u0627\u0630\u064a\u0631 \u0648\u062a\u062d\u0630\u064a\u0631\u0627\u062a\n"
            "\u2705 PDF \u0643\u0627\u0645\u0644 + \u0628\u0637\u0627\u0642\u0629 \u0633\u0631\u064a\u0639\u0629\n\n"
            "\U0001f4b0 <b>\u0627\u0644\u0633\u0639\u0631: {price}</b>\n\n"
            "\u0623\u062f\u062e\u0644 <b>\u0643\u0648\u062f \u0645\u062c\u0627\u0646\u064a</b> \u0625\u0646 \u0643\u0627\u0646 \u0644\u062f\u064a\u0643:"
        ),
        "pay_stars_btn":  "\u2b50 \u0627\u062f\u0641\u0639 {stars} \u0646\u062c\u0645\u0629 ({price})",
        "enter_code_btn": "\U0001f511 \u0644\u062f\u064a \u0643\u0648\u062f \u0645\u062c\u0627\u0646\u064a",
        "use_points_btn": "\U0001f4af \u0627\u0633\u062a\u062e\u062f\u0645 \u0627\u0644\u0646\u0642\u0627\u0637 ({pts} \u0646\u0642\u0637\u0629)",
        "code_prompt":    "\U0001f511 \u0623\u062f\u062e\u0644 \u0643\u0648\u062f\u0643 \u0627\u0644\u0645\u062c\u0627\u0646\u064a:",
        "code_invalid":   "\u274c \u0643\u0648\u062f \u063a\u064a\u0631 \u0635\u062d\u064a\u062d \u0623\u0648 \u0645\u0633\u062a\u062e\u062f\u0645. \u062c\u0631\u0628 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649:",
        "share_msg":      (
            "\U0001f4e4 <b>\u0634\u0627\u0631\u0643 \u0648\u0627\u0643\u0633\u0628 \u0646\u0642\u0627\u0637!</b>\n\n"
            "\u2b50 <b>{pts} \u0646\u0642\u0637\u0629</b> \u062d\u062a\u0649 \u0627\u0644\u0622\u0646\n"
            "\U0001f3af <b>\u062a\u062d\u062a\u0627\u062c {needed} \u0646\u0642\u0637\u0629 \u0623\u062e\u0631\u0649</b> = \u062a\u0642\u064a\u064a\u0645 \u0645\u062c\u0627\u0646\u064a\n\n"
            "\u0631\u0627\u0628\u0637 \u0645\u0634\u0627\u0631\u0643\u062a\u0643 \u0627\u0644\u0634\u062e\u0635\u064a:\n"
            "<code>{link}</code>\n\n"
            "\u0643\u0644 \u0634\u062e\u0635 \u064a\u0633\u062a\u062e\u062f\u0645 \u0631\u0627\u0628\u0637\u0643 = <b>+10 \u0646\u0642\u0627\u0637</b>\n"
            "\U0001f3c6 <b>50 \u0646\u0642\u0637\u0629 = \u062a\u0642\u064a\u064a\u0645 \u0645\u062c\u0627\u0646\u064a</b>\n\n"
            "\u0643\u0648\u062f \u0645\u062c\u0627\u0646\u064a \u0644\u0634\u062e\u0635 \u0648\u0627\u062d\u062f:\n"
            "<code>{code}</code>"
        ),
        "points_msg":     (
            "\u2b50 <b>\u0646\u0642\u0627\u0637\u0643</b>\n\n"
            "\u0627\u0644\u0631\u0635\u064a\u062f: <b>{pts} \u0646\u0642\u0637\u0629</b>\n"
            "\u0627\u0644\u062d\u062f: <b>50 \u0646\u0642\u0637\u0629</b>\n"
            "\u062a\u062d\u062a\u0627\u062c: <b>{needed}</b>\n\n"
            "\u0631\u0627\u0628\u0637\u0643:\n<code>{link}</code>"
        ),
        "summary_header": "<b>\U0001f4cb \u0645\u0644\u062e\u0635 \u0628\u064a\u0627\u0646\u0627\u062a\u0643:</b>\n\n",
        "confirm_q":      "\n\u2705 <b>\u0647\u0644 \u0647\u0630\u0647 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0635\u062d\u064a\u062d\u0629\u061f</b>",
        "summary_fields": [
            ("name",             "\U0001f464 <b>\u0627\u0644\u0627\u0633\u0645:</b> {}"),
            ("age",              "\U0001f382 <b>\u0627\u0644\u0639\u0645\u0631:</b> {} \u0633\u0646\u0629"),
            ("gender",           "<b>\u0627\u0644\u062c\u0646\u0633:</b> {}"),
            ("occupation",       "\U0001f4bc <b>\u0627\u0644\u0645\u0647\u0646\u0629:</b> {}"),
            ("chief_complaint",  "\U0001f915 <b>\u0627\u0644\u0634\u0643\u0648\u0649:</b> {}"),
            ("body_region",      "\U0001f4cd <b>\u0627\u0644\u0645\u0646\u0637\u0642\u0629:</b> {}"),
            ("onset_duration",   "\u23f1 <b>\u0627\u0644\u0645\u062f\u0629:</b> {}"),
            ("pain_scale",       "\U0001f534 <b>\u0627\u0644\u0623\u0644\u0645:</b> {}/10"),
            ("medical_history",  "\U0001f48a <b>\u0627\u0644\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0637\u0628\u064a:</b> {}"),
        ],
        "disclaimer": (
            "\n\n<i>\u26a0 <b>\u0625\u062e\u0644\u0627\u0621 \u0645\u0633\u0624\u0648\u0644\u064a\u0629:</b> "
            "\u0644\u0623\u063a\u0631\u0627\u0636 \u062a\u0639\u0644\u064a\u0645\u064a\u0629 \u0641\u0642\u0637. "
            "\u0644\u064a\u0633 \u0628\u062f\u064a\u0644\u0627\u064b \u0639\u0646 \u0627\u0644\u062a\u0634\u062e\u064a\u0635 \u0627\u0644\u0645\u0647\u0646\u064a.</i>"
        ),
        "lang_select":  "\U0001f310 \u0627\u062e\u062a\u0631 \u0644\u063a\u062a\u0643:",
        "report_done":  "\u2705 <b>\u0627\u0643\u062a\u0645\u0644 \u0627\u0644\u062a\u0642\u0631\u064a\u0631!</b>",
        "free_badge":   "\U0001f3c6 \u062a\u0645 \u0627\u0633\u062a\u062e\u062f\u0627\u0645 \u0627\u0644\u062a\u0642\u064a\u064a\u0645 \u0627\u0644\u0645\u062c\u0627\u0646\u064a",
        "paid_badge":   "\U0001f4b3 \u062a\u0642\u064a\u064a\u0645 \u0645\u062f\u0641\u0648\u0639",
    }
}

QUESTIONS = {
    "en": [
        {"key": "name",               "q": "What is your full name?",                                                                    "type": "text"},
        {"key": "age",                "q": "How old are you?",                                                                            "type": "text"},
        {"key": "gender",             "q": "Gender:",                                                                                    "type": "keyboard", "options": ["Male", "Female"]},
        {"key": "occupation",         "q": "What is your occupation?",                                                                    "type": "text"},
        {"key": "chief_complaint",    "q": "Describe your main complaint in your own words:",                                             "type": "text"},
        {"key": "body_region",        "q": "Where is the primary pain?",                                                                 "type": "keyboard",
         "options": ["Neck / Head", "Shoulder", "Elbow / Forearm", "Wrist / Hand",
                     "Upper Back", "Lower Back / Pelvis", "Hip / Thigh",
                     "Knee", "Ankle / Foot", "Multiple areas"]},
        {"key": "onset_duration",     "q": "How long have you had this problem? (e.g. 3 days, 2 weeks)",                                 "type": "text"},
        {"key": "mechanism",          "q": "How did it start?",                                                                          "type": "keyboard",
         "options": ["Sudden", "Gradual", "After injury", "After exertion",
                     "Repetitive movement", "No clear cause"]},
        {"key": "pain_scale",         "q": "Rate your pain right now (0 = none, 10 = worst ever):",                                      "type": "keyboard",
         "options": ["0","1","2","3","4","5","6","7","8","9","10"]},
        {"key": "pain_character",     "q": "What does the pain feel like?",                                                              "type": "keyboard",
         "options": ["Sharp / stabbing", "Burning", "Numbness / tingling",
                     "Dull / aching", "Throbbing", "Stiffness"]},
        {"key": "radiation",          "q": "Does pain stay in one spot or travel? If travels, where to?",                               "type": "text"},
        {"key": "aggravating",        "q": "What makes it WORSE?",                                                                       "type": "keyboard",
         "options": ["Sitting", "Standing", "Walking", "Movement",
                     "Night / rest", "Lifting / bending", "Other"]},
        {"key": "relieving",          "q": "What makes it BETTER?",                                                                      "type": "keyboard",
         "options": ["Rest", "Heat", "Ice", "Movement",
                     "Medication", "Specific position", "Nothing"]},
        {"key": "associated_symptoms","q": "Any associated symptoms?",                                                                   "type": "keyboard",
         "options": ["Numbness in limbs", "Muscle weakness", "Dizziness",
                     "Headache", "Swelling", "Redness / warmth", "None"]},
        {"key": "previous_treatment", "q": "Previous treatment? (meds, PT, surgery, imaging...)",                                        "type": "text"},
        {"key": "medical_history",    "q": "Any chronic conditions? (diabetes, osteoporosis, cancer, rheumatism...)",                    "type": "text"},
        {"key": "activity_level",     "q": "Physical activity level:",                                                                   "type": "keyboard",
         "options": ["Inactive", "Light (1-2x/week)", "Moderate (3-4x/week)", "Active (5+/week)"]},
    ],
    "ar": [
        {"key": "name",               "q": "\u0645\u0627 \u0627\u0633\u0645\u0643 \u0627\u0644\u0643\u0627\u0645\u0644\u061f",                   "type": "text"},
        {"key": "age",                "q": "\u0643\u0645 \u0639\u0645\u0631\u0643\u061f",                                                        "type": "text"},
        {"key": "gender",             "q": "\u0627\u0644\u062c\u0646\u0633:",                                                                    "type": "keyboard", "options": ["\u0630\u0643\u0631", "\u0623\u0646\u062b\u0649"]},
        {"key": "occupation",         "q": "\u0645\u0627 \u0637\u0628\u064a\u0639\u0629 \u0639\u0645\u0644\u0643\u061f",                         "type": "text"},
        {"key": "chief_complaint",    "q": "\u0635\u0641 \u0634\u0643\u0648\u0627\u0643 \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629:",       "type": "text"},
        {"key": "body_region",        "q": "\u0641\u064a \u0623\u064a \u0645\u0646\u0637\u0642\u0629 \u062a\u0634\u0639\u0631 \u0628\u0627\u0644\u0623\u0644\u0645\u061f", "type": "keyboard",
         "options": ["\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633", "\u0627\u0644\u0643\u062a\u0641", "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f",
                    "\u0627\u0644\u0631\u0633\u063a \u0648\u0627\u0644\u064a\u062f", "\u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631", "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631",
                    "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630", "\u0627\u0644\u0631\u0643\u0628\u0629", "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645", "\u0623\u0643\u062b\u0631 \u0645\u0646 \u0645\u0646\u0637\u0642\u0629"]},
        {"key": "onset_duration",     "q": "\u0645\u0646\u0630 \u0645\u062a\u0649 \u0628\u062f\u0623\u062a \u0647\u0630\u0647 \u0627\u0644\u0645\u0634\u0643\u0644\u0629\u061f", "type": "text"},
        {"key": "mechanism",          "q": "\u0643\u064a\u0641 \u0628\u062f\u0623 \u0627\u0644\u0623\u0644\u0645\u061f",                         "type": "keyboard",
         "options": ["\u0641\u062c\u0623\u0629", "\u062a\u062f\u0631\u064a\u062c\u064a\u0627\u064b", "\u0628\u0639\u062f \u0625\u0635\u0627\u0628\u0629",
                    "\u0628\u0639\u062f \u0645\u062c\u0647\u0648\u062f", "\u062d\u0631\u0643\u0629 \u0645\u062a\u0643\u0631\u0631\u0629", "\u0628\u062f\u0648\u0646 \u0633\u0628\u0628"]},
        {"key": "pain_scale",         "q": "\u062f\u0631\u062c\u0629 \u0627\u0644\u0623\u0644\u0645 (0-10):",                                    "type": "keyboard",
         "options": ["0","1","2","3","4","5","6","7","8","9","10"]},
        {"key": "pain_character",     "q": "\u0637\u0628\u064a\u0639\u0629 \u0627\u0644\u0623\u0644\u0645:",                                     "type": "keyboard",
         "options": ["\u062d\u0627\u062f \u0637\u0627\u0639\u0646", "\u062d\u0627\u0631\u0642", "\u062a\u0646\u0645\u064a\u0644 / \u0648\u062e\u0632",
                    "\u062b\u0642\u064a\u0644 \u0636\u0627\u063a\u0637", "\u0646\u0627\u0628\u0636", "\u062a\u064a\u0628\u0633"]},
        {"key": "radiation",          "q": "\u0647\u0644 \u0627\u0644\u0623\u0644\u0645 \u0645\u0648\u0636\u0639\u064a \u0623\u0645 \u064a\u0646\u062a\u0634\u0631\u061f \u0623\u064a\u0646\u061f", "type": "text"},
        {"key": "aggravating",        "q": "\u0645\u0627 \u064a\u0632\u064a\u062f \u0627\u0644\u0623\u0644\u0645:",                              "type": "keyboard",
         "options": ["\u0627\u0644\u062c\u0644\u0648\u0633", "\u0627\u0644\u0648\u0642\u0648\u0641", "\u0627\u0644\u0645\u0634\u064a",
                    "\u0627\u0644\u062d\u0631\u0643\u0629", "\u0627\u0644\u0644\u064a\u0644", "\u0627\u0644\u0631\u0641\u0639 \u0648\u0627\u0644\u0627\u0646\u062d\u0646\u0627\u0621", "\u063a\u064a\u0631\u0647"]},
        {"key": "relieving",          "q": "\u0645\u0627 \u064a\u062e\u0641\u0641 \u0627\u0644\u0623\u0644\u0645:",                              "type": "keyboard",
         "options": ["\u0627\u0644\u0631\u0627\u062d\u0629", "\u0627\u0644\u062d\u0631\u0627\u0631\u0629", "\u0627\u0644\u062b\u0644\u062c",
                    "\u0627\u0644\u062d\u0631\u0643\u0629", "\u0627\u0644\u062f\u0648\u0627\u0621", "\u0648\u0636\u0639\u064a\u0629 \u0645\u0639\u064a\u0646\u0629", "\u0644\u0627 \u0634\u064a\u0621"]},
        {"key": "associated_symptoms","q": "\u0623\u0639\u0631\u0627\u0636 \u0645\u0635\u0627\u062d\u0628\u0629:",                               "type": "keyboard",
         "options": ["\u062a\u0646\u0645\u064a\u0644 \u0641\u064a \u0627\u0644\u0623\u0637\u0631\u0627\u0641", "\u0636\u0639\u0641 \u0639\u0636\u0644\u064a",
                    "\u062f\u0648\u062e\u0629", "\u0635\u062f\u0627\u0639", "\u062a\u0648\u0631\u0645", "\u0627\u062d\u0645\u0631\u0627\u0631", "\u0644\u0627 \u0634\u064a\u0621"]},
        {"key": "previous_treatment", "q": "\u0647\u0644 \u062c\u0631\u0628\u062a \u0639\u0644\u0627\u062c\u0627\u064b \u0633\u0627\u0628\u0642\u0627\u064b\u061f",  "type": "text"},
        {"key": "medical_history",    "q": "\u0647\u0644 \u062a\u0639\u0627\u0646\u064a \u0645\u0646 \u0623\u0645\u0631\u0627\u0636 \u0645\u0632\u0645\u0646\u0629\u061f",  "type": "text"},
        {"key": "activity_level",     "q": "\u0645\u0633\u062a\u0648\u0649 \u0646\u0634\u0627\u0637\u0643:",                                     "type": "keyboard",
         "options": ["\u063a\u064a\u0631 \u0646\u0634\u0637", "\u062e\u0641\u064a\u0641", "\u0645\u062a\u0648\u0633\u0637", "\u0639\u0627\u0644\u064a"]},
    ]
}

# EMAIL collection at question index 4 (after chief_complaint)
EMAIL_GATE_INDEX = 4


def ui(lang, key):
    return UI[lang].get(key, UI["en"].get(key, key))


def qs(lang):
    return QUESTIONS.get(lang, QUESTIONS["en"])


def n_qs(lang):
    return len(qs(lang))


def progress_bar(lang, index):
    n = n_qs(lang)
    filled = "\U0001f7e2" * (index + 1)
    empty  = "\u26aa" * (n - index - 1)
    return f"{filled}{empty} <b>({index+1}/{n})</b>"


def build_kb(options, show_back=True, lang="en"):
    keyboard = []
    row = []
    for i, opt in enumerate(options):
        row.append(InlineKeyboardButton(opt, callback_data=f"ans:{opt}"))
        if len(row) == 2 or i == len(options)-1:
            keyboard.append(row)
            row = []
    if show_back:
        keyboard.append([InlineKeyboardButton(ui(lang,"back_btn"), callback_data="back")])
    return InlineKeyboardMarkup(keyboard)


def build_summary(pd_data, lang):
    lines = [ui(lang, "summary_header")]
    for key, fmt in ui(lang, "summary_fields"):
        val = pd_data.get(key) or "-"
        lines.append(fmt.format(val))
    if pd_data.get("extra_notes"):
        note_lbl = "\U0001f4dd <b>Notes:</b>" if lang=="en" else "\U0001f4dd <b>\u0645\u0644\u0627\u062d\u0638\u0627\u062a:</b>"
        lines.append(f"{note_lbl} {pd_data['extra_notes']}")
    lines.append(ui(lang, "confirm_q"))
    return "\n".join(lines)


def check_red_flags(pd_data):
    combined = " ".join([pd_data.get(k,"") for k in
        ["associated_symptoms","chief_complaint","medical_history","mechanism"]]).lower()
    flags = []
    for kw, lbl in [
        ("bladder","bladder loss"), ("\u0645\u062b\u0627\u0646\u0629","bladder loss"),
        ("cancer","cancer hx"), ("\u0633\u0631\u0637\u0627\u0646","cancer hx"),
        ("cauda equina","cauda equina"),
    ]:
        if kw in combined: flags.append(lbl)
    try:
        if int(pd_data.get("pain_scale","0")) >= 9:
            flags.append("pain 9-10/10")
    except (ValueError, TypeError):
        pass
    return flags


def split_msg(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    while len(text) > max_len:
        sp = text.rfind("\n\n", 0, max_len)
        if sp == -1: sp = text.rfind("\n", 0, max_len)
        if sp < max_len//2: sp = max_len
        chunks.append(text[:sp].rstrip())
        text = text[sp:].lstrip("\n")
    if text.strip(): chunks.append(text.strip())
    return chunks


async def safe_send(message, text, markup=None, edit=False):
    kwargs = {"parse_mode": ParseMode.HTML}
    if markup: kwargs["reply_markup"] = markup
    try:
        if edit: await message.edit_text(text, **kwargs)
        else:    await message.reply_text(text, **kwargs)
    except Exception:
        plain = re.sub(r'<[^>]+>', '', text)
        try:
            if edit: await message.edit_text(plain, reply_markup=markup)
            else:    await message.reply_text(plain, reply_markup=markup)
        except Exception as e2:
            logger.error(f"send failed: {e2}")


async def generate_report(pd_data, lang):
    prompt = build_full_prompt(pd_data, lang)
    try:
        msg = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"API Error: {str(e)[:200]}"


# ── HANDLERS ─────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    tg_user = update.effective_user
    lang = "en"

    # Handle referral
    args = context.args
    if args:
        ref_code = args[0]
        if ref_code.startswith("REF_"):
            ref_code = ref_code[4:]
        elif ref_code.startswith("FREE"):
            context.user_data["pending_code"] = ref_code

    user = get_or_create_user(
        tg_user.id,
        tg_user.username or tg_user.first_name or "",
        lang
    )
    if args and not args[0].startswith("FREE"):
        process_start_referral(tg_user.id, args[0].replace("REF_",""))

    context.user_data.update({
        "lang": lang,
        "patient_data": {},
        "current_q": 0,
        "tg_id": tg_user.id,
        "email_collected": bool(user.get("email")),
    })

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("English \U0001f1ec\U0001f1e7", callback_data="lang:en"),
        InlineKeyboardButton("\u0639\u0631\u0628\u064a \U0001f1f8\U0001f1e6",  callback_data="lang:ar"),
    ]])
    await update.message.reply_text(
        "\U0001f310 <b>Welcome / \u0645\u0631\u062d\u0628\u0627</b>\n\nSelect language / \u0627\u062e\u062a\u0631 \u0644\u063a\u062a\u0643:",
        parse_mode=ParseMode.HTML, reply_markup=kb
    )
    return LANG_SELECT


async def lang_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    context.user_data["lang"] = lang
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    if context.user_data.get("tg_id"):
        update_user_lang(context.user_data["tg_id"], lang)

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(ui(lang,"start_btn"), callback_data="start_assessment")
    ]])
    await safe_send(query.message, ui(lang,"welcome"), markup=kb, edit=True)
    return LANG_SELECT


async def start_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["current_q"] = 0
    return await send_q(query.message, context, 0, edit=True)


async def send_q(message, context, q_index, edit=False):
    lang = context.user_data.get("lang","en")
    questions = qs(lang)

    # Email gate
    if (q_index == EMAIL_GATE_INDEX and
            not context.user_data.get("email_collected")):
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(ui(lang,"skip_btn"), callback_data="skip_email")
        ]])
        await safe_send(message, ui(lang,"email_q"), markup=kb, edit=edit)
        return EMAIL_STEP

    if q_index >= len(questions):
        return await show_extra_notes(message, context)

    q = questions[q_index]
    current = context.user_data["patient_data"].get(q["key"])
    current_str = f"\n<i>\u2022 Current: {current}</i>" if current else ""
    text = f"{progress_bar(lang,q_index)}\n\n{q['q']}{current_str}"

    if q["type"] == "keyboard":
        markup = build_kb(q["options"], show_back=(q_index>0), lang=lang)
    else:
        markup = (InlineKeyboardMarkup([[
            InlineKeyboardButton(ui(lang,"back_btn"), callback_data="back")
        ]]) if q_index > 0 else None)

    await safe_send(message, text, markup=markup, edit=edit)
    return ANSWERING


async def show_extra_notes(message, context):
    lang = context.user_data.get("lang","en")
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(ui(lang,"skip_btn"), callback_data="skip_notes")
    ]])
    try:
        await safe_send(message, ui(lang,"extra_notes_q"), markup=kb, edit=True)
    except Exception:
        await safe_send(message, ui(lang,"extra_notes_q"), markup=kb)
    return EXTRA_NOTES


async def show_summary(message, context):
    lang = context.user_data.get("lang","en")
    pd_data = context.user_data.get("patient_data",{})
    summary = build_summary(pd_data, lang)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(ui(lang,"confirm_yes"),  callback_data="confirm_yes"),
        InlineKeyboardButton(ui(lang,"confirm_edit"), callback_data="confirm_edit"),
    ]])
    try:
        await safe_send(message, summary, markup=kb, edit=True)
    except Exception:
        await safe_send(message, summary, markup=kb)
    return CONFIRMING


async def show_payment(message, context):
    lang  = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    pts   = get_user_points(tg_id) if tg_id else 0
    is_free = can_use_free(tg_id) if tg_id else True

    if is_free:
        # Go straight to analysis
        return await run_analysis_free(message, context)

    text = ui(lang,"payment_intro").replace("{price}", PRICE_LABEL)
    buttons = [[InlineKeyboardButton(
        ui(lang,"pay_stars_btn").replace("{stars}", str(PRICE_STARS)).replace("{price}", PRICE_LABEL),
        callback_data="pay_stars"
    )]]
    if pts >= POINTS_FOR_FREE:
        buttons.append([InlineKeyboardButton(
            ui(lang,"use_points_btn").replace("{pts}", str(pts)),
            callback_data="use_points"
        )])
    buttons.append([InlineKeyboardButton(ui(lang,"enter_code_btn"), callback_data="enter_code")])
    kb = InlineKeyboardMarkup(buttons)
    try:
        await safe_send(message, text, markup=kb, edit=True)
    except Exception:
        await safe_send(message, text, markup=kb)
    return PAYING


async def run_analysis_free(message, context):
    lang  = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    if tg_id: mark_free_used(tg_id)
    return await _do_analysis(message, context, paid=0)


async def run_analysis_paid(message, context):
    lang  = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    if tg_id: mark_paid(tg_id)
    return await _do_analysis(message, context, paid=1)


async def _do_analysis(message, context, paid=0):
    lang    = context.user_data.get("lang","en")
    pd_data = context.user_data.get("patient_data",{})
    tg_id   = context.user_data.get("tg_id")

    flags = check_red_flags(pd_data)
    if flags:
        await safe_send(message, ui(lang,"emergency"), edit=True)
        return ConversationHandler.END

    await safe_send(message, ui(lang,"processing"), edit=True)

    report = await generate_report(pd_data, lang)
    full_text = report + ui(lang,"disclaimer")
    context.user_data["last_report"]  = full_text
    context.user_data["patient_name"] = pd_data.get("name","Patient")

    # Save to DB
    if tg_id:
        save_assessment(
            tg_id, lang,
            pd_data.get("body_region",""),
            pd_data.get("chief_complaint",""),
            int(pd_data.get("pain_scale","0") or 0),
            paid, full_text
        )

    # Send report chunks
    chunks = split_msg(full_text)
    for i, chunk in enumerate(chunks):
        try:
            if i == 0: await safe_send(message, chunk, edit=True)
            else:      await safe_send(message, chunk)
        except Exception as e:
            logger.error(f"Chunk {i}: {e}")
            try: await safe_send(message, chunk)
            except: pass

    # End keyboard
    end_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(ui(lang,"end_full_pdf"),  callback_data="pdf_full")],
        [InlineKeyboardButton(ui(lang,"end_quick_pdf"), callback_data="pdf_quick")],
        [InlineKeyboardButton(ui(lang,"end_share"),     callback_data="share")],
        [InlineKeyboardButton(ui(lang,"end_new"),       callback_data="new_assessment")],
    ])
    badge = ui(lang,"free_badge") if not paid else ui(lang,"paid_badge")
    await safe_send(message, f"{ui(lang,'report_done')} {badge}", markup=end_kb)
    return ConversationHandler.END


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang    = context.user_data.get("lang","en")
    q_index = context.user_data.get("current_q",0)
    questions = qs(lang)
    state   = context.user_data.get("_state")

    # Email
    if not context.user_data.get("email_collected") and q_index == EMAIL_GATE_INDEX:
        email = update.message.text.strip()
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            await safe_send(update.message, ui(lang,"email_invalid"))
            return EMAIL_STEP
        context.user_data["email_collected"] = True
        tg_id = context.user_data.get("tg_id")
        if tg_id: update_user_email(tg_id, email)
        context.user_data["patient_data"]["email"] = email
        return await send_q(update.message, context, q_index)

    # Free code
    if context.user_data.get("_awaiting_code"):
        code = update.message.text.strip().upper()
        tg_id = context.user_data.get("tg_id")
        if tg_id and use_one_time_code(code, tg_id):
            context.user_data["_awaiting_code"] = False
            return await run_analysis_paid(update.message, context)
        else:
            # Invalid
            await safe_send(update.message, ui(lang,"code_invalid"))
            return CODE_ENTRY

    # Extra notes
    if q_index >= len(questions):
        context.user_data["patient_data"]["extra_notes"] = update.message.text.strip()
        return await show_summary(update.message, context)

    q = questions[q_index]
    if q["type"] != "text":
        await safe_send(update.message, ui(lang,"kb_only"))
        return ANSWERING

    context.user_data["patient_data"][q["key"]] = update.message.text.strip()
    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_q(update.message, context, next_q)


async def handle_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang  = context.user_data.get("lang","en")
    data  = query.data

    if data == "back":
        q_index = max(0, context.user_data.get("current_q",0) - 1)
        context.user_data["current_q"] = q_index
        return await send_q(query.message, context, q_index, edit=True)

    if data.startswith("ans:"):
        answer  = data[4:]
        q_index = context.user_data.get("current_q",0)
        questions = qs(lang)
        if q_index < len(questions):
            context.user_data["patient_data"][questions[q_index]["key"]] = answer
            context.user_data["current_q"] = q_index + 1
            return await send_q(query.message, context, q_index+1, edit=True)

    if data == "skip_email":
        context.user_data["email_collected"] = True
        q_index = context.user_data.get("current_q",0)
        return await send_q(query.message, context, q_index, edit=True)

    if data == "skip_notes":
        context.user_data["patient_data"]["extra_notes"] = ""
        return await show_summary(query.message, context)

    if data == "confirm_yes":
        return await show_payment(query.message, context)

    if data == "confirm_edit":
        context.user_data["current_q"] = 0
        return await send_q(query.message, context, 0, edit=True)

    if data == "pay_stars":
        return await send_stars_invoice(query, context)

    if data == "use_points":
        tg_id = context.user_data.get("tg_id")
        if tg_id and redeem_points_for_free(tg_id):
            return await run_analysis_paid(query.message, context)

    if data == "enter_code":
        context.user_data["_awaiting_code"] = True
        await safe_send(query.message, ui(lang,"code_prompt"), edit=True)
        return CODE_ENTRY

    if data == "pdf_full":
        return await send_pdf(query, context, full=True)

    if data == "pdf_quick":
        return await send_pdf(query, context, full=False)

    if data == "share":
        return await show_share(query, context)

    if data == "new_assessment":
        return await new_assessment_cb(update, context)

    if data == "my_points":
        return await show_points(query, context)

    return ANSWERING


async def send_stars_invoice(query, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    title = "PhysioAssist Assessment Report"
    desc  = ("Full physiotherapy assessment with personalized exercise program, "
             "home PT modalities guide, and 2 PDF reports.")
    await query.message.reply_invoice(
        title=title,
        description=desc,
        payload="physio_assessment",
        currency="XTR",
        prices=[LabeledPrice(label="PhysioAssist Report", amount=PRICE_STARS)],
    )
    return PAYING


async def precheckout_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_analysis_paid(update.message, context)


async def send_pdf(query, context: ContextTypes.DEFAULT_TYPE, full: bool = True):
    lang   = context.user_data.get("lang","en")
    report = context.user_data.get("last_report","")
    name   = context.user_data.get("patient_name","Patient")

    if not report:
        await query.message.reply_text("No report found. Complete an assessment first.")
        return

    gen_msg = "\U0001f4c4 Generating PDF..." if lang=="en" else "\U0001f4c4 \u062c\u0627\u0631\u064d \u0625\u0646\u0634\u0627\u0621 PDF..."
    await query.message.reply_text(gen_msg)

    if full:
        pdf_bytes = generate_full_pdf(report, name, lang)
        filename  = f"PhysioAssist_Full_{name.replace(' ','_')}.pdf"
        caption   = "Your Full PhysioAssist Report" if lang=="en" else "\u062a\u0642\u0631\u064a\u0631\u0643 \u0627\u0644\u0643\u0627\u0645\u0644"
    else:
        pdf_bytes = generate_quick_card_pdf(report, name, lang)
        filename  = f"PhysioAssist_QuickCard_{name.replace(' ','_')}.pdf"
        caption   = "Your Quick Reference Card" if lang=="en" else "\u0628\u0637\u0627\u0642\u062a\u0643 \u0627\u0644\u0633\u0631\u064a\u0639\u0629"

    await query.message.reply_document(
        document=BytesIO(pdf_bytes),
        filename=filename,
        caption=caption
    )


async def show_share(query, context: ContextTypes.DEFAULT_TYPE):
    lang  = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    if not tg_id: return

    # Award share points
    record_referral_share(tg_id)
    pts    = get_user_points(tg_id)
    needed = max(0, POINTS_FOR_FREE - pts)
    ref_code = get_referral_code(tg_id)
    link  = f"https://t.me/{BOT_USERNAME}?start=REF_{ref_code}"
    code  = generate_one_time_code(tg_id)

    text = ui(lang,"share_msg").replace("{pts}",str(pts)).replace(
        "{needed}",str(needed)).replace("{link}",link).replace("{code}",code)

    await safe_send(query.message, text)


async def show_points(query, context: ContextTypes.DEFAULT_TYPE):
    lang  = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    if not tg_id: return

    pts    = get_user_points(tg_id)
    needed = max(0, POINTS_FOR_FREE - pts)
    ref_code = get_referral_code(tg_id)
    link  = f"https://t.me/{BOT_USERNAME}?start=REF_{ref_code}"

    text = ui(lang,"points_msg").replace("{pts}",str(pts)).replace(
        "{needed}",str(needed)).replace("{link}",link)

    await safe_send(query.message, text)


async def new_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang","en")
    tg_id = context.user_data.get("tg_id")
    email_collected = context.user_data.get("email_collected", False)
    context.user_data["patient_data"] = {}
    context.user_data["current_q"]    = 0
    context.user_data["email_collected"] = email_collected
    return await send_q(query.message, context, 0, edit=False)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang","en")
    context.user_data.clear()
    await update.message.reply_text(ui(lang,"cancel_msg"), parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command /stats"""
    from database import get_stats
    s = get_stats()
    text = (
        f"\U0001f4ca <b>PhysioAssist Stats</b>\n\n"
        f"Total users: <b>{s['total_users']}</b>\n"
        f"Total assessments: <b>{s['total_assessments']}</b>\n"
        f"Paid assessments: <b>{s['paid_assessments']}</b>\n"
        f"Emails collected: <b>{s['emails_collected']}</b>"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        lang = "en"
        if hasattr(context, "user_data"):
            lang = context.user_data.get("lang","en")
        await update.effective_message.reply_text(
            ui(lang,"error_msg"), parse_mode=ParseMode.HTML
        )


# ── MAIN ─────────────────────────────────────────
def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG_SELECT: [
                CallbackQueryHandler(lang_cb,             pattern="^lang:"),
                CallbackQueryHandler(start_assessment_cb, pattern="^start_assessment$"),
            ],
            ANSWERING: [
                CallbackQueryHandler(handle_btn),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            EMAIL_STEP: [
                CallbackQueryHandler(handle_btn, pattern="^skip_email$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            EXTRA_NOTES: [
                CallbackQueryHandler(handle_btn, pattern="^skip_notes$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            CODE_ENTRY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            CONFIRMING: [
                CallbackQueryHandler(handle_btn, pattern="^(confirm_yes|confirm_edit)$"),
            ],
            PAYING: [
                CallbackQueryHandler(handle_btn,
                    pattern="^(pay_stars|use_points|enter_code)$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(PreCheckoutQueryHandler(precheckout_cb))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_cb))
    app.add_handler(CallbackQueryHandler(send_pdf,          pattern="^pdf_(full|quick)$"))
    app.add_handler(CallbackQueryHandler(show_share,        pattern="^share$"))
    app.add_handler(CallbackQueryHandler(show_points,       pattern="^my_points$"))
    app.add_handler(CallbackQueryHandler(new_assessment_cb, pattern="^new_assessment$"))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_error_handler(error_handler)

    logger.info("PhysioAssist v4.0 starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
