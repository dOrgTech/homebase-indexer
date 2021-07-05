from typing import List
from tortoise import Model, fields


class DAO(Model):
    address = fields.CharField(36, pk=True)

class Token(Model):
    contract = fields.CharField(36, pk=True)
    network = fields.CharField(25)
    level = fields.IntField()
    token_id = fields.IntField()
    symbol = fields.CharField(25)
    name = fields.CharField(50)
    decimals = fields.IntField()
    icon = fields.CharField(255)
    supply: fields.CharField(50)
    transfered = fields.IntField()

    class Meta:
        table = 'tokens'

class TokenBalance(Model):
    id = fields.IntField(pk=True)
    holder_id = fields.ForeignKeyField('models.Holder', 'token_balances')
    token_id = fields.ForeignKeyField('models.Token', 'token_balances')
    balance = fields.CharField(50)

    class Meta:
        table = 'token_balances'

class Holder(Model):
    address = fields.CharField(36, pk=True)

class Proposal(Model):
    id = fields.IntField(pk=True)
    dao = fields.ForeignKeyField('models.DAO', 'proposals')
    upvotes = fields.IntField(default=0)
    downvotes = fields.IntField(default=0)
    start_date = fields.DatetimeField()
    metadata = fields.CharField(512)
    proposer = fields.ForeignKeyField('models.Holder', 'proposals')
    voting_stage_num: fields.CharField(50)
    proposer_frozen_token: fields.CharField(50)
    quorum_threshold: fields.CharField(50)

    class Meta:
        table = 'proposals' 


class Vote(Model):
    id = fields.IntField(pk=True)
    proposal = fields.ForeignKeyField('models.Proposal', 'votes')
    amount = fields.IntField()
    support = fields.BooleanField()
    voter = fields.ForeignKeyField('models.Holder', 'votes')

    class Meta:
        table = 'votes'
