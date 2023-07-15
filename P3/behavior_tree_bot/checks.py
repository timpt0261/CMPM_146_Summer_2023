

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
        + sum(fleet.num_ships for fleet in state.my_fleets()) \
        > sum(planet.num_ships for planet in state.enemy_planets()) \
        + sum(fleet.num_ships for fleet in state.enemy_fleets())


def is_opponenent_spreading(state):
    # To check if the  opposing bot is using the spread tatic
    neutral_planets = [planet for planet in state.neutral_planets()
                       if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    enenmy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]

    enemy_planets.sort(key=lambda p: p.num_ships)

    return len(neutral_planets) > 1


def is_opponent_attacking(state):
    # Check is opponet is sending fleet to waekest opposing planets
    my_planets = [planet for planet in state.my_planets()
                  if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]

    return True


def is_opponent_defending(state):
    # Check if oponet is sending fleets to it's weakest planets
    return True
