
from mcts_node import MCTSNode
from random import choice, random
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.0


ROLLOUTS = 10
MAX_DEPTH = 5


def ucb(node, parent_visits):
    exploitaion = node.wins/node.vists
    exploration = explore_faction * sqrt(log(parent_visits)/node.vists)
    return exploitaion + exploration


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the prev stage of the search can proceed.

    """
    if node is None:
        return None

    best_ucb = 0
    best_child = None

    for child in node.child_nodes.values():
        child_ucb = ucb(child, node.visits)
        if (child_ucb > best_ucb):
            best_ucb = child_ucb
            best_child = child

    if best_child is not None:
        return traverse_nodes(best_child, board, state, identity)

    return None


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    actions_list = board.legal_actions(state)
    for action in actions_list:
        if action in node.untried_actions:  # check actions we haven't vistied
            new_node_action_list = node.untried_actions.remove(action)
            new_node = MCTSNode(parent=node, parent_action=action,
                                action_list=new_node_action_list)
            node.child_nodes[action] = new_node

            break

    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    moves = board.legal_actions(state)

    best_move = moves[0]
    best_expectation = float('-inf')

    me = board.current_player(state)

    # Define a helper function to calculate the difference between the bot's score and the opponent's.
    def outcome(owned_boxes, game_points):
        if game_points is not None:
            # Try to normalize it up?  Not so sure about this code anyhow.
            red_score = game_points[1]*9
            blue_score = game_points[2]*9
        else:
            red_score = len([v for v in owned_boxes.values() if v == 1])
            blue_score = len([v for v in owned_boxes.values() if v == 2])
        return red_score - blue_score if me == 1 else blue_score - red_score

    for move in moves:
        total_score = 0.0

        # Sample a set number of games where the target move is immediately applied.
        for r in range(ROLLOUTS):
            rollout_state = board.next_state(state, move)

            # Only play to the specified depth.
            for i in range(MAX_DEPTH):
                if board.is_ended(rollout_state):
                    break
                rollout_move = random.choice(
                    board.legal_actions(rollout_state))
                rollout_state = board.next_state(rollout_state, rollout_move)

            total_score += outcome(board.owned_boxes(rollout_state),
                                   board.points_values(rollout_state))

        expectation = float(total_score) / ROLLOUTS

        # If the current move has a better average score, replace best_move and best_expectation
        if expectation > best_expectation:
            best_expectation = expectation
            best_move = move

    return best_move


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won (win = 1, loss = -1):    An indicator of whether the bot won or lost the game.

    """
    if (node.parent is None):
        return

    node.wins += won
    node.visits += 1

    prev = node.parent
    backpropagate(prev, won)
    return


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None,
                         action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        leaf = traverse_nodes(node, board, state, identity_of_bot)
        new_node = expand_leaf(leaf, board, state)
        best_move = rollout(board, state)
        backpropagate(best_move, won)

        return best_child(node)

        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best_ucb
    # estimated win rate.
    return None


def best_child(node):
    most_visits = 0
    best_child = None
    for child in node.child_nodes.values():
        if (child.visits > most_visits):
            most_vists = child.visits
            best_child = child
    return best_child
