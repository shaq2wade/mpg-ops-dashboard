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
        raise SystemExit('missing text: ' + old[:120])
    page = page.replace(old, new, 1)


def sub(pattern, new):
    global page
    page, n = re.subn(pattern, new, page, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('missing pattern: ' + pattern[:120])

if 'Requirement Details' in page:
    raise SystemExit('requirement fields already applied')

rep('<span style="{{ r.textStyle }}">{{ r.text }}</span>\n                      </button>\n                    </sc-for>', '<span style="{{ r.textStyle }}">{{ r.text }}</span>\n                      </button>\n                      <sc-if value="{{ r.hasMeta }}" hint-placeholder-val="{{ false }}">\n                        <div style="display:flex;gap:5px;flex-wrap:wrap;margin:0 0 5px 24px">\n                          <sc-for list="{{ r.meta }}" as="m" hint-placeholder-count="3">\n                            <span style="{{ m.style }}">{{ m.text }}</span>\n                          </sc-for>\n                        </div>\n                      </sc-if>\n                    </sc-for>')

rep('<textarea ref="{{ regEl }}" data-k="{{ task.erKey }}" onchange="{{ onInput }}" placeholder="One subtask or requirement per line" style="font:400 12px Urbanist;padding:7px 9px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none;flex:1;min-width:220px;min-height:86px;resize:vertical">{{ task.dReqs }}</textarea>\n                    </div>\n                  </div>\n                </sc-if>', '<textarea ref="{{ regEl }}" data-k="{{ task.erKey }}" onchange="{{ onInput }}" placeholder="One subtask or requirement per line" style="font:400 12px Urbanist;padding:7px 9px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none;flex:1;min-width:220px;min-height:86px;resize:vertical">{{ task.dReqs }}</textarea>\n                    </div>\n                    <sc-if value="{{ task.hasReqs }}" hint-placeholder-val="{{ false }}">\n                      <div style="margin-top:10px;border-top:1px dashed #E0D2BD;padding-top:10px">\n                        <div style="font-size:11px;color:#A2978C;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:7px">Requirement Details</div>\n                        <sc-for list="{{ task.reqEditRows }}" as="rq" hint-placeholder-count="3">\n                          <div style="background:#FBF3E6;border:1px solid #EFE3D2;border-radius:9px;padding:9px;margin-bottom:7px">\n                            <div style="font-size:12px;font-weight:700;margin-bottom:7px;color:#201420">{{ rq.label }}</div>\n                            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:7px;margin-bottom:7px">\n                              <select ref="{{ regEl }}" data-k="{{ rq.ownerKey }}" defaultvalue="{{ rq.owner }}" onchange="{{ onInput }}" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none"><option value="">Owner</option><option value="MR">MR</option><option value="AL">AL</option><option value="RW">RW</option></select>\n                              <input ref="{{ regEl }}" data-k="{{ rq.sourceKey }}" defaultvalue="{{ rq.source }}" onchange="{{ onInput }}" placeholder="Source" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none">\n                              <select ref="{{ regEl }}" data-k="{{ rq.statusKey }}" defaultvalue="{{ rq.status }}" onchange="{{ onInput }}" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none"><option value="">Status</option><option value="requested">Requested</option><option value="received">Received</option><option value="reviewed">Reviewed</option><option value="query">Query raised</option><option value="complete">Complete</option></select>\n                              <input type="date" ref="{{ regEl }}" data-k="{{ rq.dueKey }}" defaultvalue="{{ rq.due }}" onchange="{{ onInput }}" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none">\n                            </div>\n                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px">\n                              <input ref="{{ regEl }}" data-k="{{ rq.noteKey }}" defaultvalue="{{ rq.note }}" onchange="{{ onInput }}" placeholder="Notes / issue found" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none;min-width:0">\n                              <input ref="{{ regEl }}" data-k="{{ rq.linkKey }}" defaultvalue="{{ rq.link }}" onchange="{{ onInput }}" placeholder="File/link" style="font:400 12px Urbanist;padding:6px 8px;border:1px solid #E0D2BD;border-radius:8px;background:#fff;color:#201420;outline:none;min-width:0">\n                            </div>\n                          </div>\n                        </sc-for>\n                      </div>\n                    </sc-if>\n                  </div>\n                </sc-if>')

rep("t.reqs = t.reqs.map(r => typeof r === 'string' ? { text:r, done:false } : { text:(r.text||''), done:!!r.done }).filter(r => r.text);", "t.reqs = t.reqs.map(r => typeof r === 'string' ? { text:r, done:false, owner:'', source:'', status:'', due:'', note:'', link:'' } : { text:(r.text||''), done:!!r.done, owner:['MR','AL','RW'].includes(r.owner)?r.owner:'', source:r.source||'', status:r.status||'', due:r.due||'', note:r.note||'', link:r.link||'' }).filter(r => r.text);")

for old, new in {
"{text:'Current Policy Schedules - required to assess current coverage.',done:false}": "{text:'Current Policy Schedules - required to assess current coverage.',done:false,owner:'',source:'broker / insurer',status:'requested',due:'',note:'',link:''}",
"{text:'Last year renewal submission - proposal forms, sum insured calculation sheets and fleet values to understand values.',done:false}": "{text:'Last year renewal submission - proposal forms, sum insured calculation sheets and fleet values to understand values.',done:false,owner:'',source:'broker / finance',status:'requested',due:'',note:'',link:''}",
"{text:'Last year renewal report - understand the renewal strategy adopted last year.',done:false}": "{text:'Last year renewal report - understand the renewal strategy adopted last year.',done:false,owner:'',source:'broker',status:'requested',due:'',note:'',link:''}",
"{text:'Example contracts - assess assumption of risk for services provided under each business.',done:false}": "{text:'Example contracts - assess assumption of risk for services provided under each business.',done:false,owner:'',source:'legal / operations',status:'requested',due:'',note:'',link:''}",
"{text:'Staff Information - understand numbers and seasonal fluctuations, plus details on health cover provided so options can be assessed.',done:false}": "{text:'Staff Information - understand numbers and seasonal fluctuations, plus details on health cover provided so options can be assessed.',done:false,owner:'',source:'HR',status:'requested',due:'',note:'',link:''}",
}.items():
    rep(old, new)

new_save = """saveEdit(k, id) { const g=key=>{const e=this.els[key];return e?e.value:null;}; this.mutate(d => { const t=this.findSec(d,k).tasks.find(t=>t.id===id); const p=g('ep-'+id);if(p!==null)t.priority=p; const o=g('eo-'+id);if(o!==null)t.owner=['MR','AL','RW'].includes(o)?o:''; const du=g('ed-'+id);if(du!==null)t.due=du; const n=g('en-'+id);if(n!==null)t.note=n; const rs=g('er-'+id); if(rs!==null){ const old=t.reqs||[]; const byText={}; old.forEach((r,i)=>{ const x=typeof r==='string'?{text:r,done:false}:r; const item={text:x.text||'',done:!!x.done,owner:x.owner||'',source:x.source||'',status:x.status||'',due:x.due||'',note:x.note||'',link:x.link||''}; byText[item.text]=item; }); t.reqs=rs.split(/\\n+/).map(x=>x.trim()).filter(Boolean).map((text,i)=>{ const prev=byText[text]||{}; const owner=g('ro-'+id+'-'+i); const source=g('rs-'+id+'-'+i); const status=g('rt-'+id+'-'+i); const due=g('rd-'+id+'-'+i); const note=g('rn-'+id+'-'+i); const link=g('rl-'+id+'-'+i); return {text,done:!!prev.done,owner:owner!==null&&['MR','AL','RW'].includes(owner)?owner:(prev.owner||''),source:source!==null?source:(prev.source||''),status:status!==null?status:(prev.status||''),due:due!==null?due:(prev.due||''),note:note!==null?note:(prev.note||''),link:link!==null?link:(prev.link||'')}; }); } }); this.setState({ editingId:null }); }"""
sub(r"saveEdit\(k, id\) \{.*?\}\n  toggleReq", new_save + "\n  toggleReq")

new_req = """const reqRaw = (t.reqs||[]).map(r => typeof r === 'string' ? { text:r, done:false, owner:'', source:'', status:'', due:'', note:'', link:'' } : { text:r.text||'', done:!!r.done, owner:r.owner||'', source:r.source||'', status:r.status||'', due:r.due||'', note:r.note||'', link:r.link||'' }).filter(r=>r.text);
    const statusLabel = { requested:'Requested', received:'Received', reviewed:'Reviewed', query:'Query raised', complete:'Complete' };
    const chip = (text, kind='') => ({ text, style:'font:600 10.5px Urbanist;padding:2px 7px;border-radius:20px;border:1px solid '+(kind==='status'?'#C9D8EA':'#E0D2BD')+';background:'+(kind==='status'?'#EAF0F9':'#fff')+';color:'+(kind==='status'?'#2D5F94':'#6E5F57') });
    const reqs = reqRaw.map((r,i) => {
      const meta = [];
      if (r.owner) meta.push(chip('Owner: '+r.owner));
      if (r.source) meta.push(chip('Source: '+r.source));
      if (r.status) meta.push(chip(statusLabel[r.status]||r.status,'status'));
      if (r.due) meta.push(chip('Due: '+this.fmtDue(r.due)));
      if (r.note) meta.push(chip('Note: '+r.note));
      if (r.link) meta.push(chip('File/link: '+r.link));
      return { text:r.text, done:r.done, mark:r.done?'✓':'', meta, hasMeta:meta.length>0,
      boxStyle:'width:16px;height:16px;border-radius:4px;border:1px solid '+(r.done?'#5C8A1B':'#D7C6AD')+';background:'+(r.done?'#E7F0DA':'#fff')+';color:#5C8A1B;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex:none;margin-top:1px',
      textStyle:'line-height:1.35;'+(r.done?'text-decoration:line-through;color:#6E5F57':'color:#201420'),
      onToggle:()=>this.toggleReq(sec.key,t.id,i),
    }});"""
sub(r"const reqRaw = \(t\.reqs\|\|\[\]\).*?\n    \}\)\);", new_req)

rep("""dPriority:t.priority||'', dOwner:t.owner||'', dDue:t.due||'', dNote:t.note||'', dReqs:reqRaw.map(r=>r.text).join('\\n'),
      epKey:'ep-'+t.id, eoKey:'eo-'+t.id, edKey:'ed-'+t.id, enKey:'en-'+t.id, erKey:'er-'+t.id, cmKey:'cm-'+sec.key+'-'+t.id,""", """dPriority:t.priority||'', dOwner:t.owner||'', dDue:t.due||'', dNote:t.note||'', dReqs:reqRaw.map(r=>r.text).join('\\n'),
      reqEditRows:reqRaw.map((r,i)=>({ label:(i+1)+'. '+r.text, owner:r.owner||'', source:r.source||'', status:r.status||'', due:r.due||'', note:r.note||'', link:r.link||'', ownerKey:'ro-'+t.id+'-'+i, sourceKey:'rs-'+t.id+'-'+i, statusKey:'rt-'+t.id+'-'+i, dueKey:'rd-'+t.id+'-'+i, noteKey:'rn-'+t.id+'-'+i, linkKey:'rl-'+t.id+'-'+i })),
      epKey:'ep-'+t.id, eoKey:'eo-'+t.id, edKey:'ed-'+t.id, enKey:'en-'+t.id, erKey:'er-'+t.id, cmKey:'cm-'+sec.key+'-'+t.id,""")

data['pages'][entry] = page
new_template = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
pg = json.loads(new_template)['pages'][entry]
for marker in ['Requirement Details', 'ownerKey', 'File/link', 'broker / insurer', 'Query raised']:
    if marker not in pg:
        raise SystemExit('missing marker: ' + marker)
text = text[:m.start(2)] + new_template + text[m.end(2):]
json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', text, re.S).group(1))
path.write_text(text, encoding='utf-8')
