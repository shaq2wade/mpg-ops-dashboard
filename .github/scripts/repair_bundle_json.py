from pathlib import Path
import json

path = Path('monarch-ops-dashboard.html')
text = path.read_text(encoding='utf-8')
open_tag = '<script type="__bundler/template">'
start = text.index(open_tag) + len(open_tag)
end = text.index('</script>', start)
content = text[start:end]


def escape_controls_in_strings(s):
    out = []
    in_str = False
    esc = False
    for ch in s:
        if in_str:
            if esc:
                out.append(ch)
                esc = False
            elif ch == '\\':
                out.append(ch)
                esc = True
            elif ch == '"':
                out.append(ch)
                in_str = False
            elif ch == '\n':
                out.append('\\n')
            elif ch == '\r':
                out.append('\\r')
            elif ch == '\t':
                out.append('\\t')
            elif ord(ch) < 32:
                out.append('\\u%04x' % ord(ch))
            else:
                out.append(ch)
        else:
            out.append(ch)
            if ch == '"':
                in_str = True
    return ''.join(out)

fixed = escape_controls_in_strings(content)
parsed = json.loads(fixed)
page = parsed['pages'][parsed['entry']]
for marker in ['LOCAL_KEY', 'saveLocalData', 'loadLocalData']:
    if marker not in page:
        raise SystemExit(f'missing marker after repair: {marker}')

text = text[:start] + fixed + text[end:]
path.write_text(text, encoding='utf-8')
