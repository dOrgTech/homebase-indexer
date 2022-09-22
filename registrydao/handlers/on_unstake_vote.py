from registrydao.utils.ledger import update_ledger
from typing import Optional
from datetime import datetime
from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.unstake_vote import UnstakeVoteParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_unstake_vote(
    ctx: HandlerContext,
    unstake_vote: Transaction[UnstakeVoteParameter, RegistryStorage],
) -> None:
    try:
        dao_address = unstake_vote.data.target_address
        await update_ledger(dao_address, unstake_vote.data.diffs)
    except Exception as e:
        print("Error in on_unstake_vote: " + str(unstake_vote.data.target_address))
        print(e)