/**
 * FoodTraceability Contract Deployment Script
 * 
 * Usage:
 *   npx hardhat run scripts/deploy.js --network amoy
 * 
 * Prerequisites:
 *   1. Set PRIVATE_KEY in .env (wallet with MATIC for gas)
 *   2. Set POLYGON_AMOY_RPC_URL in .env
 *   3. Set REGULATOR_ADDRESS in .env (address to receive REGULATOR_ROLE)
 */

const hre = require("hardhat");

async function main() {
  console.log("🚀 FoodTraceability Contract Deployment");
  console.log("==========================================\n");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log(`👤 Deploying with account: ${deployer.address}`);
  
  // Check balance
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`💰 Account balance: ${hre.ethers.formatEther(balance)} MATIC`);
  
  if (balance === 0n) {
    console.error("\n❌ ERROR: Account has no MATIC for gas fees!");
    console.log("   Get testnet MATIC from: https://faucet.polygon.technology/");
    process.exit(1);
  }
  console.log("");

  // Get regulator address from env or use deployer as default
  const regulatorAddress = process.env.REGULATOR_ADDRESS || deployer.address;
  console.log(`👮 Regulator address: ${regulatorAddress}`);
  
  if (regulatorAddress === deployer.address) {
    console.log("   ⚠️  Using deployer as regulator (set REGULATOR_ADDRESS in .env to change)");
  }
  console.log("");

  // Deploy the contract
  console.log("📄 Deploying FoodTraceability contract...");
  const FoodTraceability = await hre.ethers.getContractFactory("FoodTraceability");
  const contract = await FoodTraceability.deploy(regulatorAddress);
  
  console.log("   ⏳ Waiting for deployment confirmation...");
  await contract.waitForDeployment();
  
  const contractAddress = await contract.getAddress();
  console.log(`   ✅ Contract deployed to: ${contractAddress}\n`);

  // Grant PRODUCER_ROLE to deployer for testing
  console.log("🌾 Granting PRODUCER_ROLE to deployer for testing...");
  const PRODUCER_ROLE = await contract.PRODUCER_ROLE();
  const grantTx = await contract.grantRole(PRODUCER_ROLE, deployer.address);
  await grantTx.wait();
  console.log(`   ✅ PRODUCER_ROLE granted to ${deployer.address}\n`);

  // Display role information
  console.log("📋 Role Hashes (for reference):");
  console.log(`   PRODUCER_ROLE:    ${await contract.PRODUCER_ROLE()}`);
  console.log(`   DISTRIBUTOR_ROLE: ${await contract.DISTRIBUTOR_ROLE()}`);
  console.log(`   RETAILER_ROLE:    ${await contract.RETAILER_ROLE()}`);
  console.log(`   REGULATOR_ROLE:   ${await contract.REGULATOR_ROLE()}`);
  console.log("");

  // Summary
  console.log("==========================================");
  console.log("✅ DEPLOYMENT SUCCESSFUL!");
  console.log("==========================================\n");
  
  console.log("📝 Next Steps:");
  console.log(`   1. Update backend/.env with:`);
  console.log(`      CONTRACT_ADDRESS=${contractAddress}`);
  console.log("");
  console.log(`   2. Verify contract on PolygonScan:`);
  console.log(`      npx hardhat verify --network amoy ${contractAddress} "${regulatorAddress}"`);
  console.log("");
  console.log(`   3. View on PolygonScan:`);
  console.log(`      https://amoy.polygonscan.com/address/${contractAddress}`);
  console.log("");
  console.log(`   4. Assign additional roles using:`);
  console.log(`      npx hardhat run scripts/assign-roles.js --network amoy`);
  console.log("");

  // Return contract address for programmatic use
  return contractAddress;
}

// Run deployment
main()
  .then((address) => {
    console.log(`\n🎉 Contract Address: ${address}`);
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });

