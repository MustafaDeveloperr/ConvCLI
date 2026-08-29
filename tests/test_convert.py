"""Tests for the unit converter."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from toolbox.cli import cli
from toolbox.commands.convert import convert_value
from toolbox.errors import AppError


# ---------------------------------------------------------------------------
# Unit-level tests (no CLI layer)
# ---------------------------------------------------------------------------


class TestConvertValue:
    def test_km_to_miles(self) -> None:
        result, category = convert_value(1, "km", "miles")
        assert abs(result - 0.621371) < 0.001
        assert category == "length"

    def test_miles_to_km(self) -> None:
        result, _ = convert_value(1, "miles", "km")
        assert abs(result - 1.60934) < 0.001

    def test_celsius_to_fahrenheit(self) -> None:
        result, category = convert_value(100, "c", "f")
        assert abs(result - 212) < 0.001
        assert category == "temperature"

    def test_fahrenheit_to_celsius(self) -> None:
        result, _ = convert_value(32, "f", "c")
        assert abs(result - 0) < 0.001

    def test_celsius_to_kelvin(self) -> None:
        result, _ = convert_value(0, "c", "k")
        assert abs(result - 273.15) < 0.001

    def test_kelvin_to_fahrenheit(self) -> None:
        result, _ = convert_value(273.15, "k", "f")
        assert abs(result - 32) < 0.01

    def test_same_unit(self) -> None:
        result, _ = convert_value(42, "c", "c")
        assert result == 42.0

    def test_gb_to_mb(self) -> None:
        result, category = convert_value(5, "gb", "mb")
        assert result == 5120.0
        assert category == "storage"

    def test_hours_to_minutes(self) -> None:
        result, _ = convert_value(2, "hours", "minutes")
        assert result == 120.0

    def test_kph_to_mph(self) -> None:
        result, _ = convert_value(100, "kph", "mph")
        assert abs(result - 62.137) < 0.01

    def test_invalid_unit(self) -> None:
        with pytest.raises(AppError):
            convert_value(1, "furlong", "km")

    def test_incompatible_units(self) -> None:
        with pytest.raises(AppError):
            convert_value(1, "km", "kg")

    def test_case_insensitive(self) -> None:
        result, _ = convert_value(1, "KM", "MILES")
        assert abs(result - 0.621371) < 0.001

    def test_temperature_alias(self) -> None:
        result, _ = convert_value(100, "celsius", "fahrenheit")
        assert abs(result - 212) < 0.001

    def test_zero_value(self) -> None:
        result, _ = convert_value(0, "km", "m")
        assert result == 0.0


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestConvertCLI:
    def test_basic_conversion(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["convert", "10", "km", "miles"])
        assert result.exit_code == 0
        assert "6.21" in result.output

    def test_temperature(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["convert", "100", "c", "f"])
        assert result.exit_code == 0
        assert "212" in result.output

    def test_unknown_unit_exits_1(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["convert", "1", "lightyears", "km"])
        assert result.exit_code == 1

    def test_list_flag(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["convert", "1", "km", "m", "--list"])
        assert result.exit_code == 0
        assert "length" in result.output.lower()

    def test_storage(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["convert", "1", "gb", "mb"])
        assert result.exit_code == 0
        assert "1,024" in result.output or "1024" in result.output
