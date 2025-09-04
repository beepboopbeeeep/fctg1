#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shazam Telegram Bot
A Telegram bot that can identify music using ShazamIO library
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultAudio,
    InputFile,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
    ConversationHandler,
    CommandHandler
)
from telegram.constants import ParseMode

from shazamio import Shazam, Serialize

# Configuration - All variables defined directly in code
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your actual bot token
ADMIN_USER_ID = None  # Replace with your admin user ID if needed

# Language translations
TRANSLATIONS = {
    'fa': {
        'welcome': """🎵 **به ربات شناسایی موسیقی خوش آمدید!**

این ربات با استفاده از ShazamIO می‌تواند موسیقی را از فایل‌های صوتی شناسایی کند.

**قابلیت‌های ربات:**
🔍 شناسایی آهنگ از فایل صوتی
🌐 جستجوی آهنگ در گروه‌ها (inline mode)
✏️ ویرایش اطلاعات آهنگ
🎼 دریافت اطلاعات کامل آهنگ
👨‍🎤 دریافت اطلاعات هنرمند
🎶 پیدا کردن آهنگ‌های مشابه
📊 مشاهده آمار شنوندگان

برای شروع، زبان خود را انتخاب کنید:""",
        'select_language': 'لطفاً زبان خود را انتخاب کنید:',
        'language_selected': '✅ زبان با موفقیت تنظیم شد!',
        'send_audio': 'لطفاً یک فایل صوتی ارسال کنید تا آهنگ را شناسایی کنم.',
        'processing': '⏳ در حال پردازش فایل...',
        'song_not_found': '❌ متأسفانه نتوانستم آهنگ را شناسایی کنم. لطفاً فایل دیگری را امتحان کنید.',
        'song_found': '🎵 **آهنگ شناسایی شد!**\n\n',
        'title': 'عنوان: ',
        'artist': 'هنرمند: ',
        'album': 'آلبوم: ',
        'year': 'سال: ',
        'genre': 'ژانر: ',
        'duration': 'مدت: ',
        'listen_count': 'تعداد شنوندگان: ',
        'edit_info': '✏️ ویرایش اطلاعات آهنگ',
        'edit_title': 'عنوان جدید را وارد کنید:',
        'edit_artist': 'نام هنرمند جدید را وارد کنید:',
        'edit_album': 'نام آلبوم جدید را وارد کنید:',
        'edit_year': 'سال انتشار جدید را وارد کنید:',
        'edit_genre': 'ژانر جدید را وارد کنید:',
        'info_updated': '✅ اطلاعات با موفقیت به‌روزرسانی شد!',
        'cancel': '❌ لغو',
        'back': '🔙 بازگشت',
        'search_inline': 'برای جستجوی آهنگ در گروه‌ها، از @{} استفاده کنید.',
        'no_results': '❌ نتیجه‌ای یافت نشد.',
        'error': '❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.',
        'main_menu': '🏠 منوی اصلی',
        'help': """📖 **راهنمای استفاده:**

/start - شروع ربات
/language - تغییر زبان
/help - نمایش این راهنما

**نحوه استفاده:**
1. یک فایل صوتی ارسال کنید تا آهنگ شناسایی شود
2. در گروه‌ها از @{} برای جستجوی آهنگ استفاده کنید
3. پس از شناسایی آهنگ، می‌توانید اطلاعات آن را ویرایش کنید"""
    },
    'en': {
        'welcome': """🎵 **Welcome to Music Recognition Bot!**

This bot can identify music from audio files using ShazamIO.

**Bot Features:**
🔍 Identify songs from audio files
🌐 Search songs in groups (inline mode)
✏️ Edit song information
🎼 Get complete song information
👨‍🎤 Get artist information
🎶 Find similar songs
📊 View listener statistics

To get started, please select your language:""",
        'select_language': 'Please select your language:',
        'language_selected': '✅ Language set successfully!',
        'send_audio': 'Please send an audio file so I can identify the song.',
        'processing': '⏳ Processing file...',
        'song_not_found': '❌ Sorry, I couldn\'t identify the song. Please try another file.',
        'song_found': '🎵 **Song Identified!**\n\n',
        'title': 'Title: ',
        'artist': 'Artist: ',
        'album': 'Album: ',
        'year': 'Year: ',
        'genre': 'Genre: ',
        'duration': 'Duration: ',
        'listen_count': 'Listen Count: ',
        'edit_info': '✏️ Edit Song Info',
        'edit_title': 'Enter new title:',
        'edit_artist': 'Enter new artist name:',
        'edit_album': 'Enter new album name:',
        'edit_year': 'Enter new release year:',
        'edit_genre': 'Enter new genre:',
        'info_updated': '✅ Information updated successfully!',
        'cancel': '❌ Cancel',
        'back': '🔙 Back',
        'search_inline': 'Use @{} to search for songs in groups.',
        'no_results': '❌ No results found.',
        'error': '❌ An error occurred. Please try again.',
        'main_menu': '🏠 Main Menu',
        'help': """📖 **Usage Guide:**

/start - Start the bot
/language - Change language
/help - Show this guide

**How to use:**
1. Send an audio file to identify the song
2. Use @{} in groups to search for songs
3. After song identification, you can edit its information"""
    }
}

