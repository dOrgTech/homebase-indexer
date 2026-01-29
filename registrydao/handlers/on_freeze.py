from registrydao.utils.ledger import update_ledger
from typing import Optional

from dipdup.models.tezos_tzkt import TzktTransaction as Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.freeze import FreezeParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_freeze(
    ctx: HandlerContext,
    freeze: Transaction[FreezeParameter, RegistryStorage],
) -> None:
    try:
        dao_address = freeze.data.target_address
        await update_ledger(dao_address, freeze.data.diffs)
    except Exception as e:
        print("Error in on_freeze: " + str(freeze.data.target_address))
        print(e)
