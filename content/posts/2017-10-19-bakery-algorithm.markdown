---
title: The bakery algorithm for mutual exclusion
layout: post
tags: ["programming", "concurrency"]
date: 2017-10-19
math: true
---


The [bakery algorithm][1] was proposed by Leslie Lamport as a solution to
Dijkstra's concurrent programming problem. In the problem, Dijkstra had first
identified the need for mutual exclusion among a group of concurrently executing
processes.

We want to run `N` processes concurrently, with exclusive access to a shared
resource. Modern day languages solve this with help from hardware. But the
bakery algorithm allows for pure software mutual exclusion by making sure that
at most one process is executing its critical section, while other non-faulty
processes are either in their non-critical section, or spinning in place,
waiting to get to the critical section. In other words, mutual exclusion in the
critical section is achieved in software. Now this is inefficient, since it
involves processes "spinning" in a loop while waiting for a chance to execute
the critical section.

What is remarkable about this algorithm (as Lamport points out multiple times in
the paper) is that even though reads from memory may not be atomic (which is
important with overlapping reads and writes to the same location), the algorithm
works fine, since it does not care _what_ exact value is read, and makes do with
a distinction between _zero_ and _nonzero_ values. Here's an implementation
followed by a description (the code is on github: `go get
github.com/yati-sagade/bakery`):

```go
package main

import (
	"flag"
	"fmt"
	"time"
)

func max(xs []int) int {
	if len(xs) < 1 {
		panic("max() on empty slice")
	}
	ret := xs[0]
	for i := 1; i < len(xs); i++ {
		if xs[i] > ret {
			ret = xs[i]
		}
	}
	return ret
}

func main() {
	n := flag.Int("nodes", 5, "number of participating nodes")
	iters := flag.Int("iters", 100000, "number of iterations")
	debug := flag.Bool("debug", false, "print debug trace")

	flag.Parse()

	// 1. process i is in the doorway while choosing[i] == true
	// 2. process i is in the bakery from when it resets choosing[i] to false till
	// either it fails, or finishes its critical section.

	choosing := make([]bool, *n+1, *n+1) // one extra for the monitoring process
	numbers := make([]int, *n+1, *n+1)

	sharedMap := map[string]int{
		"last_updated_by": -1,
	}

	sharedSlice := make([]int, 0)

	lock := func(id int) {

		choosing[id] = true

		/* At the doorway */

		if *debug {
			fmt.Printf("%d: choosing\n", id)
		}

		numbers[id] = 1 + max(numbers)
		if *debug {
			fmt.Printf("%d: chose number %d\n", id, numbers[id])
		}

		choosing[id] = false

		/* Entered bakery */

		for k := 0; k <= *n; k++ {                              /* L1 */
			printed := false
			for choosing[k] {                                   /* L2 */
				// spin
				if *debug && !printed {
					fmt.Printf("%d: spinning for %d (waiting for it to choose: %v)\n",
						id, k, choosing)
					printed = true
				}
				// this is important, as tight spinning here would cause only
				// the first $n_core goroutines to be scheduled, starving
				// all others. this would in turn cause the whole algorithm
				// to stop making any progress.
				time.Sleep(10 * time.Millisecond)
			}
			printed = false
			for numbers[k] != 0 &&
				((numbers[k] < numbers[id]) ||
					(numbers[k] == numbers[id] && k < id)) {    /* L3 */
				// spin
				if *debug && !printed {
					fmt.Printf("%d: spinning for %d (waiting for it to finish CS: %v)\n",
						id, k, numbers)
					printed = true
				}
				time.Sleep(10 * time.Millisecond)
			}
		}
	}

	unlock := func(id int) {
		if *debug {
			fmt.Printf("%d: unlock: %v\n", id, numbers)
		}
		numbers[id] = 0
	}

	proc := func(id int, stop chan struct{}, ack chan struct{}) {
	out:
		for {
			select {
			case <-stop:
				break out

			default:

				lock(id)
				fmt.Printf("%d: entering critical section\n", id)

				// critical section
				sharedMap["last_updated_by"] = id
				sharedSlice = append(sharedSlice, id)
				sharedSlice = sharedSlice[1:]
				// end critical section

				fmt.Printf("%d: done critical section\n", id)
				unlock(id)
			}
		}
		ack <- struct{}{}
	}

	stops := make([]chan struct{}, 0)
	acks := make([]chan struct{}, 0)
	for i := 0; i < *n; i++ {
		c := make(chan struct{})
		d := make(chan struct{})
		stops = append(stops, c)
		acks = append(acks, d)
		go proc(i, c, d)
	}

	// Monitor and quit after some time

	for i := 1; i < *iters; i++ {
		lock(*n)
		if *debug {
			fmt.Sprintf("monitor lock acquired", sharedSlice)
		}
		if len(sharedSlice) > 1 {
			panic(fmt.Sprintf("found concurrent access with %v", sharedSlice))
		}
		// Go will panic when sharedMap is written to by two goroutines

		unlock(*n)
		if *debug {
			fmt.Sprintf("monitor lock released", sharedSlice)
		}
	}

	for _, stop := range stops {
		fmt.Println("stopping")
		stop <- struct{}{}
	}

	for _, ack := range acks {
		<-ack
	}

}

```


