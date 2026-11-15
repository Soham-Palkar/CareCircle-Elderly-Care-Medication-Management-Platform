"""Realtime SSE broker scoped by circle_id."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator
from uuid import UUID


class RealtimeBroker:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, circle_id: UUID | str) -> asyncio.Queue:
        cid = str(circle_id)
        queue: asyncio.Queue = asyncio.Queue()
        if cid not in self._subscribers:
            self._subscribers[cid] = []
        self._subscribers[cid].append(queue)
        return queue

    def unsubscribe(self, circle_id: UUID | str, queue: asyncio.Queue) -> None:
        cid = str(circle_id)
        if cid in self._subscribers:
            self._subscribers[cid] = [q for q in self._subscribers[cid] if q is not queue]
            if not self._subscribers[cid]:
                del self._subscribers[cid]

    async def publish(self, circle_id: UUID | str, event: dict) -> None:
        cid = str(circle_id)
        if cid in self._subscribers:
            for q in list(self._subscribers[cid]):
                await q.put(event)

    async def stream(self, circle_id: UUID | str) -> AsyncGenerator[str, None]:
        q = self.subscribe(circle_id)
        try:
            # Yield initial keepalive
            yield f"event: ping\ndata: {json.dumps({'status': 'connected'})}\n\n"
            while True:
                data = await q.get()
                yield f"event: update\ndata: {json.dumps(data)}\n\n"
        finally:
            self.unsubscribe(circle_id, q)


realtime_broker = RealtimeBroker()
