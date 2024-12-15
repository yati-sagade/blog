---
title: "Writing a type-checking calculator"
date: 2023-06-18
showToc: true
---
To learn about typecheckers, I decided to make a small typed calculator. I
figured this could be useful to other folks trying to learn about implementing
typed languages.


## High-level requirements

* Support integer, float and boolean datatypes and common operations on them
* Support typechecking of expressions
* Support variables
* Take multiple expressions, one per line, and evaluate each in order:
  - Report type errors if any
  - Print evaluation result if no errors
  - An expression can use variables set in previous expressions

### Example program

```py
a = 42;
b = 10;
a + b < 100;
```

Running the above should print

```py
a = 42
	[<type:Int>] 42
b = 10
	[<type:Int>] 10
a + b < 100
	[<type:Bool>] true
```

## Implementation design

The calculator is structured like a very typical amateur interpreter project:

<img src="/images/tycalc-arch.svg"
    width="80%"
     alt="program text is tokenized into tokens by a scanner; tokens are parsed into parse trees by the parser; the parse trees are then type-checked by the typechecker, which produces annotated trees with type information; finally, these typed trees are interpreted to produce values" />


The scanner first splits the input program into a list of tokens. For our program, this
step produces the tokens `[Ident(a), Sym(=), Int(10), Sym(;), Ident(b), Sym(=),
Int(42), ...]`. Note how no meaning is ascribed to groups of symbols yet, this
is all about grouping characters into meaningful symbols.

Next, the parser groups tokens together into expressions, and emits a list of
parse trees, one per expression. Note how our expressions are delimited by the
`;` symbol, and just splitting the input text on the semicolon would also be
kind of a grouping of expressions. But our parser produces a richer, tree
structure that encodes precedence. In each expression tree node, any child
expressions need to be evaluated before evaluating the node itself. For example,
the last expression in our program, `a + b < 100;` is parsed into

        BinaryExpr(Sym(<), 
            BinaryExpr(Sym(+),
               IdentExpr(Ident(a); attrs={}),
               IdentExpr(Ident(b); attrs={}); attrs={}),
            Literal(Int(100); attrs={}); attrs={})

Note how the `+` operation is a child of the `<` operation, indicating that `+`
should be evaluated first (i.e., binary `+` has a higher precedence than binary
`<` in our language). 

Next, the typechecker attaches type information to each expression. That's what
will go in the `attrs` attached to each parse tree node. For instance, this is how the above tree for `a + b < 100;` looks when type-annotated:

        BinaryExpr(Sym(<),
          BinaryExpr(Sym(+),
            IdentExpr(Ident(a); attrs={'type': <type:Int>}),
            IdentExpr(Ident(b); attrs={'type': <type:Int>}); attrs={'type': <type:Int>}),
          Literal(Int(100); attrs={'type': <type:Int>}); attrs={'type': <type:Bool>})

See how each sub-expression is now annotated with its deduced type, and so is
the top-level expression.

Finally, the interpreter walks the list of expression trees, evaluating each in post-order.

At any point, any of the components can have a fatal error that causes the
program to halt with an exception.

## Grammar

To implement the scanner and parser components, it is useful to write down the
the grammar of our little expression language. Here's the grammar in
[PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) syntax:

```peg
TyCalc {
  Prog = Stmt*
  Stmt = Expr ";"
  Expr = Assignment
  Assignment = AssignmentAux | LogicalOr
  AssignmentAux = ident "=" Assignment
  LogicalOr = LogicalAnd ("||" LogicalAnd)*
  LogicalAnd = Equality ("&&" Equality)*
  Equality = Comparison (("!=" | "==") Comparison)*
  Comparison = Term (("<=" | "<" | ">" | ">=") Term)*
  Term = Factor (("+" | "-") Factor)*
  Factor = Unary (("*" | "/" | "%") Unary)*
  Unary = ("+" | "-")? Exponent
  Exponent = ExponentExpr | Primary
  ExponentExpr = Exponent ("**" Exponent)*
  Primary = ParenExpr | ident | numlit | boollit
  ParenExpr = "(" Expr ")"
  ident = letter alnum*
  numlit = fractional | integral
  fractional = digit* "." digit+
  integral = digit+
  boollit = "true" | "false"
}
```

