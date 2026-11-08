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
        } else if (session.username) {
            console.log("with username")

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
    <div class="join-card">
        <div class="join-title">Join game</div>

        <div class="join-fields">
            <span class="join-field">
                <span>Enter Name</span>
                <input bind:value={session.username} placeholder="Your name">
            </span>

            <span class="join-field">
                <span>Or Lobby Code:</span>
                <input class="code" bind:value={session.lobbyCode} placeholder="Lobby code">
            </span>
        </div>

        <button class="enter-btn" onclick={enter}>Enter Game</button>
    </div>
</div>

<style>
    /* The join screen is presented as a playing card, matching /game/game. */
    .join-card {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        width: 22rem;
        padding: 2rem;
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

    .join-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--game-gray-900);
    }

    .join-fields {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .join-field {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        color: var(--game-gray-900);
        font-weight: 600;
        text-align: left;
    }

    .join-field input {
        border: none;
        border-radius: 10px;
        padding: 0.55rem 0.8rem;
        background-color: var(--game-cream);
        color: var(--game-gray-900);
        font-weight: 600;
        outline: 2px solid transparent;
        transition: outline-color 0.2s ease;
    }

    .join-field input.code {
        font-family: var(--font-code, monospace);
    }

    .join-field input:focus {
        outline-color: var(--game-green-600);
    }

    .enter-btn {
        padding: 0.7rem 1rem;
        border-radius: 9999px;
        border: 4px solid transparent;
        background-origin: border-box;
        background-clip: padding-box, border-box;
        background-image:
            linear-gradient(var(--game-green-600), var(--game-green-600)),
            linear-gradient(135deg, var(--game-green-700) 0%, var(--game-lime-500) 100%);
        color: var(--game-white);
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        cursor: pointer;
        box-shadow: 0 4px 10px color-mix(in srgb, var(--game-black) 15%, transparent);
        transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .enter-btn:hover {
        transform: translateY(-2px);
    }
</style>
