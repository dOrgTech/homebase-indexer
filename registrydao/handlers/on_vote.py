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

    await models.Vote.get_or_create(
        key=vote_diff['key'],
        hash=vote_diff['hash'],
        proposal=proposal,
        amount=vote_diff['value']['voters'][0]['vote_amount'],
        support=vote_diff['value']['voters'][0]['vote_type'],
        voter=voter
    )