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

    created_status = await models.ProposalStatus.get(description='created')
    executed_status = await models.ProposalStatus.get(description='executed')
    created_proposals = await models.Proposal.filter(dao=dao, status=created_status)

    for i in range(len(created_proposals)):
        if created_proposals[i].key not in non_flushed_or_executed_keys:
            created_proposals[i].status = executed_status
            await created_proposals[i].save()

