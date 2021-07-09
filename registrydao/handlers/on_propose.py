from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext, RollbackHandlerContext
from typing import Optional


import registrydao.models as models

from registrydao.types.registry.parameter.propose import ProposeParameter
from registrydao.types.registry.storage import RegistryStorage
import requests


async def on_propose(
    ctx: HandlerContext,
    propose: Transaction[ProposeParameter, RegistryStorage],
) -> None:
    await models.Proposal(id="").save()