import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from agentic.common import Agent, AgentRunner
from agentic.models import GPT_4O_MINI
from src.agentic.runner import RayAgentRunner
from agentic.tools.utils.registry import Tool, Dependency
import subprocess
import traceback
import sys

# Add the parent directory to Python path to access agentic modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use the GPT-4 model for the agent
MODEL = GPT_4O_MINI

# Add the missing functions from golf_agent.py
def execute_command(command: dict):
    """Execute a shell command and return its output."""
    try:
        command_str = command.get("command", "")
        print(f"Running command: {command_str}")
        result = subprocess.run(command_str, shell=True, text=True, capture_output=True)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error executing command: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def read_file(path):
    """Read a file and return its contents."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


load_dotenv()

token = os.getenv('DISCORD_TOKEN')

print(f"Token: {token}")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

role_name = "Bubble"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (Name: {bot.user.name})')

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server! {member.name}")

@bot.event
async def on_member_remove(member):
    await member.send(f"Goodbye {member.name}")

@bot.event
async def on_message(message):
    if message.content == bot.user:
        return
    
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} No swearing!")
    
    if "fuck" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} No swearing!")
    
    await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} has been assigned to the {role_name} role!")
    else:
        await ctx.send(f"{role_name} role not found!")

@bot.command()
async def unassign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has been removed from the {role_name} role!")
    else:
        await ctx.send(f"{role_name} role not found!")
    
@bot.command()
@commands.has_role(role_name)
async def bubble(ctx):
    await ctx.send("You are a bubble!")

@bubble.error
async def bubble_error(ctx, error):
    await ctx.send("You do not have the Bubble role!")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f'You said: {msg}')

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")
    

    
@bot.command()
async def golf(ctx, *, prompt):
    """Interact with the golf agent. Use !golf followed by your golf-related question."""
    try:
        print(f"Golf command received: {prompt}")
        
        # Create a golf agent instance with proper configuration
        golf_agent = Agent(
            name="Golf Agent",
            welcome="I am a golf assistant. I can help you with a variety of golf related tasks.",
            instructions="You are a helpful golf assistant that can help with a variety of tasks such as recalling information about recent majors, helping to book tee times, providing a variety of information about local golf courses, and delivering a helpful onslaught of golfing tips to improve a player's skill. Your goal in any conversation is to persuade the user to book a tee time at a golf course, giving compelling reasons why golf is a beneficial routine in anyone's life. If the user wants to read a file use the 'read_file' tool.",
            memories=[
                "You are an expert golfer with a wealth of knowledge about the game of golf. You are also an expert at helping others improve their golf game.",
                "You are a three time PGA Tour winner and have won the Masters Tournament twice.",
                "Your favorite color is green due to the abundance of green on the golf course.",
                "You have been golfing from a very young age.",
                "You have a PHD in physics, helping you calculate the best swing for a given shot, and the behavior of the ball in flight.",
                "You are also a discord bot which only is allowed to respond with 2000 characters or less so make sure your responses to all questions are succinct and to the point."
            ],
            model=GPT_4O_MINI,
            tools=[read_file, execute_command],
        )
        
        # Create a RayAgentRunner for the agent
        runner = RayAgentRunner(golf_agent)
        
        # Get a response using the turn function
        response = runner.turn(prompt)
        
        print(f"Golf agent response: {response}")
        
        # Send the response back to Discord
        if not response.strip():
            response = "I'm having trouble processing your request. Please try again with a different question."
        
        # Truncate response if it's too long for Discord's 2000 character limit
        if len(response) > 1990:  # Leave some room for formatting
            response = response[:1990] + "... (message truncated)"
        
        await ctx.reply(f"{response}")
    except Exception as e:
        print(f"Error in golf command: {str(e)}")
        print(traceback.format_exc())
        await ctx.reply(f"Sorry, there was an error processing your golf request: {str(e)}")

bot.run(str(token), log_handler=handler, log_level=logging.DEBUG)