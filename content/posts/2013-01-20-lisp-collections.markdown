---
title: Common Lisp Collections
layout: post
date: 2013-01-20
---


Even though Lisp lists are remarkably powerful and flexible, they are not the
only data-structure available in Common Lisp. Among the most useful other
data structures are arrays and hash tables.

Vectors
--------
Vectors in Common Lisp come in two flavours - fixed size and resizeable. The
former are roughly the Lisp analogues of C/Java arrays and the latter are more
like Python lists or C++ ``std::vector``.

Vectors can be created using the ``VECTOR`` function by passing it an arbitrary
number of elements in the vector:

    CL-USER> (vector 1 2 3)
    #(1 2 3)

    CL-USER> (vector)
    #()

These calls return a *fixed-size* vector. Note that the literal syntax for
vectors is ``#(...)``.

There is a more general function called ``MAKE-ARRAY`` that can make multi-
dimensional arrays(including vectors, which are just 1-D arrays).

    CL-USER> (make-array 5)
    #(0 0 0 0 0)
    CL-USER> (make-array '(2 2))
    #2A((0 0) (0 0))
    CL-USER> (make-array '(5))
    #(0 0 0 0 0)

The only required argument to ``MAKE-ARRAY`` is the dimension of the array
being requested, as a list. As a convenience, when we want a vector(i.e., only
one dimension), we can skip wrapping the size of that dimension in a list - a
bare number is accepted. This returns a *resizeable* vector. The arrays returned
from ``MAKE-ARRAY`` may not have their elements initialized, so they may not
be accessed before a ``SETF`` (this is not the case on SBCL at least, but it is
a good idea to initialize anyway). To initialize all the elements of an array
with a value, pass that value as the ``:initial-element`` keyword argument to
``MAKE-ARRAY``.

    CL-USER> (make-array '(2 2) :initial-element "hola")
    #2A(("hola" "hola") ("hola" "hola"))

Resizeable vectors have a *fill pointer* associated with them, which is
basically the index of the next vacant position in the vector. To create a
vector of capacity 5 which is initially empty, we must specify the
``:fill-pointer`` keyword argument to ``MAKE-ARRAY`` as 0.

    CL-USER> (make-array 5 :fill-pointer 0)
    #()
    CL-USER> (make-array 5 :fill-pointer 1)
    #(0)
    CL-USER> (make-array 5 :fill-pointer 1 :initial-element 10)
    #(10)

Once we have a resizeable vector, we can insert elements in it using the
``VECTOR-PUSH`` function, which adds an item at the fill pointer and increments
the fill pointer value and returns the index at which the new element was
inserted. The inverse to this is ``VECTOR-POP``, which returns the last pushed
element and decrements the fill pointer by one.

Note that when you try to push past the allocated capacity of a vector, no
push happens and ``VECTOR-PUSH`` returns ``NIL`` to signify this. To make
truly resizeable vectors set the ``:adjustable`` keyword argument to non-nil
when creating the vector using ``MAKE-ARRAY``. To insert stuff into a
resizeable vector, we use ``VECTOR-PUSH-EXTEND``, which increases the capacity
of the underlying storage if a push is attempted beyond the current capacity
of the vector.

    CL-USER> (defparameter *x* (make-array 2 :fill-pointer 0))
    *X*
    CL-USER> (vector-push 'a *x*)
    0
    CL-USER> (vector-push 'b *x*)
    1
    CL-USER> *x*
    #(A B)
    CL-USER> (vector-push 'c *x*)
    NIL
    CL-USER> *x*
    #(A B)
    ;; Now a create a resizeable vector:
    CL-USER> (defparameter *y* (make-array 2 :fill-pointer 0 :adjustable t))
    *Y*
    CL-USER> (vector-push-extend 'a *y*)
    0
    CL-USER> (vector-push-extend 'b *y*)
    1
    CL-USER> *y*
    #(A B)
    CL-USER> (vector-push-extend 'c *y*)
    2
    CL-USER> *y*
    #(A B C)

One can create specialized vectors to hold strictly a particular type of
elements by passing a type descriptor to ``MAKE-ARRAY`` via the
``:element-type`` keyword argument. So, one can create resizeable and mutable
strings like so:

    CL-USER> (make-array 5 :fill-pointer 0 :adjustable t :element-type 'character)
    ""

Which implies that strings are actually implemented as vectors!

Both lists and vectors(both the general and specialized variants) are a form of
*sequences*, which is a higher level abstraction. This calls for operations that
are valid on any sequence - i.e., operations common to vectors and lists.

Two of them are ``LENGTH`` and ``ELT``, for taking the length of a sequence and
getting the element at a particular index in a sequence, respectively.

There are some other functions that operate on sequences:

``COUNT`` takes an item and a sequence and returns the number of occurrences of
the item in that sequence.

``FIND`` takes an item and a sequence and returns the item if it is found in
the sequence and ``NIL`` otherwise.

``POSITION`` takes an item and a sequence and returns the index of the first
occurrence of the item in the sequence if found and ``NIL`` otherwise.

``REMOVE`` takes an item and a sequence and *returns* a new sequence with all
occurrences of the item removed.

``SUBSTITUTE`` takes a new-item, item and a sequence and returns a new sequence
with all occurrences of the item replaced by new-item.

All these functions use the generic object equality test ``EQL`` when comparing
two elements. But we can pass a custom function that tests the equality of
two elements in the ``:test`` keyword argument. Further customization can be
done by passing in a one argument function as the ``:key`` keyword argument
which is applied on every element and the return value is used for the
comparison.

The ``:start`` and ``:end`` keyword arguments can be given the starting and
(one past) the ending indices of the subsequence of the passed sequence to
operate on. If the keyword argument ``:from-end`` is true, the (sub)sequence is
operated on in reverse order.

In addition to these, ``SUBSTITUTE`` and ``REMOVE`` take another keyword
argument ``:count`` that specifies the number of elements to substitute of
remove in the result.

There is a class of sequence functions similar to the above, but which, instead
of taking an element and a sequence, take a one argument predicate and a
sequence. For example, ``REMOVE-IF-NOT`` takes a predicate and a sequence and
returns a sequence with all the elements that satisfy that predicate.
``REMOVE-IF``, on the other hand, does the opposite - returns a sequence with
all elements that do NOT satisfy the predicate.

    CL-USER> (defparameter *n* #(1 2 3 4 5))
    *N*
    CL-USER> (remove-if-not #'evenp *n*)
    #(2 4)
    CL-USER> (remove 1 *n*)
    #(2 3 4 5)
    CL-USER> (find 'a #((a 1) (b 2) (c 3)))
    NIL
    CL-USER> (find 'a #((a 1) (b 2) (c 3)) :key #'first)
    (A 1)
    CL-USER> (find 'a #((a 1) (b 2) (c 3) (a 4)) :key #'first)
    (A 1)
    CL-USER> (find 'a #((a 1) (b 2) (c 3) (a 4)) :key #'first :from-end t)
    (A 4)
    CL-USER> (substitute '(g 1) 'a #((a 1) (b 2) (c 3) (a 4)) :key #'first)
    #((G 1) (B 2) (C 3) (G 1))
    CL-USER> (substitute '(g 1) 'a #((a 1) (b 2) (c 3) (a 4)) :key #'first :count 1)
    #((G 1) (B 2) (C 3) (A 4))
    CL-USER> (substitute '(g 1) 'a #((a 1) (b 2) (c 3) (a 4)) :key #'first :count 1 :from-end t)
    #((A 1) (B 2) (C 3) (G 1))
    CL-USER> (substitute-if '(g 1) #'(lambda (x) (eql (first x) 'a)) #((a 1) (b 2) (c 3) (a )))
    #((G 1) (B 2) (C 3) (G 1))

``REMOVE-DUPLICATES`` takes a sequence and removes all the duplicate elements,
keeping the lasts of each kind in the default invocation. It takes the same
keyword arguments as ``REMOVE`` except ``:count``.

    CL-USER> (remove-duplicates #(1 1 1 2 1 3 4 5 1))
    #(2 3 4 5 1)
    CL-USER> (remove-duplicates #(1 1 1 2 1 3 4 5 1) :from-end t)
    #(1 2 3 4 5)

Some functions that operate on sequences as a whole are also provided. For
example, there is ``COPY-SEQ`` that returns a copy of its sole argument and
there is ``REVERSE`` that returns a copy of its only argument with the items
arranged in the reverse order. 

The ``CONCATENATE`` function creates and returns a new sequence by concatenating
any number of sequences. It must also be given the type of the sequence we
expect from it.

    CL-USER> (reverse #(1 2 3))
    #(3 2 1)
    CL-USER> (reverse '(1 2 3))
    (3 2 1)
    CL-USER> (concatenate 'vector #(1 2 3) '(a b c))
    #(1 2 3 A B C)
    CL-USER> (concatenate 'list #(1 2 3) '(a b c))
    (1 2 3 A B C)
    CL-USER> (copy-seq #(1 2 3))
    #(1 2 3)

``REVERSE`` and ``COPY-SEQ`` return a sequence of the same type as their
sole argument.

Sorting and merging support is provided in the CL standard library via the
``SORT``, ``STABLE-SORT`` and ``MERGE`` functions. Both ``SORT`` and
``STABLE-SORT`` are destructive functions and will modify their argument. Like
``CONCATENATE``, ``MERGE`` also requires a type specifier as the first argument
which becomes the type of the sequence returned.

``SUBSEQ`` can be used to extract/assign-to subsequences.

    CL-USER> (subseq "lama" 1)
    "ama"
    CL-USER> (concatenate 'string "os" (subseq "lama" 1))
    "osama"
    CL-USER> (subseq "obama" 1 3)
    "ba"

``SUBSEQ`` returns a ``SETF`` able place, but it does not extend/shrink a
sequence. If the new value and the subsequence to be replaces are of different
lengths, the shorter one determines the number of characters actually replaced.

    CL-USER> (defparameter *x* (copy-seq "foobarbaz"))
    *X*
    CL-USER> (subseq *x* 3 6)
    "bar"
    CL-USER> (setf (subseq *x* 3 6) "xxx")
    "xxx"
    CL-USER> *x*
    "fooxxxbaz"
    CL-USER> (setf (subseq *x* 3 6) "abcs")
    "abcs"
    CL-USER> *x*
    "fooabcbaz"
    CL-USER> (setf (subseq *x* 3 6) "xx")
    "xx"
    CL-USER> *x*
    "fooxxcbaz"


Hashtables
------------

Common Lisp has hash-tables, that are the CL analogs of Python dicts
or the C++ ``std::map``. A hashtable can be created using ``MAKE-HASH-TABLE``
which also accepts a ``:test`` keyword parameter, which can only be one of
``EQL`` (which is the default), ``EQUAL``, ``EQ`` or ``EQUALP``. 

The ``GETHASH`` function can be used to get the value stored in a hash under
a key. The first argument to ``GETHASH`` is the key and the second is the
hashtable. One can use ``SETF`` with ``GETHASH`` to set values in a hashtable.
``GETHASH`` returns two values - the first one is the value under the given
key in the given hash table, or ``NIL`` if there is no such key. The second
return value is a boolean which indicates whether the requested key was present
in the hashtable or not. This is needed because the first return value being
``NIL`` can mean either the key is not present or that while the key is present,
the value under the requested key is itself ``NIL``.

    CL-USER> (defparameter *h* (make-hash-table))
    *H*
    CL-USER> (gethash 'foo *h*)
    NIL
    NIL
    CL-USER> (setf (gethash 'foo *h*) "hello")
    "hello"
    CL-USER> (gethash 'foo *h*)
    "hello"
    T
    CL-USER> (setf (gethash 'foo *h*) "hello")
    "hello"
    CL-USER> (gethash :foo *h*)
    NIL
    NIL

``REMHASH`` takes the same arguments as ``GETHASH`` and removes the key given.
``CLRHASH`` clears an entire hashtable.

Iterating over a hashtable
---------------------------

The ``MAPHASH`` function takes a two argument function and a hashtable and
calls the passed function for each key-value pair in the hashtable. One can
``SETF`` and ``REMHASH`` the current entry, but other than that, adding/removing
arbitrary elements to a hashtable leads to undefined behaviour.


    CL-USER> (defparameter *hashtab* (make-hash-table))
    *HASHTAB*
    CL-USER> (setf (getf 'one *hashtab*) 1)

    1
    CL-USER> (setf (getf 'two *hashtab*) 2)

    2
    CL-USER> (maphash #'(lambda (k v)
                            (format t "~a is counted out loud as ~a~%" v k))
                      *hashtab*)

    1 is counted out loud as ONE
    2 is counted out loud as TWO
    NIL

To conclude, Common Lisp is a very rich language, which sometimes makes it look
ugly, just like C++, but I'll take the ugliness of a practical, powerful
language anyday over being circumscribed by an aesthetically pleasing toy
language.


