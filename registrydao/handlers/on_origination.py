from dipdup.models import OperationData, Transaction, Origination, BigMapDiff, BigMapData, BigMapAction
from dipdup.context import HandlerContext, RollbackHandlerContext
from datetime import datetime
from typing import Optional
import aiohttp


import registrydao.models as models

from registrydao.types.registry.storage import RegistryStorage

async def fetch(url: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        json_resp = await resp.json()
        return json_resp

async def on_origination(
    ctx: HandlerContext,
    registry_origination: Origination[RegistryStorage],
) -> None:

    token_address = registry_origination.data.storage['governance_token']['address']
    token_id = registry_origination.data.storage['governance_token']['token_id']

    fetched_token = (await fetch(f'https://api.better-call.dev/v1/tokens/florencenet/metadata?contract={token_address}&token_id={token_id}'))[0]
    print(fetched_token)

    type = await models.DAOType.get_or_none(name="registry")

    if type == None:
        type = await models.DAOType.create(name="registry")

    await type.save()

    token = models.Token(
        contract=fetched_token["contract"],
        network=fetched_token["network"],
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

    await token.save()

    dao = models.DAO(
        address=registry_origination.data.originated_contract_address,
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
        network=fetched_token["network"],
        governance_token=token,
        type=type
    )

    await dao.save()

    print(registry_origination)