import math
import random
import time


# Solve Every Sudoku Puzzle
# See http://norvig.com/sudoku.html

# References used:
# http://www.scanraid.com/BasicStrategies.htm
# http://www.sudokudragon.com/sudokustrategy.htm
# http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
# http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/

# Throughout this program we have:
#   r is a row,    e.g. 'A'
#   c is a column, e.g. '3'
#   s is a square, e.g. 'A3'
#   d is a digit,  e.g. '9'
#   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
#   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
#   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}


####################
# Problem Data
####################
def cross(list_a, list_b):
    """Cross product of elements in list_a and elements in list_b."""
    return [a + b for a in list_a for b in list_b]


digits = "123456789"
rows = "ABCDEFGHI"
cols = digits
squares = cross(rows, cols)
unit_list = (
        [cross(rows, col) for col in cols]
        + [cross(row, cols) for row in rows]
        + [cross(rs, cs) for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")]
)
units = dict((square, [unit for unit in unit_list if square in unit]) for square in squares)
peers = dict((square, set(sum(units[square], [])) - {square}) for square in squares)

########################################################################################################################
########################################################################################################################
########################################################################################################################

####################
# Custom utils
####################
# Let's take advantage of the cross function to generate the rows, cols.
# This will allow us to easily iterate through the rows and cols.
square_columns = [cross(rows, col) for col in cols]
square_rows = [cross(row, cols) for row in rows]


def get_box_neighbours(square):
    neighbours = set(units[square][2])
    neighbours.discard(square)
    return neighbours


########################################################################################################################
########################################################################################################################
########################################################################################################################

####################
# Constraint Propagation DFS
####################
def assign_depth_first_search(values, square, digit, heuristic=None):
    """Eliminate all the other values (except digit) from values[square] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[square].replace(digit, "")
    if all(eliminate_depth_first_search(values, square, digit_2, heuristic) for digit_2 in other_values):
        return values
    else:
        return False


def eliminate_depth_first_search(values, square, digit, heuristic=None):
    """Eliminate digit from values[square]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if digit not in values[square]:
        return values  # Already eliminated
    values[square] = values[square].replace(digit, "")

    # (1) If a square is reduced to one value digit_2, then eliminate digit_2 from the peers.
    if len(values[square]) == 0:
        return False  # Contradiction: removed last value
    elif len(values[square]) == 1:
        digit_2 = values[square]
        if not all(eliminate_depth_first_search(values, square_2, digit_2) for square_2 in peers[square]):
            return False
    # (2) If a unit is reduced to only one place for a value digit, then put it there.
    for unit in units[square]:
        digit_places = [square for square in unit if digit in values[square]]
        if len(digit_places) == 0:
            return False  # Contradiction: no place for this value
        elif len(digit_places) == 1:
            # digit can only be in one place in unit; assign it there
            if not assign_depth_first_search(values, digit_places[0], digit):
                return False

    ####################
    # Question 3 de TP
    ####################
    # TODO: Compare in terms of performance
    if heuristic is None:
        return values
    elif heuristic == 0 and len(values[square]) == 2:
        values = heuristic_naked_pairs(values, square)
    elif heuristic == 1 and len(values[square]) == 2:
        values = heuristic_hidden_pairs(values, square)

    return values


####################
# Depth First Search
####################
def solve_depth_first_search(grid, use_random_parsing=False, heuristic=None):
    if not use_random_parsing:
        values = parse_grid_depth_first_search(grid, heuristic)
    else:
        values = parse_grid_hill_climbing(grid)
    return depth_first_search(values, use_random_parsing, heuristic)


def depth_first_search(values, use_random_parsing=False, heuristic=None):
    # Using depth-first search and propagation, try all possible values.
    if values is False:
        return False  # Failed earlier
    if all(len(values[square]) == 1 for square in squares):
        return values  # Solved!

    # Chose the unfilled square with the fewest possibilities
    length, square = min((len(values[square]), square) for square in squares if len(values[square]) > 1)

    ####################
    # Question 2 de TP
    ####################
    # TODO: Compare in terms of performance
    # n, square = random.choice(
    #    list(((len(values[square]), square) for square in squares if len(values[square]) > 1))
    # )  # choisir case et chiffre au hasard

    return some(
        depth_first_search(assign_depth_first_search(values.copy(), square, digit, heuristic), use_random_parsing,
                           heuristic) for digit in values[square])


def heuristic_naked_pairs(values, square):
    values_copy = values.copy()

    for peer in peers[square]:
        # If square and peer do not have the same indices, continue
        duplicate = values_copy[square]  # Values to remove from each peer
        if duplicate != values_copy[peer]:
            continue

        # Find mutual peers and eliminate the two values
        for unit in peers[square] & (peers[peer]):
            if not all(eliminate_depth_first_search(values_copy, unit, digit) for digit in duplicate):
                return False

        # We found a naked pair and there cannot be two
        break

    return values_copy


def heuristic_hidden_pairs(values, square):
    values_copy = values.copy()
    for peer in peers[square]:
        if len(values_copy[peer]) < 2:
            continue

        val_square = values_copy[square]
        val_peer = values_copy[peer]

        # Get digits that are in both squares
        mutual_val = set(val_square) & set(val_peer)

        if len(mutual_val) < 2:
            continue

        # Get the common peers
        mutual_peers = peers[square].intersection(peers[peer])
        for mutual_peer in mutual_peers:
            mutual_val = mutual_val - set(values_copy[mutual_peer])
        if mutual_val is None:
            continue

        # A hidden pair was found
        if len(mutual_val) == 2:
            eliminate_square = set(val_square) - mutual_val
            eliminate_peer = set(val_peer) - mutual_val
            if not all(
                    eliminate_depth_first_search(values_copy, square, digit) for digit in eliminate_square) or not all(
                eliminate_depth_first_search(values_copy, peer, digit) for digit in eliminate_peer
            ):
                return False
        break

    return values_copy


########################################################################################################################
########################################################################################################################
########################################################################################################################

####################
# Constraint Propagation Hill Climbing
####################
def assign_hill_climbing(values, square, digit):
    """Eliminate all the other values (except digit) from values[square] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[square].replace(digit, "")
    if all(eliminate_hill_climbing(values, square, digit_2) for digit_2 in other_values):
        return values
    else:
        return False


def eliminate_hill_climbing(values, square, digit):
    """Variant of eliminate(). This variant only checks the 3x3 unit instead
    of also checking rows and cols. Eliminate digit from values[square]; propagate
    when values or places <= 2. Return values, except return False if a
    contradiction is detected."""
    if digit not in values[square]:
        return values  # Already eliminated
    values[square] = values[square].replace(digit, "")

    # (1) If a square is reduced to one value digit_2, then eliminate digit_2 from the peers.
    if len(values[square]) == 0:
        return False  # Contradiction: removed last value
    elif len(values[square]) == 1:
        digit_2 = values[square]
        if not all(eliminate_hill_climbing(values, square_2, digit_2) for square_2 in get_box_neighbours(square)):
            return False
    # (2) If a unit is reduced to only one place for a value digit, then put it there.
    # Now we only check [units[square][2]] because we only care about squares in the same 3x3 unit
    # The added surrounding brackets are to keep the same code logic as eliminate()
    for unit in [units[square][2]]:
        digit_places = [square for square in unit if digit in values[square]]
        if len(digit_places) == 0:
            return False  # Contradiction: no place for this value
        elif len(digit_places) == 1:
            # digit can only be in one place in unit; assign it there
            if not assign_hill_climbing(values, digit_places[0], digit):
                return False
    return values


####################
# Hill Climbing
####################

def solve_hill_climbing(grid, use_random_parsing=False, heuristic=None):
    # TODO Check if we can use the same parse_grid function as in DFS
    if not use_random_parsing:
        values = parse_grid_depth_first_search(grid, heuristic)
    else:
        values = parse_grid_hill_climbing(grid)
    values = random_3x3_unit_fill(values)
    return hill_climbing(values)


def random_3x3_unit_fill(values):
    """Fill each 3x3 unit randomly, without considering
    conflicts outside the 3x3 unit"""

    values_copy = values.copy()
    # Try to fill until no square is left empty
    while not all(len(values_copy[square]) <= 1 for square in squares):
        # Use the same strategy as dfs() to select the square:
        # Chose the unfilled square with the fewest possibilities
        length, square = min((len(values_copy[square]), square) for square in squares if len(values_copy[square]) > 1)
        # Chose an available digit and assign it
        digit = random.choice(values_copy[square])
        assign_hill_climbing(values_copy, square, digit)

    return values_copy


def get_score(values):
    # The trick with len(set(counter)) - 9 was inspired by the following StackOverflow post:
    # https://stackoverflow.com/a/46959086
    #
    # It is a lot faster than the technique initially used (see comments below) because it
    # avoids iterating unnecessarily.
    #
    # Essentially, we want to count the number of conflicts in each row and col. The maximum number of conflicts
    # is 9, so we subtract 9 from the length of the set of values in each row and col to get the number of conflicts.
    # If all values are unique, the length of the set will be 9, so 9 - 9 = 0 conflicts. If there are any duplicates,
    # the length of the set will be less than 9, so 9 - (less than 9) = (more than 0) conflicts.

    total_conflicts = 0

    # Count the number of conflicts in each row/col
    for row in square_rows:
        # counter = {}
        counter = []
        for square in row:
            value = values[square]
            # counter[value] = counter.get(value, 0) + 1
            counter.append(value)
        # total_conflicts += sum([count - 1 for item, count in counter.items() if count > 1])
        total_conflicts += len(set(counter)) - 9

    for col in square_columns:
        # counter = {}
        counter = []
        for square in col:
            value = values[square]
            # counter[value] = counter.get(value, 0) + 1
            counter.append(value)
        # total_conflicts += sum([count - 1 for item, count in counter.items() if count > 1])
        total_conflicts += len(set(counter)) - 9

    # We want to minimize the number of conflicts
    # The score needs to increase when the number of conflicts decreases
    return total_conflicts


def get_potential_swaps(values):
    swaps = []
    swapped = set()
    for square in squares:
        # Copy the values to avoid modifying the original grid
        values_copy = values.copy()

        # Get the box containing the square, but exclude squares that have already been swapped
        box = set(get_box_neighbours(square)).difference(swapped)
        for peer in box:
            # Swap values
            values_copy[square], values_copy[peer] = values_copy[peer], values_copy[square]
            # Save the resulting grid
            swaps.append(values_copy)

        # Add square to swapped set as we have already tried all swaps
        swapped.add(square)
    return swaps


def hill_climbing(values):
    # Initialize the current state
    current_values = values

    # Loop until we reach a local maximum
    while True:
        # Initialize the potential best score and values
        potential_values = current_values
        potential_best_score = get_score(current_values)
        score_improved = False

        # Get the potential swaps
        potential_swaps = get_potential_swaps(current_values)

        # Compare the score of the potential swaps
        for swap in potential_swaps:
            # Get scode of the swap
            swap_score = get_score(swap)
            # Check if the swap is better than the current state
            if swap_score > potential_best_score:
                potential_values = swap
                potential_best_score = swap_score
                score_improved = True

        # If the potential best score is the same as the current score, we have reached a local maximum
        if not score_improved:
            return current_values

        # If we have not, we update the current state
        current_values = potential_values


########################################################################################################################
########################################################################################################################
########################################################################################################################


####################
# Simulated Annealing
####################

def solve_simulated_annealing(grid, use_random_parsing=False, schedule_constant=0.99, max_steps=10000):
    # TODO Check if we can use the same parse_grid function as in DFS
    if not use_random_parsing:
        values = parse_grid_depth_first_search(grid)
    else:
        values = parse_grid_hill_climbing(grid)
    values = random_3x3_unit_fill(values)
    return simulated_annealing(values, schedule_constant, max_steps)


def get_random_swap(values):
    # Copy the values to avoid modifying the original grid
    values_copy = values.copy()

    # Get the box containing the square, but exclude squares that have already been swapped
    square = random.choice(squares)
    neighbours = list(get_box_neighbours(square))
    neighbour = random.choice(neighbours)

    # Swap values
    values_copy[square], values_copy[neighbour] = values_copy[neighbour], values_copy[square]
    return values_copy


def simulated_annealing(values, schedule_constant=0.99, max_steps=10000):
    # Initialize the current state
    current_values = values
    t = 1
    for _ in range(max_steps):
        # Decrease the temperature
        t = schedule_constant * t

        # If the temperature is very low or if the board is solved, then
        # we have reached a local maximum
        if t == 0 or solved(current_values):
            return current_values

        # Get the potential swap
        potential_values = get_random_swap(current_values)
        # Calculate the score
        delta_e = get_score(potential_values) - get_score(current_values)

        # If the potential swap is better than the current state, we update the current state
        if delta_e > 0:
            current_values = potential_values

        # If the potential swap is worse than the current state, we update the current
        # state with a certain probability
        elif random.random() < pow(math.e, delta_e / t):
            current_values = potential_values

    # If we reached this point, that means we have not solved the puzzle
    # within the maximum number of steps
    return values


########################################################################################################################
########################################################################################################################
########################################################################################################################

#######################################
# OTHER STUFF
#######################################


####################
# Unit Tests
####################
def test():
    """A set of tests that must pass."""
    assert len(squares) == 81
    assert len(unit_list) == 27
    assert all(len(units[square]) == 3 for square in squares)
    assert all(len(peers[square]) == 20 for square in squares)
    assert units["C2"] == [
        ["A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2"],
        ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"],
        ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"],
    ]
    assert peers["C2"] == {"A2", "B2", "D2", "E2", "F2", "G2", "H2", "I2", "C1", "C3", "C4", "C5", "C6", "C7", "C8",
                           "C9", "A1", "A3", "B1", "B3"}
    print("All tests pass.")


####################
# Utilities
####################
def some(seq):
    """Return some element of seq that is true."""
    for e in seq:
        if e:
            return e
    return False


def from_file(filename, sep="\n"):
    """Parse a file into a list of strings, separated by sep."""
    return open(filename).read().strip().split(sep)


def shuffled(seq):
    """Return a randomly shuffled copy of the input sequence."""
    seq = list(seq)
    random.shuffle(seq)
    return seq


####################
# Display as 2-D grid
####################
def display(values):
    """Display these values as a 2-D grid."""
    width = 1 + max(len(values[square]) for square in squares)
    line = "+".join(["-" * (width * 3)] * 3)
    for row in rows:
        print("".join(values[row + col].center(width) + ("|" if col in "36" else "") for col in cols))
        if row in "CF":
            print(line)
    print()


####################
# Parse a Grid
####################
def parse_grid_hill_climbing(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    # To start, every square can be any digit; then assign values from the grid.
    values = dict((square, digits) for square in squares)
    for square, digit in grid_values(grid).items():
        if digit in digits and not assign_hill_climbing(values, square, digit):
            return False  # (Fail if we can't assign digit to square.)
    return values


def parse_grid_depth_first_search(grid, heuristic=None):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    # To start, every square can be any digit; then assign values from the grid.
    values = dict((square, digits) for square in squares)
    for square, digit in grid_values(grid).items():
        if digit in digits and not assign_depth_first_search(values, square, digit, heuristic):
            return False  # (Fail if we can't assign digit to square.)
    return values


def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = [column for column in grid if column in digits or column in "0."]
    assert len(chars) == 81
    return dict(zip(squares, chars))


####################
# System test
####################
def solved(values):
    """A puzzle is solved if each unit is a permutation of the digits 1 to 9."""

    def unitsolved(unit):
        return set(values[square] for square in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unit_list)


def solve_all(grids, name="", showif=0.0, algo="dfs", use_random_parsing=False, heuristic=None, schedule_constant=0.99,
              max_steps=10000):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles.

    algo: {hc: "Hill Climbing", sa: "Simulated Annealing", dfs: "Depth First Search"}
    use_random_parsing: {True, False}

    FOR SIMULATED ANNEALING:
    schedule_constant: {0.0 < float < 1.0}
    max_steps: {int}

    FOR NON-RANDOM PARSING: heuristic: {None, 0: "Naked Pairs", 1: "Hidden Pairs"}
    """

    def time_solve(grid):
        start_time = time.time_ns()

        if algo == "dfs":
            values = solve_depth_first_search(grid, use_random_parsing, heuristic)
        elif algo == "hc":
            values = solve_hill_climbing(grid, use_random_parsing, heuristic)
        elif algo == "sa":
            values = solve_simulated_annealing(grid, use_random_parsing, schedule_constant, max_steps)
        else:
            values = solve_depth_first_search(grid, use_random_parsing, heuristic)

        end_time = time.time_ns() - start_time

        # Display puzzles that take long enough
        if showif is not None and end_time > showif:
            display(grid_values(grid))
            if values:
                display(values)
            print("(%.2f nanoseconds)\n" % end_time)
        return end_time, solved(values)

    times, results = zip(*[time_solve(grid) for grid in grids])
    n = len(grids)
    if n >= 1:
        print(
            f"Solved {sum(results)}/{n} {name} puzzles:\n - {n / sum(times) * 1e9:.2f} Hz\n - avg {(sum(times) / n / 1e6):.2f} ms | {(sum(times) / n):,.2f} ns\n - max {max(times) / 1e6:.2f} ms | {max(times):,} ns. "
        )


def random_puzzle(n=17):
    """Make a random puzzle with n or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((square, digits) for square in squares)
    for square in shuffled(squares):
        if not assign_depth_first_search(values, square, random.choice(values[square])):
            break
        ds = [values[square] for square in squares if len(values[square]) == 1]
        if len(ds) >= n and len(set(ds)) >= 8:
            return "".join(values[square] if len(values[square]) == 1 else "." for square in squares)
    return random_puzzle(n)  # Give up and make a new puzzle


grid1 = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
grid2 = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......"
hard1 = ".....6....59.....82....8....45........3........6..3.54...325..6.................."

if __name__ == "__main__":
    test()
    # Algos: {hc: "Hill Climbing", dfs: "Depth First Search"}

    # For simulated Annealing
    schedule_constant = 0.99
    max_steps = 10000

    print("====================================================")
    print("Depth First Search - Non-random parsing")
    print("====================================================")
    algo = "dfs"
    use_random_parsing = False

    print("== No Heuristic ==")
    heuristic = None
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Naked Pairs ==")
    heuristic = 0
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Hidden Pairs ==")
    heuristic = 1
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("====================================================")
    print("Depth First Search - Random parsing")
    print("====================================================")
    print(" TOO LONG TO RUN")
    print()
    # algo = "dfs"
    # use_random_parsing = True
    #
    # print("== No Heuristic ==")
    # heuristic = None
    # solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
    #           max_steps)
    # print()

    print("====================================================")
    print("Hill Climbing - Non-random parsing")
    print("====================================================")
    algo = "hc"
    use_random_parsing = False

    print("== No Heuristic ==")
    heuristic = None
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Naked Pairs ==")
    heuristic = 0
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Hidden Pairs ==")
    heuristic = 1
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("====================================================")
    print("Hill Climbing - Random parsing")
    print("====================================================")
    algo = "hc"
    use_random_parsing = True

    print("== No Heuristic ==")
    heuristic = None
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("====================================================")
    print("Simulated Annealing - Non-random parsing")
    print("====================================================")
    algo = "sa"
    use_random_parsing = False

    print("== No Heuristic ==")
    heuristic = None
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Naked Pairs ==")
    heuristic = 0
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("== Hidden Pairs ==")
    heuristic = 1
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()

    print("====================================================")
    print("Simulated Annealing - Random parsing")
    print("====================================================")
    algo = "sa"
    use_random_parsing = True

    print("== No Heuristic ==")
    heuristic = None
    solve_all(from_file("sudoku_1000.txt"), "sudoku_1000", None, algo, use_random_parsing, heuristic, schedule_constant,
              max_steps)
    print()


    # solve_all(from_file("sudoku_100.txt"), "sudoku_100", None, algo, use_random_parsing, heuristic, schedule_constant,
    #           max_steps)
    # solve_all(from_file("top_95.txt"), "95sudoku", None, algo, use_random_parsing, heuristic, schedule_constant,
    #           max_steps)
    # solve_all([random_puzzle() for _ in range(99)], "random", None, algo, use_random_parsing, heuristic,
    #           schedule_constant, max_steps)
