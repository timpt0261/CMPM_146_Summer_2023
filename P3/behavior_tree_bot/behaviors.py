import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from math import inf


def attack_weakest_enemy_planet(state):
    """
    Attacks the weakest enemy planet.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the attack was successful or not.
    """
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination.
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 1)


def spread_to_weakest_neutral_planet(state):
    """
    Spreads ships to the weakest neutral planet.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the spread was successful or not.
    """
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination.
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest neutral planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def counter_fleet(state):
    """
    Sends a larger fleet to a planet that the enemy is sending a fleet to overtake.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the counter fleet was sent successfully or not.
    """
    # Find enemy fleet not already being countered.
    target = None
    for enemy_fleet in state.enemy_fleets():
        if enemy_fleet.num_ships > state.planets[enemy_fleet.destination_planet].num_ships:
            covered = False
            for my_fleet in state.my_fleets():
                if enemy_fleet.destination_planet == my_fleet.destination_planet:
                    # Fleet already being countered.
                    covered = True
                    break
            if not covered:
                # Eligible fleet found.
                size = enemy_fleet.num_ships
                target = enemy_fleet.destination_planet
                break
    if not target:
        return False

    # Find planet capable of countering the enemy fleet.
    best_planet = state.my_planets()[0]
    best_dist = state.distance(best_planet.ID, target)
    planet_found = False
    for planet in state.my_planets():
        if planet.num_ships > size + 1:
            possible_dist = state.distance(planet.ID, target)
            if possible_dist < best_dist:
                best_planet = planet
                best_dist = possible_dist
                planet_found = True

    # Send counter fleet.
    if not planet_found:
        return False
    else:
        return issue_order(state, best_planet.ID, target, size + 1)


def take_high_growth(state):
    """
    Attacks the planet with the highest growth rate.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the attack was successful or not.
    """
    target = max(state.planets, key=lambda p: p.growth_rate, default=None)
    best_dist = inf
    best_source = None
    best_size = None
    for planet in state.my_planets():
        this_dist = state.distance(planet.ID, target.ID)
        required_ships = target.num_ships + (this_dist * target.growth_rate) + 1
        if planet.num_ships > required_ships and this_dist < best_dist:
            best_source = planet
            best_dist = this_dist
            best_size = required_ships
    if not best_source:
        return False
    else:
        return issue_order(state, best_source.ID, target.ID, best_size)


def rush_first_target(state):
    """
    Rushes the first target, i.e., the enemy's first planet.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the rush was successful or not.
    """
    target = state.enemy_planets()[0]
    best_dist = inf
    best_source = None
    for planet in state.my_planets():
        this_dist = state.distance(planet.ID, target.ID)
        required_ships = target.num_ships + (this_dist * target.growth_rate) + 1
        if planet.num_ships > required_ships and this_dist < best_dist:
            best_source = planet
            best_dist = this_dist
    if not best_source:
        return False
    else:
        return issue_order(state, best_source.ID, target.ID, best_source.num_ships - 1)


def attack(state):
    """
    Attacks enemy planets based on the strength of our planets.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the attack was successful or not.
    """
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    enemy_planets = [planet for planet in state.enemy_planets()
                     if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)
    target_planets = iter(enemy_planets)

    success = False

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                             state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                success = True
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return success


def spread(state):
    """
    Spreads ships to neutral planets based on the strength of our planets.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the spread was successful or not.
    """
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [planet for planet in state.neutral_planets()
                       if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)

    success = False

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                success = True
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return success


def defend(state):
    """
    Defends weak planets and reinforces strong planets.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the defense was successful or not.
    """
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return False

    def strength(p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if not weak_planets or not strong_planets:
        return False

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    success = False

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0:
                success = True
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            elif have > 0:
                success = True
                issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return success


def production(state):
    """
    Sends ships from strong planets to target planets based on their strength.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the production was successful or not.
    """
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))

    target_planets = [planet for planet in state.not_my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = iter(sorted(target_planets, key=lambda p: p.num_ships, reverse=True))

    success = False

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                success = True
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                target_planet = next(target_planets)

    except StopIteration:
        return success


def grow_from_one(state):
    """
    Sends ships from the first planet to the nearest neutral planet.

    Args:
        state: The current game state.

    Returns:
        A boolean indicating if the growth from one planet was successful or not.
    """
    planet = state.my_planets()[0]
    least_distance = inf
    nearest_target = None

    for target in state.neutral_planets():
        target_distance = state.distance(planet.ID, target.ID)
        if target_distance < least_distance:
            required_ships = target.num_ships + 1
            if planet.num_ships > required_ships:
                least_distance = target_distance
                nearest_target = target
    if not nearest_target:
        return False
    else:
        return issue_order(state, planet.ID, nearest_target.ID, required_ships)
