from typing import Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.drop_proposal import DropProposalParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_drop_proposal(
    ctx: HandlerContext,
    drop_proposal: Transaction[DropProposalParameter, RegistryStorage],
) -> None:

    status = await models.ProposalStatus.get(description='dropped')
    proposal = await models.Proposal.get(key=drop_proposal.data.parameter_json)
    proposal.status = status
    await proposal.save()