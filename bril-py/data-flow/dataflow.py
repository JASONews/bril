
import sys
import collections

import cfg as m_cfg


def merge(b_name, preds, out):
    ret = set()
    for pred in preds:
        ret = ret.union(out[pred])
    return ret


def transfer(definitions, entry, analysis_type="define"):
    if analysis_type == "define":
        return entry.union(definitions)

    elif analysis_type == "reaching":

        killed = set()
        ret = set(definitions)

        for new_define in definitions:
            dest = new_define.split("#")[0]
            killed.add(dest)

        for old_define in entry:
            dest = old_define.split("#")[0]

            if dest not in killed:
                ret.add(old_define)

        return ret 
            
    elif analysis_type == "live":
        pass
    else:
        return set();



def build_predecessors(cfg, preds):
    for pred, successors in cfg.items():
        for succ in successors:
            preds[succ].append(pred)

    return preds


def worklist_run(cfg, analysis_type="define"):
    blocks = cfg['blocks']

    defines = {}
    entry = {}
    out = {}
    worklist = []
    successors = cfg['cfg']
    predessors = {}
    define_count = {}

    for name, block in blocks.items():
        definitions = set()
        predessors[name] = []

        for instr in block:

            if 'dest' in instr:
                dest = instr['dest']
                define_count[dest] = define_count.get(dest, 0) + 1

                if analysis_type == "reaching":
                    
                    if define_count[dest] > 1:
                        definitions.discard("{}#{}".format(dest, define_count[dest]-1))
                    definitions.add("{}#{}".format(dest, define_count[dest]))
                else:
                    definitions.add(dest)

        entry[name] = set()
        out[name] = definitions
        defines[name] = definitions
        worklist.append(name)

    predessors = build_predecessors(cfg['cfg'], predessors)

    worklist_forward(worklist, entry, out, defines, predessors, successors, analysis_type=analysis_type)

    print_analysis(blocks.keys(), entry, out)

    
def worklist_forward(worklist, entry, out, defines, preds, succ, analysis_type):
    while worklist:
        b_name = worklist.pop()
        entry[b_name] = merge(b_name, preds[b_name], out)
        new_out = transfer(defines[b_name], entry[b_name], analysis_type=analysis_type)
        if out[b_name] != new_out:
            worklist += list(succ[b_name])
            out[b_name] = new_out

def print_analysis(names, entry, out):
    for name in names:
        print("\t", name)
        print("\t\tin", entry[name])
        print("\t\tout", out[name])
        print()


def main(fd):
    cfgs = m_cfg.make_cfg(fd)

    for function_name in cfgs:
        print("Function", function_name, "\n")
        worklist_run(cfgs[function_name], analysis_type="define" if len(sys.argv) < 2 else sys.argv[1])



if __name__ == "__main__":
    print(sys.argv)
    main(sys.stdin)
    
