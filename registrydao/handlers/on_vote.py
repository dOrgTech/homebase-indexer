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
    voter = await models.Holder.get_or_create(address=vote_diff['value']['voters'][0]['key']['address'])
    support = vote_diff['value']['voters'][0]['key']['bool']
    amount = vote_diff['value']['voters'][0]['value']

    await update_ledger(vote.data.target_address, vote.data.diffs)

    await models.Vote.get_or_create(
        key=vote_diff['key'],
        hash=vote_diff['hash'],
        proposal=proposal,
        amount=amount,
        support=support,
        voter=voter[0]
    )

    if support == True:
        proposal.upvotes = int(proposal.upvotes) + int(amount)
    else:
        proposal.downvotes = int(proposal.downvotes) + int(amount)

    await proposal.save()