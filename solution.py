from utils import *

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    naked_twins = list()
    for unit in unitlist:
        naked_twins += [ (unit[a],unit[b]) for a in range(0,len(unit)) for b in range(a,len(unit))
            if unit[a] != unit[b] and len(values[unit[a]]) == 2 and values[unit[a]] == values[unit[b]] ]

    # Eliminate the naked twins as possibilities for their peers
    for box1,box2 in set(naked_twins):
        shared_peers = [ box for box in peers[box1] if box in peers[box2] ]
        for box in shared_peers:
            values = assign_value(values, box, values[box].replace(values[box1][0],'').replace(values[box1][1],''))

    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved = [ box for box in values.keys() if len(values[box])== 1 ]
    for box in solved:
        value = values[box]
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(value,''))

    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    new_values = values.copy()  # note: do not modify original values
    for box_name in units:
        for unit in units[box_name]:
            choices = "".join([ values[box] for box in unit ])
            one_choices = [choice for choice in choices if len(choices) == (len(choices.replace(choice,"")) + 1)]

            for box in unit:
                for choice in one_choices:
                    if choice in values[box]:
                        new_values = assign_value(new_values, box, choice)
                        one_choices.remove(choice)
                        break
    return new_values

def reduce_puzzle(values):
    """
    Apply constraints iteratively until the puzzle is solved or stalled
    Args:
        values: Sudoku grid in dictionary form
    Returns:
        False: if a box has no possibilities
        values: dictionary of values with constraints applied
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    solved = False
    while not stalled and not solved:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Eliminate Strategy
        values = eliminate(values)
        # Only Choice Strategy
        values = only_choice(values)
        # Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # If puzzle is solved, stop the loop
        solved = len(values) == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Args:
        values: Sudoku in dictionary form.
    Returns:
        solved or reduced puzzle dictionary or False if unable to reduce
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[box]) == 1 for box in values):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    size,box = min((len(values[box]),box) for box in values.keys() if len(values[box]) > 1)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for option in values[box]:
        new_values = values.copy()
        new_values[box] = option
        new_values = search(new_values)
        if not new_values:
            continue
        return new_values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