My favorite tool to play with a grammar is the online [OhmJS
editor](https://ohmjs.org/editor/). Paste this grammar, add examples and see the
editor explain the parses.

Nothing fancy, most of the complexity in the grammar is to properly encode
operator precedence, and some quirks of the Ohm PEG notation. Here's some examples:

* Variable assignment
    ```c
    a = 1
    b = true
    ```
* Arithmetic
    ```c
    a + 12.3 ** 6
    ```
* Logic
    ```c
    b && true
    ```
* Equality
    ```c
    b && a < 10
    ```
* Parenthesized expressions
    ```c
    (2 + a) * 4
    ```

## Parsing

Once the grammar is written down, you can either generate a parser for it using
[OhmJS](https://ohmjs.org/) or [ANTLR](https://www.antlr.org/), or roll your own
[recursive-descent
parser](https://en.wikipedia.org/wiki/Recursive_descent_parser). I rolled my
[own parser](https://github.com/yati-sagade/tycalc/blob/main/parsing.py), and if you are new to this, I highly recommend [Crafting
Interpreters](https://craftinginterpreters.com/contents.html).

You can print the parse tree of any tycalc program by invoking [parsing.py](https://github.com/yati-sagade/tycalc/blob/main/parsing.py) as follows:

```bash
$ python parsing.py FILENAME # -OR-
$ echo 'a + b;' |python parsing.py
```

## Typechecking

*Typechecking is implemented in [typechecking.py](https://github.com/yati-sagade/tycalc/blob/main/typechecking.py)*.

The goal of the typechecking phase is to assign a type to each expression in the
program, producing an error if this is not possible. Modern languages have sophisticated type inference, and it is not always an "error" if the typechecker cannot figure out the type of an expression -- it just might need more type annotations to eliminate ambiguity. Our language is, however, very small, and the typechecker is also quite simple. Here are the rules for type assignment:

1. Literals get their types trivially:

    - `true` is always a `Bool`
    - `1234` is an `Int`
    - `12.3`, `.4`, `99.` are all `Float`s

2. Each variable assignments sets the type of the variable to the assignment's right hand side, and this is the type of the variable until it is reassigned later.
3. Arithmetic operations (`+`, `-`, `*`, `/`) expect numeric arguments (either `Int` or `Float`). If either of the arguments is a `Float`, the result is also a `Float`, else it is an `Int`.
4. The integer division remainder (mod) operation (`%`) expects `Int` arguments.
5. The operators (`<=`, `>=`, `<`, `>`) expect numeric arguments and produce a `Bool`.
6. The operators `==` and `!=` expect either two numeric arguments, or two `Bool` arguments, and produce a `Bool`.
7. Logic operators (`&&`, `||`) take two `Bool`s and produce a `Bool`.

We can model type assignment of an expression as a recursive problem of
assigning types to the child expressions in the expression's AST, and then
calculating the resulting type using the rules above.

Let's look at an example:

```
a = 42;
b = 10.;
a + b < 100;
```

Here's the result of running our parser on it.

```python
python parsing.py <(echo "a = 42; b = 10.; a + b < 100;")
====== Input program =========
a = 42; b = 10.; a + b < 100;
====== Parse trees (one line per input expr) =========
 BinaryExpr(Sym(=), IdentExpr(Ident(a); attrs={}), Literal(Int(42); attrs={}); attrs={})
 BinaryExpr(Sym(=), IdentExpr(Ident(b); attrs={}), Literal(Float(10.0); attrs={}); attrs={})
 BinaryExpr(Sym(<), BinaryExpr(Sym(+), IdentExpr(Ident(a); attrs={}), IdentExpr(Ident(b); attrs={}); attrs={}), Literal(Int(100); attrs={}); attrs={})
```

The empty `attrs` associated with each subexpression will eventually contain the
type. Let's work out the type deduction by hand.

For the first expression assigns the integer literal `42` to `a`. The result of this assignment expression is twofold:

- The binary assignment expression itself is typed as `Int`,
- The typechecker remembers that subsequent references to the variable `a` are
`Int`-typed, until `a` is redefined.

Similarly, the next expression assigns the `Float` literal `10.` to the variable
`b`, so the expression has type `Float`, and the typechecker remembers that `b`
has type `Float`.

Now let's zoom into the last expression:

```python
BinaryExpr(Sym(<), # .......................... toplevel expr
    BinaryExpr(Sym(+), # .......................|- subexpr 1
      IdentExpr(Ident(a); attrs={}), # ............|- subexpr 1.1
      IdentExpr(Ident(b); attrs={}); attrs={} # ...|- subexpr 1.2
    ),                                        # | 
    Literal(Int(100); attrs={}) # ..............|- subexpr 2
 ; attrs={})
```


We know that the type of a valid `<` operation is always a boolean, and the
operation is valid if both its arguments are numbers. Therefore, we need to
first find the types of `subexpr 1` and `subexpr 2`.

 - To find the type of subexpr 1, we need the types of subexprs 1.1 and 1.2
   
   - subexpr 1.1 is a variable reference to `a`, and `a` is previously defined as an `Int` in `a = 42;`.
   - subexpr 1.2 is a variable reference to `b`, and `b` is previously defined as a `Float` in `a = 10.;`
   - Therefore, subexpr 1 is typed as a `Float` by rule (3) above.

 - subexpr 2 is easy, it is an `Int` literal, which always has the type `Int`.

 - Therefore, the arguments to our `<` operation have types `Float` and `Int`.
 This is a valid operation, and the result has the type `Bool`.


Here's the result of running the typechecker alone on our program above:

```py
$ python typechecking.py <(echo "a = 42; b = 10.; a + b < 100;")
====== Input program =========
a = 42; b = 10.; a + b < 100;
====== Typed parse trees (one line per input expr) =========
 BinaryExpr(Sym(=), IdentExpr(Ident(a); attrs={}), Literal(Int(42); attrs={'type': <type:Int>}); attrs={'type': <type:Int>})
 BinaryExpr(Sym(=), IdentExpr(Ident(b); attrs={}), Literal(Float(10.0); attrs={'type': <type:Float>}); attrs={'type': <type:Float>})
 BinaryExpr(Sym(<), BinaryExpr(Sym(+), IdentExpr(Ident(a); attrs={'type': <type:Int>}), IdentExpr(Ident(b); attrs={'type': <type:Float>}); attrs={'type': <type:Float>}), Literal(Int(100); attrs={'type': <type:Int>}); attrs={'type': <type:Bool>})
```

Notice how each subexpression now has types, the same ones we worked out manually.

Now let's look at an example where the typechecking fails:

```py
python typechecking.py <(echo "a = 42; b = true; a + b;")
====== Input program =========
a = 42; b = true; a + b;
====== Typed parse trees (one line per input expr) =========
 BinaryExpr(Sym(=), IdentExpr(Ident(a); attrs={}), Literal(Int(42); attrs={'type': <type:Int>}); attrs={'type': <type:Int>})
 BinaryExpr(Sym(=), IdentExpr(Ident(b); attrs={}), Literal(Bool(True); attrs={'type': <type:Bool>}); attrs={'type': <type:Bool>})
 BinaryExpr(Sym(+), IdentExpr(Ident(a); attrs={'type': <type:Int>}), IdentExpr(Ident(b); attrs={'type': <type:Bool>}); attrs={'type': <badtype:Invalid operand types for Sym(+): <type:Int>, <type:Bool>>})
 ```

 So here, we attempted to add an `Int` and a `Bool`, and the typechcker produced
 the "type" of the final expression as a special type, which actually represents
 a typecheck error. This strategy, of progressively typing as many expressions
 as possible without breaking the program, allows catching multiple errors at
 once.

## Evaluation

*Evaluation is implemented in [interp.py](https://github.com/yati-sagade/tycalc/blob/main/interp.py)*.

The evaluation is very simple, it just visits the type-annotated expression
trees, remembering values of variables, and evaluates each expression by walking
its tree. In fact, for this simple calculator, we did not need a separate
typechecking pass, and could have bundled typechecking along with evaluation.
But in a more interesting language, it is almost always a good idea to keep
typechecking and evaluation as different passes. This will make your life easier
as you add more features to the language.