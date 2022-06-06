from dipdup.context import HandlerContext


def extract_network_from_ctx(ctx: HandlerContext) -> str:
    datasource_url = ctx.datasource._http._url
    
    if 'mainnet' in datasource_url:
        return 'mainnet'

    if 'ithacanet' in datasource_url:
        return 'ithacanet'

    raise RuntimeError('Could not extract network from handler context')