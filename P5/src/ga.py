import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    # "f",  # a flag, do not generate
    # "v",  # a flagpole, do not generate
    # "m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        left = 1
        right = width - 1

        if random.random() < 0.1 and len(genome) == 16:
            mutation_type = random.choice(["cols", "rows", "positions"])
            if mutation_type == "cols":
                num_cols = random.randint(1, width // 4)
                cols_to_mutate = random.sample(range(left, right), num_cols)
                for y in range(height):
                    for x in cols_to_mutate:
                        block = genome[y][x]
                        if block == '-' and y in range(3, 15):
                            if random.random() < .8:
                                genome[y][x] = random.choice(options[:5])[0]

                        elif block in ["X", "?", "M", "B", "o"]:
                            shift_by = random.random()
                            y2 = clip(0, y + random.choice([-1, 1]), height-1)
                            x2 = clip(left, x + random.choice([-1, 1]), right)
                            if (shift_by < 0.25):
                                genome[y][x] = random.choice(
                                    ["X", "?", "M", "B", "o"])[0]
                            elif shift_by < 0.5:
                                genome[y][x], genome[y][x2] = genome[y][x2], genome[y][x]
                            elif shift_by < 0.75:
                                genome[y][x], genome[y2][x] = genome[y2][x], genome[y][x]
                            else:
                                genome[y][x], genome[y2][x2] = genome[y2][x2], genome[y][x]
                        elif genome[y][x] == "T":
                            y1 = random.randint(4, 13)
                            height_diff = abs(y - y1)
                            for h in range(min(y, y1), max(y, y1)):
                                genome[h][x] = "|"
                        elif genome[y][x] == "E":
                            # Enemy has the option of being replaced or not
                            if random.random() < 0.5:
                                genome[y][x] = random.choice(["-", "E"])

            elif mutation_type == "rows":
                num_rows = random.randint(1, height // 4)
                rows_to_mutate = random.sample(range(4, 13), num_rows)
                for y in rows_to_mutate:
                    for x in range(left, right):
                        block = genome[y][x]
                        if block == '-' and y in range(3, 15):
                            if random.random() < .8:
                                genome[y][x] = random.choice(options[:5])[0]

                        elif block in ["X", "?", "M", "B", "o"]:
                            shift_by = random.random()
                            y2 = clip(0, y + random.choice([-1, 1]), height-1)
                            x2 = clip(left, x + random.choice([-1, 1]), right)
                            if (shift_by < 0.25):
                                genome[y][x] = random.choice(
                                    ["X", "?", "M", "B", "o"])[0]
                            elif shift_by < 0.5:
                                genome[y][x], genome[y][x2] = genome[y][x2], genome[y][x]
                            elif shift_by < 0.75:
                                genome[y][x], genome[y2][x] = genome[y2][x], genome[y][x]
                            else:
                                genome[y][x], genome[y2][x2] = genome[y2][x2], genome[y][x]
                        elif genome[y][x] == '|':
                            pass
                        elif genome[y][x] == "T":
                            y1 = random.randint(4, 13)
                            height_diff = abs(y - y1)
                            for h in range(min(y, y1), max(y, y1)):
                                genome[h][x] = "|"
                        elif genome[y][x] == "E":
                            if random.random() < 0.5:
                                genome[y][x] = random.choice(["-", "E"])

            elif mutation_type == "positions":
                num_positions = random.randint(1, width * height // 4)
                positions_to_mutate = random.sample(
                    [(y, x) for y in range(height) for x in range(left, right)], num_positions)
                for y, x in positions_to_mutate:
                    block = genome[y][x]
                    if block == '-' and y in range(3, 15):
                        if random.random() < .8:
                            genome[y][x] = random.choice(options[:5])[0]

                    elif block in ["X", "?", "M", "B", "o"]:
                        shift_by = random.random()
                        y2 = clip(0, y + random.choice([-1, 1]), height-1)
                        x2 = clip(left, x + random.choice([-1, 1]), right)
                        if (shift_by < 0.25):
                            genome[y][x] = random.choice(
                                ["X", "?", "M", "B", "o"])[0]
                        elif shift_by < 0.5:
                            genome[y][x], genome[y][x2] = genome[y][x2], genome[y][x]
                        elif shift_by < 0.75:
                            genome[y][x], genome[y2][x] = genome[y2][x], genome[y][x]
                        else:
                            genome[y][x], genome[y2][x2] = genome[y2][x2], genome[y][x]
                    elif genome[y][x] == '|':
                        pass
                    elif genome[y][x] == "T":
                        y1 = random.randint(4, 13)
                        height_diff = abs(y - y1)
                        for h in range(min(y, y1), max(y, y1)):
                            genome[h][x] = "|"
                    elif genome[y][x] == "E":
                        if random.random() < 0.5:
                            genome[y][x] = random.choice(["-", "E"])

        return genome

    # Create zero or more children from self and other

    def generate_children(self, other):
        new_genome_self = copy.deepcopy(self.genome)
        new_genome_other = copy.deepcopy(other.genome)

        # Leaving first and last columns alone...
        # do crossover with other
        left = 1
        right = width - 1
        P = [[random.random() for _ in range(left, right+1)]
             for _ in range(height)]

        for y in range(height):
            for x in range(left, right):
                temp = new_genome_self
                if new_genome_self[y][x] == "T" or new_genome_other[y][x] == "T":
                    for h in range(y, 16):
                        new_genome_self[h][x] = new_genome_other[h][x]
                        new_genome_other[h][x] = temp[h][x]
                elif P[y][x] < 0.5:
                    new_genome_self[y][x] = new_genome_other[y][x]
                    new_genome_other[y][x] = temp[y][x]

        # Perform mutation; note we're returning a one-element tuple here
        return (Individual_Grid(self.mutate(new_genome_self)), Individual_Grid(self.mutate(new_genome_other)))

    # Turn the genome into a level string (easy for this genome)

    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [["-" for col in range(width)] for row in range(height)]
        # set first four row to zero
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"

        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"

        num_holes = random.randint(2, 5)
        num_pipe = random.randint(2, width/4)
        num_platforms = random.randint(2, 10)
        num_stairs = random.randint(2, 4)
        num_enemies = random.randint(10, 30)
        num_coins = random.randint(20, 60)

        pipe_pos = []
        stair_pos = []
        platform_pos = []
        hole_pos = []

        # create holes in level
        for hole in range(num_holes):
            x = random.randint(1, width-5)
            w2 = random.randint(3, 10)
            for w in range(w2):
                x2 = clip(3, x + w, width-2)
                if (g[15][x2] == "X" and (15, x2) not in hole_pos):
                    g[15][x2] = "-"
                    hole_pos.append((15, x2))

        avilable_pos = hole_pos

        # create pipes in level
        for pipe in range(num_pipe):
            x = random.randint(3, width-2)
            peak_height = height - \
                (math.ceil(height * math.sin(((math.pi * x) / 200))))
            peak_height = max(1, peak_height)

            for h in range(peak_height, height):
                g[h][x] = "|"
                pipe_pos.append((h, x))

            g[peak_height][x] = "T"
            pipe_pos.append((peak_height, x))

        avilable_pos += pipe_pos

        # Create stairs in level
        for _ in range(num_stairs):
            direction = random.choice([-1, 1])
            h = random.randint(3, 6)
            x = random.randint(1, width - 2)

            for step in range(1, h + 1):
                for y in range(step if direction == 1 else h - step):

                    y2 = clip(0, height - y - 1, height - 1)
                    x2 = clip(1, x + step, width - 2)

                    if g[y2][x2] == "-" or (y2, x2) not in avilable_pos:
                        g[y2][x2] = "X"
                        stair_pos.append((y2, x2))
                        avilable_pos.append((y2, x2))

        # Create platforms in level
        for platform in range(num_platforms):
            h = random.randint(1, height - 4)
            x = random.randint(2, width-2)
            depth = random.randint(1, 6)

            for d in range(depth):
                y2 = clip(0, height - h - 1, height-1)
                x2 = clip(1, x + d, width-2)
                if (g[y2][x2] == "-" or (y2, x2) not in avilable_pos):
                    g[y2][x2] = random.choices(options[1:5])[0]
                    platform_pos.append((y2, x2))
                    avilable_pos.append((y2, x2))

        # Create  enemies
        for enemy in range(num_enemies):
            choice = random.random()
            if choice < .5:
                # choose among floor
                y, x = 15, random.randint(6, width-4)
                if g[y-2][x] == '-':
                    g[y-2][x] = "E"
            else:
                # choose among all postion
                y, x = random.choices(platform_pos)[0]
                if g[y-2][x] == '-':
                    g[y-2][x] = "E"

        # Add coins in level
        for coin in range(num_coins):
            y = random.randint(1, height-2)
            x = random.randint(1, width-2)
            if g[y][x] == "-":
                g[y][x] = "o"

        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.1 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 4)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        child_genome_a = []
        child_genome_b = []

        # Ensure both genomes are of equal length
        max_len = max(len(self.genome), len(other.genome))
        self.genome += [""] * (max_len - len(self.genome))
        other.genome += [""] * (max_len - len(other.genome))

        # Perform uniform crossover
        for gene_self, gene_other in zip(self.genome, other.genome):
            # Randomly choose bits from both parents
            if random.random() < 0.5:
                child_genome_a.append(gene_self)
                child_genome_b.append(gene_other)
            else:
                child_genome_a.append(gene_other)
                child_genome_b.append(gene_self)

        # Remove any trailing empty elements
        child_genome_a = [gene for gene in child_genome_a if gene]
        child_genome_b = [gene for gene in child_genome_b if gene]

        # Perform mutation
        return Individual_DE(self.mutate(child_genome_a)), Individual_DE(self.mutate(child_genome_b))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)
                                 ][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)
                             ][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8),
             random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block",
             random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock",
             random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs",
             random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_Grid


