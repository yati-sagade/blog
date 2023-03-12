---
title: SICP Exercise 1.13
date: 2015-04-05
layout: post
math: true
---

The Fibonacci sequence is given by,

$$
Fib(n) = {
   \begin{cases}
    0 & n = 0 \\
    1 & n = 1 \\
    Fib(n - 1) + Fib(n - 2) & n \gt 1
   \end{cases}
}
$$

Exercise 1.13 in [SICP][1] asks you to prove that the <span>$n^{th}$</span> Fibonacci number
<span>$(n = 0, 1,...)$</span> is equal to the <em>closest integer</em> to
<span>$\frac{ { \phi } ^ { n } } { \sqrt 5 }$</span>, where <span>${ \phi } = { \frac { 1 + { \sqrt 5 } } { 2 } }$</span>.
The given hint is to use <span>${ \psi } = { \frac { 1 - { \sqrt 5 } } { 2 } }$</span> to
prove that <span>${Fib(n)} = { \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } }$</span>.

Some will recognize the constant <span>$\phi$</span> as the [Golden Ratio][2].
While knowing this fact allows one to use some useful properties of
<span>$\phi$</span> and <span>$\psi$</span>, I am not going to use them in my
proof.

We will first prove by induction that 
<div>
$$
{Fib(n)} = { \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } }
$$
</div>
And then use this result to prove that
<div>
$$
{Fib(n)} = nint \left( { \frac{ { \phi } ^ { n } } { \sqrt 5 } } \right)
$$
</div>
Where <span>$$ nint(x) $$</span> is the nearest integer to <span>$$
x $$</span>.


Inductive base cases
---------------------
For $n = 0$,
$$
{ \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } }
 = { \frac { {\phi}^{0} - {\psi}^{0} } { \sqrt 5 } } = { \frac { 1 - 1 } { \sqrt 5 } } = 0 = { Fib(0) }
$$

For $n = 1$,
$$
{ \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } }
 = { \frac { {\phi}^{1} - {\psi}^{1} } { \sqrt 5 } }
 = { \frac { {\phi} - {\psi} } { \sqrt 5 } }
 = { \frac { { \frac { 1 + { \sqrt 5 } } { 2 } } - { \frac { 1 - { \sqrt 5 } } { 2 } } } { \sqrt 5 } }
 = { \frac { 2 { \sqrt 5 } } { 2 { \sqrt 5 } } }
 = 1 = { Fib(1) }
$$

For $ n = 2 $,
$$
{ \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } }
 = { \frac { {\phi}^{2} - {\psi}^{2} } { \sqrt 5 } }
 = { \frac { { { \left( { \frac { 1 + { \sqrt 5 } } { 2 } } \right) } ^ { 2 } } - 
             { { \left( { \frac { 1 - { \sqrt 5 } } { 2 } } \right) } ^ { 2 } } } { \sqrt 5 } }
 = { \frac { 1 + 2\sqrt 5 + 5 - 1 + 2\sqrt 5 - 5 } { 4\sqrt 5} } 
 = { \frac { 4 { \sqrt 5 } } { 4 { \sqrt 5 } } }
 = 1 = { Fib(2) }
$$

Inductive step
----------------
Assume that the relation we seek to prove holds for <span>$ n = m $</span>
and $ n = m - 1 $ for some $ m \gt 2 $. That is,

$$
Fib(m) = { \frac { {\phi}^{m} - {\psi}^{m} } { \sqrt 5 } },
Fib(m-1) = { \frac { {\phi}^{m-1} - {\psi}^{m-1} } { \sqrt 5 } }
$$

<em>We need to prove</em> that,
$$
Fib(m+1) = { \frac { {\phi}^{m+1} - {\psi}^{m+1} } { \sqrt 5 } }
$$

Now,

$$
Fib(m+1) = Fib(m) + Fib(m-1)
$$

$$
= { { \frac { {\phi}^{m} - {\psi}^{m} } { \sqrt 5 } } + { \frac { {\phi}^{m-1} - {\psi}^{m-1} } { \sqrt 5 } } }
$$

$$
= { \frac { \left( {\phi}^{m} + {\phi}^{m-1} \right) - \left( {\psi}^{m} + {\psi}^{m-1} \right) } { \sqrt 5 } }
$$

