---
title: Doing numbers without the numbers
layout: post
date: 2017-07-30

---

Numbers are abstractions invented by humans to aid with various activities,
mainly counting, and sometimes recreation. While the "three" might be the number
of coins in my pocket right now, the number "three" is in itself an abstract
entity, worthy of study in its own right. It is defined as the successor to the
integer "two". It is, in general, really hard to define what data is. According
to one definition, we define data in terms of operations possible on it, and
certain constraints on these operations, like an axiomatic system. Note that
under this scheme, the actual representation of the data object in question is
irrelevant: only the external operations on it and a set of properties obeyed by
those operations is enough.

For example, let's consider natural numbers (0, 1, 2, 3..) as data objects. No
matter how we represent these numbers on a computer, we would like basic
arithmetic properties of numbers to hold, like addition and multiplication of
natural numbers behaving normally, the presence of a total ordering among the
numbers, etc.

On most computers, these numbers are simply represented in their binary form,
usually as 32 or 64 bits. However, like I mentioned above, as long as the
expected operations on natural numbers are available and obey certain
properties, the representation does not matter. One cool way of encoding numbers
is the [Church encoding][1], due to Alonzo Church. In the simplest form, **we
encode a number as the number of applications of a given function $f$**. For
example, $0$ is encoded as _no_ application, $1$ is encoded as just one
application of $f$, while an arbitrary natural number $n$ is encoded as the
function composition $f^n$. Let's try this out in some Perl 6 code:

```perl6
# zero($f) returns a function that just returns its argument, i.e., the identity
# function.
sub zero ($f) {
    -> $x { $x }
}

sub one ($f) {
    -> $x { $f($x) }
}

sub two ($f) {
    -> $x { $f($f($x)) }
}
```

So, for example, `two($foo)` is a function that, when called with some parameter
`$x`, will apply `$foo` twice, i.e., compute `$f($f($x))`.

Of course we don't want to write out all numbers as functions, so we just define
`zero`, and a successor function, which transforms a Church encoded natural
number to the next higher natural number.

```perl6
sub successor ($n) {
    -> $f {
        -> $x {
            $f($n($f)($x))
        }
    }
}
```

The key here is the bit `$f($n($f)($x))`, which is where the "increment" happens
by applying `$f` one more time:

- The expression `$n($f)` is a function that when called with `$x`, will apply
  `$f` for `$n` times, to compute $f^n\left(x\right)$
- i.e., `$n($f)($x)` _is_ the result of applying the composition obtained by
  repeating `$f` for `$n` times to `$x`.
- Next, we simply add another `$f` call to the chain, thus ending up with
  `$f($n($f)($x))`.

Note that the returned value is still a function that takes a function `$f`, and
returns another function of the variable `$x`, which in turn applies `$f` for
$n+1$ times to `$x`. This is consistent with the interface we have for `zero`,
and more importantly, demonstrates the use of closures: the function of `$x`
_captures_ its environment, which contains `$f`. Also, the function of `$f` (the
outer lambda returned by `successor`) captures the function `$n` as it was when
provided as an argument to `successor`.

To make it even clearer, let's try to come up with a mechanism to convert from
the Church representation to normal Perl 6 numbers. We want to invent a function
`$g` and a value `$a`, that when used with any of our Church encoded numbers,
give us the corresponding integers. Concretely, we want:

```perl6

zero($g)($a) --> 0
one($g)($a)  --> 1
successor(successor(one))($g)($a) --> 2
...
```

One choice could be to use `$g = { $_ + 1 }`, i.e., the increment function, with
`$a = 0`:

```perl6
sub increment ($x) { $x + 1 }

sub church-to-human ($n) {
    $n(&increment)(0)
}

church-to-human(successor(successor(successor(zero)))).say; #: 3
```

Once we understand this function, the rest of the operations are easy to derive:

```perl6
sub zero ($f) {
    -> $x { $x }
}

sub successor ($n) {
    -> $f {
        -> $x {
            $f($n($f)($x))
        }
    }
}

sub add ($y, $z) {
    -> $f {
        -> $x {
            $z($f)($y($f)($x))
        }
    }
}

sub multiply ($y, $z) {
    -> $f {
        -> $x {
            $y($z($f))($x)
        }
    }
}
```


The predecessor function, however, is a bit more involved: given a numeral $n$,
that applies $f$ for $n$ times to an initial value $x$, we want to derive a
function that applies $f$ _one less time_. While there are multiple ways of
doing this, the easiest to understand for me was to apply $n$ to _transformed_
versions of $f$ and $x$. Let's first define a function $g$ that takes a _pair_
$\left(a, b\right)$ and if $a=0$, returns $\left(0, f(a)\right)$, and if $a=1$,
returns $\left(0, a\right)$. In essence, the first element of the pair tells $g$
if it should _skip_ applying $f$ to the second element. Here's $g$:
    
$$
g\left(p\right) =
\begin{cases}
 \left(0, z\right), & \text{when } p = \left(1, z\right) \\\\
 \left(0, f(z)\right), & \text{when } p = \left(0, z\right)
\end{cases}
$$

Note that if $g$ is composed for $n$ times and applied to a pair $\left(1,
x\right)$, we will in the end have the pair $\left(0,
f^{n-1}\left(x\right)\right)$!

e.g.,

$$
g\left(g\left(\left(1, x\right)\right)\right) \\\\
= g\left(\left(0, x\right)\right) \\\\
= \left(0, f\left(x\right)\right)
$$

Now Perl 6 of course has lists which we could use to represent our pairs, but
let's use an alternate representation in the spirit of this post. A pair is
a data object that stores two other objects, and provides the two functions
`first` and `second` for accessing those objects. This can be implemented like
so:

```perl6
# The constructor returns a function which takes a function and applies it
# to the contained objects.
sub pair ($x, $y) {
    -> $f {
        $f($x, $y)
    }
}

# Apply the pair object to a function that returns its first argument
sub first ($pair) {
    $pair(-> $x, $y { $x })
}

# Apply the pair object to a function that returns its second argument
sub second ($pair) {
    $pair(-> $x, $y { $y })
}
```

To take things even further, let's also encode the boolean type, and implement
a conditional function:

```perl6
my $true = -> $fst {
    -> $snd {
        $fst;
    }
};

my $false = -> $fst {
    -> $snd {
        $snd;
    }
};

sub If ($cond, $then, $else) {
    $cond($then)($else)
}
```


Now let's implement the predecessor function, finally:

```perl6
sub pred ($n) {
    -> $f {
        -> $x {
            my $g = -> $pair {
                If(first($pair),
                   pair($false, second($pair)),
                   pair($false, $f(second($pair))))
            };
            my $p = pair($true, $x);
            second($n($g)($p));
        }
    }
}

# Subtraction of $z from $y is the same as finding the $z'th predecessor of $y,
# which means we apply `pred` to $y for $z times, which is readily done by
# calling $z with pred().
sub subtract ($y, $z) {
    -> $f {
        -> $x {
            $z(&pred)($y)($f)($x)
        }
    }
}
```


[1]: https://en.wikipedia.org/wiki/Church_encoding 
