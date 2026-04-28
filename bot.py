"""
PhysioAssist Bot v2.0
- Bilingual: English (default) + Arabic
- Back button navigation
- Edit previous answers
- Additional notes box
- PDF export
- Better clinical output
- Fixed text truncation
"""

import logging
import os
import textwrap
from io import BytesIO

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

load_dotenv()

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not BOT_TOKEN: raise ValueError("BOT_TOKEN not set")
if not ANTHROPIC_API_KEY: raise ValueError("ANTHROPIC_API_KEY not set")

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── STATES ───────────────────────────────────────
LANG_SELECT = 0
ANSWERING   = 1
CONFIRMING  = 2
EXTRA_NOTES = 3

# ─── TRANSLATIONS ────────────────────────────────
T = {
    "en": {
        "welcome": (
            "\U0001f3e5 Welcome to PhysioAssist\n\n"
            "I will help you:\n"
            "\u2705 Assess your condition using international PT protocols\n"
            "\u2705 Get a personalized home exercise program\n"
            "\u2705 Receive clinical instructions & precautions\n\n"
            "\u26a0\ufe0f This bot is for home-manageable conditions only.\n"
            "\U0001f6a8 For severe pain or accidents: go to Emergency immediately.\n\n"
            "\U0001f557 Assessment takes about 5 minutes."
        ),
        "start_btn": "\U0001f680 Start Assessment",
        "back_btn": "\u2b05\ufe0f Back",
        "processing": (
            "\u2699\ufe0f Analyzing your data...\n\n"
            "\U0001f52c Screening for red flags\n"
            "\U0001f9e0 Generating diagnosis\n"
            "\U0001f3cb Designing exercise program\n"
            "\U0001f4dd Preparing full report\n\n"
            "This may take 30-60 seconds..."
        ),
        "confirm_yes": "\u2705 Correct, Start Analysis",
        "confirm_no": "\u270f\ufe0f Edit Answers",
        "summary_header": "\U0001f4cb Summary of your data:\n",
        "confirm_q": "\n\u2705 Is this information correct?",
        "end_msg": "\u2705 Report complete. Start a new assessment?",
        "new_assessment": "\U0001f504 New Assessment",
        "about_btn": "\u2139\ufe0f About",
        "download_pdf": "\U0001f4e5 Download PDF Report",
        "error_msg": "\u26a0\ufe0f An error occurred. Type /start to try again.",
        "cancel_msg": "Assessment cancelled. Type /start to begin again.",
        "keyboard_only": "\u26a0\ufe0f Please select from the buttons below.",
        "progress_filled": "\U0001f7e2",
        "progress_empty": "\u26aa",
        "emergency": (
            "\U0001f6a8 WARNING: Red flags detected - immediate medical assessment needed.\n\n"
            "Please go to the nearest emergency room NOW.\n"
            "\U0001f4de Emergency: 911 / 997\n\n"
            "\u26a0\ufe0f Do not delay seeking medical care."
        ),
        "extra_notes_q": (
            "\U0001f4dd Final Question:\n\n"
            "Please share any additional information that may help your assessment:\n\n"
            "- Other symptoms not mentioned\n"
            "- Previous surgeries or injuries\n"
            "- Medications you are taking\n"
            "- Work or sports activities\n"
            "- Anything else relevant to your condition\n\n"
            "Type your notes below, or press Skip if nothing to add:"
        ),
        "skip_btn": "\u23e9 Skip",
        "edit_answer": "\u270f\ufe0f Edit this answer",
        "select_question": "Select which question to edit:",
        "lang_select": "\U0001f310 Please select your language:",
        "disclaimer": (
            "\n\n\u26a0\ufe0f MEDICAL DISCLAIMER\n"
            "This report is for educational purposes based on PT protocols. "
            "It is not a substitute for professional diagnosis and treatment. "
            "Consult a licensed physiotherapist for full evaluation."
        ),
    },
    "ar": {
        "welcome": (
            "\U0001f3e5 \u0645\u0631\u062d\u0628\u0627\u064b \u0628\u0643 \u0641\u064a PhysioAssist\n\n"
            "\u0633\u0623\u0633\u0627\u0639\u062f\u0643 \u0639\u0644\u0649:\n"
            "\u2705 \u062a\u0642\u064a\u064a\u0645 \u062d\u0627\u0644\u062a\u0643 \u0628\u0646\u0627\u0621\u064b \u0639\u0644\u0649 \u0628\u0631\u0648\u062a\u0648\u0643\u0648\u0644\u0627\u062a \u062f\u0648\u0644\u064a\u0629\n"
            "\u2705 \u0628\u0631\u0646\u0627\u0645\u062c \u062a\u0645\u0627\u0631\u064a\u0646 \u0639\u0644\u0627\u062c\u064a\u0629 \u0645\u0646\u0632\u0644\u064a\u0629 \u0645\u062e\u0635\u0635\u0629\n"
            "\u2705 \u062a\u0639\u0644\u064a\u0645\u0627\u062a \u0637\u0628\u064a\u0629 \u0648\u0625\u0631\u0634\u0627\u062f\u0627\u062a \u0633\u0644\u0648\u0643\u064a\u0629 \u062f\u0642\u064a\u0642\u0629\n\n"
            "\u26a0\ufe0f \u0647\u0630\u0627 \u0627\u0644\u0628\u0648\u062a \u0645\u062e\u0635\u0635 \u0644\u0644\u062d\u0627\u0644\u0627\u062a \u0627\u0644\u062a\u064a \u064a\u0645\u0643\u0646 \u0639\u0644\u0627\u062c\u0647\u0627 \u0645\u0646\u0632\u0644\u064a\u064b\u0627 \u0641\u0642\u0637.\n"
            "\U0001f6a8 \u0641\u064a \u062d\u0627\u0644 \u0627\u0644\u0623\u0644\u0645 \u0627\u0644\u0634\u062f\u064a\u062f \u0623\u0648 \u0627\u0644\u062d\u0648\u0627\u062f\u062b: \u062a\u0648\u062c\u0647 \u0644\u0644\u0637\u0648\u0627\u0631\u0626 \u0641\u0648\u0631\u064b\u0627.\n\n"
            "\U0001f557 \u0627\u0644\u062a\u0642\u064a\u064a\u0645 \u064a\u0633\u062a\u063a\u0631\u0642 \u062d\u0648\u0627\u0644\u064a 5 \u062f\u0642\u0627\u0626\u0642."
        ),
        "start_btn": "\U0001f680 \u0627\u0628\u062f\u0623 \u0627\u0644\u062a\u0642\u064a\u064a\u0645",
        "back_btn": "\u2b05\ufe0f \u0631\u062c\u0648\u0639",
        "processing": (
            "\u2699\ufe0f \u062c\u0627\u0631\u064d \u062a\u062d\u0644\u064a\u0644 \u0628\u064a\u0627\u0646\u0627\u062a\u0643...\n\n"
            "\U0001f52c \u0641\u062d\u0635 \u0639\u0644\u0627\u0645\u0627\u062a \u0627\u0644\u062e\u0637\u0631\n"
            "\U0001f9e0 \u0627\u0633\u062a\u062e\u0644\u0627\u0635 \u0627\u0644\u062a\u0634\u062e\u064a\u0635\n"
            "\U0001f3cb \u062a\u0635\u0645\u064a\u0645 \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u062a\u0645\u0627\u0631\u064a\u0646\n"
            "\U0001f4dd \u0625\u0639\u062f\u0627\u062f \u0627\u0644\u062a\u0642\u0631\u064a\u0631 \u0627\u0644\u0643\u0627\u0645\u0644\n\n"
            "\u0642\u062f \u064a\u0633\u062a\u063a\u0631\u0642 \u0647\u0630\u0627 30-60 \u062b\u0627\u0646\u064a\u0629..."
        ),
        "confirm_yes": "\u2705 \u0635\u062d\u064a\u062d\u060c \u0627\u0628\u062f\u0623 \u0627\u0644\u062a\u062d\u0644\u064a\u0644",
        "confirm_no": "\u270f\ufe0f \u062a\u0639\u062f\u064a\u0644 \u0627\u0644\u0625\u062c\u0627\u0628\u0627\u062a",
        "summary_header": "\U0001f4cb \u0645\u0644\u062e\u0635 \u0628\u064a\u0627\u0646\u0627\u062a\u0643:\n",
        "confirm_q": "\n\u2705 \u0647\u0644 \u0647\u0630\u0647 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0635\u062d\u064a\u062d\u0629\u061f",
        "end_msg": "\u2705 \u0627\u0646\u062a\u0647\u0649 \u0627\u0644\u062a\u0642\u0631\u064a\u0631. \u0647\u0644 \u062a\u0631\u064a\u062f \u062a\u0642\u064a\u064a\u0645\u0627\u064b \u062c\u062f\u064a\u062f\u0627\u064b\u061f",
        "new_assessment": "\U0001f504 \u062a\u0642\u064a\u064a\u0645 \u062c\u062f\u064a\u062f",
        "about_btn": "\u2139\ufe0f \u062d\u0648\u0644 \u0627\u0644\u0628\u0648\u062a",
        "download_pdf": "\U0001f4e5 \u062a\u062d\u0645\u064a\u0644 \u0627\u0644\u062a\u0642\u0631\u064a\u0631 PDF",
        "error_msg": "\u26a0\ufe0f \u062d\u062f\u062b \u062e\u0637\u0623. \u0627\u0643\u062a\u0628 /start \u0644\u0644\u0645\u062d\u0627\u0648\u0644\u0629 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649.",
        "cancel_msg": "\u062a\u0645 \u0627\u0644\u0625\u0644\u063a\u0627\u0621. \u0627\u0643\u062a\u0628 /start \u0644\u0644\u0628\u062f\u0621 \u0645\u0646 \u062c\u062f\u064a\u062f.",
        "keyboard_only": "\u26a0\ufe0f \u064a\u0631\u062c\u0649 \u0627\u0644\u0627\u062e\u062a\u064a\u0627\u0631 \u0645\u0646 \u0627\u0644\u0623\u0632\u0631\u0627\u0631 \u0623\u062f\u0646\u0627\u0647.",
        "progress_filled": "\U0001f7e2",
        "progress_empty": "\u26aa",
        "emergency": (
            "\U0001f6a8 \u062a\u062d\u0630\u064a\u0631: \u062a\u0645 \u0627\u0643\u062a\u0634\u0627\u0641 \u0639\u0644\u0627\u0645\u0627\u062a \u062e\u0637\u0631 - \u064a\u0644\u0632\u0645 \u062a\u0642\u064a\u064a\u0645 \u0637\u0628\u064a \u0641\u0648\u0631\u064a\n\n"
            "\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u0648\u062c\u0647 \u0641\u0648\u0631\u064b\u0627 \u0644\u0623\u0642\u0631\u0628 \u0645\u0631\u0643\u0632 \u0637\u0628\u064a.\n"
            "\U0001f4de \u0627\u0644\u0637\u0648\u0627\u0631\u0626: 911 / 997\n\n"
            "\u26a0\ufe0f \u0644\u0627 \u062a\u0624\u062c\u0644 \u0637\u0644\u0628 \u0627\u0644\u0631\u0639\u0627\u064a\u0629 \u0627\u0644\u0637\u0628\u064a\u0629."
        ),
        "extra_notes_q": (
            "\U0001f4dd \u0627\u0644\u0633\u0624\u0627\u0644 \u0627\u0644\u0623\u062e\u064a\u0631:\n\n"
            "\u064a\u0631\u062c\u0649 \u0625\u0636\u0627\u0641\u0629 \u0623\u064a \u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0625\u0636\u0627\u0641\u064a\u0629 \u062a\u0633\u0627\u0639\u062f \u0641\u064a \u062a\u0642\u064a\u064a\u0645\u0643:\n\n"
            "- \u0623\u0639\u0631\u0627\u0636 \u0623\u062e\u0631\u0649 \u0644\u0645 \u064a\u062a\u0645 \u0630\u0643\u0631\u0647\u0627\n"
            "- \u0639\u0645\u0644\u064a\u0627\u062a \u0633\u0627\u0628\u0642\u0629 \u0623\u0648 \u0625\u0635\u0627\u0628\u0627\u062a \u0633\u0627\u0628\u0642\u0629\n"
            "- \u0627\u0644\u0623\u062f\u0648\u064a\u0629 \u0627\u0644\u062a\u064a \u062a\u062a\u0646\u0627\u0648\u0644\u0647\u0627\n"
            "- \u0637\u0628\u064a\u0639\u0629 \u0639\u0645\u0644\u0643 \u0623\u0648 \u0646\u0634\u0627\u0637\u0643 \u0627\u0644\u0631\u064a\u0627\u0636\u064a\n"
            "- \u0623\u064a \u0634\u064a\u0621 \u0622\u062e\u0631 \u0645\u062a\u0639\u0644\u0642 \u0628\u062d\u0627\u0644\u062a\u0643\n\n"
            "\u0627\u0643\u062a\u0628 \u0645\u0644\u0627\u062d\u0638\u0627\u062a\u0643 \u0623\u062f\u0646\u0627\u0647\u060c \u0623\u0648 \u0627\u0636\u063a\u0637 \u062a\u062e\u0637\u064a \u0625\u0630\u0627 \u0644\u0645 \u064a\u0643\u0646 \u0647\u0646\u0627\u0643 \u0634\u064a\u0621 \u0644\u0644\u0625\u0636\u0627\u0641\u0629:"
        ),
        "skip_btn": "\u23e9 \u062a\u062e\u0637\u064a",
        "edit_answer": "\u270f\ufe0f \u062a\u0639\u062f\u064a\u0644 \u0647\u0630\u0627 \u0627\u0644\u062c\u0648\u0627\u0628",
        "select_question": "\u0627\u062e\u062a\u0631 \u0627\u0644\u0633\u0624\u0627\u0644 \u0627\u0644\u0630\u064a \u062a\u0631\u064a\u062f \u062a\u0639\u062f\u064a\u0644\u0647:",
        "lang_select": "\U0001f310 \u064a\u0631\u062c\u0649 \u0627\u062e\u062a\u064a\u0627\u0631 \u0627\u0644\u0644\u063a\u0629:",
        "disclaimer": (
            "\n\n\u26a0\ufe0f \u0625\u062e\u0644\u0627\u0621 \u0627\u0644\u0645\u0633\u0624\u0648\u0644\u064a\u0629\n"
            "\u0647\u0630\u0627 \u0627\u0644\u062a\u0642\u0631\u064a\u0631 \u0644\u0623\u063a\u0631\u0627\u0636 \u062a\u0639\u0644\u064a\u0645\u064a\u0629 \u0641\u0642\u0637. "
            "\u0644\u064a\u0633 \u0628\u062f\u064a\u0644\u0627\u064b \u0639\u0646 \u0627\u0644\u062a\u0634\u062e\u064a\u0635 \u0648\u0627\u0644\u0639\u0644\u0627\u062c \u0627\u0644\u0645\u0647\u0646\u064a. "
            "\u0627\u0633\u062a\u0634\u0631 \u0623\u062e\u0635\u0627\u0626\u064a \u0639\u0644\u0627\u062c \u0637\u0628\u064a\u0639\u064a \u0645\u0631\u062e\u0635\u064b\u0627 \u0644\u0644\u062a\u0642\u064a\u064a\u0645 \u0627\u0644\u0643\u0627\u0645\u0644."
        ),
    }
}

