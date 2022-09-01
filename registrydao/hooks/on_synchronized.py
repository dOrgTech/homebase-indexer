from dipdup.context import HookContext


async def on_synchronized(
    ctx: HookContext,
) -> None:
    try:
        await ctx.execute_sql('on_synchronized')
    except Exception as e:
        print("Error in on_synchronized")
        print(e)