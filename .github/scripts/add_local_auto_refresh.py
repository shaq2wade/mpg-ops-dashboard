from pathlib import Path

path = Path('agenda.html')
page = path.read_text(encoding='utf-8')

if 'fetchLocalOutlookDigest' not in page:
    page = page.replace(
        '<div class="bigdate">Outlook feed</div>',
        '<div class="bigdate">Agenda sources</div>',
        1,
    )
    page = page.replace(
        '<div class="notice">Use an Outlook ICS link or upload an .ics export. The URL/file is stored only in this browser.</div>',
        '<div class="notice">For one-click refresh, run <strong>Start-Agenda-AutoRefresh.cmd</strong> locally and keep that window open. You can still use an Outlook ICS link, .ics import, or JSON upload as a fallback.</div>',
        1,
    )
    marker = '''    function loadOutlookDigest() {
      try {
        return JSON.parse(localStorage.getItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1")) || "{}");
      } catch (err) {
        return {};
      }
    }
'''
    insert = marker + r'''
    async function fetchLocalOutlookDigest() {
      const url = config.localDigestUrl || "http://127.0.0.1:8765/digest";
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 20000);
      try {
        const res = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), {
          cache: "no-store",
          signal: controller.signal
        });
        if (!res.ok) throw new Error("Local Outlook helper unavailable");
        const digest = await res.json();
        localStorage.setItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1"), JSON.stringify(digest));
        els.calendarStatus.textContent = "Outlook refreshed";
        return digest;
      } catch (err) {
        return loadOutlookDigest();
      } finally {
        clearTimeout(timer);
      }
    }
'''
    if marker not in page:
        raise SystemExit('loadOutlookDigest marker not found')
    page = page.replace(marker, insert, 1)
    page = page.replace(
        '      const digest = loadOutlookDigest();',
        '      const digest = await fetchLocalOutlookDigest();',
        1,
    )
    page = page.replace(
        '    refresh();\n  </script>',
        '    refresh();\n    setInterval(() => {\n      if (!shouldLock()) refresh();\n    }, config.autoRefreshMs || 300000);\n  </script>',
        1,
    )

required = ['fetchLocalOutlookDigest', 'Start-Agenda-AutoRefresh.cmd', 'config.autoRefreshMs']
missing = [x for x in required if x not in page]
if missing:
    raise SystemExit('missing markers: ' + ', '.join(missing))
if 'msal' in page or 'calendarView' in page:
    raise SystemExit('old Microsoft connector code still present')

path.write_text(page, encoding='utf-8')
print('local agenda auto-refresh patched')