# Conversation states for editing
EDIT_TITLE, EDIT_ARTIST, EDIT_ALBUM, EDIT_YEAR, EDIT_GENRE = range(5)

# User data storage
user_languages = {}
user_sessions = {}

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    return user_languages.get(user_id, 'en')

def get_text(user_id: int, key: str) -> str:
    """Get translated text for user"""
    lang = get_user_language(user_id)
    return TRANSLATIONS[lang].get(key, key)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    text = get_text(user_id, 'welcome')
    
    # Create language selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang_fa'),
            InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    user_id = update.effective_user.id
    bot = context.bot
    text = get_text(user_id, 'help').format(bot.username)
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language command"""
    user_id = update.effective_user.id
    text = get_text(user_id, 'select_language')
    
    keyboard = [
        [
            InlineKeyboardButton("🇮🇷 فارسی", callback_data='lang_fa'),
            InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang_code = query.data.split('_')[1]
    
    user_languages[user_id] = lang_code
    text = get_text(user_id, 'language_selected')
    
    # Create main menu keyboard
    keyboard = [
        [get_text(user_id, 'main_menu')],
        [get_text(user_id, 'help')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle audio file messages"""
    user_id = update.effective_user.id
    processing_text = get_text(user_id, 'processing')
    
    # Send processing message
    processing_msg = await update.message.reply_text(processing_text)
    
    try:
        # Download audio file
        audio_file = await update.message.audio.get_file()
        audio_data = await audio_file.download_as_bytearray()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        # Initialize Shazam
        shazam = Shazam()
        
        # Recognize song
        result = await shazam.recognize(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if result and result.get('track'):
            track = result['track']
            
            # Format song information
            song_info = get_text(user_id, 'song_found')
            song_info += f"{get_text(user_id, 'title')}{track.get('title', 'N/A')}\n"
            song_info += f"{get_text(user_id, 'artist')}{track.get('subtitle', 'N/A')}\n"
            
            if track.get('sections'):
                for section in track['sections']:
                    if section.get('type') == 'SONG' and section.get('metadata'):
                        metadata = section['metadata']
                        song_info += f"{get_text(user_id, 'album')}{metadata.get('album', 'N/A')}\n"
                        song_info += f"{get_text(user_id, 'year')}{metadata.get('year', 'N/A')}\n"
                        song_info += f"{get_text(user_id, 'genre')}{metadata.get('genre', 'N/A')}\n"
            
            # Create edit button
            keyboard = [
                [InlineKeyboardButton(get_text(user_id, 'edit_info'), callback_data='edit_song')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store song data for editing
            user_sessions[user_id] = {
                'track_data': track,
                'file_id': update.message.audio.file_id
            }
            
            await processing_msg.delete()
            await update.message.reply_text(song_info, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            error_text = get_text(user_id, 'song_not_found')
            await processing_msg.delete()
            await update.message.reply_text(error_text)
    
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        error_text = get_text(user_id, 'error')
        await processing_msg.delete()
        await update.message.reply_text(error_text)

async def edit_song_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle edit song callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    
    if not session:
        await query.edit_message_text(get_text(user_id, 'error'))
        return
    
    # Create edit options keyboard
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'title'), callback_data='edit_title')],
        [InlineKeyboardButton(get_text(user_id, 'artist'), callback_data='edit_artist')],
        [InlineKeyboardButton(get_text(user_id, 'album'), callback_data='edit_album')],
        [InlineKeyboardButton(get_text(user_id, 'year'), callback_data='edit_year')],
        [InlineKeyboardButton(get_text(user_id, 'genre'), callback_data='edit_genre')],
        [InlineKeyboardButton(get_text(user_id, 'cancel'), callback_data='edit_cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("✏️ " + get_text(user_id, 'edit_info'), reply_markup=reply_markup)

async def edit_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle edit field callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    field = query.data.split('_')[1]
    
    if field == 'cancel':
        await query.edit_message_text(get_text(user_id, 'cancel'))
        return
    
    # Store the field being edited
    context.user_data['edit_field'] = field
    
    prompt_text = get_text(user_id, f'edit_{field}')
    await query.edit_message_text(prompt_text)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages for editing"""
    user_id = update.effective_user.id
    text = update.message.text
    edit_field = context.user_data.get('edit_field')
    
    if edit_field:
        # Update the field
        session = user_sessions.get(user_id)
        if session:
            track_data = session['track_data']
            
            # Update the appropriate field
            if edit_field == 'title':
                track_data['title'] = text
            elif edit_field == 'artist':
                track_data['subtitle'] = text
            elif edit_field in ['album', 'year', 'genre']:
                if 'sections' not in track_data:
                    track_data['sections'] = []
                
                # Find or create metadata section
                metadata_section = None
                for section in track_data['sections']:
                    if section.get('type') == 'SONG':
                        metadata_section = section
                        break
                
                if not metadata_section:
                    metadata_section = {'type': 'SONG', 'metadata': {}}
                    track_data['sections'].append(metadata_section)
                
                if 'metadata' not in metadata_section:
                    metadata_section['metadata'] = {}
                
                metadata_section['metadata'][edit_field] = text
            
            # Clear edit field
            context.user_data['edit_field'] = None
            
            # Show updated information
            updated_text = get_text(user_id, 'song_found')
            updated_text += f"{get_text(user_id, 'title')}{track_data.get('title', 'N/A')}\n"
            updated_text += f"{get_text(user_id, 'artist')}{track_data.get('subtitle', 'N/A')}\n"
            
            if track_data.get('sections'):
                for section in track_data['sections']:
                    if section.get('type') == 'SONG' and section.get('metadata'):
                        metadata = section['metadata']
                        updated_text += f"{get_text(user_id, 'album')}{metadata.get('album', 'N/A')}\n"
                        updated_text += f"{get_text(user_id, 'year')}{metadata.get('year', 'N/A')}\n"
                        updated_text += f"{get_text(user_id, 'genre')}{metadata.get('genre', 'N/A')}\n"
            
            updated_text += f"\n{get_text(user_id, 'info_updated')}"
            
            await update.message.reply_text(updated_text, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(get_text(user_id, 'error'))
    else:
        # Handle other text messages
        if text == get_text(user_id, 'main_menu'):
            await start_command(update, context)
        elif text == get_text(user_id, 'help'):
            await help_command(update, context)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries"""
    query = update.inline_query
    if not query:
        return
    
    user_id = query.from_user.id
    search_query = query.query.strip()
    
    if not search_query:
        return
    
    try:
        # Initialize Shazam
        shazam = Shazam()
        
        # Search for tracks
        results = await shazam.search_track(query=search_query, limit=10)
        
        inline_results = []
        
        if results and results.get('tracks', {}).get('hits'):
            for hit in results['tracks']['hits'][:5]:  # Limit to 5 results
                track = hit['track']
                
                # Create inline result
                result = InlineQueryResultAudio(
                    id=str(track.get('key', '')),
                    audio_url=track.get('hub', {}).get('actions', [{}])[0].get('uri', ''),
                    title=track.get('title', 'Unknown'),
                    performer=track.get('subtitle', 'Unknown Artist'),
                    caption=f"🎵 {track.get('title', 'Unknown')} - {track.get('subtitle', 'Unknown Artist')}"
                )
                inline_results.append(result)
        
        if inline_results:
            await query.answer(inline_results, cache_time=300)
        else:
            no_results_text = get_text(user_id, 'no_results')
            await query.answer([], cache_time=300)
    
    except Exception as e:
        logger.error(f"Error in inline query: {e}")
        await query.answer([], cache_time=300)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        user_id = update.effective_user.id
        error_text = get_text(user_id, 'error')
        await update.effective_message.reply_text(error_text)

def main() -> None:
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(edit_song_callback, pattern='^edit_song$'))
    application.add_handler(CallbackQueryHandler(edit_field_callback, pattern='^edit_(title|artist|album|year|genre|cancel)$'))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Add inline query handler
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Set bot commands
    async def set_commands():
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
            BotCommand("language", "Change language")
        ]
        await application.bot.set_my_commands(commands)
    
    application.job_queue.run_once(lambda context: asyncio.create_task(set_commands()), 1)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()