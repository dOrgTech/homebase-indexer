from dipdup.context import HookContext


async def on_reindex(
    ctx: HookContext,
) -> None:
    try:
        await ctx.execute_sql('on_reindex')
    except Exception as e:
        print("Error in on_reindex")
        print(e)