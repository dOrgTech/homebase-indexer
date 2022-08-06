from dipdup.context import HandlerContext


def extract_network_from_ctx(ctx: HandlerContext) -> str:
    datasource_url = ctx.datasource._http._url
    print("datasource_url: ", datasource_url);
    
    if 'mainnet' in datasource_url:
        return 'mainnet'

    if 'jakartanet' in datasource_url:
        return 'jakartanet'
    
    if 'mainnet' or 'jakartanet' not in datasource_url:
        return 'devnet'

    raise RuntimeError('Could not extract network from handler context')