# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete the warehouse domain.

'''
Construct and return Kropki Grid CSP models.
'''

from cspbase import *
import itertools


class KropkiBoard:
    '''Abstract class for defining KropkiBoards for search routines'''

    def __init__(self, dim, cell_values, consec_row, consec_col, double_row, double_col):
        '''Problem specific state space objects must always include the data items
           a) self.dim === the dimension of the board (rows, cols)
           b) self.cell_values === a list of lists. Each list holds values in a row on the grid. Values range from 1 to dim);
           -1 represents a value that is yet to be assigned.
           c) self.consec_row === a list of lists. Each list holds values that indicate where adjacent values in a row must be
           consecutive.  For example, if a list has a value of 1 in position 0, this means the values in the row between 
           index 0 and index 1 must be consecutive. In general, if a list has a value of 1 in position i,
           this means the values in the row between index i and index i+1 must be consecutive.
           d) self.consec_col === a list of lists. Each list holds values to indicate where adjacent values in a column must be 
           consecutive. Same idea as self.consec_row, but for columns instead of rows.
           e) self.double_row === a list of lists. Each list holds values to indicate where adjacent values in a row must be
           hold two values, one of which is the twice the value of the other.  For example, if a list has a value of 1 in 
           position 0, this means the value in the row at index 0 myst be either twice or one half the value at index 1 in the row.
           f) self.double_col === a list of lists. Each list holds values to indicate where adjacent values in a column must be
           hold two values, one of which is the twice the value of the other.  For example, if a list has a value of 1 in 
           position 0, this means the value in the column at index 0 myst be either twice or one half the value at index 1 in that
           column.
        '''
        self.dim = dim
        self.cell_values = cell_values
        self.consec_row = consec_row
        self.consec_col = consec_col
        self.double_row = double_row
        self.double_col = double_col


