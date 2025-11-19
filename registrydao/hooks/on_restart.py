from dipdup.context import HookContext
import registrydao.models as models
from registrydao.hooks.on_startup import process_network

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
        await models.DAOType.get_or_create(name='lambda')
        
        # Discover and index historical DAOs
        ctx.logger.info("Starting historical DAO discovery...")
        
        # Process mainnet
        await process_network(
            ctx,
            'mainnet',
            2900000,
            'KT1MFxwTan4ptw6PSc3KK6e1xfzMrCb382tw',
            'tzkt_mainnet'
        )
        
        # Process ghostnet
        await process_network(
            ctx,
            'ghostnet',
            8900000,
            'KT1QZtF8vVUvZYRxttRwgftc4EaQHZWgzXNp',
            'tzkt_ghostnet'
        )
        
        ctx.logger.info("Historical DAO discovery completed")
    except Exception as e:
        ctx.logger.error(f"Error in on_restart: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())
        print("Error in on_restart")
        print(e)