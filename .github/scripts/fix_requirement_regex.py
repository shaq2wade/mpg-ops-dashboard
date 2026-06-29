from pathlib import Path
import json
import re

path = Path('monarch-ops-dashboard.html')
text = path.read_text(encoding='utf-8')
m = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', text, re.S)
if not m:
    raise SystemExit('template bundle not found')

data = json.loads(m.group(2))
entry = data['entry']
page = data['pages'][entry]

bad = 'rs.split(/\n+/)'
fixed = 'rs.split(/\\n+/)'
if bad not in page:
    raise SystemExit('bad regex pattern not found')
page = page.replace(bad, fixed, 1)

# Validate the bundled page still contains the requirement fields.
for marker in ['Requirement Details', 'File/link', 'Query raised']:
    if marker not in page:
        raise SystemExit('missing marker: ' + marker)

data['pages'][entry] = page
new_template = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
# Roundtrip validation and no raw </script> in the embedded JSON.
json.loads(new_template)
if '</script>' in new_template.lower():
    raise SystemExit('unsafe script close marker in template')

text = text[:m.start(2)] + new_template + text[m.end(2):]
json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
path.write_text(text, encoding='utf-8')
