import os
import sys
import logging
import re
import openai
import zulip
from dotenv import load_dotenv
import tiktoken
import sqlite3
import datetime
import contexts

class Subcommands:

    def __init__(self, message, content):
        """
        Read subcommands from the given content.
        """
        content_chunks = content.strip().split()
        self._subcommands = [word.lower().replace("!", "")
            for word in content_chunks if word.startswith("!")]
        self._message = message

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("%s Prompt from %s with subcommands: %s is: %s",
            str(current_time), str(msg['sender_email']), ", ".join(subcommands), content)

    def __iter__(self):
        for subcommand in self._subcommands:
            yield context


    def strip(self, content):
        """
        Strip subcommands from the given content.
        """
        for subcommand in self._subcommands:
            content = re.sub(f"!{subcommand} ", "", content,
                             flags=re.IGNORECASE).strip()
            content = re.sub(f"!{subcommand}", "", content,
                             flags=re.IGNORECASE).strip()
        return content


    def set(self, content):
        content_chunks = content.strip().split()
        command = content_chunks[0].lower()

        # set the specified command
        commands.set(command, self._message, content_chunks)


    def unset(self, content):
        content_chunks = content.strip().split()
        command = content_chunks[0].lower()

        # unset the specified command
        commands.unset(command, self._message, content_chunks)

