import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

export type SteamGameData = {
  appid: number;
  name: string;
  developer: string;
  publisher: string;
  score_rank: string;
  positive: number;
  negative: number;
  userscore: number;
  owners: string;
  average_forever: number;
  average_2weeks: number;
  median_forever: number;
  median_2weeks: number;
  price: string;
  initialprice: string;
  discount: string;
  ccu: number;
  icon_url: string;
}

// Parse owner range and return the average
function parseOwners(ownerRange: string): number {
  const [min, max] = ownerRange.split(' .. ')
    .map(str => parseInt(str.replace(/,/g, '')));
  return (min + max) / 2;
}

// Load and parse the Steam database
export async function loadSteamDatabase(): Promise<Map<number, SteamGameData>> {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const dbPath = path.join(__dirname, '..', 'db', 'base_steam.jsonl');
  
  const data = await fs.readFile(dbPath, 'utf-8');
  const lines = data.trim().split('\n');
  
  const steamDb = new Map<number, SteamGameData>();
  
  for (const line of lines) {
    try {
      const gameData = JSON.parse(line) as SteamGameData;
      steamDb.set(gameData.appid, gameData);
    } catch (error) {
      console.error(`Error parsing game data: ${error}`);
    }
  }
  
  console.log(`📚 Loaded ${steamDb.size} games from Steam database`);
  return steamDb;
}
