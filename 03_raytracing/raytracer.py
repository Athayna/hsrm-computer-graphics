from PIL import Image
from functools import reduce
import numpy as np
import time
import numbers

def extract(cond, x):
    if isinstance(x, numbers.Number):
        return x
    else:
        return np.extract(cond, x)

class vec3():
    def __init__(self, x, y, z):
        (self.x, self.y, self.z) = (x, y, z)
    def __mul__(self, other):
        return vec3(self.x * other, self.y * other, self.z * other)
    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
    def __abs__(self):
        return self.dot(self)
    def norm(self):
        mag = np.sqrt(abs(self))
        return self * (1.0 / np.where(mag == 0, 1, mag))
    def components(self):
        return (self.x, self.y, self.z)
    def extract(self, cond):
        return vec3(extract(cond, self.x),
                    extract(cond, self.y),
                    extract(cond, self.z))
    def place(self, cond):
        r = vec3(np.zeros(cond.shape), np.zeros(cond.shape), np.zeros(cond.shape))
        np.place(r.x, cond, self.x)
        np.place(r.y, cond, self.y)
        np.place(r.z, cond, self.z)
        return r
    def cross(self, other):
        a = ((self.y * other.z) - (self.z * other.y))
        b = ((self.z * other.x) - (self.x * other.z))
        c = ((self.x * other.y) - (self.y * other.x))
        return vec3(a, b, c)
rgb = vec3

L = vec3(5, 5, -10)        # Point light position
E = vec3(0, 0.35, -1)     # Eye position
FARAWAY = 1.0e39            # an implausibly huge distance

def raytrace(O, D, scene, bounce = 0):
    # O is the ray origin, D is the normalized ray direction
    # scene is a list of Sphere objects (see below)
    # bounce is the number of the bounce, starting at zero for camera rays

    distances = [s.intersect(O, D) for s in scene]
    nearest = reduce(np.minimum, distances)
    color = rgb(0, 0, 0)
    for (s, d) in zip(scene, distances):
        hit = (nearest != FARAWAY) & (d == nearest)
        if np.any(hit):
            dc = extract(hit, d)
            Oc = O.extract(hit)
            Dc = D.extract(hit)
            cc = s.light(Oc, Dc, dc, scene, bounce)
            color += cc.place(hit)
    return color

class Sphere:
    def __init__(self, center, r, diffuse, mirror = 0.5):
        self.c = center
        self.r = r
        self.diffuse = diffuse
        self.mirror = mirror

    def intersect(self, O, D):
        b = 2 * D.dot(O - self.c)
        c = abs(self.c) + abs(O) - 2 * self.c.dot(O) - (self.r * self.r)
        disc = (b ** 2) - (4 * c)
        sq = np.sqrt(np.maximum(0, disc))
        h0 = (-b - sq) / 2
        h1 = (-b + sq) / 2
        h = np.where((h0 > 0) & (h0 < h1), h0, h1)
        pred = (disc > 0) & (h > 0)
        return np.where(pred, h, FARAWAY)

    def diffusecolor(self, M):
        return self.diffuse

    def light(self, O, D, d, scene, bounce):
        M = (O + D * d)                         # intersection point
        N = (M - self.c) * (1. / self.r)        # normal
        toL = (L - M).norm()                    # direction to light
        toO = (E - M).norm()                    # direction to ray origin
        nudged = M + N * .0001                  # M nudged to avoid itself

        # Shadow: find if the point is shadowed or not.
        # This amounts to finding out if M can see the light
        light_distances = [s.intersect(nudged, toL) for s in scene]
        light_nearest = reduce(np.minimum, light_distances)
        seelight = light_distances[scene.index(self)] == light_nearest

        # Ambient
        color = rgb(0.05, 0.05, 0.05)

        # Lambert shading (diffuse)
        lv = np.maximum(N.dot(toL), 0)
        color += self.diffusecolor(M) * lv * seelight

        # Reflection
        if bounce < 2:
            rayD = (D - N * 2 * D.dot(N)).norm()
            color += raytrace(nudged, rayD, scene, bounce + 1) * self.mirror

        # Blinn-Phong shading (specular)
        phong = N.dot((toL + toO).norm())
        color += rgb(1, 1, 1) * np.power(np.clip(phong, 0, 1), 50) * seelight
        return color
    
    def rotate(self, pos, neg):
        if pos:
            cos_theta = np.cos(np.pi / 10)
            sin_theta = np.sin(np.pi / 10)
        elif neg:
            cos_theta = np.cos(-np.pi / 10)
            sin_theta = np.sin(-np.pi / 10)

        R = np.array([  [cos_theta,   0,  sin_theta   ],
                        [0,           1,  0           ],
                        [-sin_theta,  0,  cos_theta   ]])
        
        newCenter = R@np.array([self.c.x, self.c.y, self.c.z]).T
        self.c = vec3(newCenter[0], newCenter[1], newCenter[2])

