from typing import List

import registrydao.models as models

async def update_ledger(dao_address: str, diffs: List) -> None:

    dao = await models.DAO.get(address=dao_address)

    if diffs == None:
        return

    for diff in diffs:
        if diff['path'] == 'freeze_history':
            holder_address = diff['content']['key']
            past_unstaked = diff['content']['value']['past_unstaked']
            current_stage_num = diff['content']['value']['current_stage_num']
            current_unstaked = diff['content']['value']['current_unstaked']
            staked = diff['content']['value']['staked']

            holder = await models.Holder.get_or_create(address=holder_address)

            found_ledger = await models.Ledger.get_or_none(dao=dao, holder=holder[0])

            if found_ledger == None:
                await models.Ledger.create(past_unstaked=past_unstaked, dao=dao, holder=holder[0], current_stage_num=current_stage_num, current_unstaked=current_unstaked, staked=staked)
            else:
                found_ledger.past_unstaked = past_unstaked
                found_ledger.current_stage_num = current_stage_num
                found_ledger.current_unstaked = current_unstaked
                found_ledger.staked = staked
                await found_ledger.save()