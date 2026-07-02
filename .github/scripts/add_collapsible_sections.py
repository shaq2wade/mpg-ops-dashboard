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

if 'toggleSection(k)' not in page:
    page, n = re.subn(
        r'<button onclick="\{\{ sec\.onDelete \}\}" style="margin-left:auto;[^>]*>.*?</button>',
        '<button onclick="{{ sec.onToggle }}" style="margin-left:auto;font:700 11px Urbanist;padding:4px 10px;border-radius:20px;border:1px solid #E0D2BD;background:#fff;color:#201420;cursor:pointer;white-space:nowrap">{{ sec.toggleLabel }}</button>\n              <button onclick="{{ sec.onDelete }}" style="font:500 11px Urbanist;padding:4px 10px;border-radius:20px;border:1px solid #F0B9B9;background:#fff;color:#A32D2D;cursor:pointer">✕ section</button>',
        page,
        count=1,
    )
    if n != 1:
        raise SystemExit(f'delete button replace count {n}')

    task_loop = '<sc-for list="{{ sec.tasks }}" as="task" hint-placeholder-count="3">'
    task_insert = '''<sc-if value="{{ sec.isCollapsed }}" hint-placeholder-val="{{ false }}">
              <div style="font-size:12px;color:#6E5F57;background:#fff;border:1px dashed #E0D2BD;border-radius:10px;padding:9px 12px;margin-top:-2px">{{ sec.collapsedLabel }}</div>
            </sc-if>

            <sc-if value="{{ sec.isOpen }}" hint-placeholder-val="{{ true }}">
            ''' + task_loop
    idx = page.find(task_loop)
    if idx < 0:
        raise SystemExit('task loop not found')
    page = page[:idx] + task_insert + page[idx + len(task_loop):]

    start = page.find('data-k="{{ sec.addKey }}"', idx)
    if start < 0:
        raise SystemExit('add input not found')
    close_marker = '\n          </div>\n        </sc-for>'
    end = page.find(close_marker, start)
    if end < 0:
        raise SystemExit('section close marker not found')
    page = page[:end] + '\n            </sc-if>' + page[end:]

    old_state = """    view: 'list', activeTab: 'all', activeFilter: 'all', showOldDone: false,
    editingId: null, commentingId: null,
"""
    new_state = """    view: 'list', activeTab: 'all', activeFilter: 'all', showOldDone: false,
    collapsedSections: {},
    editingId: null, commentingId: null,
"""
    if old_state not in page:
        raise SystemExit('state block not found')
    page = page.replace(old_state, new_state, 1)

    old_method = """  setView(v) { this.setState({ view:v, paletteOpen:false }); }
  setTab(k) { this.setState({ activeTab:k }); }
"""
    new_method = """  setView(v) { this.setState({ view:v, paletteOpen:false }); }
  toggleSection(k) { this.setState(s => { const cur = s.collapsedSections || {}; return { collapsedSections:{ ...cur, [k]: !cur[k] } }; }); }
  setTab(k) { this.setState({ activeTab:k }); }
"""
    if old_method not in page:
        raise SystemExit('method insertion not found')
    page = page.replace(old_method, new_method, 1)

    old_return = '''        return {
          label:sec.label, countLabel:sdn+'/'+stot, pctLabel:spct+'%',
          dotStyle:'width:10px;height:10px;border-radius:50%;flex:none;background:'+sec.color,
          barStyle:'height:100%;border-radius:5px;transition:width .6s;width:'+spct+'%;background:'+bc,
          tasks:visible.map(t=>this.taskVM(sec,t)),
          hasHiddenOld:hiddenOld>0, hiddenLabel:hiddenOld+' completed task'+(hiddenOld>1?'s':'')+' hidden (done 1m+)',
          addKey:'an-'+sec.key, statusKey:'as-'+sec.key,
          onAddTask:()=>this.addTask(sec.key), onDelete:()=>this.deleteSection(sec.key),
        };
'''
    new_return = '''        const collapsed = !!((st.collapsedSections || {})[sec.key]);
        return {
          label:sec.label, countLabel:sdn+'/'+stot, pctLabel:spct+'%',
          dotStyle:'width:10px;height:10px;border-radius:50%;flex:none;background:'+sec.color,
          barStyle:'height:100%;border-radius:5px;transition:width .6s;width:'+spct+'%;background:'+bc,
          tasks:visible.map(t=>this.taskVM(sec,t)),
          hasHiddenOld:hiddenOld>0, hiddenLabel:hiddenOld+' completed task'+(hiddenOld>1?'s':'')+' hidden (done 1m+)',
          isOpen:!collapsed, isCollapsed:collapsed,
          toggleLabel:collapsed?'▸ Open':'▾ Close',
          collapsedLabel:visible.length+' task'+(visible.length===1?'':'s')+' hidden',
          addKey:'an-'+sec.key, statusKey:'as-'+sec.key,
          onAddTask:()=>this.addTask(sec.key), onDelete:()=>this.deleteSection(sec.key), onToggle:()=>this.toggleSection(sec.key),
        };
'''
    if old_return not in page:
        raise SystemExit('return block not found')
    page = page.replace(old_return, new_return, 1)

    old_palette = """    allWS.forEach(x => add('•', x.t.name, x.s.label, ()=>{this.setView('list');this.setTab(x.s.key);this.setState({editingId:x.t.id,commentingId:null});}));
"""
    new_palette = """    allWS.forEach(x => add('•', x.t.name, x.s.label, ()=>{this.setView('list');this.setTab(x.s.key);this.setState(s=>({editingId:x.t.id,commentingId:null,collapsedSections:{...(s.collapsedSections||{}),[x.s.key]:false}}));}));
"""
    if old_palette in page:
        page = page.replace(old_palette, new_palette, 1)

markers = ['collapsedSections', 'toggleSection(k)', 'sec.toggleLabel', 'sec.isOpen', 'sec.isCollapsed', 'Insurance & Risk', 'Requirement Details', 'File/link']
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
print('collapsible sections added')
