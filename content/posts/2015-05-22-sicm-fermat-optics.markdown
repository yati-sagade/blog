---
title: Deriving the laws of reflection and refraction of light from Fermat's principle
layout: post
date: 2015-05-22

---

[Fermat's principle][1] of least time can be roughly stated as, <em>"The path taken
between two points by a ray of light is the path that can be traversed in the
least time"</em> (From Wikipedia). Fermat used this observation to derive the
laws of reflection and refraction of light.



Reflection of light
-------------------
The law of reflection of light states that the angle at which a ray is incident
on a reflective surface is equal to the angle at which it is reflected from the
surface. In other words, in the following diagram (light travels from <span>$A$</span>
to <span>$O$</span> to <span>$B$</span>), <span>${\theta}_i = {\theta}_r$</span>.

<img src="/assets/reflection.svg" alt="reflection"
     width="50%"
     height="50%" />


Let's try to derive this law from Fermat's principle. The total distance that
the ray of light has to travel from <span>$A$</span> to <span>$B$</span> with
one reflection at <span>$O$</span> is
<div>$
L = \overline{AO} + \overline{OB}
$</div>
<div>$
= \sqrt{a^2 + x^2} + \sqrt{b^2 + {\left( l - x \right)}^2}
$</div>

Now since the speed of light is constant, minimizing the time taken by light to
take the path <span>$AOB$</span> is equivalent to minimizing the path itself.
To do this, we set <span>$\frac{dL}{dx} = 0$</span>.

<div>$
\frac{dL}{dx} = 0
$</div>

<div>$
\implies \frac{d}{dx} \left( \sqrt{a^2 + x^2} + \sqrt{b^2 + {\left( l - x \right)}^2} \right) = 0
$</div>

<div>$
\implies \frac{2x}{2\sqrt{a^2 + x^2}} +
         \frac{2 \left( l - x \right) \left( -1 \right)}{2\sqrt{b^2 + {\left( l - x \right)}^2}} = 0
$</div>

<div>$
\implies \frac{x}{\sqrt{a^2 + x^2}} =
         \frac{\left( l - x \right)}{\sqrt{b^2 + {\left( l - x \right)}^2}}
$</div>

<div>$
\implies \sin{ {\theta}_i } = \sin{ {\theta}_r }
$</div>

<div>$
\implies {\theta}_i = {\theta}_r \, \blacksquare
$</div>

<div>$
$</div>

Refraction
-----------

The law of refraction of light, or [Snell's Law][2] states that the ratio of
the sines of the angles of incidence and refraction is equal to the inverse
ratio of the indices of refraction of the two media.

<img src="/assets/refraction.svg" alt="refraction"
     width="50%"
     height="50%" />


With reference to the image above, Snell's Law can be mathematically stated as,

<div>$
\frac{\sin {\theta}_i }{\sin {\theta}_r } = \frac{n_2}{n_1}
$</div>


Now to prove this using Fermat's principle.

We know that,
<div>$
\text{index of refraction of a medium} = \frac{ \text{speed of light in vacuum} }{ \text{speed of light in the medium} }$</div>

Let the speeds of light in our media be <span>$v_1 = \frac{c}{n_1}$</span> and
<span>$v_2 = \frac{c}{n_2}$</span>. Now the total time taken by light to
travel from <span>$A$</span> to <span>$B$</span> with a refraction at
<span>$O$</span> is
<div>$ t = \frac{ \overline{AO} }{v_1} + \frac{ \overline{OB} }{v_2} $</div>
<div>$ = \frac{ \overline{AO} \times n_1  }{c} + \frac{ \overline{OB} \times n_2 }{c} $</div>
<div>$ = \frac{ n_1 \sqrt{ a^2 + x^2 } }{c} + \frac{ n_2 \sqrt{ b^2 + {\left( d - x \right) }^2 } }{c} $</div>


To minimize <span>$t$</span>, we'll set <span>$\frac{dt}{dx} = 0$</span>

<div>$ \frac{d}{dx} \left( \frac{ n_1 \sqrt{ a^2 + x^2 } }{c} + \frac{ n_2 \sqrt{ b^2 + {\left( d - x \right) }^2 } }{c} \right) = 0$</div>

<div>$
\implies \frac{1}{c} \frac{d}{dx} \left( { n_1 \sqrt{ a^2 + x^2 } } + { n_2 \sqrt{ b^2 + {\left( d - x \right) }^2 } } \right) = 0
$</div>

<div>$
\implies \frac{2 x n_1}{ 2 \sqrt{ a^2 + x^2 } } + \frac{ 2 \left( d - x \right) n_2 \left( -1 \right) }{ 2 \sqrt{ b^2 + {\left( d - x \right) }^2 } } = 0
$</div>

<div>$
\implies n_1 \frac{x}{ \sqrt{ a^2 + x^2 } } = n_2 \frac{ \left( d - x \right) }{ \sqrt{ b^2 + {\left( d - x \right) }^2 } } 
$</div>

<div>$
\implies n_1 \sin {\theta}_i = n_2 \sin {\theta}_r
$</div>

<div>$
\implies \frac{\sin {\theta}_i }{\sin {\theta}_r } = \frac{n_2}{n_1} \, \blacksquare
$</div>



[1]: http://en.wikipedia.org/wiki/Fermat's_principle
[2]: http://en.wikipedia.org/wiki/Snell's_law
