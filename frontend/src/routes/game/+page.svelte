<script lang="ts">
    import { goto } from "$app/navigation"
    import { pb } from "../../lib/pb"
    import { getPlayers } from "../../lib/players"
    import { session } from "../../lib/stores.svelte"

    const code = $derived(session.lobbyCode)

    let players = $state<string[]>([])
    let unsubscribe: (() => void) | undefined
    let redirected = false

    // Once two players are in the lobby, send everyone to the game page.
    // The game page reads the same lobby code and loads the players itself.
    $effect(() => {
        if (players.length >= 2 && !redirected) {
            redirected = true
            goto("/game/game")
        }
    })

    $effect(() => {
        const gameId = code
        if (!gameId) {
            return
        }

        let active = true

        getPlayers(gameId)
            .then((names) => {
                if (active) {
                    players = names
                }
            })
            .catch((err) => console.error("Could not load players", err))

        pb.collection("games")
            .subscribe(gameId, (e) => {
                players = e.record.expand?.players?.map((player: { name: string }) => player.name) ?? []
            }, { expand: "players" })
            .then((unsub) => {
                if (active) {
                    unsubscribe = unsub
                } else {
                    unsub()
                }
            })

        return () => {
            active = false
            unsubscribe?.()
            unsubscribe = undefined
        }
    })
</script>

<div class="h-screen w-full flex items-center justify-center">
    <div class="lobby-card">
        <h1 class="lobby-title">Game Id: <span class="lobby-code">{code}</span></h1>

        <h2 class="lobby-subtitle">Players</h2>

        <ul class="lobby-players">
            {#each players as player}
                <li>{player}</li>
            {/each}
        </ul>
    </div>
</div>

<style>
    /* The lobby is presented as a playing card, matching /game/game. */
    .lobby-card {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 22rem;
        padding: 1.5rem 1.75rem;
        border-radius: 16px;
        border: 5px solid transparent;
        background-origin: border-box;
        background-clip: padding-box, border-box;
        background-image:
            linear-gradient(var(--game-white), var(--game-white)),
            linear-gradient(to bottom, var(--game-zinc-500), var(--game-zinc-900));
        box-shadow:
            0 6px 14px color-mix(in srgb, var(--game-black) 30%, transparent),
            0 2px 4px color-mix(in srgb, var(--game-black) 20%, transparent);
        text-align: center;
    }

    .lobby-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--game-gray-900);
    }

    .lobby-code {
        font-family: var(--font-code, monospace);
    }

    .lobby-subtitle {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--game-zinc-500);
    }

    .lobby-players {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .lobby-players li {
        font-family: inherit;
        padding: 0.5rem 0.75rem;
        border-radius: 10px;
        background-color: var(--game-cream);
        color: var(--game-gray-900);
        font-weight: 600;
    }
</style>