def generate_successors(population):
    results = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.
    # selection_method = random.choices(["roulette",  "elitist"])[0]
    # if selection_method == "roulette":
    #     # Roulette Selection
    #     total_fitness = sum(gen._fitness for gen in population)
    #     probabilities = [gen._fitness / total_fitness for gen in population]

    #     for _ in range(len(population)):
    #         selected_gen = random.choices(population, probabilities)[0]
    #         results.append(selected_gen)

    # elif selection_method == "elitist":
    # Elitist Selection
    elite_gen = [gen for gen in population if gen.genome != []]
    num_of_elites = math.ceil((random.randint(1, 25) / 100) * len(elite_gen))
    elite_gen = sorted(elite_gen, key=lambda p: p._fitness, reverse=True)[:num_of_elites]
    results += elite_gen

    for child_self in results:
        for child_other in results:
            if child_self == child_other:
                continue

            if child_self == [] or child_other == []:
                continue

            child_1, child_2 = Individual.generate_children(child_self, child_other)

            if (len(results) < len(population)):
                child_1 = Individual.calculate_fitness(child_1)
                child_2 = Individual.calculate_fitness(child_2)
                results.append(child_1)
                results.append(child_2)

    return results

def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " +
              str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        init_done = time.time()
        print("Created and calculated initial population statistics in:",
              init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:",
                          (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = False if generation < 1000 else True
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
