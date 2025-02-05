Setup a virtual env and install deps:

```bash
$ python -mvenv ~/.virtualenvs/blog
$ . ~/.virtualenvs/blog/bin/activate
$ pip install --upgrade -r requirements.txt

Build the site in ./site:

```bash
$ just build
```

Build with drafts:

```bash
$ just build-with-drafts
```

Build and publish:

```bash
$ just publish
```

### Hosting

Currently hosting this on Cloudflare pages:

- explog.pages.dev
- pulls branch:main of github.com/yati-sagade/blog
- installs the entire `site/` directory as the website (index.html is the default entry point)



