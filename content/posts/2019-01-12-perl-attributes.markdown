---
date: 2019-01-12

layout: post

title: Tagging functions with attributes in Perl

---

Suppose we have a Perl module that allows us to query a set of business objects
(for example, purchases made on our website). The API of the module looks
something like:

```perl

    my $collection = Purchase::Collection->new();

    my @purchases_2018 = $collection
                           ->date_after('2017-12-31')
                           ->date_before('2019-01-01')
                           ->region(['EU', 'US'])
                           ->revenue_collected(1)
                           ->with_amount({ '>', 1000 })
                         ->fetch();
```

So all the selector methods like `date_after` or `revenue_collected` update
internal filter state of the collection object, and all these filters are
applied only at the end with the `fetch()`.

Now suppose we are writing a command line interface to this module, which we
might want to look something like:

```bash
    
    $ find-purchases \
        --date-after=2017-12-31\
        --date-before=2019-01-01\
        --region=EU --region=US\
        --revenue-collected\
        --with-amount='>1000'
    
```

Notice that the filter methods all take different kinds of arguments --
`date_after` makes sense only with one date, whereas `region` can work with
multiple region codes. Also, `revenue_collected` is a boolean flag.

The Perl `GetOpt::Long` module allows us to specify this interface quite easily,
and we could just go over all the filter methods in `Purchase::Collection` and
manually create declarations for the corresponding options. But what if we
wanted to automatically collect this information within `Purchase::Collection`
itself? One approach could be to module level hash:

```perl

    package Purchase::Collection;
    ...
    my %all_filters;

    sub all_filters { %all_filters }

    sub mkfilter {
      my ( $name, $args_spec ) = @_;
      $all_filters{$name} = $args_spec;
    }

    ...

    sub date_after {
      my ( $self, $date ) = @_;
      ...
      return $self; # for chaining
    }
    mkfilter( date_after => 's' ); # declare date_after takes a single string

    ...

    sub region {
      my ( $self, $regions ) = @_;
      ...
      return $self;
    }
    mkfilter( region => 's@' ); # declare region takes multiple strings
    ...

```

The CLI code can then do something like:

```perl

    use GetOpt::Long;
    use Purchase::Collection;

    my %filter_spec = Purchase::Collection::all_filters();
    my $opts;
    GetOpt::Long($opts,
      %filter_spec,
      ...
    );

```

Note that we don't need any extra translation as we reuse the specifiers that
`GetOpt::Long` uses.

This is a fine approach, and one way attributes can be used to get rid of the
`mkfilter` calls after each sub definition is as follows:

```perl
    use B qw(svref_2object);
    no warnings 'reserved';

    my %all_filters;

    # called at compile time for each sub
    sub MODIFY_CODE_ATTRIBUTES {
      my ($pkg, $coderef, @attributes) = @_;

      # any unidentified attributes need to be returned so Perl can fail
      # compilation
      my @disallowed;

      my $argtype;

      for my $attr ( @attributes ) {
        if ( $attr =~ /^filter\(
                            (
                             [siof]
                             [@%]?
                            )
                       \)$/x ) {
          $argtype = $1;
        } else {
          push @disallowed, $attr;
        }
      }
      my $sub_name = svref_2object($coderef)->GV->NAME;

      $all_filters{$sub_name} = $argtype if $argtype;

      return @disallowed;
    }

    ...

    sub date_after :filter(s) {
      my ( $self, $date ) = @_;
      ...
      return $self; # for chaining
    }

    ...

    sub region :filter(s@) {
      my ( $self, $regions ) = @_;
      ...
      return $self;
    }
    
    ...
    sub fetch { # not a filter, so not tagged
      ...
    }
```

How attributes work is described very nicely [in this
post](https://www.perl.com/article/untangling-subroutine-attributes/). Here, we
"tag" each filter method with a `:filter(...)` attribute. Perl will pass all
such attributes as an array of strings to `__PACKAGE__->MODIFY_CODE_ATTRIBUTES`,
which is called _at compile time_ for each sub. There, we are free to do what we
want with the attribute strings. In our case, we simply update our
`%all_filters` map. But we can easily imagine uses like wrapping functions with
custom code.

Note that in Python, functions are also objects, so you can trivially add a new
attribute to a function using a decorator. With Perl, while subroutine
references (CODE refs) can be blessed, subs themselves cannot have arbitrary
object like hash storage.

