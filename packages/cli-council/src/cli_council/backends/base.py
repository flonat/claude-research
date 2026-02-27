"""Abstract base for CLI backends."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from abc import ABC, abstractmethod
from time import perf_counter

from cli_council.config import STAGE_TIMEOUT

logger = logging.getLogger(__name__)


class CLIBackend(ABC):
    """Base class for CLI tool backends."""

    name: str = ""
    command: str = ""

    @abstractmethod
    def build_args(self, prompt: str, *, model: str | None = None) -> list[str]:
        """Build the full argument list for subprocess execution."""

    def is_available(self) -> bool:
        """Check if the CLI tool is installed and on PATH."""
        return shutil.which(self.command) is not None

    async def run(
        self,
        prompt: str,
        *,
        model: str | None = None,
        timeout: int = STAGE_TIMEOUT,
        cwd: str | None = None,
    ) -> tuple[str, int]:
        """Execute the CLI tool and return (output_text, elapsed_ms).

        Raises RuntimeError if the command fails or times out.
        """
        args = self.build_args(prompt, model=model)
        logger.info("Running %s: %s", self.name, " ".join(args[:4]) + "...")

        # Clean environment: unset CLAUDECODE to allow nested claude calls
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        t0 = perf_counter()
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            elapsed = int((perf_counter() - t0) * 1000)
            raise RuntimeError(
                f"{self.name} timed out after {timeout}s"
            ) from None

        elapsed = int((perf_counter() - t0) * 1000)
        output = stdout.decode("utf-8", errors="replace").strip()

        if proc.returncode != 0:
            err = stderr.decode("utf-8", errors="replace").strip()
            logger.warning(
                "%s exited with code %d: %s",
                self.name, proc.returncode, err[:200],
            )
            # Some backends write useful output to stderr on non-zero exit
            if not output and err:
                output = err

        return output, elapsed
