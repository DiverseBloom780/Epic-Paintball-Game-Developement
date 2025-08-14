import math, pygame

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def length(vec):
    x, y = vec
    return math.hypot(x, y)

def norm(vec):
    x, y = vec
    l = length(vec) or 1.0
    return (x / l, y / l)

def dot(a, b): return a[0]*b[0] + a[1]*b[1]

def angle_deg(a, b):
    # angle between vectors in degrees
    na, nb = norm(a), norm(b)
    d = clamp(dot(na, nb), -1, 1)
    return math.degrees(math.acos(d))

def line_of_sight(start, end, solids, step=8):
    # Sample along the line to see if intersects any wall rect
    vx, vy = end[0]-start[0], end[1]-start[1]
    dist = max(1, int(math.hypot(vx, vy) / step))
    for i in range(1, dist+1):
        x = start[0] + vx * i / dist
        y = start[1] + vy * i / dist
        p = pygame.Rect(x-2, y-2, 4, 4)
        if any(p.colliderect(r) for r in solids):
            return False
    return True
