from pathlib import Path

path = Path('agenda.html')
page = path.read_text(encoding='utf-8')

if 'digestInput' not in page:
    page = page.replace(
        '    .score { font-size: 11px; font-weight: 800; color: #a2978c; text-transform: uppercase; letter-spacing: .05em; }\n',
        '    .score { font-size: 11px; font-weight: 800; color: #a2978c; text-transform: uppercase; letter-spacing: .05em; }\n    .subsection { margin-top: 18px; padding-top: 14px; border-top: 1px dashed #e0d2bd; }\n',
        1,
    )
    page = page.replace(
        '''      <div class="field">
        <label for="fileInput">ICS file import</label>
        <input class="file" id="fileInput" type="file" accept=".ics,text/calendar">
      </div>
''',
        '''      <div class="field">
        <label for="fileInput">ICS file import</label>
        <input class="file" id="fileInput" type="file" accept=".ics,text/calendar">
      </div>
      <div class="field">
        <label for="digestInput">Outlook inbox and task digest JSON</label>
        <input class="file" id="digestInput" type="file" accept=".json,application/json">
      </div>
''',
        1,
    )
    page = page.replace(
        '        <div id="meetingList"></div>\n',
        '''        <div id="meetingList"></div>
        <div class="subsection">
          <h2>Inbox Actions</h2>
          <div id="inboxList"></div>
        </div>
        <div class="subsection">
          <h2>Outlook Tasks</h2>
          <div id="outlookTaskList"></div>
        </div>
''',
        1,
    )
    page = page.replace(
        '      fileInput: document.getElementById("fileInput"),\n',
        '      fileInput: document.getElementById("fileInput"),\n      digestInput: document.getElementById("digestInput"),\n',
        1,
    )
    page = page.replace(
        '      meetingList: document.getElementById("meetingList"),\n',
        '      meetingList: document.getElementById("meetingList"),\n      inboxList: document.getElementById("inboxList"),\n      outlookTaskList: document.getElementById("outlookTaskList"),\n',
        1,
    )

    digest_functions = r'''
    function loadOutlookDigest() {
      try {
        return JSON.parse(localStorage.getItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1")) || "{}");
      } catch (err) {
        return {};
      }
    }

    function dateLabel(value) {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return new Intl.DateTimeFormat("en-NZ", { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }).format(date);
    }

    function renderInbox(items) {
      if (!items.length) {
        els.inboxList.innerHTML = '<div class="empty">No inbox digest imported.</div>';
        return;
      }
      els.inboxList.innerHTML = items.slice(0, 8).map((mail) => {
        const tags = [mail.unread ? "Unread" : "", mail.flagged ? "Flagged" : "", mail.importance === "high" ? "High" : ""].filter(Boolean);
        return '<div class="row">' +
          '<div class="time">' + escapeHtml(dateLabel(mail.received)) + '</div>' +
          '<div>' +
            '<div class="item-title">' + escapeHtml(mail.subject || "No subject") + '</div>' +
            '<div class="meta">' + escapeHtml([mail.sender, mail.preview].filter(Boolean).join(" | ")) + '</div>' +
            '<div>' + tags.map((tag) => '<span class="badge orange">' + escapeHtml(tag) + '</span>').join("") + '</div>' +
          '</div>' +
        '</div>';
      }).join("");
    }

    function renderOutlookTasks(items) {
      if (!items.length) {
        els.outlookTaskList.innerHTML = '<div class="empty">No Outlook task digest imported.</div>';
        return;
      }
      els.outlookTaskList.innerHTML = items.slice(0, 8).map((task) => {
        const tags = [task.due ? "Due " + task.due : "", task.importance === "high" ? "High" : "", task.percentComplete ? task.percentComplete + "% done" : ""].filter(Boolean);
        return '<div class="row">' +
          '<div class="time">' + escapeHtml(task.due || "Task") + '</div>' +
          '<div>' +
            '<div class="item-title">' + escapeHtml(task.subject || "Untitled task") + '</div>' +
            '<div class="meta">' + escapeHtml(task.preview || "") + '</div>' +
            '<div>' + tags.map((tag) => '<span class="badge blue">' + escapeHtml(tag) + '</span>').join("") + '</div>' +
          '</div>' +
        '</div>';
      }).join("");
    }
'''
    marker = '    }\n\n    function taskScore(task) {\n'
    if marker not in page:
        raise SystemExit('taskScore marker not found')
    page = page.replace(marker, '    }\n' + digest_functions + '\n    function taskScore(task) {\n', 1)

    start = page.find('    function renderPriorities(items) {')
    end = page.find('    function escapeHtml(value) {', start)
    if start < 0 or end < 0:
        raise SystemExit('renderPriorities block not found')
    new_priority = r'''    function renderPriorities(items) {
      if (!items.length) {
        els.priorityList.innerHTML = '<div class="empty">No priority items found on this browser.</div>';
        return;
      }
      els.priorityList.innerHTML = items.map((item) => {
        const task = item.task || {};
        const title = item.title || task.name || task.subject || "Untitled";
        const section = item.section || "";
        const tags = item.tags || [
          task.priority === "crit" ? "Critical" : task.priority === "hi" ? "High" : "",
          task.status ? task.status : "",
          task.due ? "Due " + task.due : ""
        ].filter(Boolean);
        return '<div class="focus">' +
          '<div class="score">' + Math.round(item.score || 0) + ' priority points</div>' +
          '<div class="item-title">' + escapeHtml(title) + '</div>' +
          '<div class="meta">' + escapeHtml(section || "") + '</div>' +
          '<div>' + tags.map((t) => '<span class="badge ' + (item.badge || badgeClass(task)) + '">' + escapeHtml(t) + '</span>').join("") + '</div>' +
        '</div>';
      }).join("");
    }

    function digestPriorityItems() {
      const digest = loadOutlookDigest();
      const inbox = (digest.inbox || []).map((mail) => ({
        title: mail.subject || "No subject",
        section: ["Inbox", mail.sender, dateLabel(mail.received)].filter(Boolean).join(" | "),
        score: mail.score || 0,
        tags: ["Email", mail.unread ? "Unread" : "", mail.flagged ? "Flagged" : "", mail.importance === "high" ? "High" : ""].filter(Boolean),
        badge: mail.flagged || mail.importance === "high" ? "orange" : "blue"
      }));
      const tasks = (digest.tasks || []).map((task) => ({
        title: task.subject || "Untitled task",
        section: ["Outlook Task", task.due ? "Due " + task.due : ""].filter(Boolean).join(" | "),
        score: task.score || 0,
        tags: ["Task", task.due ? "Due " + task.due : "", task.importance === "high" ? "High" : ""].filter(Boolean),
        badge: task.importance === "high" ? "orange" : "blue"
      }));
      return inbox.concat(tasks);
    }

'''
    page = page[:start] + new_priority + page[end:]

    page = page.replace(
        '''      const text = await loadIcsText();
      renderMeetings(text ? todaysEvents(text) : []);
      renderPriorities(dashboardTasks());
''',
        '''      const text = await loadIcsText();
      const digest = loadOutlookDigest();
      renderMeetings(text ? todaysEvents(text) : []);
      renderInbox(digest.inbox || []);
      renderOutlookTasks(digest.tasks || []);
      renderPriorities(digestPriorityItems().concat(dashboardTasks()).sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, config.priorityLimit || 8));
''',
        1,
    )

    page = page.replace(
        '''    els.fileInput.addEventListener("change", async () => {
      const file = els.fileInput.files && els.fileInput.files[0];
      if (!file) return;
      currentIcsText = await file.text();
      localStorage.setItem(storeKey("calendarTextStorageKey", "mpg_agenda_calendar_text_v1"), currentIcsText);
      localStorage.removeItem(storeKey("calendarFeedStorageKey", "mpg_agenda_calendar_feed_v1"));
      refresh();
    });

    refresh();
''',
        '''    els.fileInput.addEventListener("change", async () => {
      const file = els.fileInput.files && els.fileInput.files[0];
      if (!file) return;
      currentIcsText = await file.text();
      localStorage.setItem(storeKey("calendarTextStorageKey", "mpg_agenda_calendar_text_v1"), currentIcsText);
      localStorage.removeItem(storeKey("calendarFeedStorageKey", "mpg_agenda_calendar_feed_v1"));
      refresh();
    });
    els.digestInput.addEventListener("change", async () => {
      const file = els.digestInput.files && els.digestInput.files[0];
      if (!file) return;
      const text = await file.text();
      JSON.parse(text);
      localStorage.setItem(storeKey("outlookDigestStorageKey", "mpg_agenda_outlook_digest_v1"), text);
      refresh();
    });

    refresh();
''',
        1,
    )

required = ['digestInput', 'renderInbox', 'renderOutlookTasks', 'digestPriorityItems', 'outlookDigestStorageKey']
missing = [x for x in required if x not in page]
if missing:
    raise SystemExit('missing markers: ' + ', '.join(missing))
if 'msal' in page or 'calendarView' in page:
    raise SystemExit('old Microsoft connector code still present')

path.write_text(page, encoding='utf-8')
print('agenda outlook digest import patched')
