import os
import discord
# from discord import Option
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True  # Enable the members intent
bot = discord.Bot(intents=intents)

# Reset data.json file (temporary)
# with open('data.json', 'w') as f:
#     json.dump({"users": {}}, f)

# Load the data from data.json at the start
with open('data.json', 'r') as f:
    data = json.load(f)


# Function to save data to JSON
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def initialize_user(user_id):
    if user_id not in data["users"]:
        data["users"][user_id] = {"membean_minutes": 15, "reminders": {}}


days_of_week = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']


@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")
    check_reminders.start()


@bot.slash_command(name='display_reminders', description='Display your Membean reminders')
async def display_reminders(ctx: discord.ApplicationContext):
    user_id = str(ctx.author.id)

    if user_id not in data["users"] or not data["users"][user_id]["reminders"]:
        await ctx.respond(f"{ctx.author.mention}, you don't have any Membean reminders set.")
    else:
        reminders = [f"{day}: {time}" for day,
                     time in data["users"][user_id]['reminders'].items()]
        await ctx.respond(f"{ctx.author.mention}, your current reminders are:\n" + "\n".join(reminders))


@bot.slash_command(name='set_reminder', description="Set a time for when you'll receive a reminder")
async def set_reminder(
    ctx: discord.ApplicationContext,
    # Description for time
    time: str,
    # Description for day
    day: str
):
    day = day.capitalize()
    user_id = str(ctx.author.id)

    initialize_user(user_id)

    # Check if the provided day is valid
    if day not in days_of_week:
        await ctx.respond(f"{ctx.author.mention}, please enter a valid day of the week.")
        return

    try:
        # Example format: '7:00PM'
        time_obj = datetime.strptime(time, '%I:%M%p')
        if day in data['users'][user_id]['reminders'] and data['users'][user_id]['reminders'][day] == time_obj.strftime('%I:%M %p'):
            await ctx.respond(f"{ctx.author.mention}, you already set a reminder at that time on {day}.")
            return

        data["users"][user_id]['reminders'][day] = time_obj.strftime(
            '%I:%M %p')
    except ValueError:
        await ctx.respond(f"{ctx.author.mention}, please enter a valid time in HH:MMAM/PM format, such as 7:00PM.")
        return

    # Save the updated data
    save_data()

    await ctx.respond(f"{ctx.author.mention}, you've set a reminder for Membean at {time} on {day}s.")


@bot.slash_command(name="help", description="List all available commands and their descriptions")
async def help_command(ctx: discord.ApplicationContext):
    help_message = (
        "**Here are the available commands:**\n"
        "/help - Show this help message.\n"
        "/set_reminder [time] [day] - Set a reminder for Membean.\n"
        "/display_reminders - Display your current Membean reminders."
    )
    await ctx.respond(help_message)


@tasks.loop(minutes=1)
async def check_reminders():
    current_time = datetime.now().strftime("%I:%M %p")
    for user_id, user_data in data['users'].items():
        minutes = user_data["membean_minutes"]
        reminders = user_data["reminders"]

        for day, time in reminders.items():
            if day == datetime.now().strftime("%A") and time == current_time:
                user = bot.get_user(int(user_id))
                if user:
                    await user.send(f"Hey {user.mention}, it's time to do your {minutes}-minute Membean session!")

bot.run(TOKEN)