# ─── QUESTIONS ────────────────────────────────────
QUESTIONS = {
    "en": [
        {"key": "name",               "q": "What is your name?",                                                                                    "type": "text"},
        {"key": "age",                "q": "What is your age?",                                                                                     "type": "text"},
        {"key": "gender",             "q": "Gender:",                                                                                               "type": "keyboard", "options": ["Male", "Female"]},
        {"key": "occupation",         "q": "What is your occupation?",                                                                              "type": "text"},
        {"key": "chief_complaint",    "q": "What is your main complaint? (describe in your own words)",                                             "type": "text"},
        {"key": "body_region",        "q": "Which area is the primary pain location?",                                                              "type": "keyboard",
         "options": ["Neck/Head", "Shoulder", "Elbow/Forearm", "Wrist/Hand", "Upper Back", "Lower Back/Pelvis", "Hip/Thigh", "Knee", "Ankle/Foot", "Multiple areas"]},
        {"key": "onset_duration",     "q": "How long have you had this pain? (e.g. 3 days, 2 weeks, 1 month)",                                     "type": "text"},
        {"key": "mechanism",          "q": "How did the pain start?",                                                                               "type": "keyboard",
         "options": ["Sudden onset", "Gradual onset", "After injury/trauma", "After exertion", "After repetitive movement", "No clear cause"]},
        {"key": "pain_scale",         "q": "Rate your current pain (0 = no pain, 10 = worst imaginable):",                                         "type": "keyboard",
         "options": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]},
        {"key": "pain_character",     "q": "How would you describe the pain?",                                                                      "type": "keyboard",
         "options": ["Sharp/stabbing", "Burning", "Numbness/tingling", "Dull/aching", "Throbbing", "Stiffness"]},
        {"key": "radiation",          "q": "Does the pain stay in one place or radiate? If it radiates, where to?",                                "type": "text"},
        {"key": "aggravating",        "q": "What makes the pain WORSE?",                                                                            "type": "keyboard",
         "options": ["Sitting", "Standing", "Walking", "Movement", "Night/rest", "Lifting", "Bending"]},
        {"key": "relieving",          "q": "What makes the pain BETTER?",                                                                           "type": "keyboard",
         "options": ["Rest", "Heat", "Ice/cold", "Movement", "Medication", "Specific position", "Nothing"]},
        {"key": "associated_symptoms","q": "Do you have any of these associated symptoms?",                                                         "type": "keyboard",
         "options": ["Numbness in limbs", "Muscle weakness", "Dizziness", "Headache", "Swelling", "Redness/warmth", "None of these"]},
        {"key": "previous_treatment", "q": "Have you tried any treatment? (medications, PT, imaging, etc.)",                                       "type": "text"},
        {"key": "medical_history",    "q": "Do you have any chronic conditions? (diabetes, osteoporosis, cancer, rheumatism, etc.)",                "type": "text"},
        {"key": "activity_level",     "q": "What is your physical activity level?",                                                                 "type": "keyboard",
         "options": ["Inactive (<30 min/week)", "Light (1-2x/week)", "Moderate (3-4x/week)", "Active (5+ times/week)"]},
    ],
    "ar": [
        {"key": "name",               "q": "\u0645\u0627 \u0627\u0633\u0645\u0643\u061f",                                                            "type": "text"},
        {"key": "age",                "q": "\u0643\u0645 \u0639\u0645\u0631\u0643\u061f",                                                             "type": "text"},
        {"key": "gender",             "q": "\u0627\u0644\u062c\u0646\u0633:",                                                                         "type": "keyboard", "options": ["\u0630\u0643\u0631", "\u0623\u0646\u062b\u0649"]},
        {"key": "occupation",         "q": "\u0645\u0627 \u0637\u0628\u064a\u0639\u0629 \u0639\u0645\u0644\u0643\u061f",                              "type": "text"},
        {"key": "chief_complaint",    "q": "\u0645\u0627 \u0647\u064a \u0634\u0643\u0648\u0627\u0643 \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629\u061f", "type": "text"},
        {"key": "body_region",        "q": "\u0641\u064a \u0623\u064a \u0645\u0646\u0637\u0642\u0629 \u062a\u0634\u0639\u0631 \u0628\u0627\u0644\u0623\u0644\u0645\u061f", "type": "keyboard",
         "options": ["\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633", "\u0627\u0644\u0643\u062a\u0641", "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f", "\u0627\u0644\u0631\u0633\u063a \u0648\u0627\u0644\u064a\u062f", "\u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631", "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631 \u0648\u0627\u0644\u062d\u0648\u0636", "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630", "\u0627\u0644\u0631\u0643\u0628\u0629", "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645", "\u0623\u0643\u062b\u0631 \u0645\u0646 \u0645\u0646\u0637\u0642\u0629"]},
        {"key": "onset_duration",     "q": "\u0645\u0646\u0630 \u0645\u062a\u0649 \u0628\u062f\u0623 \u0627\u0644\u0623\u0644\u0645\u061f",           "type": "text"},
        {"key": "mechanism",          "q": "\u0643\u064a\u0641 \u0628\u062f\u0623 \u0627\u0644\u0623\u0644\u0645\u061f",                              "type": "keyboard",
         "options": ["\u0641\u062c\u0623\u0629", "\u062a\u062f\u0631\u064a\u062c\u064a\u0627\u064b", "\u0628\u0639\u062f \u0625\u0635\u0627\u0628\u0629", "\u0628\u0639\u062f \u0645\u062c\u0647\u0648\u062f", "\u0628\u0639\u062f \u062d\u0631\u0643\u0629 \u0645\u062a\u0643\u0631\u0631\u0629", "\u0628\u062f\u0648\u0646 \u0633\u0628\u0628 \u0648\u0627\u0636\u062d"]},
        {"key": "pain_scale",         "q": "\u062f\u0631\u062c\u0629 \u0623\u0644\u0645\u0643 \u0645\u0646 0 \u0625\u0644\u0649 10:",                 "type": "keyboard",
         "options": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]},
        {"key": "pain_character",     "q": "\u0643\u064a\u0641 \u062a\u0635\u0641 \u0637\u0628\u064a\u0639\u0629 \u0627\u0644\u0623\u0644\u0645\u061f", "type": "keyboard",
         "options": ["\u062d\u0627\u062f \u0637\u0627\u0639\u0646", "\u062d\u0627\u0631\u0642", "\u062a\u0646\u0645\u064a\u0644 / \u0648\u062e\u0632", "\u062b\u0642\u064a\u0644 \u0636\u0627\u063a\u0637", "\u0646\u0627\u0628\u0636", "\u062a\u064a\u0628\u0633"]},
        {"key": "radiation",          "q": "\u0647\u0644 \u0627\u0644\u0623\u0644\u0645 \u0645\u0648\u0636\u0639\u064a \u0623\u0645 \u064a\u0646\u062a\u0634\u0631\u061f \u0648\u0625\u0630\u0627 \u0643\u0627\u0646 \u064a\u0646\u062a\u0634\u0631\u060c \u0623\u064a\u0646\u061f", "type": "text"},
        {"key": "aggravating",        "q": "\u0645\u0627 \u0627\u0644\u0630\u064a \u064a\u0632\u064a\u062f \u0627\u0644\u0623\u0644\u0645\u061f",      "type": "keyboard",
         "options": ["\u0627\u0644\u062c\u0644\u0648\u0633", "\u0627\u0644\u0648\u0642\u0648\u0641", "\u0627\u0644\u0645\u0634\u064a", "\u0627\u0644\u062d\u0631\u0643\u0629", "\u0627\u0644\u0644\u064a\u0644 / \u0627\u0644\u0631\u0627\u062d\u0629", "\u0627\u0644\u0631\u0641\u0639", "\u0627\u0644\u0627\u0646\u062d\u0646\u0627\u0621"]},
        {"key": "relieving",          "q": "\u0645\u0627 \u0627\u0644\u0630\u064a \u064a\u062e\u0641\u0641 \u0627\u0644\u0623\u0644\u0645\u061f",      "type": "keyboard",
         "options": ["\u0627\u0644\u0631\u0627\u062d\u0629", "\u0627\u0644\u062d\u0631\u0627\u0631\u0629", "\u0627\u0644\u062b\u0644\u062c", "\u0627\u0644\u062d\u0631\u0643\u0629", "\u0627\u0644\u062f\u0648\u0627\u0621", "\u0648\u0636\u0639\u064a\u0629 \u0645\u0639\u064a\u0646\u0629", "\u0644\u0627 \u0634\u064a\u0621"]},
        {"key": "associated_symptoms","q": "\u0647\u0644 \u064a\u0648\u062c\u062f \u0623\u064a \u0645\u0646 \u0647\u0630\u0647 \u0627\u0644\u0623\u0639\u0631\u0627\u0636 \u0627\u0644\u0645\u0635\u0627\u062d\u0628\u0629\u061f", "type": "keyboard",
         "options": ["\u062a\u0646\u0645\u064a\u0644 \u0641\u064a \u0627\u0644\u0623\u0637\u0631\u0627\u0641", "\u0636\u0639\u0641 \u0639\u0636\u0644\u064a", "\u062f\u0648\u062e\u0629", "\u0635\u062f\u0627\u0639", "\u062a\u0648\u0631\u0645", "\u0627\u062d\u0645\u0631\u0627\u0631 \u0648\u062d\u0631\u0627\u0631\u0629", "\u0644\u0627 \u0634\u064a\u0621 \u0645\u0646 \u0647\u0630\u0627"]},
        {"key": "previous_treatment", "q": "\u0647\u0644 \u062c\u0631\u0628\u062a \u0623\u064a \u0639\u0644\u0627\u062c \u0633\u0627\u0628\u0642\u0627\u064b\u061f", "type": "text"},
        {"key": "medical_history",    "q": "\u0647\u0644 \u062a\u0639\u0627\u0646\u064a \u0645\u0646 \u0623\u0645\u0631\u0627\u0636 \u0645\u0632\u0645\u0646\u0629\u061f", "type": "text"},
        {"key": "activity_level",     "q": "\u0645\u0633\u062a\u0648\u0649 \u0646\u0634\u0627\u0637\u0643 \u0627\u0644\u0628\u062f\u0646\u064a\u061f", "type": "keyboard",
         "options": ["\u063a\u064a\u0631 \u0646\u0634\u0637", "\u062e\u0641\u064a\u0641", "\u0645\u062a\u0648\u0633\u0637", "\u0639\u0627\u0644\u064a"]},
    ]
}

