import numpy as np

# get the point on an arc at the given angle
def get_arc_point(angle, radius):
    return (
        radius * np.cos(np.deg2rad(angle)),
        radius * np.sin(np.deg2rad(angle)),
    )


# draw an arc
def draw_arc(start_angle, end_angle, radius, step=10):
    points = []
    for angle in np.arange(start_angle, end_angle + step, step):
        x = radius * np.cos(np.deg2rad(angle))
        y = radius * np.sin(np.deg2rad(angle))
        points.append((x, y))
    return points


# roate the points by the required angle
def rotate(points, angle):
    return [
        [
            x * np.cos(np.deg2rad(angle)) - y * np.sin(np.deg2rad(angle)),
            x * np.sin(np.deg2rad(angle)) + y * np.cos(np.deg2rad(angle)),
        ]
        for x, y in points
    ]


# move the points out to the distance at the requited angle
def translate(points, distance, angle):
    return [
        [
            x + distance * np.cos(np.deg2rad(angle)),
            y + distance * np.sin(np.deg2rad(angle)),
        ]
        for x, y in points
    ]


# flip the y coordinate
def flip_y(points):
    return [[x, -y] for x, y in points]


def flip_x(points):
    return [[-x, y] for x, y in points]


def create_pad(radius, angle, name):
    return {
        "x": radius * np.cos(np.deg2rad(angle)),
        "y": radius * np.sin(np.deg2rad(angle)),
        "name": name,
    }


def create_silk(point, text):
    return {
        "x": point[0],
        "y": point[1],
        "text": text,
    }


def create_via(point):
    return {"x": point[0], "y": point[1]}


def create_track(points):
    return [{"x": x, "y": y} for x, y in points]


def optimize_points(points):
    # follow the line and remove points that are in the same direction as the previous poin
    # keep doing this until the direction changes significantly
    # this is a very simple optimization that removes a lot of points
    # it's not perfect but it's a good start
    optimized_points = []
    for i in range(len(points)):
        if i == 0:
            optimized_points.append(points[i])
        else:
            vector1 = np.array(points[i]) - np.array(points[i - 1])
            vector2 = np.array(points[(i + 1) % len(points)]) - np.array(points[i])
            length1 = np.linalg.norm(vector1)
            length2 = np.linalg.norm(vector2)
            if length1 > 0 and length2 > 0:
                dot = np.dot(vector1, vector2) / (length1 * length2)
                # clamp dot between -1 and 1
                dot = max(-1, min(1, dot))
                angle = np.arccos(dot)
                if angle > np.deg2rad(5):
                    optimized_points.append(points[i])
    print("Optimised from {} to {} points".format(len(points), len(optimized_points)))
    return optimized_points


def chaikin(points, iterations):
    if iterations == 0:
        return points
    l = len(points)
    smoothed = []
    for i in range(l - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        smoothed.append([0.95 * x1 + 0.05 * x2, 0.95 * y1 + 0.05 * y2])
        smoothed.append([0.05 * x1 + 0.95 * x2, 0.05 * y1 + 0.95 * y2])
    smoothed.append(points[l - 1])
    return chaikin(smoothed, iterations - 1)
