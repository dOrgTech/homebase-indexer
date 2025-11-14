# Re-export storage as tezos_storage for DipDup v7 compatibility
from registrydao.types.registry.storage import (
    Config,
    Key,
    Delegate,
    Lambdas,
    ExtraModel,
    FreezeHistory,
    GovernanceToken,
    Key1,
    MapItem,
    OngoingProposalsDlistItem,
    Proposals,
    QuorumThresholdAtCycle,
    Key2,
    StakedVote,
    RegistryStorage
)

__all__ = [
    'Config',
    'Key',
    'Delegate',
    'Lambdas',
    'ExtraModel',
    'FreezeHistory',
    'GovernanceToken',
    'Key1',
    'MapItem',
    'OngoingProposalsDlistItem',
    'Proposals',
    'QuorumThresholdAtCycle',
    'Key2',
    'StakedVote',
    'RegistryStorage'
]

