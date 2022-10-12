from typing import Dict, List
import registrydao.models as models

async def update_extra(dao_address: str, storage: Dict):

    for key in storage:
        dao = await models.DAO.get(address=dao_address).prefetch_related("type")

        if dao.type.name == 'treasury':
            dao_extra = await models.TreasuryExtra.get(dao=dao)
        elif dao.type.name == 'registry':
            dao_extra = await models.RegistryExtra.get(dao=dao)
        elif dao.type.name == 'lambda':
            dao_extra = await models.LambdaExtra.get(dao=dao)
        
        diff_key = key
        diff_value = storage[key]
        
        if diff_key == 'frozen_extra_value':
            dao_extra.frozen_extra_value = diff_value
        if diff_key == 'frozen_scale_value':
            dao_extra.frozen_scale_value = diff_value
        if diff_key == 'slash_division_value':
            dao_extra.slash_division_value = diff_value
        if diff_key == 'min_xtz_amount':
            dao_extra.min_xtz_amount = diff_value
        if diff_key == 'max_xtz_amount':
            dao_extra.max_xtz_amount = diff_value
        if diff_key == 'slash_scale_value':
            dao_extra.slash_scale_value = diff_value
        if diff_key == 'registry':
            dao_extra.registry = diff_value
        if diff_key == 'registry_affected':
            dao_extra.registry_affected = diff_value

        await dao_extra.save()