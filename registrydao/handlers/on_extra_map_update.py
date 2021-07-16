from dipdup.context import HandlerContext
from dipdup.models import BigMapDiff

import registrydao.models as models
from registrydao.types.registry.big_map.extra_key import ExtraKey
from registrydao.types.registry.big_map.extra_value import ExtraValue


async def on_extra_map_update(
    ctx: HandlerContext,
    extra: BigMapDiff[ExtraKey, ExtraValue],
) -> None:
    dao_address = extra.data.contract_address
    dao = await models.DAO.get(address=dao_address).prefetch_related("type")

    if dao.type.name == 'treasury':
        dao_extra = await models.TreasuryExtra.get(dao=dao)
    elif dao.type.name == 'registry':
        dao_extra = await models.RegistryExtra.get(dao=dao)
    
    if extra.data.key == 'frozen_extra_value':
       dao_extra.frozen_extra_value = extra.data.value
    if extra.data.key == 'frozen_scale_value':
       dao_extra.frozen_scale_value = extra.data.value
    if extra.data.key == 'slash_division_value':
       dao_extra.slash_division_value = extra.data.value
    if extra.data.key == 'min_xtz_amount':
       dao_extra.min_xtz_amount = extra.data.value
    if extra.data.key == 'max_xtz_amount':
       dao_extra.max_xtz_amount = extra.data.value
    if extra.data.key == 'slash_scale_value':
       dao_extra.slash_scale_value = extra.data.value
    if extra.data.key == 'registry':
       dao_extra.registry = extra.data.value
    if extra.data.key == 'registry_affected':
       dao_extra.registry_affected = extra.data.value

    await dao_extra.save()