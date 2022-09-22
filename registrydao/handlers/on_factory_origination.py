from registrydao.utils.ctx import extract_network_from_ctx
from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext
from typing import cast


from registrydao.types.registry.storage import RegistryStorage


async def on_factory_origination(
    ctx: HandlerContext,
    registry_origination: Origination[RegistryStorage],
) -> None:
    try:
        originated_contract = cast(str, registry_origination.data.originated_contract_address)
        index_name = f'registry_dao_{originated_contract}'
        
        network = extract_network_from_ctx(ctx)
        
        if index_name not in ctx.config.indexes:
            await ctx.add_contract(
                name=originated_contract,
                address=originated_contract,
                typename='registry',
            )
            await ctx.add_index(
                name=index_name,
                template='registry_dao',
                values=dict(contract=originated_contract, datasource=f'tzkt_{network}'),
            )
    except Exception as e:
        print("Error in on_factory_origination: " + cast(str, registry_origination.data.originated_contract_address))
        print(e)