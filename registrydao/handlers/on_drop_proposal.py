from registrydao.utils.ledger import update_ledger
from typing import Optional
from datetime import datetime
from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.drop_proposal import DropProposalParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_drop_proposal(
    ctx: HandlerContext,
    drop_proposal: Transaction[DropProposalParameter, RegistryStorage],
) -> None:

    dao_address = drop_proposal.data.target_address

    await update_ledger(dao_address, drop_proposal.data.diffs)

    dao = await models.DAO.get(address=dao_address)
    status = await models.ProposalStatus.get(description='dropped')
    proposal = await models.Proposal.get(key=drop_proposal.data.parameter_json, dao=dao)
    
    await models.ProposalStatusUpdates.get_or_create(status=status, proposal=proposal, timestamp=drop_proposal.data.timestamp, level=drop_proposal.data.level)