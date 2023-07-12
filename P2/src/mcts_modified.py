from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_factor = 2.0


def ucb(node, parent_visits, player, identity):

    # print(f"Node wins: {node.wins} Node visits: {node.visits}")

    if identity == player:
        exploitation = node.wins / node.visits
    else:
        exploitation = (1 - node.wins / node.visits)

    exploration = explore_factor * sqrt(log(parent_visits) / node.visits)
    return exploitation + exploration


def find_best_child(node, board, state, identity):
    best_child = None
    best_ucb = float('-inf')
    current_player = board.current_player(state)

    for child in node.child_nodes.values():
        child_ucb = ucb(child, node.visits, current_player, identity)
        if child_ucb > best_ucb:
            best_ucb = child_ucb
            best_child = child

    return best_child


def traverse_nodes(node, board, state, identity):
    """Traverses the tree until the end criterion are met.

    Args:
        node: A tree node from which the search is traversing.
        board: The game setup.
        state: The state of the game.
        identity: The bot's identity, either 'red' or 'blue'.

    Returns: A node from which the previous stage of the search can proceed.
    """
    # remove recursion

    if node.is_terminal(board, state):
        # print("Is terminal ")
        return node

    if node.is_expanded():
        # print("Node is expanded ")
        child_node = expand_leaf(node, board, state)
        return child_node
    # print("looking for best child")

    best_child = find_best_child(node, board, state, identity)

    return best_child


def expand_leaf(node, board, state):
    """Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node: The node for which a child will be added.
        board: The game setup.
        state: The state of the game.

    Returns: The added child node.
    """
    # print("Expanding current node")
    untried_actions = node.untried_actions
    action = choice(untried_actions)
    untried_actions.remove(action)

    next_state = board.next_state(state, action)
    child_node = MCTSNode(parent=node, parent_action=action,
                          action_list=board.legal_actions(next_state))
    node.child_nodes[action] = child_node
    # print(f"Current node has {len(node.child_nodes.values())}")
    return child_node

# def heuristic(board, state, node, action):
#     #if applying an action leads to a win, prioritize that action

#     #get current num of wins
#     wins = board.win_values[1](state)

#     #copy the current state into temp state
#     temp_state = state

#     #apply a random action to the temp state and get # of wins
#     temp_action = choice(board.legal_actions(temp_state)) #select a random legal action
#     temp_state = board.next_state(temp_state, temp_action) #apply it to the temp state
#     temp_boxes = board.owned_boxes(temp_state) #get number of boxes

#     if(temp_boxes > boxes):
#         state = temp_state


def outcome(owned_boxes, game_points, current_player):
    if game_points is not None:
        red_score = game_points[1] * 9
        blue_score = game_points[2] * 9
    else:
        red_score = len([v for v in owned_boxes.values() if v == 1])
        blue_score = len([v for v in owned_boxes.values() if v == 2])

    return red_score - blue_score if current_player == 1 else blue_score - red_score


# def rollout_policy(board, state, current_player):
#     moves = board.legal_actions(state)

#     best_move = moves[0]
#     best_expectation = float('-inf')
#     best_state = state

#     for move in moves:
#         total_score = 0.0

#         # Sample a set number of games where the target move is immediately applied.
#         for r in range(10):
#             rollout_state = board.next_state(state, move)

#             # Only play to the specified depth.
#             for i in range(5):
#                 if board.is_ended(rollout_state):
#                     break
#                 rollout_move = choice(board.legal_actions(rollout_state))
#                 rollout_state = board.next_state(rollout_state, rollout_move)

#             total_score += outcome(board.owned_boxes(rollout_state),
#                                    board.points_values(rollout_state), current_player)

#         # Divide by the correct number of rollouts
#         expectation = float(total_score) / 10

#         # If the current move has a better average score, replace best_move, best_expectation, and best_state
#         if expectation > best_expectation:
#             best_expectation = expectation
#             best_move = move
#             best_state = rollout_state

#     return best_state
def rollout_policy(board, state, current_player):
    moves = board.legal_actions(state)

    best_expectation = float('-inf')
    best_state = state

    for move in moves:
        rollout_state = board.next_state(state, move)

        if board.is_ended(rollout_state):
            # If the rollout state is already an end state, no need to perform a rollout
            total_score = outcome(board.owned_boxes(
                rollout_state), board.points_values(rollout_state), current_player)
        else:
            total_score = 0.0

            # Perform a single rollout from the current move
            rollout_move = choice(board.legal_actions(rollout_state))
            rollout_state = board.next_state(rollout_state, rollout_move)

            total_score += outcome(board.owned_boxes(rollout_state),
                                   board.points_values(rollout_state), current_player)

        # If the current move has a better score, replace best_move, best_expectation, and best_state
        if total_score > best_expectation:
            best_expectation = total_score
            best_state = rollout_state

    return best_state


def rollout(board, state, identity):
    """ Given the state of the game, the rollout plays out the remainder using a heuristic.

    Args:
        board:  The game setup.
        state:  The state of the game.
        identity: The bot's identity, either 'red' or 'blue'.

    Returns: Win (+1), draw (0), or lose (-1).
    """
    rollout_state = state

    rollout_state = rollout_policy(board, rollout_state, identity)
    results = outcome(board.owned_boxes(rollout_state),
                      board.points_values(rollout_state), identity)
    # print(f"results: {results}")

    return results


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won (win = 1, loss = -1):    An indicator of whether the bot won or lost the game.

    """
    if node is None:
        return

    node.wins += won
    node.visits += 1

    prev = node.parent
    backpropagate(prev, won)


def think(board, state):
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None,
                         action_list=board.legal_actions(state))

    # need to initialize state with initlal root
    for step in range(num_nodes):
        sampled_game = state
        node = root_node

        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)
        sampled_game = board.next_state(sampled_game, leaf.parent_action)
        result_of_game = rollout(board, sampled_game, identity_of_bot)
        # print(f"Result of the game:  {result_of_game}")
        backpropagate(leaf, result_of_game)
        # print(f"Root node has {node.wins} win")

    best_child_node = find_best_win_rate(root_node)
    if best_child_node is not None:
        print(root_node.tree_to_string())
        return best_child_node.parent_action

    return None


def find_best_win_rate(node):

    best_child = None
    best_win_rate = float('-inf')

    for child in node.child_nodes.values():
        win_rate = child.wins / child.visits
        if (win_rate > best_win_rate):
            best_win_rate = win_rate
            best_child = child
    return best_child
