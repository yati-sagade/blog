---
title: Cryptographic hash functions
layout: post
category: notes
tags: ["cryptography", "math"]
date: 2017-08-12
math: true
---

Hashing is commonly used when we want to reduce a message of an arbitrary size
to a fixed length "digest", for purposes ranging from integrity checking of
files downloaded from the internet to building blocks for cryptocurrencies.
There are many functions one can use to map the input message to its hash. The
only requirement is that the output be of a known, fixed size. For example,
consider the function


$$
H_{mod3}\left(x\right) = x \mod 3
$$

which maps an arbitrarily large value $x$ to a value in the set
$\left\\{ 0,1,2 \right\\}$. Such hash functions (i.e., based on simple modulo
arithmetic) are used (with other, more complicated hash functions) in
distributed systems (see [consistent hashing][1]). However, this simple function
has little utility when it comes to integrity checking. For example, we would
like to download a file and check if the file we downloaded was indeed the one
that we intended to download. This can be solved as follows:

- Website offering the file lists the file's hash along with the hashing
  function used.

- We download the file and use the same hashing function on the contents of the
  file to get its hash.

- Next, we compare the hash published on the site with the answer we got, and
  conclude that the integrity check passed if the hashes are equal.

It is easy to see that the simple modulo function based hashing will not work at
all here, since given any message value $x$ (the contents of the file), every
third value, i.e., $x+3, x+6, ...$ will have the _same_ hash, and an attacker
could fool our integrity checking by adding appropriate content to the original
file.

So what do we need from a good hash function for integrity checking?

## 1. Collision freedom

In the above example, we found _collisions_ under the function $H_{mod3}$ --
i.e., we could easily craft a message $x'$ such that $H_{mod3}\left(x\right)
= H_{mod3}\left(x'\right)$ (just pick $x' = x + 3k$ for any $k \gt 1$). We want
a hash function $H$ such that it is extremely hard to find collisions under it.
Note that since a hash function must transform an arbitrary message into
a _fixed size_ output that is often much smaller than the input size, there will
necessarily be collisions -- a large number of them indeed. What is important is
that it is extremely hard to craft a message that does not equal the original
message, but whose hash still matches that of the original message.


## 2. Hiding

It should be extremely hard to figure out the original message $x$ from its
hash $H\left(x\right)$. Our modulo function $H_{mod3}$ is actually pretty good
at this --- given the remainder of a number of when divided by 3, you cannot
figure out the original number at all, even though you _can_ reduce the number
of candidates by only looking at the numbers that produce the given remainder
when divided by 3. As you might notice, the degree of hiding offered by the
hashing function depends on the range of values that the message variable $x$
can take up: consider trying to hide the outcome of a coin toss. We'll encode
$\text{HEAD}=0$, and $\text{TAIL}=1$.
    
$$
H_{toss}\left(\text{outcome}\right) = \left(1 + \text{outcome}\right) \mod 2
$$

such that $H_{toss}\left(\text{HEAD}\right) = 1$ and $H_{toss}\left(\text{TAIL}\right) = 0$.

Now if the domain ($\left\\{\text{HEAD},\text{TAIL}\right\\}$) is known to the
attacker, given a hash value 1, they might simply try hashing each value in the
set to find out that the original message was HEAD. The problem here is that the
message domain is easily enumerable. Now if we pick a random integer of, say 256
bits, $r$ from a distribution with a high [min entropy][2], and use its bits
appended to the original message's bits, we suddenly have an input space which
is extremely hard to enumerate ($2^257$ possibilities). So, now, given a hash
value of 1, it is extremely hard for an attacker without the knowledge of the
random key $r$ to deduce the outcome of the toss. Min entropy of a distribution
is simply the negative logarithm of the probability of the _most probable_ value
being taken up by the random variable distributed according to that
distribution. For example, if you have a loaded die that shows a 6 50% of the
times, with the other faces each having a probability of 10%, the min entropy of
this distribution would be $-\lg{\frac{1}{2}} = 1$, since the most probable
value, 6, comes up with a probability $\frac{1}{2}\$. Intuitively, when all
values in a distribution are negligibly likely, and no particular value is
more likely than others, the distribution has a high min entropy, and it is
increasingly difficult to enumerate such a distribution's values to break the
hiding property of a hash function.

## 3 "Puzzle friendliness"

For the sake of using hashes as challenges, as is done in cryptocurrency
implementations, we need an additional property from a good hash function. Given
a key $k$ chosen from a distribution with high min entropy, and a set of target
hash values $Y$, it should be hard to find a value $x$ such that the
concatenation of $k$ and $x$ hashes to a value in $Y$. More precisely, by "hard"
we mean that no strategy of picking $x$ values should be better than randomly
picking $x$ values and trying if $H\(k|x\) \in Y$.

[1]: https://en.wikipedia.org/wiki/Consistent_hashing
[2]: https://en.wikipedia.org/wiki/Min_entropy
