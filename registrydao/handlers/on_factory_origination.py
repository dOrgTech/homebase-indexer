from registrydao.utils.ctx import extract_network_from_ctx
from registrydao.utils.http import fetch
from registrydao.constants import NETWORK_MAP
from dipdup.models.tezos_tzkt import TzktOrigination as Origination, TzktOperationData
from dipdup.context import HandlerContext
from typing import cast, Union


async def on_factory_origination(
    ctx: HandlerContext,
    registry_origination: Union[Origination, TzktOperationData],
) -> None:
    try:
        # Handle both TzktOrigination (with .data) and TzktOperationData (direct)
        # Check if it's a TzktOrigination wrapper by checking if it has 'storage' attribute
        if hasattr(registry_origination, 'storage'):
            # TzktOrigination wrapper
            origination_data = registry_origination.data
            originated_contract = cast(str, origination_data.originated_contract_address)
            origination_level = origination_data.level
        else:
            # TzktOperationData directly (for similar_to pattern)
            origination_data = registry_origination
            originated_contract = cast(str, origination_data.originated_contract_address)
            origination_level = origination_data.level
        
        index_name = f'registry_dao_{originated_contract}'
        
        ctx.logger.info(f"on_factory_origination called for {originated_contract} at level {origination_level}")
        
        network = extract_network_from_ctx(ctx)
        
        try:
            eps = await fetch(
                f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/contracts/{originated_contract}/entrypoints"
            )
            if isinstance(eps, list):
                ep_set = set(ep.get('name', ep) if isinstance(ep, dict) else ep for ep in eps)
            else:
                ep_set = set()
            required = {"propose", "vote", "flush", "freeze", "unfreeze", "drop_proposal"}
            if not required.issubset(ep_set):
                ctx.logger.info(
                    "Skipping index for %s: missing required entrypoints; got: %s",
                    originated_contract,
                    sorted(list(ep_set))[:10],
                )
                return
        except Exception as e:
            ctx.logger.info(
                "Skipping index for %s due to entrypoint verification error: %s",
                originated_contract,
                e,
            )
            return

        try:
            exists = index_name in ctx.config.indexes
        except Exception:
            exists = False
        
        if not exists:
            try:
                from dipdup.database import get_connection
                async with get_connection() as conn:
                    result = await conn.fetchval(
                        "SELECT EXISTS(SELECT 1 FROM dipdup_index WHERE name = $1)",
                        index_name
                    )
                    exists = result if result else False
            except Exception:
                exists = False

        if not exists:
            try:
                await ctx.add_contract(
                    name=originated_contract,
                    address=originated_contract,
                    typename='registry',
                    kind='tezos',
                )
                await ctx.add_index(
                    name=index_name,
                    template='registry_dao',
                    values=dict(contract=originated_contract, datasource=f'tzkt_{network}'),
                    first_level=origination_level,
                )
            except Exception as e:
                ctx.logger.info('Skipping index creation for %s: %s', originated_contract, e)
    except Exception as e:
        ctx.logger.error(f"Error in on_factory_origination: {e}")
        ctx.logger.error(f"Handler received: {type(registry_origination)}")
        if hasattr(registry_origination, 'data'):
            ctx.logger.error(f"Data attributes: {dir(registry_origination.data)}")
        else:
            ctx.logger.error(f"Direct attributes: {dir(registry_origination)}")