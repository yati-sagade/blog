---
title: SICP excercises 1.19 - Logarithmic time Fibonacci number generation
layout: post
date: 2015-04-25

---

This exercise describes a transformation <span>$T_{pq}$</span>, that, when
applied to a pair <span>$\left( a, b \right)$</span>, transforms it according
to <span>$a \gets aq + bq + ap$</span> and <span>$b \gets bp + aq$</span>. The
transformation used to generate Fibonacci numbers, starting from the pair
<span>$\left( 0, 1 \right)$</span>, can be written as <span>$a \gets
a + b$</span> and <span>$b \gets a$</span>.

Note that the Fibonacci transformation is <span>$T_{01}$</span>
(<span>$p=0$</span> and <span>$q=1$</span>).

The exercise asks us to show that applying any transformation
<span>$T_{pq}$</span> <em>twice</em> (or <span>$T^2_{pq}$</span>) to a pair
<span>$\left( a, b \right)$</span> is equivalent to applying the
transformation <span>$T_{p'q'}$</span> for some <span>$p'$</span> and
<span>$q'$</span>, and to find <span>$p'$</span> and <span>$q'$</span> in terms
of <span>$p$</span> and <span>$q$</span>.

Let's apply the transformation once to get

<div>$
a' = aq + bq + ap
$</div>
<div>$
b' = bp + aq
$</div>

Now apply the transformation once more.
<div>$
a'' = a'q + b'q + a'p
$</div>
<div>$
b'' = b'p + a'q
$</div>

Substitute for <span>$a'$</span> and <span>$b'$</span> and rearrange
<div>$
a'' = \left( aq + bq + ap \right) q + \left( bp + aq \right) q + \left( aq + bq + ap \right) p
$</div>
<div>$
= ap^2 + bq^2 + 2aq^2 + 2apq + 2bpq
$</div>
<div>$
= a \left( 2q^2 + p^2 + 2pq \right) + b \left( q^2 + 2pq \right)
$</div>
<div>$
= a \left( q^2 + 2pq \right) + a \left( p^2 + q^2 \right) + b \left( q^2 + 2pq \right) 
$</div>
<div>$
= a \left( q^2 + 2pq \right) + b \left( q^2 + 2pq \right) + a \left( p^2 + q^2 \right)
$</div>

<div>$
b'' = b'p + a'q
$</div>
<div>$
= \left( bp + aq \right)p + \left( aq + bq + ap \right)q
$</div>
<div>$
= bp^2 + apq + aq^2 + bq^2 + apq
$</div>
<div>$
= b\left( p^2 + q^2 \right) + a\left( q^2 + 2pq \right)
$</div>

Now comparing the final expressions for <span>$a''$</span> and
<span>$b''$</span> with the original transformations, we note that transforming
<span>$\left( a,b \right)$ by <span>$T^2_{pq}$</span> is equivalent to the
single transformation <span>$T_{p'q'}$</span>, where $p' = p^2 + q^2$ and <span>$q' = q^2 + 2pq$</span>.

