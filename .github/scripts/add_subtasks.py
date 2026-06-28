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


def rep(old, new):
    global page
    if old not in page:
        raise SystemExit('missing text: ' + old[:180])
    page = page.replace(old, new, 1)


def sub(pattern, fn):
    global page
    page, n = re.subn(pattern, fn, page, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('missing pattern: ' + pattern[:180])


if 'Required / Subtasks' in page:
    raise SystemExit('subtasks already applied')

rep("""                <sc-if value="{{ task.hasNote }}" hint-placeholder-val="{{ false }}">
                  <div style="font-size:12.5px;color:#6E5F57;font-style:italic;margin-top:8px">{{ task.note }}</div>
                </sc-if>

                <sc-if value="{{ task.isEditing }}" hint-placeholder-val="{{ false }}">""", """                <sc-if value="{{ task.hasNote }}" hint-placeholder-val="{{ false }}">
                  <div style="font-size:12.5px;color:#6E5F57;font-style:italic;margin-top:8px">{{ task.note }}</div>
                </sc-if>
                <sc-if value="{{ task.hasReqs }}" hint-placeholder-val="{{ false }}">
                  <div style="margin-top:10px;background:#FBF3E6;border:1px solid #EFE3D2;border-radius:9px;padding:9px 11px">
                    <div style="font-size:11px;color:#A2978C;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Required / Subtasks</div>
                    <sc-for list="{{ task.reqs }}" as="r" hint-placeholder-count="3">
                      <button onclick="{{ r.onToggle }}" style="display:flex;align-items:flex-start;gap:8px;width:100%;text-align:left;border:none;background:transparent;padding:4px 0;font:500 12px Urbanist;color:#201420;cursor:pointer">
                        <span style="{{ r.boxStyle }}">{{ r.mark }}</span>
                        <span style="{{ r.textStyle }}">{{ r.text }}</span>
                      </button>
                    </sc-for>
                  </div>
                </sc-if>

                <sc-if value="{{ task.isEditing }}" hint-placeholder-val="{{ false }}">""")

textarea_block = '''
                    <div style="display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap;margin-top:9px">
                      <span style="font-size:11px;color:#A2978C;padding-top:7px">Required</span>
                      <textarea ref="{{ regEl }}" data-k="{{ task.erKey }}" onchange="{{ onInput }}" placeholder="One subtask or requirement per line" style="font:400 12px Urbanist;padding:7px 9px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none;flex:1;min-width:220px;min-height:86px;resize:vertical">{{ task.dReqs }}</textarea>
                    </div>'''
sub(r'(<input ref="\{\{ regEl \}\}" data-k="\{\{ task\.enKey \}\}"[^>]+>\n\s*<button onclick="\{\{ task\.onSaveEdit \}\}"[^>]+>Save</button>\n\s*</div>)', lambda mm: mm.group(1) + textarea_block)

rep("""      if (!t.comments) t.comments = [];
      if (!t.due) t.due = '';
      if (!t.owner || !['MR','AL','RW'].includes(t.owner)) t.owner = '';
      if (!this.ST[t.status]) t.status = 'ns';
      if (t.completedAt === undefined) t.completedAt = null;""", """      if (!t.comments) t.comments = [];
      if (!t.due) t.due = '';
      if (!t.owner || !['MR','AL','RW'].includes(t.owner)) t.owner = '';
      if (!this.ST[t.status]) t.status = 'ns';
      if (!t.reqs) t.reqs = [];
      t.reqs = t.reqs.map(r => typeof r === 'string' ? { text:r, done:false } : { text:(r.text||''), done:!!r.done }).filter(r => r.text);
      if (t.completedAt === undefined) t.completedAt = null;""")

rep("""this.findSec(d,k).tasks.push({id:this.nextId++,name,status:st,priority:'',due:'',owner:'',note:'',comments:[],completedAt:st==='dn'?new Date().toISOString():null});""", """this.findSec(d,k).tasks.push({id:this.nextId++,name,status:st,priority:'',due:'',owner:'',note:'',reqs:[],comments:[],completedAt:st==='dn'?new Date().toISOString():null});""")

rep("""  saveEdit(k, id) { const g=key=>{const e=this.els[key];return e?e.value:null;}; this.mutate(d => { const t=this.findSec(d,k).tasks.find(t=>t.id===id); const p=g('ep-'+id);if(p!==null)t.priority=p; const o=g('eo-'+id);if(o!==null)t.owner=['MR','AL','RW'].includes(o)?o:''; const du=g('ed-'+id);if(du!==null)t.due=du; const n=g('en-'+id);if(n!==null)t.note=n; }); this.setState({ editingId:null }); }""", """  saveEdit(k, id) { const g=key=>{const e=this.els[key];return e?e.value:null;}; this.mutate(d => { const t=this.findSec(d,k).tasks.find(t=>t.id===id); const p=g('ep-'+id);if(p!==null)t.priority=p; const o=g('eo-'+id);if(o!==null)t.owner=['MR','AL','RW'].includes(o)?o:''; const du=g('ed-'+id);if(du!==null)t.due=du; const n=g('en-'+id);if(n!==null)t.note=n; const rs=g('er-'+id); if(rs!==null){ const old=t.reqs||[]; const doneByText={}; old.forEach(r=>{ const x=typeof r==='string'?{text:r,done:false}:r; doneByText[x.text]=!!x.done; }); t.reqs=rs.split(/\\n+/).map(x=>x.trim()).filter(Boolean).map(text=>({text,done:!!doneByText[text]})); } }); this.setState({ editingId:null }); }
  toggleReq(k, id, ri) { this.mutate(d => { const t=this.findSec(d,k).tasks.find(t=>t.id===id); if(!t||!t.reqs||!t.reqs[ri])return; const r=t.reqs[ri]; if(typeof r==='string') t.reqs[ri]={text:r,done:true}; else r.done=!r.done; }); }""")

rep("""    const od = this.isOverdue(t);
    const comments = (t.comments||[]).map((c,i) => ({ text:c.text, ts:c.ts, onDelete:()=>this.deleteComment(sec.key,t.id,i) }));
    return {
      id:t.id, name:t.name, note:t.note, hasNote:!!t.note,""", """    const od = this.isOverdue(t);
    const comments = (t.comments||[]).map((c,i) => ({ text:c.text, ts:c.ts, onDelete:()=>this.deleteComment(sec.key,t.id,i) }));
    const reqRaw = (t.reqs||[]).map(r => typeof r === 'string' ? { text:r, done:false } : { text:r.text||'', done:!!r.done }).filter(r=>r.text);
    const reqs = reqRaw.map((r,i) => ({
      text:r.text, done:r.done, mark:r.done?'✓':'',
      boxStyle:'width:16px;height:16px;border-radius:4px;border:1px solid '+(r.done?'#5C8A1B':'#D7C6AD')+';background:'+(r.done?'#E7F0DA':'#fff')+';color:#5C8A1B;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex:none;margin-top:1px',
      textStyle:'line-height:1.35;'+(r.done?'text-decoration:line-through;color:#6E5F57':'color:#201420'),
      onToggle:()=>this.toggleReq(sec.key,t.id,i),
    }));
    return {
      id:t.id, name:t.name, note:t.note, hasNote:!!t.note, reqs, hasReqs:reqs.length>0,""")

rep("""      dPriority:t.priority||'', dOwner:t.owner||'', dDue:t.due||'', dNote:t.note||'',
      epKey:'ep-'+t.id, eoKey:'eo-'+t.id, edKey:'ed-'+t.id, enKey:'en-'+t.id, cmKey:'cm-'+sec.key+'-'+t.id,""", """      dPriority:t.priority||'', dOwner:t.owner||'', dDue:t.due||'', dNote:t.note||'', dReqs:reqRaw.map(r=>r.text).join('\\n'),
      epKey:'ep-'+t.id, eoKey:'eo-'+t.id, edKey:'ed-'+t.id, enKey:'en-'+t.id, erKey:'er-'+t.id, cmKey:'cm-'+sec.key+'-'+t.id,""")

insurance = """        {id:30,name:'Insurance',status:'ns',priority:'hi',due:'',owner:'',note:'Information request',reqs:[
          {text:'Current Policy Schedules - required to assess current coverage.',done:false},
          {text:'Last year renewal submission - proposal forms, sum insured calculation sheets and fleet values to understand values.',done:false},
          {text:'Last year renewal report - understand the renewal strategy adopted last year.',done:false},
          {text:'Example contracts - assess assumption of risk for services provided under each business.',done:false},
          {text:'Staff Information - understand numbers and seasonal fluctuations, plus details on health cover provided so options can be assessed.',done:false},
        ],comments:[],completedAt:null},
"""
sub(r"(\s*\{id:7,name:'DSO Buildout',status:'wip',priority:'hi',due:'2026-02-13',owner:'',note:'',comments:\[\],completedAt:null\},\n)", lambda mm: mm.group(1) + insurance)

rep("els = {}; nextId = 200;", "els = {}; nextId = 300;")

data['pages'][entry] = page
new_template = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
roundtrip = json.loads(new_template)
pg = roundtrip['pages'][entry]
for marker in ['Required / Subtasks', 'toggleReq', 'Insurance', 'Current Policy Schedules', 'erKey', 'Staff Information']:
    if marker not in pg:
        raise SystemExit('missing marker: ' + marker)
text = text[:m.start(2)] + new_template + text[m.end(2):]
json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
path.write_text(text, encoding='utf-8')
