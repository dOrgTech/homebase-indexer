#!/usr/bin/env python3
"""
Patch for DipDup v7 to handle missing 'reward' field in TzKT API responses
"""

import os
import sys

def patch_tzkt_model():
    """Patch the TzktBlockData.from_json method to handle missing 'reward' field"""
    
    file_path = '/opt/dipdup/src/dipdup/models/tezos_tzkt.py'
    
    # Read the original file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic line to handle missing 'reward' field
    # The original line: reward=block_json['reward'],
    # Should become: reward=block_json.get('reward', 0),
    
    old_pattern = "reward=block_json['reward'],"
    new_pattern = "reward=block_json.get('reward', 0),"
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # Write the patched file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Successfully patched {file_path}")
        return True
    else:
        print(f"Pattern not found or already patched in {file_path}")
        return False

if __name__ == '__main__':
    try:
        if patch_tzkt_model():
            sys.exit(0)
        else:
            # Not an error if already patched
            sys.exit(0)
    except Exception as e:
        print(f"Error patching file: {e}")
        sys.exit(1)




