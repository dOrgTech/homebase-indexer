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
    symbol= fields.CharField(25)
    name = fields.CharField(25)
    decimals = fields.IntField()
    is_transferable = fields.BooleanField()
    should_prefer_symbol = fields.BooleanField()
    supply = fields.CharField(36)
    daos: fields.ReverseRelation["DAO"]

    class Meta:
        table = 'tokens'
        unique_together=(("contract", "token_id"), )

class DAO(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(36, unique=True)
    frozen_token_id = fields.IntField()
    governance_token: fields.ForeignKeyRelation[Token] = fields.ForeignKeyField(
        "models.Token", related_name="daos"
    )
    guardian = fields.CharField(36)
    ledger: fields.ReverseRelation["Ledger"]
    proposals: fields.ReverseRelation["Proposal"]
    max_proposals = fields.CharField(255)
    max_quorum_change = fields.CharField(255)
    max_quorum_threshold = fields.CharField(255)
    max_votes = fields.CharField(255)
    min_quorum_threshold = fields.CharField(255)
    period = fields.CharField(255)
    proposal_expired_time = fields.CharField(255)
    proposal_flush_time = fields.CharField(255)
    quorum_change = fields.CharField(255)
    last_updated_cycle = fields.CharField(255)
    quorum_threshold = fields.CharField(255)
    staked = fields.CharField(255)
    start_time = fields.DatetimeField()
    type: fields.ForeignKeyRelation[DAOType] = fields.ForeignKeyField(
        "models.DAOType", related_name="daos"
    )
    network = fields.CharField(36)

    class Meta:
        table = 'daos' 

class RegistryExtra(Model):
    id = fields.IntField(pk=True)
    dao: fields.ForeignKeyRelation[DAOType] = fields.ForeignKeyField(
        "models.DAOType"
    )
    registry = fields.CharField(2500)
    registryAffected = fields.CharField(2500)
    frozen_extra_value = fields.CharField(255)
    frozen_scale_value = fields.CharField(255)
    slash_division_value = fields.CharField(255)
    min_xtz = fields.CharField(255)
    max_xtz = fields.CharField(255)
    slash_scale_value = fields.CharField(255)

    class Meta:
        table = 'registry_extra' 

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
    balance = fields.CharField(36)
    dao: fields.ForeignKeyRelation[DAO] = fields.ForeignKeyField(
        "models.DAO", related_name="ledger"
    )
    holder: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="ledger"
    )

    class Meta:
        table = 'ledger'

class Proposal(Model):
    id = fields.IntField(pk=True)
    dao: fields.ForeignKeyRelation[DAO] = fields.ForeignKeyField(
        "models.DAO", related_name="proposals"
    )
    upvotes = fields.CharField(36)
    downvotes = fields.CharField(36)
    start_date = fields.DatetimeField()
    metadata = fields.CharField(512)
    proposer: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="proposals"
    )
    voting_stage_num: fields.CharField(50)
    proposer_frozen_token: fields.CharField(50)
    quorum_threshold: fields.CharField(50)
    votes: fields.ReverseRelation["Vote"]

    class Meta:
        table = 'proposals' 


class Vote(Model):
    id = fields.IntField(pk=True)
    proposal: fields.ForeignKeyRelation[Proposal] = fields.ForeignKeyField(
        "models.Proposal", related_name="votes"
    )
    amount = fields.CharField(36)
    support = fields.BooleanField()
    voter: fields.ForeignKeyRelation[Holder] = fields.ForeignKeyField(
        "models.Holder", related_name="votes"
    )

    class Meta:
        table = 'votes'
