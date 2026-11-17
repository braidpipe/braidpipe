from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from braidpipe.extensions.sdk import DestinationConnector, ExtensionConfig


class StdoutConfig(ExtensionConfig):
    pass


class StdoutDestination(DestinationConnector):
    """Print JSON Lines to stdout."""

    async def push(self, records: AsyncIterator[dict[str, Any]]) -> None:
        async for record in records:
            print(json.dumps(record, indent=2, default=str))
