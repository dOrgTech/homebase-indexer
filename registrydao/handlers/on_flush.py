from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext, RollbackHandlerContext
from typing import Optional


import registrydao.models as models

from registrydao.types.registry.parameter.flush import FlushParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_flush(
    ctx: HandlerContext,
    flush: Transaction[FlushParameter, RegistryStorage],
) -> None:
    ...