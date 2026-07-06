from pathlib import Path
import re

agenda_path = Path("agenda.html")
config_path = Path("agenda-config.js")
export_path = Path("Export Outlook Agenda.ps1")

agenda = agenda_path.read_text(encoding="utf-8")
config = config_path.read_text(encoding="utf-8")
export = export_path.read_text(encoding="utf-8")

css_old = '''    .file { border: 1px dashed #e0d2bd; border-radius: 10px; padding: 11px; background: #fff; }
    .row { display: flex; gap: 10px; align-items: flex-start; padding: 12px 0; border-top: 1px solid #f1e7d6; }
    .row:first-child { border-top: 0; padding-top: 0; }
    .time { width: 86px; flex: none; font-size: 12px; font-weight: 800; color: #b5650f; }'''
css_new = '''    .file { border: 1px dashed #e0d2bd; border-radius: 10px; padding: 11px; background: #fff; }
    .row { display: flex; gap: 10px; align-items: flex-start; padding: 12px 0; border-top: 1px solid #f1e7d6; }
    .row:first-child { border-top: 0; padding-top: 0; }
    .row.is-done { opacity: .55; }
    .row.is-done .item-title, .row.is-done .meta { text-decoration: line-through; }
    .done-check { position: relative; width: 24px; height: 24px; flex: none; margin-top: -2px; cursor: pointer; }
    .done-check input { position: absolute; opacity: 0; inset: 0; margin: 0; cursor: pointer; }
    .done-check span {
      display: block;
      width: 22px;
      height: 22px;
      border: 1px solid #d9cbb8;
      border-radius: 7px;
      background: #fff;
      position: relative;
    }
    .done-check input:checked + span { border-color: #5c8a1b; background: #5c8a1b; }
    .done-check input:checked + span::after {
      content: "";
      position: absolute;
      left: 7px;
      top: 3px;
      width: 5px;
      height: 10px;
      border: solid #fff;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }
    .time { width: 86px; flex: none; font-size: 12px; font-weight: 800; color: #b5650f; }'''
if ".done-check" not in agenda:
    agenda = agenda.replace(css_old, css_new, 1)

if 'doneStorageKey:' not in config:
    config = config.replace('''  outlookDigestStorageKey: "mpg_agenda_outlook_digest_v1",
  localDigestUrl:''', '''  outlookDigestStorageKey: "mpg_agenda_outlook_digest_v1",
  doneStorageKey: "mpg_agenda_done_v1",
  localDigestUrl:''', 1)

agenda = agenda.replace('''        els.calendarStatus.textContent = "Outlook " + stats.inbox + " inbox / " + stats.tasks + " tasks";''', '''        els.calendarStatus.textContent = "Outlook " + stats.inbox + " flagged / " + stats.tasks + " tasks";''')

functions_block = '''

    function doneStoreKey() {
      return storeKey("doneStorageKey", "mpg_agenda_done_v1");
    }

    function loadDoneMap() {
      try {
        return JSON.parse(localStorage.getItem(doneStoreKey()) || "{}");
      } catch (err) {
        return {};
      }
    }

    function saveDoneMap(doneMap) {
      localStorage.setItem(doneStoreKey(), JSON.stringify(doneMap));
    }

    function itemDoneId(kind, item) {
      const parts = [
        kind,
        item.id || "",
        item.senderEmail || "",
        item.sender || "",
        item.received || "",
        item.due || "",
        item.subject || ""
      ];
      return parts.join("|").toLowerCase();
    }

    function isDone(kind, item) {
      return !!loadDoneMap()[itemDoneId(kind, item)];
    }

    function doneControl(kind, item) {
      const id = itemDoneId(kind, item);
      const checked = isDone(kind, item) ? " checked" : "";
      return '<label class="done-check" title="Done">' +
        '<input type="checkbox" aria-label="Done" data-done-id="' + escapeHtml(id) + '"' + checked + '>' +
        '<span></span>' +
      '</label>';
    }

    function dateValue(value, fallback) {
      if (!value) return fallback;
      const time = Date.parse(value);
      return Number.isNaN(time) ? fallback : time;
    }

    function sortInboxByDate(items) {
      return (items || []).slice().sort((a, b) => dateValue(b.received, 0) - dateValue(a.received, 0));
    }

    function sortTasksByDate(items) {
      return (items || []).slice().sort((a, b) => {
        const diff = dateValue(a.due, Number.MAX_SAFE_INTEGER) - dateValue(b.due, Number.MAX_SAFE_INTEGER);
        if (diff !== 0) return diff;
        return String(a.subject || "").localeCompare(String(b.subject || ""));
      });
    }
'''
if "function doneStoreKey()" not in agenda:
    date_label_block = '''    function dateLabel(value) {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return new Intl.DateTimeFormat("en-NZ", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }).format(date);
    }
'''
    agenda = agenda.replace(date_label_block, date_label_block + functions_block, 1)

