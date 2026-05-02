#!/usr/bin/env python3
"""
PhysioAssist Bot - MINIMAL VERSION FOR TESTING
Full logging to diagnose issues
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Setup DETAILED logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/bot_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8660311978

logger.info("="*80)
logger.info("🚀 BOT STARTING")
logger.info("="*80)
logger.info(f"BOT_TOKEN: {BOT_TOKEN[:20]}..." if BOT_TOKEN else "❌ BOT_TOKEN NOT SET")
logger.info(f"ADMIN_ID: {ADMIN_ID}")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN is missing!")
    sys.exit(1)


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


async def main():
    """Main entry point"""
    logger.info("🔧 Initializing Application...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    logger.info("✅ Application created")
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("✅ Handlers added")
    logger.info("🚀 Starting polling...")
    
    # Initialize and start
    await app.initialize()
    logger.info("✅ App initialized")
    
    await app.start()
    logger.info("✅ App started")
    
    await app.updater.start_polling()
    logger.info("✅ Polling started - BOT IS RUNNING!")
    
    # Keep running
    await app.updater.idle()


if __name__ == '__main__':
    import asyncio
    
    logger.info("🚀 STARTING BOT PROCESS")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Bot interrupted")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
