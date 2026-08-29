"""Data converter commands: sql-to-json, json-to-sql, csv-to-json, json-to-csv, xml-to-json.

All commands support reading from a file path argument or STDIN.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from toolbox.cli import cli
from toolbox.errors import AppError
from toolbox.services.data_converters import (
    csv_to_json,
    json_to_csv,
    json_to_sql,
    sql_to_json,
    xml_to_json,
)
from toolbox.utils.files import resolve_output_path
from toolbox.utils.output import console, print_error, print_success


def _read_input(file_arg: str | None) -> tuple[str, Path | None]:
    """Read input text from file_arg or STDIN."""
    if file_arg and file_arg != "-":
        p = Path(file_arg)
        if not p.exists():
            raise AppError(f"File not found: {file_arg}")
        if not p.is_file():
            raise AppError(f"Not a regular file: {file_arg}")
        return p.read_text(encoding="utf-8", errors="replace"), p

    # STDIN
    if not sys.stdin.isatty():
        return sys.stdin.read(), None

    raise AppError(
        "No input provided.",
        hint="Provide a file path argument or pipe content via STDIN.",
    )


# ---------------------------------------------------------------------------
# sql-to-json
# ---------------------------------------------------------------------------


@cli.command(name="sql-to-json")
@click.argument("sql_file", required=False)
@click.option("--table", "-t", default=None, help="Specific table name to extract.")
@click.option("--output", "-o", default=None, help="Output JSON file path.")
@click.option("--indent", "-i", default=2, show_default=True, help="JSON indent width.")
def sql_to_json_cmd(sql_file: str | None, table: str | None, output: str | None, indent: int) -> None:
    """Convert a SQL file (INSERT dump or SQLite DB) to JSON.

    \b
    Examples:
      tool sql-to-json dump.sql
      tool sql-to-json database.db --table users
      cat dump.sql | tool sql-to-json
    """
    try:
        if sql_file and Path(sql_file).exists() and Path(sql_file).is_file():
            # Check SQLite binary file
            res = sql_to_json(Path(sql_file), table_name=table)
            in_path = Path(sql_file)
        else:
            raw, in_path = _read_input(sql_file)
            res = sql_to_json(raw, table_name=table)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    formatted = json.dumps(res, indent=indent, ensure_ascii=False)

    if output:
        out_p = Path(output)
        out_p.write_text(formatted, encoding="utf-8")
        print_success("Converted SQL to JSON successfully.", input_path=in_path, output_path=out_p)
    else:
        console.print_json(formatted)


# ---------------------------------------------------------------------------
# json-to-sql
# ---------------------------------------------------------------------------


@cli.command(name="json-to-sql")
@click.argument("json_file", required=False)
@click.option("--table", "-t", default="data", show_default=True, help="Target SQL table name.")
@click.option("--output", "-o", default=None, help="Output SQL file path.")
def json_to_sql_cmd(json_file: str | None, table: str, output: str | None) -> None:
    """Convert JSON array of objects to SQL INSERT statements.

    \b
    Examples:
      tool json-to-sql users.json --table users
      cat users.json | tool json-to-sql --table users
    """
    try:
        raw, in_path = _read_input(json_file)
        sql_out = json_to_sql(raw, table_name=table)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    if output:
        out_p = Path(output)
        out_p.write_text(sql_out, encoding="utf-8")
        print_success("Converted JSON to SQL successfully.", input_path=in_path, output_path=out_p)
    else:
        console.print(sql_out)


# ---------------------------------------------------------------------------
# csv-to-json
# ---------------------------------------------------------------------------


@cli.command(name="csv-to-json")
@click.argument("csv_file", required=False)
@click.option("--output", "-o", default=None, help="Output JSON file path.")
@click.option("--indent", "-i", default=2, show_default=True, help="JSON indent width.")
def csv_to_json_cmd(csv_file: str | None, output: str | None, indent: int) -> None:
    """Convert CSV file or STDIN to JSON.

    \b
    Examples:
      tool csv-to-json data.csv
      cat data.csv | tool csv-to-json
    """
    try:
        raw, in_path = _read_input(csv_file)
        res = csv_to_json(raw)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    formatted = json.dumps(res, indent=indent, ensure_ascii=False)

    if output:
        out_p = Path(output)
        out_p.write_text(formatted, encoding="utf-8")
        print_success("Converted CSV to JSON successfully.", input_path=in_path, output_path=out_p)
    else:
        console.print_json(formatted)


# ---------------------------------------------------------------------------
# json-to-csv
# ---------------------------------------------------------------------------


@cli.command(name="json-to-csv")
@click.argument("json_file", required=False)
@click.option("--output", "-o", default=None, help="Output CSV file path.")
def json_to_csv_cmd(json_file: str | None, output: str | None) -> None:
    """Convert JSON array of objects to CSV.

    \b
    Examples:
      tool json-to-csv data.json
      cat data.json | tool json-to-csv
    """
    try:
        raw, in_path = _read_input(json_file)
        csv_out = json_to_csv(raw)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    if output:
        out_p = Path(output)
        out_p.write_text(csv_out, encoding="utf-8")
        print_success("Converted JSON to CSV successfully.", input_path=in_path, output_path=out_p)
    else:
        console.print(csv_out.strip())


# ---------------------------------------------------------------------------
# xml-to-json
# ---------------------------------------------------------------------------


@cli.command(name="xml-to-json")
@click.argument("xml_file", required=False)
@click.option("--output", "-o", default=None, help="Output JSON file path.")
@click.option("--indent", "-i", default=2, show_default=True, help="JSON indent width.")
def xml_to_json_cmd(xml_file: str | None, output: str | None, indent: int) -> None:
    """Convert XML file or STDIN to JSON.

    \b
    Examples:
      tool xml-to-json document.xml
      cat document.xml | tool xml-to-json
    """
    try:
        raw, in_path = _read_input(xml_file)
        res = xml_to_json(raw)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    formatted = json.dumps(res, indent=indent, ensure_ascii=False)

    if output:
        out_p = Path(output)
        out_p.write_text(formatted, encoding="utf-8")
        print_success("Converted XML to JSON successfully.", input_path=in_path, output_path=out_p)
    else:
        console.print_json(formatted)
