from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel

from braidpipe.extensions.sdk import BraidContext, SourceConnector


class GeneratorConfig(BaseModel):
    count: int = 10
    prefix: str = "record"


class GeneratorSource(SourceConnector):
    """Yield N synthetic records. Perfect for testing the engine."""

    def __init__(self, config: dict[str, Any], context: BraidContext):
        super().__init__(config, context)
        self.cfg = GeneratorConfig(**config)

    async def fetch(self) -> AsyncIterator[dict[str, Any]]:
        for i in range(self.cfg.count):
            yield {
                "id": i,
                "name": f"{self.cfg.prefix}_{i}",
                "value": i*10,
            }
