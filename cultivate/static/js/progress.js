/* Progress page — weekly goals */

function incrementGoal(goalId) {
  apiCall('/api/weekly-goal/' + goalId + '/increment', { method: 'POST' })
    .then(function() {
      showToast('+1');
      setTimeout(function() { location.reload(); }, 400);
    }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}

function createGoal(category) {
  apiCall('/api/weekly-goal', {
    method: 'POST',
    body: JSON.stringify({ category: category, target: 5, actual: 1 })
  }).then(function() {
    showToast('Goal created (+1)');
    setTimeout(function() { location.reload(); }, 400);
  }).catch(function(e) { showToast('Error: ' + e.message, 'error'); });
}
