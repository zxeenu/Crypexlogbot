from pyrogram import Client, filters
import logging
import os

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# Access environment variables
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')

app = Client(
    "my_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

@app.on_message(filters.text & filters.private)
async def echo(client, message):
    print('Received message:', message.text)
    print('From user:', message.from_user.id)
    await message.reply(message.text)
    print('Reply sent')

@app.on_message()
async def handle_message(client, message):
    await message.reply_text("Hello, I received your message!")


logging.info("Bot started")
logging.info(f"api id: {api_id}")

app.run() 

