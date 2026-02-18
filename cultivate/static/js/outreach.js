/* Outreach center interactions */

function generateTopEmails() {
  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating...';

  apiCall('/api/generate-top-emails', { method: 'POST' })
    .then(data => {
      showToast(data.message, 'success');
      setTimeout(() => location.reload(), 1000);
    })
    .catch(e => {
      showToast('Error: ' + e.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Generate for Top 15';
    });
}

function copyEmailText(emailId) {
  apiCall('/api/email/' + emailId + '/body')
    .then(data => {
      const text = 'Subject: ' + data.subject + '\n\n' + data.body;
      navigator.clipboard.writeText(text)
        .then(() => showToast('Copied to clipboard!', 'success'))
        .catch(() => {
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

function editEmail(emailId) {
  const bodyEl = document.getElementById('emailBody-' + emailId);
  const currentText = bodyEl.textContent;

  const textarea = document.createElement('textarea');
  textarea.value = currentText;
  textarea.style.cssText = 'width:100%;min-height:200px;background:var(--bg);border:1px solid var(--border);color:var(--text);font-family:Karla,sans-serif;font-size:14px;padding:16px;border-radius:4px;line-height:1.65;resize:vertical;outline:none;';

  bodyEl.textContent = '';
  bodyEl.appendChild(textarea);
  textarea.focus();

  // Add save/cancel buttons
  const actions = document.createElement('div');
  actions.style.cssText = 'margin-top:8px;display:flex;gap:8px;';
  actions.innerHTML = '<button class="btn btn-primary btn-sm" id="saveEdit-' + emailId + '">Save</button><button class="btn btn-ghost btn-sm" id="cancelEdit-' + emailId + '">Cancel</button>';
  bodyEl.appendChild(actions);

  document.getElementById('saveEdit-' + emailId).addEventListener('click', function() {
    const newText = textarea.value;
    apiCall('/api/email/' + emailId, {
      method: 'PATCH',
      body: JSON.stringify({ body: newText }),
    })
    .then(data => {
      bodyEl.textContent = newText;
      // Update word count
      const card = bodyEl.closest('.email-card');
      const wcEl = card.querySelector('.word-count');
      if (wcEl) {
        wcEl.textContent = data.word_count + ' words';
        wcEl.className = 'word-count ' + (data.word_count <= 150 ? 'ok' : (data.word_count <= 180 ? 'warning' : 'over'));
      }
      showToast('Email saved', 'success');
    })
    .catch(() => { bodyEl.textContent = currentText; showToast('Failed to save', 'error'); });
  });

  document.getElementById('cancelEdit-' + emailId).addEventListener('click', function() {
    bodyEl.textContent = currentText;
  });
}

function markStatus(emailId, status) {
  apiCall('/api/email/' + emailId, {
    method: 'PATCH',
    body: JSON.stringify({ status: status }),
  })
  .then(() => {
    showToast('Status updated to ' + status, 'success');
    setTimeout(() => location.reload(), 800);
  })
  .catch(() => showToast('Failed to update', 'error'));
}

function regenerateEmail(prospectId) {
  apiCall('/api/generate-email/' + prospectId, { method: 'POST' })
    .then(data => {
      if (data.error) showToast(data.error, 'error');
      else {
        showToast('Email regenerated!', 'success');
        setTimeout(() => location.reload(), 800);
      }
    })
    .catch(e => showToast('Error', 'error'));
}
