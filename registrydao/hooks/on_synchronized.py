from dipdup.context import HookContext
from registrydao.hooks.on_startup import process_network


async def on_synchronized(
    ctx: HookContext,
) -> None:
    ctx.logger.info('All indexes are synchronized')
    
    # Discover and index historical DAOs (only run once)
    try:
        from dipdup.database import get_connection
        async with get_connection() as conn:
            # Check if we've already run historical DAO discovery
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM dipdup_index WHERE name LIKE 'registry_dao_%')"
            )
            if result:
                ctx.logger.info("Historical DAOs already indexed, skipping discovery")
                return
    except Exception as e:
        ctx.logger.warning(f"Could not check for existing indexes: {e}")
    
    try:
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
        ctx.logger.error(f"Error in historical DAO discovery: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())