### Description

So we have `n` goroutines, and each wants to mutate a shared map (by updating
the single value in it) and a shared slice (by appending the process id to it,
and then reslicing it to maintain a length of 1). There is also the main
monitoring goroutine that checks if the shared slice ever contains more than
two items. Simultaneous mutation of a map by more than one goroutines is
detected by the Go runtime, which panics in such a case.

The key idea of the algorithm is that just like in an old fashioned bakery (or
a bank), each participant gets a token, or a number, roughly in the order of
arrival. Participants then get serviced in order of their token numbers. The
thing is that in our situation, there is no single receptionist to hand these
tokens over to participant processes. So, our solution is to have processes pick
their own numbers, and such a tie is broken by letting the process with a lower
id enter the critical section first.

The `lock` routine is the meat of the bakery algorithm. There are two shared
slices, `choosing` and `numbers`, and process `i` only writes to `choosing[i]`
and `numbers[i]`, but can read from any other indices in `choosing` and
`numbers`.


### Correctness

Our system with `N` processes (goroutines, here) functions such that at any
given time, at most one process is in the critical section. To prove this, let's
see the execution from process `i`'s perspective, and first define some terms:

- $t^{ik}_{L2}$: Time when process `i` completes the _last_ iteration of loop
`L2` for process `k`. This is when it sees `choosing[k] == false`.
- $t^{ik}_{L3}$: Time when process `i` completes the _last_ iteration of loop
`L3` for process `k`. This happens when process `i` sees a `0` in `numbers[k]`,
or if it thinks it should be serviced before process `k` owing to a lower token
number.
- $t^k_{d}$: Time at which process `k` completes `choosing[k] = true`.
- $t^k_{e}$: Time at which process `k` completes setting `choosing[k] = false`,
after choosing a number.

We can now make some observations:

- $t^k_d \lt t^k_e$.
- At time $t^k_e$, `numbers[k]` is completely written, and a read at or after this
point of `numbers[k]` will not return a partial result.
- At $t^{ik}_{L2}$, either process `k` is just out of the doorway (set
`choosing[k] = false`) and in the bakery (either waiting for other processes,
or executing its critical section); or is neither in the doorway or in the
bakery (maybe executing some non-critical section code). This corresponds to
either $t^{ik}_{L2} \gt t^k_e$, or $t^{ik}_{L2} \lt t^k_d$, respectively.

  * When $t^{ik}_{L2} \gt t^k_e$, we also have $t^{ik}_{L3} \gt t^k_e$. 
This means that process `i` found (at time $t^{ik}_{L3}$) either `numbers[i]
< numbers[k]`, or if both numbers are equal, that `i < k`. Note that `k`
_must have_ picked a number at least as large as `numbers[i]` in this case.

  * When $t^{ik}_{L2} \lt t^k_d$, it must be that `numbers[i] < numbers[k]`,
since when `k` does enter the doorway (after the moment $t^k_d$), it will
pick a number that is at least one larger than `numbers[i]`, which has
already been written completely.

Hence, in both these cases, process `i` does not wait for process `k`.
Generalizing this to all other processes `k` that a given process `i` needs to
share resources with, it can be seen that at most one process will be able to
execute its critical section.


### Failure

If a process fails after setting `choosing[k] = true`, and then keeps failing
and recovering, never resetting `choosing[k]`, a deadlock can be reached as
other processes will keep spinning, waiting on the failed process.


### Starvation because of spinning

If we do not yield to the runtime by calling `time.Sleep()` in every loop
iteration, only as many goroutines as the number of cores on our computer will
be able to run causing the algorithm to stop making any progress.


[1]: http://lamport.azurewebsites.net/pubs/bakery.pdf
