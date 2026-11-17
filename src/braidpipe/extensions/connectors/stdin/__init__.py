from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import AsyncIterator
from typing import Any

from braidpipe.extensions.sdk import ExtensionConfig, SourceConnector


class StdinExtension(ExtensionConfig):
    pass


class StdinSource(SourceConnector):
    """Read JSON Lines from sys.stdin. Unix-pipe friendly."""

    async def fetch(self) -> AsyncIterator[dict[str, Any]]:

        def _read():
            for line in sys.stdin:
                line = line.strip()
                if line:
                    yield json.loads(line)

        # Use sync generator via to_thread iteration
        records = await asyncio.to_thread(lambda: list(_read()))
        for record in records:
            yield record
