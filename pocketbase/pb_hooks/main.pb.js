/// <reference path="../pocketbase_0.41.1_linux_amd64/pb_data/types.d.ts" />

// Creates a new game (lobby) with a unique 5 digit code, inserts the
// requesting player into it and returns the new game id (the code).
routerAdd("POST", "/game/new", (e) => {
    try {
        const body = e.requestInfo().body
        const username = String(body.username || "").trim()

        if (!username) {
            return e.json(400, { message: "username is required" })
        }

        const gamesCollection = $app.findCollectionByNameOrId("games")
        const playersCollection = $app.findCollectionByNameOrId("players")

        const newPlayer = new Record(playersCollection)
        newPlayer.set("name", body.username)
        $app.save(newPlayer)

        const newGame = new Record(gamesCollection)
        newGame.set("players", [newPlayer.id])
        $app.save(newGame)

        return e.json(200, newGame.id)
    } catch (err) {
        return e.json(500, { message: "Could not create a game: " + err })
    }
})

routerAdd("POST", "/game/join", (e) => {
    try {
        const body = e.requestInfo().body
        const username = String(body.username || "").trim()
        const code = String(body.code || "").trim()

        if (!username) {
            return e.json(400, { message: "username is required" })
        }

        if (!code) {
            return e.json(400, { message: "code is required" })
        }

        let game
        try {
            game = $app.findRecordById("games", code)
        } catch (err) {
            return e.json(404, { message: "game not found" })
        }

        const playersCollection = $app.findCollectionByNameOrId("players")
        
        const newPlayer = new Record(playersCollection)
        newPlayer.set("name", body.username)
        $app.save(newPlayer)

        game.set("players+", newPlayer.id)

        $app.save(game)

        return e.json(200, game.id)
    } catch (err) {
        return e.json(500, { message: "Could not join a game: " + err })
    }
})

routerAdd("POST", "/game/leave", (e) => {
    try {
        const body = e.requestInfo().body
        const username = String(body.username || "").trim()
        const code = String(body.code || "").trim()

        if (!username) {
            return e.json(400, { message: "username is required" })
        }

        if (!code) {
            return e.json(400, { message: "code is required" })
        }

        let game
        try {
            game = $app.findRecordById("games", code)
        } catch (err) {
            return e.json(404, { message: "game not found" })
        }

        let player
        try {
            player = $app.findFirstRecordByFilter("players", "name = {:name}", { name: username })
        } catch (err) {
            return e.json(404, { message: "player not found" })
        }

        game.set("players-", player.id)
        $app.save(game)

        $app.delete(player)

        return e.json(200, { message: "left game" })
    } catch (err) {
        return e.json(500, { message: "Could not leave game: " + err })
    }
})

routerAdd("GET", "/hello/{name}", (e) => {
    let name = e.request.pathValue("name")

    return e.json(200, { "message": "Hello " + name })
})
