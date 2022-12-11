from typing import Optional

from dipdup.models import OperationData, Origination, Transaction
from dipdup.context import HandlerContext

import registrydao.models as models

from registrydao.types.registry.parameter.call_custom import CallCustomParameter
from registrydao.types.registry.storage import RegistryStorage


async def on_call_custom(
    ctx: HandlerContext,
    call_custom: Transaction[CallCustomParameter, RegistryStorage],
) -> None:
    try:
        dao_address = call_custom.data.target_address
        dao = await models.DAO.get(address=dao_address).prefetch_related('governance_token')
        timestamp = call_custom.data.timestamp
        amount = call_custom.data.amount
        integer_amount = call_custom.data.amount
        decimal_amount = (call_custom.data.amount) / (10 ** 6)
        from_address = call_custom.data.sender_address
        hash = call_custom.data.hash

        await models.Transfer.get_or_create(
            timestamp=timestamp,
            amount=amount,
            integer_amount=integer_amount,
            decimal_amount=decimal_amount,
            from_address=from_address,
            dao=dao,
            hash=hash
        )
    except Exception as e:
        print("Error in on_call_custom: " + str(call_custom.data.target_address))
        print(e)