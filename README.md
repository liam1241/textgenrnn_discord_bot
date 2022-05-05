## textgenrnn_discord_bot
A simple Python script to turn a model into a functioning Discord bot.

**Before continuing, visit the repository for [textgenrnn](https://github.com/minimaxir/textgenrnn) and follow the instructions there to prepare a trained model. You will need a trained model to use this script.**

This started as a personal project and was later developed into a generalized script that can be used for any textgenrnn model. Credit to [Max Woolf (minimaxir)](https://github.com/minimaxir) for creating textgenrnn, which serves as the foundation for this project. Using this script, you can have a fully functional Discord bot just by editing the .env file. You shouldn't have to actually touch the code (unless you want to 😊).

### Bot Features
- Slash command and custom prefix support
- Allows the user to prompt the model's response
- Typing indicator while message generates
- Bot generates it's own status that updates every hour
- Can be ran on a CPU (no GPU required)

### Dependencies
- General
	- Python 3
	- Discord Account
	- Discord Bot Token
		- [Follow these instructions](https://discord-interactions.readthedocs.io/en/latest/quickstart.html) to obtain a bot token if you don't have one already. Follow that guide until the "Running the Bot and creating commands" section, then come back here after copying your token.
	- Linux?
		- This script has only been tested on Linux
		- It will *probably* work on other platforms
- Python
	- TensorFlow ([Installation Instructions](https://www.tensorflow.org/install))
		- Version 2.1.0 or later
	- textgenrnn (`pip install textgenrnn`)
	- dotenv (`pip install python-dotenv`)
	- discord.py (`pip install discord.py`)
	- interactions.py (`pip install discord-py-interactions`)

### Usage
Clone the repository to a directory on your local system:

`git clone [url here]`

Navigate to the directory and create a .env file from the template to use:

`cp .env_template .env`

Use your favorite text editor to change the parameters in .env to customize your bot. The template provides an explanation of what each value does. If you face any errors, double check the .env file.

Run the script:

`python bot.py`

Good job! You hopefully have a working bot at this point 🥳


### License
This project is licensed under the MIT license.
