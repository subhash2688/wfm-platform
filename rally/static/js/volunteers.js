/* Rally — Volunteers page: filters, sorting, CRUD, CSV export */

document.addEventListener('DOMContentLoaded', function() {
  initVolunteerFilters();
  initVolunteerSorting();
});

function initVolunteerFilters() {
  var search = document.getElementById('searchInput');
  var campus = document.getElementById('filterCampus');
  var status = document.getElementById('filterStatus');

  [search, campus, status].forEach(function(el) {
    if (el) {
      el.addEventListener('input', applyVolunteerFilters);
      el.addEventListener('change', applyVolunteerFilters);
    }
  });
}

function applyVolunteerFilters() {
  var search = (document.getElementById('searchInput').value || '').toLowerCase();
  var campus = document.getElementById('filterCampus').value;
  var status = document.getElementById('filterStatus').value;

  document.querySelectorAll('#volunteersBody tr').forEach(function(row) {
    var rowCampuses = row.dataset.campuses || '';
    var rowStatus = row.dataset.status || '';
    var rowText = row.textContent.toLowerCase();

    var show = true;
    if (search && rowText.indexOf(search) === -1) show = false;
    if (campus && rowCampuses.indexOf(campus) === -1) show = false;
    if (status && rowStatus !== status) show = false;

    row.style.display = show ? '' : 'none';
  });
}

/* Sorting */
var volSort = { field: 'name', dir: 'asc' };

function initVolunteerSorting() {
  document.querySelectorAll('#volunteersTable th[data-sort]').forEach(function(th) {
    th.addEventListener('click', function() {
      var field = this.dataset.sort;
      if (volSort.field === field) {
        volSort.dir = volSort.dir === 'asc' ? 'desc' : 'asc';
      } else {
        volSort.field = field;
        volSort.dir = 'asc';
      }
      document.querySelectorAll('#volunteersTable th').forEach(function(h) { h.classList.remove('sorted'); });
      this.classList.add('sorted');
      var arrow = this.querySelector('.sort-arrow');
      if (arrow) arrow.textContent = volSort.dir === 'asc' ? '\u25B2' : '\u25BC';
      sortVolunteersTable();
    });
  });
}

function sortVolunteersTable() {
  var tbody = document.getElementById('volunteersBody');
  if (!tbody) return;
  var rows = Array.from(tbody.querySelectorAll('tr'));
  var numericFields = ['shifts', 'hours', 'reliability'];

  rows.sort(function(a, b) {
    var aVal = a.dataset[volSort.field] || '';
    var bVal = b.dataset[volSort.field] || '';

    if (numericFields.indexOf(volSort.field) !== -1) {
      aVal = parseFloat(aVal) || 0;
      bVal = parseFloat(bVal) || 0;
    } else {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (aVal < bVal) return volSort.dir === 'asc' ? -1 : 1;
    if (aVal > bVal) return volSort.dir === 'asc' ? 1 : -1;
    return 0;
  });

  rows.forEach(function(row) { tbody.appendChild(row); });
}

/* CRUD */
function showCreateVolunteer() {
  var form = document.getElementById('createVolunteerForm');
  if (form) form.style.display = form.style.display === 'none' ? '' : 'none';
}

function createVolunteer(e) {
  e.preventDefault();
  var formData = new FormData(e.target);
  var data = {};
  data.first_name = formData.get('first_name');
  data.last_name = formData.get('last_name');
  data.phone = formData.get('phone');
  data.email = formData.get('email');
  data.preferred_campuses = formData.getAll('preferred_campuses');
  data.is_youth = formData.get('is_youth') === 'on';

  apiCall('/api/volunteers', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  .then(function(d) {
    if (d.error) { showToast(d.error, 'error'); }
    else { showToast('Volunteer added!'); setTimeout(function() { location.reload(); }, 500); }
  })
  .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function deleteVolunteer(id) {
  if (!confirm('Remove this volunteer?')) return;
  apiCall('/api/volunteers/' + id, { method: 'DELETE' })
    .then(function() {
      showToast('Volunteer removed');
      setTimeout(function() { location.reload(); }, 500);
    })
    .catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
