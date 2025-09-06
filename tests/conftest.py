import sys
from pathlib import Path

# Ensure `src` is on the Python path so tests can import `ts_shape`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

