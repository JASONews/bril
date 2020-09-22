import sys
import json

def tdce(body):
    body_updated = True

    last_def = {}

    while body_updated: # going until no updates made

        body_updated = False

        removed = []
        last_def = {}

        for ln, instr in enumerate(body):

            if 'args' in instr: # check use first 
                for arg in instr['args']:
                    if arg in last_def:
                        del last_def[arg]

            if 'dest' in instr:
                dest = instr['dest']

                if dest in last_def: # check definition 
                    removed.append(last_def[dest]) # remove last unused def

                last_def[dest] = ln

        removed += list(last_def.values())

        body_updated = not not removed 
            
        for ln in sorted(removed)[::-1]: # remove instrs from end to the front.
            body.pop(ln)
        
    return body

def main(fd):

    program = json.load(fd)

    for function in program['functions']:
        function["instrs"] = tdce(function['instrs'])
    
    json.dump(program, sys.stdout)

if __name__ == "__main__":
    main(sys.stdin)
