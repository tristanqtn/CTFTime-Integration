import discord
import responses

async def send_message(message, user_message, is_private):
    """
    Send a message to the user or channel.
    
    Args:
        message (discord.Message): The message object.
        user_message (str): The message sent by the user.
        is_private (bool): Whether the response should be private or not.
    """
    
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f"Error: {e}")
        
        
def run_discord_bot(BOT_TOKEN):
    """
    Run the Discord bot.
    
    Args:
        BOT_TOKEN (str): The token for the Discord bot.
    """
    
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        print(f"{client.user} is now running.")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        print(f"Message from {username} in {channel}: {user_message}")
        
        if user_message.startswith("?"):
            await send_message(message, user_message[1:], True)
        else:
            await send_message(message, user_message, False)

    client.run(YOUR_BOT_TOKEN)