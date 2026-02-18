/* Company detail page interactions */

function updateStage(select) {
  const id = select.dataset.id;
  apiCall('/api/prospect/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ pipeline_stage: select.value }),
  })
  .then(() => showToast('Stage updated', 'success'))
  .catch(() => showToast('Failed to update', 'error'));
}

function autoScore(id) {
  apiCall('/api/auto-score/' + id, { method: 'POST' })
    .then(data => {
      showToast('Scores updated!', 'success');
      setTimeout(() => location.reload(), 800);
    })
    .catch(e => showToast('Error: ' + e.message, 'error'));
}

function fetch990ForCompany(id) {
  const btn = document.getElementById('fetch990Btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Fetching...';

  apiCall('/api/prospect/' + id + '/fetch-990', { method: 'POST' })
    .then(data => {
      if (data.error) {
        showToast(data.error, 'error');
        btn.disabled = false;
        btn.textContent = 'Fetch 990 Data';
      } else {
        showToast('Foundation data loaded!', 'success');
        setTimeout(() => location.reload(), 1000);
      }
    })
    .catch(e => {
      showToast('Error: ' + e.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Fetch 990 Data';
    });
}

function generateEmailForCompany(id) {
  apiCall('/api/generate-email/' + id, { method: 'POST' })
    .then(data => {
      if (data.error) showToast(data.error, 'error');
      else {
        showToast('Email draft generated!', 'success');
        setTimeout(() => location.reload(), 800);
      }
    })
    .catch(e => showToast('Error: ' + e.message, 'error'));
}

function copyEmail(emailId) {
  apiCall('/api/email/' + emailId + '/body')
    .then(data => {
      const text = 'Subject: ' + data.subject + '\n\n' + data.body;
      navigator.clipboard.writeText(text)
        .then(() => showToast('Copied to clipboard!', 'success'))
        .catch(() => {
          // Fallback
          const ta = document.createElement('textarea');
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          ta.remove();
          showToast('Copied to clipboard!', 'success');
        });
    })
    .catch(e => showToast('Error', 'error'));
}

function saveNotes(id, value) {
  apiCall('/api/prospect/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ notes: value }),
  })
  .then(() => showToast('Notes saved', 'success'))
  .catch(() => showToast('Failed to save', 'error'));
}

function toggleCompanyAction(id, checked) {
  apiCall('/api/action/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ status: checked ? 'done' : 'todo' })
  }).then(function() {
    showToast(checked ? 'Done!' : 'Reopened');
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deepResearchForCompany(prospectId) {
  var btn = document.getElementById('deepResearchBtn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Researching...';
  }
  apiCall('/api/prospect/' + prospectId + '/deep-research', { method: 'POST' })
    .then(function(data) {
      if (data.error) {
        showToast(data.error, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Run Deep Research'; }
      } else {
        var msg = 'Deep research complete: ' + (data.grantee_count || 0) + ' grantees, ' +
                  (data.officer_count || 0) + ' officers';
        showToast(msg, 'success');
        setTimeout(function() { location.reload(); }, 1000);
      }
    })
    .catch(function(e) {
      showToast('Error: ' + e.message, 'error');
      if (btn) { btn.disabled = false; btn.textContent = 'Run Deep Research'; }
    });
}

function showAddNoteForm() {
  document.getElementById('addNoteForm').style.display = 'block';
}

function saveResearchNote(prospectId) {
  var noteType = document.getElementById('noteType').value;
  var title = document.getElementById('noteTitle').value;
  var content = document.getElementById('noteContent').value;
  var sourceUrl = document.getElementById('noteSourceUrl').value;

  if (!title || !content) {
    showToast('Title and content are required', 'error');
    return;
  }

  apiCall('/api/prospect/' + prospectId + '/research-note', {
    method: 'POST',
    body: JSON.stringify({
      note_type: noteType,
      title: title,
      content: content,
      source_url: sourceUrl || null
    })
  })
  .then(function(data) {
    showToast('Note saved!', 'success');
    setTimeout(function() { location.reload(); }, 800);
  })
  .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteResearchNote(noteId) {
  if (!confirm('Delete this research note?')) return;
  apiCall('/api/research-note/' + noteId, { method: 'DELETE' })
    .then(function() {
      showToast('Note deleted');
      setTimeout(function() { location.reload(); }, 800);
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
