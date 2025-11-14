from dipdup.context import HookContext


async def on_reindex(
    ctx: HookContext,
) -> None:
    ctx.logger.info('Reindexing triggered')