
import json
import traceback

_CFG = {}

def get(v):
    return _CFG[v]

def load():
    global _CFG
    # We let this throw exceptions because we want the server to stop
    with open("data/config.json", "r") as f:
        _CFG = json.load(f)


def save():
    try:
        with open("data/config.json", "w") as f:
            json.dump(_CFG,f,indent=2)

    except Exception:
        traceback.print_exc()

def set_default():
    global _CFG
    _CFG = {
        "eye_positions": {
            "disco": [
                [-75, 115],
                [0, 0],
            ],
            "headlights": [
                [0, 10],
                [0, 10]
            ]
        },

        "parallax_distance": 0.125,
        "eye_rotation": {
            "p": 30.0,
            "b": -30.0
        }    
    }