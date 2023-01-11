# Import Built-In Modules
import asyncio
import json
import os
import random
import sys
import threading
import time
from datetime import datetime
from logging import ERROR, basicConfig

# Import Third-Party Modules
from dotenv import load_dotenv

# Suppress Non-Critical Logging
if os.path.exists(".env") is False:
    print("The .env is missing, please create one from the template.")
    sys.exit()
load_dotenv()
SUPPRESS_LOGGING = os.getenv("SUPPRESS_LOGGING")
if SUPPRESS_LOGGING == "1":
    basicConfig(level=ERROR)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Finish Importing Third-Party Modules
import discord  # noqa: E402
import interactions  # noqa: E402
from textgenrnn import textgenrnn  # noqa: E402

# Load constants from .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_NAME = os.getenv("BOT_NAME")
MINIMUM_TEMPERATURE = os.getenv("MINIMUM_TEMPERATURE")
MAXIMUM_TEMPERATURE = os.getenv("MAXIMUM_TEMPERATURE")
MODEL_FILE_NAME = os.getenv("MODEL_FILE_NAME")
EMOJI_SERVER = os.getenv("EMOJI_SERVER")
EMOJI_NAME = os.getenv("EMOJI_NAME")
CHAT_COMMAND_NAME = os.getenv("CHAT_COMMAND_NAME")
CHAT_COMMAND_DESCRIPTION = os.getenv("CHAT_COMMAND_DESCRIPTION")
CHAT_COMMAND_TYPING_MESSAGE = os.getenv("CHAT_COMMAND_TYPING_MESSAGE")
PROMPT_COMMAND_NAME = os.getenv("PROMPT_COMMAND_NAME")
PROMPT_COMMAND_DESCRIPTION = os.getenv("PROMPT_COMMAND_DESCRIPTION")
PROMPT_COMMAND_TYPING_MESSAGE = os.getenv("PROMPT_COMMAND_TYPING_MESSAGE")
PROMPT_INPUT_DESCRIPTION = os.getenv("PROMPT_INPUT_DESCRIPTION")

# Print starting message
print("[Starting textgenrnn_discord_bot]")

# Create library client instances
discordpy_client = discord.Client()
interactions_client = interactions.Client(token=DISCORD_TOKEN)
http_client = interactions.api.http.HTTPClient(DISCORD_TOKEN)


async def generate_message(generation_prefix):
    """Generates a message using the textgenrnn model

    Allows for an optional prefix
    The prefix is used to start the returned message
    The message is formatted as "[Prefix][Generated Message]"
    The prefix affects the outcome of the generated message
    The model attempts to continue from the prefix

    :param: generation_prefix: an optional prefix used to prompt the model
    :return: the generated message, including the prefix
    """
    main_textgenrnn = textgenrnn(MODEL_FILE_NAME)
    # Determine the message's temperature
    random_temperature = random.uniform(
        float(MINIMUM_TEMPERATURE), float(MAXIMUM_TEMPERATURE)
    )
    raw_generation = main_textgenrnn.generate(
        1,
        temperature=random_temperature,
        prefix=generation_prefix,
        return_as_list=True,
    )
    returned_generation = "".join(raw_generation)
    return returned_generation


async def find_emoji():
    """Returns the ID of the emoji specified in .env

    Queries the Discord API for a list of emoji on the guild specified in .env
    Searches the list for the emoji specified in .env and returns its ID

    :return: the encoded emoji text, returns 0 if emoji isn't found or enabled
    """
    # Check if emoji is disabled
    if EMOJI_SERVER == "False":
        return 0
    # Obtain list of all emoji
    emoji_list = await http_client.get_all_emoji(EMOJI_SERVER)
    emoji_json = json.dumps(emoji_list)
    emoji_object = json.loads(emoji_json)
    internal_emoji_id = 0
    # Search for emoji specified in .env
    for emoji_item in emoji_object:
        if emoji_item["name"] == EMOJI_NAME:
            internal_emoji_id = emoji_item["id"]
    if internal_emoji_id == 0:
        internal_encoded_emoji = ""
    else:
        internal_encoded_emoji = "<a:typing:" + internal_emoji_id + ">"
    return internal_encoded_emoji


async def game_status():
    """Update the status using the game variant

    The game status always starts with "Playing "
    "Playing " is given to generate_message() as a prefix

    :return: the generated message that was set as the status
    """
    status_message = await generate_message("Playing ")
    trimmed_status = status_message[8:135]
    await discordpy_client.change_presence(
        activity=discord.Game(name=trimmed_status)
    )
    return trimmed_status


