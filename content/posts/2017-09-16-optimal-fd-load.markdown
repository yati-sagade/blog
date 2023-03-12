---
layout: post
title: Optimal failure detector performance
tags: ["distributed-systems"]
date: 2017-09-16
math: true
---

This is a note to self on computing the lower bound on number of messages each
process in a distributed failure detector must send to guarantee adherence to
pre-specified values for:

- Time to first detection of a true failure.
- False positive detection rate.
- Message loss rate.

In other words, the failure detector accepts as parameters the above three
values, and for those guarantees to be respected, each node in the failure
detector cluster must send at least $m$ number of messages, which is what we are
after.

The original paper from which I learnt most of this is [On Scalable and
Efficient Distributed Failure Detectors][2].

We shall talk about eventually complete (_every_ failure is eventually detected)
failure detection, in a crash-stop failure model (actually it isn't hard to
extend the analysis to a crash-recovery model, but we don't assume Byzantine
failures).


## Parameters

### 1. Time to first detection of a true failure

The failure detector in question accepts a parameter $T$, which is the maximum
time in seconds between a process failing, and _some_ other process detecting
this. Note that this explicitly does _not_ assume any dissemination mechanism,
and depending on what it is, _first_ detection may or may not mean detection by
all non-faulty processes.

### 2. False positive detection rate

The next parameter the failure detector accepts is $\alpha_{T}$, the acceptable
false failure detection rate till the first true failure detection. This is
a bit tricky to understand. Consider at time $t_0$, we have a bunch of
non-faulty processes $p_1, p_2, p_3.., p_M$ that have not been marked failed
yet. We want the probability that any _non faulty_ process marks any of $p_i$ as
failed till $t_0 + T$ to be capped at $\alpha_{T}$. To look at this from another
perspective, consider 1000 random time periods, each of length $T$. For each
time period, we count the number of false failure detections, and sum them up
(good nodes marked as faulty by another good node). We want this number to be no
more than $1000\alpha_T$.

### 3. Message loss rate

The application also specifies the probability of any given message being lost.
This is applied independently to each message, and hence may not be a true
picture of what happens in the real world (correlated message losses around
congested network zones), but hey at least [we are not talking about a spherical
cow in vaccum][1]. We call this parameter $p_{ml}$.


## Result

With the parameters specified as above, in an $N$ node distributed failure
detector, the _minimum_ number of messages each node has to send per second is
given by

$$
    m_{min} = \frac{1}{T} \frac{\log\alpha_T}{\log{p_{ml}}}
$$

This is neat, because it does not depend on the cluster size $N$!

## Proof

Suppose each node sends $m$ messages out (as heartbeats or pings to other nodes)
in a time period $T$. The only way a non-faulty process can appear as faulty to
all others is if _all_ its outgoing messages are dropped in the time-period of
$T$ seconds. This happens with probability $\left(p_{ml}\right)^m$. We want this
probability to be capped at $\alpha_T$. So,

$$
\alpha_T \ge \left(p_{ml}\right)^m
$$

$$
\implies \log{\alpha_T} \ge m\log{p_{ml}}
$$

$$
\implies m  \ge \frac{\log\alpha_T}{\log{p_{ml}}}
\left(\because 0 \lt p_{ml}
\lt 1, 0 \lt \alpha_T \lt 1 \right)
$$

Since $m$ is the number of messages sent _every T seconds_, the number of
messages per second $m_r \ge \frac{1}{T} \frac{\log\alpha_T}{\log{p_{ml}}}$, and
hence, $m_{min} = \frac{1}{T} \frac{\log\alpha_T}{\log{p_{ml}}}$.


[1]: http://abstrusegoose.com/406
[2]: http://www.cs.cornell.edu/projects/quicksilver/public_pdfs/On%20Scalable.pdf
