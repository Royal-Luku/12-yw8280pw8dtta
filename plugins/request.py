import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize your Pyrogram client
app = Client("my_bot")

# Define your list of admin user IDs
ADMINS = [1782834874]  # Replace these with actual admin user IDs

# Define the channel ID where you want to log the requests
REQUEST_LOG_CHANNEL_ID = -1002087721784  # Replace with your channel ID

# Define your command and keyword filters
request_filters = filters.command("request")

# Define your message handler function
@app.on_message(request_filters & filters.group)
async def handle_request(bot, message):
    # Check if there's a reply to the message
    if message.reply_to_message:
        # Get the user ID and mention of the reporter
        reporter_id = message.from_user.id
        reporter_mention = message.from_user.mention
        
        # Get the text of the replied message
        replied_text = message.reply_to_message.text
        
        # Forward the message to each admin defined in ADMINS variable asynchronously
        async def forward_message(admin_id):
            try:
                await message.reply_to_message.forward(admin_id)
            except Exception as e:
                print(f"Failed to forward message to admin {admin_id}: {e}")
        
        await asyncio.gather(*[forward_message(admin_id) for admin_id in ADMINS])
        
        # Prepare the inline keyboard with one button
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Notify User", callback_data="notifyuser")
                ]
            ]
        )
        
        # Send the request information to the request log channel with the inline keyboard
        try:
            await bot.send_message(
                REQUEST_LOG_CHANNEL_ID, 
                f"Reporter: {reporter_mention} (ID: {reporter_id})\nMessage: {replied_text}",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Failed to send request log to channel: {e}")
        
        # Send a confirmation message to the user
        await message.reply_text("**✅ Movie request sent to bot admin(s) ✅**")

# Define your callback query handler function
@app.on_callback_query(filters.regex("notifyuser"))
async def notify_user(bot, query):
    # Get the message text from the request log
    message_text = query.message.text
    
    # Get the user ID from the message text
    user_id = int(message_text.split("(ID: ")[1].split(")")[0])
    
    # Get the movie name from the message text
    movie_name = message_text.split("Message: ")[1]
    
    # Send a message to the user mentioning the movie name
    try:
        await bot.send_message(user_id, f"The requested movie '{movie_name}' is now available!")
    except Exception as e:
        print(f"Failed to notify user: {e}")
    
    # Answer the callback query
    await query.answer("User has been notified!")
