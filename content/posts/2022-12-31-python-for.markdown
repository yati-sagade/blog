---
title: Python's for loop syntax is more flexible than I thought!
date: 2022-12-31
summary: TL;DR - All assignment LHS forms are valid syntax for the for-loop target
---

I came across an expression like:

```python
for self.batch in batches:
    ...
```

I had no idea one could use expressions like `self.batch` as the loop iterator.
This works as expected, and right after the last iteration of the loop (assuming
there was one), `self.batch` is set to the last item of `batches`. It _also_
works if `self` had no attribute called `batch` initially.

So I was curious and looked up the relevant portion of the [grammar](https://docs.python.org/3/reference/grammar.html), which is:

```ebnf
# For statement
# -------------

for_stmt:
    | 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block] 
    | ASYNC 'for' star_targets 'in' ~ star_expressions ':' [TYPE_COMMENT] block [else_block] 
```

So the left side of the `for .. in ..` construct can contain "`star_targets`":

```ebnf
star_targets:
    | star_target !',' 
    | star_target (',' star_target )* [','] 

star_targets_list_seq: ','.star_target+ [','] 

star_targets_tuple_seq:
    | star_target (',' star_target )+ [','] 
    | star_target ',' 

star_target:
    | '*' (!'*' star_target) 
    | target_with_star_atom

target_with_star_atom:
    | t_primary '.' NAME !t_lookahead 
    | t_primary '[' slices ']' !t_lookahead 
    | star_atom
```

This is a bit more flexible than being able to use an attribute for the iterator. 

1. Using an attribute:
```python
class Foo:
  x = 0

foo = Foo()

for foo.x in range(3):
  print(foo.x)

0
1
2
```

2. Using a `*sequence`. 

```python
for x, *y, z in ((1, 2, 3), ('bar', 'baz', 'spam')):
    print(x, y, z)

1 [2] 3
bar ['baz'] spam
```

In this form, very sensibly, you can have at most one `*starred`, and specifying
more than one is a syntax error.

3. Using a slice

```python
x = [1, 2, 3]
for x[:2] in [(0, 0), ('bar', 'baz')]:
  print(x)

[0, 0, 3]
['bar', 'baz', 3]
```

I think I've needed to do what each of the above are doing, but I have always
gone about it in a more direct style. I am not sure if these lesser known ways
of iteration are immediately more or less readable, but they don't look too
clunky.
