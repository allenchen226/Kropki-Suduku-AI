# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented.
import queue

'''
This file will contain different constraint propagators to be used within
bt_search.

propagator == a function with the following template
    propagator(csp, newly_instantiated_variable=None)
        ==> returns (True/False, [(Variable, Value), (Variable, Value) ...])

    csp is a CSP object---the propagator can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    newly_instaniated_variable is an optional argument.
    if newly_instantiated_variable is not None:
        then newly_instantiated_variable is the most
        recently assigned variable of the search.
    else:
        propagator is called before any assignments are made
        in which case it must decide what processing to do
        prior to any variables being assigned. SEE BELOW

    The propagator returns True/False and a list of (Variable, Value) pairs.

    Returns False if a deadend has been detected by the propagator.
        in this case bt_search will backtrack
    Returns True if we can continue.

    The list of variable values pairs are all of the values
    the propagator pruned (using the variable's prune_value method).
    bt_search NEEDS to know this in order to correctly restore these
    values when it undoes a variable assignment.

    NOTE propagator SHOULD NOT prune a value that has already been
    pruned! Nor should it prune a value twice.

    IF PROPAGATOR is called with newly_instantiated_variable = None
        PROCESSING REQUIRED:
            for plain backtracking (where we only check fully instantiated
            constraints) we do nothing...return (true, [])

            for forward checking (where we only check constraints with one
            remaining variable) we look for unary constraints of the csp
            (constraints whose scope contains only one variable) and we
            forward_check these constraints.

            for gac we establish initial GAC by initializing the GAC queue with
            all constaints of the csp

    IF PROPAGATOR is called with newly_instantiated_variable = a variable V
        PROCESSING REQUIRED:
            for plain backtracking we check all constraints with V (see csp
            method get_cons_with_var) that are fully assigned.

            for forward checking we forward check all constraints with V that
            have one unassigned variable left

            for gac we initialize the GAC queue with all constraints containing
            V.
'''


def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''
    # IMPLEMENT
    restore_lst = []

    if newVar is not None:
        all_constraints = csp.get_cons_with_var(newVar)
    else:
        all_constraints = csp.get_all_cons()

    for c in all_constraints:

        # restore_lst = []
        # num = c.get_n_unasgn()
        # if num == 1:
        #     variable_in_list = c.get_unasgn_vars()
        #     variable = variable_in_list[0]
        for variable in c.get_unasgn_vars():
            for value in variable.cur_domain():
                if not c.has_support(variable, value):
                    variable.prune_value(value)
                    restore_lst.append((variable, value))
                    # print("before",variable.cur_domain())
                    # status, pruned = FCCheck(c, variable)
                    # print("after", variable.cur_domain())
                    if len(variable.cur_domain()) == 0:
                        return False, restore_lst
            # for v in pruned:
            #     restore_lst.append(v)
            # if status:
            #     return False, restore_lst

    # print(restore_lst)
    # if flag:
    #     return False, restore_lst
    return True, restore_lst


# def FCCheck(c, x):
#     """Follows the template the slide given, c is a constraint and x is a variable"""
#     DWO = True
#     pruned_value = []  # used to record the pruned values
#     # print(x.cur_domain())
#     for d in x.cur_domain():
#         if not c.has_support(x, d):
#             x.prune_value(d)
#             pruned_value.append(d)  # add pruned value to a list, for restore purpose
#     # print(x.cur_domain())
#     # print(pruned_value)
#         if len(x.cur_domain()) == 0:
#             return DWO, pruned_value
#     return False, pruned_value


GACQueue = queue.Queue()


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    # Follow the pseudocode example from lec slides.
    prund_lst = []
    if newVar is not None:
        all_constraints = csp.get_cons_with_var(newVar)
    else:
        all_constraints = csp.get_all_cons()

    check_lst = make_Queue_and_check_list(all_constraints)

    while not GACQueue.empty():
        constraints = GACQueue.get()
        if constraints in check_lst:
            # check lst only check for unique constraints. No duplicate constraints in check lst.
            check_lst.remove(constraints)
        for variable in constraints.get_unasgn_vars():
            for value in variable.cur_domain():
                if not constraints.has_support(variable, value):
                    variable.prune_value(value)
                    prund_lst.append((variable, value))

                    # DWO occurred
                    if len(variable.cur_domain()) == 0:
                        return False, prund_lst
                    # deep first search, keep finding other constraints with current variable.
                    new_constraints = csp.get_cons_with_var(variable)
                    for item in new_constraints:
                        # avoid duplicates
                        if item not in check_lst:
                            # update check lst and Queue.
                            check_lst.append(item)
                            GACQueue.put(item)
    # print("okay", prund_lst)
    return True, prund_lst


def make_Queue_and_check_list(cons: list):
    """ Make a list copy of all constraints. Also, put all constraints into the Queue.
    And Return the copy list for further checking and updating"""
    check_lst = []
    for item in cons:
        check_lst.append(item)
        GACQueue.put(item)
    return check_lst


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    all_variables = csp.get_all_vars()
    dict = {}
    for variable in all_variables:
        if not variable.is_assigned():
            count = len(variable.cur_domain())
            dict[variable] = count
    for key in dict.keys():
        if dict[key] == min(dict.values()):
            # print(key)
            return key

    return None
