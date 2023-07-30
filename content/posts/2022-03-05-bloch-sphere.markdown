---
date: 2022-03-05

layout: post
title: The Bloch sphere
tags: [notes, qc]
math: true
summary: Notes on visualizing qubits with the Block sphere
---
This video is the best derivation I found:
[https://www.youtube.com/watch?v=a-dIl1Y1aTs](https://www.youtube.com/watch?v=a-dIl1Y1aTs).

`__BEGIN__` notes

A single complex number $z = a + ib$ has two degrees of freedom, the two real
numbers a and b.

A qubit, or a two-level quantum state can be represented with two complex
numbers, the amplitudes of the $\ket{\psi} = \alpha\ket{0} + \beta\ket{1}$.

But $\alpha$ and $\beta$ are not unconstrained parameters.

First, we have the normalization constraint, which means that $\lvert \alpha
\rvert^2 + \lvert \beta \rvert^2 = 1$.

So we may write $\ket{\psi}$ as:

$$\ket{\psi} = {\rm e}^{i\phi_0}\cos{\frac{\theta}{2}}\ket{0} + {\rm e}^{i\phi_1}\sin{\frac{\theta}{2}}\ket{1}$$

with $0 \le \theta \le \pi$ (since only positive real parts of the amplitude
suffice), and $0 \le \phi_0, \phi_1 \lt 2\pi$ (since $2\pi$ is the same
phase as $0$). Using $\frac{\theta}{2}$ is more convenient than $\theta$
for visualization.

Secondly, the global phase of a qubit does not matter -- only the *relative*
phase between the amplitudes is physically detectable. This means:

$$\ket{\psi} = {\rm e}^{i\phi_0}\cos{\frac{\theta}{2}}\ket{0} + {\rm e}^{i\phi_1}\sin{\frac{\theta}{2}}\ket{1} = {\rm e}^{i\phi_0}\left(\cos{\frac{\theta}{2}}\ket{0} + {\rm e}^{i\left(\phi_1-\phi_0\right)}\sin{\frac{\theta}{2}}\ket{1}\right)$$

Ridding the global phase factor of ${\rm e}^{i\phi_0}$, and writing $\phi =
\phi_1 - \phi_0$, this state is equivalent to:

$$\cos{\frac{\theta}{2}}\ket{0} + {\rm e}^{i\phi}\sin{\frac{\theta}{2}}\ket{1}$$

So now we are able to describe a two-level quantum state with only two real
numbers, $0 \le \theta \le \pi$ and $0 \le \phi \lt 2\pi$.

For $\ket{\psi} = \ket{0}$, $\theta = 0$, and for $\ket{\psi} = \ket{1}$,
$\theta = \pi$ and $\phi = 0$.

While we could scatter plot qubit states in a 2-D $\theta {\rm vs.} \phi$
chart, visualizing using spherical co-ordinates gives a richer and more useful
picture. In this spherical co-ordinate system since we have only unit vectors,
we can render qubit states as points on the unit sphere with $\ket{0}$ on the
north pole, and $\ket{1}$ on the south pole of the sphere.



