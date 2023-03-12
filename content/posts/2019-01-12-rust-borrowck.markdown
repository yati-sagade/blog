---
date: 2019-01-12

layout: post

title: Embrace the borrow checker

---

The borrow checker is arguably one of the biggest sources of frustration when
learning Rust. Once the Rust compiler is satisfied with the syntax, it gets down
to the real stuff: proving that your program is free from data races caused by
aliasing of memory.

However hard it might seem, the borrow checker _is_ really right, and once you
internalize its ways, data-race prone code written in any language will jump out
at you, even without actually running the code.

For me, one of the most irritating borrow checker complaints was its refusal to
admit code like this:

```rust
    let mut x = 5;
    let _alias = &x;

    x = 6;
```

which produces the following output:

```rust
    error[E0506]: cannot assign to `x` because it is borrowed
     --> ./test.rs:4:5
      |
    3 |     let _alias = &x;
      |                   - borrow of `x` occurs here
    4 |     x = 6;
      |     ^^^^^ assignment to borrowed `x` occurs here

    error: aborting due to previous error

    For more information about this error, try `rustc --explain E0506`.
```

That is perfectly ok in C++. The assignment would be visible via any alias
(either a reference or a raw pointer). Why is Rust complaining about creating
read/write aliases to the same memory location *in the same thread*? Consider
the following snippet:

```rust
    fn main() {
        let mut vec = vec!["foo", "bar", "baz"];
        println!("{:?}", &vec);

        // A reference to the first item in the vector
        let _alias = vec.get(0).unwrap();
        println!("{:?}", &vec);

        vec.push("another");
        println!("{:?}", &vec);
    }
```

As expected, that code doesn't compile -- it is essentially the same as the
first snippet. Can you spot the issue now? If not, consider this code:

```rust
    fn main() {
        let mut vec = vec!["foo", "bar", "baz"];
        println!("{:?}", &vec);

        // A reference to the first item in the vector
        let _alias = vec.get(0).unwrap();
        println!("{:?}", &vec);

        for _ in 0..1_000_000_000 {
            vec.push("item");
        }

        println!("{:?}", &vec);
    }
```

Spot it now?

So a `Vec` is a resizable collection of items, sequentially stored in memory.
The implementation starts out with an array for the storage. When the
application tries to insert more items than the storage can currently hold, the
implementation will reallocate memory, copy all items from the old memory
range to the new (larger) one, and release the old memory range. Any aliases
into the old range of memory are invalid after such reallocation. In the above
program, there will almost certainly be a reallocation, which would make the
`_alias` reference invalid. Fortunately, Rust's simple borrowing rules are
enough to flag this program as invalid.

Let's see what happens in C++ though:

```c++
    #include <iostream>
    #include <vector>

    template<class T>
    void printvec(const std::vector<T>& vec)
    {
        std::cout << "[";
        bool first = true;
        for (auto& el : vec)
        {
            if (first)
                first = false;
            else
                std::cout << ",";
            std::cout << el;
        }
        std::cout << "]" << std::endl;
    }


    int main()
    {
        std::vector<std::string> vec { "foo", "bar", "baz" };
        printvec(vec);

        auto& alias = vec[0];
        std::cout << "&vec[0] = " << &alias << std::endl;
        std::cout << "vec[0] = " << alias << std::endl;

        for (int i = 0; i < 1000000; i++)
        {
            vec.push_back("lama");
        }

        auto& yet_another_alias = vec[0];
        std::cout << "&vec[0] = " << &yet_another_alias << std::endl;
        std::cout << "vec[0] = " << yet_another_alias << std::endl;

        std::cout << "Old alias points to address " << &alias
                  << ", and  has contents " << alias << std::endl;

        return 0;
    }
```

Output:

```rust
    [foo,bar,baz]
    &vec[0] = 0xabfc20
    vec[0] = foo
    &vec[0] = 0x7f16861de010
    vec[0] = foo
    Old alias points to address 0xabfc20, and  has contents ȋBȋB������B��B [...more garbage...]
```

Note that Rust's borrow checking rules do not talk explicitly about dangling
references caused by such reallocation. By requiring you to prove that a mutable
borrow to a piece of memory is the only such borrow active at any given time in
your program, Rust automatically makes this class of errors impossible. Indeed,
the borrow checker eliminates a *bunch* of other such logic errors caused by
aliasing of memory.

Of course a well known side effect is that occasionally, certain patterns just
cannot be expressed in Rust, and might require some rethinking of how you model
your data. One example that particularly annoys me is the following:

```rust
    use std::sync::{Arc, Mutex};

    struct Foo {
        x: i32,
        history: Vec<i32>,
        mutex: Arc<Mutex<()>>,
    }

    impl Foo {
        fn new(x: i32) -> Foo {
            Foo { x, history: vec![], mutex: Arc::new(Mutex::new(())) }
        }

        fn update(&mut self, x: i32) {
            let _lock = self.mutex.lock().unwrap();
            self.step_history();
            self.x = x;
        }

        fn step_history(&mut self) {
            self.history.push(self.x);
        }
    }

    fn main() {
        let mut foo = Foo::new(0);
        foo.update(1);
    }
```

That is a contrived example of course -- we don't really need `step_history`
here. But this the essence a real, more complicated requirement that came up in
a project of mine. This is the output we get from rustc:

```rust
    error[E0502]: cannot borrow `*self` as mutable because `self.mutex` is also borrowed as immutable
      --> test.rs:16:9
       |
    15 |         let _lock = self.mutex.lock().unwrap();
       |                     ---------- immutable borrow occurs here
    16 |         self.step_history();
       |         ^^^^ mutable borrow occurs here
    17 |         self.x = x;
    18 |     }
       |     - immutable borrow ends here

    error: aborting due to previous error
```

The error is self-explanatory -- the value `_lock` internally holds on to an
immutable borrow of `self` and we are trying to call a method that requires
a coexisting mutable borrow of `self`, which is a no go.

The only solution I've found to this one is to realize that in `step_history`,
we only really need a mutable borrow to `self.history`, not to the entirety of
`self`. So, we could do this:

```rust
    use std::sync::{Arc, Mutex};

    struct Foo {
        x: i32,
        history: Vec<i32>,
        mutex: Arc<Mutex<()>>,
    }

    fn update_history(new_val: i32, history: &mut Vec<i32>) {
        history.push(new_val);
    }

    impl Foo {
        fn new(x: i32) -> Foo {
            Foo { x, history: vec![], mutex: Arc::new(Mutex::new(())) }
        }

        fn update(&mut self, x: i32) {
            let _lock = self.mutex.lock().unwrap();
            let history = &mut self.history;
            update_history(x, history);
            self.x = x;
        }
    }

    fn main() {
        let mut foo = Foo::new(0);
        foo.update(1);
    }
```

Note how we now directly borrow the required field, and use it like a normal
mutable borrow.

Another example where the borrow checker can become a pain is self-referential
or cyclic data structure representations, like the straightforward pointer
linked implementation of graphs. There are always alternative rerpresentations,
like using a vector of nodes, and representing the graph adjacency in terms of
*indices* into this vector.

All this does mean that there are programs that you know are correct, but rustc
refuses to accept them because of borrowck failures. Embrace the borrowck here:
*most* of the time, your program was likely incorrect. Even if it wasn't, you
might get to learn an alternative representation for the data you are modeling!

