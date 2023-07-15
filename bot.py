"""
Main class for the Zulip bot and main entry.
"""
import os
import sys
import logging
import openai
import zulip
from dotenv import load_dotenv
from .contexts import Contexts
from .message import Message

PERMISSIONS_SET_CONTEXT = os.environ['PERMISSIONS_SET_CONTEXT']
BOT_NAME = os.environ['BOT_NAME']
VERSION = "1.1.3"

# Set up logging
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

class Bot:
    """
    Main class for the Zulip bot.
    """

    def __init__(self):
        # Load the .env file
        load_dotenv()

        self.contexts = Contexts()

        # Set up GPT-3 API key
        openai.api_key = os.environ['OPENAI_API_KEY']

        # Set up Zulip client
        self._client = zulip.Client(config_file=".zuliprc")

        logging.info("Initiate DB...")

        logging.info("Contexts")
        logging.info(self.contexts)

		# This is needed to be exposed to the Message class
        self.name = BOT_NAME
        self.email = self._client.email

    def run(self):
        """
        Start handling Zulip messages.
        """
        result = self._client.get_profile()
        logging.debug(result)

        if result.get('code') == 'UNAUTHORIZED':
            logging.error("Invalid API key")
            sys.exit(1)

        logging.info("Starting the GPT Zulip bot named: %s", BOT_NAME)
        self._client.call_on_each_event(self.handle_message, event_types=['message'])


    def send_message(self, message):
        """
        Send response message.
        """
        self._client.send_message(message)


    def help_message(self):
        """
        Return multiline string with help message.
        """
        return """# ChatGPT Assistant
This is a chatbot assistant that uses OpenAI's ChatGPT API to generate responses to your messages.

## How to use

To use the bot, simply mention it in a message, e.g. @**{bot}** hello!. The bot will then generate a response and send it back to you.
You can also write a private message to the bot without mentioning it.

## Subcommands

Subcommands are words starting with an exclamation mark, e.g. `!new`.
You can use the following subcommands to control the bot:

### General:
- `!help` - show this help message

### Context:
- `!topic` - use context from the current topic (default behaviour; subcommand not implemented/needed)
- `!stream` - use context from the current stream
- `!new` - start a new conversation; no previous context (the bot will use context from the previous conversation by default which may affect the generated response)
- `!contexts` - list all available contexts (e.g. `!cicada`, `!frankie`) and their values

Example custom defined context: `!cicada` - add system context for Cicada; this may provide more accurate responses

### Model (default depends on server settings):
- `!gpt3` - use GPT-3.5 Turbo (4K tokens, up to 2.5K for input)
- `!gpt4` - use GPT-4 (8K tokens, up to 6K for input)

### Global settings:
- `!set` - (not implemented yet) show current settings
- `!set context <name> <value> - insert a context like !cicada. Example: `!set context cicada Cicada is a business wallet`
- `!unset context <name>` - delete a context

### User settings (not implemented yet):
- `!me` - show your current settings
- `!me model gpt3` - set your default model to GPT-3.5 Turbo
- `!me model gpt4` - set your default model to GPT-4

## Example usage
- `@{bot} !gpt4 !stream Can you summarise previous messages?` - use GPT-4 and context from the current stream
- `@{bot} !new I have a question...` - start a new conversation using GPT-3.5 Turbo and no context (previous messages will be ignored)

Bot version: {version}
""".format(bot=BOT_NAME, version=VERSION)


    def is_from_admin(self, msg):
        """
        Check if the message is from admin user or not.
        """
        member = self._client.get_user_by_id(msg['sender_id'])
        return PERMISSIONS_SET_CONTEXT == "admin" and member.get("user", {}).get("is_admin")


    def handle_message(self, event):
        """
        Zulip message handling callback function.
        """
        logging.debug("Handling event type: %s", event['type'])

        if event['type'] != 'message':
            return

        message = Message(self, event['message'])
        message.process()


if __name__ == "__main__":
    bot = Bot()
    bot.run()
