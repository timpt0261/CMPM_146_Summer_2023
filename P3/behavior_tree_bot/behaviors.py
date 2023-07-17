# behaviors.py
import sys
import logging
sys.path.insert(0, '../')
from planet_wars import issue_order
import random
import math

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.growth_rate + 1)


# Want a distance formula, tracker of how many of our forces going where, growth rate tracker

# Sort by lowest distance to target planet
def distance(source, destination):
    dx = source.x - destination.x
    dy = source.y - destination.y
    return math.ceil(math.sqrt(dx * dx + dy * dy))


# Not accounting for distance yet
def spread_to_best_neutral_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships * (1 + 1/p.growth_rate))[:5]
    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = sorted(neutral_planets, key=lambda p: p.num_ships * (1 + 1/p.growth_rate))

    for target_planet in target_planets:
        top_5_ships_available = sum(planet.num_ships * (1/3) for planet in my_planets)
        required_ships = target_planet.num_ships + 5
        forces_sent = 0

        for my_planet in my_planets:
            if forces_sent == required_ships or my_planet.num_ships * (2/3) < 25:
                break

            regiment = min(my_planet.num_ships * (1/3), top_5_ships_available - forces_sent)
            forces_sent += regiment
            issue_order(state, my_planet.ID, target_planet.ID, regiment)

    return False


def pester_weakest_enemy_planet(state):
    # Randomly choose a planet
    planet = random.choice(state.my_planets()) if state.my_planets() else None

    # Find weakest enemy planet
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    # Send a random number of ships that does not exceed growth rate
    if planet and weakest_planet:
        return issue_order(state, planet.ID, weakest_planet.ID, max(1, planet.growth_rate - 1))

    # No legal source or destination
    return False


def spread_to_closest_weakest_planet(state):
    if not state.my_planets():
        return False

    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

    closest_weak_planet = min(
        state.not_my_planets(),
        key=lambda planet: distance(strongest_planet, planet) + planet.num_ships
    )

    if strongest_planet.num_ships > closest_weak_planet.num_ships + 20:
        issue_order(state, strongest_planet.ID, closest_weak_planet.ID, closest_weak_planet.num_ships + 20)

    return False


def disrupt_spreading(state):
    # Find planets most likely to be spread
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
    weak_neutral_planets = [planet for planet in neutral_planets if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]

    target_planet = iter(weak_neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planet)
        while True:
            required_ships = target_planet.num_ships + state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planet)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return False


def defend_weakest_planets(state):
    # 1) Find weakest owned planets that are being targeted
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    weakest_owned_planets = [planet for planet in my_planets if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]

    defend_planet = weakest_owned_planets[0]
    
    # 2) Find fleets heading to the current planet
    enemy_heading_to_weakest = [fleet for fleet in state.enemy_fleets() if fleet.destination_planet == planet.ID]
    enemy_heading_to_weakest.sort(key=lambda p : p.turns_remaining())
    
    num_of_enemies = enemy_heading_to_weakest[0].num_ships()
    distance_to_planet = enemy_heading_to_weakest[0].total_trip_length()
    enemy_future = defend_planet.growth_rate / ((num_of_enemies + defend_planet.growth_rate * distance_to_planet + 1) * distance_to_planet)

    # Calculate the closest or strongest to counter the expexted future
    closest_planets = sorted(state.my_planets(), key=lambda p: state.distance(defend_planet, p))
    
    for close in closest_planets:
            
        # if the closet planet is able to give the required ships send correct amount, other wise 
        required_ship = defend_planet.num_ships + state.distance(close.ID, defend_planet) * defend_planet.growth_rate + 1
        close_future = defend_planet.growth_rate / (required_ship * state.distance(defend_planet.ID))

        if close_future > enemy_future:
            return issue_order(state, close.ID,defend_planet, required_ship)
        else: 
            continue
        
    return False

