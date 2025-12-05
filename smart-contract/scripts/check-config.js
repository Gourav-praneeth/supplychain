/**
 * Configuration Check Script
 * Run this before deployment to verify your setup
 * 
 * Usage: npx hardhat run scripts/check-config.js
 */

const hre = require("hardhat");

async function main() {
  console.log("🔍 FoodTraceability Configuration Check");
  console.log("==========================================\n");

  let hasErrors = false;

  // Check PRIVATE_KEY
  console.log("1️⃣  Checking PRIVATE_KEY...");
  if (!process.env.PRIVATE_KEY) {
    console.log("   ❌ PRIVATE_KEY not set in .env");
    console.log("   💡 Export your private key from MetaMask:");
    console.log("      - Click account icon → Account Details → Export Private Key");
    console.log("      - Add to .env: PRIVATE_KEY=your_key_here (without 0x prefix)");
    hasErrors = true;
  } else if (process.env.PRIVATE_KEY.length < 64) {
    console.log("   ⚠️  PRIVATE_KEY looks too short. Should be 64 hex characters.");
    hasErrors = true;
  } else {
    console.log("   ✅ PRIVATE_KEY is set");
  }
  console.log("");

  // Check RPC URL
  console.log("2️⃣  Checking POLYGON_AMOY_RPC_URL...");
  const rpcUrl = process.env.POLYGON_AMOY_RPC_URL || "https://rpc-amoy.polygon.technology/";
  console.log(`   📡 Using: ${rpcUrl}`);
  
  try {
    const blockNumber = await hre.ethers.provider.getBlockNumber();
    console.log(`   ✅ Connected! Current block: ${blockNumber}`);
  } catch (error) {
    console.log(`   ❌ Failed to connect to RPC: ${error.message}`);
    hasErrors = true;
  }
  console.log("");

  // Check account and balance
  console.log("3️⃣  Checking deployer account...");
  try {
    const [deployer] = await hre.ethers.getSigners();
    console.log(`   👤 Address: ${deployer.address}`);
    
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    const balanceInMatic = hre.ethers.formatEther(balance);
    console.log(`   💰 Balance: ${balanceInMatic} MATIC`);
    
    if (balance === 0n) {
      console.log("   ❌ No MATIC! Get testnet tokens from:");
      console.log("      https://faucet.polygon.technology/");
      console.log("      (Select Amoy network and paste your address)");
      hasErrors = true;
    } else if (parseFloat(balanceInMatic) < 0.1) {
      console.log("   ⚠️  Low balance. Consider getting more testnet MATIC.");
    } else {
      console.log("   ✅ Sufficient balance for deployment");
    }
  } catch (error) {
    console.log(`   ❌ Error checking account: ${error.message}`);
    hasErrors = true;
  }
  console.log("");

  // Check REGULATOR_ADDRESS
  console.log("4️⃣  Checking REGULATOR_ADDRESS...");
  if (!process.env.REGULATOR_ADDRESS) {
    console.log("   ⚠️  REGULATOR_ADDRESS not set. Will use deployer address.");
    console.log("   💡 Set in .env to use a different regulator address.");
  } else {
    console.log(`   ✅ Regulator: ${process.env.REGULATOR_ADDRESS}`);
  }
  console.log("");

  // Summary
  console.log("==========================================");
  if (hasErrors) {
    console.log("❌ Configuration has issues. Fix them before deploying.");
    process.exit(1);
  } else {
    console.log("✅ Configuration looks good! Ready to deploy.");
    console.log("\n🚀 Deploy with:");
    console.log("   npx hardhat run scripts/deploy.js --network amoy");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

