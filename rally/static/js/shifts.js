/* Rally — Shifts page: filters, sorting, CRUD */

document.addEventListener('DOMContentLoaded', function() {
  initShiftFilters();
  initShiftSorting();
});

function initShiftFilters() {
  var search = document.getElementById('searchInput');
  var campus = document.getElementById('filterCampus');
  var status = document.getElementById('filterStatus');
  var type = document.getElementById('filterType');

  [search, campus, status, type].forEach(function(el) {
    if (el) {
      el.addEventListener('input', applyShiftFilters);
      el.addEventListener('change', applyShiftFilters);
    }
  });
}

function applyShiftFilters() {
  var search = (document.getElementById('searchInput').value || '').toLowerCase();
  var campus = document.getElementById('filterCampus').value;
  var status = document.getElementById('filterStatus').value;
  var type = document.getElementById('filterType').value;

  document.querySelectorAll('#shiftsBody tr').forEach(function(row) {
    var rowCampus = row.dataset.campus || '';
    var rowStatus = row.dataset.status || '';
    var rowType = row.dataset.type || '';
    var rowText = row.textContent.toLowerCase();

    var show = true;
    if (search && rowText.indexOf(search) === -1) show = false;
    if (campus && rowCampus !== campus) show = false;
    if (status && rowStatus !== status) show = false;
    if (type && rowType !== type) show = false;

    row.style.display = show ? '' : 'none';
  });
}

/* Sorting */
var shiftSort = { field: 'date', dir: 'asc' };

function initShiftSorting() {
  document.querySelectorAll('#shiftsTable th[data-sort]').forEach(function(th) {
    th.addEventListener('click', function() {
      var field = this.dataset.sort;
      if (shiftSort.field === field) {
        shiftSort.dir = shiftSort.dir === 'asc' ? 'desc' : 'asc';
      } else {
        shiftSort.field = field;
        shiftSort.dir = 'asc';
      }
      document.querySelectorAll('#shiftsTable th').forEach(function(h) { h.classList.remove('sorted'); });
      this.classList.add('sorted');
      var arrow = this.querySelector('.sort-arrow');
      if (arrow) arrow.textContent = shiftSort.dir === 'asc' ? '\u25B2' : '\u25BC';
      sortShiftsTable();
    });
  });
}

function sortShiftsTable() {
  var tbody = document.getElementById('shiftsBody');
  if (!tbody) return;
  var rows = Array.from(tbody.querySelectorAll('tr'));

  rows.sort(function(a, b) {
    var aVal = a.dataset[shiftSort.field] || '';
    var bVal = b.dataset[shiftSort.field] || '';

    if (shiftSort.field === 'fill') {
      aVal = parseInt(aVal) || 0;
      bVal = parseInt(bVal) || 0;
    }

    if (aVal < bVal) return shiftSort.dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return shiftSort.dir === 'asc' ? 1 : -1;
    return 0;
  });

  rows.forEach(function(row) { tbody.appendChild(row); });
}

/* CRUD */
function showCreateShift() {
  var form = document.getElementById('createShiftForm');
  if (form) form.style.display = form.style.display === 'none' ? '' : 'none';
}

function createShift(e) {
  e.preventDefault();
  var data = Object.fromEntries(new FormData(e.target));
  data.required_count = parseInt(data.required_count) || 4;

  apiCall('/api/shifts', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  .then(function(d) {
    if (d.error) { showToast(d.error, 'error'); }
    else { showToast('Shift created!'); setTimeout(function() { location.reload(); }, 500); }
  })
  .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteShift(id) {
  if (!confirm('Delete this shift?')) return;
  apiCall('/api/shifts/' + id, { method: 'DELETE' })
    .then(function() {
      showToast('Shift deleted');
      setTimeout(function() { location.reload(); }, 500);
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
