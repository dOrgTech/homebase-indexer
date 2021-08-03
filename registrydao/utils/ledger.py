from typing import List

import registrydao.models as models

async def update_ledger(dao_address: str, diffs: List) -> None:

    dao = await models.DAO.get(address=dao_address)

    if diffs == None:
        return

    for diff in diffs:
        if diff['path'] == 'ledger':
            holder_address = diff['content']['key']['address']
            amount = diff['content']['value']

            holder = await models.Holder.get_or_create(address=holder_address)

            found_ledger = await models.Ledger.get_or_none(dao=dao, holder=holder[0])

            if found_ledger == None:
                await models.Ledger.create(balance=amount, dao=dao, holder=holder[0])
            else:
                found_ledger.balance = amount
                await found_ledger.save()