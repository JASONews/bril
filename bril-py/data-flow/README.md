Data Flow Analysis

Reaching definition analysis 

```
(py3) ➜  data-flow git:(py-bril) ✗ bril2json < test/fact.bril | python dataflow.py reaching
Function main 

	 block_0
		in set()
		out {'i#1', 'result#1'}

	 header
		in {'i#2', 'zero#1', 'i#1', 'cond#1', 'one#1', 'result#2', 'result#1'}
		out {'i#1', 'i#2', 'zero#1', 'cond#1', 'one#1', 'result#2', 'result#1'}

	 body
		in {'i#2', 'zero#1', 'i#1', 'cond#1', 'one#1', 'result#2', 'result#1'}
		out {'i#2', 'zero#1', 'cond#1', 'one#1', 'result#2'}

	 end
		in {'i#2', 'zero#1', 'i#1', 'cond#1', 'one#1', 'result#2', 'result#1'}
		out {'i#1', 'i#2', 'zero#1', 'cond#1', 'one#1', 'result#2', 'result#1'}
```


Definition analysis

```
(py3) ➜  data-flow git:(py-bril) ✗ bril2json < test/fact.bril | python dataflow.py define  
Function main 

	 block_0
		in set()
		out {'i', 'result'}

	 header
		in {'i', 'result', 'zero', 'cond', 'one'}
		out {'i', 'result', 'zero', 'cond', 'one'}

	 body
		in {'i', 'result', 'zero', 'cond', 'one'}
		out {'i', 'result', 'zero', 'cond', 'one'}

	 end
		in {'i', 'result', 'zero', 'cond', 'one'}
		out {'i', 'result', 'zero', 'cond', 'one'}
```