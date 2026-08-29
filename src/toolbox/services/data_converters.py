"""Data Converters Service — SQL, JSON, CSV, and XML conversions.

All functions use pure Python stdlib (sqlite3, json, csv, xml.etree.ElementTree, re).
"""

from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from toolbox.errors import AppError


# ---------------------------------------------------------------------------
# SQL -> JSON
# ---------------------------------------------------------------------------


def sql_to_json(
    source: str | Path, table_name: str | None = None
) -> dict[str, Any] | list[dict[str, Any]]:
    """Convert a SQL file (INSERT statements or SQLite DB file) to JSON structure.

    If source is a SQLite database file, uses sqlite3 module to extract table data.
    If source is a SQL script text / file, parses INSERT INTO statements.
    """
    path = Path(source) if isinstance(source, (str, Path)) and Path(source).exists() else None

    # 1. SQLite Database file
    if path and path.is_file():
        # Check if it's a binary SQLite file by reading magic header
        try:
            with path.open("rb") as f:
                header = f.read(16)
            if header.startswith(b"SQLite format 3"):
                return _sqlite_to_json(path, table_name)
        except Exception:
            pass

    # 2. Text SQL file or SQL string
    sql_text = path.read_text(encoding="utf-8", errors="replace") if path else str(source)
    return _parse_sql_insert_dump(sql_text, target_table=table_name)


