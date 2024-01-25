import sys


def get_input(input_file):
    with open(input_file, "r") as f:
        # Store all constraints in a dictionary
        constraints = dict()
        for x in ["highs_each_row", "bases_each_row", "highs_each_column", "bases_each_column"]:
            constraints[x] = [int(y) for y in f.readline().split()]
        board = []

        for row in f.readlines():
            board.append(row.split())

        return board, constraints


def is_valid_move(board, cell):
    # Checks given cells neighbors' values and returns false if
    # cell's value = B and one of the neighbors is B
    # cell's value = H and one of the neighbors is H
    neighbor_values = [cell[2] for cell in find_neighbors(board, cell)]
    if cell[2] == "B":
        return "B" not in neighbor_values
    elif cell[2] == "H":
        return "H" not in neighbor_values

    return True


def possible_candidates(board, cell):
    # searches for possible tile pairs for the cell and it's other half
    candidates = []
    other_half = find_other_half(board, cell)
    # Try H first then B at last N
    for value, other_half_value in zip("HBN", "BHN"):
        possible_cell = (cell[0], cell[1], value)
        possible_other_half_cell = (other_half[0], other_half[1], other_half_value)
        if is_valid_move(board, possible_cell) and is_valid_move(board, possible_other_half_cell):
            candidates.append(possible_cell[2])

    return candidates


def is_on_board(board, cell):
    # Checks if the cell is in the boundaries of the board
    number_of_columns = len(board[0])
    number_of_rows = len(board)
    if 0 <= cell[0] < number_of_rows and 0 <= cell[1] < number_of_columns:
        return True

    return False


def append_if_on_board(board, alist, cells):
    for cell in cells:
        if is_on_board(board, cell):
            alist.append(cell + (board[cell[0]][cell[1]],))


def find_vertical_neighbors(board, cell):
    neighbors = []
    # Check up and down of the cell if they exist add them to set
    append_if_on_board(board, neighbors, [(cell[0] - 1, cell[1]), (cell[0] + 1, cell[1])])
    return neighbors


def find_horizontal_neighbors(board, cell):
    neighbors = []
    # Check left, right of the cell if they exist add them to set
    append_if_on_board(board, neighbors, [(cell[0], cell[1] - 1), (cell[0], cell[1] + 1)])
    return neighbors


def find_neighbors(board, cell):
    return find_vertical_neighbors(board, cell) + find_horizontal_neighbors(board, cell)


def find_other_half(board, cell):
    # finds the value of other_half of the cell
    # example: L -> R, D -> U ...
    vertical_neighbors = find_vertical_neighbors(board, cell)
    horizontal_neighbors = find_horizontal_neighbors(board, cell)
    if cell[2] == "L":
        for neighbor in horizontal_neighbors:
            if neighbor[2] == "R":
                return neighbor

    if cell[2] == "R":
        for neighbor in horizontal_neighbors:
            if neighbor[2] == "L":
                return neighbor

    if cell[2] == "U":
        for neighbor in vertical_neighbors:
            if neighbor[2] == "D":
                return neighbor

    if cell[2] == "D":
        for neighbor in vertical_neighbors:
            if neighbor[2] == "U":
                return neighbor


def place_tile(board, cell, value):
    board[cell[0]][cell[1]] = value
    other_half = find_other_half(board, cell)
    if value == "H":
        board[other_half[0]][other_half[1]] = "B"
    if value == "B":
        board[other_half[0]][other_half[1]] = "H"
    if value == "N":
        board[other_half[0]][other_half[1]] = "N"


def remove_tile(board, cell, other_half):
    board[cell[0]][cell[1]] = cell[2]
    board[other_half[0]][other_half[1]] = other_half[2]


def appearance_in_column(board, column_index, char):
    # returns how many times the char appeared in a column
    i = 0
    for row in board:
        if row[column_index] == char:
            i += 1

    return i


