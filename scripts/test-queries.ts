// test-hasura-queries.ts
// Run with: npx ts-node test-hasura-queries.ts
// Or compile and run: tsc test-hasura-queries.ts && node test-hasura-queries.js

import { GraphQLClient } from "graphql-request"
import { gql } from "graphql-request"

const GET_DAOS_QUERY = gql`
  query getDaos($network: String!) {
    daos(where: { network: { _eq: $network } }) {
      dao_type {
        name
      }
      description
      address
      frozen_token_id
      governance_token_id
      ledgers {
        holder {
          address
        }
      }
      name
      network
      period
      staked
      start_level
      token {
        contract
        decimals
        is_transferable
        level
        name
        network
        should_prefer_symbol
        supply
        symbol
        timestamp
        token_id
      }
    }
  }
`

const GET_DAO_QUERY = gql`
  query getDao($address: String!) {
    daos(where: { address: { _eq: $address } }) {
      dao_type {
        id
        name
      }
      description
      address
      frozen_token_id
      governance_token_id
      guardian
      id
      last_updated_cycle
      ledgers {
        id
        holder {
          id
          address
          proposals_aggregate {
            aggregate {
              count
            }
          }
          votes_aggregate {
            aggregate {
              sum {
                amount
              }
            }
          }
        }
        current_stage_num
        current_unstaked
        past_unstaked
        staked
      }
      max_quorum_change
      max_quorum_threshold
      min_quorum_threshold
      name
      network
      period
      proposal_expired_level
      proposal_flush_level
      quorum_change
      fixed_proposal_fee_in_token
      quorum_threshold
      staked
      start_level
      lambda_extras {
        id
        frozen_extra_value
        frozen_scale_value
        max_xtz_amount
        min_xtz_amount
        registry
        registry_affected
        slash_division_value
        slash_scale_value
      }
      token {
        id
        contract
        decimals
        is_transferable
        level
        name
        network
        should_prefer_symbol
        supply
        symbol
        timestamp
        token_id
      }
    }
  }
`

const GET_PROPOSALS_QUERY = gql`
  query getDao($address: String!) {
    daos(where: { address: { _eq: $address } }) {
      proposals {
        downvotes
        hash
        id
        key
        metadata
        proposer_frozen_token
        proposer_id
        quorum_threshold
        start_level
        start_date
        upvotes
        voting_stage_num
        holder {
          address
          id
        }
        status_updates(order_by: { timestamp: asc }) {
          timestamp
          id
          level
          proposal_status {
            id
            description
          }
        }
        votes {
          amount
          holder {
            address
            id
          }
          id
          support
          staked
        }
      }
    }
  }
`

const GET_PROPOSAL_QUERY = gql`
  query getDao($address: String!, $proposalKey: String!) {
    daos(where: { _and: { address: { _eq: $address } } }) {
      proposals(where: { key: { _eq: $proposalKey } }) {
        downvotes
        hash
        id
        key
        metadata
        proposer_frozen_token
        proposer_id
        quorum_threshold
        start_level
        start_date
        upvotes
        voting_stage_num
        holder {
          address
          id
        }
        status_updates(order_by: { timestamp: asc }) {
          timestamp
          id
          level
          proposal_status {
            id
            description
          }
        }
        votes {
          amount
          holder {
            address
            id
          }
          id
          support
          staked
        }
      }
    }
  }
`

const GET_XTZ_TRANSFERS = gql`
  query getTransfers($address: String!) {
    transfer(where: { dao: { address: { _eq: $address } } }) {
      decimal_amount
      amount
      from_address
      timestamp
      hash
    }
  }
`

interface TestConfig {
  hasuraUrl: string
  testNetwork: string
  testDaoAddress?: string
  testProposalKey?: string
}

async function testQuery(
  name: string,
  query: any,
  variables: Record<string, any>,
  client: GraphQLClient
): Promise<{ success: boolean; error?: string; data?: any; count?: number }> {
  try {
    console.log(`\n🔍 Testing: ${name}`)
    console.log(`   Variables:`, JSON.stringify(variables, null, 2))
    
    const startTime = Date.now()
    const data = await client.request(query, variables)
    const duration = Date.now() - startTime
    
    const resultCount = Array.isArray(data.daos) 
      ? data.daos.length 
      : Array.isArray(data.transfer)
      ? data.transfer.length
      : data.daos?.[0]?.proposals?.length || 0
    
    console.log(`   ✅ Success (${duration}ms)`)
    console.log(`   📊 Results: ${resultCount} item(s)`)
    
    return { success: true, data, count: resultCount }
  } catch (error: any) {
    console.log(`   ❌ Failed`)
    console.log(`   Error: ${error.message}`)
    if (error.response) {
      console.log(`   Response:`, JSON.stringify(error.response, null, 2))
    }
    return { success: false, error: error.message }
  }
}

