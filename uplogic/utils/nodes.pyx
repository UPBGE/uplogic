
cpdef evaluate_cells(tree, cells, int max_blocking_loop_count):
    from uplogic.utils import STATUS_READY
    from uplogic.utils import STATUS_WAITING
    cdef list done_cells = []

    cdef int loop_index = 0
    while cells:
        if loop_index == max_blocking_loop_count:
            tree.stop()
            return
        cell = cells.popleft()
        if cell in done_cells:
            continue
        else:
            done_cells.append(cell)
        cell.evaluate()
        tree.evaluated_cells += 1
        if not cell.has_status(STATUS_READY):
            cells.append(cell)
        loop_index += 1
    done_cells = []
    for cell in tree._cells:
        cell.reset()
        if cell.has_status(STATUS_WAITING):
            cells.append(cell)
    for network in tree.sub_networks:
        if network._owner.invalid:
            tree.sub_networks.remove(network)
        elif not network.stopped:
            network.evaluate()


cpdef name_query(list named_items, str query):
    assert len(query) > 0
    cdef bint postfix = (query[0] == "*")
    cdef bint prefix = (query[-1] == "*")
    cdef bint infix = (prefix and postfix)
    cdef str token
    if infix:
        token = query[1:-1]
        for item in named_items:
            if token in item.name:
                return item
    if prefix:
        token = query[:-1]
        for item in named_items:
            if item.name.startswith(token):
                return item
    if postfix:
        token = query[1:]
        for item in named_items:
            if item.name.endswith(token):
                return item
    for item in named_items:
        if item.name == query:
            return item
    return None


def is_invalid(*a) -> bool:
    from . import STATUS_WAITING
    for ref in a:
        if ref is None or ref is STATUS_WAITING or ref == '':
            return True
        if not hasattr(ref, "invalid"):
            continue
        elif ref.invalid:
            return True
    return False


cpdef check_game_object(str query, scene=None):
    '''TODO: Documentation
    '''
    from bge import logic
    scene = scene if scene else logic.getCurrentScene()
    if (query is None) or (query == ""):
        return
    if not is_invalid(scene):
        # find from scene
        return name_query(list(scene.objects), query)


cpdef get_input(node, param, scene=None, type=None):
    from . import ULLogicBase
    from . import STATUS_READY
    from . import STATUS_WAITING

    if str(param).startswith('NLO:'):
        if str(param) == 'NLO:U_O':
            return node.network._owner
        else:
            return check_game_object(param.split(':')[-1], scene)
    if isinstance(param, ULLogicBase):
        if param.has_status(STATUS_READY):
            return param.get_value()
        else:
            return STATUS_WAITING
    else:
        return param