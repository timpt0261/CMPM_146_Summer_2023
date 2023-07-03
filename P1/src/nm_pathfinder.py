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

    print("EBIC COORDS", source_point, destination_point)

    source_point =  (310, 337)
    destination_point = (69, 434)
    path = []
    # mapping of boxes to (backpointer to previous box), used to find the path
    boxes = {}
    # p is the current from the src
    # q will be the current from the
    src_box = find_box(source_point, mesh)
    dst_box = find_box(destination_point, mesh)

    p_box = src_box

    if (src_box is None or dst_box is None):
        print("No path!")
        path.append(source_point)
        path.append(destination_point)
        return path, boxes.keys()

    boxes[src_box] = True
    p_src = source_point
    p_dst = None
    frontier = []  # takes in a (priority, {stuff})

    # stuff has:
    # current box
    # destination type (src or dst) to distinguish forward or back

    heappush(frontier, (0, src_box, destination_point))
    heappush(frontier, (0, dst_box, source_point))

    forward_points = {src_box : source_point}
    backward_points = {dst_box : destination_point}


    # used to track edge costs
    forward_cost = {src_box: 0}
    backward_cost = {dst_box: 0}

    # track backpointers
    forward_prev = {}
    backward_prev = {}

    forward_prev[src_box] = None
    backward_prev[dst_box] = None

    pathFound = False
    while (frontier):
        p_priority, p_box, curr_goal = heappop(frontier)
        boxes[p_box] = True

        if ((curr_goal == destination_point and p_box in backward_prev)
            or (curr_goal == source_point and p_box in forward_prev)):
            # boxes = forward_prev.copy()
            # boxes.update(backward_prev)
            # q_path = construct_path(forward_prev[p_box], src_box, backward_prev)
            # print(q_path)
            # # path = p_path + q_path.reverse()
            pathFound = True
            break

        # if ((q_box, q_src) in forward_prev.values()):
        #     boxes = forward_prev.copy()
        #     boxes.update(backward_prev)

        #     p_path = construct_path((p_box, p_src), dst_box, forward_prev)
        #     print(p_path)
        #     q_path = construct_path(forward_prev[p_box], src_box, backward_prev)
        #     print(q_path)
        #     # path = p_path + q_path.reverse()
        #     pathFound = True
        #     break

        # if ((p_box, p_src) in backward_prev.values()):
        #     boxes = forward_prev.copy()
        #     boxes.update(backward_prev)

        #     q_path = construct_path((q_box, q_src), dst_box, backward_prev)
        #     p_path = construct_path(backward_prev[q_box], src_box, forward_prev)

        #     print(p_path)
        #     print(q_path)
        #     # path = p_path + q_path.reverse()
        #     pathFound = True
        #     break
        points, prev, cost_so_far = (forward_points, forward_prev, forward_cost) if (curr_goal == destination_point) else (backward_points, backward_prev, backward_cost)
        p_src = points[p_box]

        for neighbor in mesh["adj"][p_box]:
            p_dst = find_next_point(p_src, p_box, neighbor)
            # print(p_dst)

            link_cost = euclidean(p_src, p_dst)
            new_cost = cost_so_far[p_box] + link_cost
            if (neighbor not in prev or new_cost < cost_so_far[neighbor]):

                cost_so_far[neighbor] = new_cost
                prev[neighbor] = p_box
                points[neighbor] = p_dst

                p_priority = new_cost + euclidean(p_dst, curr_goal)
                heappush(frontier, (p_priority, neighbor, curr_goal))


        # for neighbor in mesh["adj"][q_box]:
        #     q_dst = find_next_point(q_src, q_box, neighbor)
        #     link_cost = euclidean(q_src, q_dst)
        #     new_cost = backward_cost[q_box] + link_cost
        #     if (neighbor not in backward_prev or new_cost < backward_cost[neighbor]):
        #         backward_cost[neighbor] = new_cost
        #         q_priority = new_cost + euclidean(q_dst, p_src)
        #         heappush(q_frontier, (q_priority, (neighbor, q_dst)))
        #         backward_prev[neighbor] = (q_box, q_dst)

    if (pathFound):
        print("Found Path")
        assert(forward_points[src_box] == source_point)
        assert(backward_points[dst_box] == destination_point)


        f_path = construct_path(p_box, src_box, forward_prev, forward_points)
        b_path = construct_path(p_box, dst_box, backward_prev, backward_points, None, False)
        if (len(f_path) > 0 and len(b_path) > 0):
            if (f_path[-1] == b_path[0]):
                f_path = f_path[:-1]

        path = f_path + b_path
        # path += [destination_point]

        assert(path[0] == source_point)
        assert(path[-1] == destination_point)
        print(source_point, destination_point)
        print(f_path)
        print(b_path)
        print(len(path), len(set(path)))


        assert(len(path) == len(set(path)))

        check, b = astar_find_path(source_point, destination_point, mesh)

        print(source_point, destination_point)
        print(len(check), len(set(check)))

        # checka, b = astar_find_path(destination_point,source_point, mesh)

        # print(destination_point, source_point)
        # print(len(checka), len(set(checka)))

        # print(path_len(path), path_len(check), path_len(checka))
        print(path_len(path), path_len(check))

        # print(check)
        # assert(check == path)
        path = check


    else:
        path.append(source_point)
        path.append(destination_point)
        print("No path!")

    return path, boxes.keys()

