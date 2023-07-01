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
    # mapping of boxes to (backpointer to previous box), used to find the path
    boxes = {}
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
    p_frontier = []  # takes in a (priority, {stuff})
    q_frontier = []

    # stuff has:
    # current box
    # current local source point

    heappush(p_frontier, (0, (p_box, p_src)))
    heappush(q_frontier, (0, (q_box, q_src)))

    foward_cost = {p_box: 0}
    backward_cost = {q_box: 0}

    foward_prev = {}
    backward_prev = {}

    foward_prev[p_box] = None
    backward_prev[q_box] = None

    p_path = []
    q_path = []

    pathFound = False
    while (p_frontier and q_frontier):
        p_priority, (p_box, p_src) = heappop(p_frontier)
        q_priority, (q_box, q_src) = heappop(q_frontier)

        if ((q_box, q_src) in foward_prev.values()):
            boxes = foward_prev.copy()
            boxes.update(backward_prev)

            p_path = construct_path((p_box, p_src), dst_box, foward_prev)
            print(p_path)
            q_path = construct_path(foward_prev[p_box], src_box, backward_prev)
            print(q_path)
            # path = p_path + q_path.reverse()
            pathFound = True
            break

        if ((p_box, p_src) in backward_prev.values()):
            boxes = foward_prev.copy()
            boxes.update(backward_prev)

            q_path = construct_path((q_box, q_src), dst_box, backward_prev)
            p_path = construct_path(backward_prev[q_box], src_box, foward_prev)

            print(p_path)
            print(q_path)
            # path = p_path + q_path.reverse()
            pathFound = True
            break

        for neighbor in mesh["adj"][p_box]:
            p_dst = find_next_point(p_src, p_box, neighbor)
            link_cost = euclidean(p_src, p_dst)
            new_cost = foward_cost[p_box] + link_cost
            if (neighbor not in foward_prev or new_cost < foward_cost[neighbor]):
                foward_cost[neighbor] = new_cost
                p_priority = new_cost + euclidean(p_dst, q_src)
                heappush(p_frontier, (p_priority, (neighbor, p_dst)))
                foward_prev[neighbor] = (p_box, p_dst)

        for neighbor in mesh["adj"][q_box]:
            q_dst = find_next_point(q_src, q_box, neighbor)
            link_cost = euclidean(q_src, q_dst)
            new_cost = backward_cost[q_box] + link_cost
            if (neighbor not in backward_prev or new_cost < backward_cost[neighbor]):
                backward_cost[neighbor] = new_cost
                q_priority = new_cost + euclidean(q_dst, p_src)
                heappush(q_frontier, (q_priority, (neighbor, q_dst)))
                backward_prev[neighbor] = (q_box, q_dst)

    if (pathFound):
        print("Found Path")

    return path, boxes.keys()


def construct_path(box_point, target_box, prev_dict):
    """
    Constructs a path from the given box_point to the target_box using the prev_dict.

    Args:
        box_point: The current box and point tuple (box, point)
        target_box: The target box to reach
        prev_dict: Dictionary containing the previous box and point for each box

    Returns:
        The constructed path as a list of points from box_point to target_box
    """
    path = []
    while box_point[0] != target_box:
        path.append(box_point[1])
        print(prev_dict[box_point[0]])
        box_point = prev_dict[box_point[0]]
    path.append(box_point[1])
    return path


def find_box(p, mesh):
    for box in mesh["boxes"]:
        if (check_in_box(p, box)):
            return box
    return False


def check_in_box(p, box):
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
        top = max(srcbox[2], dstbox[2])  # b1y1 , b2y1
        bottom = min(srcbox[3], dstbox[3])  # b1y2 , b2y2
        ret_y = top if (n[1] <= top) else bottom if (bottom <= n[1]) else n[1]

    # check if top and down meet
    if (srcbox[2] == dstbox[3] or srcbox[3] == dstbox[2]):
        ret_y = srcbox[2] if (srcbox[2] == dstbox[3]) else srcbox[3]

        # x range (Max of the left, the min of the right)
        left = max(srcbox[0], dstbox[0])  # b1x1 , b2x1
        right = min(srcbox[1], dstbox[1])  # b1x2 , b2x2
        ret_x = left if (n[0] <= left) else right if (right <= n[0]) else n[0]

    return (ret_x, ret_y)
