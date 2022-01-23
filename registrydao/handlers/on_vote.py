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

    vote_diff = vote.data.diffs[0]['content']
    dao_address = vote.data.target_address

    dao = await models.DAO.get(address=dao_address)
    proposal = await models.Proposal.get(key=vote_diff['key'], dao=dao)

    for voter_diff in vote_diff['value']['voters']:
        voter = await models.Holder.get_or_create(address=voter_diff['key']['address'])
        support = voter_diff['key']['bool']
        amount = voter_diff['value']

        await update_ledger(vote.data.target_address, vote.data.diffs)

        await models.Vote.update_or_create(
            key=vote_diff['key'],
            hash=vote_diff['hash'],
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