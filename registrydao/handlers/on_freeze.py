from registrydao.utils.ledger import update_ledger
from typing import Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.freeze import FreezeParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_freeze(
    ctx: HandlerContext,
    freeze: Transaction[FreezeParameter, RegistryStorage],
) -> None:
    await update_ledger(freeze.data.target_address, freeze.data.diffs)