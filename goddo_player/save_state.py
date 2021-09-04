import sqlite3
from dataclasses import dataclass


@dataclass
class State:
    save_file: str

    def __post_init__(self):
        self.db_conn = sqlite3.connect(self.save_file)
        cursor = self.db_conn.cursor()

        with open("sql/create_table.sql") as sql_file:
            sql_as_string = sql_file.read()
            cursor.executescript(sql_as_string)


