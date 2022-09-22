from dipdup.context import HookContext
import registrydao.models as models

async def on_restart(
    ctx: HookContext,
) -> None:
    try:
        await ctx.execute_sql('on_restart')
        await models.ProposalStatus.get_or_create(description="created")
        await models.ProposalStatus.get_or_create(description="dropped")
        await models.ProposalStatus.get_or_create(description="executed")
        await models.ProposalStatus.get_or_create(description="rejected_and_flushed")
        await models.DAOType.get_or_create(name='treasury')
        await models.DAOType.get_or_create(name='registry')
    except Exception as e:
        print("Error in on_restart")
        print(e)