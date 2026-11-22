#!/usr/bin/env node
/**
 * RailKit Node.js Bridge for SmartTrip Backend
 * Executes RailKit SDK calls in a safe, isolated subprocess.
 */

const path = require('path');
const fs = require('fs');

// Try loading railkit from frontend/node_modules or global/local
let railkit;
try {
  railkit = require('railkit');
} catch (e1) {
  try {
    const frontendRailkitPath = path.join(__dirname, '../../frontend/node_modules/railkit');
    railkit = require(frontendRailkitPath);
  } catch (e2) {
    console.error(JSON.stringify({
      success: false,
      error: "RailKit package not found. Please install railkit via npm."
    }));
    process.exit(1);
  }
}

// Read API key from env or argument. Prefer env so secrets do not appear in process args.
const apiKey = process.env.RAILKIT_API_KEY || process.argv[2];
const argOffset = process.env.RAILKIT_API_KEY ? 2 : 3;
if (!apiKey) {
  console.error(JSON.stringify({
    success: false,
    error: "RAILKIT_API_KEY is not configured in environment or arguments."
  }));
  process.exit(1);
}

try {
  railkit.configure(apiKey);
} catch (cfgErr) {
  console.error(JSON.stringify({
    success: false,
    error: `RailKit configuration failed: ${cfgErr.message}`
  }));
  process.exit(1);
}

async function run() {
  const action = process.argv[argOffset] || "search";
  const fromStn = process.argv[argOffset + 1];
  const toStn = process.argv[argOffset + 2];
  const date = process.argv[argOffset + 3];

  try {
    if (action === "search") {
      if (!fromStn || !toStn) {
        console.log(JSON.stringify({
          success: false,
          error: "Source and destination station codes are required."
        }));
        return;
      }
      const res = await railkit.searchTrainBetweenStations(fromStn, toStn, date || undefined);
      console.log(JSON.stringify(res));
    } else if (action === "stations") {
      if (!fromStn) {
        console.log(JSON.stringify({ success: false, error: "Query string required." }));
        return;
      }
      const res = await railkit.stationsByName(fromStn);
      console.log(JSON.stringify(res));
    } else if (action === "info") {
      if (!fromStn) {
        console.log(JSON.stringify({ success: false, error: "Train number required." }));
        return;
      }
      const res = await railkit.getTrainInfo(fromStn);
      console.log(JSON.stringify(res));
    } else {
      console.log(JSON.stringify({
        success: false,
        error: `Unsupported bridge action '${action}'`
      }));
    }
  } catch (err) {
    console.log(JSON.stringify({
      success: false,
      error: err.message || String(err)
    }));
  }
}

run();