def _sqlite_to_json(
    db_path: Path, table_name: str | None = None
) -> dict[str, Any] | list[dict[str, Any]]:
    """Extract rows from SQLite database file."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        if table_name:
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = [dict(row) for row in cursor.fetchall()]
            return rows

        # All tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [r[0] for r in cursor.fetchall()]
        result: dict[str, list[dict[str, Any]]] = {}

        for tbl in tables:
            cursor.execute(f"SELECT * FROM `{tbl}`")
            result[tbl] = [dict(row) for row in cursor.fetchall()]

        return result
    except sqlite3.Error as exc:
        raise AppError(f"SQLite error: {exc}")
    finally:
        conn.close()


def _parse_sql_insert_dump(
    sql_text: str, target_table: str | None = None
) -> dict[str, Any] | list[dict[str, Any]]:
    """Parse INSERT INTO SQL statements into JSON objects."""
    # Pattern to match INSERT INTO table_name (cols...) VALUES (...)
    insert_pattern = re.compile(
        r"INSERT\s+INTO\s+[`\"']?(\w+)[`\"']?\s*(?:\(([^)]+)\))?\s*VALUES\s*(.+?);",
        re.IGNORECASE | re.DOTALL,
    )

    tables_data: dict[str, list[dict[str, Any]]] = {}

    for match in insert_pattern.finditer(sql_text):
        tbl_name = match.group(1)
        cols_raw = match.group(2)
        values_raw = match.group(3)

        if target_table and tbl_name.lower() != target_table.lower():
            continue

        columns = [c.strip(" `\"'\n\r\t") for c in cols_raw.split(",")] if cols_raw else []

        # Parse tuples from values_raw: (val1, val2), (val3, val4)
        value_tuples = _parse_sql_values(values_raw)

        if tbl_name not in tables_data:
            tables_data[tbl_name] = []

        for row_vals in value_tuples:
            if columns and len(columns) == len(row_vals):
                row_dict = dict(zip(columns, row_vals))
            else:
                row_dict = {f"col_{i+1}": v for i, v in enumerate(row_vals)}
            tables_data[tbl_name].append(row_dict)

    if not tables_data:
        raise AppError(
            "No valid INSERT statements or SQLite tables found in input SQL."
        )

    if target_table:
        return tables_data.get(target_table, [])
    if len(tables_data) == 1:
        return next(iter(tables_data.values()))
    return tables_data


def _parse_sql_values(values_str: str) -> list[list[Any]]:
    """Helper to parse SQL tuple values: (1, 'Mustafa', NULL, 99.5), (2, 'Ali', TRUE, 85)."""
    rows: list[list[Any]] = []
    # Split by rows ending with )
    tuples = re.findall(r"\(([^)]+)\)", values_str)

    for tuple_str in tuples:
        row_vals = []
        # Split items by comma while respecting quotes
        items = re.findall(r"(?:'[^']*'|\"[^\"]*\"|[^,]+)", tuple_str)
        for item in items:
            val = item.strip()
            if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                row_vals.append(val[1:-1].replace("''", "'"))
            elif val.upper() == "NULL":
                row_vals.append(None)
            elif val.upper() == "TRUE":
                row_vals.append(True)
            elif val.upper() == "FALSE":
                row_vals.append(False)
            elif re.match(r"^-?\d+$", val):
                row_vals.append(int(val))
            elif re.match(r"^-?\d+\.\d+$", val):
                row_vals.append(float(val))
            else:
                row_vals.append(val)
        rows.append(row_vals)

    return rows


# ---------------------------------------------------------------------------
# JSON -> SQL
# ---------------------------------------------------------------------------


def json_to_sql(json_data: Any, table_name: str = "data") -> str:
    """Convert JSON array of objects to SQL INSERT statements."""
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    if isinstance(json_data, dict):
        # Could be multi-table dict or single object
        if all(isinstance(v, list) for v in json_data.values()):
            lines = []
            for tbl, rows in json_data.items():
                lines.append(json_to_sql(rows, table_name=tbl))
            return "\n\n".join(lines)
        json_data = [json_data]

    if not isinstance(json_data, list) or not json_data:
        raise AppError("JSON input must be a non-empty array of objects.")

    # Determine column schema
    columns: list[str] = []
    for row in json_data:
        if isinstance(row, dict):
            for k in row.keys():
                if k not in columns:
                    columns.append(k)

    if not columns:
        raise AppError("JSON items must be objects with key-value pairs.")

    sql_lines = []
    cols_str = ", ".join(f"`{c}`" for c in columns)

    # Create table statement
    col_defs = [f"  `{c}` TEXT" for c in columns]
    create_table = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n" + ",\n".join(col_defs) + "\n);"
    sql_lines.append(create_table)

    # Insert statements
    for row in json_data:
        vals = []
        for col in columns:
            v = row.get(col) if isinstance(row, dict) else None
            if v is None:
                vals.append("NULL")
            elif isinstance(v, bool):
                vals.append("TRUE" if v else "FALSE")
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            else:
                escaped = str(v).replace("'", "''")
                vals.append(f"'{escaped}'")
        vals_str = ", ".join(vals)
        sql_lines.append(f"INSERT INTO `{table_name}` ({cols_str}) VALUES ({vals_str});")

    return "\n".join(sql_lines)


# ---------------------------------------------------------------------------
# CSV <-> JSON
# ---------------------------------------------------------------------------


def csv_to_json(csv_text: str) -> list[dict[str, str]]:
    """Convert CSV text to list of dicts."""
    f = io.StringIO(csv_text.strip())
    reader = csv.DictReader(f)
    rows = list(reader)
    if not rows:
        raise AppError("CSV input is empty or missing headers.")
    return rows


def json_to_csv(json_data: Any) -> str:
    """Convert JSON array of objects to CSV string."""
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    if not isinstance(json_data, list) or not json_data:
        raise AppError("JSON input must be a non-empty array of objects.")

    columns: list[str] = []
    for row in json_data:
        if isinstance(row, dict):
            for k in row.keys():
                if k not in columns:
                    columns.append(k)

    if not columns:
        raise AppError("JSON items must be objects.")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in json_data:
        if isinstance(row, dict):
            writer.writerow(row)

    return output.getvalue()


# ---------------------------------------------------------------------------
# XML -> JSON
# ---------------------------------------------------------------------------


def xml_to_json(xml_text: str) -> dict[str, Any]:
    """Convert XML string to a JSON-serializable dict structure."""
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError as exc:
        raise AppError(f"Invalid XML: {exc}")

    def _elem_to_dict(elem: ET.Element) -> Any:
        d: dict[str, Any] = {}
        if elem.attrib:
            d["@attributes"] = elem.attrib

        children = list(elem)
        if children:
            child_dict: dict[str, Any] = {}
            for child in children:
                cd = _elem_to_dict(child)
                tag = child.tag
                if tag in child_dict:
                    if not isinstance(child_dict[tag], list):
                        child_dict[tag] = [child_dict[tag]]
                    child_dict[tag].append(cd)
                else:
                    child_dict[tag] = cd
            d.update(child_dict)

        text = (elem.text or "").strip()
        if text:
            if d:
                d["#text"] = text
            else:
                return text
        return d or ""

    return {root.tag: _elem_to_dict(root)}
