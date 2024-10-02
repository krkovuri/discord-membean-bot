from dotenv import load_dotenv
import os
import discord

load_dotenv()

token = str(os.getenv("TOKEN"))
# print(token)
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")


bot.run(os.getenv("TOKEN"))  # run the bot with the token
