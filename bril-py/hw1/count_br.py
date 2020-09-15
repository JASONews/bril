import json
import sys


def count_br(prog):
    counter = 0
    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr and instr['op'] == 'br':
                counter+=1
    return counter

def load_bril(fn):
    with open(fn) as f:
        prog = json.load(f);
        br_count = count_br(prog)
        print("This bril %s program contains %d br(anch) operations." % (fn, br_count))

if __name__ == "__main__":
    if len(sys.argv) == 2:
        load_bril(sys.argv[1])
    else:
        print("ERR: usage:\n \t\t %s filename" % sys.argv[0])