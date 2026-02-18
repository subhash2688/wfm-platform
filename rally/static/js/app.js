/* Rally — Global utility functions */

function showToast(message, type) {
  type = type || 'success';
  var container = document.getElementById('toastContainer');
  var toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s';
    setTimeout(function() { toast.remove(); }, 300);
  }, 3000);
}

function apiCall(url, options) {
  options = options || {};
  var defaults = {
    headers: { 'Content-Type': 'application/json' },
  };
  return fetch(url, Object.assign({}, defaults, options))
    .then(function(r) {
      if (!r.ok) throw new Error('Request failed');
      return r.json();
    });
}

/* Date/time formatting helpers */
function formatDate(isoDate) {
  if (!isoDate) return '';
  var d = new Date(isoDate + 'T00:00:00');
  var options = { weekday: 'short', month: 'short', day: 'numeric' };
  return d.toLocaleDateString('en-US', options);
}

function formatTime(timeStr) {
  if (!timeStr) return '';
  var parts = timeStr.split(':');
  var h = parseInt(parts[0]);
  var m = parts[1];
  var ampm = h >= 12 ? 'PM' : 'AM';
  if (h > 12) h -= 12;
  if (h === 0) h = 12;
  return h + ':' + m + ' ' + ampm;
}

function campusClass(campus) {
  if (!campus) return '';
  if (campus.indexOf('De Anza') !== -1) return 'de-anza';
  if (campus.indexOf('Foothill') !== -1) return 'foothill';
  if (campus.indexOf('Chabot') !== -1) return 'chabot';
  return '';
}

function campusCssClass(campus) {
  if (!campus) return '';
  if (campus.indexOf('De Anza') !== -1) return 'campus-de-anza';
  if (campus.indexOf('Foothill') !== -1) return 'campus-foothill';
  if (campus.indexOf('Chabot') !== -1) return 'campus-chabot';
  return '';
}

function fillClass(filled, required) {
  var pct = required > 0 ? filled / required : 1;
  if (pct >= 1) return 'full';
  if (pct >= 0.5) return 'partial';
  return 'critical';
}
