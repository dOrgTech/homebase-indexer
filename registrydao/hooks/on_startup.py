from dipdup.context import HookContext
from registrydao.utils.http import fetch
from registrydao.constants import NETWORK_MAP
from typing import cast


def get_factory_address_from_config(ctx: HookContext, network: str) -> str:
    """Get factory contract address from config for a given network"""
    contract_name = f'registry_{network}'
    if contract_name in ctx.config.contracts:
        contract_config = ctx.config.contracts[contract_name]
        if hasattr(contract_config, 'address'):
            return contract_config.address
    raise ValueError(f"Factory contract not found in config for network: {network}")


async def get_registry_code_hash(ctx: HookContext, network: str) -> str:
    """Get the code hash of the registry contract"""
    registry_address = get_factory_address_from_config(ctx, network)
    
    contract_info = await fetch(
        f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/contracts/{registry_address}"
    )
    return contract_info['codeHash']


async def get_historical_daos(ctx: HookContext, network: str, code_hash: str, first_level: int) -> list:
    """Query TzKT for all originations with the same code hash"""
    all_daos = []
    offset = 0
    limit = 1000
    
    ctx.logger.info(f"Fetching historical DAOs for {network} from level {first_level}...")
    
    while True:
        url = (
            f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/operations/originations"
            f"?codeHash.eq={code_hash}"
            f"&level.ge={first_level}"
            f"&limit={limit}"
            f"&offset={offset}"
            f"&status=applied"
            f"&sort=level"
        )
        
        try:
            originations = await fetch(url)
            if not originations or len(originations) == 0:
                break
                
            all_daos.extend(originations)
            ctx.logger.info(f"  Fetched {len(originations)} originations (total: {len(all_daos)})")
            offset += limit
            
            if len(originations) < limit:
                break
                
            # Small delay to avoid rate limiting
            import asyncio
            await asyncio.sleep(0.5)
        except Exception as e:
            ctx.logger.error(f"Error fetching originations: {e}")
            break
    
    return all_daos


async def verify_dao_entrypoints(network: str, dao_address: str) -> bool:
    """Verify that a DAO has the required entrypoints"""
    try:
        eps = await fetch(
            f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/contracts/{dao_address}/entrypoints"
        )
        if isinstance(eps, list):
            ep_set = set(ep.get('name', ep) if isinstance(ep, dict) else ep for ep in eps)
        else:
            ep_set = set()
        required = {"propose", "vote", "flush", "freeze", "unfreeze", "drop_proposal"}
        return required.issubset(ep_set)
    except Exception:
        return False


def extract_network_configs(ctx: HookContext):
    """Extract factory contract addresses, first levels, and datasources from dipdup.yml config"""
    networks_config = {}
    
    for contract_name, contract_config in ctx.config.contracts.items():
        if contract_name.startswith('registry_'):
            network = contract_name.replace('registry_', '')
            if hasattr(contract_config, 'address'):
                networks_config[network] = {
                    'factory_address': contract_config.address,
                    'contract_name': contract_name
                }
    
    for index_name, index_config in ctx.config.indexes.items():
        if index_name.startswith('factory_'):
            network = index_name.replace('factory_', '')
            if network in networks_config:
                if hasattr(index_config, 'first_level'):
                    networks_config[network]['first_level'] = index_config.first_level
                if hasattr(index_config, 'datasource'):
                    datasource = index_config.datasource
                    if hasattr(datasource, 'name'):
                        networks_config[network]['datasource'] = datasource.name
                    elif isinstance(datasource, str):
                        networks_config[network]['datasource'] = datasource
                    else:
                        networks_config[network]['datasource'] = f'tzkt_{network}'
    
    return networks_config


