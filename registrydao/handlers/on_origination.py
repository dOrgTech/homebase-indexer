from datetime import datetime
from registrydao.constants import BETTER_CALL_DEV_API
from registrydao.utils.http import fetch

from dipdup.context import HandlerContext
from dipdup.models import Origination

import registrydao.models as models
from registrydao.types.registry.storage import RegistryStorage

def find_in_json(key_to_compare: str, key_name: str, data):
    for i in data:
        if i[key_to_compare] == key_name:
            return i


async def on_origination(
        ctx: HandlerContext,
        registry_origination: Origination[RegistryStorage],
) -> None:
    token_address = registry_origination.data.storage['governance_token']['address']
    token_id = registry_origination.data.storage['governance_token']['token_id']
    dao_address = registry_origination.data.originated_contract_address

    fetched_token = (await fetch(
        f'{BETTER_CALL_DEV_API}/tokens/florencenet/metadata?contract={token_address}&token_id={token_id}'))[0]

    network = fetched_token["network"]

    fetched_metadata = await fetch(f'{BETTER_CALL_DEV_API}/account/{network}/{dao_address}/metadata')

    dao_type = fetched_metadata['extras']['template']

    type = await models.DAOType.get_or_create(name=dao_type)

    token = await models.Token.get_or_create(
        contract=fetched_token["contract"],
        network=network,
        level=fetched_token["level"],
        timestamp=datetime.strptime(fetched_token["timestamp"], '%Y-%m-%dT%H:%M:%SZ'),
        token_id=fetched_token["token_id"],
        symbol=fetched_token["symbol"],
        name=fetched_token["name"],
        decimals=fetched_token["decimals"],
        is_transferable=fetched_token["is_transferable"],
        should_prefer_symbol=fetched_token["should_prefer_symbol"],
        supply=fetched_token["supply"]
    )

    dao = await models.DAO.get_or_create(
        address=dao_address,
        frozen_token_id=registry_origination.data.storage['frozen_token_id'],
        guardian=registry_origination.data.storage['guardian'],
        max_proposals=registry_origination.data.storage['max_proposals'],
        max_quorum_change=registry_origination.data.storage['max_quorum_change'],
        max_quorum_threshold=registry_origination.data.storage['max_quorum_threshold'],
        max_votes=registry_origination.data.storage['max_votes'],
        min_quorum_threshold=registry_origination.data.storage['min_quorum_threshold'],
        period=registry_origination.data.storage['period'],
        proposal_expired_time=registry_origination.data.storage['proposal_expired_time'],
        proposal_flush_time=registry_origination.data.storage['proposal_flush_time'],
        quorum_change=registry_origination.data.storage['quorum_change'],
        last_updated_cycle=registry_origination.data.storage['quorum_threshold_at_cycle']['last_updated_cycle'],
        quorum_threshold=registry_origination.data.storage['quorum_threshold_at_cycle']['quorum_threshold'],
        staked=registry_origination.data.storage['quorum_threshold_at_cycle']['staked'],
        start_time=datetime.strptime(registry_origination.data.storage['start_time'], '%Y-%m-%dT%H:%M:%SZ'),
        network=network,
        name=fetched_metadata['name'],
        description=fetched_metadata['description'],
        governance_token=token[0],
        type=type[0]
    )

    extra_map_number = registry_origination.data.storage['extra']
    fetched_extra = await fetch(f'https://api.{network}.tzkt.io/v1/bigmaps/{extra_map_number}/keys')

    if dao_type == 'registry':
        await models.RegistryExtra.create(
            registry=find_in_json('key', 'registry', fetched_extra)['value'],
            registry_affected=find_in_json('key', 'registry_affected', fetched_extra)['value'],
            frozen_extra_value=find_in_json('key', 'frozen_extra_value', fetched_extra)['value'],
            frozen_scale_value=find_in_json('key', 'frozen_scale_value', fetched_extra)['value'],
            slash_division_value=find_in_json('key', 'slash_division_value', fetched_extra)['value'],
            min_xtz_amount=find_in_json('key', 'min_xtz_amount', fetched_extra)['value'],
            max_xtz_amount=find_in_json('key', 'max_xtz_amount', fetched_extra)['value'],
            slash_scale_value=find_in_json('key', 'slash_scale_value', fetched_extra)['value'],
            dao=dao[0]
        )
    else:
        await models.TreasuryExtra.create(
            frozen_extra_value=find_in_json('key', 'frozen_extra_value', fetched_extra)['value'],
            frozen_scale_value=find_in_json('key', 'frozen_scale_value', fetched_extra)['value'],
            slash_division_value=find_in_json('key', 'slash_division_value', fetched_extra)['value'],
            min_xtz_amount=find_in_json('key', 'min_xtz_amount', fetched_extra)['value'],
            max_xtz_amount=find_in_json('key', 'max_xtz_amount', fetched_extra)['value'],
            slash_scale_value=find_in_json('key', 'slash_scale_value', fetched_extra)['value'],
            dao=dao[0]
        )

    
