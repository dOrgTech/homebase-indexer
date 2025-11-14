#!/usr/bin/env python3
"""
Generate static index entries for historical DAOs that weren't caught by similar_to pattern.
This script queries TzKT API for all originations with the same code hash as the registry contract.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from registrydao.utils.http import fetch
from registrydao.constants import NETWORK_MAP


async def get_registry_code_hash(network: str) -> str:
    """Get the code hash of the registry contract"""
    registry_address = {
        'mainnet': 'KT1MFxwTan4ptw6PSc3KK6e1xfzMrCb382tw',
        'ghostnet': 'KT1QZtF8vVUvZYRxttRwgftc4EaQHZWgzXNp'
    }[network]
    
    contract_info = await fetch(
        f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/contracts/{registry_address}"
    )
    return contract_info['codeHash']


async def get_historical_daos(network: str, code_hash: str, first_level: int) -> list:
    """Query TzKT for all originations with the same code hash"""
    all_daos = []
    offset = 0
    limit = 1000
    
    print(f"Fetching historical DAOs for {network} from level {first_level}...")
    
    while True:
        url = (
            f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/operations/originations"
            f"?codeHash.eq={code_hash}"
            f"&level.ge={first_level}"
            f"&limit={limit}"
            f"&offset={offset}"
            f"&status=applied"
            f"&sort=level"
        )
        
        try:
            originations = await fetch(url)
            if not originations or len(originations) == 0:
                break
                
            all_daos.extend(originations)
            print(f"  Fetched {len(originations)} originations (total: {len(all_daos)})")
            offset += limit
            
            if len(originations) < limit:
                break
                
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error fetching originations: {e}")
            break
    
    return all_daos


async def verify_dao_entrypoints(network: str, dao_address: str) -> bool:
    """Verify that a DAO has the required entrypoints"""
    try:
        eps = await fetch(
            f"https://api.{NETWORK_MAP[network]}.tzkt.io/v1/contracts/{dao_address}/entrypoints"
        )
        if isinstance(eps, list):
            ep_set = set(ep.get('name', ep) if isinstance(ep, dict) else ep for ep in eps)
        else:
            ep_set = set()
        required = {"propose", "vote", "flush", "freeze", "unfreeze", "drop_proposal"}
        return required.issubset(ep_set)
    except Exception:
        return False


async def generate_indexes_for_network(network: str, first_level: int, contract_name: str, datasource_name: str):
    """Generate index entries for a specific network"""
    print(f"\n=== Processing {network} network ===")
    
    # Get registry code hash
    code_hash = await get_registry_code_hash(network)
    print(f"Registry code hash: {code_hash}")
    
    # Get all historical DAOs
    historical_daos = await get_historical_daos(network, code_hash, first_level)
    print(f"\nFound {len(historical_daos)} total originations")
    
    # Filter DAOs that have required entrypoints
    valid_daos = []
    for dao_data in historical_daos:
        dao_address = dao_data['originatedContract']['address']
        if await verify_dao_entrypoints(network, dao_address):
            valid_daos.append(dao_data)
            print(f"  ✓ {dao_address} at level {dao_data['level']}")
        else:
            print(f"  ✗ {dao_address} - missing required entrypoints")
    
    print(f"\nValid DAOs: {len(valid_daos)}")
    
    # Generate YAML entries
    yaml_entries = []
    for dao_data in valid_daos:
        dao_address = dao_data['originatedContract']['address']
        level = dao_data['level']
        yaml_entries.append(f"""  registry_dao_{dao_address}:
    template: registry_dao
    first_level: {level}
    values:
      contract: {contract_name}
      datasource: {datasource_name}
""")
    
    return yaml_entries, len(valid_daos)


async def main():
    """Main function"""
    print("=" * 60)
    print("Historical DAO Index Generator")
    print("=" * 60)
    
    # Process mainnet
    mainnet_entries, mainnet_count = await generate_indexes_for_network(
        'mainnet', 
        2900000,
        'registry_mainnet',
        'tzkt_mainnet'
    )
    
    # Process ghostnet
    ghostnet_entries, ghostnet_count = await generate_indexes_for_network(
        'ghostnet',
        8900000,
        'registry_ghostnet',
        'tzkt_ghostnet'
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Mainnet DAOs: {mainnet_count}")
    print(f"Ghostnet DAOs: {ghostnet_count}")
    print(f"Total DAOs: {mainnet_count + ghostnet_count}")
    
    # Print YAML entries
    print("\n" + "=" * 60)
    print("YAML ENTRIES TO ADD TO dipdup.yml")
    print("=" * 60)
    print("\n# Historical DAO indexes (generated)")
    for entry in mainnet_entries + ghostnet_entries:
        print(entry, end='')
    
    # Also save to a file
    output_file = os.path.join(os.path.dirname(__file__), 'historical_dao_indexes.yaml')
    with open(output_file, 'w') as f:
        f.write("# Historical DAO indexes (generated)\n")
        for entry in mainnet_entries + ghostnet_entries:
            f.write(entry)
    
    print(f"\n\nYAML entries also saved to: {output_file}")


if __name__ == '__main__':
    asyncio.run(main())

