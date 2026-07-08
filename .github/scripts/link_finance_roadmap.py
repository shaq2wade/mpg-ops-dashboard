from pathlib import Path

agenda_path = Path("agenda.html")
dash_path = Path("monarch-ops-dashboard.html")

agenda = agenda_path.read_text(encoding="utf-8")
dash = dash_path.read_text(encoding="utf-8")

if 'href="./finance-roadmap.html"' not in agenda:
    agenda = agenda.replace(
        '        <a class="btn" href="./">Back to dashboard</a>\n',
        '        <a class="btn" href="./">Back to dashboard</a>\n        <a class="btn" href="./finance-roadmap.html">Finance roadmap</a>\n',
        1,
    )

if 'finance-roadmap.html' not in dash:
    needle = '<div style=\\"display:flex;align-items:center;gap:9px\\">\\n        <button onclick=\\"{{ openPalette }}\\"'
    insert = '<div style=\\"display:flex;align-items:center;gap:9px\\">\\n        <a href=\\"finance-roadmap.html\\" style=\\"display:flex;align-items:center;gap:8px;font:700 12px Urbanist;padding:9px 13px;border-radius:10px;border:1px solid #E0D2BD;background:#fff;color:#201420;cursor:pointer;text-decoration:none;white-space:nowrap\\">Finance Roadmap<\\/a>\\n        <a href=\\"agenda.html\\" style=\\"display:flex;align-items:center;gap:8px;font:700 12px Urbanist;padding:9px 13px;border-radius:10px;border:1px solid #E0D2BD;background:#fff;color:#201420;cursor:pointer;text-decoration:none;white-space:nowrap\\">Agenda<\\/a>\\n        <button onclick=\\"{{ openPalette }}\\"'
    if needle not in dash:
        raise SystemExit("Dashboard action area needle not found")
    dash = dash.replace(needle, insert, 1)

agenda_path.write_text(agenda, encoding="utf-8", newline="")
dash_path.write_text(dash, encoding="utf-8", newline="")
print("Finance roadmap links applied")
