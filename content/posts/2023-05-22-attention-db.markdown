---
title: Attention - this value does not exist
date: 2023-04-30
summary: "Building a fuzzy, hallucinating key-value store using attention"
---
Here, we play with the attention mechanism and word embeddings to get make a KV
store that fuzzily searches through the key space, and might _also_ return
candidate values that are nonexistent in the store.

Suppose we have the following key/value pairs:

```
{
  'one': 'number',
  'cat': 'animal',
  'dog': 'animal',
  'ball': 'toy',
  'sphere': 'shape',
  'male': 'gender',
}
```

Here are some example queries and their results:

```
rhombus  ['shape' 'shaped' 'fit' 'fits' 'resembles']
parabola ['shape' 'shaped' 'fit' 'fits' 'resembles']
female   ['gender' 'ethnicity' 'orientation' 'racial' 'mainstreaming']
seven    ['number' 'numbers' 'ten' 'only' 'other']
seventy  ['gender' 'ethnicity' 'orientation' 'regardless' 'defining']
cylinder ['toy' 'instance' 'unlike' 'besides' 'newest']
```

So as we can see, the top result for `seven` is `number`, because `seven` is
similar to `one`. but there are also other results that are not in the dataset.

Then there is `seventy`, which should also have returned `number` as at least
one result, but it didn't. Somehow our store thinks `seventy` is closer to
`male` than to `one`.

## Answering queries with attention

### The interface

```python
# Init with a dict containing they key/value pairs.
db = Database({
  'key1': 'val1',
  'key2': 'val2,
})

# Query
results = db.query('foo')
assert type(results) == list
```
### Answering queries with attention

Consider a dataset D containing key-value pairs $D = \{(\textbf{k}_1, \textbf{v}_1), ..., (\textbf{k}_m, \textbf{v}_m)\}$.

Imagine a query mechanism that, given a query $\textbf{q}$, produces a result given by:

$$
Attention(\textbf{q}, D) = \sum_{i=1}^{m}\alpha(\textbf{q}, \textbf{k}_i) \textbf{v}_i
$$

Note:

* The weights $\alpha(\textbf{q}, \textbf{k}_i)$ are non-negative, and sum to 1.
* We can make this an exact key match retrieval by setting $\alpha(\textbf{q}, \textbf{k}_i)=1$ when $q=\textbf{k}_i$, and $0$ otherwise.
* We can get average pooling OTOH if we set $\alpha(\textbf{q}, \textbf{k}_i)=\frac{1}{m}$.

### Implementation

Our DB interface uses variable length words, but the attention mechanism wants
fixed-length vectors. While we could use a simple one-hot encoding of words, it
won't capture the semantic closeness of words.

Instead, we'll use the [GloVe](https://nlp.stanford.edu/projects/glove/)
embeddings, that allow us to represent variable length words with their fixed
size embeddings.

Sketch:

* For each k, v in the records dict, create embeddings for k and v and put them in separate tensors, called keys and values.
  - keys and values both have a shape of `(len(records), embed_size)`
* Given a query,
  - Create its embedding into a vector `q_embed` of shape `(embed_size,)`
  - compute `w = softmax(keys.mul(q_embed))` to get a `(len(records),)` shaped vector of attention weights.
  - Compute the attention as `sum(w .* values)` to get a weighted sum of values in a `(n_embed,)` vector.
  - Reverse the weighted-sum vector thus obtained into candidate words by searching the embedding space for nearby words.

Runnable code in https://colab.research.google.com/drive/1ReE-WIEzAGNr1a-6TUHsQucwtgWFhuTF?usp=sharing