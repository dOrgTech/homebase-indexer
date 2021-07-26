from typing import Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.vote import VoteParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_vote(
    ctx: HandlerContext,
    vote: Transaction[VoteParameter, RegistryStorage],
) -> None:

    vote_diff = vote.data.diffs[0]['content']
    dao_address = vote.data.target_address

    dao = await models.DAO.get(address=dao_address)
    proposal = await models.Proposal.get(key=vote_diff['key'], dao=dao)
    voter = await models.Holder.get(address=vote_diff['value']['voters'][0]['voter_address'])
    support = vote_diff['value']['voters'][0]['vote_type']
    amount = vote_diff['value']['voters'][0]['vote_amount']
    passed_status = await models.ProposalStatus.get_or_create(description="passed")
    rejected_status = await models.ProposalStatus.get_or_create(description="rejected")

    await models.Vote.get_or_create(
        key=vote_diff['key'],
        hash=vote_diff['hash'],
        proposal=proposal,
        amount=amount,
        support=support,
        voter=voter
    )

    if support == True:
        proposal.upvotes = int(proposal.upvotes) + int(amount)
    else:
        proposal.downvotes = int(proposal.downvotes) + int(amount)

    await proposal.save()

    is_passed = int(proposal.upvotes) >= int(proposal.quorum_threshold)
    is_rejected = int(proposal.downvotes) >= int(proposal.quorum_threshold)
    already_passed = await models.ProposalStatusUpdates.exists(proposal=proposal, status=passed_status[0])
    already_rejected = await models.ProposalStatusUpdates.exists(proposal=proposal, status=rejected_status[0])

    if is_passed and already_passed == False:
        await models.ProposalStatusUpdates.get_or_create(status=passed_status[0], proposal=proposal, timestamp=vote.data.timestamp)
    
    if is_rejected and already_rejected == False and is_passed == False:
        await models.ProposalStatusUpdates.get_or_create(status=rejected_status[0], proposal=proposal, timestamp=vote.data.timestamp)