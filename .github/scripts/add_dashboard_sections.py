import json
import re
from pathlib import Path

path = Path('monarch-ops-dashboard.html')
text = path.read_text(encoding='utf-8')
m = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', text, re.S)
if not m:
    raise SystemExit('template not found')

data = json.loads(m.group(2))
entry = data['entry']
page = data['pages'][entry]

insurance_task = """        {id:30,name:'Insurance',status:'ns',priority:'hi',due:'',owner:'',note:'Information request',reqs:[
          {text:'Current Policy Schedules - required to assess current coverage.',done:false,owner:'',source:'broker / insurer',status:'requested',due:'',note:'',link:''},
          {text:'Last year renewal submission - proposal forms, sum insured calculation sheets and fleet values to understand values.',done:false,owner:'',source:'broker / finance',status:'requested',due:'',note:'',link:''},
          {text:'Last year renewal report - understand the renewal strategy adopted last year.',done:false,owner:'',source:'broker',status:'requested',due:'',note:'',link:''},
          {text:'Example contracts - assess assumption of risk for services provided under each business.',done:false,owner:'',source:'legal / operations',status:'requested',due:'',note:'',link:''},
          {text:'Staff Information - understand numbers and seasonal fluctuations, plus details on health cover provided so options can be assessed.',done:false,owner:'',source:'HR',status:'requested',due:'',note:'',link:''},
        ],comments:[],completedAt:null},
"""

sections = [
    ("insurance-risk", "Insurance & Risk", "#C0392B", [
        insurance_task,
        "        {id:101,name:'Claims register',status:'ns',priority:'',due:'',owner:'',note:'Track open claims, loss history and insurer responses.',comments:[],completedAt:null},\n",
        "        {id:102,name:'Contract risk assumptions',status:'ns',priority:'',due:'',owner:'',note:'Capture assumed liability and indemnity points from service contracts.',comments:[],completedAt:null},\n",
        "        {id:103,name:'H&S insurance inputs',status:'ns',priority:'',due:'',owner:'',note:'Link H&S, incident and worker information needed for cover options.',comments:[],completedAt:null},\n",
    ]),
    ("legal-contracts", "Legal / Contracts", "#6B3FA0", [
        "        {id:111,name:'Service agreements',status:'ns',priority:'',due:'',owner:'',note:'Core customer and supplier agreements to review.',comments:[],completedAt:null},\n",
        "        {id:112,name:'Contract renewals',status:'ns',priority:'',due:'',owner:'',note:'Upcoming renewals, notice dates and decision points.',comments:[],completedAt:null},\n",
        "        {id:113,name:'Compliance documents',status:'ns',priority:'',due:'',owner:'',note:'Policies, licences, certifications and key legal docs.',comments:[],completedAt:null},\n",
    ]),
    ("people-hr", "People / HR Inputs", "#2D5F94", [
        "        {id:121,name:'Staff counts',status:'ns',priority:'',due:'',owner:'',note:'Permanent, casual and entity-level counts.',comments:[],completedAt:null},\n",
        "        {id:122,name:'Seasonal labour profile',status:'ns',priority:'',due:'',owner:'',note:'Seasonal peaks, locations and workforce movements.',comments:[],completedAt:null},\n",
        "        {id:123,name:'Health cover and payroll assumptions',status:'ns',priority:'',due:'',owner:'',note:'Benefits, health cover, payroll inputs and assumptions.',comments:[],completedAt:null},\n",
    ]),
    ("systems-automation", "Systems & Automation", "#00A6A6", [
        "        {id:131,name:'Dashboards',status:'ns',priority:'',due:'',owner:'',note:'Reporting dashboards and live trackers.',comments:[],completedAt:null},\n",
        "        {id:132,name:'Tools and integrations',status:'ns',priority:'',due:'',owner:'',note:'Internal tools, data links and system integrations.',comments:[],completedAt:null},\n",
        "        {id:133,name:'Process automation',status:'ns',priority:'',due:'',owner:'',note:'Repeatable workflows that can be automated.',comments:[],completedAt:null},\n",
    ]),
    ("data-evidence", "Data Requests / Evidence", "#B5650F", [
        "        {id:141,name:'Recurring information requests',status:'ns',priority:'',due:'',owner:'',note:'Chasing documents, support and evidence packs.',comments:[],completedAt:null},\n",
        "        {id:142,name:'Document request tracker',status:'ns',priority:'',due:'',owner:'',note:'Who has been asked, what is missing and where files are saved.',comments:[],completedAt:null},\n",
    ]),
    ("governance-decisions", "Governance / Decisions", "#5C8A1B", [
        "        {id:151,name:'ELT decisions',status:'ns',priority:'',due:'',owner:'',note:'Items needing executive decision or direction.',comments:[],completedAt:null},\n",
        "        {id:152,name:'Board approvals',status:'ns',priority:'',due:'',owner:'',note:'Items requiring board paper, approval or sign-off.',comments:[],completedAt:null},\n",
        "        {id:153,name:'Delegated sign-offs',status:'ns',priority:'',due:'',owner:'',note:'Management approvals and delegated authorities.',comments:[],completedAt:null},\n",
    ]),
    ("external-parties", "External Parties", "#C98A1F", [
        "        {id:161,name:'Broker',status:'ns',priority:'',due:'',owner:'',note:'Broker requests, advice and follow-ups.',comments:[],completedAt:null},\n",
        "        {id:162,name:'PWC',status:'ns',priority:'',due:'',owner:'',note:'PWC requests, deliverables and open items.',comments:[],completedAt:null},\n",
        "        {id:163,name:'Lawyers, insurers, banks and vendors',status:'ns',priority:'',due:'',owner:'',note:'Third-party dependencies and responses.',comments:[],completedAt:null},\n",
    ]),
    ("compliance-registrations", "Compliance / Registrations", "#4D7FB3", [
        "        {id:171,name:'FSP and statutory registrations',status:'ns',priority:'',due:'',owner:'',note:'FSP, Companies Office and statutory items.',comments:[],completedAt:null},\n",
        "        {id:172,name:'Licensing and audit',status:'ns',priority:'',due:'',owner:'',note:'Licences, audit requirements and compliance evidence.',comments:[],completedAt:null},\n",
        "        {id:173,name:'Tax registrations',status:'ns',priority:'',due:'',owner:'',note:'Tax setup, registrations and related filings.',comments:[],completedAt:null},\n",
    ]),
    ("projects-change", "Projects / Change", "#E2557B", [
        "        {id:181,name:'Cross-functional initiatives',status:'ns',priority:'',due:'',owner:'',note:'One-off projects spanning finance, ops, HR or legal.',comments:[],completedAt:null},\n",
        "        {id:182,name:'Change impacts',status:'ns',priority:'',due:'',owner:'',note:'Process, ownership and communication changes.',comments:[],completedAt:null},\n",
    ]),
]

