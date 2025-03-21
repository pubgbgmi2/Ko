import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary data storage (stores user balances and referrals)
users = {}

# Constants
DAILY_BONUS = 2
REFERRAL_BONUS = 5
WITHDRAWAL_THRESHOLD = 50

# Start command
async def start(update: Update, context):
    user_id = update.message.from_user.id
    referrer_id = context.args[0] if context.args else None

    # Register user if not already in the system
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "received_bonus": False}

        # Check if referred by someone
        if referrer_id and referrer_id.isdigit():
            referrer_id = int(referrer_id)
            if referrer_id in users:
                users[referrer_id]["balance"] += REFERRAL_BONUS
                users[referrer_id]["referrals"] += 1
                await context.bot.send_message(referrer_id, f"🎉 You earned ₹{REFERRAL_BONUS} for referring a new user!")

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("🔗 My Referral Link", callback_data="referral")],
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("💵 Withdraw Money", callback_data="withdraw")],
        [InlineKeyboardButton("📖 How to Earn?", callback_data="earnings_info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Welcome! Earn ₹5 per referral and claim ₹2 daily bonus.\nClick below to explore!",
        reply_markup=reply_markup
    )

# Handle button clicks
async def button_handler(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "received_bonus": False}

    # Check balance
    if query.data == "balance":
        balance = users[user_id]["balance"]
        await query.answer()
        await query.message.edit_text(f"💰 Your balance: ₹{balance}")

    # Provide referral link
    elif query.data == "referral":
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.answer()
        await query.message.edit_text(f"🔗 Your referral link: {ref_link}\nShare this to earn ₹{REFERRAL_BONUS} per referral!")

    # Claim daily bonus
    elif query.data == "daily_bonus":
        if not users[user_id]["received_bonus"]:
            users[user_id]["balance"] += DAILY_BONUS
            users[user_id]["received_bonus"] = True
            await query.answer()
            await query.message.edit_text(f"🎁 You claimed ₹{DAILY_BONUS} daily bonus! Your balance: ₹{users[user_id]['balance']}")
        else:
            await query.answer("❌ You have already claimed today's bonus.", show_alert=True)

    # Withdraw money
    elif query.data == "withdraw":
        if users[user_id]["balance"] >= WITHDRAWAL_THRESHOLD:
            users[user_id]["balance"] -= WITHDRAWAL_THRESHOLD
            await query.answer()
            await query.message.edit_text("✅ Withdrawal request sent! You will receive ₹50 soon.")
        else:
            await query.answer("❌ You need at least ₹50 to withdraw.", show_alert=True)

    # Explain earning methods
    elif query.data == "earnings_info":
        await query.answer()
        await query.message.edit_text(
            "📖 How to Earn:\n"
            "1️⃣ Invite friends using your referral link (₹5 per referral)\n"
            "2️⃣ Claim ₹2 daily bonus\n"
            "3️⃣ Withdraw money once you reach ₹50\n"
            "🚀 Start referring now!"
        )

# Reset daily bonus eligibility (run this once a day)
async def reset_daily_bonus(context):
    for user_id in users:
        users[user_id]["received_bonus"] = False

# Error handler
async def error_handler(update: Update, context):
    logger.warning(f"Update {update} caused error {context.error}")

# Main function
def main():
    BOT_TOKEN = "7806976016:AAGtAinH2HRIbHuk2QdS1H7w6yscNCeIomg"

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)

    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import asyncio

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = "7806976016:AAGtAinH2HRIbHuk2QdS1H7w6yscNCeIomg"
CHANNEL_USERNAME = "https://t.me/+Tn8USVhdIhphY2Nl"  # Extracted from your provided channel link
CHANNEL_LINK = f"https://t.me/+{CHANNEL_USERNAME}"

# Temporary storage for user data
users = {}

# Constants
DAILY_BONUS = 2
REFERRAL_BONUS = 5
WITHDRAWAL_THRESHOLD = 50

# Check if user has joined the channel
async def is_user_member(user_id, context):
    try:
        chat_member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking user membership: {e}")
        return False

# Start Command
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    referrer_id = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "received_bonus": False}

        # Handle referrals
        if referrer_id and referrer_id.isdigit():
            referrer_id = int(referrer_id)
            if referrer_id in users:
                users[referrer_id]["balance"] += REFERRAL_BONUS
                users[referrer_id]["referrals"] += 1
                await context.bot.send_message(referrer_id, f"🎉 You earned ₹{REFERRAL_BONUS} for referring a new user!")

    # Check if user has joined the channel
    if not await is_user_member(user_id, context):
        join_button = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]]
        await update.message.reply_text(
            "🚨 To use this bot, you must join our official channel!",
            reply_markup=InlineKeyboardMarkup(join_button)
        )
        return

    # Send main menu
    await show_main_menu(update, context)

# Main Menu
async def show_main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
         InlineKeyboardButton("🔗 Referral Info", callback_data="referral")],
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="daily_bonus"),
         InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("📖 How to Earn?", callback_data="earnings_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(
            "🏠 Main Menu:\nEarn ₹5 per referral and ₹2 daily bonus!",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "🏠 Welcome! Earn ₹5 per referral and ₹2 daily bonus.\nChoose an option below:",
            reply_markup=reply_markup
        )

# Callback Handler
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "received_bonus": False}

    # Ensure user is a channel member
    if not await is_user_member(user_id, context):
        join_button = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]]
        await query.message.edit_text(
            "🚨 You must join our official channel to access this bot!",
            reply_markup=InlineKeyboardMarkup(join_button)
        )
        return

    # Handle different actions
    if query.data == "balance":
        balance = users[user_id]["balance"]
        await query.message.edit_text(f"💰 Your balance: ₹{balance}", reply_markup=back_button())

    elif query.data == "referral":
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        referral_count = users[user_id]["referrals"]
        await query.message.edit_text(
            f"🔗 Your referral link:\n{ref_link}\n\n👥 Referrals: {referral_count}\n\nEarn ₹{REFERRAL_BONUS} per referral!",
            reply_markup=back_button()
        )

    elif query.data == "daily_bonus":
        if not users[user_id]["received_bonus"]:
            users[user_id]["balance"] += DAILY_BONUS
            users[user_id]["received_bonus"] = True
            await query.message.edit_text(f"🎁 You claimed ₹{DAILY_BONUS} daily bonus!\n💰 Balance: ₹{users[user_id]['balance']}", reply_markup=back_button())
        else:
            await query.answer("❌ You have already claimed today's bonus.", show_alert=True)

    elif query.data == "withdraw":
        if users[user_id]["balance"] >= WITHDRAWAL_THRESHOLD:
            users[user_id]["balance"] -= WITHDRAWAL_THRESHOLD
            await query.message.edit_text("✅ Withdrawal request sent!\nYou will receive ₹50 soon.", reply_markup=back_button())
        else:
            await query.answer("❌ You need at least ₹50 to withdraw.", show_alert=True)

    elif query.data == "earnings_info":
        await query.message.edit_text(
            "📖 How to Earn:\n"
            "1️⃣ Invite friends using your referral link (₹5 per referral)\n"
            "2️⃣ Claim ₹2 daily bonus\n"
            "3️⃣ Withdraw money once you reach ₹50\n"
            "🚀 Start referring now!",
            reply_markup=back_button()
        )

    elif query.data == "back":
        await show_main_menu(update, context)

# Generate Back Button
def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])

# Reset daily bonus eligibility
async def reset_daily_bonus(context: CallbackContext):
    for user_id in users:
        users[user_id]["received_bonus"] = False

# Error Handler
async def error_handler(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

# Main Function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)

    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()