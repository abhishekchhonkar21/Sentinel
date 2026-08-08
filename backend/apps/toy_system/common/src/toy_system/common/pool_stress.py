"""MongoDB connection pool stress — simulates pool exhaustion latency."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorClient

from toy_system.common.fault_state import fault_state_store
from toy_system.common.logging import configure_logging

if TYPE_CHECKING:
    from toy_system.common.config import ToyServiceSettings

logger = configure_logging("pool-stress")


class PoolStressManager:
    """Holds extra MongoDB clients open to starve the connection pool."""

    def __init__(self, *, settings: ToyServiceSettings) -> None:
        self._settings = settings
        self._clients: list[AsyncIOMotorClient] = []
        self._keeper_task: asyncio.Task[None] | None = None
        self._target_connections = 0

    async def sync(self) -> None:
        """Align held connections with fault_state.pool_stress_connections."""
        target = fault_state_store.get().pool_stress_connections
        if target == self._target_connections:
            return

        self._target_connections = target
        await self._release_all()

        if target <= 0:
            logger.info("pool_stress_disabled")
            return

        for _ in range(target):
            client = AsyncIOMotorClient(
                self._settings.mongodb_uri,
                maxPoolSize=1,
                minPoolSize=1,
            )
            self._clients.append(client)

        self._keeper_task = asyncio.create_task(self._keep_alive())
        logger.warning("pool_stress_enabled connections=%s", target)

    async def _keep_alive(self) -> None:
        while self._clients and self._target_connections > 0:
            for client in list(self._clients):
                try:
                    await client.admin.command("ping")
                except Exception:
                    logger.exception("pool_stress_ping_failed")
            await asyncio.sleep(2.0)

    async def shutdown(self) -> None:
        await self._release_all()

    async def _release_all(self) -> None:
        if self._keeper_task:
            self._keeper_task.cancel()
            try:
                await self._keeper_task
            except asyncio.CancelledError:
                pass
            self._keeper_task = None

        for client in self._clients:
            client.close()
        self._clients.clear()