class CheckeredPlane:
    def __init__(self, center, normal, diffuse, mirror=0.05):
        self.c = center
        self.n = normal
        self.diffuse = diffuse
        self.mirror = mirror

    def intersect(self, O, D):
        co = O - self.c
        t = -self.n.dot(co) / self.n.dot(D)
        return np.where((t > 0), t, FARAWAY)

    def diffusecolor(self, M):
        checker = ((M.x * 2).astype(int) % 2) == ((M.z * 2).astype(int) % 2)
        return self.diffuse * checker

    def light(self, O, D, d, scene, bounce):
        M = (O + D * d)                         # intersection point        # Usprung + Distanz * Strahl
        N = self.n                              # normal
        toL = (L - M).norm()                    # direction to light
        toO = (E - M).norm()                    # direction to ray origin
        nudged = M + N * .0001                  # M nudged to avoid itself  # damit er sich nicht selbst reflektiert, also sich nicht selbst nochmal schneidet (Strahl reflektiert an Objekt)

        # Shadow: find if the point is shadowed or not.
        # This amounts to finding out if M can see the light
        light_distances = [s.intersect(nudged, toL) for s in scene]
        light_nearest = reduce(np.minimum, light_distances)
        seelight = light_distances[scene.index(self)] == light_nearest # self = Objekt (z.B. Kugel), vergleicht, ob eigene Distanzen die nähsten sind??

        # Ambient
        color = rgb(0.05, 0.05, 0.05)

        # Lambert shading (diffuse)
        lv = np.maximum(N.dot(toL), 0)
        color += self.diffusecolor(M) * lv * seelight

        # Reflection
        if bounce < 2: # nur 1x reflektieren
            rayD = (D - N * 2 * D.dot(N)).norm()
            color += raytrace(nudged, rayD, scene, bounce + 1) * self.mirror # mirror = wie stark reflektiert es; dann addiert auf Farbe (aka dann neue Farbe)

        # Blinn-Phong shading (specular)
        phong = N.dot((toL + toO).norm())
        color += rgb(1, 1, 1) * np.power(np.clip(phong, 0, 1), 50) * seelight
        return color
    
    def rotate(self, pos, neg):
        pass

