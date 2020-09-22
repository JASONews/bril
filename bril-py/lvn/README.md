LVN homework:
---

Here are the results that show ```lvn.py``` and ```tdce.py``` actually work. 

For the ```commute.bril``` file, we can see that ```sum1``` and ```sum2``` are
actually the same value.
```
(py3) lvn$ cat commute.bril
# ARGS: -c
# (a + b) * (b + a)
@main {
  a: int = const 4;
  b: int = const 2;
  sum1: int = add a b;
  sum2: int = add b a;
  prod: int = mul sum1 sum2;
  print prod;
}

(py3) lvn$ bril2json < commute.bril | brili -p
36
total_dyn_inst: 6
```

After processed by the lvn + tdce, ```commute.bril``` has only 5 LOC instead of
6 and `sum1` replaces all `sum2` in the code. The number of dynamic instruction
also reduces from 6 to 5. 

```
(py3) lvn$ bril2json < test/lvn/commute.bril | python lvn.py | python tdce.py | bril2txt
@main {
  a: int = const 4;
  b: int = const 2;
  sum1: int = add a b;
  prod: int = mul sum1 sum1;
  print prod;
}

(py3) lvn$ bril2json < test/lvn/commute.bril | python lvn.py | python tdce.py | brili -p
36
total_dyn_inst: 5
```

```clobber.bril``` file reassigns ```sum1``` and ```sum2```.
```
(py3) lvn$ cat clobber.bril
# CMD: bril2json < {filename} | python3 ../../lvn.py | python3 ../../tdce.py tdce | bril2txt
#
@main {
  a: int = const 4;
  b: int = const 2;

  # (a + b) * (a + b)
  sum1: int = add a b;
  sum2: int = add a b;
  prod1: int = mul sum1 sum2;

  # Clobber both sums.
  sum1: int = const 0;
  sum2: int = const 0;

  # Use the sums again.
  sum3: int = add a b;
  prod2: int = mul sum3 sum3;

  print prod2;
}

(py3) lvn$ bril2json < clobber.bril | brili -p
36
total_dyn_inst: 10
```

Here is the result after LVN and TDCE.
```
(py3) lvn$ bril2json < test/lvn/clobber.bril | python lvn.py | python tdce.py | bril2txt
@main {
  a: int = const 4;
  b: int = const 2;
  sum1: int = add a b;
  prod1: int = mul sum1 sum1;
  print prod1;
}

(py3) lvn$ bril2json < test/lvn/clobber.bril | python lvn.py | python tdce.py | brili -p
36
total_dyn_inst: 5
```

```idchain-prop.bril```
```
(py3) lvn$ cat idchain-prop.bril
# ARGS: -p
@main {
  x: int = const 4;
  copy1: int = id x;
  copy2: int = id copy1;
  copy3: int = id copy2;
  print copy3;
}

(py3) lvn$ bril2json < idchain-prop.bril | brili -p
4
total_dyn_inst: 5
```
```
(py3) lvn$ bril2json < test/lvn/idchain-prop.bril | python lvn.py | python tdce.py | bril2txt
@main {
  x: int = const 4;
  print x;
}

(py3) lvn$ bril2json < test/lvn/idchain-prop.bril | python lvn.py | python tdce.py | brili -p
4
total_dyn_inst: 2
```