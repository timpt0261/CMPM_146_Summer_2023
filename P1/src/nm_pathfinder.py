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

    path = []
    boxes = {} # mapping of boxes to (backpointer to previous box), used to find the path

    # p is the current from the src
    # q will be the current from the



    src_box = find_box(source_point, mesh)
    dst_box = find_box(destination_point, mesh)

    p_box = src_box
    q_box = dst_box

    if (p_box is None or q_box is None):
        return path, boxes.keys()

    p_src = source_point
    p_dst = None

    q_src = destination_point
    q_dst = None

    p_frontier = [] # takes in a (priority, {stuff})


    # stuff has:
    # current box
    # current local source point


    heappush(p_frontier, (0, (p_box, p_src)))
    costsofar = { p_box : 0 }


    # intialize current box as visited
    boxes[p_box] = None # I came from nowhere to the source!

    pathfound = False
    while (p_frontier):
        priority, (p_box, p_src) = heappop(p_frontier)

        if(p_box == q_box):
            pathfound = True
            break

        for neighbor in mesh["adj"][p_box]:
            p_dst = find_next_point(p_src, p_box, neighbor)
            link_cost = euclidean(p_src, p_dst)
            new_cost = costsofar[p_box] + link_cost

            if (neighbor not in boxes or new_cost < costsofar[neighbor]):
                costsofar[neighbor] = new_cost
                priority = new_cost + euclidean(p_dst, q_src)
                heappush(p_frontier, (priority, (neighbor, p_dst)))
                boxes[neighbor] = (p_box, p_dst)

                # path.append((boxes[0], boxes[1]))

    if (pathfound):
        path.append(destination_point)
        curr = dst_box
        while (curr != src_box):
            path.append(boxes[curr][1])
            curr = boxes[curr][0]
        path.append(source_point)
        path.reverse()

    return path, boxes.keys()

def find_box(p, mesh):
    for box in mesh["boxes"]:
        if (check_in_box(p, box)):
            return box
    return False


def check_in_box(p, box):
    """
    """
    return (box[0] <= p[0] < box[1]) and (box[2] <= p[1] < box[3])


def euclidean(p1=(0, 0), p2=(0, 0)):
    # Euclidean Hueistic
    return sqrt(pow((p2[1] - p1[1]), 2) + pow((p2[0] - p1[0]), 2))

# p is the current point
def find_next_point(n, srcbox, dstbox):
    ret_x = n[0]
    ret_y = n[1]

    # check if left and right meet
    if (srcbox[0] == dstbox[1] or srcbox[1] == dstbox[0]):
        ret_x = srcbox[0] if (srcbox[0] == dstbox[1]) else srcbox[1]

        # y range (max of the top, the min of the bottom)
        top = max(srcbox[2], dstbox[2]) # b1y1 , b2y1
        bottom = min(srcbox[3], dstbox[3]) # b1y2 , b2y2
        ret_y = top if (n[1] <= top) else bottom if (bottom <= n[1]) else n[1]

    # check if top and down meet
    if (srcbox[2] == dstbox[3] or srcbox[3] == dstbox[2]):
        ret_y = srcbox[2] if (srcbox[2] == dstbox[3]) else srcbox[3]

        # x range (Max of the left, the min of the right)
        left = max(srcbox[0], dstbox[0]) # b1x1 , b2x1
        right = min(srcbox[1], dstbox[1]) # b1x2 , b2x2
        ret_x = left if (n[0] <= left) else right if (right <= n[0]) else n[0]

    return (ret_x, ret_y)

def transtion_cost( p_point, q_point):
    distance = sqrt(pow((q_point[1] - p_point[1]), 2) + pow((q_point[0] - p_point[0]), 2))
    average_cost = ()/2
    return distance