render_inbox = '''    function renderInbox(items) {
      const sorted = sortInboxByDate(items);
      if (!sorted.length) {
        els.inboxList.innerHTML = '<div class="empty">No flagged inbox actions loaded yet.</div>';
        return;
      }
      els.inboxList.innerHTML = sorted.slice(0, 8).map((mail) => {
        const tags = [
          mail.unread ? "Unread" : "",
          mail.flagged ? "Flagged" : "",
          mail.importance === "high" ? "High" : ""
        ].filter(Boolean);
        const done = isDone("mail", mail);
        return '<div class="row' + (done ? ' is-done' : '') + '">' +
          doneControl("mail", mail) +
          '<div class="time">' + escapeHtml(dateLabel(mail.received)) + '</div>' +
          '<div>' +
            '<div class="item-title">' + escapeHtml(mail.subject || "No subject") + '</div>' +
            '<div class="meta">' + escapeHtml([mail.sender, mail.preview].filter(Boolean).join(" | ")) + '</div>' +
            '<div>' + tags.map((tag) => '<span class="badge orange">' + escapeHtml(tag) + '</span>').join("") + '</div>' +
          '</div>' +
        '</div>';
      }).join("");
    }'''
agenda, inbox_count = re.subn(r"    function renderInbox\(items\) \{\n.*?^    \}\n\n    function renderOutlookTasks", render_inbox + "\n\n    function renderOutlookTasks", agenda, count=1, flags=re.S | re.M)
if inbox_count != 1:
    raise SystemExit("Could not patch renderInbox")

render_tasks = '''    function renderOutlookTasks(items) {
      const sorted = sortTasksByDate(items);
      if (!sorted.length) {
        els.outlookTaskList.innerHTML = '<div class="empty">No Outlook tasks loaded yet.</div>';
        return;
      }
      els.outlookTaskList.innerHTML = sorted.slice(0, 8).map((task) => {
        const tags = [
          task.due ? "Due " + task.due : "",
          task.importance === "high" ? "High" : "",
          task.percentComplete ? task.percentComplete + "% done" : ""
        ].filter(Boolean);
        const done = isDone("task", task);
        return '<div class="row' + (done ? ' is-done' : '') + '">' +
          doneControl("task", task) +
          '<div class="time">' + escapeHtml(task.due || "Task") + '</div>' +
          '<div>' +
            '<div class="item-title">' + escapeHtml(task.subject || "Untitled task") + '</div>' +
            '<div class="meta">' + escapeHtml(task.preview || "") + '</div>' +
            '<div>' + tags.map((tag) => '<span class="badge blue">' + escapeHtml(tag) + '</span>').join("") + '</div>' +
          '</div>' +
        '</div>';
      }).join("");
    }'''
agenda, task_count = re.subn(r"    function renderOutlookTasks\(items\) \{\n.*?^    \}\n\n    function taskScore", render_tasks + "\n\n    function taskScore", agenda, count=1, flags=re.S | re.M)
if task_count != 1:
    raise SystemExit("Could not patch renderOutlookTasks")

digest_priority = '''    function digestPriorityItems() {
      const digest = loadOutlookDigest();
      const inbox = sortInboxByDate(digest.inbox || []).filter((mail) => !isDone("mail", mail)).map((mail) => ({
        title: mail.subject || "No subject",
        section: ["Inbox", mail.sender, dateLabel(mail.received)].filter(Boolean).join(" | "),
        score: mail.score || 0,
        tags: ["Email", mail.unread ? "Unread" : "", mail.flagged ? "Flagged" : "", mail.importance === "high" ? "High" : ""].filter(Boolean),
        badge: mail.flagged || mail.importance === "high" ? "orange" : "blue"
      }));
      const tasks = sortTasksByDate(digest.tasks || []).filter((task) => !isDone("task", task)).map((task) => ({
        title: task.subject || "Untitled task",
        section: ["Outlook Task", task.due ? "Due " + task.due : ""].filter(Boolean).join(" | "),
        score: task.score || 0,
        tags: ["Task", task.due ? "Due " + task.due : "", task.importance === "high" ? "High" : ""].filter(Boolean),
        badge: task.importance === "high" ? "orange" : "blue"
      }));
      return inbox.concat(tasks);
    }'''
agenda, priority_count = re.subn(r"    function digestPriorityItems\(\) \{\n.*?^    \}\n\n    function escapeHtml", digest_priority + "\n\n    function escapeHtml", agenda, count=1, flags=re.S | re.M)
if priority_count != 1:
    raise SystemExit("Could not patch digestPriorityItems")

