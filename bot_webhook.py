#!/usr/bin/env python3
"""
PhysioAssist Bot - WEBHOOK VERSION FOR RAILWAY
Uses FastAPI for webhook instead of polling
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import json

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8660311978
PORT = int(os.getenv('PORT', 8000))
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL', 'https://physio-bot.up.railway.app')

logger.info("="*80)
logger.info("🚀 WEBHOOK BOT STARTING")
logger.info("="*80)
logger.info(f"BOT_TOKEN: {BOT_TOKEN[:20]}..." if BOT_TOKEN else "❌ BOT_TOKEN NOT SET")
logger.info(f"ADMIN_ID: {ADMIN_ID}")
logger.info(f"PORT: {PORT}")
logger.info(f"WEBHOOK_URL: {RAILWAY_STATIC_URL}")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN is missing!")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI()
bot = Bot(token=BOT_TOKEN)

# Store application instance
application = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    logger.info(f"✅ START command received from user {user_id}")
    
    try:
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
            [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')],
            [InlineKeyboardButton("ℹ️ About Modes", callback_data='mode_info')]
        ]
        
        text = "🏥 **PhysioAssist Oracle v8.0**\n\nSelect your mode:"
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        logger.info(f"✅ Buttons sent to user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error in start: {e}", exc_info=True)
        await update.message.reply_text(f"Error: {str(e)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    logger.info(f"✅ Button clicked by user {user_id}: {query.data}")
    
    try:
        if query.data == 'mode_info':
            text = "**👨‍💼 Admin**: Full access\n**👤 User**: Regular mode"
            keyboard = [
                [InlineKeyboardButton("👨‍💼 Admin", callback_data='mode_admin')],
                [InlineKeyboardButton("👤 User", callback_data='mode_user')]
            ]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data == 'mode_admin':
            if user_id != ADMIN_ID:
                await query.answer("❌ Admin only!", show_alert=True)
                logger.warning(f"⚠️ Non-admin user {user_id} tried to access admin mode")
                return
            
            await query.edit_message_text(
                "✅ Admin Mode Activated\n\nSelect language:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
                    [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
                ])
            )
            logger.info(f"✅ Admin mode activated for user {user_id}")
        
        elif query.data == 'mode_user':
            await query.edit_message_text(
                "👤 User Mode\n\nSelect language:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
                    [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
                ])
            )
            logger.info(f"✅ User mode activated for user {user_id}")
        
        elif query.data == 'lang_en':
            await query.edit_message_text("✅ English selected\n\nReady to help!")
            logger.info(f"✅ English selected by user {user_id}")
        
        elif query.data == 'lang_ar':
            await query.edit_message_text("✅ تم اختيار العربية\n\nجاهز للمساعدة!")
            logger.info(f"✅ Arabic selected by user {user_id}")
    
    except Exception as e:
        logger.error(f"❌ Error in button_callback: {e}", exc_info=True)
        await query.answer(f"Error: {str(e)}", show_alert=True)


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
    logger.info("✅ Health check")
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
    global application
    
    try:
        logger.info("🔧 Initializing Application...")
        
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Application created")
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("✅ Handlers added")
        
        # Initialize
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