class Triangle:
    def __init__(self, a, b, c, diffuse, mirror = 0.5):
        self.a = a
        self.b = b
        self.c = c
        self.diffuse = diffuse
        self.mirror = mirror

    def intersect(self, O, D):
        # Berechnung 1 zu 1 aus Folien übernommen (Folie 30 - Ray-Triangle Intersection)
        u = self.b - self.a
        v = self.c - self.a
        w = O - self.a

        t = 1 / (D.cross(v).dot(u)) * (w.cross(u).dot(v))
        r = 1 / (D.cross(v).dot(u)) * (D.cross(v).dot(w))
        s = 1 / (D.cross(v).dot(u)) * (w.cross(u).dot(D))

        pred = (r >= 0) & (r <= 1) & (s >= 0) & (s <= 1) & (r + s <= 1) # nimmt nur Werte auf, an denen r,s zwischen 0,1 sind und r+s kleiner gleich 1
        return np.where(pred, t, FARAWAY)

    def diffusecolor(self, M):
        return self.diffuse

    def light(self, O, D, d, scene, bounce):
        M = (O + D * d)                         # intersection point        # Usprung + Distanz * Strahl
        N = self.a.cross(self.b)          # normal
        toL = (L - M).norm()                    # direction to light        # Richtung zum Licht
        toO = (E - M).norm()                    # direction to ray origin   # Richtung zum Ursprung
        nudged = M + N * .0001                  # M nudged to avoid itself  # damit er sich nicht selbst reflektiert, also sich nicht selbst nochmal schneidet (Strahl reflektiert an Objekt)

        # Shadow: find if the point is shadowed or not.
        # This amounts to finding out if M can see the light
        light_distances = [s.intersect(nudged, toL) for s in scene]
        light_nearest = reduce(np.minimum, light_distances)
        seelight = light_distances[scene.index(self)] == light_nearest # self = Objekt (z.B. Kugel), vergleicht, ob eigene Distanzen die nähsten sind??

        # Ambient
        color = rgb(0.05, 0.05, 0.05)

        # Lambert shading (diffuse)
        lv = np.maximum(N.dot(toL), 0)
        color += self.diffusecolor(M) * lv * seelight

        # Reflection
        if bounce < 2: # nur 1x reflektieren
            rayD = (D - N * 2 * D.dot(N)).norm()
            color += raytrace(nudged, rayD, scene, bounce + 1) * self.mirror # mirror = wie stark reflektiert es; dann addiert auf Farbe (aka dann neue Farbe)

        # Blinn-Phong shading (specular)
        phong = N.dot((toL + toO).norm())
        color += rgb(1, 1, 1) * np.power(np.clip(phong, 0, 1), 50) * seelight
        return color
    
    def rotate(self, pos, neg):
        if pos:
            cos_theta = np.cos(np.pi / 10)
            sin_theta = np.sin(np.pi / 10)
        elif neg:
            cos_theta = np.cos(-np.pi / 10)
            sin_theta = np.sin(-np.pi / 10)

        R = np.array([  [cos_theta,   0,  sin_theta   ],
                        [0,           1,  0           ],
                        [-sin_theta,  0,  cos_theta   ]])
        
        newA = R@np.array([self.a.x, self.a.y, self.a.z]).T
        self.a = vec3(newA[0], newA[1], newA[2])

        newB = R@np.array([self.b.x, self.b.y, self.b.z]).T
        self.b = vec3(newB[0], newB[1], newB[2])

        newC = R@np.array([self.c.x, self.c.y, self.c.z]).T
        self.c = vec3(newC[0], newC[1], newC[2])

scene = [Sphere(vec3(.75, .1, 2.25), .6, vec3(1, 0, 0)), # red sphere (right)
        Sphere(vec3(-.75, .1, 2.25), .6, vec3(0, 1, 0)), # green sphere (left)
        Sphere(vec3(0, 1.25, 2.25), .6, vec3(0, 0, 1)), # blue sphere (top)
        CheckeredPlane(vec3(0, -1, 0), vec3(0, 1, 0), vec3(1, 1, 1)),
        Triangle(vec3(-.75, .1, 2.25), vec3(.75, .1, 2.25), vec3(0, 1.25, 2.25), vec3(1, 1, 0))]

def render_scene(width, height, pos = False, neg = False):

    if pos or neg:
        for object in scene:
            object.rotate(pos, neg)

    r = float(width) / height
    # Screen coordinates: x0, y0, x1, y1.
    S = (-1, 1 / r + .25, 1, -1 / r + .25)
    x = np.tile(np.linspace(S[0], S[2], width), height)
    y = np.repeat(np.linspace(S[1], S[3], height), width)

    t0 = time.time()
    Q = vec3(x, y, 0)
    color = raytrace(E, (Q - E).norm(), scene)
    print ("Took", time.time() - t0)

    rgb = [Image.fromarray((255 * np.clip(c, 0, 1).reshape((height, width))).astype(np.uint8), "L") for c in color.components()]
    im = Image.merge("RGB", rgb)
    return np.array(im)
