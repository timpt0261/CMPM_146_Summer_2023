

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
        + sum(fleet.num_ships for fleet in state.my_fleets()) \
        > sum(planet.num_ships for planet in state.enemy_planets()) \
        + sum(fleet.num_ships for fleet in state.enemy_fleets())


def is_opponent_spreading(state):
    # To check if the opposing bot is using the spread tactic

    # 1) Find if more small neutral planets have enemy fleets on their way
    neutral_planets = sorted(state.neutral_planets(), key=lambda p: p.num_ships)
    weak_neutral_planets = [planet for planet in neutral_planets if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]

    # 2) Calculate the number of fleets heading towards weak neutral planets
    fleets_heading_weak_neutral = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet in [planet.ID for planet in weak_neutral_planets])

    # 3) Check if the majority of enemy fleets are heading towards weak neutral planets
    majority_threshold = 0.5
    return fleets_heading_weak_neutral > (len(state.enemy_fleets()) * majority_threshold)



def is_opponent_attacking_weakest(state):
    # To check is opponet is sending fleet to waekest opposing planets

    # 1) Find Weakest planets 
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    weakest_owned_planets = [planet for planet in my_planets if any(fleet.destination == planet.ID for fleet in state.enemy_fleets())]

    # 2) Calculate the number of fleets heading to weak owned planets 
    fleets_heading_weak_owned = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet in [planet.ID for planet in weak_owned_planets])
    
    # 3) Check if the majority of fleets are heading toward weak owned planets
    majority_threshold = 0.5
    return fleets_heading_weak_owned > (len(state.enemy_fleets()) * majority_threshold)

def is_opponent_attacking_strongest(state):
    # To check is opponet is sending fleet to waekest opposing planets

    # 1) Find strongest planets 
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships,reverse=True)
    strongest_owned_planets = [planet for planet in my_planets if any(fleet.destination == planet.ID for fleet in state.enemy_fleets())]

    # 2) Calculate the number of fleets heading to strong owned planets 
    fleets_heading_strong_owned = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet in [planet.ID for planet in strong_owned_planets])
    
    # 3) Check if the majority of fleets are heading toward strong owned planets
    majority_threshold = 0.5
    return fleets_heading_strong_owned > (len(state.enemy_fleets()) * majority_threshold)



def is_opponent_defending_weakest(state):
    # To check is opponet is sending fleet to weakest owned planets

    # 1) Find Weakest planets 
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships)
    weakest_owned_planets = [planet for planet in enemy_planets if any(fleet.destination == planet.ID for fleet in state.enemy_fleets())]

    # 2) Calculate the number of fleets heading to weak owned planets 
    fleets_heading_weak_owned = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet in [planet.ID for planet in weak_owned_planets])
    
    # 3) Check if the majority of fleets are heading toward weak owned planets
    majority_threshold = 0.5
    return fleets_heading_weak_owned > (len(state.enemy_fleets()) * majority_threshold)


def is_opponent_defending_strongest(state):
    # To check is opponet is sending fleet to strongest owned planets

    # 1) Find strongest planets 
    enemy_planets = sorted(state.enemy_planets(), key=lambda p: p.num_ships, reverse=True)
    strongest_owned_planets = [planet for planet in enemy_planets if any(fleet.destination == planet.ID for fleet in state.enemy_fleets())]

    # 2) Calculate the number of fleets heading to strong owned planets 
    fleets_heading_strong_owned = sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet in [planet.ID for planet in strong_owned_planets])
    
    # 3) Check if the majority of fleets are heading toward strong owned planets
    majority_threshold = 0.5
    return fleets_heading_strong_owned > (len(state.enemy_fleets()) * majority_threshold)