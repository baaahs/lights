
import json
import traceback

_CFG = {}
_config_file = "data/config.json"

def get(v):
    return _CFG[v]

def has(v):
    return v in _CFG

def copy():
    "Returns a copy of the entire config"
    return _CFG.copy()

def load(filename="data/config.json"):
    global _CFG
    global _config_file

    _config_file = filename

    # We let this throw exceptions because we want the server to stop
    with open(filename, "r") as f:
        loaded = json.load(f)
        _CFG.update(loaded)


def save():
    try:
        with open(_config_file, "w") as f:
            json.dump(_CFG,f,indent=2)

    except Exception:
        traceback.print_exc()



def set_default():
    global _CFG
    _CFG = {
        "mode": "ola",
        "sim_host": "localhost",
        "sim_port": 4444,
        "opc_host": "localhost",
        "opc_port": 7890,
        "max_pixels": 100,
        "max_time": 900,

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

set_default()