---
title: Analysis of gossip based dissemination
layout: post
categories: programming distributed-systems
date: 2017-09-10
---

Gossip based protocols are widely used in distributed systems for robust
dissemination of information. The problem: spreading a message among a set of
processes. For example, in the Bitcoin P2P network, whenever a new transaction
happens, it needs to be broadcast to all peers in order for it to end up on the
blockchain. Typically, such information originates at one of the nodes in the
network, and needs to be communicated to the rest of the peers.

One elegant solution to this problem mimics how rumours spread in the society by
word of mouth, namely "gossip" based protocols. The gossip component of every
non-faulty process in the network maintains two main pieces of state: a list of
other known live peers, and a buffer of recent messages. Then every `T` seconds,
(called the _gossip period_), every node executes the following:

1. Pick `f` peers from the membership list at random. Here, `f` is called the
gossip fanout.
2. Send recent messages from our messages buffer to each of these peers.

Of course, in parallel, each node must listen for messages and update its
message buffer.

The details like the value of the gossip fanout, and what exact messages to
relay, and for how many rounds, etc. are what make different gossip protocols
different, but we aren't going to talk much about it here.

## Analysis

The analysis focuses on finding upper bounds for:

- The number of rounds needed to get an update to all participants.
- The load on each participating peer.

To begin with, we note that the inherent random nature of the algorithm means
that we can only comment about the _expected_ behaviour of the protocol ---
i.e., we are after the number of rounds that a cluster of `N` nodes needs to
have a message disseminated across the cluster _with high probability_.

### Dissemination time

This refers to the number of gossip rounds before we can be reasonably sure
about a message having been disseminated across the cluster.

This analysis is borrowed (indirectly) from work on epidemiology --- our problem
is not so different from a situation where an infected organism comes in contact
with random uninfected individuals, thereby infecting them. These individuals
in turn go on to infect others and so on.

For our purpose, we shall say that a node in possession of a particular message
`M` is "infected", while nodes which don't know about `M` yet are uninfected.
Let's further suppose that after round `T`, `x` nodes are still uninfected, and
`y` nodes are infected. Of course, at `T=0`, `x=N-1`, and `y=1` (i.e., we have
one "infected" node that knows of the message `M` and is now out to infect
others with this knowledge). Now because each node picks `f` others at random to
gossip with, and because the proportion of uninfected nodes in the cluster is
$\frac{x}{N}$, on average any given infected node will pick $\frac{x}{N}f$
uninfected nodes. Since there are $y$ such infected nodes, on average, we'll
see $\frac{f}{N}xy$ infected-uninfected interactions in a round. Since an
uninfected node turns into an infected node after receiving the message `M`, on
average, each round results in a _decrease_ in the number of uninfected nodes
($x$) by this quantity $\frac{f}{N}xy$. Therefore,

$$
\frac{dx}{dT} = -\frac{f}{N}xy
$$

Let $ \beta = \frac{f}{N} $

Then,

$$
\begin{align*}
\frac{dx}{dT} &= -\beta xy \\\\
\implies \frac{dx}{dT} &= -\beta x\left(N-x\right) \\\\
\implies \frac{dx}{x\left(N-x\right)} &= -\beta dT \\\\
\implies \int \frac{dx}{x\left(N-x\right)} &= -\beta \int dT \tag{eqn1} \label{eqn1}
\end{align*}
$$

Let $\frac{1}{x\left(N-x\right)} = \frac{A}{x} + \frac{B}{N-x} \implies A\left(N-x\right) + Bx = 1$.

Now setting $x=0 \implies A = \frac{1}{N}$, and setting $x=N \implies
B = \frac{1}{N}$. Using this in $\eqref{eqn1}$, we have

$$
\begin{align*}
\frac{1}{N}\int \frac{dx}{x} + \frac{1}{N} \int \frac{dx}{N-x}  &= -\beta \int dT \\\\
\implies \frac{1}{N} \left( \ln{x} - \ln{\left(N-x\right)} \right) + C &= -\beta T \tag{eqn2} \label{eqn2}
\end{align*}
$$

Where $C$ is the constant of integration. To find it, we note that at $T=0,
x=N-1$. Using this in $\eqref{eqn2}$, we find that $C=-\frac{ln\left(N-1\right)}{N}$.
Substituting this value for $C$ in \eqref{eqn2} then yields:

