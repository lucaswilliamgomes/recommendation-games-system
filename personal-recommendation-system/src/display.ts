import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import type { GameRecommendation } from './types.js'
import { loadSteamDatabase } from './steamDb.js'
import { CONFIG, STEAM_ID } from './config.js';

// Enhanced recommendation data including Steam DB info
interface EnhancedRecommendation extends GameRecommendation {
  owners?: string;
  positiveReviews?: number;
  developer?: string;
  storeUrl: string;
}

export async function displayRecommendations(recommendations: GameRecommendation[]): Promise<void> {
  if (recommendations.length === 0) {
    console.log("😕 No recommendations found. This could be because:")
    console.log("   • Your friends' profiles are private")
    console.log("   • You already own all popular games among your friends")
    console.log("   • You have no friends added")
    return
  }

  // Load Steam database for additional info
  const steamDb = await loadSteamDatabase()

  // Create enhanced recommendations with Steam DB data
  const enhancedRecommendations: EnhancedRecommendation[] = recommendations.map(rec => {
    const steamGameData = steamDb.get(rec.appid);
    const enhanced: EnhancedRecommendation = {
      ...rec,
      storeUrl: `https://store.steampowered.com/app/${rec.appid}`
    };
    
    if (steamGameData) {
      enhanced.owners = steamGameData.owners;
      enhanced.positiveReviews = steamGameData.positive;
      enhanced.developer = steamGameData.developer;
    }
    
    return enhanced;
  });

  console.log(`\n🏆 Top ${recommendations.length} Game Recommendations:\n`)

  enhancedRecommendations.forEach((rec, index) => {
    console.log(`${index + 1}. ${rec.name}`)
    console.log(`   📊 Score: ${rec.score.toFixed(1)}`)
    console.log(`   👥 Owned by ${rec.friendsWhoOwn.length} friend(s)`)
    console.log(`   🔥 Recently played by ${rec.friendsWhoPlayedRecently.length} friend(s)`)
    console.log(`   ⏱️ Average playtime: ${rec.averagePlaytime} hours`)
    
    if (rec.owners) {
      console.log(`   🌍 Owners: ${rec.owners}`)
    }
    
    if (rec.positiveReviews) {
      console.log(`   👍 Positive reviews: ${rec.positiveReviews.toLocaleString()}`)
    }
    
    if (rec.developer) {
      console.log(`   🧑‍💻 Developer: ${rec.developer}`)
    }
    
    console.log(`   🆔 Steam ID: ${rec.appid}`)
    console.log(`   🔗 Store: ${rec.storeUrl}`)
    console.log("")
  })

  // Save the enhanced recommendations to JSON
  await saveRecommendationsToJson(enhancedRecommendations);

  console.log("💡 Higher scores indicate games that are:")
  console.log("   • Owned by more of your friends")
  console.log("   • Currently being played by your friends")
  console.log("   • Have high average playtime (indicating quality)")
  console.log("   • Popular across the Steam platform")
  console.log("   • Well-rated by the Steam community")
  console.log("\n✅ Recommendations saved to recommendations.json")
}

/**
 * Save recommendations to JSON file organized by Steam ID
 */
async function saveRecommendationsToJson(recommendations: EnhancedRecommendation[]): Promise<void> {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const filePath = path.join(__dirname, '..', 'recommendations.json');
  
  // Load existing data or start with empty object
  let allRecommendations: Record<string, EnhancedRecommendation[]> = {};
  
  try {
    const existingData = await fs.readFile(filePath, 'utf-8');
    allRecommendations = JSON.parse(existingData);
  } catch (error) {
    // File doesn't exist yet or other error, start with empty object
  }
  
  // Add timestamp to the recommendations data
  const steamId = STEAM_ID;
  
  if (typeof steamId === 'undefined') {
    throw new Error('STEAM_ID is undefined. Please check your configuration.');
  }

  // Create or update recommendations for this Steam ID
  allRecommendations[steamId] = recommendations.map(rec => ({
    ...rec,
    timestamp: new Date().toISOString() // Add timestamp to each set of recommendations
  }));
  
  // Save to file
  await fs.writeFile(
    filePath, 
    JSON.stringify(allRecommendations, null, 2)
  );
}
