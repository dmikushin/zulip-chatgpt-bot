"""
Handler of "context" subcommand. 
"""

class ContextSubcommand:
    """
    Handler of "context" subcommand. 
    """

    def __init__(self, message):
        self.name = "context"
        self._message = message

    def set(self, content_chunks):
        """
        Set the context to the given value.
        """
        if self._message.is_from_admin():
            self._message.send_reply("Sorry, only admins can un/set contexts")
            return

        context_name = content_chunks[1].lower()
        context_value = " ".join(content_chunks[2:])

        if self._message.bot.contexts.insert(context_name, context_value):
            self._message.send_reply(f"I have set !{context_name} to: {context_value}")
        else:
            self._message.send_reply(f"Sorry, you can't set context for {context_name}")

    def unset(self, content_chunks):
        """
        Unset the context.
        """
        if self._message.is_from_admin():
            self._message.send_reply("Sorry, only admins can un/set contexts")
            return

        context_name = content_chunks[1].lower()
        self._message.bot.contexts.delete(context_name)
        self._message.send_reply(f"I have unset !{context_name}")