$$
\begin{align*}
\frac{1}{N} \left( \ln{x} - \ln{\left(N-x\right)} - \ln{\left(N-1\right)} \right) &= -\beta T \\\\
\implies \ln{\frac{x}{N-x}} - \ln{\left(N-1\right)} &= -N\beta T \\\\
\implies \ln{\frac{x}{N-x}}  &= -N\beta T + \ln{\left(N-1\right)} \\\\
\implies \frac{x}{N-x} &= e^{-N\beta T + \ln{\left(N-1\right)} } = \left(N-1\right)e^{-N\beta T}  \\\\
\implies \frac{N-x}{x} &= {e^{N\beta T}\over N-1} \\\\
\implies \frac{N}{x} &= 1 + {e^{N\beta T}\over N-1} \\\\
\implies \frac{x}{N} &= {1\over {1 + {e^{N\beta T}\over N-1}}} = \frac{N-1}{N-1+e^{N\beta T}} \\\\
\end{align*}
$$

So, as $T$ (number of gossip rounds) grows, the expected value of the fraction
$x\over N$ of uninfected nodes rapidly approaches zero. Since the number of
_infected_ nodes $y=N-x$, we have the proportion of uninfected nodes

$$
\begin{align*}
{y\over N} &= 1 - {x\over N} \\\\
&= 1 - \frac{N-1}{N-1+e^{N\beta T}} \\\\
&= \frac{e^{N\beta T}}{N-1+e^{N\beta T}}
\end{align*}
$$

As we grow $T\to\infty$,

$$
\begin{align*}
\lim_{T\to\infty}\frac{e^{N\beta T}}{N-1+e^{N\beta T}} &= \\\\
&= \lim_{T\to\infty}\frac{1}{\frac{N-1}{e^{N\beta T}}+1} \\\\
&= \frac{1}{\lim_{T\to\infty}\frac{N-1}{e^{N\beta T}}+1} \\\\
&= \frac{1}{0+1} \\\\
&= 1
\end{align*}
$$

Hence the expected proportion of infected nodes reaches 100% as the protocol
keeps running. But this begs the question, how long in practice do we have to
wait before the whole cluster gets the new message with high probability? Let's
call $T_{1\over2}$ the number of rounds when _half_ of the cluster gets the
update, i.e., at $T=T_{h}$, $\frac{x}{N}=\frac{y}{N}=\frac{1}{2}$.
Therefore, from the expression for $\frac{x}{N}$ above,

$$
\begin{align*}
\frac{1}{2} &= \frac{N-1}{N-1+e^{N\beta T_{h}}} \\\\
\implies e^{N\beta T_{h}} &= N-1 \\\\
\implies N\beta T_h &= \ln\left({N-1}\right) \\\\
\implies T_h &= \frac{1}{N\beta}\ln\left({N-1}\right)
\end{align*}
$$

Now using $\beta = {f\over N}$, we get $T_h = \frac{1}{f}\ln{\left(N-1\right)}
= O\left(\ln{N}\right)$.  Hence, the half life of the process is logarithmic
in the number of participants $N$. Now, to find the number of rounds it takes
for $99\%$ of the uninfected nodes to befome infected can be computed as:

$$
\begin{align*}
\frac{N-1}{N-1+e^{N\beta T_{0.99}}} = 0.99 \\\\
\implies N\beta T_{0.99} &= \ln\left(\frac{N-1}{9}\right) \\\\
\implies  T_{0.99} &= {\ln\left(\frac{N-1}{9}\right) \over N\beta } = O\left(\ln{N}\right)\\\\
\end{align*}
$$

So we see that within a logarithmic number of rounds, a _most_ of the nodes
get infected with high probability.


### Message load per member

A dissemination mechanism is no good if it puts unreasonable load on member
nodes, and/or fails to spread out the load evenly across the cluster. In gossip
based dissemination, each node sends out $f$ messages, and receives on
expectation $f\over N$ messages _per round_. Since $\Theta\left(\ln{N}\right)$
rounds are needed for a message to get to the whole cluster, the load on each
node is also logarithmic in $N$, and every node has similar load. This is quite
nice, since one can grow the cluster to very huge sizes, and even then the load
on each node remains reasonably low.

## Conclusion

Gossip based protocols are amazingly simple and robust, which is why they form
crucial elements of failure detection and membership layers of many large scale
distributed systems. Note that I did not talk about nodes failing in this post,
and the focus was on the use of gossip for dissemination. However, gossip itself
can be used to implement failure detectors, like the [SWIM failure
detector][1](very readable paper). Here, every node periodically gossips cluster
membership updates. The protocol is augmented with several features like
acknowledgements and indirect acknowledgements allows the failure detector to
scale with tunable false positive characteristics.

[1]: https://www.cs.cornell.edu/~asdas/research/dsn02-swim.pdf


