/* Intelligence page — search & 990 fetching */

document.addEventListener('DOMContentLoaded', function() {
  var searchInput = document.getElementById('foundationSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var term = this.value.toLowerCase();
      document.querySelectorAll('.foundation-card').forEach(function(card) {
        var name = card.getAttribute('data-name') || '';
        card.style.display = name.includes(term) ? '' : 'none';
      });
    });
  }
});

/* Hidden class toggle */
document.querySelectorAll('.foundation-card').forEach(function(card) {
  var details = card.querySelector('.fdn-details');
  if (details) details.classList.add('hidden');
});

/* Style for hidden */
var style = document.createElement('style');
style.textContent = '.hidden { display: none !important; }';
document.head.appendChild(style);

function fetchAll990() {
  if (!confirm('Fetch 990 data for all prospects? This may take a minute.')) return;
  apiCall('/api/fetch-all-990', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 1500);
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deepResearch(prospectId) {
  showToast('Running deep research...', 'success');
  apiCall('/api/prospect/' + prospectId + '/deep-research', { method: 'POST' })
    .then(function(data) {
      if (data.error) {
        showToast(data.error, 'error');
      } else {
        var msg = 'Deep research done: ' + (data.grantee_count || 0) + ' grantees, ' +
                  (data.officer_count || 0) + ' officers, trend: ' + (data.trend || 'N/A');
        showToast(msg, 'success');
        setTimeout(function() { location.reload(); }, 1500);
      }
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deepResearchAll() {
  if (!confirm('Run deep research on all foundations? This fetches XML files from IRS and may take several minutes.')) return;
  showToast('Starting deep research for all foundations...', 'success');
  apiCall('/api/deep-research-all', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 1500);
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function fetch990(prospectId) {
  apiCall('/api/prospect/' + prospectId + '/fetch-990', { method: 'POST' })
    .then(function(data) {
      if (data.error) showToast(data.error, 'error');
      else {
        showToast('990 data fetched!', 'success');
        setTimeout(function() { location.reload(); }, 1000);
      }
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
