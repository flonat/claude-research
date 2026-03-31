"""
Tool registry auto-loader.

Importing this package triggers side-effect registration of all tools.
Conditional tools (ORCID, CORE, Altmetric) register only if their
API credentials are available — handled inside each module.
"""

import sys
from pathlib import Path

# Ensure the parent directory (package root) is on sys.path
# so tool modules can `from _app import ...`
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

# Import all tool modules — each registers its tools as a side effect
from tools import openalex      # noqa: F401  (8 tools)
from tools import scholarly     # noqa: F401  (9+ tools)
from tools import orcid         # noqa: F401  (2 tools, conditional)
from tools import core          # noqa: F401  (2 tools, conditional)
from tools import altmetric     # noqa: F401  (2 tools, conditional)
from tools import openreview    # noqa: F401  (3 tools)
from tools import dblp          # noqa: F401  (1 tool)
from tools import opencitations # noqa: F401  (2 tools)
from tools import unpaywall     # noqa: F401  (1 tool)
from tools import zenodo        # noqa: F401  (2 tools)
