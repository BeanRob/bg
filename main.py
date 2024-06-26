# pip install discord
# pip install py-cord

import os
import time
import asyncio
import threading
import datetime
import discord
from   discord     import Option
from   discord.ext import commands
from   config      import token

print("Checking for birthdays directory...")
try:
    os.mkdir("./birthdays")
    print("Directory did not exist, so has been made.")
except FileExistsError:
    print("Directory exists.")

print("Checking for settings directory...")
try:
    os.mkdir("./settings")
    print("Directory did not exist, so has been made.")
except FileExistsError:
    print("Directory exists.")

# Instantiate bot
bot = discord.Bot()

# Checks whether user of a command is an operator (can manage the server)
def isOperator(ctx):
    return ctx.author.guild_permissions.manage_guild


# Function to return whether current year is a leap year
def isleap():
    now = datetime.date.today()
    return now.year % 4 == 0


# Function to return whether given user has registered their birthday in given
# guild
def registered(guild, user):
    print(f"Checking if {user} in {guild} is registerd.")
    lines = []
    try:
        with open("./birthdays/" + str(guild) + ".txt", "r") as file:
            lines = file.readlines()
        print(lines)
        for line in lines:
            print(line)
            if str(user) in line:
                print("Registered here!")
                return True
    except FileNotFoundError:
        return False
    return False

# Changes list of string IDs into list of int IDs
def numberify(list):
    for i in range(0, len(list)):
        list[i] = int(list[i].strip())
    return list

# Check for any birthdays
async def checkbirth():
    for guild in os.listdir("./birthdays/"):
        guild = int(guild.split('.')[0])
        await checkguild(guild)

async def checkguild(guild):
    print(f"Checking guild with ID {guild}")
    with open(f"./settings/{guild}.txt", 'r') as file:
        settings = numberify(file.readlines())
    print(f"Settings for guild with ID {guild} are: {settings}")
    if settings != []:
        channel = settings[0]
        role    = settings[1]
        lines   = []
        with open(f"./birthdays/{guild}.txt", 'r') as file:
            lines = file.readlines()
        print(f"Birthdays: {lines}")
        now = datetime.date.today()
        for line in lines:
            split = numberify(line.split(" "))
            try:
                if now.day == split[1] and now.month == split[2]:
                    print(f"Birthday detected for user {split[0]}")
                    await birthday(guild, role, channel, split[0])
                elif not isleap() and split[1] == 29 and now.day == 29 and now.month == 2:
                    print(f"Birthday detected for user {split[0]} (normally 29/2, but this is not a leap year)")
                    await birthday(guild, role, channel, split[0])
                else:
                    await unbirthday(guild, role, channel, split[0])
            except discord.errors.NotFound:
                print("Oops! Unknown person!")

async def birthday(guild_id, role_id, channel_id, user_id):
    guild   = bot.get_guild(guild_id)
    role    = guild.get_role(role_id)
    channel = bot.get_channel(channel_id)
    user    = await guild.fetch_member(user_id)
    await user.add_roles(role)
    await channel.send(f"@everyone Today {user.mention} is the birthday ghoul. Wish them a happy birthday!")


async def unbirthday(guild_id, role_id, channel_id, user_id):
    guild   = bot.get_guild(guild_id)
    role    = guild.get_role(role_id)
    user    = await guild.fetch_member(user_id)
    print(f"deleting birthday status from {user.name}")
    try:
        await user.remove_roles(role)
    except discord.errors.Forbidden:
        print(f"Tried to remove birthday priveleges from {user.name}, but failed. Might someone else do it, pretty please?")

# When the bot is ready:
@bot.event
async def on_ready():
    print("real")
    try:
        # Sync all the slash commands
        await bot.sync_commands()
        print("synced")
    except Exception as e:
        print(e)
    await wrapper()

