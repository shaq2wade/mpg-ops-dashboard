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

if 'ensureInsuranceTask(data)' in page:
    raise SystemExit('migration already applied')

insurance_method = """
  insuranceTask() {
    return {id:30,name:'Insurance',status:'ns',priority:'hi',due:'',owner:'',note:'Information request',reqs:[
      {text:'Current Policy Schedules - required to assess current coverage.',done:false},
      {text:'Last year renewal submission - proposal forms, sum insured calculation sheets and fleet values to understand values.',done:false},
      {text:'Last year renewal report - understand the renewal strategy adopted last year.',done:false},
      {text:'Example contracts - assess assumption of risk for services provided under each business.',done:false},
      {text:'Staff Information - understand numbers and seasonal fluctuations, plus details on health cover provided so options can be assessed.',done:false},
    ],comments:[],completedAt:null};
  }
  ensureInsuranceTask(data) {
    const finance = data.sections.find(s => s.key === 'finance') || data.sections[0];
    if (!finance || finance.tasks.some(t => t.name === 'Insurance')) return;
    const idx = finance.tasks.findIndex(t => t.id === 8 || t.name.indexOf('Fixed Asset Register') === 0);
    const task = this.insuranceTask();
    if (idx >= 0) finance.tasks.splice(idx, 0, task); else finance.tasks.push(task);
  }"""

old = """  normalizeData(data) {
    if (!data || !data.sections) return data;
    data.sections.forEach(s => s.tasks.forEach(t => {"""
new = insurance_method + """
  normalizeData(data) {
    if (!data || !data.sections) return data;
    this.ensureInsuranceTask(data);
    data.sections.forEach(s => s.tasks.forEach(t => {"""
if old not in page:
    raise SystemExit('normalizeData start not found')
page = page.replace(old, new, 1)

data['pages'][entry] = page
new_template = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
pg = json.loads(new_template)['pages'][entry]
for marker in ['ensureInsuranceTask(data)', 'insuranceTask()', 'Current Policy Schedules']:
    if marker not in pg:
        raise SystemExit('missing marker ' + marker)
text = text[:m.start(2)] + new_template + text[m.end(2):]
json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
path.write_text(text, encoding='utf-8')
