/**
 * Role Assignment Helper Script for FoodTraceability Contract
 *
 * Usage:
 *   npx hardhat run scripts/assign-roles.js --network amoy
 *
 * This script assigns supply chain roles to multiple test addresses.
 * Edit the test addresses below before running.
 */

const hre = require("hardhat");

async function main() {
  // ========== CONFIGURATION ==========
  // TODO: Replace with your deployed contract address
  const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS || "0x0000000000000000000000000000000000000000";

  if (CONTRACT_ADDRESS === "0x0000000000000000000000000000000000000000") {
    console.error("❌ ERROR: Please set CONTRACT_ADDRESS in your .env file or as an environment variable");
    console.log("   Example: export CONTRACT_ADDRESS=0xYourContractAddress");
    process.exit(1);
  }

  // ========== TEST ADDRESSES ==========
  // TODO: Replace with actual addresses you want to assign roles to
  const TEST_ADDRESSES = {
    producers: [
      "0x0000000000000000000000000000000000000001",  // Producer 1
      "0x0000000000000000000000000000000000000002",  // Producer 2
    ],
    distributors: [
      "0x0000000000000000000000000000000000000003",  // Distributor 1
      "0x0000000000000000000000000000000000000004",  // Distributor 2
    ],
    retailers: [
      "0x0000000000000000000000000000000000000005",  // Retailer 1
      "0x0000000000000000000000000000000000000006",  // Retailer 2
    ],
    regulators: [
      "0x0000000000000000000000000000000000000007",  // Regulator 1
    ]
  };

  console.log("🔧 FoodTraceability Role Assignment Script");
  console.log("==========================================\n");

  // Get signer (must have DEFAULT_ADMIN_ROLE)
  const [deployer] = await hre.ethers.getSigners();
  console.log(`👤 Using account: ${deployer.address}`);
  console.log(`💰 Balance: ${hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address))} MATIC\n`);

  // Get contract instance
  console.log(`📄 Connecting to contract at: ${CONTRACT_ADDRESS}`);
  const FoodTraceability = await hre.ethers.getContractAt("FoodTraceability", CONTRACT_ADDRESS);
  console.log("✅ Contract connected\n");

  // Get role hashes from contract
  const PRODUCER_ROLE = await FoodTraceability.PRODUCER_ROLE();
  const DISTRIBUTOR_ROLE = await FoodTraceability.DISTRIBUTOR_ROLE();
  const RETAILER_ROLE = await FoodTraceability.RETAILER_ROLE();
  const REGULATOR_ROLE = await FoodTraceability.REGULATOR_ROLE();

  console.log("📋 Role Hashes:");
  console.log(`   PRODUCER_ROLE:    ${PRODUCER_ROLE}`);
  console.log(`   DISTRIBUTOR_ROLE: ${DISTRIBUTOR_ROLE}`);
  console.log(`   RETAILER_ROLE:    ${RETAILER_ROLE}`);
  console.log(`   REGULATOR_ROLE:   ${REGULATOR_ROLE}\n`);

  // Check if deployer has admin role
  const DEFAULT_ADMIN_ROLE = await FoodTraceability.DEFAULT_ADMIN_ROLE();
  const hasAdminRole = await FoodTraceability.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);

  if (!hasAdminRole) {
    console.error(`❌ ERROR: ${deployer.address} does not have DEFAULT_ADMIN_ROLE`);
    console.log("   Only the contract admin can grant roles.");
    process.exit(1);
  }
  console.log("✅ Deployer has DEFAULT_ADMIN_ROLE\n");

  // ========== ASSIGN PRODUCER ROLES ==========
  console.log("🌾 Assigning PRODUCER roles...");
  for (const address of TEST_ADDRESSES.producers) {
    if (address === "0x0000000000000000000000000000000000000001") {
      console.log(`   ⚠️  Skipping placeholder address: ${address}`);
      continue;
    }

    try {
      const hasRole = await FoodTraceability.hasRole(PRODUCER_ROLE, address);
      if (hasRole) {
        console.log(`   ✓ ${address} already has PRODUCER_ROLE`);
      } else {
        const tx = await FoodTraceability.grantRole(PRODUCER_ROLE, address);
        console.log(`   ⏳ Granting PRODUCER_ROLE to ${address}...`);
        await tx.wait();
        console.log(`   ✅ PRODUCER_ROLE granted to ${address}`);
      }
    } catch (error) {
      console.error(`   ❌ Error granting PRODUCER_ROLE to ${address}:`, error.message);
    }
  }
  console.log("");

  // ========== ASSIGN DISTRIBUTOR ROLES ==========
  console.log("🚚 Assigning DISTRIBUTOR roles...");
  for (const address of TEST_ADDRESSES.distributors) {
    if (address === "0x0000000000000000000000000000000000000003") {
      console.log(`   ⚠️  Skipping placeholder address: ${address}`);
      continue;
    }

    try {
      const hasRole = await FoodTraceability.hasRole(DISTRIBUTOR_ROLE, address);
      if (hasRole) {
        console.log(`   ✓ ${address} already has DISTRIBUTOR_ROLE`);
      } else {
        const tx = await FoodTraceability.grantRole(DISTRIBUTOR_ROLE, address);
        console.log(`   ⏳ Granting DISTRIBUTOR_ROLE to ${address}...`);
        await tx.wait();
        console.log(`   ✅ DISTRIBUTOR_ROLE granted to ${address}`);
      }
    } catch (error) {
      console.error(`   ❌ Error granting DISTRIBUTOR_ROLE to ${address}:`, error.message);
    }
  }
  console.log("");

  // ========== ASSIGN RETAILER ROLES ==========
  console.log("🏪 Assigning RETAILER roles...");
  for (const address of TEST_ADDRESSES.retailers) {
    if (address === "0x0000000000000000000000000000000000000005") {
      console.log(`   ⚠️  Skipping placeholder address: ${address}`);
      continue;
    }

    try {
      const hasRole = await FoodTraceability.hasRole(RETAILER_ROLE, address);
      if (hasRole) {
        console.log(`   ✓ ${address} already has RETAILER_ROLE`);
      } else {
        const tx = await FoodTraceability.grantRole(RETAILER_ROLE, address);
        console.log(`   ⏳ Granting RETAILER_ROLE to ${address}...`);
        await tx.wait();
        console.log(`   ✅ RETAILER_ROLE granted to ${address}`);
      }
    } catch (error) {
      console.error(`   ❌ Error granting RETAILER_ROLE to ${address}:`, error.message);
    }
  }
  console.log("");

  // ========== ASSIGN REGULATOR ROLES ==========
  console.log("👮 Assigning REGULATOR roles...");
  for (const address of TEST_ADDRESSES.regulators) {
    if (address === "0x0000000000000000000000000000000000000007") {
      console.log(`   ⚠️  Skipping placeholder address: ${address}`);
      continue;
    }

    try {
      const hasRole = await FoodTraceability.hasRole(REGULATOR_ROLE, address);
      if (hasRole) {
        console.log(`   ✓ ${address} already has REGULATOR_ROLE`);
      } else {
        const tx = await FoodTraceability.grantRole(REGULATOR_ROLE, address);
        console.log(`   ⏳ Granting REGULATOR_ROLE to ${address}...`);
        await tx.wait();
        console.log(`   ✅ REGULATOR_ROLE granted to ${address}`);
      }
    } catch (error) {
      console.error(`   ❌ Error granting REGULATOR_ROLE to ${address}:`, error.message);
    }
  }
  console.log("");

  console.log("==========================================");
  console.log("✅ Role assignment complete!");
  console.log("\n📊 Summary:");
  console.log(`   Producers:    ${TEST_ADDRESSES.producers.length} addresses`);
  console.log(`   Distributors: ${TEST_ADDRESSES.distributors.length} addresses`);
  console.log(`   Retailers:    ${TEST_ADDRESSES.retailers.length} addresses`);
  console.log(`   Regulators:   ${TEST_ADDRESSES.regulators.length} addresses`);
  console.log("\n💡 Tip: Use the Admin dashboard in Streamlit to verify role assignments");
}

// Run the script
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
