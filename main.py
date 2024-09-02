
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import asyncio

from tracker import controller

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')

MY_GUILD = discord.Object(id=1148739090049675306)
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all()) #gets all intents for the bot to work
jobs_found = set()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord! Version {discord.__version__}')
    run_jobs_loop.start()
    try:
        synced = await bot.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@bot.tree.command(guild=MY_GUILD, name = "hello")
async def hello(interaction):
    await interaction.response.send_message("Fuck you your inputs are wrong")

async def print_jobs(channel):
    global jobs_found
    all_job_ids, jobs_responses = controller(jobs_found)
    jobs_found.update(all_job_ids)

    for job_id, response in jobs_responses:
        await channel.send(f"{response}\nhttps://www.linkedin.com/jobs/view/{job_id}")

@tasks.loop(minutes=15)
async def run_jobs_loop():
    channel = bot.get_channel(1279745830659690598)
    asyncio.create_task(print_jobs(channel))

@bot.tree.command(guild=MY_GUILD, name = "run_jobs")
async def run_jobs(interaction):
    await interaction.response.send_message("generating response")
    asyncio.create_task(print_jobs(interaction.channel))

bot.run(discord_token)