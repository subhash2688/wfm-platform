/* Pipeline page — filtering, sorting, inline editing, import/export */

document.addEventListener('DOMContentLoaded', function() {
  initFilters();
  initSorting();
  initInlineEdit();
  initStageSelects();
});

/* Filtering */
function initFilters() {
  var search = document.getElementById('searchInput');
  var stage = document.getElementById('filterStage');
  var industry = document.getElementById('filterIndustry');
  var campus = document.getElementById('filterCampus');

  [search, stage, industry, campus].forEach(function(el) {
    if (el) el.addEventListener('input', applyFilters);
    if (el) el.addEventListener('change', applyFilters);
  });
}

function applyFilters() {
  var search = (document.getElementById('searchInput').value || '').toLowerCase();
  var stage = document.getElementById('filterStage').value;
  var industry = document.getElementById('filterIndustry').value;
  var campus = document.getElementById('filterCampus').value;

  document.querySelectorAll('#pipelineBody tr').forEach(function(row) {
    var company = (row.dataset.company || '').toLowerCase();
    var rowIndustry = row.dataset.industry || '';
    var rowCampus = row.dataset.campus || '';
    var rowStage = row.dataset.stage || '';

    var show = true;
    if (search && !company.includes(search)) show = false;
    if (stage && rowStage !== stage) show = false;
    if (industry && rowIndustry !== industry) show = false;
    if (campus && rowCampus !== campus) show = false;

    row.style.display = show ? '' : 'none';
  });
}

/* Sorting */
var currentSort = { field: 'total_score', dir: 'desc' };

function initSorting() {
  document.querySelectorAll('#pipelineTable th[data-sort]').forEach(function(th) {
    th.addEventListener('click', function() {
      var field = this.dataset.sort;
      if (currentSort.field === field) {
        currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort.field = field;
        currentSort.dir = 'asc';
      }

      document.querySelectorAll('#pipelineTable th').forEach(function(h) { h.classList.remove('sorted'); });
      this.classList.add('sorted');
      this.querySelector('.sort-arrow').textContent = currentSort.dir === 'asc' ? '\u25B2' : '\u25BC';

      sortTable();
    });
  });
}

function sortTable() {
  var tbody = document.getElementById('pipelineBody');
  var rows = Array.from(tbody.querySelectorAll('tr'));

  var colIndex = {
    'company_name': 0, 'industry': 1, 'hq_city': 2, 'nearest_campus': 3,
    'alignment_score': 4, 'proximity_score': 5, 'capacity_score': 6,
    'total_score': 7, 'pipeline_stage': 8,
  };

  var idx = colIndex[currentSort.field];
  var isNumeric = ['alignment_score', 'proximity_score', 'capacity_score', 'total_score'].includes(currentSort.field);

  rows.sort(function(a, b) {
    var aVal = a.cells[idx].textContent.trim();
    var bVal = b.cells[idx].textContent.trim();

    if (isNumeric) {
      aVal = parseInt(aVal) || 0;
      bVal = parseInt(bVal) || 0;
    } else {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (aVal < bVal) return currentSort.dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return currentSort.dir === 'asc' ? 1 : -1;
    return 0;
  });

  rows.forEach(function(row) { tbody.appendChild(row); });
}

/* Inline editing for score cells */
function initInlineEdit() {
  document.querySelectorAll('.editable[data-field]').forEach(function(cell) {
    cell.addEventListener('click', function() {
      if (this.querySelector('input')) return;

      var field = this.dataset.field;
      var id = this.dataset.id;
      var currentVal = this.textContent.trim();
      var self = this;

      var input = document.createElement('input');
      input.type = 'number';
      input.min = '0';
      input.max = '5';
      input.value = currentVal;
      input.style.width = '50px';

      this.textContent = '';
      this.appendChild(input);
      input.focus();
      input.select();

      function save() {
        var newVal = parseInt(input.value) || 0;
        if (newVal < 0) newVal = 0;
        if (newVal > 5) newVal = 5;
        self.textContent = newVal;

        if (newVal !== parseInt(currentVal)) {
          var body = {};
          body[field] = newVal;
          apiCall('/api/prospect/' + id, {
            method: 'PATCH',
            body: JSON.stringify(body),
          })
          .then(function(data) {
            var row = self.closest('tr');
            row.cells[7].innerHTML = '<strong style="color: var(--primary);">' + data.total_score + '</strong>';
            showToast('Score updated', 'success');
          })
          .catch(function() {
            self.textContent = currentVal;
            showToast('Failed to update', 'error');
          });
        }
      }

      input.addEventListener('blur', save);
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') { e.preventDefault(); save(); }
        if (e.key === 'Escape') { self.textContent = currentVal; }
      });
    });
  });
}

/* Stage select change */
function initStageSelects() {
  document.querySelectorAll('.stage-select').forEach(function(select) {
    select.addEventListener('change', function() {
      var id = this.dataset.id;
      apiCall('/api/prospect/' + id, {
        method: 'PATCH',
        body: JSON.stringify({ pipeline_stage: this.value }),
      })
      .then(function() {
        select.closest('tr').dataset.stage = select.value;
        showToast('Stage updated', 'success');
      })
      .catch(function() { showToast('Failed to update', 'error'); });
    });
  });
}

/* Add prospect */
function showAddProspect() {
  document.getElementById('addProspectForm').style.display = '';
  document.getElementById('newCompanyName').focus();
}

function hideAddProspect() {
  document.getElementById('addProspectForm').style.display = 'none';
}

function addProspect() {
  var name = document.getElementById('newCompanyName').value.trim();
  if (!name) { showToast('Company name required', 'error'); return; }

  apiCall('/api/prospect', {
    method: 'POST',
    body: JSON.stringify({
      company_name: name,
      industry: document.getElementById('newIndustry').value,
      hq_city: document.getElementById('newHqCity').value,
      nearest_campus: document.getElementById('newCampus').value,
      foundation_name: document.getElementById('newFoundation').value,
      focus_areas: document.getElementById('newFocus').value,
    })
  }).then(function() {
    showToast('Prospect added');
    setTimeout(function() { location.reload(); }, 500);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* Auto-score all */
function autoScoreAll() {
  apiCall('/api/auto-score-all', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 500);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* Fetch 990 */
function fetch990(id) {
  showToast('Fetching 990 data...');
  apiCall('/api/prospect/' + id + '/fetch-990', { method: 'POST' })
    .then(function(data) {
      showToast(data.message || 'Done', 'success');
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* Generate email */
function generateEmail(id) {
  showToast('Generating email...');
  apiCall('/api/generate-email/' + id, { method: 'POST' })
    .then(function(data) {
      showToast(data.message || 'Email generated', 'success');
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

/* Import / Export */
function importExcel() {
  apiCall('/api/import-excel', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 1000);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function resetDB() {
  if (!confirm('This will DELETE all data and re-import from Excel. Are you sure?')) return;
  apiCall('/api/reset-db', { method: 'POST' })
    .then(function(data) {
      showToast(data.message);
      setTimeout(function() { location.reload(); }, 1000);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
