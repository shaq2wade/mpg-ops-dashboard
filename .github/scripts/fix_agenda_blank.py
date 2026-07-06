from pathlib import Path
import re

agenda_path = Path("agenda.html")
helper_path = Path("Start-Agenda-AutoRefresh.ps1")

agenda = agenda_path.read_text(encoding="utf-8")
helper = helper_path.read_text(encoding="utf-8")

if "const helperTimeoutMs = 5000;" not in agenda:
    agenda = agenda.replace('    let currentIcsText = "";\n', '    let currentIcsText = "";\n    const helperTimeoutMs = 5000;\n', 1)

if "function digestStats(digest)" not in agenda:
    agenda = agenda.replace('''    function loadOutlookDigest() {
      try {
        return JSON.parse(localStorage.getItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1")) || "{}");
      } catch (err) {
        return {};
      }
    }

    async function fetchLocalOutlookDigest() {''', '''    function loadOutlookDigest() {
      try {
        return JSON.parse(localStorage.getItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1")) || "{}");
      } catch (err) {
        return {};
      }
    }

    function digestStats(digest) {
      const inbox = (digest && digest.inbox) || [];
      const tasks = (digest && digest.tasks) || [];
      return { inbox: inbox.length, tasks: tasks.length, total: inbox.length + tasks.length };
    }

    async function fetchLocalOutlookDigest() {''', 1)

new_fetch = '''    async function fetchLocalOutlookDigest() {
      const url = config.localDigestUrl || "http://127.0.0.1:8765/digest";
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), helperTimeoutMs);
      els.calendarStatus.textContent = "Checking Outlook helper...";
      try {
        const res = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), {
          cache: "no-store",
          signal: controller.signal
        });
        if (!res.ok) throw new Error("Local Outlook helper unavailable");
        const digest = await res.json();
        localStorage.setItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1"), JSON.stringify(digest));
        const stats = digestStats(digest);
        els.calendarStatus.textContent = "Outlook " + stats.inbox + " inbox / " + stats.tasks + " tasks";
        return digest;
      } catch (err) {
        const fallback = loadOutlookDigest();
        const stats = digestStats(fallback);
        els.calendarStatus.textContent = stats.total ? "Using saved Outlook digest" : "Start local Outlook helper";
        return fallback;
      } finally {
        clearTimeout(timer);
      }
    }'''
agenda, fetch_count = re.subn(r"    async function fetchLocalOutlookDigest\(\) \{\n.*?^    \}\n\n    function dateLabel", new_fetch + "\n\n    function dateLabel", agenda, count=1, flags=re.S | re.M)
if fetch_count != 1:
    raise SystemExit("Could not patch fetchLocalOutlookDigest")

agenda = agenda.replace("No inbox digest imported.", "No inbox actions loaded yet.")
agenda = agenda.replace("No Outlook task digest imported.", "No Outlook tasks loaded yet.")
agenda = agenda.replace('''    function digestPriorityItems() {
      const digest = await fetchLocalOutlookDigest();''', '''    function digestPriorityItems() {
      const digest = loadOutlookDigest();''', 1)

new_refresh = '''    async function refresh() {
      if (shouldLock()) { showLock(); return; }
      showAgenda();
      const cachedDigest = loadOutlookDigest();
      renderInbox(cachedDigest.inbox || []);
      renderOutlookTasks(cachedDigest.tasks || []);
      renderPriorities(digestPriorityItems().concat(dashboardTasks()).sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, config.priorityLimit || 8));
      const text = await loadIcsText();
      renderMeetings(text ? todaysEvents(text) : []);
      const digest = await fetchLocalOutlookDigest();
      renderInbox(digest.inbox || []);
      renderOutlookTasks(digest.tasks || []);
      renderPriorities(digestPriorityItems().concat(dashboardTasks()).sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, config.priorityLimit || 8));
    }'''
agenda, refresh_count = re.subn(r"    async function refresh\(\) \{\n.*?^    \}\n\n    els\.refresh", new_refresh + "\n\n    els.refresh", agenda, count=1, flags=re.S | re.M)
if refresh_count != 1:
    raise SystemExit("Could not patch refresh")

if "Access-Control-Allow-Private-Network" not in helper:
    helper = helper.replace('''    "Access-Control-Allow-Headers: Content-Type`r`n" +
    "Cache-Control: no-store`r`n" +''', '''    "Access-Control-Allow-Headers: Content-Type`r`n" +
    "Access-Control-Allow-Private-Network: true`r`n" +
    "Cache-Control: no-store`r`n" +''', 1)

agenda_path.write_text(agenda, encoding="utf-8", newline="")
helper_path.write_text(helper, encoding="utf-8", newline="")
print("Agenda blank-state patch applied")
