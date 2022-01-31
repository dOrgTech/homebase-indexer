from registrydao.utils.ledger import update_ledger
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

    vote_diff = vote.parameter.__root__[0].argument
    dao_address = vote.data.target_address
    proposal_key = vote_diff.proposal_key

    dao = await models.DAO.get(address=dao_address)
    proposal = await models.Proposal.get(key=proposal_key, dao=dao)

    voter = await models.Holder.get_or_create(address=vote_diff.from_)
    support = vote_diff.vote_type
    amount = vote_diff.vote_amount

    await update_ledger(vote.data.target_address, vote.data.diffs)

    await models.Vote.update_or_create(
        proposal=proposal,
        support=support,
        voter=voter[0],
        defaults={
            'amount':amount
        }
    )

    if support:
        proposal.upvotes = float(proposal.upvotes) + float(amount)
    else:
        proposal.downvotes = float(proposal.downvotes) + float(amount)
    
    await proposal.save()