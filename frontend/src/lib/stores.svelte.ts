import { pb } from "./pb"

// Shared, app-wide session state.
// This file must use the `.svelte.ts` extension so that `$state` works in a module.
export const session = $state({
    username: "",
    lobbyCode: ""
})

// Leaves the current game and clears the lobby code so it can't be left twice.
export function leaveGame() {
    if (!session.lobbyCode || !session.username) {
        return
    }

    const username = session.username
    const code = session.lobbyCode

    session.lobbyCode = ""

    pb.send("/game/leave", {
        method: "POST",
        body: JSON.stringify({
            username: username,
            code: code
        })
    }).catch((err) => console.error("Could not leave game", err))
}