async function runTests(config: TestConfig) {
  console.log("=".repeat(60))
  console.log("🧪 Hasura GraphQL Query Test Suite")
  console.log("=".repeat(60))
  console.log(`\n📡 Hasura URL: ${config.hasuraUrl}`)
  console.log(`🌐 Test Network: ${config.testNetwork}`)
  if (config.testDaoAddress) {
    console.log(`📍 Test DAO Address: ${config.testDaoAddress}`)
  }
  if (config.testProposalKey) {
    console.log(`🔑 Test Proposal Key: ${config.testProposalKey}`)
  }
  
  const client = new GraphQLClient(config.hasuraUrl, {
    headers: { "content-type": "application/json" }
  })
  
  const results: Array<{ name: string; success: boolean }> = []
  
  // Test 1: GET_DAOS_QUERY
  const test1 = await testQuery(
    "GET_DAOS_QUERY - Fetch all DAOs for network",
    GET_DAOS_QUERY,
    { network: config.testNetwork },
    client
  )
  results.push({ name: "GET_DAOS_QUERY", success: test1.success })
  
  // If we got DAOs, use the first one for subsequent tests
  let daoAddress = config.testDaoAddress
  if (!daoAddress && test1.success && test1.data?.daos?.length > 0) {
    daoAddress = test1.data.daos[0].address
    console.log(`\n   ℹ️  Using first DAO address from results: ${daoAddress}`)
  }
  
  if (!daoAddress) {
    console.log(`\n⚠️  No DAO address available. Skipping DAO-specific tests.`)
    console.log(`   Provide a testDaoAddress in config to test remaining queries.`)
    printSummary(results)
    return
  }
  
  // Test 2: GET_DAO_QUERY
  const test2 = await testQuery(
    "GET_DAO_QUERY - Fetch single DAO by address",
    GET_DAO_QUERY,
    { address: daoAddress },
    client
  )
  results.push({ name: "GET_DAO_QUERY", success: test2.success })
  
  // Test 3: GET_PROPOSALS_QUERY
  const test3 = await testQuery(
    "GET_PROPOSALS_QUERY - Fetch all proposals for DAO",
    GET_PROPOSALS_QUERY,
    { address: daoAddress },
    client
  )
  results.push({ name: "GET_PROPOSALS_QUERY", success: test3.success })
  
  // Get proposal key from proposals if available
  let proposalKey = config.testProposalKey
  if (!proposalKey && test3.success && test3.data?.daos?.[0]?.proposals?.length > 0) {
    proposalKey = test3.data.daos[0].proposals[0].key
    console.log(`\n   ℹ️  Using first proposal key from results: ${proposalKey}`)
  }
  
  // Test 4: GET_PROPOSAL_QUERY
  if (proposalKey) {
    const test4 = await testQuery(
      "GET_PROPOSAL_QUERY - Fetch single proposal by key",
      GET_PROPOSAL_QUERY,
      { address: daoAddress, proposalKey },
      client
    )
    results.push({ name: "GET_PROPOSAL_QUERY", success: test4.success })
  } else {
    console.log(`\n⚠️  No proposal key available. Skipping GET_PROPOSAL_QUERY test.`)
    results.push({ name: "GET_PROPOSAL_QUERY", success: false })
  }
  
  // Test 5: GET_XTZ_TRANSFERS
  const test5 = await testQuery(
    "GET_XTZ_TRANSFERS - Fetch XTZ transfers for DAO",
    GET_XTZ_TRANSFERS,
    { address: daoAddress },
    client
  )
  results.push({ name: "GET_XTZ_TRANSFERS", success: test5.success })
  
  printSummary(results)
}

function printSummary(results: Array<{ name: string; success: boolean }>) {
  console.log("\n" + "=".repeat(60))
  console.log("📋 Test Summary")
  console.log("=".repeat(60))
  
  const passed = results.filter(r => r.success).length
  const failed = results.filter(r => !r.success).length
  
  results.forEach(result => {
    const icon = result.success ? "✅" : "❌"
    console.log(`${icon} ${result.name}`)
  })
  
  console.log("\n" + "-".repeat(60))
  console.log(`Total: ${results.length} | Passed: ${passed} | Failed: ${failed}`)
  console.log("=".repeat(60))
}

// Main execution
async function main() {
  const hasuraUrl = process.env.REACT_APP_HASURA_URL || process.env.HASURA_URL
  const testNetwork = process.env.TEST_NETWORK || "mainnet"
  const testDaoAddress = process.env.TEST_DAO_ADDRESS
  const testProposalKey = process.env.TEST_PROPOSAL_KEY
  
  if (!hasuraUrl) {
    console.error("❌ Error: REACT_APP_HASURA_URL or HASURA_URL environment variable is required")
    console.error("\nUsage:")
    console.error("  REACT_APP_HASURA_URL=http://localhost:8080/v1/graphql \\")
    console.error("  TEST_NETWORK=mainnet \\")
    console.error("  TEST_DAO_ADDRESS=KT1... \\")
    console.error("  TEST_PROPOSAL_KEY=... \\")
    console.error("  npx ts-node test-hasura-queries.ts")
    process.exit(1)
  }
  
  const config: TestConfig = {
    hasuraUrl,
    testNetwork,
    testDaoAddress,
    testProposalKey
  }
  
  await runTests(config)
}

if (require.main === module) {
  main().catch(error => {
    console.error("❌ Fatal error:", error)
    process.exit(1)
  })
}

export { runTests, testQuery }