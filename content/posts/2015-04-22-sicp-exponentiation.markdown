---
layout: post
title: SICP Exercise 1.16
date: 2015-04-22
---

This exercise requires the design of a procedure that evolves an iterative
exponentiation process using successive squaring. It should use constant space
and a logarithmic number of steps. The hint is to note that <span>$\left( b^{
\frac{n}{2} } \right)^2 = \left( b^2 \right)^{ \frac {n}{2} }$</span> and to
transform states such that <span>$ab^n$</span> is invariant, and equal to
<span>$b^n$</span> where `a` is another state variable along with the base `b`
and exponent `n`. Here is the implementation:

    (define (even? x)
      (= (remainder x 2) 0))

    (define (expt b n)
      (expt-iter 1 b n))

    (define (expt-iter a b n)
      (cond ((= n 0) a)
            ((even? n) (expt-iter a (square b) (/ n 2)))
            (else (expt-iter (* a b) b (- n 1)))))


Here, `expt-iter`starts with the state variables `a = 1`, `b`, the base, and
`n`, the exponent.

We will the use the notation <span>$a_0$</span>, <span>$b_0$</span>,
<span>$n_0$</span> to denote the initial values, and <span>$a_c$</span>,
<span>$b_c$</span>, <span>$n_c$</span> to denote the <em>current</em> values,
of the state variables `a`, `b` and `n`, respectively.

When the exponent `n` falls to zero, our invariant says that <span>$a_c {b_c}
^0 = a_c$</span> must equal the final result <span>${b_0}^{n_0}$</span>. Hence
in this case, we return <span>$a_c$</span>, the current value of `a`. The
correctness of this can be readily verified for <span>$n_0 = 0$</span>. For
other values of <span>$n$</span>, we need to prove that given any call to
`expr-iter` with arguments <span>$a_c$</span>,
<span>$b_c$</span>, <span>$n_c$</span> such that the invariant is preserved,
i.e., <span>$ a_c  { b_c }^{n_c} = {b_0}^{n_0}$</span>, each arm of the `cond` in
`expt-iter` preserves the invariant through the next recursive call to itself.

For even values of <span>$n$</span>, we use the first part of the hint to
reduce the exponent by half while squaring <span>$b$</span>. Let's look at our
invariant expression in this case. Suppose we are dealing with some even
exponent <span>$n_c = 2k$</span>.  Before our transformation, the invariant
says that <span>$a_c { b_c } ^{2k} = {b_0}^{n_0}$</span>. After our
transformation, the invariant is <span>$a_c { {b_c}^2 }^k$</span>, which is
just a rearrangement of the invariant expression before the transformation, and
hence, must also equal <span>${b_0}^{n_0}$</span>.

For odd values of <span>$n$</span>, we transform by changing <span>$a$</span>
to be the product <span>$ab$</span> while reducing <span>$n$</span> by
<span>$1$</span>. For some odd value of <span>$n_c = 2k+1$</span>, the
invariant before the transformation is <span>$a_c {b_c}^{2k+1}$</span>. After
the transformation, it becomes <span>$ \left( a_c b_c \right) {b_c}^{2k}
$</span>, which is only a rearrangement of the previous term, implying that our
transformation correctly preserves the invariant.

Maintaining an invariant across state transformations is a powerful way of
designing iterative processes, and also makes it easy to reason for the
correctness of the procedures behind such processes.

