from typing import Optional
from datetime import datetime

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.propose import ProposeParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_propose(
    ctx: HandlerContext,
    propose: Transaction[ProposeParameter, RegistryStorage],
) -> None:
    dao_address = propose.data.target_address
    proposal_diff = propose.data.diffs[0]['content']
    
    dao = await models.DAO.get(address=dao_address).prefetch_related('governance_token')
    proposer = await models.Holder.get_or_create(address=proposal_diff['value']['proposer'])
    created_status = await models.ProposalStatus.get(description='created')
    start_date = datetime.strptime(proposal_diff['value']['start_date'], '%Y-%m-%dT%H:%M:%SZ')

    proposal = await models.Proposal.get_or_create(
        dao=dao,
        hash=proposal_diff['hash'],
        key=proposal_diff['key'],
        defaults={
            'upvotes': proposal_diff['value']['upvotes'],
            'start_date': start_date,
            'metadata': proposal_diff['value']['metadata'],
            'proposer': proposer[0],
            'downvotes': proposal_diff['value']['downvotes'],
            'voting_stage_num': proposal_diff['value']['voting_stage_num'],
            'proposer_frozen_token': proposal_diff['value']['proposer_frozen_token'],
            'quorum_threshold': round((int(proposal_diff['value']['quorum_threshold']) / 1000000) * int(dao.governance_token.supply)),
        }
    )

    await models.ProposalStatusUpdates.get_or_create(status=created_status, proposal=proposal[0], timestamp=propose.data.timestamp)