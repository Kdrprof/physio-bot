#!/usr/bin/env python3
"""
PhysioAssist Oracle v8.0 - FINAL VERSION
Single clean entry point
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from anthropic import Anthropic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ADMIN_ID = 8660311978

if not BOT_TOKEN or not ANTHROPIC_API_KEY:
    logger.error("❌ Missing BOT_TOKEN or ANTHROPIC_API_KEY")
    exit(1)

# Initialize Anthropic client
client = Anthropic()


class PhysioBot:
    def __init__(self):
        self.sessions = {}
        logger.info("✅ PhysioBot initialized")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start - Show mode selection"""
        user_id = update.effective_user.id
        logger.info(f"📱 User {user_id} started bot")
        
        self.sessions[user_id] = {'mode': None, 'language': None, 'messages': []}
        
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
            [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')],
            [InlineKeyboardButton("ℹ️ About Modes", callback_data='mode_info')]
        ]
        
        text = "🏥 **PhysioAssist Oracle v8.0**\n\nSelect your mode:"
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def mode_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mode selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == 'mode_info':
            text = "**👨‍💼 Admin**: Full access\n**👤 User**: Regular mode"
            keyboard = [
                [InlineKeyboardButton("👨‍💼 Admin", callback_data='mode_admin')],
                [InlineKeyboardButton("👤 User", callback_data='mode_user')]
            ]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            return
        
        mode = 'admin' if query.data == 'mode_admin' else 'user'
        
        if mode == 'admin' and user_id != ADMIN_ID:
            await query.answer("❌ Admin only!", show_alert=True)
            return
        
        self.sessions[user_id]['mode'] = mode
        logger.info(f"✅ User {user_id} mode: {mode}")
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
        ]
        text = f"Mode: {mode.upper()}\n\nSelect language:"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def lang_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        language = 'English' if query.data == 'lang_en' else 'Arabic'
        self.sessions[user_id]['language'] = language
        
        text = "Great! Tell me your issue:" if language == 'English' else "رائع! أخبرني عن مشكلتك:"
        await query.edit_message_text(text, parse_mode='Markdown')
        logger.info(f"✅ User {user_id} language: {language}")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.sessions:
            await self.start(update, context)
            return
        
        session = self.sessions[user_id]
        language = session.get('language', 'English')
        
        session['messages'].append({'role': 'user', 'content': text})
        
        try:
            response = client.messages.create(
                model="gpt-4.1-mini",
                max_tokens=300,
                messages=session['messages']
            )
            
            reply = response.content[0].text
            session['messages'].append({'role': 'assistant', 'content': reply})
            await update.message.reply_text(reply)
            logger.info(f"✅ Reply sent to {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            await update.message.reply_text(f"Error: {str(e)}")


async def main():
    """Main entry point"""
    logger.info("🚀 Starting PhysioAssist Oracle...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    bot = PhysioBot()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.mode_callback, pattern='^mode_'))
    app.add_handler(CallbackQueryHandler(bot.lang_callback, pattern='^lang_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.message_handler))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ BOT STARTED!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
