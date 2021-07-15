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
    dao_address = unfreeze.data.target_address
    unfreeze_diff = unfreeze.data.diffs[0]['content']

    dao = await models.DAO.get(address=dao_address)
    holder = await models.Holder.get_or_create(address=unfreeze_diff['key']['address'])

    ledger = await models.Ledger.get_or_none(dao=dao, holder=holder[0])

    if ledger == None:
        await models.Ledger.create(balance=unfreeze_diff['value'], dao=dao, holder=holder[0])
    else:
        ledger.balance = unfreeze_diff['value']
        await ledger.save()