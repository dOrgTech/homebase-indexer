from asyncio import sleep
from datetime import datetime
from registrydao.utils.ctx import extract_network_from_ctx
from registrydao.constants import DIPDUP_METADATA_API, NETWORK_MAP
from registrydao.utils.http import fetch

from dipdup.context import HandlerContext
from dipdup.models import Origination

import registrydao.models as models
from registrydao.types.registry.storage import RegistryStorage

def find_in_json(key_to_compare: str, key_name: str, data):
    for i in data:
        if i[key_to_compare] == key_name:
            return i

async def wait_and_fetch_metadata(network: str, dao_address: str):
    fetched_metadata = await fetch(f'{DIPDUP_METADATA_API}/contract_metadata?contract={dao_address}&network={NETWORK_MAP[network]}')
    # https://metadata.dipdup.net/api/rest/contract_metadata?contract=KT1BxBvA6WBdYZsToVJDxNdxNJEi359UBYYu&network=mainnet
    
    while fetched_metadata == None:
        print(f'Metadata not yet indexed for DAO {dao_address}')
        await sleep(5)
        fetched_metadata = await fetch(f'{DIPDUP_METADATA_API}/contract_metadata?contract={dao_address}&network={NETWORK_MAP[network]}')

    return fetched_metadata
    

async def on_origination(
        ctx: HandlerContext,
        registry_origination: Origination[RegistryStorage],
) -> None:
    # try:
    network = extract_network_from_ctx(ctx)
    token_address = registry_origination.data.storage['governance_token']['address']
    token_id = registry_origination.data.storage['governance_token']['token_id']
    dao_address = registry_origination.data.originated_contract_address

    fetched_token_resp = (await fetch(
        f'https://api.{NETWORK_MAP[network]}.tzkt.io/v1/tokens?contract={token_address}&tokenId={token_id}'))

    if not fetched_token_resp:
        return

    fetched_token = fetched_token_resp[0]
    fetched_token_metadata = fetched_token['metadata']

    if('symbol' not in fetched_token_metadata):
        return

    fetched_metadata_arr = await wait_and_fetch_metadata(network, dao_address)
    print("fetched_metadata_arr", fetched_metadata_arr)
    fetched_metadata = fetched_metadata_arr["contract_metadata"][0]["metadata"]
    print("fetched_metadata", fetched_metadata)
    dao_type = fetched_metadata['template']
    print(dao_type, "dao_type")
    
    if 'discourse' in fetched_metadata and fetched_metadata['discourse']:
        discourse = fetched_metadata['discourse'].strip("/")
    else:
        discourse = "forum.tezosagora.org"

    type = await models.DAOType.get_or_create(name=dao_type)

    if 'firstLevel' in fetched_token:
        firstLevel = fetched_token["firstLevel"]
    else:
        firstLevel = -1

    if 'shouldPreferSymbol' in fetched_token:
        shouldPreferSymbol = fetched_token_metadata['shouldPreferSymbol']
    else:
        shouldPreferSymbol = True

    token = await models.Token.get_or_create(
        contract=token_address,
        network=network,
        level=firstLevel,
        timestamp=datetime.strptime(fetched_token["firstTime"], '%Y-%m-%dT%H:%M:%SZ'),
        token_id=token_id,
        symbol=fetched_token_metadata["symbol"],
        name=fetched_token_metadata["name"],
        decimals=fetched_token_metadata["decimals"],
        is_transferable=True,
        should_prefer_symbol=shouldPreferSymbol,
        supply=fetched_token["totalSupply"]
    )

    dao = await models.DAO.get_or_create(
        admin=registry_origination.data.storage['admin'],
        address=dao_address,
        frozen_token_id=registry_origination.data.storage['frozen_token_id'],
        guardian=registry_origination.data.storage['guardian'],
        # max_proposals=registry_origination.data.storage['max_proposals'],
        max_quorum_change=registry_origination.data.storage['config']['max_quorum_change'],
        max_quorum_threshold=registry_origination.data.storage['config']['max_quorum_threshold'],
        min_quorum_threshold=registry_origination.data.storage['config']['min_quorum_threshold'],
        period=registry_origination.data.storage['config']['period'],
        proposal_expired_level=registry_origination.data.storage['config']['proposal_expired_level'],
        proposal_flush_level=registry_origination.data.storage['config']['proposal_flush_level'],
        quorum_change=registry_origination.data.storage['config']['quorum_change'],
        fixed_proposal_fee_in_token=registry_origination.data.storage['config']['fixed_proposal_fee_in_token'],
        last_updated_cycle=registry_origination.data.storage['quorum_threshold_at_cycle']['last_updated_cycle'],
        quorum_threshold=round((int(registry_origination.data.storage['quorum_threshold_at_cycle']['quorum_threshold']) / 1000000) * int(fetched_token["totalSupply"])),
        staked=registry_origination.data.storage['quorum_threshold_at_cycle']['staked'],
        start_level=registry_origination.data.storage['start_level'],
        network=network,
        name=fetched_metadata['name'],
        description=fetched_metadata['description'],
        governance_token=token[0],
        type=type[0],
        discourse=discourse
    )
        
        # fetched_extra = registry_origination.data.storage['extra']

        # if dao_type == 'registry':
        #     await models.RegistryExtra.get_or_create(
        #         registry=fetched_extra['registry'],
        #         registry_affected=fetched_extra['registry_affected'],
        #         frozen_extra_value=fetched_extra['frozen_extra_value'],
        #         frozen_scale_value=fetched_extra['frozen_scale_value'],
        #         slash_division_value=fetched_extra['slash_division_value'],
        #         min_xtz_amount=fetched_extra['min_xtz_amount'],
        #         max_xtz_amount=fetched_extra['max_xtz_amount'],
        #         slash_scale_value=fetched_extra['slash_scale_value'],
        #         dao=dao[0]
        #     )
        # else:
        #     await models.TreasuryExtra.get_or_create(
        #         frozen_extra_value=fetched_extra['frozen_extra_value'],
        #         frozen_scale_value=fetched_extra['frozen_scale_value'],
        #         slash_division_value=fetched_extra['slash_division_value'],
        #         min_xtz_amount=fetched_extra['min_xtz_amount'],
        #         max_xtz_amount=fetched_extra['max_xtz_amount'],
        #         slash_scale_value=fetched_extra['slash_scale_value'],
        #         dao=dao[0]
        #     )
    # except Exception as e:
        # print("Error in Origination Handler: " + str(registry_origination.data.originated_contract_address))
        # print(e)
