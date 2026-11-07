# A winner between two objects can be queried by getting: <DOMAIN>/winner?object1=<OBJECT1>&object2=<OBJECT2>
# fastapi dev Interface.py - Starts fastapi

from fastapi import FastAPI
from WinnerDecider import WinnerDecider

app = FastAPI()

@app.get("/winner")
def getWinner(object1:str, object2:str):
    return {
        "winner" : WinnerDecider.returnWinner(object1, object2)
    }