"""Unit converter command — pure Python, zero external dependencies.

Supported categories:
    length      km  m  cm  mm  mi  yd  ft  in
    weight      kg  g  mg  lb  oz  t
    temperature c   f  k
    storage     b   kb  mb  gb  tb  pb
    time        ms  s   min  h  d  w
    speed       mps  kph  mph  knot
    area        m2  km2  cm2  ft2  mi2  acre  ha
    volume      ml  l   fl_oz  cup  pt  qt  gal
"""

from __future__ import annotations

import sys
from typing import Callable

import click

from toolbox.cli import cli
from toolbox.errors import AppError
from toolbox.utils.output import print_result, print_error


# ---------------------------------------------------------------------------
# Conversion tables — all values relative to a canonical base unit
# ---------------------------------------------------------------------------

# length — base: meters
_LENGTH: dict[str, float] = {
    "km": 1000.0,
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "mi": 1609.344,
    "mile": 1609.344,
    "miles": 1609.344,
    "yd": 0.9144,
    "ft": 0.3048,
    "in": 0.0254,
    "inch": 0.0254,
}

# weight — base: kilograms
_WEIGHT: dict[str, float] = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "lb": 0.453592,
    "lbs": 0.453592,
    "oz": 0.0283495,
    "t": 1000.0,
    "ton": 1000.0,
}

# storage — base: bytes
_STORAGE: dict[str, float] = {
    "b": 1.0,
    "byte": 1.0,
    "bytes": 1.0,
    "kb": 1024.0,
    "mb": 1024.0 ** 2,
    "gb": 1024.0 ** 3,
    "tb": 1024.0 ** 4,
    "pb": 1024.0 ** 5,
}

# time — base: seconds
_TIME: dict[str, float] = {
    "ms": 0.001,
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "min": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "h": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
    "d": 86400.0,
    "day": 86400.0,
    "days": 86400.0,
    "w": 604800.0,
    "week": 604800.0,
    "weeks": 604800.0,
}

# speed — base: meters per second
_SPEED: dict[str, float] = {
    "mps": 1.0,
    "kph": 1.0 / 3.6,
    "kmh": 1.0 / 3.6,
    "mph": 0.44704,
    "knot": 0.514444,
    "knots": 0.514444,
}

# area — base: square meters
_AREA: dict[str, float] = {
    "m2": 1.0,
    "km2": 1e6,
    "cm2": 1e-4,
    "ft2": 0.092903,
    "mi2": 2.59e6,
    "acre": 4046.86,
    "ha": 10000.0,
}

# volume — base: liters
_VOLUME: dict[str, float] = {
    "ml": 0.001,
    "l": 1.0,
    "liter": 1.0,
    "litre": 1.0,
    "fl_oz": 0.0295735,
    "cup": 0.236588,
    "pt": 0.473176,
    "qt": 0.946353,
    "gal": 3.78541,
}

# ---------------------------------------------------------------------------
# Temperature has special (non-multiplicative) conversions
# ---------------------------------------------------------------------------


def _celsius_to_fahrenheit(v: float) -> float:
    return v * 9 / 5 + 32


def _celsius_to_kelvin(v: float) -> float:
    return v + 273.15


def _fahrenheit_to_celsius(v: float) -> float:
    return (v - 32) * 5 / 9


def _fahrenheit_to_kelvin(v: float) -> float:
    return _celsius_to_kelvin(_fahrenheit_to_celsius(v))


def _kelvin_to_celsius(v: float) -> float:
    return v - 273.15


def _kelvin_to_fahrenheit(v: float) -> float:
    return _celsius_to_fahrenheit(_kelvin_to_celsius(v))


_TEMP_CONVERTERS: dict[tuple[str, str], Callable[[float], float]] = {
    ("c", "f"): _celsius_to_fahrenheit,
    ("c", "k"): _celsius_to_kelvin,
    ("f", "c"): _fahrenheit_to_celsius,
    ("f", "k"): _fahrenheit_to_kelvin,
    ("k", "c"): _kelvin_to_celsius,
    ("k", "f"): _kelvin_to_fahrenheit,
}

_TEMP_ALIASES: dict[str, str] = {
    "celsius": "c",
    "fahrenheit": "f",
    "kelvin": "k",
}

