---
date: 2018-01-28
layout: post
title: Summary of "ImageNet Classification with Deep Convolutional Neural Networks"
tags: [deep-learning]
---

I decided to read interesting deep learning papers often and try to summarize
them to aid my own understanding of the topics.

This paper, [ImageNet Classification with Deep Convolutional Neural Networks][1]
demonstrates a record breaking result on the ImageNet LSVRC-2012 competition.
The authors participated in the competition under the name [SuperVision][2] (which is
extremently difficult to Google, especially in the "deep learning" context, which 
makes Google surface supervised learning related results).

## Data

They trained the model on the ImageNet dataset, which contains about 1.2 million
images of 1000 categories.

### Image preprocessing

Since ImageNet images are variable resolution, and the model presented in this
paper requires fixed size images, they scaled every image to 256x256 pixels. The
scaling like so:

1. Scale a possibly rectangular image so that the shorter side is 256 pixels.
2. Take the middle 256x256 patch as the input image.

### Data augmentation

Actually, the network presented in the paper works with 224x224 images, which
are generated by randomly sampling patches of that size from each 256x256 image.
This is one of the ways they did data augmentation.

The other way they augmented the dataset involved perturbing the R,G,B values of
each input image by a scaled version of the principal components (in RGB space)
across the whole training set. If $\mathbf{p_1}$, $\mathbf{p_2}$ and
$\mathbf{p_3}$ be the eigenvectors and $\lambda_1$, $\lambda_2$, $\lambda_3$ the
corresponding eigenvalues, each pixel in a given image is perturbed such that:

<!-- TODO: Does not render in KaTeX on Hugo, but works in MathJax/Jekyll -->
$$
\begin{align}

I' &= I + \begin{bmatrix}
        \leftarrow \mathbf{p_1}^T \rightarrow \\
        \leftarrow \mathbf{p_2}^T \rightarrow \\
        \leftarrow \mathbf{p_3}^T \rightarrow \\
      \end{bmatrix}

      \begin{bmatrix}
        \alpha_1 \lambda_1 \\
        \alpha_2 \lambda_2 \\
        \alpha_3 \lambda_3
      \end{bmatrix}

\end{align}
$$

where each $\alpha_1$ is picked from a Gaussian with 0 mean and 0.1 std every
time an image is used for training (but the values are shared by all pixels in
the image once picked). They claim this captured an invariance of object
identity under changes in intensity and color of illumination, which seems to
have accounted for a ~ 1% decrease in top-1 error rate.

## Model architecture

The model has 5 convolutional layers and 3 fully-connected layers.

<img src="/assets/imagenet-cnn-model.png"
     alt="image showing the convolutional network architecture, picked from the paper" />


### Choice of nonlinearity

Authors chose the ReLU function (`ReLU(x) = max(0,x)`) and were I think one of
the first to endorse it, and for good reasons. They saw that using the ReLU
activation function, as opposed to the conventional tanh or sigmoid, yielded
tremendous gains in training speed, owing to the non saturating nature of the
function. When pitted against the tanh activation with no other changes, they
were able to train their model to 25% error rate on the training set _6 times
faster_ with the ReLU activation.

### Pooling

They use max pooling but with overlapping windows (filter size of 3 and stride
of 2). Max pooling is applied after response renormalization, described next.


### Local response renormalization

Activations from a given filter/kernel for a given location $\left(x,y\right)$
are scaled by a term involving the activations on $n$ adjacent kernels for the
same location. $n$ and other terms in question are hyperparameters and described
very well in the corresponding section in the paper. The inspiration seems to be
biological in nature, and in effect causes filters in an $n$ group to "compete"
for having larger activations. Of course they probably wouldn't have kept it had
it not given them a significant error rate reduction on their validation set
(which it did).


### Dropout, momentum and weight decay

Dropout is used in the first two fully-connected layers (layers 6 and 7 in the
overall network). Essentially, a given neuron is switched-off in
a forward-backward cycle with probability `0.5`. This means that the model is
forced to learn redundant representations with shared weights. During testing,
they do not switch of neurons, but multiply their outputs by `0.5`. No one quite
knows exactly why dropout works well, but indeed it has worked extremely well
for the authors and for many other models that followed. It has become very
commonplace today to incorporate dropout in FC layers to reduce overfitting.
Dropout approximately doubled the training time.

Momentum is a technique to speed up training by pushing batch gradient descent
updates to move towards the optimum faster. This is especially important when
the objective function is like a long ravine leading to the optimum with steep
wells (or like a hammock with a heavy person inside, but in higher dimensions).

<img src="/assets/ravine.png"
     alt="contours of an objective function which looks like a hammock" />

In such an objective, plain batch gradient descent, if starting on the left
side, will oscillate up and down, moving slowly towards the optimum. Momentum
uses exponentially weighted averages to take into account previous gradient
descent updates. This averaging has an effect of cancelling out the up and down
oscillations, thus speeding up the learning significantly. Authors use
a momentum parameter of $0.9$, which roughly keeps the past 10 values in the
moving average memory.

Weight decay is simply to scale down weights by a factor slightly less than 1 to
prevent them from becoming too big. This can be seen as a regularizing
technique. In all the gradient descent updates for the model weights look like
the following:

$$
v \leftarrow 0.9 v - 0.0005.\epsilon.w  - \epsilon\frac{\partial L}{\partial w} \\
w \leftarrow w + v
$$

## Training

The training is done on two GPUs for parallelism, and the setup is quite
interesting. The GPUs used each have 3GB memory. The network is split into
halves, as can be seen in the model description figure, across the two GPUs. The
interesting bit is that while layer 4 (CONV) operates on input which comes from
the layer 3 activations from _both_ GPUs, other conv layers in the network do
not have this cross GPU communication going on, and only work with activations
from the GPU local half of the network.

Selecting how many layers should have cross-GPU comms going on is a problem for
cross-validation, and apparently this scheme seems to have worked well for them.
In the following figure, we see the first conv layer weights visualized, the top
half being the first GPU, and the bottom half the other. As the authors mention
in the paper, the two halves of the network consistently specialized in
features, with one focusing on frequency/orientation, and the other in coloured
blob detection.

<img src="/assets/gpu-specific-learning.png"
     alt="the first conv layer learned representations in both GPUs" />

Because of the sheer number of parameters (60 million), the training still takes
5-6 days. The learning rate had to be manually decayed when progress plateaued.

## Conclusion

This work was the first of its kind to have trained deep convolutional networks
on GPUs to achieve impressive results on the ImageNet dataset for object
detection. To conclude, here's a Google Trends visualization for the term "deep
learning" over time:

<script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/1294_RC01/embed_loader.js"></script>
<script type="text/javascript">
trends.embed.renderExploreWidget("TIMESERIES", {"comparisonItem":[{"keyword":"deep learning","geo":"","time":"2004-01-01 2018-01-28"}],"category":0,"property":""}, {"exploreQuery":"date=all&q=deep%20learning","guestPath":"https://trends.google.com:443/trends/embed/"});
</script>

(the paper was presented in December 2012 at NIPS).

[1]: http://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf
[2]: http://image-net.org/challenges/LSVRC/2012/results.html