def section_js(sec):
    key, label, color, tasks = sec
    return "      { key:'%s', label:'%s', color:'%s', tasks:[\n%s      ]},\n" % (key, label, color, ''.join(tasks))

additions = ''.join(section_js(sec) for sec in sections)

if 'ensureCoreSections(data)' not in page:
    page = page.replace(insurance_task, '', 1)
    insert_at = page.find("    ]},\n    view:", page.find("{ key:'tools'"))
    if insert_at < 0:
        raise SystemExit('section insertion point not found')
    page = page[:insert_at] + additions + page[insert_at:]

old_methods = """  ensureInsuranceTask(data) {
    const finance = data.sections.find(s => s.key === 'finance') || data.sections[0];
    if (!finance || finance.tasks.some(t => t.name === 'Insurance')) return;
    const idx = finance.tasks.findIndex(t => t.id === 8 || t.name.indexOf('Fixed Asset Register') === 0);
    const task = this.insuranceTask();
    if (idx >= 0) finance.tasks.splice(idx, 0, task); else finance.tasks.push(task);
  }
  normalizeData(data) {
    if (!data || !data.sections) return data;
    this.ensureInsuranceTask(data);
"""

new_methods = """  coreSections() {
    return [
%s    ];
  }
  ensureCoreSections(data) {
    this.coreSections().forEach(sec => {
      if (!data.sections.some(s => s.key === sec.key)) data.sections.push(JSON.parse(JSON.stringify(sec)));
    });
  }
  ensureInsuranceTask(data) {
    const target = data.sections.find(s => s.key === 'insurance-risk') || data.sections[0];
    if (!target) return;
    let existing = null, from = null;
    data.sections.forEach(s => {
      const idx = s.tasks.findIndex(t => t.name === 'Insurance');
      if (idx >= 0 && !existing) { existing = s.tasks[idx]; from = s; }
    });
    const task = existing || this.insuranceTask();
    if (from && from.key !== target.key) from.tasks = from.tasks.filter(t => t !== task);
    if (!target.tasks.some(t => t === task || t.name === 'Insurance')) target.tasks.unshift(task);
  }
  normalizeData(data) {
    if (!data || !data.sections) return data;
    this.ensureCoreSections(data);
    this.ensureInsuranceTask(data);
""" % additions

if old_methods in page:
    page = page.replace(old_methods, new_methods, 1)
elif 'ensureCoreSections(data)' not in page:
    raise SystemExit('method block not found')

markers = ['Insurance & Risk','Legal / Contracts','People / HR Inputs','Systems & Automation','Data Requests / Evidence','Governance / Decisions','External Parties','Compliance / Registrations','Projects / Change','Requirement Details','File/link']
missing = [x for x in markers if x not in page]
if missing:
    raise SystemExit('missing markers: ' + ', '.join(missing))
if 'rs.split(/\\n+/)' not in page:
    raise SystemExit('regex escape check failed')

data['pages'][entry] = page
new_template = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
new_text = text[:m.start(2)] + new_template + text[m.end(2):]
json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', new_text, re.S).group(1))
path.write_text(new_text, encoding='utf-8')
print('dashboard sections added')