# When joining a new guild:
@bot.event
async def on_guild_join(guild):
    # Make birthdays file
    with open("./birthdays/" + str(guild.id) + ".txt", "w") as file:
        file.write("")
    # Make settings file
    with open("./settings/" + str(guild.id) + ".txt", "w") as file:
        file.write("")
    print("New files created for guild with ID " + str(guild.id))

# When leaving a guild:
@bot.event
async def on_guild_remove(guild):
    # Delete birthdays file
    os.remove("birthdays/" + str(guild.id) + ".txt")
    # Delete settings file
    os.remove("settings/" + str(guild.id) + ".txt")
    print("Files deleted for guild with ID " + str(guild.id))

# Add birthday command
@bot.command(name="addbirth", description="add your birthday")
async def addbirth(ctx,
            day: Option(int, "birth day"),
            month: Option(int, "birth month")
):
    try:
        days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if month < 1 or month > 12:
            raise ValueError("month not within range")
        if day < 1 or day > days[month - 1]:
            raise ValueError("day not within range")
        if registered(ctx.guild.id, ctx.author.id):
            raise AttributeError("already registered")
        try:
            with open("./birthdays/" + str(ctx.guild.id) + ".txt", "a") as file:
                file.write(f"{ctx.author.id} {day} {month}\n")
        except FileNotFoundError:
            with open("./birthdays/" + str(ctx.guild.id) + ".txt", "w") as file:
                file.write(f"{ctx.author.id} {day} {month}\n")

        if day == 29 and month == 2:
            await ctx.respond(f"{ctx.author.mention}, your birthday has been recorded as {day}/{month}. *On non-leap years, your birthday will be treated as 28/02.*", ephemeral=True)
        else:
            await ctx.respond(f"{ctx.author.mention}, your birthday has been recorded as {day}/{month}.", ephemeral=True)

    except ValueError:
        await ctx.respond("**Error:** Day and month should be valid numbers.", ephemeral=True)
    except AttributeError:
        await ctx.respond("**Error:** You already have a birthday registered.", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"**Fatal Error:** {e}", ephemeral=True)



@bot.command(name="init", description="set the bot up")
async def init(ctx,
            channel: Option(
                discord.TextChannel,
                "Enter the birthday channel:",
                required = True
            ),
            role: Option(
                discord.Role,
                "Enter the birthday role:",
                required = True
            )
):
    if isOperator(ctx):
        try:
            with open(dir + "/settings/" + str(ctx.guild.id) + ".txt", "w") as file:
                file.write(f"{channel.id}\n{role.id}")
            await ctx.respond("Setup success.", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"**Error:** Setup failure. Reason:\n{e}", ephemeral=True)
    else:
        await ctx.respond("**Error:** To set the bot up, you must be able to manage the server.", ephemeral=True)

@bot.command(name="list", description="list all birthdays")
async def list(ctx):
    guild = ctx.guild
    with open(f"./birthdays/{guild.id}.txt", 'r') as file:
        lines = file.readlines()
    output = "# All registered birthdays:\n"
    for line in lines:
        split = line.split()
        try:
            user = await guild.fetch_member(split[0])
            date = split[1] + "/" + split[2]
            output = output + f"{user.mention} - {date}\n"
        except discord.errors.NotFound:
            print("Whoops, unknown person")
    await ctx.respond(output, ephemeral=True)

@bot.command(name="check", description="force check for birthdays")
async def check(ctx):
    if isOperator(ctx):
        await ctx.respond("Checking for birthdays...", ephemeral=True)
        await checkguild(ctx.guild.id)
    else:
        await ctx.respond("**Error:** To force check for birthdays, you must be able to manage the server.", ephemeral=True)

async def run_at(time, coro):
    now = datetime.datetime.now()
    delay = ((time - now) % datetime.timedelta(days=1)).total_seconds()
    await asyncio.sleep(delay)
    return await coro

async def wrapper():
    time = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
    while True:
        await run_at(time, checkbirth())
    
def main():
    bot.run(token)

if __name__ == "__main__":
    main()
