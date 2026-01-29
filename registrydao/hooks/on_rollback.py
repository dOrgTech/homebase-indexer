from dipdup.context import HookContext


async def on_rollback(
    ctx: HookContext,
    from_level: int,
    to_level: int,
) -> None:
    try:
        await ctx.execute_sql('on_rollback')
        await ctx.reindex('rollback')
    except Exception as e:
        print("Error in on_rollback")
        print(e)