def kropki_csp_model_1(initial_kropki_board):
    '''Return a tuple containing a CSP object representing a Kropki Grid CSP problem along 
       with an array of variables for the problem. That is, return

       kropki_csp, variable_array

       where kropki_csp is a csp representing Kropki grid of dimension N using model_1
       and variable_array is a list such that variable_array[i*N+j] is the Variable 
       (object) that you built to represent the value to be placed in cell i,j of
       the Kropki Grid.
              
       The input board is specified as a KropkiBoard (see the class definition above)
              
       This routine returns model_1 which consists of a variable for
       each cell of the board, with domain equal to {1-N} if the board
       has a -1 at that position, and domain equal {i} if the board has
       a non-negative number i at that cell.
       
       model_1 contains BINARY CONSTRAINTS OF NOT-EQUAL between
       all relevant variables (e.g., all variables in the
       same row, etc.).

       model_1 also contains binary consecutive and double constraints for each 
       column and row, as well as sub-square constraints.

       Note that we will only test on boards of size 6x6, 9x9 and 12x12
       Subsquares on boards of dimension 6x6 are each 2x3.
       Subsquares on boards of dimension 9x9 are each 3x3.
       Subsquares on boards of dimension 12x12 are each 4x3.
    '''
    # IMPLEMENT
    global c, c1
    csp = CSP("kropki_csp_model_1")
    variables = []
    lst = record_domain_values_in_list(initial_kropki_board)
    for row in range(0, initial_kropki_board.dim):
        # sort_by_row.append()
        for col in range(0, initial_kropki_board.dim):
            variable = Variable('V{}'.format((row * initial_kropki_board.dim + col) + 1))
            # assigned_value = initial_kropki_board.cell_values[row][col]
            variable.add_domain_values(lst)
            csp.add_var(variable)

    sort_by_row = sort_variable_by_row(csp, initial_kropki_board)
    sort_by_col = sort_variable_by_col(sort_by_row, initial_kropki_board)
    sort_by_subsquare = sort_variable_by_sub_square(sort_by_row, initial_kropki_board)
    # print(sort_by_row)
    # print(sort_by_col)
    # print(sort_by_subsquare)
    # print(sort_by_col)

    # add all normal sodoku(row, col, sub square) constraints into csp
    cons_row = []
    cons_col = []
    cons_square = []
    for i in range(0, initial_kropki_board.dim):
        for j in range(0, initial_kropki_board.dim):
            for k in range(1 + j, initial_kropki_board.dim):
                c = Constraint("C(Q{},Q{})".format(j + 1, k + 1), [sort_by_row[i][j], sort_by_row[i][k]])
                c1 = Constraint("C(Q{},Q{})".format(i + 1, k + 1), [sort_by_col[i][j], sort_by_col[i][k]])
                c2 = Constraint("C(Q{},Q{})".format(i + 1, k + 1), [sort_by_subsquare[i][j], sort_by_subsquare[i][k]])
                # print(sort_by_row[i][j], sort_by_row[i][k])
                sat_tuples = []
                for item in itertools.product(lst, lst):
                    if item[0] != item[1]:
                        # if queensCheck(k, j, item[0], item[1]):
                        sat_tuples.append(item)
                # print(sat_tuples)
                c.add_satisfying_tuples(sat_tuples)
                c1.add_satisfying_tuples(sat_tuples)
                c2.add_satisfying_tuples(sat_tuples)
                cons_row.append(c)
                cons_col.append(c1)
                cons_square.append(c2)
    for c_row in cons_row:
        csp.add_constraint(c_row)
    for c_col in cons_col:
        csp.add_constraint(c_col)
    for c_square in cons_square:
        csp.add_constraint(c_square)
    # c = None
    # c1 = None

    # add all consecutive row/col constraints into csp
    cons_consec_row = []
    cons_consec_col = []
    for i in range(0, len(initial_kropki_board.consec_row)):
        for j in range(1, len(initial_kropki_board.consec_row)):
            if initial_kropki_board.consec_row[i][j - 1] == 1:
                c = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
            if initial_kropki_board.consec_col[i][j - 1] == 1:
                c1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
            sat_tuples = []
            for item in itertools.product(lst, lst):
                if abs(item[0] - item[1]) == 1:
                    sat_tuples.append(item)
            c.add_satisfying_tuples(sat_tuples)
            c1.add_satisfying_tuples(sat_tuples)
            cons_consec_row.append(c)
            cons_consec_col.append(c1)
    for c_consec_row in cons_consec_row:
        csp.add_constraint(c_consec_row)
    for c_consec_col in cons_consec_col:
        csp.add_constraint(c_consec_col)

    # add all double row/col constraints into csp
    cons_double_row = []
    cons_double_col = []
    for i in range(0, len(initial_kropki_board.double_row)):
        for j in range(1, len(initial_kropki_board.double_row)):
            if initial_kropki_board.double_row[i][j - 1] == 1:
                c = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
            if initial_kropki_board.double_col[i][j - 1] == 1:
                c1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
            sat_tuples = []
            for item in itertools.product(lst, lst):
                if item[0] * 2 == item[1] or item[1] * 2 == item[0]:
                    sat_tuples.append(item)
            c.add_satisfying_tuples(sat_tuples)
            c1.add_satisfying_tuples(sat_tuples)
            cons_double_row.append(c)
            cons_double_col.append(c1)
    for c_double_row in cons_double_row:
        csp.add_constraint(c_double_row)
    for c_double_col in cons_double_col:
        csp.add_constraint(c_double_col)

    # print(len(csp.get_all_cons()))
    return csp, variables  # change this!


def sort_variable_by_row(csp, board):
    """ Sort variables by rows """
    lst = csp.get_all_vars()
    length = board.dim
    helper_lst = []
    final = []
    count = 0
    for i in lst:
        helper_lst.append(i)
        count += 1
        if count == length:
            copy = helper_lst.copy()
            final.append(copy)
            helper_lst.clear()
            count = 0
    return final


def sort_variable_by_col(lst, board):
    """ Sort variables by cols """
    final = []
    for item in range(0, board.dim):
        helper = []
        for num in range(0, len(lst)):
            helper.append(lst[num][item])
        final.append(helper)
    return final


