import os
import sys
import subprocess
import argparse
import shutil
from jinja2 import Environment, FileSystemLoader
import frontmatter
import tempfile

BLOG_TITLE = 'Explog'

parser = argparse.ArgumentParser(description='Generate a blog site.')
parser.add_argument('directory', help='The directory containing the blog files.')
parser.add_argument('--site-directory',
                    type=str,
                    default=None,
                    help='Output directory. Created if does not exist, wiped clean if it does.')
parser.add_argument('--include-drafts',
                    action='store_true',
                    help='Also render draft posts')
args = parser.parse_args()


def render_template(template_path, context):
  env = Environment(loader=FileSystemLoader('templates'))
  template = env.get_template(template_path)
  rendered_template = template.render(context)
  return rendered_template


def convert_file_with_pandoc(input_path, output_path):
  command = f"pandoc -f markdown -t html --standalone --mathml {input_path} -o {output_path}"
  print(f'Running {command}')
  result = subprocess.run(command, shell=True, capture_output=True, text=True)
  print(result.stdout)
  print(result.stderr)
  return output_path

if __name__ == '__main__':
  directory = args.directory
  site_directory = os.path.join(directory, 'site')
  if (d:=args.site_directory) is not None:
    site_directory = d
  if os.path.exists(site_directory):
    shutil.rmtree(site_directory)
  os.makedirs(site_directory, exist_ok=True)

  # Keep track of posts to render the index page.
  posts = []
  for filename in os.listdir(directory):
    if filename.endswith(".md") or filename.endswith(".markdown"):
      print(f"--- Processing {filename}...")
      path = os.path.join(directory, filename)
      outputname = os.path.splitext(os.path.basename(filename))[0] + ".html"
      # Load post details before converting.
      with open(path, 'r') as f:
        post = frontmatter.load(f)
        if post.get('draft', False) and not args.include_drafts:
          print(f'Skipping draft post {filename} as --include-drafts is not given.')
          continue
        post_dict = {key: post[key] for key in ['title', 'date', 'tags'] if key in post}
        post_dict['snippet'] = post.content[:100] + '...'
        post_dict['link'] = outputname
        posts.append(post_dict)
      # Convert
      outputpath = os.path.join(site_directory, outputname)
      convert_file_with_pandoc(path, outputpath)
      print(f"{filename} converted to {outputname}.")
      outputname = os.path.splitext(filename)[0] + ".html"
      print(f"---")

  # Now render the index.
  index_tmpl = 'index.html'
  context = {
    'blog_title': BLOG_TITLE,
    'posts': sorted(posts, key=lambda p: p.get('date', '1960-01-01'), reverse=True),
  }
  with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
    rendered_html = render_template(index_tmpl, context)
    fp.write(rendered_html.encode('utf-8'))
    fp.close()
    convert_file_with_pandoc(fp.name, os.path.join(site_directory, 'index.html'))
