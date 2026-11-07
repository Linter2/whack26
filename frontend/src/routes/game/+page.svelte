<script lang="ts">
    import { pb } from "../../lib/pb"
    import { getPlayers } from "../../lib/players"
    import { session } from "../../lib/stores.svelte"

    const code = $derived(session.lobbyCode)

    let players = $state<string[]>([])
    let unsubscribe: (() => void) | undefined

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

<h1>Game {code}</h1>

<h2>Players</h2>

<ul>
    {#each players as player}
        <li>{player}</li>
    {/each}
</ul>
