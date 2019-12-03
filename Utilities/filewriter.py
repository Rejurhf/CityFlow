from datetime import datetime
import numpy as np
import json

def write3dArrayToFile(array3d):
  now = datetime.now()
  outFileName = "{}T{}".format(now.strftime("%Y-%m-%d"), now.strftime("%H%M%S"))

  np.save(outFileName, array3d)
  print("FW:", "Array saved to {}".format(outFileName))


def writeToJSON(data, fileName = "unknown"):
  now = datetime.now()
  outFileName = "{}_{}T{}.txt".format(fileName, now.strftime("%y%m%d"), now.strftime("%H%M%S"))

  with open(outFileName, 'w') as outFile:
    json.dump(data, outFile)
  print("FW:", "Saved to {} JSON file".format(outFileName))

def readFromJSON(inFileName):
  with open(inFileName) as inFile:
    data = json.load(inFile)
  print("FW:", "Data red from {} JSON file".format(inFileName))
  
  return data