SUMMARY_FIELDS_EN = [
    ("name",             "\U0001f464 Name: {}"),
    ("age",              "\U0001f382 Age: {} years"),
    ("gender",           "Gender: {}"),
    ("occupation",       "\U0001f4bc Occupation: {}"),
    ("chief_complaint",  "\U0001f915 Complaint: {}"),
    ("body_region",      "\U0001f4cd Pain area: {}"),
    ("onset_duration",   "\u23f1\ufe0f Duration: {}"),
    ("pain_scale",       "\U0001f534 Pain score: {}/10"),
    ("medical_history",  "\U0001f48a Medical history: {}"),
]

SUMMARY_FIELDS_AR = [
    ("name",             "\U0001f464 \u0627\u0644\u0627\u0633\u0645: {}"),
    ("age",              "\U0001f382 \u0627\u0644\u0639\u0645\u0631: {} \u0633\u0646\u0629"),
    ("gender",           "\u0627\u0644\u062c\u0646\u0633: {}"),
    ("occupation",       "\U0001f4bc \u0627\u0644\u0645\u0647\u0646\u0629: {}"),
    ("chief_complaint",  "\U0001f915 \u0627\u0644\u0634\u0643\u0648\u0649: {}"),
    ("body_region",      "\U0001f4cd \u0645\u0646\u0637\u0642\u0629 \u0627\u0644\u0623\u0644\u0645: {}"),
    ("onset_duration",   "\u23f1\ufe0f \u0627\u0644\u0645\u062f\u0629: {}"),
    ("pain_scale",       "\U0001f534 \u062f\u0631\u062c\u0629 \u0627\u0644\u0623\u0644\u0645: {}/10"),
    ("medical_history",  "\U0001f48a \u0627\u0644\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u0637\u0628\u064a: {}"),
]


