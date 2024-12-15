---
title: SICP excercises 1.17 and 1.18 - Multiplication using addition, doubling and halving
layout: post
date: 2015-04-25
---

These two exercises ask us to implement a multiplication routine assuming
we can only add, double, and halve even numbers. The first implementation is
a straightforward translation of the facts that the product of two numbers
<span>$a$</span> and <span>$b$</span> is given by <span>$ab = 2 \left( a \times
\frac {b} { 2} \right) $</span> for even values of <span>$b$</span> and
<span>$ab = a(b-1) + a$</span> for odd values of <span>$b$</span>. Here is the
code:
    
    (define (fast* a b)
      (cond ((= b 1) a)
            ((even? b) (double (fast* a (halve b))))
            (else (+ a (fast* a (- b 1))))))

This assumes that the routines `double` and `halve` are available.

Note that in this algorithm, doubling <span>$b$</span> will only increase the
total number of steps (and the height of the call stack) by one. This means we
have a process that consumes <span>$\Theta \left( \lg b \right)$</span> space
and time.

Now to implement an iterative version of logarithmic time multiplication which
takes constant space. When designing an iterative process, it helps to think
about an expression involving the state variables of the process which will
evaluate to the same value, across iterative transformations, for a particular
invocation of the process. In this case, we shall use the expression $ab + c$,
with the assertion that this expression always evaluates to the
intended product. For example, if we invoke our procedure with values
<span>$a=a_0$</span> and <span>$b=b_0$</span> and another state variable
<span>$c$</span>, at any point in the iteration, say, the <span>$t^{th}$<span>
step, <span>$a_t b_t + c_t$</span> must equal <span>$a_0 b_0$</span>.
This means the only choice for <span>$c_0$</span>, the initial value of the
state variable <span>$c$</span> is <span>$c_0 = 0$</span>.

Next, the transformations will be as follows.

For even $b$,

$$
a \gets 2a \\\\
b \gets \frac {b} {2}
$$

For odd $b$,
$$
b \gets b-1 \\\\
c \gets a + c
$$

Finally, when <span>$b = 0$</span>, we return <span>$c$</span> as the
result. Here's the code:
    
    (define (iter* a b)
      (define (aux a b c)
        ;; The invariant is that a*b + c always equals the intended product.
        (cond ((= b 0) c)
              ((even? b) (aux (double a) (halve b) c))
              (else (aux a (- b 1) (+ a c)))))
      (aux a b 0))

We can see that just like the previous recursive `fast*`, `iter*` also takes
<span>$\Theta \left( \lg b \right)$</span> steps. But unlike `fast*`, `iter*`
takes <em>constant</em> or <span>$\Theta \left( 1 \right)$</span> space, to store the state
variables `a`, `b` and `c`.
