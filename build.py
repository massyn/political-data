import os
import logging
import jinja2
import markdown
from data import Data

def render_jinja(template,output,**KW):
    os.makedirs(os.path.dirname(output),exist_ok = True)
    template_dir = 'templates'
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    tmpl = env.get_template(template)
    result = tmpl.render(**KW)
    print(f"Writing {output}")
    with open(output,'wt',encoding='utf-8') as q:
        q.write(result)

def render_markdown_page(md_file, output_file, page_id, page_title):
    """Read markdown file, convert to HTML, and render using page template"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables'])

    # Render using the page template
    render_jinja('page.jinja', output_file,
                 content=html_content,
                 page_id=page_id,
                 page_title=page_title)

def main(target):
    D = Data()
    os.makedirs(target,exist_ok=True)

    # Render the static markdown pages
    render_markdown_page('pages/about.md', f'{target}/about.html', 'about', 'About')

    # Render the index page
    render_jinja('index.jinja', f'{target}/index.html', jurisdictions = D.jurisdictions())

    for j in D.jurisdictions():
        render_jinja('jurisdiction.jinja', f'{target}/{j.lower()}.html', jurisdiction = j, indicators = D.indicators(j))

        for i in D.indicators(j):
            res = D.result(j,i['id'],is_latest=False)

            # Check if any graph has an overlay_metric and fetch that data
            overlay_data = {}
            if res['indicator'].get('graph') and res['indicator']['graph'] != False:
                for graph_config in res['indicator']['graph']:
                    if 'overlay_metric' in graph_config:
                        overlay_id = graph_config['overlay_metric']
                        if overlay_id not in overlay_data:
                            overlay_data[overlay_id] = D.result(j, overlay_id, is_latest=False)

            render_jinja('indicator.jinja', f"{target}/{j.lower()}_{i['id'].lower()}.html",
                        jurisdiction = j, indicator = res, overlay_data = overlay_data)

if __name__ == '__main__':
    main('./dist')