# ─── HELPERS ─────────────────────────────────────
def t(lang, key):
    return T[lang].get(key, T["en"].get(key, key))


def get_questions(lang):
    return QUESTIONS.get(lang, QUESTIONS["en"])


def get_num_questions(lang):
    return len(get_questions(lang))


def get_progress(lang, index):
    n = get_num_questions(lang)
    filled = t(lang, "progress_filled") * (index + 1)
    empty = t(lang, "progress_empty") * (n - index - 1)
    return f"{filled}{empty} ({index + 1}/{n})"


def build_keyboard(options, back_index=None, lang="en"):
    keyboard = []
    row = []
    for i, option in enumerate(options):
        row.append(InlineKeyboardButton(option, callback_data=f"ans:{option}"))
        if len(row) == 2 or i == len(options) - 1:
            keyboard.append(row)
            row = []
    if back_index is not None and back_index >= 0:
        keyboard.append([InlineKeyboardButton(t(lang, "back_btn"), callback_data="back")])
    return InlineKeyboardMarkup(keyboard)


def build_summary(patient_data, lang):
    fields = SUMMARY_FIELDS_AR if lang == "ar" else SUMMARY_FIELDS_EN
    lines = [t(lang, "summary_header")]
    for key, fmt in fields:
        val = patient_data.get(key, "-")
        lines.append(fmt.format(val))
    if patient_data.get("extra_notes"):
        note_label = "\U0001f4dd \u0645\u0644\u0627\u062d\u0638\u0627\u062a" if lang == "ar" else "\U0001f4dd Additional notes"
        lines.append(f"{note_label}: {patient_data['extra_notes']}")
    lines.append(t(lang, "confirm_q"))
    return "\n".join(lines)


