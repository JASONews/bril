SSA
---

## Input File
factLT10.bril

This function takes an argument ```arg``` and print ```arg!``` if ```arg``` < 10 else
print 1 instead. Here is the bril code:

```
(py3) ➜  ssa git:(py-bril) ✗ cat test/factLT10.bril
# ARGS: live

@main(arg: int) {
  result: int = const 1;
  i: int = id arg;
  ten: int = const 10;

.test:
  isLT10: bool = lt i ten;
  br isLT10 .header .end;

.header:
  # Enter body if i >= 0.
  zero: int = const 0;
  cond: bool = gt i zero;
  br cond .body .end;

.body:
  result: int = mul result i;

  # i--
  one: int = const 1;
  i: int = sub i one;

  jmp .header;

.end:
  print result;
}
```

Results of running the script with the brili interpreter.
```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 2
2
total_dyn_inst: 23
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 5
120
total_dyn_inst: 44
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 7
5040
total_dyn_inst: 58
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 9
362880
total_dyn_inst: 72
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 10
1
total_dyn_inst: 6
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | brili -p 12
1
total_dyn_inst: 6
```

## In SSA
Here is the in SSA output(with phi instructions) for factLT10.bril:

```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | bril2txt
@main(arg: int) {
.block_0:
  result.1: int = const 1;
  i.1: int = id arg;
  ten.1: int = const 10;
.test:
  isLT10.1: bool = lt i.1 ten.1;
  br isLT10.1 .header .end;
.header:
  one.1: int = phi one.2 .body;
  i.2: int = phi i.1 i.3 .test .body;
  result.2: int = phi result.1 result.3 .test .body;
  zero.1: int = const 0;
  cond.1: bool = gt i.2 zero.1;
  br cond.1 .body .end;
.body:
  result.3: int = mul result.2 i.2;
  one.2: int = const 1;
  i.3: int = sub i.2 one.2;
  jmp .header;
.end:
  one.3: int = phi one.1 .header;
  cond.2: bool = phi cond.1 .header;
  zero.2: int = phi zero.1 .header;
  i.4: int = phi i.1 i.2 .test .header;
  result.4: int = phi result.1 result.2 .test .header;
  print result.4;
}
```

Tested as in SSA form.
```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | python ../../examples/is_ssa.py
yes
```

Here is the result of running above instructions with brili interpreter:
```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 2
2
total_dyn_inst: 37
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 5
120
total_dyn_inst: 67
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 7
5040
total_dyn_inst: 87
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 9
362880
total_dyn_inst: 107
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 10
1
total_dyn_inst: 11
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py phi | brili -p 12
1
total_dyn_inst: 11
```


## Out SSA

Here is the out SSA output(without phi instructions) for factLT10.bril:

```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | bril2txt
@main(arg: int) {
.block_0:
  result.1: int = const 1;
  i.1: int = id arg;
  ten.1: int = const 10;
.test:
  isLT10.1: bool = lt i.1 ten.1;
  br isLT10.1 .test.header .test.end;
.test.header:
  i.2 = id i.1;
  result.2 = id result.1;
  jmp .header;
.test.end:
  i.4 = id i.1;
  result.4 = id result.1;
  jmp .end;
.header:
  zero.1: int = const 0;
  cond.1: bool = gt i.2 zero.1;
  br cond.1 .body .header.end;
.header.end:
  one.3 = id one.1;
  cond.2 = id cond.1;
  zero.2 = id zero.1;
  i.4 = id i.2;
  result.4 = id result.2;
  jmp .end;
.body:
  result.3: int = mul result.2 i.2;
  one.2: int = const 1;
  i.3: int = sub i.2 one.2;
  jmp .body.header;
.body.header:
  one.1 = id one.2;
  i.2 = id i.3;
  result.2 = id result.3;
  jmp .header;
.end:
  print result.4;
}
```

Here is the result of running above instructions with brili interpreter:
```
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 2
2
total_dyn_inst: 40
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 5
120
total_dyn_inst: 73
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 7
5040
total_dyn_inst: 95
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 9
362880
total_dyn_inst: 117
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 10
1
total_dyn_inst: 9
(py3) ➜  ssa git:(py-bril) ✗ bril2json < test/factLT10.bril | python ssa.py | brili -p 112
1
total_dyn_inst: 9
```

As shown above, ssa.py transforms normal bril code to SSA form and replaces phi nodes with
incoming blocks while gives the same results of the original code.

