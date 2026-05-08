import sys
import re
import os
import webbrowser

def parse_inline(text):
    # bold italic combined
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # links with image
    text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', text)
    # links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    # strikethrough
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
    return text

def convert(md):
    lines = md.split('\n')
    html = []
    in_ul = False
    in_ol = False
    in_code = False
    in_table = False
    code_lang = ''
    code_lines = []
    table_rows = []

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul:
            html.append('</ul>')
            in_ul = False
        if in_ol:
            html.append('</ol>')
            in_ol = False

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            t = '<table><thead><tr>'
            headers = [h.strip() for h in table_rows[0].split('|') if h.strip()]
            for h in headers:
                t += f'<th>{parse_inline(h)}</th>'
            t += '</tr></thead><tbody>'
            for row in table_rows[2:]:
                cells = [c.strip() for c in row.split('|') if c.strip()]
                t += '<tr>'
                for c in cells:
                    t += f'<td>{parse_inline(c)}</td>'
                t += '</tr>'
            t += '</tbody></table>'
            html.append(t)
            table_rows = []
            in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.startswith('```'):
            if in_code:
                lang_class = f' class="language-{code_lang}"' if code_lang else ''
                html.append(f'<pre><code{lang_class}>' + '\n'.join(code_lines) + '</code></pre>')
                code_lines = []
                code_lang = ''
                in_code = False
            else:
                close_list()
                close_table()
                code_lang = line[3:].strip()
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue

        # table detection
        if '|' in line:
            close_list()
            in_table = True
            table_rows.append(line)
            i += 1
            continue
        else:
            close_table()

        # close lists on non-list lines
        if not line.startswith('- ') and not re.match(r'^\d+\. ', line):
            close_list()

        # headings
        if re.match(r'^#{1,6} ', line):
            level = len(line) - len(line.lstrip('#'))
            text = parse_inline(line[level:].strip())
            anchor = re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))
            html.append(f'<h{level} id="{anchor}">{text}</h{level}>')

        # horizontal rule
        elif re.match(r'^(-{3,}|\*{3,}|_{3,})$', line.strip()):
            html.append('<hr>')

        # blockquote
        elif line.startswith('> '):
            close_list()
            html.append(f'<blockquote><p>{parse_inline(line[2:])}</p></blockquote>')

        # unordered list
        elif line.startswith('- ') or line.startswith('* '):
            if not in_ul:
                html.append('<ul>')
                in_ul = True
            checked = ''
            content = line[2:]
            if content.startswith('[ ] '):
                checked = '☐ '
                content = content[4:]
            elif content.startswith('[x] ') or content.startswith('[X] '):
                checked = '☑ '
                content = content[4:]
            html.append(f'<li>{checked}{parse_inline(content)}</li>')

        # ordered list
        elif re.match(r'^\d+\. ', line):
            if not in_ol:
                html.append('<ol>')
                in_ol = True
            content = re.sub(r'^\d+\. ', '', line)
            html.append(f'<li>{parse_inline(content)}</li>')

        # empty line
        elif line.strip() == '':
            html.append('')

        # paragraph
        else:
            html.append(f'<p>{parse_inline(line)}</p>')

        i += 1

    close_list()
    close_table()
    return '\n'.join(html)