def check_red_flags(patient_data):
    combined = " ".join([
        patient_data.get("associated_symptoms", ""),
        patient_data.get("chief_complaint", ""),
        patient_data.get("medical_history", ""),
        patient_data.get("mechanism", ""),
    ]).lower()
    found = []
    triggers = [
        ("\u0645\u062b\u0627\u0646\u0629", "bladder control loss"),
        ("bladder", "bladder control loss"),
        ("\u0633\u0631\u0637\u0627\u0646", "cancer history"),
        ("cancer", "cancer history"),
        ("cauda equina", "cauda equina symptoms"),
    ]
    for kw, label in triggers:
        if kw in combined:
            found.append(label)
    try:
        if int(patient_data.get("pain_scale", "0")) >= 9:
            found.append("severe pain 9-10/10")
    except (ValueError, TypeError):
        pass
    return found


def split_message(text, max_len=4000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    while len(text) > max_len:
        # Try to split at section boundary first
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at == -1:
            split_at = text.rfind("\n", 0, max_len)
        if split_at == -1 or split_at < max_len // 2:
            split_at = max_len
        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip("\n")
    if text.strip():
        chunks.append(text.strip())
    return chunks


def generate_pdf_bytes(report_text: str, patient_name: str) -> bytes:
    """Generate a simple text-based PDF."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.enums import TA_LEFT

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                 rightMargin=2*cm, leftMargin=2*cm,
                                 topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        style = ParagraphStyle('body', fontName='Helvetica', fontSize=10,
                                leading=14, alignment=TA_LEFT)
        title_style = ParagraphStyle('title', fontName='Helvetica-Bold',
                                      fontSize=14, leading=18, alignment=TA_LEFT)
        story = []
        story.append(Paragraph("PhysioAssist - Assessment Report", title_style))
        story.append(Paragraph(f"Patient: {patient_name}", style))
        story.append(Spacer(1, 0.5*cm))

        for line in report_text.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.2*cm))
            elif line.startswith("###"):
                story.append(Paragraph(line.replace("#", "").strip(), title_style))
            else:
                # Escape HTML special chars
                line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(line, style))

        doc.build(story)
        return buf.getvalue()
    except ImportError:
        # Fallback: plain text as bytes
        return report_text.encode("utf-8")


# ─── AI ENGINE ───────────────────────────────────
def build_prompt(patient_data: dict, lang: str) -> str:
    lang_instruction = "Respond entirely in English." if lang == "en" else "Respond entirely in Arabic."

    return f"""You are an expert physiotherapist and rehabilitation specialist.
{lang_instruction}

PROTOCOLS: APTA CPGs | NICE Guidelines | McKenzie MDT | Cochrane Reviews | WHO Rehab 2023

PATIENT DATA:
Name: {patient_data.get('name')}
Age: {patient_data.get('age')} | Gender: {patient_data.get('gender')} | Occupation: {patient_data.get('occupation')}
Activity level: {patient_data.get('activity_level')}

COMPLAINT:
Chief complaint: {patient_data.get('chief_complaint')}
Body region: {patient_data.get('body_region')}
Duration: {patient_data.get('onset_duration')}
Mechanism: {patient_data.get('mechanism')}
Pain score: {patient_data.get('pain_scale')}/10
Pain character: {patient_data.get('pain_character')}
Radiation: {patient_data.get('radiation')}
Aggravating: {patient_data.get('aggravating')}
Relieving: {patient_data.get('relieving')}
Associated symptoms: {patient_data.get('associated_symptoms')}
Previous treatment: {patient_data.get('previous_treatment')}
Medical history: {patient_data.get('medical_history')}
Additional notes: {patient_data.get('extra_notes', 'None')}

Write a COMPLETE physiotherapy assessment report using this EXACT structure.
IMPORTANT: Complete EVERY section fully. Do not truncate any section.

=== RED FLAG SCREENING ===
State clearly if any red flags are present and what action is needed.

=== CLINICAL ASSESSMENT ===
Most likely diagnosis: [name + ICD-10]
Differential diagnoses: [list]
Clinical reasoning: [why this diagnosis based on patient data]
Condition stage: Acute / Subacute / Chronic

=== TREATMENT GOALS ===
Week 1-2: [goals]
Week 3-6: [goals]
Week 6-12: [goals]

=== HOME EXERCISE PROGRAM ===
[For each exercise - provide ALL of the following:]

EXERCISE [N]: [Name]
Target: [specific muscle/structure]
Goal: [why this exercise for this patient]
Starting position: [exact body position]
Step-by-step execution:
  1. [step]
  2. [step]
  3. [step]
Sets: X | Reps: X | Hold: X seconds
Rest between sets: X seconds
Frequency: X times per day
Duration: X weeks
Progression: [how to make it harder over time]
Video reference: [YouTube channel name] - [URL with timestamp if applicable e.g. youtube.com/watch?v=XXXXX&t=90]
WARNING: [specific warning for this exercise]

[Provide 4-5 exercises total - COMPLETE all details for each]

=== WEEKLY SCHEDULE ===
Week 1-2: [specific daily schedule]
Week 3-6: [specific daily schedule]
Week 6-12: [specific daily schedule]

=== ACTIVITY MODIFICATIONS (DAILY LIFE) ===
[This section is MANDATORY and must be detailed]
- Sleeping position: [exact recommendation]
- Sitting posture: [exact recommendation]
- Work modifications: [exact recommendation based on occupation]
- Lifting technique: [exact instructions]
- Driving/commuting: [if relevant]
- Sports/exercise: [what to avoid, what is allowed]
- Household activities: [specific modifications]

=== THERMAL THERAPY ===
Ice: [when, how long, frequency]
Heat: [when, how long, frequency]

=== CONTRAINDICATIONS & PRECAUTIONS ===
[List everything the patient must AVOID for their specific condition]
- Movements to avoid: [specific list]
- Activities to limit: [specific list]
- Postures to avoid: [specific list]
- Warning signs to stop exercise: [list]

=== RECOVERY TIMELINE & EXPECTATIONS ===
Week 1: [what to expect]
Week 2-4: [what to expect]
Month 2-3: [what to expect]
Signs of improvement: [list]
Signs of deterioration: [list]

=== WHEN TO SEE A SPECIALIST ===
See physiotherapist urgently if: [list]
See doctor if: [list]
Go to emergency if: [list]
"""


async def generate_report(patient_data: dict, lang: str) -> str:
    prompt = build_prompt(patient_data, lang)
    try:
        msg = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        logger.error(f"API error: {e}")
        return f"API Error: {str(e)[:300]}"


# ─── HANDLERS ────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("English \U0001f1ec\U0001f1e7", callback_data="lang:en"),
        InlineKeyboardButton("\u0639\u0631\u0628\u064a \U0001f1f8\U0001f1e6", callback_data="lang:ar"),
    ]])
    await update.message.reply_text(
        "\U0001f310 Welcome / \u0645\u0631\u062d\u0628\u0627\n\nPlease select your language / \u0627\u062e\u062a\u0631 \u0644\u063a\u062a\u0643:",
        reply_markup=keyboard
    )
    return LANG_SELECT


async def lang_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    context.user_data["lang"] = lang
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    context.user_data["answers_history"] = []

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "start_btn"), callback_data="start_assessment")
    ]])
    await query.message.edit_text(t(lang, "welcome"), reply_markup=keyboard)
    return LANG_SELECT


async def start_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=True)


async def send_question(message, context, q_index, edit=False):
    lang = context.user_data.get("lang", "en")
    questions = get_questions(lang)
    n = len(questions)

    if q_index >= n:
        return await show_extra_notes(message, context)

    q = questions[q_index]
    progress = get_progress(lang, q_index)

    # Show current answer if editing
    current_val = context.user_data["patient_data"].get(q["key"])
    current_str = f"\n[Current: {current_val}]" if current_val else ""

    text = f"{progress}\n\n? {q['q']}{current_str}"

    back_index = q_index - 1

    if q["type"] == "keyboard":
        markup = build_keyboard(q["options"], back_index=back_index, lang=lang)
    else:
        # For text questions, add back button separately
        if back_index >= 0:
            markup = InlineKeyboardMarkup([[
                InlineKeyboardButton(t(lang, "back_btn"), callback_data="back")
            ]])
        else:
            markup = None

    try:
        if edit:
            await message.edit_text(text, reply_markup=markup)
        else:
            await message.reply_text(text, reply_markup=markup)
    except Exception:
        await message.reply_text(text, reply_markup=markup)

    return ANSWERING


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "en")
    q_index = context.user_data.get("current_q", 0)
    questions = get_questions(lang)

    if q_index >= len(questions):
        # Extra notes
        context.user_data["patient_data"]["extra_notes"] = update.message.text.strip()
        return await show_summary(update.message, context)

    q = questions[q_index]
    if q["type"] != "text":
        await update.message.reply_text(t(lang, "keyboard_only"))
        return ANSWERING

    context.user_data["patient_data"][q["key"]] = update.message.text.strip()
    next_q = q_index + 1
    context.user_data["current_q"] = next_q
    return await send_question(update.message, context, next_q)


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    data = query.data

    if data == "back":
        q_index = context.user_data.get("current_q", 0)
        prev = max(0, q_index - 1)
        context.user_data["current_q"] = prev
        return await send_question(query.message, context, prev, edit=True)

    if data.startswith("ans:"):
        answer = data[4:]
        q_index = context.user_data.get("current_q", 0)
        questions = get_questions(lang)
        if q_index < len(questions):
            q = questions[q_index]
            context.user_data["patient_data"][q["key"]] = answer
            next_q = q_index + 1
            context.user_data["current_q"] = next_q
            return await send_question(query.message, context, next_q, edit=True)

    if data == "confirm_yes":
        return await run_analysis(query, context)

    if data == "confirm_edit":
        context.user_data["current_q"] = 0
        return await send_question(query.message, context, 0, edit=True)

    if data == "skip_notes":
        context.user_data["patient_data"]["extra_notes"] = ""
        return await show_summary(query.message, context)

    if data == "new_assessment":
        return await new_assessment_cb(update, context)

    return ANSWERING


async def show_extra_notes(message, context):
    lang = context.user_data.get("lang", "en")
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "skip_btn"), callback_data="skip_notes")
    ]])
    try:
        await message.edit_text(t(lang, "extra_notes_q"), reply_markup=keyboard)
    except Exception:
        await message.reply_text(t(lang, "extra_notes_q"), reply_markup=keyboard)
    return EXTRA_NOTES


async def show_summary(message, context):
    lang = context.user_data.get("lang", "en")
    patient_data = context.user_data.get("patient_data", {})
    summary = build_summary(patient_data, lang)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(lang, "confirm_yes"), callback_data="confirm_yes"),
            InlineKeyboardButton(t(lang, "confirm_no"),  callback_data="confirm_edit"),
        ]
    ])
    try:
        await message.edit_text(summary, reply_markup=keyboard)
    except Exception:
        await message.reply_text(summary, reply_markup=keyboard)
    return CONFIRMING


async def run_analysis(query, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "en")
    patient_data = context.user_data.get("patient_data", {})

    flags = check_red_flags(patient_data)
    if flags:
        await query.message.edit_text(t(lang, "emergency"))
        return ConversationHandler.END

    await query.message.edit_text(t(lang, "processing"))

    report = await generate_report(patient_data, lang)
    full = report + t(lang, "disclaimer")

    context.user_data["last_report"] = full
    context.user_data["patient_name"] = patient_data.get("name", "Patient")

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
        [InlineKeyboardButton(t(lang, "download_pdf"), callback_data="download_pdf")],
        [InlineKeyboardButton(t(lang, "new_assessment"), callback_data="new_assessment")],
    ])
    end_label = "Report complete / \u0627\u0646\u062a\u0647\u0649 \u0627\u0644\u062a\u0642\u0631\u064a\u0631" if lang == "en" else t(lang, "end_msg")
    await query.message.reply_text(end_label, reply_markup=end_kb)
    return ConversationHandler.END


async def download_pdf_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    report = context.user_data.get("last_report", "")
    name = context.user_data.get("patient_name", "Patient")

    if not report:
        await query.message.reply_text("No report available. Please complete an assessment first.")
        return

    await query.message.reply_text("\U0001f4c4 Generating PDF..." if lang == "en" else "\U0001f4c4 \u062c\u0627\u0631\u064d \u0625\u0646\u0634\u0627\u0621 PDF...")

    pdf_bytes = generate_pdf_bytes(report, name)
    filename = f"PhysioAssist_Report_{name.replace(' ','_')}.pdf"

    await query.message.reply_document(
        document=BytesIO(pdf_bytes),
        filename=filename,
        caption="PhysioAssist Report" if lang == "en" else "\u062a\u0642\u0631\u064a\u0631 PhysioAssist"
    )


async def new_assessment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["patient_data"] = {}
    context.user_data["current_q"] = 0
    return await send_question(query.message, context, 0, edit=False)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "en")
    context.user_data.clear()
    await update.message.reply_text(t(lang, "cancel_msg"))
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Error occurred. Type /start to restart. / \u062e\u0637\u0623. \u0627\u0643\u062a\u0628 /start"
        )


# ─── MAIN ────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    n_en = len(QUESTIONS["en"])

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG_SELECT: [
                CallbackQueryHandler(lang_selected,       pattern="^lang:"),
                CallbackQueryHandler(start_assessment_cb, pattern="^start_assessment$"),
            ],
            ANSWERING: [
                CallbackQueryHandler(handle_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            EXTRA_NOTES: [
                CallbackQueryHandler(handle_button, pattern="^skip_notes$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            CONFIRMING: [
                CallbackQueryHandler(handle_button, pattern="^(confirm_yes|confirm_edit)$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(download_pdf_cb,   pattern="^download_pdf$"))
    app.add_handler(CallbackQueryHandler(new_assessment_cb, pattern="^new_assessment$"))
    app.add_error_handler(error_handler)

    logger.info("PhysioAssist Bot v2.0 starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
