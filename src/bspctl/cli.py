"""bspctl entry point - imports all command modules to register @app.command() handlers."""

from __future__ import annotations

import bspctl.commands.build  # noqa: F401
import bspctl.commands.clean  # noqa: F401
import bspctl.commands.diff  # noqa: F401
import bspctl.commands.doctor  # noqa: F401
import bspctl.commands.dump  # noqa: F401
import bspctl.commands.for_all  # noqa: F401
import bspctl.commands.gen_kas  # noqa: F401
import bspctl.commands.layers  # noqa: F401
import bspctl.commands.lock  # noqa: F401
import bspctl.commands.log  # noqa: F401
import bspctl.commands.override  # noqa: F401
import bspctl.commands.prefetch  # noqa: F401
import bspctl.commands.report  # noqa: F401
import bspctl.commands.settings  # noqa: F401
import bspctl.commands.shell  # noqa: F401
import bspctl.commands.stress_parse  # noqa: F401
import bspctl.commands.sync  # noqa: F401
import bspctl.commands.triage  # noqa: F401
from bspctl.commands import app  # noqa: F401 - re-exported for pyproject.toml entry point

__all__ = ["app"]
