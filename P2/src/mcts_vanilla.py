from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_factor = 2.0


def ucb(node, parent_visits, identity):
    if node.visits == 0 or parent_visits == 0:
        return float('inf')
    if identity == 'opponent':
        exploitation = (node.visits - node.wins) / node.visits
    else:
        exploitation = node.wins / node.visits
    exploration = explore_factor * sqrt(log(parent_visits) / node.visits)
    return exploitation + exploration


def find_best_child(node, identity):
    best_ucb = float('-inf')
    best_child = None

    for child in node.child_nodes.values():
        child_ucb = ucb(child, node.visits, identity)
        if child_ucb > best_ucb:
            best_ucb = child_ucb
            best_child = child

    return best_child


def traverse_nodes(node, board, state, identity):
    if node.is_terminal(board, state):
        return node

    if not node.is_expanded():
        child_node = expand_leaf(node, board, state)
        return child_node

    best_child = find_best_child(node, identity)
    next_state = board.next_state(state, best_child.parent_action)

    if identity == 'opponent':
        identity = 'current_player'
    else:
        identity = 'opponent'

    return traverse_nodes(best_child, board, next_state, identity)


def expand_leaf(node, board, state):
    untried_actions = node.untried_actions
    action = choice(untried_actions)
    untried_actions.remove(action)

    next_state = board.next_state(state, action)
    child_node = MCTSNode(parent=node, parent_action=action,
                          action_list=board.legal_actions(next_state))
    node.child_nodes[action] = child_node
    print(f"Current node has {len(node.child_nodes.values())} children")
    print("Is returing childe node")
    return child_node


def rollout_policy(board, state):
    while not board.is_ended(state):
        legal_actions = board.legal_actions(state)
        random_action = choice(legal_actions)
        state = board.next_state(state, random_action)
    return state


def rollout(board, state):
    print("In rollout state")
    rollout_state = state

    rollout_state = rollout_policy(board, rollout_state)

    winner_values = board.win_values(rollout_state)

    if winner_values:
        player_1 = winner_values.get(board.current_player(rollout_state))
        player_2 = winner_values.get(board.previous_player(rollout_state))

        return 1 if player_1 > player_2 else -1 if player_1 < player_2 else 0


def backpropagate(node, won):
    print("Is in backpropigating")
    if node.parent is None:
        return

    node.wins += won
    node.visits += 1

    prev = node.parent
    backpropagate(prev, won)


def think(board, state):
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None,
                         action_list=board.legal_actions(state))
    # initialize tree with root node
    for action in root_node.untried_actions:
        next_state = board.next_state(state, action)
        child_node = MCTSNode(parent=root_node, parent_action=action,
                              action_list=board.legal_actions(next_state))
        root_node.child_nodes[action] = child_node

    # need to initialize state with initlal root
    for step in range(num_nodes):
        sampled_game = state
        node = root_node
        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)

        # assert (leaf in node.child_nodes.values())
        sampled_game = board.next_state(sampled_game, leaf.parent_action)
        result_of_game = rollout(board, sampled_game)

        backpropagate(leaf, result_of_game)

    best_child_node = find_best_child(root_node, identity_of_bot)
    if best_child_node is not None:
        return best_child_node.parent_action

    return None
