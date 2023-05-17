# 1 determine the 3x3 matrix A for picture 1 and 2
import numpy as np

T1 = np.array([
    [1, 0, -4],
    [0, 1, -1],
    [0, 0, 1]
])

R = np.array([
    [np.cos(45), -np.sin(45), 0],
    [np.sin(45), np.cos(45), 0],
    [0, 0, 1]
])

S = np.array([
    [np.sqrt(2), 0, 0],
    [0, np.sqrt(2), 0],
    [0, 0, 1]
])

T2 = np.array([
    [1, 0, 4],
    [0, 1, 4],
    [0, 0, 1]
])

A = T2 @ S @ R @ T1
print(A)
