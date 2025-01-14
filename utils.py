"""
Welcome to the infamous utils file.
"""

import re
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

VREGEX = re.compile(r'version \= "(\d\.\d\.\d)"')


@cache
def now():
    return str(datetime.now(UTC))


@cache
def parse_version() -> str:
    pyproj = Path('pyproject.toml').read_text()
    return VREGEX.findall(pyproj)[0]
