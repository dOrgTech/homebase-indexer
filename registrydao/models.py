from enum import unique
from tortoise import Model, fields


class DAOType(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(25, unique=True)
    daos: fields.ReverseRelation["DAO"]

    class Meta:
        table = 'dao_types'


class Token(Model):
    id = fields.IntField(pk=True)
    contract = fields.CharField(36)
    network = fields.CharField(25)
    level = fields.IntField()
    timestamp = fields.DatetimeField()
    token_id = fields.IntField()
    symbol = fields.CharField(25)
    name = fields.CharField(25)
    decimals = fields.IntField()
    is_transferable = fields.BooleanField()
    should_prefer_symbol = fields.BooleanField()
    supply = fields.DecimalField(54, 18)
    daos: fields.ReverseRelation["DAO"]
    transfers: fields.ReverseRelation["Transfer"]

    class Meta:
        table = 'tokens'
        unique_together = (("contract", "token_id"),)


class DAO(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(36, unique=True)
    frozen_token_id = fields.IntField()
    governance_token: fields.ForeignKeyRelation[Token] = fields.ForeignKeyField(
        "models.Token", related_name="daos"
    )
    admin = fields.CharField(36)
    guardian = fields.CharField(36)
    ledger: fields.ReverseRelation["Ledger"]
    transfers: fields.ReverseRelation["Transfer"]
    proposals: fields.ReverseRelation["Proposal"]
    max_proposals = fields.CharField(255)
    max_quorum_change = fields.CharField(255)
    max_quorum_threshold = fields.DecimalField(54, 18)
    min_quorum_threshold = fields.DecimalField(54, 18)
    period = fields.CharField(255)
    proposal_expired_level = fields.IntField()
    proposal_flush_level = fields.IntField()
    quorum_change = fields.CharField(255)
    last_updated_cycle = fields.CharField(255)
    quorum_threshold = fields.DecimalField(54, 18)
    staked = fields.DecimalField(54, 18)
    start_level = fields.IntField()
    name = fields.CharField(255)
    description = fields.CharField(2500)
    discourse = fields.CharField(2500)
    type: fields.ForeignKeyRelation[DAOType] = fields.ForeignKeyField(
        "models.DAOType", related_name="daos"
    )
    network = fields.CharField(36)

    class Meta:
        table = 'daos'


class RegistryExtra(Model):
    id = fields.IntField(pk=True)
    dao: fields.ForeignKeyRelation[DAOType] = fields.ForeignKeyField(
        "models.DAO"
    )
    registry = fields.CharField(2500)
    registry_affected = fields.CharField(2500)
    frozen_extra_value = fields.CharField(255)
    frozen_scale_value = fields.CharField(255)
    slash_division_value = fields.CharField(255)
    min_xtz_amount = fields.CharField(255)
    max_xtz_amount = fields.CharField(255)
    slash_scale_value = fields.CharField(255)

    class Meta:
        table = 'registry_extra'

class TreasuryExtra(Model):
    id = fields.IntField(pk=True)
    dao: fields.ForeignKeyRelation[DAOType] = fields.ForeignKeyField(
        "models.DAO"
    )
    frozen_extra_value = fields.CharField(255)
    frozen_scale_value = fields.CharField(255)
    slash_division_value = fields.CharField(255)
    min_xtz_amount = fields.CharField(255)
    max_xtz_amount = fields.CharField(255)
    slash_scale_value = fields.CharField(255)

    class Meta:
        table = 'treasury_extra'


class Holder(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(36, unique=True)
    ledger: fields.ReverseRelation["Ledger"]
    proposals: fields.ReverseRelation["Proposal"]
    votes: fields.ReverseRelation["Vote"]

    class Meta:
        table = 'holders'


class Ledger(Model):
    id = fields.IntField(pk=True)
    current_stage_num = fields.CharField(36)
    current_unstaked = fields.DecimalField(54, 18)
    past_unstaked = fields.DecimalField(54, 18)
    staked = fields.DecimalField(54, 18)
    dao: fields.ForeignKeyRelation[DAO] = fields.ForeignKeyField(
        "models.DAO", related_name="ledger"
    )
    holder: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="ledger"
    )

    class Meta:
        table = 'ledger'
        unique_together = (("dao", "holder"),)

class ProposalStatus(Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(36)
    status_updates = fields.ReverseRelation["ProposalStatusUpdates"]

    class Meta:
        table = 'proposal_statuses'


class Proposal(Model):
    id = fields.IntField(pk=True)
    dao: fields.ForeignKeyRelation[DAO] = fields.ForeignKeyField(
        "models.DAO", related_name="proposals"
    )
    hash=fields.CharField(128)
    key=fields.CharField(128)
    upvotes = fields.DecimalField(54, 18)
    downvotes = fields.DecimalField(54, 18)
    start_level = fields.IntField()
    start_date = fields.DatetimeField()
    metadata = fields.CharField(10000)
    proposer: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="proposals"
    )
    voting_stage_num=fields.CharField(50)
    proposer_frozen_token=fields.CharField(50)
    quorum_threshold=fields.DecimalField(54, 18)
    votes: fields.ReverseRelation["Vote"]
    status_updates: fields.ReverseRelation["ProposalStatusUpdates"]

    class Meta:
        table = 'proposals'


class Vote(Model):
    id = fields.IntField(pk=True)
    proposal: fields.ForeignKeyRelation[Proposal] = fields.ForeignKeyField(
        "models.Proposal", related_name="votes"
    )
    amount = fields.DecimalField(54, 18)
    support = fields.BooleanField()
    voter: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="votes"
    )

    class Meta:
        table = 'votes'

class Transfer(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField()
    dao: fields.ForeignKeyRelation[DAO] = fields.ForeignKeyField(
        "models.DAO", related_name="transfers"
    )
    amount = fields.CharField(128)
    integer_amount = fields.BigIntField()
    decimal_amount = fields.DecimalField(54, 18)
    from_address = fields.CharField(36)
    hash = fields.CharField(128)

class ProposalStatusUpdates(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField()
    level = fields.IntField()
    status: fields.ForeignKeyRelation[ProposalStatus] = fields.ForeignKeyField(
        "models.ProposalStatus", related_name="status_updates"
    )
    proposal: fields.ForeignKeyRelation[Proposal] = fields.ForeignKeyField(
        "models.Proposal", related_name="status_updates"
    )

    class Meta:
        table = 'status_updates'
