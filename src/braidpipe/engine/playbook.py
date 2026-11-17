from typing import Any

from pydantic import BaseModel, Field, model_validator


class ConnectorNode(BaseModel):
    """
    One source or destination block in the YAML.
    Extension-specific config validation happens inside the extension class, not here.
    """
    connector: str
    context: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class Playbook(BaseModel):
    version: str
    name: str | None = None

    sources: dict[str, ConnectorNode]
    destinations: dict[str, ConnectorNode]

    @model_validator(mode="before")
    @classmethod
    def normalize_singular(cls, data: dict) -> dict:
        # source -> sources
        if "source" in data and "sources" not in data:
            source = data.pop("source")
            ctx_name = source.pop("context", "source")
            data["sources"] = {ctx_name: source}

        # destination -> destinations
        if "destination" in data and "destinations" not in data:
            destination = data.pop("destination")
            ctx_name = destination.pop("context", "destination")
            data["destinations"] = {ctx_name: destination}

        return data
