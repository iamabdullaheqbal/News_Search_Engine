"""Run CPU-bound ML inference off the asyncio event loop."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="veritas-ml")


async def run_ml(fn: Callable[..., T], *args, **kwargs) -> T:
    loop = asyncio.get_running_loop()
    if kwargs:
        return await loop.run_in_executor(_executor, lambda: fn(*args, **kwargs))
    return await loop.run_in_executor(_executor, fn, *args)
