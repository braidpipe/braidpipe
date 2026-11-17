from abc import ABC, abstractmethod
from collections import UserDict
from collections.abc import AsyncIterator
from typing import Any

from braidpipe.engine.context import BraidContext


class ExtensionConfig(UserDict):
    def __init__(self):
        super().__init__()


class SourceConfig(ExtensionConfig):
    pass


class DestinationConfig(ExtensionConfig):
    pass


class TransformationConfig(ExtensionConfig):
    pass


class Extension(ABC):
    def __init__(self, config: ExtensionConfig, context: BraidContext) -> None:
        self.config = config
        self.context = context

    async def setup(self) -> None: ...  # coroutine
    async def teardown(self) -> None: ...  # coroutine
    async def health_check(self) -> bool: ...  # type: ignore[empty-body]


class SourceConnector(Extension):
    @abstractmethod
    def fetch(self) -> AsyncIterator[dict[str, Any]]:
        """
        Return an async iterator of records.
        Implementations should use 'async def' with 'yield'.
        """
        ...


class TransformStatement(Extension):
    """A transform sits between source and destination."""

    @abstractmethod
    def transform(self, records: AsyncIterator[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
        """
        Return an async iterator of transformed records.
        Implementations should use 'async def' with 'yield'.
        """
        ...


class DestinationConnector(Extension):
    @abstractmethod
    async def push(self, records: AsyncIterator[dict[str, Any]]) -> None:
        """Consume records. This is a coroutine, not a generator."""
        ...
