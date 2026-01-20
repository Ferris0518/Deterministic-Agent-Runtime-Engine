"""Event implementations."""

from vaf.event.impl.local_event_log import LocalEventLog
from vaf.event.impl.noop_listener import NoopListener

__all__ = ["LocalEventLog", "NoopListener"]
