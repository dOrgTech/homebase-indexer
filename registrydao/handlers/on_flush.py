from typing import Dict, Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.flush import FlushParameter
from registrydao.types.registry.storage import RegistryStorage

def extract_key(proposal_key_list_item) -> str:
    return proposal_key_list_item['bytes']

async def on_flush(
    ctx: HandlerContext,
    flush: Transaction[FlushParameter, RegistryStorage],
) -> None:
    non_flushed_or_executed_keys = map(extract_key, flush.data.storage['proposal_key_list_sort_by_date'])
    dao_address = flush.data.target_address
    dao = await models.DAO.get(address=dao_address)
    treasury_type = await models.DAOType.get(name='treasury')
    registry_type = await models.DAOType.get(name='registry')

    if dao.type == treasury_type:
        dao_extra = await models.TreasuryExtra.get(dao=dao)
    elif dao.type == registry_type:
        dao_extra = await models.RegistryExtra.get(dao=dao)

    created_status = await models.DAO.get(description='created')
    executed_status = await models.DAO.get(description='executed')

    if dao_address == 'KT1P1mkdD7AnoSzJHYiBXpCtGipqnVqRenoR':
        print(flush)
    
    created_proposals = await models.Proposal.filter(dao=dao, status=created_status)

    # Update the executed/flushed proposals status
    for i in range(len(created_proposals)):
        if created_proposals[i].key not in non_flushed_or_executed_keys:
            created_proposals[i].status = executed_status
            await created_proposals[i].save()
    
    #Handle diffs
    for i in range(len(flush.data.diffs)):
        diff = flush.data.diffs[i]['content']

        if(['key'] == 'registry_affected'):
            dao_extra.registry_affected = diff['value']
            await dao_extra.save()

        if(['key'] == 'registry'):
            dao_extra.registry = diff['value']
            await dao_extra.save()
