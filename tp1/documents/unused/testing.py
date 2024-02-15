def random_3x3_unit_fill_old(grid):
    """Fill each 3x3 unit randomly, without considering
    conflicts outside the 3x3 unit"""
    # Convert grid string to mutable list
    grid = [*grid]

    for block_row in range(3):
        for block_col in range(3):
            # Generate set of all digits
            available_digits = set()
            [available_digits.add(digit) for digit in digits]

            # Find which digits are available
            for row in range(3):
                for col in range(3):
                    position = (block_row * 27) + (block_col * 3) + row * 9 + col
                    digit = grid[position]
                    available_digits.discard(digit) if digit != "." else None

            # Shuffle digits
            available_digits = shuffled(list(available_digits))
            for row in range(3):
                for col in range(3):
                    position = (block_row * 27) + (block_col * 3) + row * 9 + col
                    if grid[position] == ".":
                        grid[position] = available_digits.pop()

    return grid


def count_conflicts(grid):
    total = 0
    # Check conflicts in each row and col
    for i in range(9):
        # Initialize counter
        counter_row = {}
        counter_col = {}
        for j in range(9):
            item_row = grid[i * 9 + j]
            item_col = grid[i + 9 * j]

            # Count number apparitions of each digit
            if item_col != ".":
                counter_col[item_col] = counter_col.get(item_col, 0) + 1
            if item_row != ".":
                counter_row[item_row] = counter_row.get(item_row, 0) + 1

        total += sum([count for item, count in counter_row.items() if count > 1])
        total += sum([count for item, count in counter_col.items() if count > 1])

    return total


def count_conflicts_swap(grid, swapped_1, swapped_2):
    total = 0
    for swapped in [swapped_1, swapped_2]:
        # get row and col of swapped digit
        swapped_row = swapped // 9
        swapped_col = swapped % 9

        # Initialize counter
        counter_row = {}
        counter_col = {}

        # Iterate through swapped digit row and col
        for i in range(9):
            item_row = grid[swapped_row * 9 + i]
            item_col = grid[i * 9 + swapped_col]

            # Count number apparitions of each digit
            if item_col != ".":
                counter_col[item_col] = counter_col.get(item_col, 0) + 1
            if item_row != ".":
                counter_row[item_row] = counter_row.get(item_row, 0) + 1

        total += sum([count for item, count in counter_row.items() if count > 1])
        total += sum([count for item, count in counter_col.items() if count > 1])

    return total


def get_same_block_squares(index):
    # Get the top left position in the current block
    block_x = (index % 9) // 3
    block_y = (index // 9) // 3

    # Get the positions that are in the same block as index
    same_block = []
    for row in range(3):
        for col in range(3):
            position = (block_x * 27) + (block_y * 3) + row * 9 + col
            if position != index:
                same_block.append((block_x * 27) + (block_y * 3) + row * 9 + col)

    return same_block


def hill_climbing(grid):
    while True:
        improved = False
        swapped_set = set()
        # For each square, try to swap it with every square in its own block
        for swapped_1 in range(81):
            neighbours = get_same_block_squares(swapped_1)
            for swapped_2 in neighbours:
                if (swapped_1, swapped_2) in swapped_set:
                    continue

                # Get the current number of conflicts
                initial_conflicts = count_conflicts_swap(grid, swapped_1, swapped_2)

                temp_grid = grid.copy()

                # Get the keys corresponding to the selected positions
                temp_grid[swapped_1], temp_grid[swapped_2] = temp_grid[swapped_2], temp_grid[swapped_1]

                # Get the number of conflicts after the swap
                new_conflicts = count_conflicts_swap(temp_grid, swapped_1, swapped_2)

                # If the new configuration has fewer conflicts, accept the swap
                if new_conflicts <= initial_conflicts:
                    improved = True
                    grid = temp_grid

                swapped_set.add((swapped_1, swapped_2))
                swapped_set.add((swapped_2, swapped_1))

        if not improved:
            break

    if count_conflicts(grid) == 0:
        return parse_grid(grid)
    else:
        return False
