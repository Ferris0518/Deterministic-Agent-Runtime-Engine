"""Call the DARE A2A server (run a2a_serve.py first).

Usage:
    Terminal 1: python a2a_serve.py --port 8010
    Terminal 2: python a2a_client_demo.py [--url http://localhost:8010] [--message "Hello"]
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.a2a import A2AClient, discover_agent_card, A2AClientError


async def main() -> None:
    parser = argparse.ArgumentParser(description="A2A client demo: discover and tasks/send")
    parser.add_argument("--url", default="http://localhost:8010", help="Agent base URL")
    parser.add_argument("--message", default="Say hello in one sentence.", help="Message to send")
    parser.add_argument("--subscribe", action="store_true", help="Use tasks/sendSubscribe (SSE)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(f"Discovering AgentCard at {base_url}/.well-known/agent.json ...")
    try:
        card = await discover_agent_card(base_url)
        print(f"  name: {card.get('name')}")
        print(f"  description: {card.get('description', '')[:60]}...")
    except Exception as e:
        print(f"  Failed: {e}")
        print("  Make sure a2a_serve.py is running (e.g. python a2a_serve.py --port 8010)")
        sys.exit(1)

    client = A2AClient(base_url, timeout_seconds=120)
    print(f"\nSending: {args.message!r}")
    try:
        if args.subscribe:
            async for state in client.send_subscribe(args.message):
                print("  [SSE] state:", state.get("status", {}).get("state"), state.get("id"))
            print("  Done (SSE).")
        else:
            state = await client.send_async(args.message)
            print("  task_id:", state.get("id"))
            print("  status:", state.get("status"))
            for art in state.get("artifacts", []):
                for part in art.get("parts", []):
                    if part.get("type") == "text":
                        print("  output:", part.get("text", "")[:200])
    except A2AClientError as e:
        print(f"  Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
