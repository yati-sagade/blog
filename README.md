Generate with the following run 

```
$ git clone https://github.com/yati-sagade/blog
$ cd blog
$ python -mvenv ~/.virtualenvs/blog
$ . ~/.virtualenvs/blog/bin/activate
(blog) $ pip install --upgrade jinja2 python-frontmatter
(blog) $ python generate.py --site-directory=./site .
# To include drafts for development, say --include-drafts.
``