def sort_variable_by_sub_square(lst, board):
    """ Sort variables by sub squares """
    size = 9
    width = board.dim // 3
    height = 3
    square1 = []
    square2 = []
    square3 = []
    square4 = []
    square5 = []
    square6 = []
    square7 = []
    square8 = []
    square9 = []
    final = []
    for i in range(0, height):
        for j in range(0, width):
            square1.append(lst[i][j])
    final.append(square1)

    for i in range(0, height):
        for j in range(width, board.dim - width):
            square2.append(lst[i][j])
    final.append(square2)

    for i in range(0, height):
        for j in range(board.dim - width, board.dim):
            square3.append(lst[i][j])
    final.append(square3)

    if board.dim == 6:  # case for 6x6
        for col in range(height, board.dim):
            for row in range(0, width):
                square4.append(lst[col][row])
        final.append(square4)

        for col in range(height, board.dim):
            for row in range(width, board.dim - width):
                square5.append(lst[col][row])
        final.append(square5)

        for col in range(height, board.dim):
            for row in range(board.dim - width, board.dim):
                square6.append(lst[col][row])
        final.append(square6)
    else:  # case for 9x9
        for col in range(height, size - height):
            for row in range(0, width):
                square4.append(lst[col][row])
        final.append(square4)

        for col in range(height, size - height):
            for row in range(width, board.dim - width):
                square5.append(lst[col][row])
        final.append(square5)

        for col in range(height, size - height):
            for row in range(board.dim - width, board.dim):
                square6.append(lst[col][row])
        final.append(square6)

        for col in range(size - height, size):
            for row in range(0, width):
                square7.append(lst[col][row])
        final.append(square7)

        for col in range(size - height, size):
            for row in range(width, board.dim - width):
                square8.append(lst[col][row])
        final.append(square8)

        for col in range(size - height, size):
            for row in range(board.dim - width, size):
                square9.append(lst[col][row])
        final.append(square9)
    return final


def record_domain_values_in_list(board):
    """ record the possible values for a variable's domain.
        For example, if the board dimension is 9, then the return lst = [1,2,3,4,5,6,7,8,9]
    """
    lst = []
    for num in range(1, board.dim + 1):
        lst.append(num)
    return lst


