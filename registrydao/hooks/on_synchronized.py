from dipdup.context import HookContext
from registrydao.hooks.on_startup import process_network, extract_network_configs


async def on_synchronized(
    ctx: HookContext,
) -> None:
    try:
        await ctx.execute_sql('on_synchronized')
        
        ctx.logger.info("on_synchronized hook called - checking for historical DAOs")
        
        dao_index_count = 0
        try:
            for index_name in ctx.config.indexes.keys():
                if index_name.startswith('registry_dao_'):
                    dao_index_count += 1
        except Exception:
            pass
        
        networks_config = extract_network_configs(ctx)
        factory_addresses = {net: config['factory_address'] for net, config in networks_config.items()}
        
        actual_dao_count = 0
        try:
            import registrydao.models as models
            if factory_addresses:
                addresses_list = list(factory_addresses.values())
                total_count = await models.DAO.all().count()
                factory_count = await models.DAO.filter(address__in=addresses_list).count()
                actual_dao_count = total_count - factory_count
        except Exception as e:
            ctx.logger.warning(f"Could not check actual DAO count: {e}")
            actual_dao_count = 0
        
        ctx.logger.info(f"Found {dao_index_count} DAO indexes in config, {actual_dao_count} actual DAOs in database")
        
        if dao_index_count == 0 or actual_dao_count < 10:
            ctx.logger.info("Insufficient DAOs found - discovering historical DAOs...")
            
            for network, config in networks_config.items():
                if 'first_level' in config and 'datasource' in config:
                    await process_network(
                        ctx,
                        network,
                        config['first_level'],
                        config['factory_address'],
                        config['datasource']
                    )
        else:
            ctx.logger.info(f"Found {dao_index_count} DAO indexes and {actual_dao_count} DAOs - skipping historical discovery")
    except Exception as e:
        ctx.logger.error(f"Error in on_synchronized: {e}")
        import traceback
        ctx.logger.error(traceback.format_exc())
