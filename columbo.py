import os
import re
import time
from sqlite3 import OperationalError

import click
from rich.console import Console
from rich.prompt import Prompt
from src.service.console_service import generate_table, add_row_into_table
from src.service.database_service import put_log_file_into_database, execute_query

console = Console()


@click.command()
@click.option('--file', '-f', multiple=True, default=["example.log"])
def main(file):
    for f in file:
        console.print(f"[bold grey100]Loading {f} into database...")
        put_log_file_into_database(f)

    while True:
        query = Prompt.ask("[bold grey100] Request to execute")

        if query == "exit":
            break
        elif query == "clear":
            os.system("clear")
            continue

        try:
            with console.status("[bold grey100]Fetching data...") as status:
                rows = execute_query(query)

            with console.status("[bold grey100] Generate rendering...") as status:
                table = generate_table([column.strip() for column in re.findall(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE)[0].split(",")])
                for row in rows:
                    add_row_into_table(row, table)

            console.print(table)
        except OperationalError as e:
            console.print(f"[bold bright_red] QUERY ERROR: {e}")


if __name__ == '__main__':
    main()
