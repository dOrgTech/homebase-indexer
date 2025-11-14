from dipdup.context import HookContext


async def on_synchronized(
    ctx: HookContext,
) -> None:
    ctx.logger.info('All indexes are synchronized')