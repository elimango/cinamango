import c4d
import maxon
import json
import os
import socket
import re
import uuid
from pathlib import Path

host = socket.gethostname()

doc = c4d.documents.GetActiveDocument()
binary = doc.GetDocumentName()

wheredocument = Path(doc.GetDocumentPath())
whereanimation =  wheredocument.parent
whereproject = whereanimation.parent
wherecomp =  str(f"{whereproject}/comp")

steps = 0

def outputScene(doc):
    document = os.path.splitext(c4d)[0]
    scenejson = os.path.join(wherecomp, "scene.json")    
    scenenum = re.findall(r'\d+', document)
    scene = [int(num) for num in scenenum][0]
    file = str(f"animation/scene_{scene}/{binary}")
    length = doc.GetMaxTime().GetFrame(doc.GetFps())

    assignments = []
    passes = []

    assign = {
        "id": host,
        "job": "Name",
        "engine-passes": passes,
        "range-start": 0,
        "range-end": 0
    }
    if not os.path.exists(scenejson):
        data = {
        }
        with open(scenejson, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
    with open(scenejson, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check if 'sequences' exists
    if "sequences" not in data:
        data["sequences"] = []
    dirty = False
    if assignments is None:
        assignments.append([])
    for job in range(steps):
        session = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(job+scene)))
        assignment = assign.copy()
        assignment["job"] = session
        min = 0
        if job > 0:
            min = job * steps + 1
        assignment["range-start"] = min
        assignment["range-end"] = (job + 1) * steps
        for sequence in data["sequences"]:
            if sequence.get("scene") == scene:
                dirty = True            
                if "assigned" not in sequence or not isinstance(sequence["assigned"], list):
                    sequence["assigned"] = []
            sequence["scene"] = scene  # You can modify more fields here
            if assignment not in sequence["assigned"]:
                assignments.append(assignment)
            sequence["assigned"].extend(assignments)
        if not dirty:
            assignments.append(assignment)            
    print(assignments)
    # Update if item with same value exists, else append

    if not dirty:
        data["sequences"].append({
            "scene": scene, 
            "file": file, 
            "length": length, 
            "assigned": assignments
            })

    # Save the updated JSON back to the file
    with open(scenejson, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        