$$
= { \frac { {\phi}^{m-1} \left( \phi + 1 \right) - {\psi}^{m-1} \left( \psi + 1 \right) } { \sqrt 5 }  \tag{1}\label{eq1} }
$$

Let's look at the term <span>$ {\phi}^{m-1} \left( \phi + 1 \right) $</span> separately.

$$
{\phi}^{m-1} \left( \phi + 1 \right) \\\\
={\phi}^{m-1} \left( { \frac {1 + \sqrt 5} {2}} + 1 \right) \\\\
={\phi}^{m-1} \left( { \frac {3 + \sqrt 5} {2} } \right)
$$

Multiplying numerator and denominator by <span>$2$</span>, we have

$$
{\phi}^{m-1} \left( { \frac {6 + 2\sqrt 5} {4} } \right)
$$

$$
={\phi}^{m-1} \left( { \frac {1 + 2\sqrt 5 + 5} {4} } \right) \\\\
={\phi}^{m-1} \left( { \frac {1 + 2\sqrt 5 + {\left( \sqrt 5 \right)} ^ {2} } {4} } \right)
$$

$$
={\phi}^{m-1} \frac { { \left( 1 + \sqrt 5 \right) } ^ {2} } { {2}^{2} }
={\phi}^{m-1} { \left( { \frac { 1 + \sqrt 5 } { 2 } } \right) } ^ {2}
$$

$$
={\phi}^{m-1} {\phi}^{2}
={\phi}^{m+1}
$$

Similarly, it can be deduced that <span>$ {\psi}^{m-1} \left( \psi + 1 \right) = {\psi}^{m+1} $</span>.

Now plugging in these values for <span>$ {\phi}^{m-1} \left( \phi + 1 \right) $</span> and <span>$ {\psi}^{m-1} \left( \psi + 1 \right) $</span>  in \ref{eq1}, we have

$$
{ \frac { {\phi}^{m-1} \left( \phi + 1 \right) - {\psi}^{m-1} \left( \psi + 1 \right) } { \sqrt 5 } }
$$

$$
={ \frac { {\phi}^{m+1} - {\psi}^{m+1} } { \sqrt 5 } }
$$

Hence, we have just proved that <span>$ Fib(m+1) = { \frac { {\phi}^{m+1} - {\psi}^{m+1} } { \sqrt 5 } } $</span>, which
completes our inductive proof of the relation <span>$ Fib(n) = { \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } } $</span>.

Final proof
------------

Now to prove that <span>$ Fib(n) = nint \left( \frac { {\phi}^{n} } { \sqrt 5 } \right) $ </span>.
Note that when we say <span>$N$</span> is the nearest integer to <span>$x$</span>,
we are implying that <span>$ \lvert N - x \rvert < \frac{1}{2} $</span>. We
have already proved that <span>$ Fib(n) = { \frac { {\phi}^{n} - {\psi}^{n} } { \sqrt 5 } } $</span>. Or,

$$
Fib(n) = \frac{ {\phi}^{n} } { \sqrt 5 } - \frac{ {\psi}^{n} } { \sqrt 5 }
$$

or, 

$$
Fib(n) - \frac{ {\phi}^{n} } { \sqrt 5 } = \frac{ {\psi}^{n} } { \sqrt 5 }
$$

Taking absolute value on both sides,

$$
\lvert { Fib(n) - \frac{ {\phi}^{n} } { \sqrt 5 } } \rvert = \lvert \frac{ {\psi}^{n} } { \sqrt 5 } \rvert
$$

As noted before, if <span>$ Fib(n) $</span> is the nearest integer to
<span>$ \frac{ {\phi}^{n} } { \sqrt 5 } $</span>, the absolute value of their
difference must be less than <span>$ \frac{1}{2} $</span>. That is,

<div>
$$
\lvert { Fib(n) - \frac{ {\phi}^{n} } { \sqrt 5 } } \rvert \lt \frac {1}{2} \implies \lvert \frac{ {\psi}^{n} } { \sqrt 5 } \rvert \lt \frac {1}{2}
$$
</div>

So, to prove that <span>$ Fib(n) = nint \left( \frac { {\phi}^{n} } { \sqrt 5 } \right) $</span>, it suffices to prove that
<span>$ \lvert \frac { {\psi}^{n} } { \sqrt 5 } \rvert \lt \frac {1}{2} $</span>.