def build_toc(md):
    toc = ['<div class="toc"><h3>📋 Contents</h3><ul>']
    for line in md.split('\n'):
        m = re.match(r'^(#{1,3}) (.+)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            anchor = re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))
            indent = (level - 1) * 20
            toc.append(f'<li style="margin-left:{indent}px"><a href="#{anchor}">{text}</a></li>')
    toc.append('</ul></div>')
    return '\n'.join(toc)

def wrap_html(title, body, toc):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0d1117;
      color: #e6edf3;
      line-height: 1.8;
      padding: 40px 20px;
    }}

    .layout {{
      display: flex;
      gap: 40px;
      max-width: 1100px;
      margin: 0 auto;
    }}

    .toc {{
      position: sticky;
      top: 40px;
      width: 220px;
      flex-shrink: 0;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 10px;
      padding: 16px;
      height: fit-content;
      font-size: 13px;
    }}

    .toc h3 {{
      color: #58a6ff;
      border: none;
      font-size: 14px;
      margin-bottom: 10px;
    }}

    .toc ul {{ list-style: none; padding: 0; }}
    .toc li {{ margin: 6px 0; }}
    .toc a {{ color: #8b949e; text-decoration: none; }}
    .toc a:hover {{ color: #58a6ff; }}

    .content {{ flex: 1; min-width: 0; }}

    h1, h2, h3, h4, h5, h6 {{
      color: #58a6ff;
      margin: 28px 0 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid #21262d;
    }}

    h1 {{ font-size: 2rem; color: #79c0ff; }}
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.2rem; color: #56d364; }}

    p {{ margin: 12px 0; color: #cdd9e5; }}

    a {{ color: #58a6ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    strong {{ color: #ffa657; }}
    em {{ color: #cba6f7; font-style: italic; }}
    del {{ color: #8b949e; }}

    code {{
      background: #1c2128;
      color: #f8c555;
      padding: 2px 8px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
      font-size: 0.875em;
    }}

    pre {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 10px;
      padding: 20px;
      overflow-x: auto;
      margin: 16px 0;
      position: relative;
    }}

    pre code {{
      background: none;
      padding: 0;
      color: #e6edf3;
      font-size: 0.9em;
      line-height: 1.6;
    }}

    blockquote {{
      border-left: 4px solid #3fb950;
      background: #161b22;
      margin: 16px 0;
      padding: 12px 20px;
      border-radius: 0 8px 8px 0;
      color: #8b949e;
    }}

    blockquote p {{ color: #8b949e; margin: 0; }}

    ul, ol {{
      padding-left: 28px;
      margin: 12px 0;
      color: #cdd9e5;
    }}

    li {{ margin: 6px 0; }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 14px;
    }}

    th {{
      background: #161b22;
      color: #58a6ff;
      padding: 10px 14px;
      border: 1px solid #30363d;
      text-align: left;
    }}

    td {{
      padding: 10px 14px;
      border: 1px solid #21262d;
      color: #cdd9e5;
    }}

    tr:nth-child(even) {{ background: #0d1117; }}
    tr:nth-child(odd) {{ background: #161b22; }}
    tr:hover {{ background: #1c2128; }}

    hr {{
      border: none;
      border-top: 1px solid #30363d;
      margin: 28px 0;
    }}

    img {{
      max-width: 100%;
      border-radius: 8px;
      margin: 12px 0;
    }}

    .badge {{
      display: inline-block;
      background: #238636;
      color: #fff;
      padding: 2px 10px;
      border-radius: 20px;
      font-size: 12px;
      margin: 2px;
    }}

    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0d1117; }}
    ::-webkit-scrollbar-thumb {{ background: #30363d; border-radius: 3px; }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>{toc}</aside>
    <main class="content">{body}</main>
  </div>
</body>
</html>"""

def main():
    if len(sys.argv) < 2:
        print("\n  \033[91musage: python converter.py input.md\033[0m")
        print("  \033[90mexample: python converter.py README.md\033[0m\n")
        return

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"\n  \033[91merror: '{input_file}' not found\033[0m\n")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        md = f.read()

    title = os.path.splitext(os.path.basename(input_file))[0]
    body = convert(md)
    toc = build_toc(md)
    output = wrap_html(title, body, toc)

    output_file = os.path.splitext(input_file)[0] + '.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\n  \033[92m✅ converted: {input_file} → {output_file}\033[0m")
    print(f"  \033[90mOpening in browser...\033[0m\n")
    webbrowser.open(f'file:///{os.path.abspath(output_file)}')

if __name__ == "__main__":
    main()