async def watching_status():
    """Update the status using the watching variant

    The game status always starts with "Watching "
    "Watching " is given to generate_message() as a prefix

    :return: the generated message that was set as the status
    """
    status_message = await generate_message("Watching ")
    trimmed_status = status_message[9:136]
    await discordpy_client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=trimmed_status
        )
    )
    return trimmed_status


async def listening_status():
    """Update the status using the listening variant

    The game status always starts with "Listening to "
    "Listening to " is given to generate_message() as a prefix

    :return: the generated message that was set as the status
    """
    status_message = await generate_message("Listening to ")
    trimmed_status = status_message[13:140]
    await discordpy_client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=trimmed_status
        )
    )
    return trimmed_status


async def random_status():
    """Picks a status variant every hour to update the bot status

    This function is meant to be run in a separate thread
    At the start of every hour, a random status type is chosen
    The function for that status type is then called

    :return: False if the loop exits, which shouldn't happen
    """
    # Picks from three status types and runs every x:00
    possible_types = [game_status, watching_status, listening_status]
    sleep_time = 60
    while True:
        time.sleep(sleep_time)
        time_instance = datetime.now()
        current_minutes = time_instance.strftime("%M")
        if current_minutes == "00":
            sleep_time = 3600
            await possible_types[random.randint(0, 2)]()
        else:
            sleep_time = 60
    return False


@discordpy_client.event
async def on_ready():
    """Runs startup actions once the discordpy_client initializes

    Takes care of a few startup tasks including finding the emoji ID, setting
    the initial status, and starting a thread for the hourly random status

    :return: a string indicating the tasks are complete
    """
    # Start http client instance
    await http_client.login()
    global emoji_id
    emoji_id = await find_emoji()
    # Set the bot user's status
    possible_types = [game_status, watching_status, listening_status]
    await possible_types[random.randint(0, 2)]()
    # Thread to set status every hour
    status_thread = threading.Thread(
        target=asyncio.run, args=(random_status(),)
    )
    status_thread.start()
    # Print starting message and info about bot
    print("[textgenrnn_discord_bot has started]")
    print("────────────────────────────────────────")
    print("Bot Name:", BOT_NAME)
    print("Connected to Discord As:", discordpy_client.user)
    print("────────────────────────────────────────")
    return "Finished on_ready() actions"


@interactions_client.command(
    name=CHAT_COMMAND_NAME,
    description=CHAT_COMMAND_DESCRIPTION,
)
async def chat_command(ctx: interactions.CommandContext):
    """Discord slash command that returns a message from the model

    :param ctx: the context provided by the Discord API
    :return: a string indicating a message was sent
    """
    # Send placeholder message while message is generating
    await ctx.send(eval(CHAT_COMMAND_TYPING_MESSAGE))
    generated_text = await generate_message("")
    # Edit placeholder with final generated message
    await ctx.edit(generated_text)
    return "Chat command message sent"


@interactions_client.command(
    name=PROMPT_COMMAND_NAME,
    description=PROMPT_COMMAND_DESCRIPTION,
    options=[
        interactions.Option(
            name="input",
            description=PROMPT_INPUT_DESCRIPTION,
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def prompt_command(ctx: interactions.CommandContext, input: str):
    """Discord slash command that allows the user to prompt the model

    The value for PROMPT_INPUT_NAME is set by .env
    This value is visible to the end user

    :param ctx: the context provided by the Discord API
    :param input: the input given by the user
    :return: a string indicating a message was sent
    """
    message_content = input
    # Limit generation prefix size
    generation_prefix = message_content[0:1999]
    # Send placeholder message while message is generating
    await ctx.send(eval(PROMPT_COMMAND_TYPING_MESSAGE))
    generated_text = await generate_message(generation_prefix)
    # Edit placeholder with final generated message
    await ctx.edit(generated_text)
    return "Prompt command message sent"


# Run bot clients in separate threads to prevent issues
main_bot_loop = asyncio.get_event_loop()
discordpy_task = main_bot_loop.create_task(
    discordpy_client.start(DISCORD_TOKEN)
)
interactions_task = main_bot_loop.create_task(interactions_client.start())
gathered_bot_loops = asyncio.gather(
    interactions_task, discordpy_task, loop=main_bot_loop
)
main_bot_loop.run_until_complete(gathered_bot_loops)