def kropki_csp_model_2(initial_kropki_board):
    '''Return a tuple containing a CSP object representing a Kropki Grid CSP problem along
       with an array of variables for the problem. That is return

       kropki_csp, variable_array

       where kropki_csp is a csp representing Kropki grid of dimension N using model_2
       and variable_array is a list such that variable_array[i*N+j] is the Variable 
       (object) that you built to represent the value to be placed in cell i,j of
       the Kropki Grid.
              
       The input board is specified as a KropkiBoard (see the class definition above)
              
       This routine returns model_2 which consists of a variable for
       each cell of the board, with domain equal to {1-N} if the board
       has a -1 at that position, and domain equal {i} if the board has
       a non-negative number i at that cell.
       
       model_2 contains N-ARY CONSTRAINTS OF NOT-EQUAL between
       all relevant variables (e.g., all variables in the
       same row, etc.).

       model_2 also contains binary consecutive and double constraints for each 
       column and row, as well as sub-square constraints.

       Note that we will only test on boards of size 6x6, 9x9 and 12x12
       Subsquares on boards of dimension 6x6 are each 2x3.
       Subsquares on boards of dimension 9x9 are each 3x3.
       Subsquares on boards of dimension 12x12 are each 4x3.
    '''
    # IMPLEMENT
    global c, c1, d, d1, d2, d3, c2
    csp = CSP("kropki_csp_model_2")
    lst = record_domain_values_in_list(initial_kropki_board)
    variables = []
    for row in range(0, initial_kropki_board.dim):
        # sort_by_row.append()
        for col in range(0, initial_kropki_board.dim):
            variable = Variable('V{}'.format((row * initial_kropki_board.dim + col) + 1))
            # assigned_value = initial_kropki_board.cell_values[row][col]
            variable.add_domain_values(lst)
            csp.add_var(variable)
    sort_by_row = sort_variable_by_row(csp, initial_kropki_board)
    sort_by_col = sort_variable_by_col(sort_by_row, initial_kropki_board)
    sort_by_subsquare = sort_variable_by_sub_square(sort_by_row, initial_kropki_board)

    cons_row = []
    cons_col = []
    cons_square = []
    # d = None
    # d1 = None
    # d2 = None
    # d3 = None
    for i in range(0, initial_kropki_board.dim):
        sat_tuples = []
        sat_tuples1 = []
        sat_tuples2 = []
        c = Constraint("C(Row{})".format(i + 1), sort_by_row[i])
        c1 = Constraint("C(Col{})".format(i + 1), sort_by_col[i])
        c2 = Constraint("C(Square{})".format(i + 1), sort_by_subsquare[i])

        if initial_kropki_board.dim == 6:
            for item in itertools.permutations(lst, 6):
                if len(item) == len(set(item)):
                    sat_tuples.append(item)

        elif initial_kropki_board.dim == 9:

            for item in itertools.permutations(lst, 9):
                if len(item) == len(set(item)):
                    # print(item)
                    sat_tuples.append(item)

        c.add_satisfying_tuples(sat_tuples)
        c1.add_satisfying_tuples(sat_tuples)
        c2.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(c)
        csp.add_constraint(c1)
        csp.add_constraint(c2)
        for j in range(1, initial_kropki_board.dim):
            if initial_kropki_board.double_row[i][j - 1] == 1:
                d = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
                sat_tuples1 = []
                for item in itertools.product(lst, lst):
                    if item[0] * 2 == item[1] or item[1] * 2 == item[0]:
                        sat_tuples1.append(item)
                d.add_satisfying_tuples(sat_tuples1)
                csp.add_constraint(d)
            if initial_kropki_board.double_col[i][j - 1] == 1:
                d1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
                sat_tuples1 = []
                for item in itertools.product(lst, lst):
                    if item[0] * 2 == item[1] or item[1] * 2 == item[0]:
                        sat_tuples1.append(item)
                d1.add_satisfying_tuples(sat_tuples1)
                csp.add_constraint(d1)

            if initial_kropki_board.consec_row[i][j - 1] == 1:
                d2 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
                sat_tuples2 = []
                for item in itertools.product(lst, lst):
                    if abs(item[0] - item[1]) == 1:
                        sat_tuples2.append(item)
                d2.add_satisfying_tuples(sat_tuples2)
                csp.add_constraint(d2)

            if initial_kropki_board.consec_col[i][j - 1] == 1:
                d3 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
                sat_tuples2 = []
                for item in itertools.product(lst, lst):
                    if abs(item[0] - item[1]) == 1:
                        sat_tuples2.append(item)
                d3.add_satisfying_tuples(sat_tuples2)
                csp.add_constraint(d3)
        #     if initial_kropki_board.consec_row[i][j - 1] == 1:
        #         d = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
        #     if initial_kropki_board.consec_col[i][j - 1] == 1:
        #         d1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
        #     if initial_kropki_board.double_row[i][j - 1] == 1:
        #         d2 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
        #     if initial_kropki_board.double_col[i][j - 1] == 1:
        #         d3 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
        #
        #     if initial_kropki_board.dim == 6:
        #         # for item in itertools.product(lst, lst, lst, lst, lst, lst):
        #         #     if len(item) == len(set(item)):
        #         #
        #         #     # print(item)
        #         #         sat_tuples.append(item)
        #         for it in itertools.product(lst, lst):
        #             if abs(it[0] - it[1]) == 1:
        #                 if it not in sat_tuples2:
        #                     sat_tuples1.append(it)
        #             elif it[0] * 2 == it[1] or it[1] * 2 == it[0]:
        #                 if it not in sat_tuples1:
        #                     sat_tuples2.append(it)
        #
        #     elif initial_kropki_board.dim == 9:
        #         # for item in itertools.product(lst, lst, lst, lst, lst, lst, lst, lst, lst):
        #         #     if len(item) == len(set(item)):
        #         #     # print(item)
        #         #         sat_tuples.append(item)
        #         for it in itertools.product(lst, lst):
        #             if abs(it[0] - it[1]) == 1:
        #                 if it not in sat_tuples2:
        #                     sat_tuples1.append(it)
        #             elif it[0] * 2 == it[1] or it[1] * 2 == it[0]:
        #                 if it not in sat_tuples1:
        #                     sat_tuples2.append(it)
        #     # print("111", sat_tuples)
        #     if d is not None and d.scope != []:
        #         d.add_satisfying_tuples(sat_tuples1)
        #         csp.add_constraint(d)
        #     if d1 is not None and d1.scope != []:
        #         d1.add_satisfying_tuples(sat_tuples1)
        #         csp.add_constraint(d1)
        #     if d2 is not None and d2.scope != []:
        #         d2.add_satisfying_tuples(sat_tuples2)
        #         csp.add_constraint(d2)
        #     if d3 is not None and d3.scope!= []:
        #         d3.add_satisfying_tuples(sat_tuples2)
        #         csp.add_constraint(d3)
        # csp.add_constraint(c)
        # csp.add_constraint(c1)
        # csp.add_constraint(c2)
        #     csp.add_constraint(d)
        #     csp.add_constraint(d1)
        #     csp.add_constraint(d2)
        #     csp.add_constraint(d3)
    #     cons_row.append(c)
    #     cons_col.append(c1)
    #     cons_square.append(c2)
    # print(cons_row)
    # print(cons_col)
    # print(cons_square)
    # for c_row in cons_row:
    #     csp.add_constraint(c_row)
    # for c_col in cons_col:
    #     csp.add_constraint(c_col)
    # for c_square in cons_square:
    #     csp.add_constraint(c_square)
    # print(len(csp.get_all_cons()))

    # cons_consec_row = []
    # cons_consec_col = []
    # for i in range(0, len(initial_kropki_board.consec_row)):
    #     for j in range(1, len(initial_kropki_board.consec_row)):
    #         if initial_kropki_board.consec_row[i][j - 1] == 1:
    #             c = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
    #         if initial_kropki_board.consec_col[i][j - 1] == 1:
    #             c1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
    #         sat_tuples = []
    #         for item in itertools.product(lst, lst):
    #             if abs(item[0] - item[1]) == 1:
    #                 sat_tuples.append(item)
    #         c.add_satisfying_tuples(sat_tuples)
    #         c1.add_satisfying_tuples(sat_tuples)
    #         cons_consec_row.append(c)
    #         cons_consec_col.append(c1)
    # # print(len(cons_consec_row))
    # # print(len(cons_consec_col))
    # for c_consec_row in cons_consec_row:
    #     csp.add_constraint(c_consec_row)
    # for c_consec_col in cons_consec_col:
    #     csp.add_constraint(c_consec_col)
    # print(csp.get_all_cons())
    #
    # cons_double_row = []
    # cons_double_col = []
    # for i in range(0, len(initial_kropki_board.double_row)):
    #     for j in range(1, len(initial_kropki_board.double_row)):
    #         if initial_kropki_board.double_row[i][j - 1] == 1:
    #             c = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_row[i][j - 1], sort_by_row[i][j]])
    #         if initial_kropki_board.double_col[i][j - 1] == 1:
    #             c1 = Constraint("C(Q{},Q{})".format(j, j + 1), [sort_by_col[i][j - 1], sort_by_col[i][j]])
    #         sat_tuples = []
    #         for item in itertools.product(lst, lst):
    #             if item[0] * 2 == item[1] or item[1] * 2 == item[0]:
    #                 sat_tuples.append(item)
    #         c.add_satisfying_tuples(sat_tuples)
    #         c1.add_satisfying_tuples(sat_tuples)
    #         cons_double_row.append(c)
    #         cons_double_col.append(c1)
    # for c_double_row in cons_double_row:
    #     csp.add_constraint(c_double_row)
    # for c_double_col in cons_double_col:
    #     csp.add_constraint(c_double_col)

    return csp, variables  # change this!
