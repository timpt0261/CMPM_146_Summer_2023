#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    # reimplement everything

    early_game_strategy = Sequence(name='Early Game Strategy')
    last_check = Check(last)
    grow_from_one_action = Action(grow_from_one)
    early_game_strategy.child_nodes = [last_check, grow_from_one_action]

    production_action = Action(production)

    aggressive_strategy = Selector(name='Aggressive Strategy')
    attack_sequence = Sequence(name='Attack Sequence')
    largest_fleet_check = Check(have_largest_fleet)
    attack_action = Action(attack)
    attack_sequence.child_nodes = [largest_fleet_check, attack_action]
    spread_action = Action(spread)
    aggressive_strategy.child_nodes = [attack_sequence, spread_action]

    defend_action = Action(defend)

    root.child_nodes = [early_game_strategy, aggressive_strategy, defend_action]


    logging.info('\n' + root.tree_to_string())
    return root
#yeah dont touch under this. above is state machine. 
# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")