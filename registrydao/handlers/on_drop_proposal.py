from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext, RollbackHandlerContext
from typing import Optional


import registrydao.models as models

from registrydao.types.registry.parameter.drop_proposal import DropProposalParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_drop_proposal(
    ctx: HandlerContext,
    drop_proposal: Transaction[DropProposalParameter, RegistryStorage],
) -> None:
    ...