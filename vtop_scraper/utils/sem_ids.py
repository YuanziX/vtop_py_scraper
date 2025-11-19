import json
import os

semIDs = json.load(
    open(os.path.join(os.path.dirname(__file__), "../constants/sem_ids.json"))
).keys()
