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
    dao_address = freeze.data.target_address
    freeze_diff = freeze.data.diffs[0]['content']

    dao = await models.DAO.get(address=dao_address)
    holder = await models.Holder.get_or_create(address=freeze_diff['key']['address'])

    ledger = await models.Ledger.get_or_none(dao=dao, holder=holder[0])

    if ledger == None:
        await models.Ledger.create(balance=freeze_diff['value'], dao=dao, holder=holder[0])
    else:
        ledger.balance = freeze_diff['value']
        await ledger.save()