# Map of table name → dict of unit → base multiplier
_TABLES: dict[str, dict[str, float]] = {
    "length": _LENGTH,
    "weight": _WEIGHT,
    "storage": _STORAGE,
    "time": _TIME,
    "speed": _SPEED,
    "area": _AREA,
    "volume": _VOLUME,
}


# ---------------------------------------------------------------------------
# Core conversion logic
# ---------------------------------------------------------------------------


def _normalise_unit(unit: str) -> str:
    return unit.strip().lower()


def convert_value(value: float, from_unit: str, to_unit: str) -> tuple[float, str]:
    """Convert *value* from *from_unit* to *to_unit*.

    Returns:
        Tuple of (result_float, category_name).

    Raises:
        AppError: If units are unknown or incompatible.
    """
    fu = _normalise_unit(from_unit)
    tu = _normalise_unit(to_unit)

    # Resolve temperature aliases
    fu = _TEMP_ALIASES.get(fu, fu)
    tu = _TEMP_ALIASES.get(tu, tu)

    # Temperature — special-case
    if fu in ("c", "f", "k") or tu in ("c", "f", "k"):
        key = (fu, tu)
        if fu == tu:
            return value, "temperature"
        converter = _TEMP_CONVERTERS.get(key)
        if converter is None:
            raise AppError(
                f"Cannot convert temperature '{from_unit}' → '{to_unit}'.",
                hint="Supported temperature units: c, f, k",
            )
        return converter(value), "temperature"

    # Find the table that contains both units
    for category, table in _TABLES.items():
        if fu in table and tu in table:
            result = value * table[fu] / table[tu]
            return result, category

    # Units not found in the same table
    _all_units: set[str] = set()
    for t in _TABLES.values():
        _all_units.update(t.keys())
    _all_units.update(_TEMP_ALIASES.keys())
    _all_units.update({"c", "f", "k"})

    if fu not in _all_units and tu not in _all_units:
        raise AppError(
            f"Unknown units: '{from_unit}' and '{to_unit}'.",
            hint="Run 'tool convert --list' to see supported units.",
        )
    if fu not in _all_units:
        raise AppError(
            f"Unknown unit: '{from_unit}'.",
            hint="Run 'tool convert --list' to see supported units.",
        )
    if tu not in _all_units:
        raise AppError(
            f"Unknown unit: '{to_unit}'.",
            hint="Run 'tool convert --list' to see supported units.",
        )
    raise AppError(
        f"Cannot convert '{from_unit}' to '{to_unit}': they belong to different categories.",
        hint="Run 'tool convert --list' to see supported units.",
    )


# ---------------------------------------------------------------------------
# Click command
# ---------------------------------------------------------------------------


@cli.command(name="convert")
@click.argument("value", type=float)
@click.argument("from_unit")
@click.argument("to_unit")
@click.option(
    "--list",
    "show_list",
    is_flag=True,
    default=False,
    help="List all supported units.",
)
def convert_cmd(value: float, from_unit: str, to_unit: str, show_list: bool) -> None:
    """Convert VALUE from FROM_UNIT to TO_UNIT.

    \b
    Examples:
      tool convert 10 km miles
      tool convert 100 c f
      tool convert 5 gb mb
      tool convert 2 hours minutes
      tool convert 60 mph kph

    \b
    Note: Currency conversion is not supported (requires a live API).
    """
    if show_list:
        _print_unit_list()
        return

    try:
        result, category = convert_value(value, from_unit, to_unit)
    except AppError as exc:
        print_error(exc.message, hint=exc.hint)
        sys.exit(1)

    # Format output: avoid scientific notation for reasonable ranges
    if abs(result) >= 1e-4 or result == 0:
        formatted = f"{result:,.6g}"
    else:
        formatted = f"{result:.10g}"

    print_result(
        f"{value:g} {from_unit}",
        f"{formatted} {to_unit}  ({category})",
    )


def _print_unit_list() -> None:
    click.echo("Supported Units:")
    for category, tbl in _TABLES.items():
        click.echo(f"  {category:<12} {" ".join(sorted(tbl.keys()))}")
    click.echo("  temperature  c (Celsius)  f (Fahrenheit)  k (Kelvin)")
    click.echo("\nCurrency conversion requires a live API and is not supported.")
