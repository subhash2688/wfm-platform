/* Rally Volunteer App — client-side interactions */

function signupForShift(shiftId) {
  apiCall('/v/api/signup/' + shiftId, { method: 'POST' })
    .then(function(data) {
      showToast("You're in — a student will eat because of you.", 'success');
      setTimeout(function() { location.reload(); }, 1000);
    })
    .catch(function(err) {
      showToast('Could not sign up. Please try again.', 'error');
    });
}

function cancelSignup(signupId) {
  if (!confirm('Cancel this signup?')) return;
  apiCall('/v/api/cancel/' + signupId, { method: 'POST' })
    .then(function(data) {
      showToast(data.message || 'Cancelled.', 'success');
      setTimeout(function() { location.reload(); }, 600);
    })
    .catch(function(err) {
      showToast('Could not cancel. Please try again.', 'error');
    });
}

function checkIn(shiftId) {
  apiCall('/v/api/checkin/' + shiftId, { method: 'POST' })
    .then(function(data) {
      showToast("You're checked in. Thank you for showing up today.", 'success');
      setTimeout(function() { location.reload(); }, 1000);
    })
    .catch(function(err) {
      showToast('Could not check in. Please try again.', 'error');
    });
}

function updateProfile() {
  var campusCbs = document.querySelectorAll('#profileForm input[name="campuses"]:checked');
  var campuses = [];
  campusCbs.forEach(function(cb) { campuses.push(cb.value); });

  var typeCbs = document.querySelectorAll('#profileForm input[name="shift_types"]:checked');
  var shiftTypes = [];
  typeCbs.forEach(function(cb) { shiftTypes.push(cb.value); });

  var youthCb = document.querySelector('#profileForm input[name="is_youth"]');
  var isYouth = youthCb ? youthCb.checked : false;

  // Collect availability grid: {day: [slots]}
  var availability = {};
  document.querySelectorAll('.vol-avail-cb:checked').forEach(function(cb) {
    var day = cb.dataset.day;
    var slot = cb.dataset.slot;
    if (!availability[day]) availability[day] = [];
    availability[day].push(slot);
  });

  apiCall('/v/api/profile', {
    method: 'POST',
    body: JSON.stringify({
      preferred_campuses: campuses,
      preferred_shift_types: shiftTypes,
      is_youth: isYouth,
      availability: availability,
    }),
  })
    .then(function(data) {
      showToast(data.message || 'Saved!', 'success');
    })
    .catch(function(err) {
      showToast('Could not save. Please try again.', 'error');
    });
}

function uploadPhoto(input) {
  if (!input.files || !input.files[0]) return;

  var file = input.files[0];
  if (file.size > 5 * 1024 * 1024) {
    showToast('Photo must be under 5 MB.', 'error');
    return;
  }

  var formData = new FormData();
  formData.append('photo', file);

  fetch('/v/api/photo', {
    method: 'POST',
    body: formData,
  })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.success) {
        showToast('Photo updated!', 'success');
        // Update profile avatar
        var wrapper = document.querySelector('.vol-avatar-wrapper');
        if (wrapper) {
          var initials = document.getElementById('avatarInitials');
          var img = document.getElementById('avatarImg');
          if (initials) {
            initials.remove();
            var newImg = document.createElement('img');
            newImg.src = data.photo_url;
            newImg.alt = '';
            newImg.className = 'vol-avatar-img';
            newImg.id = 'avatarImg';
            wrapper.insertBefore(newImg, wrapper.firstChild);
          } else if (img) {
            img.src = data.photo_url;
          }
        }
        // Update header avatar
        var headerAvatar = document.getElementById('headerAvatar');
        if (headerAvatar) {
          if (headerAvatar.tagName === 'IMG') {
            headerAvatar.src = data.photo_url;
          } else {
            var newHeaderImg = document.createElement('img');
            newHeaderImg.src = data.photo_url;
            newHeaderImg.alt = '';
            newHeaderImg.className = 'vol-header-avatar';
            newHeaderImg.id = 'headerAvatar';
            headerAvatar.parentNode.replaceChild(newHeaderImg, headerAvatar);
          }
        }
      } else {
        showToast(data.error || 'Upload failed.', 'error');
      }
    })
    .catch(function() {
      showToast('Could not upload photo. Please try again.', 'error');
    });
}

function dismissBanner() {
  var banner = document.getElementById('prefsBanner');
  if (banner) {
    banner.style.display = 'none';
    sessionStorage.setItem('prefsBannerDismissed', '1');
  }
}

// On page load, check if banner was dismissed this session
document.addEventListener('DOMContentLoaded', function() {
  if (sessionStorage.getItem('prefsBannerDismissed') === '1') {
    var banner = document.getElementById('prefsBanner');
    if (banner) banner.style.display = 'none';
  }
});