def path_len(path):
    ret = 0
    pathlen = len(path)
    if (pathlen > 2):
        for i in range(1, pathlen):
            ret += euclidean(path[i - 1], path[i])
    return ret

def construct_path(last_box, target_box, prev_dict, points_dict, last_point=None, reverse=True):
    """
    Constructs a path from the given box_point to the target_box using the prev_dict.

    Args:
        last_box: The current box and point tuple (box, point)
        target_box: The target box to reach
        prev_dict: Dictionary containing the back pointers of each box
        points_dict: Dictionary mapping boxes to the points they contain
        last_point: the point in last_box (destination point)

    Returns:
        The constructed path as a list of points from box_point to target_box
    """
    path = []
    curr_box = last_box

    # Initialize with a point first...
    if (last_point is not None):
        path.append(last_point)
    else:
        if (curr_box != target_box):
            path.append(points_dict[curr_box])
            curr_box = prev_dict[curr_box]

    while curr_box != target_box:
        if (path[-1] != points_dict[curr_box]): # remove duplicates
            path.append(points_dict[curr_box])
        curr_box = prev_dict[curr_box] # (290, 625) (108, 525)

    if (len(path) > 0 and path[-1] != points_dict[target_box]):
        path.append(points_dict[target_box])

    if (reverse):
        path.reverse()

    return path



def find_box(p, mesh):
    for box in mesh["boxes"]:
        if (check_in_box(p, box)):
            return box
    return None


def check_in_box(p, box):
    return (box[0] <= p[0] <= box[1]) and (box[2] <= p[1] <= box[3])


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



def astar_find_path(source_point, destination_point, mesh):
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

    if (src_box is None or dst_box is None):
        print("No path!")
        path.append(source_point)
        path.append(destination_point)
        return path, boxes.keys()

    boxes[src_box] = True
    p_src = source_point
    p_dst = None
    frontier = []  # takes in a (priority, {stuff})

    # stuff has:
    # current box
    # destination type (src or dst) to distinguish forward or back

    heappush(frontier, (0, p_box))
    detail_points = {src_box : source_point}

    # used to track edge costs
    forward_cost = {src_box: 0}

    # track backpointers
    forward_prev = {}
    backward_prev = {}

    forward_prev[p_box] = None
    backward_prev[q_box] = None
    a = 0
    pathFound = True
    while (frontier):
        p_priority, p_box = heappop(frontier)
        boxes[p_box] = True

        if (p_box == dst_box):
            pathFound = True
            break
        p_src = detail_points[p_box]
        for neighbor in mesh["adj"][p_box]:
            p_dst = find_next_point(p_src, p_box, neighbor)

            link_cost = euclidean(p_src, p_dst)
            new_cost = forward_cost[p_box] + link_cost
            if (neighbor not in forward_prev or new_cost < forward_cost[neighbor]):

                forward_cost[neighbor] = new_cost
                forward_prev[neighbor] = p_box
                detail_points[neighbor] = p_dst

                p_priority = new_cost + 0*euclidean(p_dst, destination_point)
                heappush(frontier, (p_priority, neighbor))

            if (a == 1):
                print(forward_cost)
                print(frontier)
            a+=1


    if (pathFound):
        assert(detail_points[src_box] == source_point)
        path = construct_path(p_box, src_box, forward_prev, detail_points, destination_point)
        assert(path[0] == source_point)
        assert(path[-1] == destination_point)
        assert(len(path) == len(set(path)))

    else:
        path.append(source_point)
        path.append(destination_point)
        print("No path!")

    return path, boxes.keys()
