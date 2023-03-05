from sqlite3 import OperationalError
from typing import List

from rich.table import Table

from src.service.configuration_service import config


def generate_table(columns: List[str]) -> Table:
    table = Table(title="Result")

    configuration_columns = config.get_value("database.table.columns")
    for column in columns:

        if column == "*":
            if len(columns) == 1:
                table.add_column("ID", style="orange3", no_wrap=True)
                for configuration_column in configuration_columns:
                    table.add_column(configuration_column["name"].upper(), style=configuration_column["color"], no_wrap=True)
                break
            else:
                raise OperationalError("can use '*' only alone")

        configuration_column = next((item for item in configuration_columns if item["name"] == column), None)
        if configuration_column is not None:
            table.add_column(configuration_column["name"].upper(), style=configuration_column["color"], no_wrap=True)
        else:
            table.add_column(column.upper(), style="orange3", no_wrap=True)

    return table


def add_row_into_table(row: tuple, table: Table) -> None:
    formatted_row = []
    for col in row:
        formatted_row.append(
            apply_special_colors(str(col))
        )
    table.add_row(*formatted_row)


def apply_special_colors(value: str) -> str:
    expressions = config.get_value("special.colors.expressions")

    for expression, color in expressions.items():
        if expression in value:
            value = value.replace(expression, f"[{color}]{expression}[/{color}]")

    return value
