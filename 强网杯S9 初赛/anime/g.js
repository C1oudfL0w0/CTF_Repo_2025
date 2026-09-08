const { MongoClient } = require('mongodb');
const readline = require('readline');

const uri = 'mongodb://mongo:27017/MAL';
const dbName = 'MAL';
const collectionName = 'users';
const query = { "username": "TTXSMcc" };
const updateData = { "$set": { "role": "super_admin" } };

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    console.log("Successfully connected to local MongoDB.");

    const database = client.db(dbName);
    const collection = database.collection(collectionName);

    console.log("Ready to capture packets on Wireshark...");
    
    await new Promise(resolve => rl.question("Press Enter to send the update command to MongoDB...", resolve));
    
    const result = await collection.updateOne(query, updateData);
    console.log(`Command sent! ${result.modifiedCount} document(s) updated.`);
    
  } catch (e) {
    console.error(e);
  } finally {
    await client.close();
    rl.close();
  }
}

main().catch(console.error);
