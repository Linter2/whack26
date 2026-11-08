<script lang="ts">
    import { goto } from "$app/navigation"
    import { pb } from "../lib/pb"
    import { session } from "../lib/stores.svelte"

    async function enter() {

        console.log("joining game")

        let lobbyId

        if (session.username && session.lobbyCode) {
            console.log("with code")

            const a = (await pb.send("/game/join", {
                method: "POST",

                body: JSON.stringify({
                    username: session.username,
                    code: session.lobbyCode
                })

            }))

            console.log(a)
            lobbyId = a

            // ...

        } else if (session.username) {

            console.log("with username");

            const a = (await pb.send("/game/new", {
                method: "POST",
                body: JSON.stringify({
                    username: session.username
                })
            }))

            console.log(a)
            lobbyId = a
        } else {
            return
        }
        session.lobbyCode = String(lobbyId)
        await goto("/game")
    }
</script>

<div class="h-screen w-full flex items-center justify-center">
    <div>
        <div>Join game</div>
        <div>
            <span>Enter Name <input bind:value={session.username}></span> <span>Or Lobby Code: <input bind:value={session.lobbyCode}></span>
        </div>
        <button onclick={enter}>Enter Game</button>
    </div>
</div>