old_refresh = '''    async function refresh() {
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
    }
'''
new_refresh = '''    async function refresh() {
      if (shouldLock()) { showLock(); return; }
      showAgenda();
      const cachedDigest = loadOutlookDigest();
      renderInbox(cachedDigest.inbox || []);
      renderOutlookTasks(cachedDigest.tasks || []);
      renderAgendaPriorities();
      const text = await loadIcsText();
      renderMeetings(text ? todaysEvents(text) : []);
      const digest = await fetchLocalOutlookDigest();
      renderInbox(digest.inbox || []);
      renderOutlookTasks(digest.tasks || []);
      renderAgendaPriorities();
    }

    function renderAgendaPriorities() {
      renderPriorities(digestPriorityItems().concat(dashboardTasks()).sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, config.priorityLimit || 8));
    }

    function handleDoneChange(event) {
      const input = event.target;
      if (!input || !input.matches("input[data-done-id]")) return;
      const doneMap = loadDoneMap();
      if (input.checked) {
        doneMap[input.dataset.doneId] = new Date().toISOString();
      } else {
        delete doneMap[input.dataset.doneId];
      }
      saveDoneMap(doneMap);
      const row = input.closest(".row");
      if (row) row.classList.toggle("is-done", input.checked);
      renderAgendaPriorities();
    }
'''
if "function handleDoneChange(event)" not in agenda:
    agenda = agenda.replace(old_refresh, new_refresh, 1)
    agenda = agenda.replace('''    els.refresh.addEventListener("click", refresh);
''', '''    els.refresh.addEventListener("click", refresh);
    els.inboxList.addEventListener("change", handleDoneChange);
    els.outlookTaskList.addEventListener("change", handleDoneChange);
''', 1)

export = export.replace('''$inboxRows = New-Object System.Collections.Generic.List[object]
$inboxItems = $namespace.GetDefaultFolder(6).Items
$inboxItems.Sort("[ReceivedTime]", $true)''', '''$inboxRows = New-Object System.Collections.Generic.List[object]
$inboxItems = $namespace.GetDefaultFolder(6).Items
try { $inboxItems = $inboxItems.Restrict("[FlagStatus] = 2") } catch {}
$inboxItems.Sort("[ReceivedTime]", $true)''')
export = export.replace('''  if ($item.Class -ne 43) { continue }
  $received = $null
  try { $received = [datetime]$item.ReceivedTime } catch {}
  if ($received -and $received -lt $cutoff -and -not $item.UnRead -and $item.FlagStatus -eq 0) { continue }
  $seenInbox += 1
  $inboxRows.Add([pscustomobject]@{
    subject = Clean-Text $item.Subject 220''', '''  if ($item.Class -ne 43) { continue }
  $flagStatus = 0
  try { $flagStatus = [int]$item.FlagStatus } catch {}
  if ($flagStatus -ne 2) { continue }
  $received = $null
  try { $received = [datetime]$item.ReceivedTime } catch {}
  $seenInbox += 1
  $inboxRows.Add([pscustomobject]@{
    id = Clean-Text $item.EntryID 300
    subject = Clean-Text $item.Subject 220''')
export = export.replace('''    flagged = [bool]($item.FlagStatus -ne 0)''', '''    flagged = $true''')
export = export.replace('''    $taskRows.Add([pscustomobject]@{
      subject = Clean-Text $task.Subject 220''', '''    $taskRows.Add([pscustomobject]@{
      id = Clean-Text $task.EntryID 300
      subject = Clean-Text $task.Subject 220''')
export = export.replace('''$inboxSorted = @($inboxRows | Sort-Object score -Descending | Select-Object -First 30)
$tasksSorted = @($taskRows | Sort-Object score -Descending | Select-Object -First 30)''', '''$inboxSorted = @($inboxRows | Sort-Object @{ Expression = { if ($_.received) { [datetime]$_.received } else { [datetime]::MinValue } }; Descending = $true } | Select-Object -First 30)
$tasksSorted = @($taskRows | Sort-Object @{ Expression = { if ($_.due) { [datetime]$_.due } else { [datetime]::MaxValue } }; Ascending = $true }, subject | Select-Object -First 30)''')
export = export.replace('''  source = "Outlook desktop local export"
  inboxWindowDays = $DaysBack''', '''  source = "Outlook desktop local export"
  inboxFilter = "active flagged follow-up"''')

agenda_path.write_text(agenda, encoding="utf-8", newline="")
config_path.write_text(config, encoding="utf-8", newline="")
export_path.write_text(export, encoding="utf-8", newline="")
print("Agenda done toggles and flagged inbox filter applied")
