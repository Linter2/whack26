// pb_hooks/picks.pb.js
// Needs a "picks" collection: game (text), player (text), item (json, optional),
// all API rules locked, plus a unique index on (game, player).
//
// Each round of a match stores its picks under its own key "<gameId>:<round>"
// in the `game` field, so the same unique index works for every round.

// Save one player's pick for a round
routerAdd("POST", "/game/pick", (e) => {
  const body = e.requestInfo().body
  const code = body.code
  const username = body.username
  const round = Number(body.round)

  if (!code || !username || !Number.isInteger(round) || round < 1) {
    throw new BadRequestError("code, username and round are required")
  }

  // The game must exist and the player must be in it
  const game = $app.findRecordById("games", code)
  $app.expandRecord(game, ["players"], null)
  const names = game.expandedAll("players").map((p) => p.get("name"))
  if (!names.includes(username)) {
    throw new ForbiddenError("not in this game")
  }

  const picks = $app.findCollectionByNameOrId("picks")
  const pick = new Record(picks)
  pick.set("game", code + ":" + round)
  pick.set("player", username)
  pick.set("item", body.item ?? null)
  $app.save(pick) // the unique index rejects a second pick from the same player in a round

  return e.json(200, { ok: true })
})

// Return the opponent's pick, but only once both players have submitted for this round
routerAdd("GET", "/game/reveal", (e) => {
  const code = e.request.url.query().get("code")
  const username = e.request.url.query().get("username")
  const round = Number(e.request.url.query().get("round"))

  if (!code || !username || !Number.isInteger(round) || round < 1) {
    throw new BadRequestError("code, username and round are required")
  }

  const key = code + ":" + round
  const rows = $app.findRecordsByFilter("picks", "game = {:g}", "", 10, 0, { g: key })
  if (rows.length < 2) {
    return e.json(200, { ready: false })
  }

  const theirs = rows.find((r) => r.get("player") !== username)
  if (!theirs) {
    return e.json(200, { ready: false })
  }

  return e.json(200, { ready: true, item: theirs.get("item") })
})

// Take a player's pick back (they un-pressed READY).
// Refused once both players have picked: at that point the round is locked in.
routerAdd("POST", "/game/unpick", (e) => {
  const body = e.requestInfo().body
  const code = body.code
  const username = body.username
  const round = Number(body.round)

  if (!code || !username || !Number.isInteger(round) || round < 1) {
    throw new BadRequestError("code, username and round are required")
  }

  const key = code + ":" + round
  const rows = $app.findRecordsByFilter("picks", "game = {:g}", "", 10, 0, { g: key })
  if (rows.length >= 2) {
    throw new BadRequestError("round is locked")
  }

  const mine = rows.find((r) => r.get("player") === username)
  if (mine) {
    $app.delete(mine)
  }

  return e.json(200, { ok: true })
})
