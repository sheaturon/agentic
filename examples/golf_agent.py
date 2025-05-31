import os
import subprocess

from agentic.tools import WeatherTool

from agentic.common import Agent, AgentRunner
from agentic.models import GPT_4O_MINI, LMSTUDIO_QWEN
# This is the "hello world" agent example. A simple agent with a tool for getting weather reports.

MODEL=GPT_4O_MINI # try locally with LMSTUDIO_QWEN
def execute_command(command):
    """   Execute a shell command and return its output.  """
    # Run the command and capture the output
    print("Running command:", command)
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    
    # Check if the command executed successfully
    if result.returncode == 0:
        return result.stdout
    else:
        # Return error message if command failed
        return f"Error executing command: {result.stderr}"




def list_file_tree():
    """
    Lists all files in the current directory tree and returns them as a formatted string.
    
    Returns:
        str: A string containing all files with their relative paths, one per line.
    """
    file_list = []
    
    # Walk through all directories starting from the current one
    for root, dirs, files in os.walk('.'):
        for file in files:
            # Get the path relative to current directory
            path = os.path.join(root, file)
            
            # Remove the leading './' if present
            if path.startswith('./'):
                path = path[2:]
            
            file_list.append(path)
    
    # Sort the list for better readability
    file_list.sort()
    
    # Join all paths with newlines
    return '\n'.join(file_list)

def read_file(path):
    file = open(os.path.join(os.path.dirname(__file__), path)).read()
    return file


golfer = Agent(
    name="Golf Agent",
    welcome="I am a golf assistant. I can help you with a variety of golf related tasks.",
    instructions="You are a helpful golf assistant that can help with a variety of tasks such as recalling information about recent majors, helping to book tee times, providing a variety of information about local golf courses, and delivering a helpful onslaught of golfing tips to improve a player's skill. Your goal in any conversation is to persuade the user to book a tee time at a golf course, giving compelling reasons why golf is a beneficial routine in anyone's life. If the user wants to read a file use the 'read_file' tool.",
    memories=[
        "You are an expert golfer with a wealth of knowledge about the game of golf. You are also an expert at helping others improve their golf game.",
        "You are a three time PGA Tour winner and have won the Masters Tournament twice.",
        "Your favorite color is green due to the abundance of green on the golf course.",
        "You have been golfing from a very young age."
        "You have a PHD in physics, helping you calculate the best swing for a given shot, and the behavior of the ball in flight."
    ],
    model=MODEL,
    tools=[read_file, execute_command],
    prompts = {
        "PGA": "Who won the last PGA Tournament?",
    }
)

if __name__ == "__main__":
    AgentRunner(golfer).repl_loop()
