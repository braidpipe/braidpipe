import json
from pathlib import Path

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Braidpipe Playbook",
    "type": "object",
    "required": ["version", "source", "destination"],
    "properties": {
        "version": {
            "type": "string",
            "enum": ["1"],
            "description": "Playbook schema version"
        },
        "name": {
            "type": "string",
            "description": "Human-readable name for this braid"
        },
        "source": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["generator", "stdin", "http"]},
                "config": {"type": "object"}  # Will be refined per type
            },
            "required": ["type"]
        },
        "transform": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["filter", "rename", "select"]},
                    "config": {"type": "object"}
                }
            }
        },
        "destination": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["stdout"]},
                "config": {"type": "object"}
            },
            "required": ["type"]
        }
    }
}

Path("schema/playbook_v1.json").write_text(json.dumps(schema, indent=2))
