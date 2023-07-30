---
date: 2022-03-12
layout: post
title: Quantum programming baby steps
summary: Quantum programming languages expose low-level detail; Opportunities abound for abstractions
tags:
 - qc
---

After getting the basics of QC down with
[quantum.country](https://quantum.country/), I find thinking about and surveying
quantum programming languages a lot of fun.

Below, I have my textbook implementation of Grover search in Cirq ([runnable
Colab](https://colab.research.google.com/drive/1pg6MhRkOze27EDY6TiIfJVa0JHOUmZ1T?usp=sharing)).
Cirq docs have [many other textbook algorithm implementations
here](https://quantumai.google/cirq/tutorials/educators/textbook_algorithms).

Some raw thoughts:

1. One has to think in terms of individual single-qubit and multi-qubit logic
gates, which is very error-prone and tedious, especially when uncomputation is
needed. This is in contrast with classical programming, where thinking in terms
of elementary NAND gates is too low level.
2. Depending on your quantum hardware, some circuits might need redesigning,
since they may not be suited to the underlying device's constraints. Cirq
exposes these via [devices](https://quantumai.google/cirq/devices). While it is
easy to grab a `NamedQubit` in simulation mode as needed. In real code,
compilers will need to help programmers translate higher level ideas to circuits
that can actually run on the target machine.
3. Testing and debugging quantum programs will be interesting. Black-box testing
of classical results can probably be done by running tests on simulators.
Interactively debugging programs will be challenging as we now have a legitimate
case for Heisenbugs!  Interesting papers: [1](https://arxiv.org/abs/1812.09261),
[2](https://blog.sigplan.org/2020/12/21/how-to-test-a-quantum-program/).
4. Imagine a computer game that introduces quantum effects. Most of the game
will be a classical program, which will call out to a quantum subsystem to
efficiently do the quantum stuff. Would a single language for both classical and
quantum components make sense? I think at least in the near future, a separate
quantum service will be the norm in large part due to quantum hardware being
only available with a few providers.

I will next look at a few quantum programming frameworks, e.g.,

* [Quipper: An embedded, scalable functional programming language for quantum computing](https://hackage.haskell.org/package/quipper-0.8.1)
* [Silq: High-level programming language for quantum computing with a strong static type system](https://silq.ethz.ch/): This one sounds particularly promising re. points (1) and (2) above.
* [Qiskit](https://qiskit.org/): IBM Quantum Lab's framework
* [Q#](https://azure.microsoft.com/en-us/resources/development-kit/quantum-computing/#overview): A high-level programming language from Microsoft.
* ...

`__END__`

## Grover search impl

In the code below, our "solution" is known in advance. To solve a real search
problem, we would need additional logic to check whether a quantum state
corresponds to the sought-after solution. Since our solution is known at
circuit-build time, we just use some controlled-nottery for the
solution-checking step.

BTW, cirq comes with a bunch of algorithm implementations, including Grover search

```python
from cirq import NamedQubit, TOFFOLI, X, CNOT, H
import math

nqubits = 4
state_space_size = 2 ** nqubits
num_grover_iterations = round(math.pi / (4. * math.asin(1. / math.sqrt(state_space_size))) - 0.5)

print(f'State space size=#{state_space_size}, num iters=#{num_grover_iterations}')


x1 = NamedQubit('x1')
x2 = NamedQubit('x2')
x3 = NamedQubit('x3')
x4 = NamedQubit('x4')

w1 = NamedQubit('w1')
w2 = NamedQubit('w2')
w3 = NamedQubit('w3')
w4 = NamedQubit('w4')
w5 = NamedQubit('w5')

# I am not sure if reusing ancilla across iterations is ok, so creating
# one per iteration.
ancilla = [cirq.NamedQubit(f'a#{i}') for i in range(num_grover_iterations)]

def make_ancilla():
  """Returns a sequence of operations that prepare each ancilla bit in the
  |-⟩ = H|1⟩ state."""
  prepare_ancilla = []
  for q in ancilla:
    prepare_ancilla.append(X(q))
    prepare_ancilla.append(H(q))
  return prepare_ancilla

def make_equal_superposition_state():
  return [H(x1), H(x2), H(x3), H(x4)]

def make_oracle(solution, z):
  """Returns a sequence of gates that takes |x>|z> to -|x>|z> if
  |x> == |solution>, else leaves the state alone. Note that the solution
  is known here, but in general this oracle will check if there is a solution
  in |x>."""
  assert len(solution) == 4, "I assumed a 4 qubit solution"
  gates = []
  uncompute_gates = []

  # Convenience fn to add uncomputation operations as we add the main
  # operations.
  def _add(gate, *operands):
    gates.append(gate(*operands))
    uncompute_gates.append(cirq.inverse(gate(*operands)))

  input_qubits = [x1, x2, x3, x4]
  for i, x in enumerate(solution):
    assert x in (1, 0), "Expected a binary solution vector"
    if x == 0:
      _add(X, input_qubits[i])
  
  _add(TOFFOLI, x1, x2, w1)
  _add(TOFFOLI, w1, x3, w2)
  _add(TOFFOLI, w2, x4, w3)

  # Copy the output to the ancilla qubit since uncomputation will reset w3
  # to its input state.
  gates.append(CNOT(w3, z))

  uncompute_gates.reverse()
  gates.extend(uncompute_gates)
  return gates
  

def make_search_step(z):
  """Returns a sequence of ops that runs the diffusion step of Grover search
  by reflecting |x> about |E> where |E> is the equal superposition state.
  z is an ancilla qubit. |x>|z> should be first passed through an oracle step.
  """
  return [   
    H(x1), H(x2), H(x3), H(x4),
    X(x1), X(x2), X(x3), X(x4),
    TOFFOLI(x1, x2, w1),
    TOFFOLI(w1, x3, w2),
    TOFFOLI(w2, x4, w3),

    # Leave the result in the ancilla.
    CNOT(w3, z),

    # uncompute
    TOFFOLI(w2, x4, w3),
    TOFFOLI(w1, x3, w2),
    TOFFOLI(x1, x2, w1),
    X(x1), X(x2), X(x3), X(x4),
    H(x1), H(x2), H(x3), H(x4),
  ]

def make_ckt(solution):
  """Creates a circuit to search for the given solution, which should be a
  4-element binary (0/1) array."""
  circuit = cirq.Circuit()
  circuit.append(make_equal_superposition_state())
  circuit.append(make_ancilla())
  for iter in range(num_grover_iterations):
    circuit.append(make_oracle(solution, ancilla[iter]))
    circuit.append(make_search_step(ancilla[iter]))
  circuit.append([cirq.measure(q) for q in (x1, x2, x3, x4)])
  return circuit
```

Now we instantiate the algorithm to find the solution "1001" and simulate:

```python
circuit = make_ckt([1, 0, 0, 1])
print(circuit)

sim = cirq.Simulator()
result = sim.simulate(circuit, initial_state=0)
print(result)
```

Output:

```
measurements: x1=1 x2=0 x3=0 x4=1
output vector: -0.354|0000001001⟩ + 0.354|0010001001⟩ + 0.354|0100001001⟩ - 0.354|0110001001⟩ + 0.354|1000001001⟩ - 0.354|1010001001⟩ - 0.354|1100001001⟩ + 0.354|1110001001⟩
```