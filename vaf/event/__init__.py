"""Event domain: Audit logging and hooks."""

from vaf.event.component import IEventLog, IEventListener, IExtensionPoint, IHook
from vaf.event.types import Event, HookType
from vaf.event.impl.local_event_log import LocalEventLog
from vaf.event.impl.noop_listener import NoopListener

__all__ = [
    "IEventLog",
    "IEventListener",
    "IExtensionPoint",
    "IHook",
    "Event",
    "HookType",
    "LocalEventLog",
    "NoopListener",
]
