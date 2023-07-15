"""
Message handling functionality.
"""

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
from .subcommands import Subcommands

DEFAULT_MODEL_NAME = os.environ['DEFAULT_MODEL_NAME']

class Message:
    """
    Class for message handling.
    """

    def __init__(self, bot, msg):
        self._bot = bot
        self._msg = msg
        self._contexts = self._bot.contexts

        if msg['type'] == 'private':
            self._response = {
                 'type': 'private',
                 'to': self._msg['sender_email'],
            }
        else:
            self._response = {
                 'type': 'stream',
                 'to': self._msg['display_recipient'],
                 'subject': self._msg['subject'],
            }

        # strip the command or mention trigger
        self._content = self._msg['content'].strip()
        bot_name = self._bot.name
        self._content = re.sub(f"@**{bot_name}**", "", self._content)
        self._content = re.sub(f"@{bot_name}", "", self._content)
        self._content = self._content.strip()

        # get subcommands (words starting with exclamation mark)
        self._subcommands = Subcommands(self, self._content)

        # strip subcommands
        self._content = self._subcommands.strip(self._content)


    def send_reply(self, content):
        """
        Send message response to the Zulip server.
        """
        response = self._response
        response['content'] = content
        self._bot.send_message(response)


    def _is_ignored(self):
        """
        Check whether or not the message could be ignored.
        """
        if self._msg['sender_email'] == self._bot.email:
            logging.debug("Ignoring message sent by myself")
            return True

        bot_name = self._bot.name
        if self._msg['type'] != 'private' and \
            not re.search(f"@**{bot_name}**", self._content) and \
            not re.search(f"@{bot_name}", self._content):
            logging.debug("Ignoring message not mentioning the bot or sent in private")
            return True

        return False


    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo"):
        """
        Returns the number of tokens used by a list of messages.
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        # note: future models may deviate from this
        if model.startswith("gpt-3") or model.startswith("gpt-4"):
            num_tokens = 0
            for message in messages:
                # every message follows <im_start>{role/name}\n{content}<im_end>\n
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens

        raise NotImplementedError( \
f"""
num_tokens_from_messages() is not presently implemented for model {model}.
See https://github.com/openai/openai-python/blob/main/chatml.md
for information on how messages are converted to tokens.
""")


    def with_previous_messages(self, msg, messages, subcommands, token_limit, append_after_index):
        """
        Join the current message with the context of previous messages.
        """
        query = {
            'anchor': msg['id'],
            'num_before': 100,  # adjust this value as needed
            'num_after': 0,
            'apply_markdown': False,
            'include_anchor': False,
            'narrow': [{'operand': msg['sender_email'], 'operator': 'pm-with'}],
        }

        if msg['type'] != 'private':
            narrow = [
                {'operand': msg['display_recipient'], 'operator': 'stream'},
            ]

            # filter to topic by default
            if "stream" not in subcommands:
                narrow.append({'operand': msg['subject'], 'operator': 'topic'})

            query['narrow'] = narrow

        previous_messages = self._client.get_messages(query)['messages']
        previous_messages.reverse()

        new_messages = messages.copy()

        for msg in previous_messages:
            content = msg['content'].strip()

            # remove mentions of the bot
            content = re.sub(r"@\*\*{bot}\*\*".format(bot=BOT_NAME), "", content)
            content = content.strip()

            # get subcommands (words starting with exclamation mark)
            # subcommands = subcommands.Subcommands(content)

            # don't remove in previous messages for now, as it breaks with some code blocks
            # content = remove_subcommands(content, subcommands)

            role = "assistant" if self._client.email == msg['sender_email'] else "user"

            new_messages.insert(append_after_index, {
                                "role": role, "content": content.strip()})
            tokens = num_tokens_from_messages(messages=new_messages)

            if tokens > token_limit:
                # remove message from index 1
                new_messages = new_messages[:append_after_index] + \
                    new_messages[append_after_index+1:]
                break

        return new_messages


    def process(self):
        """
        Process the message.
        """
        if self._is_ignored():
            return

        if len(subcommands) and "help" in subcommands:
            help_message = self._bot.help_message()
            send_reply(help_message, msg)
            return

        context_names = [context[0] for context in self._contexts]
        context_map = {context[0]: context[1] for context in self._contexts}

        if "contexts" in subcommands:
            help_message = "Available contexts:\n"
            for context_name, context_value in self._contexts:
                help_message += f"- `!{context_name}`: {context_value}\n"
            send_reply(help_message, msg)
            return

        if "me" in subcommands:
            send_reply("This functionality is not implemented yet.", msg)
            return

        if "set" in subcommands:
            subcommands.set(client, msg, content)
            return

        if "unset" in subcommands:
            subcommands.unset(client, msg, content)
            return

        roles = [
            {"role": "system", "content": os.environ['BOT_ROLE']},
            {"role": "user", "content": f"{content}"},
        ]

        messages = roles

        # new messages items will be appended after this index
        # as we add custom role: system messages here
        # and then add history messages later too between system and latest user message
        append_after_index = 1

        # iterate context_names and check if any of them is in subcommands
        for context_name in context_names:
            if context_name in subcommands:
                context_value = context_map[context_name]
                messages.insert(append_after_index, {
                    "role": "system", "content": f"{context_value}"})
                append_after_index += 1

        model_name = DEFAULT_MODEL_NAME or 'gpt-3.5-turbo'
        if "gpt3" in subcommands:
            model_name = 'gpt-3.5-turbo'
        elif "gpt4" in subcommands:
            model_name = 'gpt-4'

        model = model.Model(model_name)

        if not len(subcommands) or "new" not in subcommands:
            messages = with_previous_messages(
                msg, messages, subcommands, model.token_limit, append_after_index)

        response = model.get_response(messages)

        send_reply(response, msg)
