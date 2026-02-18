/* Global utility functions */

function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function apiCall(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
  };
  return fetch(url, { ...defaults, ...options })
    .then(r => {
      if (!r.ok) throw new Error('Request failed');
      return r.json();
    });
}

/* Auto-score all prospects */
function autoScoreAll() {
  apiCall('/api/auto-score-all', { method: 'POST' })
    .then(data => {
      showToast(data.message);
      setTimeout(() => location.reload(), 1000);
    })
    .catch(e => showToast('Error: ' + e.message, 'error'));
}

/* Fetch 990 for a prospect (from pipeline table) */
function fetch990(id) {
  apiCall('/api/prospect/' + id + '/fetch-990', { method: 'POST' })
    .then(data => {
      if (data.error) showToast(data.error, 'error');
      else showToast('Fetched 990 data!', 'success');
    })
    .catch(e => showToast('Error: ' + e.message, 'error'));
}

/* Generate email from pipeline table */
function generateEmail(id) {
  apiCall('/api/generate-email/' + id, { method: 'POST' })
    .then(data => {
      if (data.error) showToast(data.error, 'error');
      else showToast('Email draft generated!', 'success');
    })
    .catch(e => showToast('Error: ' + e.message, 'error'));
}
