from dipdup.context import HookContext
from registrydao.hooks.on_startup import process_network


async def on_reindex(
    ctx: HookContext,
) -> None:
    try:
        ctx.logger.info('Reindexing triggered')
        print("=" * 60)
        print("ON_REINDEX HOOK CALLED")
        print("=" * 60)
        
        # Discover and index historical DAOs
        ctx.logger.info("Starting historical DAO discovery...")
        print("Starting historical DAO discovery...")
        
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
        print("Historical DAO discovery completed")
    except Exception as e:
        ctx.logger.error(f"Error in on_reindex: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())
        print(f"Error in on_reindex: {e}")
        print(traceback.format_exc())