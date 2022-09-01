from registrydao.utils.ledger import update_ledger
from typing import Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.unfreeze import UnfreezeParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_unfreeze(
    ctx: HandlerContext,
    unfreeze: Transaction[UnfreezeParameter, RegistryStorage],
) -> None:
    try:
        await update_ledger(unfreeze.data.target_address, unfreeze.data.diffs)
    except Exception as e:
        print("Error in on_unfreeze: " + str(unfreeze.data.target_address))
        print(e)