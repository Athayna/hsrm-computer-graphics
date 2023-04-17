# 1 given are the following vectors x, y, and z in R^2
import numpy as np
x = np.array([3, 4])
y = np.array([5, 6])
z = np.array([7, 8])
## 1.1 inner product (dot product/scalar product) of x and y
print(f'{x} ⋅ {y} = {np.dot(x, y)}')
## 1.2 angle between x and z
print(f'angle between {x} and {z} = {np.arccos(np.dot(x, z) / (np.linalg.norm(x) * np.linalg.norm(z)))} rad')
## 1.3 outer product of x and y and then result multiplied by z
print(f'{x} ⊗ {y} = {np.outer(x, y)}')
print(f'{x} ⊗ {y} ⋅ {z} = {np.dot(np.outer(x, y), z)}')
## 1.4 rank of outer product of x and y
print(f'rank of {x} ⊗ {y} = {np.linalg.matrix_rank(np.outer(x, y))}')

# 2 given are the following vectors x, y, and z in R^3
x = np.array([1, 2, 3])
y = np.array([4, 5, 6])
z = np.array([6, 9, 12])
## 2.1 length of x
print(f'|{x}| = {np.linalg.norm(x)}')
## 2.2 angle between x and y
print(f'angle between {x} and {y} = {np.arccos(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y)))} rad')
## 2.3 area of triangle formed by x and y
print(f'area of triangle formed by {x} and {y} = {np.linalg.norm(np.cross(x, y)) / 2} unit^2')
## 2.5 are the vectors x, y, and z linearly independent?
print(f'{np.linalg.matrix_rank(np.matrix([x, y, z])) == 3}')
## 2.6 rank of matrix formed by x, y, and z
print(f'rank of {np.matrix([x, y, z])} = {np.linalg.matrix_rank(np.matrix([x, y, z]))}')

# 3 plot regions that belong to all vectors x e R^2 with |x| <= 1 for the following four norms
import matplotlib.pyplot as plt
norm1 = lambda x: np.linalg.norm(x, ord=0)
norm2 = lambda x: np.linalg.norm(x, ord=1)
norm3 = lambda x: np.linalg.norm(x, ord=2)
norm4 = lambda x: np.linalg.norm(x, ord=np.inf)
norms = [norm1, norm2, norm3, norm4]
for norm in norms:
    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros(X.shape)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = norm(np.array([X[i, j], Y[i, j]]))
    plt.contour(X, Y, Z, levels=[1])
plt.show()

# 4 given are the following matrices r1 and r2 in R^2x2
alpha = 0
r1 = np.matrix([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha), np.cos(alpha)]])
r2 = np.matrix([[np.sin(alpha), np.cos(alpha)], [np.cos(alpha), -np.sin(alpha)]])
## 4.1 determinant of the matrices r1 and r2
print(f'det({r1}) = {np.linalg.det(r1)}')
print(f'det({r2}) = {np.linalg.det(r2)}')
## 4.2 are the matrices r1 and r2 orthogonal?
print(f'{np.allclose(np.dot(r1, r1.T), np.eye(2))}')
print(f'{np.allclose(np.dot(r2, r2.T), np.eye(2))}')
## 4.3 are the matrices r1 and r2 invertible?
print(f'{np.linalg.det(r1) != 0}')
print(f'{np.linalg.det(r2) != 0}')
## 4.4 what is the difference between the matrices r1 and r2?
print('r1 is a rotation matrix, r2 is a rotation and reflection matrix')
## 4.5 what are the eigenvalues and eigenvectors of the matrices r1 and r2?
print(f'eigenvalues of {r1} = {np.linalg.eig(r1)[0]}')
print(f'eigenvectors of {r1} = {np.linalg.eig(r1)[1]}')
print(f'eigenvalues of {r2} = {np.linalg.eig(r2)[0]}')
print(f'eigenvectors of {r2} = {np.linalg.eig(r2)[1]}')

# 5 given are the following complex numbers c1 and c2
c1 = 1 + 2j
c2 = 3 + 4j
## 5.1 calculate the conjugate of c1 and c2
print(f'conjugate of {c1} = {np.conj(c1)}')
print(f'conjugate of {c2} = {np.conj(c2)}')
## 5.2 calculate c3 = c1 * c2
print(f'{c1} * {c2} = {c1 * c2}')
## 5.3 calculate c4 = c2 * conj(c2)
print(f'{c2} * {np.conj(c2)} = {c2 * np.conj(c2)}')
## 5.4 calculate c5 = c1 / c2
print(f'{c1} / {c2} = {c1 / c2}')
## 5.5 calculate the euler form of c1 and c2
print(f'euler form of {c1} = {np.abs(c1)} * e^({np.angle(c1)} * i)')
print(f'euler form of {c2} = {np.abs(c2)} * e^({np.angle(c2)} * i)')

# 6 calculate the derivative of the following functions
import sympy as sp
## 6.1 y = 2x^3 + 3x^2 + 17x + 41 with respect to x
x = sp.symbols('x')
y = 2 * x ** 3 + 3 * x ** 2 + 17 * x + 41
print(f'derivative of {y} = {sp.diff(y)}')
## 6.2 y = 1 / (1 + e^-x) with respect to x
y = 1 / (1 + sp.exp(-x))
print(f'derivative of {y} = {sp.diff(y)}')
## 6.3 y = |x| with respect to x
y = sp.Abs(x)
print(f'derivative of {y} = {sp.diff(y)}')
## 6.4 x^x with respect to x
y = x ** x
print(f'derivative of {y} = {sp.diff(y)}')
## 6.5 z = sin(x) * cos(y) with respect to x and y
y = sp.symbols('y')
z = sp.sin(x) * sp.cos(y)
print(f'derivative of {z} with respect to x = {sp.diff(z, x)}')
print(f'derivative of {z} with respect to y = {sp.diff(z, y)}')
## 6.6 (x, y) = (sin(r) * s, cos(s^2) * r^2) with respect to r and s
r = sp.symbols('r')
s = sp.symbols('s')
x = sp.sin(r) * s
y = sp.cos(s ** 2) * r ** 2
print(f'derivative of {x} with respect to r = {sp.diff(x, r)}')
print(f'derivative of {x} with respect to s = {sp.diff(x, s)}')
print(f'derivative of {y} with respect to r = {sp.diff(y, r)}')
print(f'derivative of {y} with respect to s = {sp.diff(y, s)}')
