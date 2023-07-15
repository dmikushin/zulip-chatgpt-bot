"""
Implement contexts database.
"""

import os
import sqlite3

class Contexts:
    """
    Implement contexts database.
    """

    def __init__(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        self._conn = sqlite3.connect('data/data.db')
        self._cur = self._conn.cursor()

        self._contexts = {}

        self._cur.execute("CREATE TABLE IF NOT EXISTS contexts(name PRIMARY KEY, value)")

        self._refetch()


    def __iter__(self):
        for context in self._contexts:
            yield context


    def insert(self, context_name, context_value):
        """
        Insert context.
        """
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
        self._refetch()
        return True


    def delete(self, context_name):
        """
        Delete context.
        """
        self._cur.execute("DELETE FROM contexts WHERE name = ?", (context_name,))
        self._conn.commit()
        self._refetch()


    def _refetch(self):
        """
        Re-fetch contexts from the offline database.
        """
        self._contexts = self._cur.execute("SELECT * FROM contexts").fetchall()

    def _is_reserved(self, context_name):
        """
        Check if the context name is a reserved word that cannot be used.
        """
        reserved_contexts = ["topic", "stream", "new", "help",
                             "contexts", "gpt3", "gpt4", "set", "unset", "me", "admin", "stats"]
        return context_name in reserved_contexts
