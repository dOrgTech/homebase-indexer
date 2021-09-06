from registrydao.utils.extra import update_extra
from registrydao.utils.ledger import update_ledger

from dipdup.models import Transaction
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

    non_flushed_or_executed_keys = map(extract_key, flush.data.storage['proposal_key_list_sort_by_level'])
    dao_address = flush.data.target_address
    dao = await models.DAO.get(address=dao_address)
    
    await update_ledger(dao_address, flush.data.diffs)
    await update_extra(dao_address, flush.data.diffs)

    created_status = await models.ProposalStatus.get(description='created')
    executed_status = await models.ProposalStatus.get(description='executed')
    rejected_and_flushed_status = await models.ProposalStatus.get(description='rejected_and_flushed')
    dropped_status = await models.ProposalStatus.get(description='dropped')
    created_proposals = await models.Proposal.filter(dao=dao, status_updates__status=created_status)

    for i in range(len(created_proposals)):
        if created_proposals[i].key not in non_flushed_or_executed_keys:
            is_passed = int(created_proposals[i].upvotes) >= int(created_proposals[i].quorum_threshold)
            is_rejected = int(created_proposals[i].downvotes) >= int(created_proposals[i].quorum_threshold)
            is_dropped = await models.ProposalStatusUpdates.exists(proposal=created_proposals[i], status=dropped_status)
            is_executed = await models.ProposalStatusUpdates.exists(proposal=created_proposals[i], status=executed_status)
            
            if is_passed and not is_dropped and not is_executed:
                await models.ProposalStatusUpdates.get_or_create(status=executed_status, proposal=created_proposals[i], timestamp=flush.data.timestamp, level=flush.data.level)
            elif is_rejected and not is_dropped and not is_executed:
                await models.ProposalStatusUpdates.get_or_create(status=rejected_and_flushed_status, proposal=created_proposals[i], timestamp=flush.data.timestamp, level=flush.data.level)