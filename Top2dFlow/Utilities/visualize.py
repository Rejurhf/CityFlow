import matplotlib.pyplot as plt
import numpy as np

def showPlot(X, Y, u, v, p, obstacles, titleText="no text"):
    # Plot the last figure on screen
    fig = plt.figure(figsize=(60, 30), dpi=25)
    plt.contourf(X, Y, p, alpha=0.5)  # alpha - background intensity
    plt.tick_params(axis='both', which='major', labelsize=80)
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=80)
    plt.contour(X, Y, p)
    M = np.hypot(u, v)
    plt.quiver(X, Y, u, v, M, scale=1 / 0.02)  ##plotting velocity
    # plt.scatter(X, Y, color='r')
    for obstacle in obstacles:
        plt.broken_barh([(obstacle[0], obstacle[1])], (obstacle[2], obstacle[3]), 
            facecolors='grey', alpha=0.8)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(titleText, fontsize=80)
    plt.show()
