"""Worker entry point: Periodic scheduler, escalation, outbox dispatch, and twin rules."""

from __future__ import annotations

import asyncio
import signal
from typing import Any

from app.core.config import get_settings
from app.core.logging import logger, setup_logging
from app.db.session import async_session_factory
from app.worker.dispatcher import dispatch_outbox
from app.worker.generator import generate_upcoming_doses
from app.worker.risk_job import run_periodic_twin_rules
from app.worker.tick import process_scheduler_tick

settings = get_settings()
setup_logging()

_running = True


def _handle_shutdown(signum: int, frame: Any) -> None:
    global _running
    logger.info("worker_shutting_down", signal=signum)
    _running = False


async def run_worker_loop() -> None:
    logger.info("worker_started", tick_interval=settings.tick_seconds)
    tick_count = 0

    while _running:
        tick_count += 1
        try:
            async with async_session_factory() as session:
                # 1. Generate upcoming doses (daily or on tick 1)
                if tick_count % 120 == 1:  # Every hour
                    await generate_upcoming_doses(session)

                # 2. Process scheduler tick (due-soon, missed, escalation)
                tick_stats = await process_scheduler_tick(session)

                # 3. Dispatch notification outbox
                dispatched = await dispatch_outbox(session)

                # 4. Evaluate twin risk rules (every 10 ticks / 5 minutes)
                if tick_count % 10 == 0:
                    await run_periodic_twin_rules(session)

                if dispatched > 0 or tick_stats["reminded"] > 0 or tick_stats["missed"] > 0:
                    logger.info("worker_tick_summary", dispatched=dispatched, **tick_stats)

        except Exception as exc:
            logger.exception("worker_tick_error", error=str(exc))

        await asyncio.sleep(settings.tick_seconds)


def main() -> None:
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)
    asyncio.run(run_worker_loop())


if __name__ == "__main__":
    main()
