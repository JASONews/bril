# This scrpit takes a bril json file and output a control flow graph
# of the program.

# 1. build basic blocks.

import sys
import collections

import json

TERMINATORS = "br", "jmp", "ret"

def make_basic_block(body):
    block = []
    for instr in body:
        if "op" in instr: # an instruction
            block.append(instr)

            # check for terminators
            if instr["op"] in TERMINATORS:
                yield block
                block = []
        
        else: # a label
            if block:
                yield block
            block = [instr]

    if block: # if the last instruction is not a terminator.
        yield block


def naming_blocks(blocks):
    
    naming_map = collections.OrderedDict() # store the successor for the key

    for block in blocks:
        if "label" in block[0]:
            naming_map[block[0]["label"]] = block[1:]
        else:
            naming_map["block_%d" % len(naming_map)] = block

    return naming_map


def find_successor(name2block):
    
    out = {}

    keys = list(name2block.keys())

    for i, name in enumerate(name2block.keys()):
        
        block = name2block[name]

        last = block[-1]

        if last['op'] in ('jmp', 'br'):
            out[name] = last['labels']

        elif last['op'] == 'ret':
            out[name] = []

        else:
            out[name] = [keys[i+1]] if i < len(keys) - 1 else []

    return out

def find_predecessors(cfg, predecessors={}):

    for pred, successors in cfg.items():
        predecessors.setdefault(pred, [])
        for succ in successors:
            predecessors.setdefault(succ, [])
            predecessors[succ].append(pred)

    return predecessors

def make_cfg(fd):
    program = json.load(fd)
    cfgs = {}
    for function in program['functions']:
        named_block = naming_blocks(make_basic_block(function['instrs']))
        successors = find_successor(named_block)
        predecessors = find_predecessors(successors)

        # print(function['name'], cfg)
        cfgs[function['name']] = {}
        cfgs[function['name']]['successors'] = successors
        cfgs[function['name']]['predecessors'] = predecessors
        cfgs[function['name']]['blocks'] = named_block
        cfgs[function['name']]['args'] = function['args']

    return cfgs, program

def togGraphviz(func, cfg):
    print ("digraph {} {{".format(func))
    for key in cfg:
        print("{};".format(key))
    for key, vals in cfg.items():
        for val in vals:
            print("{} -> {};".format(key, val))
    print("}")

if __name__ == "__main__":
    make_cfg(sys.stdin)