"""Tests for SQL, JSON, CSV, and XML data converters."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from click.testing import CliRunner

from toolbox.cli import cli
from toolbox.services.data_converters import (
    csv_to_json,
    json_to_csv,
    json_to_sql,
    sql_to_json,
    xml_to_json,
)


def test_sql_dump_to_json() -> None:
    sql = """
    INSERT INTO `users` (`id`, `name`, `active`) VALUES (1, 'Mustafa', TRUE), (2, 'Ali', FALSE);
    """
    res = sql_to_json(sql)
    assert len(res) == 2
    assert res[0]["name"] == "Mustafa"
    assert res[0]["active"] is True
    assert res[1]["name"] == "Ali"


def test_sqlite_file_to_json(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE products (id INT, title TEXT);")
    cursor.execute("INSERT INTO products VALUES (1, 'Laptop'), (2, 'Phone');")
    conn.commit()
    conn.close()

    res = sql_to_json(db_file, table_name="products")
    assert isinstance(res, list)
    assert len(res) == 2
    assert res[0]["title"] == "Laptop"


def test_json_to_sql() -> None:
    data = [{"id": 1, "name": "Mustafa"}, {"id": 2, "name": "Ali"}]
    sql = json_to_sql(data, table_name="users")
    assert "CREATE TABLE IF NOT EXISTS `users`" in sql
    assert "INSERT INTO `users` (`id`, `name`) VALUES (1, 'Mustafa');" in sql
    assert "INSERT INTO `users` (`id`, `name`) VALUES (2, 'Ali');" in sql


def test_csv_to_json_and_back() -> None:
    csv_text = "id,name\n1,Mustafa\n2,Ali"
    json_res = csv_to_json(csv_text)
    assert len(json_res) == 2
    assert json_res[0]["name"] == "Mustafa"

    back_csv = json_to_csv(json_res)
    assert "id,name" in back_csv
    assert "1,Mustafa" in back_csv


def test_xml_to_json() -> None:
    xml_text = "<root><person><name>Mustafa</name><age>30</age></person></root>"
    res = xml_to_json(xml_text)
    assert "root" in res
    assert res["root"]["person"]["name"] == "Mustafa"


def test_sql_to_json_cli(runner: CliRunner, tmp_path: Path) -> None:
    sql_file = tmp_path / "dump.sql"
    sql_file.write_text("INSERT INTO `items` (`id`, `val`) VALUES (10, 'Test');", encoding="utf-8")
    result = runner.invoke(cli, ["sql-to-json", str(sql_file)])
    assert result.exit_code == 0
    assert "Test" in result.output


def test_json_to_sql_cli(runner: CliRunner, tmp_path: Path) -> None:
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"id": 1, "role": "admin"}]', encoding="utf-8")
    result = runner.invoke(cli, ["json-to-sql", str(json_file), "--table", "roles"])
    assert result.exit_code == 0
    assert "INSERT INTO `roles`" in result.output
