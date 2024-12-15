---
title: SICP exercises 1.37-39
layout: post
date: 2017-07-08
tags: ["sicp", "lisp"]

---

In [these exercises][1], we deal with [continued fractions][2]. These are
remarkable ways of writing rational and irrational numbers as a sum of an
integer and another number, which is itself recursively written as a continued
fraction. For instance, $\sqrt{19}$ can be represented as

$$
\sqrt{19} = 4+\frac{1}{2+\frac{1}{1 + \frac{1}{3 + \frac{1}{1+\frac{1}{2+\frac{1}{8+...}}}}}}
$$

with the continued fractional part being a continued fraction of period 6.
Here's an implementation of the continued fraction computation function in
Scheme:

```scheme
(define (cont-frac n d k)
  (define (iter k result)
    (if (< k 0)
        result
        (let ((nk (n k))
              (dk (d k)))
          (iter (- k 1)
                (/ nk (+ dk result))))))
  (iter (- k 1) 0.0))
```

And here's how we compute $\sqrt{19}$:

```scheme
(define (sqrt-19 num-terms)
  (+ 4
     (cont-frac (lambda (i) 1)
                (lambda (i)
                  (let ((r (remainder i 6)))
                    (cond ((or (= r 0)
                               (= r 4)) 2)
                          ((or (= r 1)
                               (= r 3)) 1)
                          ((= r 2) 3)
                          ((= r 5) 8))))
                num-terms)))

(sqrt-19 1000)
;; 4.358898943540673
```

The base of the natural logarithm, $\exp(1)$, can be written as:

$$
\exp(1) = 2 + \frac{1}{1 + \frac{1}{2 + \frac{1}{1 + \frac{1}{1 + \frac{1}{4 + \frac{1}{1 + \frac{1}{1 + \frac{1}{6 + \frac{1}{1 + \frac{1}{1 + \frac{1}{8 + ...}}}}}}}}}}}
$$

Here's the code:

```scheme
(define (e num-terms)
  (+ 2
     (cont-frac (lambda (i) 1)
                (lambda (i)
                  (cond ((= i 0) 1)
                        ((= 0 (remainder (- i 1) 3))
                         (* 2 (+ 1 (/ (- i 1) 3))))
                        (else 1)))
                num-terms)))

(e 1000)
;; 2.7182818284590455
(exp 1)
;; 2.718281828459045

```

Lastly, the function $\tan{x}$, when $x$ is in radians, can be written as:

$$
\tan{x} = \frac{x}{1 - \frac{x^2}{3 - \frac{x^2}{5 - ...}}}
$$

Here's the code:

```scheme
(define (tan-cf x k)
  (let ((x-squared (* x x)))
    (cont-frac (lambda (i)
                 (if (= i 0)
                     x
                     (- x-squared)))
               (lambda (i) (+ (* 2 i) 1))
               k)))

(tan-cf (/ (asin 1) 2) 1000) ;; tan(pi/4)
;; 1.0

```


[1]: https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-12.html#%_thm_1.37
[2]: https://en.wikipedia.org/wiki/Continued_fraction
