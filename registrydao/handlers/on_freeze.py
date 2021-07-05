from registrydao.types.registry.parameter.freeze import FreezeParameter
from registrydao.types.registry.storage import RegistryStorage
from dipdup.context import HandlerContext
from dipdup.models import Transaction


async def on_freeze(
    ctx: HandlerContext,
    freeze: Transaction[FreezeParameter, RegistryStorage],
) -> None:
    print(freeze)
