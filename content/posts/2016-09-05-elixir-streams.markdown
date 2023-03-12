---
date: 2016-09-05

layout: post

title: Baby steps with Elixir -- Wordcount

---
Implementing (useful subsets of) basic Unix utilities is a great way to learn
a programming language. On my quest to read a file one line at a time in Elixir,
I decided to try implementing `wc`. The interface:
    
    $ elixir wc.exs <filename>
     <line-count> <word-count> <char-count> <filename>

The code follows. Most of it is self-explanatory with the comments, but
I struggled with the `Stream.transform/3` function, so I'll try to explain what
it does later.

```elixir
## wc.exs
defmodule WordCount do

  def wordcount(filename) do
    path = Path.expand(filename)
    File.stream!(path)
    # By default, File.stream! streams lines.
    |> Stream.transform(nil, fn(line, _) -> {[wordcount_for_line(line)], nil} end)
    # At this point, each item in the stream is a map with counts for every
    # line.
    |> Enum.reduce(%{ words: 0, lines: 0, chars: 0 }, fn(count_map, acc) ->
        Map.merge(count_map, acc, fn(_k, v1, v2) -> v1 + v2 end)
       end)
  end

  defp wordcount_for_line(line) do
    with num_words = line
                     |> String.trim
                     |> String.split(~r/\s+/)
                     |> Enum.filter(&(String.length(&1) > 0))
                     |> length,
         num_lines = 1, # Of course the line-count for a line is 1! :)
         num_chars = String.length(line) do
      %{ words: num_words, lines: num_lines, chars: num_chars }
    end
  end

  defp print_result(%{ words: words, lines: lines, chars: chars }, filename) do
    IO.puts " #{lines} #{words} #{chars} #{filename}"
  end

  defp usage, do: "Give me a filename please."

  def main([]) do
    raise usage
  end

  def main([ filename | _ ]) do
    wordcount(filename) |> print_result(filename)
  end

end

WordCount.main(System.argv)
```

Let's wordcount ourselves:
    
    $ elixir wc.exs wc.exs
     37 123 1014 wc.exs

## Streams and files
Streams are Elixir's lazy collection abstraction, allowing one to _describe_
computations on a potentially unbounded (in size) data-source. These
computations are run when the result is explicitly requested, either by
functions like `Stream.run` or by trying to enumerate a stream, since streams
implement the enumerable protocol (which by the way just means that we can
iterate the stream one item at a time).

In its most basic invocation like on line 5, `File.stream!` takes a `Path` and
returns a `File.Stream` that streams the target file (if it exists) one line at
a time.

On to the next line in the call to `Stream.transform/3`: The first argument
(here `nil`) is the initial value of the accumulator variable. This is used to
hold state for successive calls to the reducer function. Next up is
the "reducer" function, which is called for every item in the stream, along with
the current accumulator. `Stream.transform/3` expects us to return a 2-tuple
with a *list of items* as the first element, and the new value of the
accumulator as the second element. It is important to note that we can, for one
item in the original stream, emit more than one items in the "transformed"
stream, and hence the first element of the returned two tuple must usually be
a list. For example, if a stream represents the number of photons detected in
a photomultiplier at each discrete time-step, like `[2, 1, 6, 9, 0, 1]`, and
we want to output a stream of `"p"`s consistent with the counts of photons in
the incoming stream, we would do something like:

```elixir
photon_counts
|> Stream.transform(nil, fn(count, _) ->
    {Stream.repeatedly(fn -> "p" end) |> Enum.take(count), nil}
end)
|> Enum.to_list
# ["p", "p", "p", "p", "p", "p", "p", "p", "p", "p", "p", "p", "p", "p",
#  "p", "p", "p", "p", "p"]

# ^^- 19 "p"s
```

Note that we are not using the accumulator at all in both these examples. We
just initialize it to `nil`, and keep sending `nil` as the "updated" accumulator
value, which is ignored anyway by our reducer function.

