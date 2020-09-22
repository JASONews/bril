import sys
import json

def lvn(body):
    
    updated = True

    while updated:

        table = [] # | table id(index) | ->  | value tuple | variable |
        val2id = {} # | value tuple | -> | table id | indexing for quick access
        variables = {} # | variable | -> | table id | 
        last_def = {}


        updated = False

        for ln, instr in enumerate(body): # record last definition of a variable
            if 'dest' in instr:
                dest = instr['dest']
                last_def[dest] = ln

        for ln, instr in enumerate(body):
            
            if 'dest' in instr: # potential new variable
                dest = instr['dest']

                if instr['op'] == 'const':
                    val_tuple = instr['op'], instr['value']
                elif instr['op'] == 'id':
                    val_tuple = table[variables[instr['args'][0]]][0]
                else:
                    val_tuple = instr['op'], *sorted(["#{}".format(variables[arg]) for arg in instr['args']])

                if val_tuple not in val2id: # new value
                    tuple_dest = dest

                    if last_def[dest] < ln:
                        tuple_dest = "@__{}_{}".format(dest, len(table))
                        instr['dest'] = tuple_dest
                        updated = True

                    val2id[val_tuple] = len(table)
                    table.append((val_tuple, tuple_dest))
                    variables[tuple_dest] = val2id[val_tuple]
                    variables[dest] = val2id[val_tuple]

                else: # old value
                    variables[dest] = val2id[val_tuple]

                    if 'args' in instr:
                        args = instr['args']
                    else:
                        del instr['value']
                        args = []

                    if instr['op'] != 'id':
                        instr['op'] = 'id'
                        updated = True

                    if len(args) != 1 or args[0] != table[val2id[val_tuple]][1]:
                        instr['args'] = [table[val2id[val_tuple]][1]]
                        updated = True
                    
                    continue

            # update arguments if needed.
            if 'args' in instr:
                args = []

                for arg in instr['args']:

                    if arg in variables and arg != table[variables[arg]][1]:
                        arg = table[variables[arg]][1]
                        updated = True

                    args.append(arg)
                
                instr['args'] = args
            
    return body

def main(in_fd, out_fd):

    program = json.load(in_fd)

    for function in program['functions']:
        function['instrs'] = lvn(function['instrs'])

    json.dump(program, out_fd)


if __name__ == "__main__":
    main(sys.stdin, sys.stdout)
    