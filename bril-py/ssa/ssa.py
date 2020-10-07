import sys

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


def main(fd):

    cfgs = m_cfg.make_cfg(fd)

    for fn, cfg in cfgs.items():
        # print("function: {}", fn)
        predecessors = cfg['predecessors']
        successors = cfg['successors']

        dom = find_dominators(predecessors, successors)
        root, tree = build_dominating_tree(dom)
        find_dominance_frointer(tree['header'], successors)


if __name__ == "__main__":
    main(sys.stdin)