/* Actions page — tabs, action items, grants, contacts, outreach, events */

/* ─── Tab switching ─── */
function switchTab(tab) {
  document.querySelectorAll('.sub-tab').forEach(function(t) { t.classList.remove('active'); });
  document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });

  // Find the clicked button by matching text
  document.querySelectorAll('.sub-tab').forEach(function(t) {
    if (t.textContent.toLowerCase().includes(tab.replace('thisweek', 'this week'))) {
      t.classList.add('active');
    }
  });

  var panel = document.getElementById('panel-' + tab);
  if (panel) panel.classList.add('active');
}

/* ─── Action Items ─── */
function showAddAction() {
  document.getElementById('addActionForm').style.display = '';
  document.getElementById('newActionDesc').focus();
}

function hideAddAction() {
  document.getElementById('addActionForm').style.display = 'none';
}

function addAction() {
  var desc = document.getElementById('newActionDesc').value.trim();
  if (!desc) { showToast('Description is required', 'error'); return; }

  apiCall('/api/action', {
    method: 'POST',
    body: JSON.stringify({
      description: desc,
      action_type: document.getElementById('newActionType').value,
      priority: document.getElementById('newActionPriority').value,
      due_date: document.getElementById('newActionDue').value || null,
    })
  }).then(function() {
    showToast('Action added');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function toggleAction(id, checked) {
  apiCall('/api/action/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ status: checked ? 'done' : 'todo' })
  }).then(function() {
    var el = document.getElementById('action-' + id);
    if (el) el.classList.toggle('done', checked);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteAction(id) {
  apiCall('/api/action/' + id, { method: 'DELETE' })
    .then(function() {
      var el = document.getElementById('action-' + id);
      if (el) el.remove();
      showToast('Action removed');
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function seedActions() {
  apiCall('/api/seed-actions', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      if (data.created > 0) setTimeout(function() { location.reload(); }, 800);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* ─── Grants ─── */
function toggleGrantForm() {
  var el = document.getElementById('addGrantForm');
  el.style.display = el.style.display === 'none' ? '' : 'none';
}

function addGrant() {
  apiCall('/api/deadline', {
    method: 'POST',
    body: JSON.stringify({
      company_name: document.getElementById('grantCompany').value,
      program_name: document.getElementById('grantProgram').value,
      focus_area: document.getElementById('grantFocus').value,
      deadline: document.getElementById('grantDeadline').value,
      award_range: document.getElementById('grantAward').value,
      application_url: document.getElementById('grantUrl').value,
      priority: document.getElementById('grantPriority').value,
      grant_type: document.getElementById('grantType').value,
    })
  }).then(function() {
    showToast('Grant added');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* ─── Contacts ─── */
function toggleContactForm() {
  var el = document.getElementById('addContactForm');
  el.style.display = el.style.display === 'none' ? '' : 'none';
}

function addContact() {
  var prospectId = document.getElementById('contactProspect').value;
  apiCall('/api/contact', {
    method: 'POST',
    body: JSON.stringify({
      prospect_id: prospectId ? parseInt(prospectId) : null,
      name: document.getElementById('contactName').value,
      title: document.getElementById('contactTitle').value,
      email: document.getElementById('contactEmail').value,
      linkedin_url: document.getElementById('contactLinkedin').value,
      source: document.getElementById('contactSource').value,
    })
  }).then(function() {
    showToast('Contact added');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* ─── Outreach Emails ─── */
function generateTopEmails() {
  apiCall('/api/generate-top-emails', { method: 'POST', body: JSON.stringify({ n: 15 }) })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 1000);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function copyEmailText(emailId) {
  apiCall('/api/email/' + emailId + '/body')
    .then(function(data) {
      var text = 'Subject: ' + data.subject + '\n\n' + data.body;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() { showToast('Copied to clipboard'); });
      } else {
        var ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast('Copied to clipboard');
      }
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function editEmail(emailId) {
  var card = document.querySelector('.email-card:has([onclick*="editEmail(' + emailId + ')"])');
  if (!card) return;
  var bodyEl = card.querySelector('.email-body');
  var origText = bodyEl.textContent.trim();

  bodyEl.innerHTML = '<textarea style="width:100%; min-height:200px; font-family:Karla,sans-serif; font-size:14px; line-height:1.7; padding:12px; border:1px solid var(--primary); border-radius:var(--radius-sm);">' + origText + '</textarea>'
    + '<div style="margin-top:8px; display:flex; gap:8px;">'
    + '<button class="btn btn-sm btn-primary" onclick="saveEmail(' + emailId + ', this)">Save</button>'
    + '<button class="btn btn-sm btn-ghost" onclick="cancelEditEmail(this, ' + JSON.stringify(origText).replace(/"/g, '&quot;') + ')">Cancel</button>'
    + '</div>';
}

function saveEmail(emailId, btn) {
  var card = btn.closest('.email-card') || btn.closest('.email-body').parentElement;
  var textarea = card.querySelector('textarea');
  apiCall('/api/email/' + emailId, {
    method: 'PATCH',
    body: JSON.stringify({ body: textarea.value })
  }).then(function() {
    showToast('Email saved');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function cancelEditEmail(btn, origText) {
  var bodyEl = btn.closest('.email-body') || btn.parentElement.parentElement;
  bodyEl.innerHTML = origText;
}

function markStatus(emailId, status) {
  apiCall('/api/email/' + emailId, {
    method: 'PATCH',
    body: JSON.stringify({ status: status })
  }).then(function() {
    showToast('Status updated to ' + status);
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function regenerateEmail(prospectId) {
  apiCall('/api/generate-email/' + prospectId, { method: 'POST' })
    .then(function() {
      showToast('Email regenerated');
      setTimeout(function() { location.reload(); }, 500);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* ─── Events ─── */
function toggleEventForm() {
  var el = document.getElementById('addEventForm');
  el.style.display = el.style.display === 'none' ? '' : 'none';
}

function addEvent() {
  apiCall('/api/event', {
    method: 'POST',
    body: JSON.stringify({
      name: document.getElementById('eventName').value,
      event_type: document.getElementById('eventType').value,
      date: document.getElementById('eventDate').value || null,
      location: document.getElementById('eventLocation').value,
      url: document.getElementById('eventUrl').value,
      description: document.getElementById('eventDesc').value,
      relevance: document.getElementById('eventRelevance').value,
    })
  }).then(function() {
    showToast('Event added');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function updateEvent(id, status) {
  apiCall('/api/event/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ status: status })
  }).then(function() {
    showToast('Event updated');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteEvent(id) {
  apiCall('/api/event/' + id, { method: 'DELETE' })
    .then(function() {
      showToast('Event removed');
      setTimeout(function() { location.reload(); }, 500);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* ─── Grant card helpers ─── */
function toggleGrantDetail(id) {
  var el = document.getElementById('grantDetail-' + id);
  var btn = document.getElementById('grantToggle-' + id);
  if (el.style.display === 'none') {
    el.style.display = '';
    btn.textContent = 'Hide Details';
  } else {
    el.style.display = 'none';
    btn.textContent = 'Show Application Details';
  }
}

function updateDeadlineStatus(id, status) {
  apiCall('/api/deadline/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ status: status })
  }).then(function() {
    showToast('Status updated');
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteDeadline(id) {
  if (!confirm('Delete this grant opportunity?')) return;
  apiCall('/api/deadline/' + id, { method: 'DELETE' })
    .then(function() {
      showToast('Deleted');
      setTimeout(function() { location.reload(); }, 500);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
