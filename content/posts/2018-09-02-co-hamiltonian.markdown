---
date: 2018-09-02
layout: post
title: Why I believe P ≠ NP
math: true
---

## The HAMCYCLE problem

If a graph $G\left(V, E\right)$ contains a [Hamiltonian cycle][1], we can pick
a subset $E' ⊆ E$ of edges in the graph such that:

1. All vertices in $G$ appear in the resulting subgraph and,
2. Starting at any vertex, we are able to visit each vertex exactly once, except
for the starting vertex, which is also the last vertex in the cycle.

The Hamiltonian cycle problem asks if a graph $G$ contains a Hamiltonian cycle
-- i.e., a cycle on which each vertex appears exactly once, except for the first
(and the last) vertex of the cycle.

The problem is [NP-Complete][2]. It is in [NP][3] because while no polynomial
time algorithm is known to solve it, given a graph and a "certificate" which
consists of a set of vertices claimed to constitute a Hamiltonian cycle, one can
decide in polynomial time if the certificate is bogus. Additionally, _any_
problem in NP can be reduced in polynomial time to an instance of the
Hamiltonian cycle problem, hence making it NP-Complete. [Here is such an
example reduction][4], which works on the related Hamiltonian Path problem,
which in turn can be reduced in polynomial time to the Hamiltonian Cycle
problem.

## The formal language described by HAMCYCLE

This problem describes a language $$L = \{<G>: \text{G is Hamiltonian}\}$$ which
is in NP. Here, the notation $$<G>$$ represents a suitable binary encoding of the
graph G (i.e., a string over $$\{0, 1\}^*$$).

## Co-HAMCYCLE

Consider the complement of problem: Finding if a graph is _not_ Hamiltonian.
This problem is at least as hard as the original problem, since if there was
a polynomial time algorithm to tell us whether a given graph G is
non-Hamiltonian, we could just use this to solve the original problem of
deciding whether G is Hamiltonian.

This complement is in the co-NP class by definition, and it is an open problem
whether co-NP = NP. Since P ⊆ NP, and P is closed under the complement,
P ⊆ NP ∩ co-NP. And if P = NP, co-NP = NP (but the inverse does not hold), but
if co-NP ≠ NP, then P ≠ NP.

<img src="/pconp-1.png"  />

The figure above shows that if NP and co-NP are different, P has to be different
than NP, since it must be a subset of both NP and co-NP.

## What if co-NP = NP?

Again, proving that co-NP = NP does not show that P = NP (although it does
address an important standing problem in its own right, and leaves the
possibility open that P = NP).

To show that co-NP = NP, we'd have to show that all problems in co-NP are
verifiable in polynomial time. Let's see what that means in the context of the
co-HAMCYLE problem.

To provide a certificate for the co-HAMCYCLE problem would require encoding the
_impossibility_ of the set of edges in G to be form a Hamiltonian graph.  In
other words, the certificate would have to provide a badge for a claim that the
graph G is not Hamiltonian. An example certificate would be the enumeration of
all possible cycles in the graph. The verification algorithm would then have to
check each cycle for being non-Hamiltonian, and also check that the set of
cycles in the certificate is exhaustive (because there might be a Hamiltonian
cycle that the certificate simply does not contain).

However, for this certificate to be verified in polynomial time, its length must
be polynomial in the size of the graph, and the check for exhaustiveness of the
certificate also needs to be carried out in polynomial time. I think this is
pretty hard, if not impossible to do. I don't know how to prove this of course,
but if we prove that there can exist no certificate of length polynomial in the
size of the input graph, we'd have proven that co-HAMCYCLE is _not_ in NP, i.e.,
NP ≠ co-NP, and by extension, since P must be contained in NP ∩ co-NP, P ≠ NP.


[1]: http://mathworld.wolfram.com/HamiltonianCycle.html
[2]: https://en.wikipedia.org/wiki/NP-completeness
[3]: https://en.wikipedia.org/wiki/NP_(complexity)
[4]: https://www.geeksforgeeks.org/proof-hamiltonian-path-np-complete/
