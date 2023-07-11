from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_factor = 2.0


def ucb(node, parent_visits, board, state, identity):
    opposing_player = board.previous_player(state)
    current_player = board.current_player(state)

    if node.visits == 0:
        return float('inf') if identity == current_player else float('-inf')

    if identity == opposing_player:
        exploitation = (1 - node.wins) / node.visits
    else:
        exploitation = node.wins / node.visits
    exploration = explore_factor * sqrt(log(parent_visits) / node.visits)
    return exploitation + exploration


def find_best_child(node, board, state, identity):

    best_child = None
    opposing_player = board.previous_player(state)
    current_player = board.current_player(state)

    if (identity == current_player):
        best_ucb = float('-inf')

        for child in node.child_nodes.values():
            child_ucb = ucb(child, node.visits, board, state, identity)
            if child_ucb > best_ucb:
                best_ucb = child_ucb
                best_child = child
    else:
        best_ucb = float('inf')
        for child in node.child_nodes.values():
            child_ucb = ucb(child, node.visits, identity)
            if child_ucb < best_ucb:
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

    if node.is_terminal(board, state):
        # print("Is terminal ")
        return node

    if node.is_expanded():
        # print("Node is expanded ")
        child_node = expand_leaf(node, board, state)
        return child_node
    # print("looking for best child")

    best_child = find_best_child(node, board, state, identity)
    next_state = board.next_state(state, best_child.parent_action)
    identity = board.current_player(next_state)

    return traverse_nodes(best_child, board, next_state, identity)


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


def rollout_policy(board, state):
    while not board.is_ended(state):
        legal_actions = board.legal_actions(state)
        random_action = choice(legal_actions)
        state = board.next_state(state, random_action)
    return state


def rollout(board, state, identity):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    returns win(+1), draw(0), or lose(-1)

    """

    rollout_state = state

    rollout_state = rollout_policy(board, rollout_state)

    winner_values = board.win_values(rollout_state)

    opposing_player = board.previous_player(rollout_state)
    current_player = board.current_player(rollout_state)

    if winner_values:
        player_1 = winner_values.get(
            identity if identity == current_player else opposing_player)
        player_2 = winner_values.get(
            identity if identity == current_player else opposing_player)
        # print( f"Winner Values for current node is Player 1: {player_1} Player 2: {player_2}")
        return 1 if player_1 > player_2 else -1 if player_1 < player_2 else 0


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

    best_child_node = find_best_child(root_node, board, state, identity_of_bot)
    if best_child_node is not None:
        print(root_node.tree_to_string())
        return best_child_node.parent_action

    return None
