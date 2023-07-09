from mcts_node import MCTSNode
from random import choice, random
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.0

# def traverse_nodes(node, board, state, identity):
#     if node.is_terminal():
#         return node

#     # Check if the current node is fully expanded
#     if not node.is_fully_expanded():
#         return expand_node(node, board, state)

#     # Use UCB (Upper Confidence Bound) to select the best child node
#     best_child = select_find_best_child(node)

#     # Update the game state based on the chosen move
#     update_state(state, best_child.move)

#     # Recursively traverse down the tree
#     return traverse_nodes(best_child, board, state, identity)


def ucb(node, parent_visits):
    exploitaion = node.wins/node.vists
    exploration = explore_faction * sqrt(log(parent_visits)/node.vists)
    return exploitaion + exploration


def find_best_child(node):
    """Selects the best child node based on the UCB score.

    Args:
        node: The parent node.

    Returns: The best child node.
    """
    best_ucb = float('-inf')
    best_child = None

    for child in node.child_nodes.values():
        child_ucb = ucb(child, node.visits)
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
    # Check if node is terminal or fully expanded
    while not bool(node.untried_actions) and not bool(node.child_nodes):
        best_child = find_best_child(node)  # Find the best child node
        # Update the game state
        state = board.next_state(state, best_child.parent_action)
        node = best_child

    # Check if node is terminal
    if not bool(node.untried_actions):
        return node

    # Node is not fully expanded, so expand the leaf node
    child_node = expand_leaf(node, board, state)
    return child_node


def expand_leaf(node, board, state):
    """Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node: The node for which a child will be added.
        board: The game setup.
        state: The state of the game.

    Returns: The added child node.
    """
    untried_actions = node.untried_actions
    action = choice(untried_actions)  # Choose a random unexplored action
    # Remove the chosen action from untried actions
    untried_actions.remove(action)

    next_state = board.next_state(state, action)  # Update the game state

    child_node = MCTSNode(parent=node, parent_action=action,
                          action_list=board.legal_actions(next_state))  # Create a new child node
    # Add the child node to the parent node
    node.child_nodes[action] = child_node

    return child_node


def rollout_policy(board, state):
    while not board.is_ended(state):
        legal_actions = board.legal_actions(state)
        random_action = choice(legal_actions)
        state = board.next_state(state, random_action)
    return state


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    returns win(+1), draw(0), or lose(-1)

    """
    rollout_state = state

    previous_player = board.previous_player(rollout_state)
    current_player = board.current_player(rollout_state)

    rollout_state = rollout_policy(board, rollout_state)

    winner_values = board.win_values(rollout_state)

    if winner_values:
        player_1 = winner_values.get(current_player)
        player_2 = winner_values.get(previous_player)

        return 1 if player_1 > player_2 else -1 if player_1 < player_2 else 0


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
    """Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board: The game setup.
        state: The state of the game.

    Returns: The action to be taken.
    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None,
                         action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        leaf = traverse_nodes(node, board, sampled_game,
                              identity_of_bot)  # Find Leaf Node

        # next_sampled_game = board.next_state(
        #     sampled_game, leaf.parent_action)

        # Simulate rest of the game
        result_of_game = rollout(board, sampled_game)

        backpropagate(leaf, result_of_game)  # Update wins and visits

    # Select the best action based on the current statistics
    best_child_node = find_best_action(root_node)
    if best_child_node is not None:
        return best_child_node.parent_action

    return None


def find_best_action(node):
    most_visits = 0
    best_child = None
    for child in node.child_nodes.values():
        if (child.visits > most_visits):
            most_vists = child.visits
            best_child = child
    return best_child
