from __future__ import annotations

from uuid import uuid4

def generator_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


