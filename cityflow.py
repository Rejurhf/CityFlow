import json

print("Open config file")

# Open buildings file
with open("config.txt") as inFile:
  buildingList = json.load(inFile)

print(buildingList["name"])
