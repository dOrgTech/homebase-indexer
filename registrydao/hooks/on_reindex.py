
from dipdup.context import HookContext
import registrydao.models as models

async def on_reindex(
    ctx: HookContext,
) -> None:
    await ctx.execute_sql('on_reindex')
    await models.ProposalStatus.get_or_create(description="created")
    await models.ProposalStatus.get_or_create(description="dropped")
    await models.ProposalStatus.get_or_create(description="executed")
    await models.ProposalStatus.get_or_create(description="rejected_and_flushed")
    await models.DAOType.get_or_create(name='treasury')
    await models.DAOType.get_or_create(name='registry')