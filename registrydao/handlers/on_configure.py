from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext, RollbackHandlerContext
import registrydao.models as models

async def on_configure(ctx: HandlerContext) -> None:
    await models.ProposalStatus.get_or_create(description="created")
    await models.ProposalStatus.get_or_create(description="dropped")
    await models.ProposalStatus.get_or_create(description="executed")
    await models.ProposalStatus.get_or_create(description="rejected_and_flushed")
    await models.DAOType.get_or_create(name='treasury')
    await models.DAOType.get_or_create(name='registry')