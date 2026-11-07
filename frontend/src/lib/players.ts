import { pb } from "./pb"

// Fetches a game and returns the names of the players in it.
export async function getPlayers(gameId: string): Promise<string[]> {
    const game = await pb.collection("games").getOne(gameId, { expand: "players" })

    return (game.expand?.players ?? []).map((player: { name: string }) => player.name)
}
