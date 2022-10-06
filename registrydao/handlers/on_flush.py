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
    try:
        non_flushed_or_executed_keys = list(map(extract_key, flush.data.storage['proposal_key_list_sort_by_level']))
        dao_address = flush.data.target_address
        dao = await models.DAO.get(address=dao_address)
        
        await update_ledger(dao_address, flush.data.diffs)
        await update_extra(dao_address, flush.data.diffs)

        dao.guardian = flush.data.storage["guardian"]
        await dao.save()

        executed_status = await models.ProposalStatus.get(description='executed')
        rejected_and_flushed_status = await models.ProposalStatus.get(description='rejected_and_flushed')
        dropped_status = await models.ProposalStatus.get(description='dropped')
        all_proposals = await models.Proposal.filter(dao=dao)

        for i in range(len(all_proposals)):
            if all_proposals[i].key not in non_flushed_or_executed_keys:
                is_rejected = int(all_proposals[i].downvotes) >= int(all_proposals[i].quorum_threshold)
                is_passed = (int(all_proposals[i].upvotes) >= int(all_proposals[i].quorum_threshold)) and not is_rejected
                is_dropped = await models.ProposalStatusUpdates.exists(proposal=all_proposals[i], status=dropped_status)
                is_executed = await models.ProposalStatusUpdates.exists(proposal=all_proposals[i], status=executed_status)
                
                if is_passed and not is_dropped and not is_executed:
                    await models.ProposalStatusUpdates.get_or_create(status=executed_status, proposal=all_proposals[i], timestamp=flush.data.timestamp, level=flush.data.level)
                elif is_rejected and not is_dropped and not is_executed:
                    await models.ProposalStatusUpdates.get_or_create(status=rejected_and_flushed_status, proposal=all_proposals[i], timestamp=flush.data.timestamp, level=flush.data.level)
                elif not is_dropped and not is_executed:
                    await models.ProposalStatusUpdates.get_or_create(status=dropped_status, proposal=all_proposals[i], timestamp=flush.data.timestamp, level=flush.data.level)
    except Exception as e:
        print("Error in on_flush: " + flush.data.target_address)
        print(e)