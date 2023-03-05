import datetime
import os
import time
from sqlite3 import connect, Connection, Cursor
from typing import List, Dict

from src.service.configuration_service import config

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class Database:
    connection: Connection
    cursor: Cursor

    table_name: str
    columns: List[Dict[str, any]]
    query_columns: str

    available_columns_type = [
        "DATETIME",
        "TEXT",
        "INTEGER"
    ]

    def __init__(self, name: str):
        os.remove(f"{name}.db")
        self.connection = connect(f"{name}.db")
        self.cursor = self.connection.cursor()

        self.table_name = config.get_value("database.table.name")
        self.columns = config.get_value("database.table.columns")
        self.query_columns = ""

        self.create_tables()

    def create_tables(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT)")

        for index, column in enumerate(self.columns):
            if column["type"] not in self.available_columns_type:
                raise Exception(f"Invalid type {column['type']} for the column {column['name']}")

            self.cursor.execute(
                f"ALTER TABLE {self.table_name} ADD COLUMN {column['name']} {column['type'].replace('DATETIME', 'INTEGER')}"
            )

            if index == (len(self.columns) - 1):
                self.query_columns += column["name"]
            else:
                self.query_columns += (column["name"] + ", ")

        self.connection.commit()


db = Database("columbo")


def insert_line_into_database(line: str):
    line_content = line.replace("\n", "").split(config.get_value("log.delimiter"))

    query_values = ""
    for index, content in enumerate(line_content):
        content = content.strip()

        try:
            column_type = db.columns[index]["type"]
        except IndexError:
            line_content.pop(index)
            continue

        if column_type == "DATETIME":
            content = str(datetime.datetime.strptime(content, config.get_value("log.date_format")).timestamp())
        elif column_type == "TEXT":
            content = str("\"" + content + "\"")

        if index == (len(line_content) - 1):
            query_values += content
        else:
            query_values += (content + ", ")

    db.cursor.execute(f"INSERT INTO {db.table_name} ({db.query_columns}) VALUES ({query_values})")


def put_log_file_into_database(file: str):
    file_content = open(file, "r")
    lines = file_content.readlines()
    file_content.close()

    progress_bar = Progress(
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    )

    with progress_bar as p:
        for line in p.track(lines):
            insert_line_into_database(line)

    db.connection.commit()


def execute_query(query: str):
    db.cursor.execute(query)
    return db.cursor.fetchall()
