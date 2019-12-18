def getDistanceFromPointToLine(p, q, point, mode="y"):
  # p and q are points of the line
  # point is point to measure distance in y or z
  # Calculate line equation ax+by=c +> y=(c-ax)/b
  
  if mode == "y":
    a = q[1] - p[1]
    b = p[0] - q[0]
    c = a*p[0] + b*p[1]
    curY = (c-(a*point[0]))/b if b != 0 else a

    return abs(curY - point[1])
  elif mode == "z":
    a = q[2] - p[2]
    b = p[0] - q[0]
    c = a*p[0] + b*p[2]
    curY = (c-(a*point[0]))/b if b != 0 else a
    
    return abs(curY - point[2])




