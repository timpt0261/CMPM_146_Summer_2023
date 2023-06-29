from math import inf, sqrt, pow
from heapq import heappop, heappush


def find_path(source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    Q = {}
    heappush(heap, source_point)
    path = []
    boxes = {}

    for box in mesh["boxes"]:  # initlize boxes as unvisited
        boxes.update({box: False})

    path.append(source_point)  # intialize path
    # intialize current box as visited
    boxes[find_box(current_destination, mesh)] = true

    while (len(Q) != 0):
        u = heappop(Q)
        for child in mesh["adj"][u]:
            if (boxes[child] == False):
                boxes[child] = True
                pred[child] = u
                heappush(Q, child)

    return path, boxes.keys()


def find_neighbor(p, mesh):
    return me


def find_box(p, mesh):
    for box in mesh["boxes"]:
        if (check_in_box(p, box)):
            return box
    return False


def check_in_box(p, box):
    return (box[0] <= p[0] < box[2]) and (box[1] <= p[1] < box[3])


def euclidean(p1=(0, 0), p2=(0, 0)):
    # Euclidean Hueistic
    return sqrt(pow((p2[1] - p1[1]), 2) + pow((p2[0] - p1[0]), 2))
