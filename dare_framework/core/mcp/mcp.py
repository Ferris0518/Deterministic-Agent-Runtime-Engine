from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Resource:
    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class ResourceContent:
    uri: str
    text: str | None
    mime_type: str | None
