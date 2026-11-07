# A winner between two objects can be queried by getting: <DOMAIN>/winner?object1=<OBJECT1>&object2=<OBJECT2>
# Random items can be queried by http://127.0.0.1:8000/items
# fastapi dev Interface.py - Starts fastapi

from fastapi import FastAPI

import random
import httpx
from fastapi import FastAPI, HTTPException, Query
import time
from fastapi.middleware.cors import CORSMiddleware


from WinnerDecider import WinnerDecider

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/winner")
def getWinner(object1:str, object2:str):
    return {
        "winner" : WinnerDecider.returnWinner(object1, object2)
    }

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
# Wikidata asks for a descriptive User-Agent; requests without one may be rejected.
USER_AGENT = "RandomWikidataDemo/1.0 (https://example.com/contact; you@example.com)"
 
# The candidate pool is cached so repeat calls don't hit Wikidata each time.
_CACHE: dict = {"key": None, "expires": 0.0, "pool": []}
 
 
async def get_random_wikidata_items() -> list[dict]:
    # ---- Settings (must stay at the top of the function) -------------------
    n = 10  # number of random items to return
 
    # Parent classes. An item is only returned if it is a subclass (P279) of
    # one of these, within `max_depth` levels. Q223557 = "physical object".
    listOfAllowedCategories = [
        "Q223557",
    ]
 
    max_depth = 3          # 1-4 levels of "subclass of". Keep small: deep chains time out.
    min_sitelinks = 20     # popularity filter: item must have >= this many Wikimedia sitelinks
    pool_size = 500        # max candidates fetched from Wikidata
    cache_seconds = 3600   # how long the candidate pool is reused
    image_width = 500      # pixel width of the returned image (Wikimedia scales it for you)
    # ------------------------------------------------------------------------
 
    max_depth = max(1, min(max_depth, 4))
    cache_key = (tuple(listOfAllowedCategories), max_depth, min_sitelinks, pool_size, image_width)
 
    now = time.time()
    if _CACHE["key"] == cache_key and _CACHE["expires"] > now and _CACHE["pool"]:
        pool = _CACHE["pool"]
        return random.sample(pool, min(n, len(pool)))
 
    # Efficiency notes:
    #  * Explicit, bounded P279 chains (1..max_depth hops) are joined with UNION.
    #    An unbounded wdt:P279* path covers a huge part of Wikidata and times out.
    #  * The sitelinks filter removes obscure classes before labels are fetched.
    #  * LIMIT caps the result size; labels/descriptions are fetched afterwards.
    #  * The random pick happens in Python, so no ORDER BY RAND() on the server.
    values = " ".join(f"wd:{c}" for c in listOfAllowedCategories)
    union = " UNION ".join(
        "{ ?item " + "/".join(["wdt:P279"] * d) + " ?parent . }"
        for d in range(1, max_depth + 1)
    )
    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?image WHERE {{
      VALUES ?parent {{ {values} }}
      {union}
      ?item wdt:P18 ?image .
      ?item wikibase:sitelinks ?links .
      FILTER(?links >= {min_sitelinks})
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {pool_size}
    """
 
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            WIKIDATA_SPARQL_URL,
            params={"query": query, "format": "json"},
            headers=headers,
        )
        resp.raise_for_status()
        rows = resp.json()["results"]["bindings"]
 
    pool = []
    seen = set()
    for r in rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        label = r.get("itemLabel", {}).get("value", qid)
        if label == qid or qid in seen:  # no English label, or a second image of the same item
            continue
        seen.add(qid)
        # P18 gives a Wikimedia Commons "Special:FilePath" link; force https and
        # ask Wikimedia for a scaled version so the image isn't huge.
        image = r["image"]["value"].replace("http://", "https://", 1)
        pool.append({"id": qid, "name": label, "image": f"{image}?width={image_width}"})
 
    if not pool:
        raise RuntimeError("Wikidata returned no results")
 
    _CACHE.update(key=cache_key, expires=now + cache_seconds, pool=pool)
    return random.sample(pool, min(n, len(pool)))
 
 
@app.get("/items")
async def random_items():
    try:
        return await get_random_wikidata_items()
    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Wikidata query failed: {exc}")
