import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from descartes import PolygonPatch
import numpy as np

def showPlot(X, Y, u, v, p, obstacles, titleText="no text", isTopView=True):
    # Plot the last figure on screen
    # calculate ratio of array dimensions 
    if len(u) < len(u[0]):
        lenRatio = len(u)/len(u[0])
        print("Big X", len(u), len(u[0]), lenRatio)
        fig = plt.figure(figsize=(60, int(lenRatio*60)), dpi=25)
    else:
        lenRatio = len(u[0])/len(u)
        
        print("Big Y", len(u), len(u[0]), lenRatio)
        fig = plt.figure(figsize=(int(lenRatio*60), 60), dpi=25)

    # fig = plt.figure(figsize=(60, 30), dpi=25)
    plt.contourf(X, Y, p, alpha=0.5)  # alpha - background intensity
    plt.tick_params(axis='both', which='major', labelsize=50)
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=50)
    plt.contour(X, Y, p)
    M = np.hypot(u, v)
    plt.quiver(X, Y, u, v, M, scale=1 / 0.02)  ##plotting velocity
    for obs in obstacles:
        ring_mixed = Polygon(obs["coordinates"])
        ax = fig.add_subplot(111)
        ring_patch = PolygonPatch(ring_mixed)
        ax.add_patch(ring_patch)     
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(titleText, fontsize=80)
    plt.show()
