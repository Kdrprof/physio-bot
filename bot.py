#!/usr/bin/env python3
"""
PhysioAssist Oracle v8.0 - Fresh Start Bot
Hybrid mode selection: Admin vs User
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from anthropic import Anthropic
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize clients
client = Anthropic()

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ADMIN_ID = 8660311978

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set!")
    sys.exit(1)

if not ANTHROPIC_API_KEY:
    logger.error("❌ ANTHROPIC_API_KEY not set!")
    sys.exit(1)


class PhysioBot:
    """Main bot class"""
    
    def __init__(self):
        self.sessions = {}
        logger.info("✅ PhysioBot initialized")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - Show mode selection"""
        user_id = update.effective_user.id
        
        logger.info(f"📱 User {user_id} started bot")
        
        # Initialize session
        self.sessions[user_id] = {
            'mode': None,
            'language': None,
            'stage': 'mode_selection',
            'messages': []
        }
        
        # Create mode selection keyboard
        keyboard = [
            [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
            [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')],
            [InlineKeyboardButton("ℹ️ About Modes", callback_data='mode_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🏥 **PhysioAssist Oracle v8.0**\n\n"
            "Welcome! Please select your mode:\n\n"
            "👨‍💼 **Admin Mode** - Full access, debug enabled\n"
            "👤 **User Mode** - Regular experience with payment\n\n"
            "Choose one to get started:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"✅ Mode selection shown to user {user_id}")
    
    async def handle_mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle mode selection callback"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == 'mode_info':
            info_text = (
                "🔍 **Mode Comparison:**\n\n"
                "**👨‍💼 Admin Mode:**\n"
                "✅ Full access\n"
                "✅ No payment\n"
                "✅ Debug info\n\n"
                "**👤 User Mode:**\n"
                "✅ Regular experience\n"
                "✅ Payment system\n"
                "✅ Subscriptions\n\n"
                "Which mode do you want?"
            )
            keyboard = [
                [InlineKeyboardButton("👨‍💼 Admin Mode", callback_data='mode_admin')],
                [InlineKeyboardButton("👤 User Mode", callback_data='mode_user')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=info_text, reply_markup=reply_markup, parse_mode='Markdown')
            return
        
        # Set mode
        mode = 'admin' if query.data == 'mode_admin' else 'user'
        
        # Check admin access
        if mode == 'admin' and user_id != ADMIN_ID:
            await query.answer("❌ Admin mode is restricted!", show_alert=True)
            return
        
        self.sessions[user_id]['mode'] = mode
        logger.info(f"✅ User {user_id} selected mode: {mode}")
        
        # Show language selection
        await self.show_language_selection(query, user_id, mode)
    
    async def show_language_selection(self, query, user_id: int, mode: str) -> None:
        """Show language selection"""
        mode_label = "ADMIN" if mode == 'admin' else "USER"
        
        text = (
            f"🏥 **PhysioAssist Oracle v8.0**\n\n"
            f"Mode: {mode_label}\n\n"
            f"Select your language:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
            [InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"✅ Language selection shown to user {user_id}")
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle language selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        language = 'English' if query.data == 'lang_en' else 'Arabic'
        self.sessions[user_id]['language'] = language
        self.sessions[user_id]['stage'] = 'chat'
        
        mode = self.sessions[user_id]['mode']
        is_admin = mode == 'admin' and user_id == ADMIN_ID
        
        if language == 'English':
            greeting = (
                "Great! Let's start your assessment.\n\n"
                "Tell me: What brings you here today?"
            )
        else:
            greeting = (
                "رائع! لنبدأ التقييم.\n\n"
                "أخبرني: ما الذي يجعلك هنا اليوم؟"
            )
        
        if is_admin:
            greeting += f"\n\n🐛 **DEBUG MODE**\nUser: {user_id}\nMode: ADMIN"
        
        await query.edit_message_text(text=greeting, parse_mode='Markdown')
        logger.info(f"✅ User {user_id} selected language: {language}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.sessions:
            await self.start(update, context)
            return
        
        session = self.sessions[user_id]
        language = session.get('language', 'English')
        mode = session.get('mode')
        is_admin = mode == 'admin' and user_id == ADMIN_ID
        
        # Store message
        session['messages'].append({'role': 'user', 'content': text})
        
        try:
            # Get AI response
            system_prompt = (
                "You are a physiotherapy assistant. Help users with their pain and movement issues."
                if language == 'English'
                else "أنت مساعد علاج طبيعي. ساعد المستخدمين في مشاكلهم الصحية."
            )
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                system=system_prompt,
                messages=session['messages']
            )
            
            ai_text = response.content[0].text
            session['messages'].append({'role': 'assistant', 'content': ai_text})
            
            if is_admin:
                ai_text += f"\n\n🐛 **DEBUG**: {len(session['messages'])} messages"
            
            await update.message.reply_text(ai_text)
            logger.info(f"✅ Response sent to user {user_id}")
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            error_msg = f"Error: {str(e)}" if language == 'English' else f"خطأ: {str(e)}"
            if is_admin:
                error_msg += f"\n\n🐛 {str(e)}"
            await update.message.reply_text(error_msg)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"❌ Update {update} caused error {context.error}")


async def main():
    """Main entry point"""
    logger.info("🚀 Starting PhysioAssist Oracle v8.0...")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    bot = PhysioBot()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CallbackQueryHandler(bot.handle_mode_selection, pattern='^mode_'))
    app.add_handler(CallbackQueryHandler(bot.handle_language_selection, pattern='^lang_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    app.add_error_handler(bot.error_handler)
    
    # Start bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("✅ BOT STARTED SUCCESSFULLY!")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
