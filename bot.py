import os
import logging
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# --- CONFIGURATION ---
# Get token from environment variables (Set this in Render dashboard later)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- FLASK KEEP-ALIVE SERVER ---
# Render requires a web service to bind to a port. 
# We run a tiny Flask app in the background to keep the bot running.
app = Flask('')

@app.route('/')
def home():
    return "TSLAx-SL Bot is Alive and Running!"

def run_http():
    # Render assigns a PORT env variable. Default to 8080 if not found.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    t = Thread(target=run_http)
    t.daemon = True
    t.start()

# --- BOT CONTENT ---
# Disclaimer text to append to financial messages (Compliance Requirement)
DISCLAIMER = "\n\n⚠️ <i>Disclaimer: This is not financial advice. Cryptocurrency markets are volatile. Do your own research (DYOR) before investing.</i>"

TEXT_CRYPTO = (
    "<b>What is Crypto?</b>\n\n"
    "Cryptocurrency is a digital or virtual currency secured by cryptography, which makes it nearly impossible to counterfeit or double-spend. "
    "Unlike traditional currencies issued by governments (fiat), crypto operates on decentralized networks."
)

TEXT_BLOCKCHAIN = (
    "<b>What is Blockchain?</b>\n\n"
    "Imagine a digital ledger that is duplicated and distributed across the entire network of computer systems on the blockchain. "
    "It records transactions in a way that makes it difficult or impossible to change, hack, or cheat the system. It is the foundation of trust for crypto."
)

TEXT_TSLAX = (
    "<b>🚀 Discover TSLAx-SL</b>\n\n"
    "TSLAx-SL is designed with a singular, ambitious vision: <b>To target a $10 Billion Market Cap in the next bull run.</b>\n\n"
    "We are building a community-driven ecosystem aiming to mirror the growth trajectory of giants like Bitcoin. "
    "This is your opportunity to learn about a project that strives to redefine limits.\n\n"
    "🔥 <i>Don't watch from the sidelines.</i>"
    + DISCLAIMER
)

# --- BOT LOGIC ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the welcome message with the 3 buttons."""
    keyboard = [
        [InlineKeyboardButton("💰 What is Crypto?", callback_data='explain_crypto')],
        [InlineKeyboardButton("🔗 What is Blockchain?", callback_data='explain_blockchain')],
        [InlineKeyboardButton("🚀 Discover TSLAx-SL", callback_data='explain_tslax')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "<b>Welcome to the Future of Finance!</b>\n\n"
        "I am here to educate you on the crypto world and introduce you to the next potential giant: <b>TSLAx-SL</b>.\n\n"
        "Tap a button below to begin:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks."""
    query = update.callback_query
    
    # Check for the specific "coming_soon" button click first
    if query.data == 'coming_soon':
        # Show a pop-up alert to the user
        await query.answer(text="The community channel is under construction. Stay tuned!", show_alert=True)
        return

    # For other buttons, stop the loading animation normally
    await query.answer()
    
    # Determine which button was pressed
    if query.data == 'explain_crypto':
        await query.message.reply_text(TEXT_CRYPTO, parse_mode=constants.ParseMode.HTML)
    elif query.data == 'explain_blockchain':
        await query.message.reply_text(TEXT_BLOCKCHAIN, parse_mode=constants.ParseMode.HTML)
    elif query.data == 'explain_tslax':
        # Changed: Button now triggers a 'coming_soon' callback instead of a URL
        join_btn = [[InlineKeyboardButton("Community Coming Soon 🚧", callback_data='coming_soon')]]
        await query.message.reply_text(
            TEXT_TSLAX, 
            parse_mode=constants.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(join_btn)
        )

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # 1. Start the Keep-Alive Web Server for Render
    start_keep_alive()
    
    # 2. Check for Token
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
    else:
        # 3. Setup Bot
        app_bot = ApplicationBuilder().token(TOKEN).build()
        
        # Add Handlers
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CallbackQueryHandler(button_handler))
        
        print("Bot is polling...")
        app_bot.run_polling()
