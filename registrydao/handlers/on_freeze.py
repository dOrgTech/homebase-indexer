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
    try:
        await update_ledger(freeze.data.target_address, freeze.data.diffs)
    except Exception as e:
        print("Error in on_freeze: " + str(freeze.data.target_address))
        print(e)