# 1 Find the camera coordinate system f, s, u which corresponds to the e, c, up.
import numpy as np
e = np.array([0, 3, 4]) # camera position (eye)
c = np.array([0, 0, 0]) # gaze direction (center)
up = np.array([0, 2, 0]) # up direction

f = c - e / np.linalg.norm(c - e) # forward direction
s = np.cross(f, up) / np.linalg.norm(np.cross(f, up)) # right direction
u = np.cross(s, f) # new up direction

print(f'f = {f}')
print(f's = {s}')
print(f'u = {u}')

# 2 Find, if possible, the first intersection of the ray r(t) = (0, 1, 1) + t * (0, 0, -1) with:
o = np.array([0, 1, 1])
d = np.array([0, 0, -1])
def r(t):
    return o + t * d

## 2.1 the sphere with center c = (0, 0, -4) and radius 2
c = np.array([0, 0, -4])
radius = 2
t = []
t.append(np.dot(c - o, d) + np.sqrt(np.dot(c - o, d)**2 - np.dot(o - c, o - c) + radius**2))
t.append(np.dot(c - o, d) - np.sqrt(np.dot(c - o, d)**2 - np.dot(o - c, o - c) + radius**2))
print(f'{r(min(t))}')

## 2.2 the plane through the point e = (0, 0, -4) with normal n = (1/3)*(1, 1, 1)
e = np.array([0, 0, -4])
n = np.array([1/3, 1/3, 1/3])
t = np.dot(e - o, n) / np.dot(d, n)
print(f'{r(t)}')

## 2.3 the triangle with vertices a = (-1, 0, -2), b = (1, 0, -4), c = (0, -2, -3)
a = np.array([-1, 0, -2])
b = np.array([1, 0, -4])
c = np.array([0, -2, -3])
n = np.cross(b - a, c - a) / np.linalg.norm(np.cross(b - a, c - a))
t = np.dot(a - o, n) / np.dot(d, n)
print(f'{r(t)}')

# 3 Implement a simple ray tracer with the pseudo code on slide 18 of the third lecture
from PIL import Image

width, height = 400, 400
fov = np.pi / 4
e = np.array([0, 1.8, 10])
c = np.array([0, 3, 0])
up = np.array([0, 1, 0])

image = Image.new("L", (width, height))

class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def intersectionParameter(self, ray):
        n = np.cross(b - a, c - a) / np.linalg.norm(np.cross(b - a, c - a))
        return np.dot(a - ray.o, n) / np.dot(ray.d, n)

class Sphere:
    def __init__(self, c, radius):
        self.c = c
        self.radius = radius

    def intersectionParameter(self, ray):
        t = []
        root = np.dot(c - ray.o, ray.d)**2 - np.dot(ray.o - c, ray.o - c) + radius**2
        if root >= 0:
            t.append(np.dot(c - ray.o, ray.d) + np.sqrt(np.dot(c - ray.o, ray.d)**2 - np.dot(ray.o - c, ray.o - c) + radius**2))
            t.append(np.dot(c - ray.o, ray.d) - np.sqrt(np.dot(c - ray.o, ray.d)**2 - np.dot(ray.o - c, ray.o - c) + radius**2))
            return min(t)
        else:
            return np.inf

class Ray:
    def __init__(self, o, d):
        self.o = o
        self.d = d

def primary_ray(x, y):
    # use the eye point e as origin o
    o = e
    # choose e, c, up to define a camera coordinate system
    f = c - e / np.linalg.norm(c - e)
    s = np.cross(f, up) / np.linalg.norm(np.cross(f, up))
    u = np.cross(s, f)
    # choose field of view (FOV) and aspect ratio (r) to determine image h and w
    alpha = fov / 2
    r = width / height
    h = 2 * np.tan(alpha)
    w = h * r
    # compute 3D position of pixel (x, y) in camera coordinates
    p = f + w * (x / width - 0.5) * s + h * (y / height - 0.5) * u
    # compute ray direction d
    d = p / np.linalg.norm(p)
    return Ray(o, d)

# create a list of all objects in the scene
objectlist = []
objectlist.append(Triangle(np.array([-1, 0, -2]), np.array([1, 0, -4]), np.array([0, -2, -3])))
objectlist.append(Sphere(np.array([-1, 0, -2]), 2))
objectlist.append(Sphere(np.array([1, 0, -4]), 2))
objectlist.append(Sphere(np.array([0, -2, -3]), 2))

for x in range(width):
  for y in range(height):
      ray = primary_ray(x, y)
      maxdist = float('inf')
      color = 255
      for object in objectlist:
        hitdist = object.intersectionParameter(ray)
        if hitdist and hitdist < maxdist:
            maxdist = hitdist
            color = int(255 * (1 - maxdist / 10))
      image.putpixel((x,y), color)

image.save("02_raytracing/raytraced_image.png")