Let's print out the first 10 values of <span>$$ \lvert \frac { {\psi}^{n} } {\sqrt 5} \rvert $$</span> for
<span>$ n = (0,1...9) $</span>.


    > (map (lambda (n)
             (abs (/ (^ psi n)
                     (sqrt 5))))
           '(0 1 2 3 4 5 6 7 8 9))

    ;(.4472135954999579 .27639320225002106 .17082039324993692 .10557280900008414
      .06524758424985282 4.0325224750231356e-2 2.4922359499621467e-2 1.5402865250609892e-2
      .00951949424901158 5.883371001598312e-3)


Clearly, these are all less than <span>$ 0.5 $</span>. But we can prove this
fact using induction.

For <span>$ n = 0 $</span>, 

<div>
$$
\lvert \frac { {\psi}^{n} } { \sqrt 5 } \rvert 
= \lvert \frac { {\psi}^{0} } { \sqrt 5 } \rvert
= \frac {1}{\sqrt 5}  = \frac {1}{ {2}^{+} } \lt \frac {1}{2} 
$$
</div>

Here, we used that fact that <span>$\sqrt 5 \gt \sqrt 4$</span>. We do not need
the exact value of <span>$\sqrt 5$</span>. We just need to know that it is
greater than 2, but not 3, which we write as <span>$ {2}^{+} $</span>. This means that the
fraction <span>$ \frac {1}{\sqrt 5} $</span> has a denominator of more than
<span>$2$</span>, making the fraction itself less than <span>$\frac {1}{2}$</span>.

For <span>$ n = 1 $</span>,

<div>
$$
\lvert \frac { {\psi}^{n} } { \sqrt 5 } \rvert 
= \lvert \frac {\psi} { \sqrt 5 } \rvert
= \lvert \frac { \frac {1 - \sqrt 5} {2} } { \sqrt 5 } \rvert
= \frac {\sqrt 5 - 1} { 2 \sqrt 5 }
= \frac {\sqrt 5 } { 2 \sqrt 5 } - \frac {1} { 2 \sqrt 5}
= \left( \frac {1}{2} - \frac {1} { 2 \sqrt 5} \right) < \frac {1}{2} (\because \frac {1} {2 \sqrt 5} \gt 0)
$$
</div>

Now let us assume that for some <span>$n = m$</span>, <span>$\lvert \frac { {\psi}^{m} } { \sqrt 5 } \rvert \lt \frac {1}{2}$</span>.
Using this, we need to prove that <span>$\lvert \frac { {\psi}^{m+1} } { \sqrt 5 } \rvert \lt \frac {1}{2}$</span>.

<div>
$$
\lvert \frac { {\psi}^{m+1} } { \sqrt 5 } \rvert
=\lvert \frac { \psi {\psi}^{m} } { \sqrt 5 } \rvert
=\lvert \psi \rvert \lvert \frac { {\psi}^{m} } { \sqrt 5 } \rvert
$$
</div>

We know that <span>$ \lvert \frac { {\psi}^{m} } { \sqrt 5 } \rvert \lt \frac {1}{2} $</span>, which was
our assumption in the inductive step. But <span>$ \lvert \psi \rvert \approx  \lvert -.6180339887498949 \rvert = .6180339887498949 \lt 1$</span>. A number less than half times a number less than <span>$1$</span> <em>has</em> to result in a number less than half. That is, 
<span>${\frac {1}{2}}^{-} \times {1}^{-} = {\frac {1}{2}}^{-}$</span>. Which
means, 
<div>$$
\lvert \psi \rvert \lvert \frac { {\psi}^{m} } { \sqrt 5 } \rvert \lt \frac {1}{2} \because \lvert \psi \rvert \lt 1, \lvert \frac { {\psi}^{m} } { \sqrt 5 } \rvert \lt \frac {1}{2}
$$</div>.

This completes our proof of the relation <span>$ \lvert \frac { {\psi}^{n} } { \sqrt 5 } \rvert \lt \frac {1}{2} \forall n \ge 0 $</span>. Which immediately leads to the final proof that,
<div>$$
Fib(n) = nint(\frac { {\phi}^{n} }{\sqrt 5}), \forall n \ge 0 \blacksquare
$$</div>











[1]: https://mitpress.mit.edu/sicp/
[2]: http://en.wikipedia.org/wiki/Golden_ratio
