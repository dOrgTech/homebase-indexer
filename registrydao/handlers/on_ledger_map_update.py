from dipdup.context import HandlerContext
from dipdup.models import BigMapAction, BigMapDiff

import registrydao.models as models
from registrydao.types.registry.big_map.ledger_key import LedgerKey
from registrydao.types.registry.big_map.ledger_value import LedgerValue


async def on_ledger_map_update(
    ctx: HandlerContext,
    ledger: BigMapDiff[LedgerKey, LedgerValue],
) -> None:

    if ledger.action == BigMapAction.ALLOCATE:
        return

    dao_address = ledger.data.contract_address
    holder_address = ledger.data.key['address']
    value = ledger.data.value

    dao = await models.DAO.get(address=dao_address)
    holder = await models.Holder.get_or_create(address=holder_address)

    found_ledger = await models.Ledger.get_or_none(dao=dao, holder=holder[0])

    if found_ledger == None:
        await models.Ledger.create(balance=value, dao=dao, holder=holder[0])
    else:
        found_ledger.balance = value
        await found_ledger.save()

    