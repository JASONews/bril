import sys
import json

import cfg as m_cfg

class DomTreeNode:

    def __init__(self, name):
        self.children = []
        self.name = name
    
    def __repr__(self):
        return "{}: {}".format(self.name, self.children)

    def childrenSet(self):
        cs = set()
        cs.add(self.name)

        for child in self.children:
            cs |= child.childrenSet()
        
        return cs


def build_dominating_tree(dominators):

    entry = None

    dom = dict(dominators)

    for name in dom:
        dom[name] = set(dom[name])
        if len(dom[name]) == 1:
            entry = DomTreeNode(name)
            
    del dom[entry.name]
    q = [entry]

    dom_tree = {}
    dom_tree[entry.name] = entry

    while dom:
        
        parent = q.pop(0)
        keys = set(dom.keys())

        for name in keys:

            dom[name].discard(parent.name)

            if len(dom[name]) == 1:
                node = DomTreeNode(name)
                parent.children.append(node)
                # add to bfs queue
                q.append(node)
                dom_tree[name] = node
                # remove it from dom to make loop converged
                del dom[name]
    
    # print("Dominance Tree: ", dom_tree)
    return entry, dom_tree


def find_dominators(predecessors, successors):

    dominators = {}

    for name in predecessors:
        dominators[name] = set(predecessors.keys())
    
    changed = True

    while changed: # loop until no changes in dominators map
        changed = False
        
        for name in dominators:
            next_dominator = set()
            
            for pred in predecessors[name]:
                next_dominator = set(dominators[pred]) if not next_dominator else next_dominator.intersection(dominators[pred])
            
            next_dominator.add(name)

            if next_dominator != dominators[name]:
                changed = True
                dominators[name] = next_dominator
    
    return dominators


def find_dominance_frointer(root: DomTreeNode, successors):
    dominated_nodes = root.childrenSet()
    frontier = set()

    # print(dominated_nodes)

    q = []
    q.append(root)

    while q:
        node = q.pop(0)
        
        for child in successors[node.name]:
            if child not in dominated_nodes:
                frontier.add(child)
        
        for child in node.children:
            q.append(child)

    # print("frontier for {}: {}".format(root.name, frontier))
    return frontier


def insert_phi_node(block, var_name, var_type):
    if not block or 'phi' not in block[0]:
        block.insert(0, {"phi": {}})
    block[0]["phi"][var_name] = {'type': var_type, 'dest': var_name, 'args': [], 'labels': []}


def flatten_phi_node(block):
    if block and 'phi' in block[0]:
        phi_nodes = block.pop(0)['phi']

        for var_name in phi_nodes:
            phi = phi_nodes[var_name]
            block.insert(0, {'op': 'phi', 'dest': phi['dest'], 'type': phi['type'],
             'args': phi['args'], 'labels': phi['labels']})


def find_variable_definitions(blocks):
    defs = {}

    for name, block in blocks.items():
        for instr in block:
            if 'dest' in instr:
                defs.setdefault(instr['dest'], {'blocks': set(), 'type': instr['type']})
                defs[instr['dest']]['blocks'].add(name)

    return defs

def to_ssa(blocks, dominators, successors, function_args):

    defs = find_variable_definitions(blocks)

    for arg in function_args:
        if arg['name'] not in defs:
            defs[arg['name']] = {'blocks': set(), 'type': arg['type']}

    entry, tree = build_dominating_tree(dominators)

    # insert phi nodes at dominance frontier
    for v, val in defs.items():

        def_blocks = val['blocks']

        _def_blocks = list(def_blocks)

        while _def_blocks:

            block_name = _def_blocks.pop()
            frontier_blocks = find_dominance_frointer(tree[block_name], successors)

            for b_name in frontier_blocks:
                insert_phi_node(blocks[b_name], v, val['type'])
                if b_name not in def_blocks:
                    def_blocks.add(b_name)
                    _def_blocks.append(b_name)


    # rename

    var_numbers = {}
    var_stacks = {}

    for var_name in defs:
        var_stacks.setdefault(var_name, [var_name])
        var_numbers.setdefault(var_name, 0)

    for arg in function_args:
        arg['name'] = var_stacks[arg['name']][-1]

    # print(var_numbers)
    # print(var_stacks)

    visited = set()

    def rename(root):

        block_name = root.name

        if block_name in visited:
            return
        else:
            visited.add(block_name)

        block = blocks[block_name]

        pushed_count = {}

        for instr in block:
            if "args" in instr:
                args = []
                old_args = instr["args"]
                while old_args:
                    args.append(var_stacks[old_args.pop()][-1])
                instr["args"] = args[::-1]
            
            if "dest" in instr:
                var_name = instr["dest"]
                var_numbers[var_name] += 1
                var_stacks[var_name].append("{}.{}".format(var_name, var_numbers[var_name]))
                instr['dest'] = var_stacks[var_name][-1]
                pushed_count[var_name] = pushed_count.get(var_name, 0) + 1

            if "phi" in instr:
                for var_name in instr['phi']:
                    var_numbers[var_name] += 1
                    var_stacks[var_name].append("{}.{}".format(var_name, var_numbers[var_name]))
                    instr['phi'][var_name]['dest'] = var_stacks[var_name][-1]
                    pushed_count[var_name] = pushed_count.get(var_name, 0) + 1
 

        for successor in successors[block_name]:
            successor_block = blocks[successor]

            if "phi" in successor_block[0]:
                for var_name in pushed_count:
                    if var_name in successor_block[0]['phi']:
                        phi = successor_block[0]['phi'][var_name]
                        phi['args'].append(var_stacks[var_name][-1])
                        phi['labels'].append(block_name)
                    
        for child in root.children:
            rename(child)

        for var_name, count in pushed_count.items():
            while count > 0:
                var_stacks[var_name].pop()
                count -= 1

        # print(var_stacks)

    rename(entry)

    for name, block in blocks.items():
        # print(name)
        flatten_phi_node(block)

def to_function(function_name, function_args, blocks):
    function = {'args': function_args, 'name': function_name, 'instrs' : []}
    for label, block in blocks.items():
        function['instrs'].append({'label': label})
        function['instrs'] += block
    return function
    

def main(fd):

    cfgs, program = m_cfg.make_cfg(fd)
    optimized_program = {"functions": []}

    for fn, cfg in cfgs.items():
        predecessors = cfg['predecessors']
        successors = cfg['successors']

        dom = find_dominators(predecessors, successors)
        to_ssa(cfg['blocks'], dom, successors, cfg['args'])

        optimized_program['functions'].append(to_function(fn, cfg['args'], cfg['blocks']))
        
    json.dump(optimized_program, sys.stdout)



if __name__ == "__main__":
    main(sys.stdin)