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

class Contexts:

    def __init__(self):
        if not os.path.exists('data'):
            os.makedir('data')
        self._conn = sqlite3.connect('data/data.db')
        self._cur = conn.cursor()

        self._contexts = {}

        self._cur.execute("CREATE TABLE IF NOT EXISTS contexts(name PRIMARY KEY, value)")

        self._refetch()

    def __iter__(self):
        for context in self._contexts:
            yield context


    def upsert(self, context_name, context_value):
        if self._is_reserved(context_name):
            return False

        context_exists = self._cur.execute(
            "SELECT * FROM contexts WHERE name = ?", (context_name,)).fetchone()
        if context_exists:
            self._cur.execute("UPDATE contexts SET value = ? WHERE name = ?",
                        (context_value, context_name))
        else:
            self._cur.execute("INSERT INTO contexts (name, value) VALUES (?, ?)",
                        (context_name, context_value))
        self._conn.commit()
        self.refetch()
        return True


    def delete(self, context_name):
        self._cur.execute("DELETE FROM contexts WHERE name = ?", (context_name,))
        self._conn.commit()
        self.refetch()


    def _refetch(self):
        self._contexts = self._cur.execute("SELECT * FROM contexts").fetchall()

    def _is_reserved(self, context_name):
        reserved_contexts = ["topic", "stream", "new", "help",
                             "contexts", "gpt3", "gpt4", "set", "unset", "me", "admin", "stats"]
        return context_name in reserved_contexts