def check_row(row_id, row, constraints):
    # Returns False if row do not match constraints
    if constraints["highs_each_row"][row_id] != -1 and row.count("H") != constraints["highs_each_row"][row_id]:
        return False
    if constraints["bases_each_row"][row_id] != -1 and row.count("B") != constraints["bases_each_row"][row_id]:
        return False
    return True


def check_columns(board, constraints):
    for column_id in range(len(board[0])):
        if (constraints["highs_each_column"][column_id] != -1 and
                appearance_in_column(board, column_id, "H") != constraints["highs_each_column"][column_id]):
            return False
        if (constraints["bases_each_column"][column_id] != -1 and
                appearance_in_column(board, column_id, "B") != constraints["bases_each_column"][column_id]):
            return False

    return True


def find_empty_cell(board):
    # Checks is there any empty cell on the board
    for row_index, row in enumerate(board):
        for column_index, value in enumerate(row):
            if value in ["L", "R", "U", "D"]:
                return row_index, column_index, value

    return None


def write_output(board, output_file):
    with open(output_file, "w") as f:
        output = "\n".join([" ".join(row) for row in board])
        f.write(output)


def write_error(output_file):
    with open(output_file, "w") as f:
        f.write("No solution!")


def solve_game(board, constraints, output_file):
    is_solved = [False,]

    def solve(board, constraints, output_file, is_solved):
        # Stop recursive operation if the game is already solved
        if is_solved[0]:
            return

        cell = find_empty_cell(board)
        if cell is None:
            # Check the last row and columns constraints stop if the game is solved
            if check_columns(board,constraints) and check_row(len(board) - 1, board[-1], constraints):
                write_output(board, output_file)
                is_solved[0] = True
            return

        # Stop if upper row do not match the constraints
        if cell[0] > 0 and not check_row(cell[0] - 1, board[cell[0] - 1], constraints):
            return

        other_half = find_other_half(board, cell)

        # Place each possible tile one by one and solve the game
        for candidate in possible_candidates(board, cell):
            place_tile(board, cell, candidate)

            solve(board, constraints, output_file, is_solved)

            remove_tile(board, cell, other_half)

    solve(board, constraints, output_file, is_solved)
    if not is_solved[0]:
        write_error(output_file)


def main(input_file, output_file):
    board, constraints = get_input(input_file)
    solve_game(board, constraints, output_file)


"""TESTS"""
def test_appearance_in_column(board):
    assert appearance_in_column(board, 0, "B") == 2
    assert appearance_in_column(board, 2, "N") == 1
    assert appearance_in_column(board, 1, "N") == 0


def test_get_input(board, constraints):
    board_input, constraints_input = get_input("i1.txt")
    assert board == board_input
    assert constraints == constraints_input


# test some important functions and check if the game works for  input and output pairs
def tests():
    board_in = [["L", "R", "L", "R"],
                ["U", "U", "L", "R"],
                ["D", "D", "L", "R"]]

    board_out = [["B", "H", "B", "H"],
                 ["H", "B", "N", "N"],
                 ["B", "H", "B", "H"]]

    constraints = {"highs_each_row": [2, -1, -1],
                   "bases_each_row": [-1, -1, 2],
                   "highs_each_column": [-1, 2, -1, -1],
                   "bases_each_column": [-1, -1, -1, 0]}

    test_get_input(board_in, constraints)
    test_appearance_in_column(board_out)

    for in_path, out_path in zip(["i1.txt", "i2.txt", "i3.txt", "i4.txt", "i5.txt"],
                                 ["o1.txt", "o2.txt", "o3.txt", "o4.txt", "o5.txt"]):
        out = "oo.txt"
        main(in_path, out)
        with open(out, "r") as out:
            with open(out_path, "r") as out_expected:
                if out.read() != out_expected.read():
                    print(f"there is difference in {out_path}")
                else:
                    print(f"output is the same with {out_path}")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