async def on_startup(ctx: HookContext) -> None:
    """Startup hook to discover and index historical DAOs"""
    try:
        print("=" * 60)
        print("ON_STARTUP HOOK CALLED")
        print("=" * 60)
        ctx.logger.info("=" * 60)
        ctx.logger.info("ON_STARTUP HOOK CALLED - Starting historical DAO discovery...")
        ctx.logger.info("=" * 60)
        
        networks_config = extract_network_configs(ctx)
        
        for network, config in networks_config.items():
            if 'first_level' in config and 'datasource' in config:
                await process_network(
                    ctx,
                    network,
                    config['first_level'],
                    config['factory_address'],
                    config['datasource']
                )
        
        ctx.logger.info("Historical DAO discovery completed")
    except Exception as e:
        ctx.logger.error(f"Error in on_startup: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())


async def process_network(
    ctx: HookContext,
    network: str,
    first_level: int,
    registry_address: str,
    datasource_name: str
) -> None:
    """Process historical DAOs for a specific network"""
    try:
        ctx.logger.info(f"Processing {network} network...")
        
        # Get registry code hash
        code_hash = await get_registry_code_hash(ctx, network)
        ctx.logger.info(f"Registry code hash: {code_hash}")
        
        # Get all historical DAOs
        historical_daos = await get_historical_daos(ctx, network, code_hash, first_level)
        ctx.logger.info(f"Found {len(historical_daos)} total originations")
        
        # Filter and create indexes for valid DAOs
        valid_count = 0
        skipped_count = 0
        
        # Factory contract address - skip this as it's already in config
        factory_address = registry_address
        
        for dao_data in historical_daos:
            dao_address = dao_data['originatedContract']['address']
            origination_level = dao_data['level']
            index_name = f'registry_dao_{dao_address}'
            
            # Skip factory contracts (already indexed)
            if dao_address == factory_address:
                ctx.logger.info(f"  ⊙ Skipping factory contract {dao_address} (network: {network}, factory: {factory_address})")
                skipped_count += 1
                continue
            
            ctx.logger.debug(f"  Processing DAO {dao_address} (network: {network}, factory: {factory_address})")
            
            # Verify entrypoints
            if not await verify_dao_entrypoints(network, dao_address):
                ctx.logger.info(f"  ✗ {dao_address} - missing required entrypoints")
                skipped_count += 1
                continue
            
            # Check if index already exists
            exists = False
            try:
                exists = index_name in ctx.config.indexes
            except Exception:
                pass
            
            if not exists:
                try:
                    from dipdup.database import get_connection
                    conn = await get_connection()
                    try:
                        result = await conn.fetchval(
                            "SELECT EXISTS(SELECT 1 FROM dipdup_index WHERE name = $1)",
                            index_name
                        )
                        exists = result if result else False
                    finally:
                        await conn.close()
                except Exception:
                    exists = False
            
            if not exists:
                try:
                    # Find the correct contract name to use
                    # 1. Check if contract is in config (use config name)
                    contract_name = None
                    for contract_alias, contract_config in ctx.config.contracts.items():
                        if hasattr(contract_config, 'address') and contract_config.address == dao_address:
                            contract_name = contract_alias
                            ctx.logger.info(f"  Found contract {contract_name} in config for {dao_address}")
                            break
                    
                    # 2. If not in config, check database
                    if not contract_name:
                        try:
                            from dipdup.database import get_connection
                            conn = await get_connection()
                            try:
                                result = await conn.fetchrow(
                                    "SELECT name FROM dipdup_contract WHERE address = $1",
                                    dao_address
                                )
                                if result:
                                    contract_name = result['name']
                                    ctx.logger.info(f"  Found contract {contract_name} in database for {dao_address}")
                            finally:
                                await conn.close()
                        except Exception:
                            pass
                    
                    # 3. If still not found, add contract first, then use its name
                    if not contract_name:
                        contract_name = dao_address
                        try:
                            await ctx.add_contract(
                                name=contract_name,
                                address=dao_address,
                                typename='registry',
                                kind='tezos',
                            )
                            ctx.logger.debug(f"  Added contract {contract_name} for {dao_address}")
                        except Exception as contract_error:
                            # If contract already exists, try to find its name
                            error_str = str(contract_error)
                            if 'already in use' in error_str:
                                # Contract exists but we don't know the name - this shouldn't happen
                                # but let's try to find it
                                try:
                                    from dipdup.database import get_connection
                                    conn = await get_connection()
                                    try:
                                        result = await conn.fetchrow(
                                            "SELECT name FROM dipdup_contract WHERE address = $1",
                                            dao_address
                                        )
                                        if result:
                                            contract_name = result['name']
                                        else:
                                            # Contract address conflict but not in DB/config
                                            # This is likely a race condition or internal DipDup state
                                            ctx.logger.warning(f"  Contract {dao_address} address conflict but not found in DB/config")
                                            raise contract_error
                                    finally:
                                        await conn.close()
                                except Exception:
                                    raise contract_error
                            else:
                                raise
                    
                    # Add index with the contract name
                    await ctx.add_index(
                        name=index_name,
                        template='registry_dao',
                        values=dict(contract=contract_name, datasource=datasource_name),
                        first_level=origination_level,
                    )
                    
                    ctx.logger.info(f"  ✓ Created index for {dao_address} at level {origination_level}")
                    valid_count += 1
                except Exception as e:
                    ctx.logger.warning(f"  ✗ Failed to create index for {dao_address}: {e}")
                    import traceback
                    ctx.logger.debug(traceback.format_exc())
                    skipped_count += 1
            else:
                ctx.logger.debug(f"  ⊙ Index already exists for {dao_address}")
        
        ctx.logger.info(f"{network}: Created {valid_count} indexes, skipped {skipped_count}")
        
    except Exception as e:
        ctx.logger.error(f"Error processing {network}: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())




