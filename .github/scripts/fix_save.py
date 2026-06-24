from pathlib import Path

path = Path('monarch-ops-dashboard.html')
text = path.read_text(encoding='utf-8')


def rep(old, new):
    global text
    if old not in text:
        raise SystemExit('missing replacement: ' + old[:160])
    text = text.replace(old, new, 1)


rep("""  BIN_BASE = 'https://api.jsonbin.io/v3/b';\n  BIN_ID = '';""", """  BIN_BASE = 'https://api.jsonbin.io/v3/b';\n  BIN_ID = '';\n  LOCAL_KEY = 'mpg_ops_dashboard_data_v4';""")

rep("""  async boot() {\n    await this.loadData();\n    if (!this.BIN_ID) this.saveData();\n  }\n\n  // ── persistence ──────────────────────────────""", """  async boot() {\n    this.loadLocalData();\n    await this.loadData();\n    if (!this.BIN_ID) this.saveData();\n  }\n\n  // ── persistence ──────────────────────────────\n  normalizeData(data) {\n    if (!data || !data.sections) return data;\n    data.sections.forEach(s => s.tasks.forEach(t => {\n      if (!t.comments) t.comments = [];\n      if (!t.due) t.due = '';\n      if (!t.owner || !['MR','AL','RW'].includes(t.owner)) t.owner = '';\n      if (!this.ST[t.status]) t.status = 'ns';\n      if (t.completedAt === undefined) t.completedAt = null;\n    }));\n    return data;\n  }\n  loadLocalData() {\n    try {\n      const raw = localStorage.getItem(this.LOCAL_KEY);\n      if (!raw) return false;\n      const data = this.normalizeData(JSON.parse(raw));\n      if (data && data.sections) { this.setState({ data }); return true; }\n    } catch(e) {}\n    return false;\n  }\n  saveLocalData(data=this.state.data) {\n    try { localStorage.setItem(this.LOCAL_KEY, JSON.stringify(data)); return true; }\n    catch(e) { return false; }\n  }""")

rep("""      if (r.ok) {\n        const data = await r.json();\n        (data.sections||[]).forEach(s => s.tasks.forEach(t => {\n          if (!t.comments) t.comments = [];\n          if (!t.due) t.due = '';\n          if (!t.owner) t.owner = '';\n          if (t.completedAt === undefined) t.completedAt = null;\n        }));\n        if (data.sections) this.setState({ data });\n      }""", """      if (r.ok) {\n        const data = this.normalizeData(await r.json());\n        if (data.sections) { this.setState({ data }); this.saveLocalData(data); }\n      }""")

rep("""  async saveData() {\n    this.setState({ syncStatus:'saving' });\n    try {\n      await this.ensureBin();\n      await fetch(`${this.BIN_BASE}/${this.BIN_ID}`, { method:'PUT', headers:{'Content-Type':'application/json','X-Master-Key':this.API_KEY}, body:JSON.stringify(this.state.data) });\n      this.setState({ syncStatus:'saved' });\n      clearTimeout(this._st); this._st = setTimeout(() => this.setState({ syncStatus:'idle' }), 2200);\n    } catch(e) { this.setState({ syncStatus:'error' }); }\n  }\n  queueSave() { clearTimeout(this.saveTimer); this.saveTimer = setTimeout(() => this.saveData(), 800); }""", """  async saveData() {\n    this.setState({ syncStatus:'saving' });\n    const localOk = this.saveLocalData(this.state.data);\n    try {\n      await this.ensureBin();\n      const r = await fetch(`${this.BIN_BASE}/${this.BIN_ID}`, { method:'PUT', headers:{'Content-Type':'application/json','X-Master-Key':this.API_KEY}, body:JSON.stringify(this.state.data) });\n      if (!r.ok) throw new Error('Remote save failed');\n      this.setState({ syncStatus:'saved' });\n    } catch(e) {\n      this.setState({ syncStatus: localOk ? 'saved' : 'error' });\n    }\n    clearTimeout(this._st); this._st = setTimeout(() => this.setState({ syncStatus:'idle' }), 2200);\n  }\n  queueSave() { clearTimeout(this.saveTimer); this.saveTimer = setTimeout(() => this.saveData(), 800); }""")

rep("""  mutate(fn) { const d = JSON.parse(JSON.stringify(this.state.data)); fn(d); this.setState({ data:d }, () => this.queueSave()); }""", """  mutate(fn) { const d = JSON.parse(JSON.stringify(this.state.data)); fn(d); this.setState({ data:d }, () => { this.saveLocalData(d); this.queueSave(); }); }""")

path.write_text(text, encoding='utf-8')
