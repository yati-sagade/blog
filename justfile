default_editor := "vim"

write NAME:
  #!/usr/bin/env bash
  ${EDITOR:-{{default_editor}}} "content/posts/$(date -I)-{{NAME}}.markdown"

build-with-drafts:
  #!/usr/bin/env bash
  python generate.py --include-drafts --site-directory=./site --copy-static=./static/images .

publish: build
  #!/usr/bin/env bash
  git add content site
  git commit -m 'yay new stuff'
  git push origin main
