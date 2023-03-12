---
title: Why IF has to be a special form in Lisp
layout: post
date: 2013-12-01
---


In both Scheme and Common Lisp, the `IF` conditional is a special form
with a simple evaluation rule:

- Evaluate the predicate.
- If the predicate evaluates to a true value, evaluate and the second
  argument(the then-clause) and return the result.
- If the predicate evaluates to false, evaluate the third argument, if
  any, and return the result of evaluation.

If one tries to model ``IF`` as a procedure in terms of the more general
``COND`` conditional, one might end up with something like this:

    (define (my-if predicate then-clause else-clause)
      (cond (predicate then-clause)
            (else else-clause)))

This even works fine for simple cases:

    (my-if (= 2 3) 0 5)
    ;; 5
    (my-if (= 1 1) 0 5)
    ;; 0

But there is a very big problem with ``MY-IF``. Consider the recursive
definition of the nth number in the Fibonacci sequence.

    (define (fib n)
      (if (or (= n 0)
              (= n 1))
          1
          (+ (fib (- n 1))
             (fib (- n 2)))))
    
    (fib 1)
    ;; 1
    (fib 3)
    ;; 3
    (fib 8)
    ;; 34

This definition assumes that if ``n`` is ``0`` or ``1``, the recursion
does not happen and the constant ``1`` is returned. But if we now
replace the ``IF`` with our ``MY-IF``,

    (define (fib n)
      (my-if (or (= n 0)
                 (= n 1))
             1
             (+ (fib (- n 1))
                (fib (- n 2)))))


Since ``MY-IF`` is a normal procedure, a call to ``(fib 1)`` will can
be reduced as follows using the substitution model:

    (fib 1)

    -> (my-if (or (= 1 0)
                  (= 1 1))
              1
              (+ (fib (- 1 1))
                 (fib (- 1 2))))

    -> (my-if true 1 (+ (my-if (or (= 0 0)
                                   (= 0 1))
                               1
                               (+ (fib (- 0 1))
                                  (fib (- 0 2))))
                        (my-if (or (= -1 0)
                                   (= -1 1))
                               1
                               (+ (fib (- -1 1))
                                  (fib (- -1 2))))))
    -> ...

As we see, this evaluation will never finish under the applicative
order of evaluation where all the arguments to a function will be
evaluated before ever entering the body of the function. So even if
the "predicate" of our ``MY-IF`` becomes ``true``, the third argument,
the ``else`` clause, is always evaluated and since that is recursive,
the evaluation never terminates and we might get a recursion-depth
exceeded error from the Scheme interpreter.

This is the reason why some simple special forms like ``IF`` must
exist to enable basic constructs in a language. 

Disclaimer: This is a note to myself as I solve the SICP exercises.

