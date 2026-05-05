"""Pytest config for tests under app/.

Modules inside app/ (e.g. utils/, components/) are written assuming app/ is the
working directory — they use bare imports like `from utils.format_data import ...`
and `from utils.helper_functions import join_lines`. Pytest doesn't run from
inside app/, so we put app/ on sys.path here. Pytest auto-discovers any
conftest.py on the path to a collected test, which is why this file just needs
to exist; no fixtures required.
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
