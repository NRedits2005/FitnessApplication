document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('session');
  if (!root) return;
  const display = document.getElementById('timer-display');
  const label = document.getElementById('state-label');
  const message = document.getElementById('timer-message');
  const pauseButton = document.getElementById('pause-timer');
  const skipSetButton = document.getElementById('skip-set');
  const skipRestButton = document.getElementById('skip-rest');
  const repsInput = document.getElementById('set-reps');
  const weightInput = document.getElementById('set-weight');
  const csrf = document.querySelector('.csrf-token input').value;
  let currentSet = Number(root.dataset.current), state = 'WORK', remaining = 0, timer = null, saving = false, paused = false, lastWasSkipped = false;

  const format = seconds => `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  const render = () => { display.textContent = format(Math.max(0, remaining)); };
  const durationFor = nextState => Number(root.dataset[nextState === 'WORK' ? 'work' : 'rest']);
  const setControls = () => {
    const active = state === 'WORK' || state === 'REST';
    pauseButton.hidden = !active;
    skipSetButton.hidden = state !== 'WORK';
    skipRestButton.hidden = state !== 'REST';
  };
  const setState = (nextState, text) => {
    state = nextState;
    remaining = durationFor(nextState);
    label.textContent = nextState;
    message.textContent = text || (nextState === 'WORK' ? 'Complete your repetitions during this set.' : 'Take a break before your next set.');
    pauseButton.textContent = paused ? 'Resume' : 'Pause';
    setControls(); render();
  };
  const updateProgress = () => {
    document.getElementById('set-count').textContent = `Set ${currentSet} of ${root.dataset.sets}`;
    document.querySelectorAll('.progress i').forEach((dot, index) => { dot.className = index + 1 < currentSet ? 'done' : index + 1 === currentSet ? 'current' : ''; });
  };
  const finishWorkout = redirect => {
    clearInterval(timer); state = 'COMPLETE'; paused = false; remaining = 0; label.textContent = 'COMPLETE'; message.textContent = lastWasSkipped ? 'Workout complete. Your final set was skipped.' : 'Workout complete!'; setControls(); render(); window.setTimeout(() => { window.location.href = redirect; }, 700);
  };
  const saveSet = async skipped => {
    if (saving) return;
    saving = true;
    const body = new FormData();
    if (skipped) body.append('skip', '1');
    else {
      body.append('reps', repsInput.value);
      if (weightInput) body.append('weight', weightInput.value);
    }
    const response = await fetch(root.dataset.completeUrl, { method: 'POST', headers: { 'X-CSRFToken': csrf }, body });
    if (!response.ok) {
      const result = await response.json();
      saving = false;
      message.textContent = result.error || 'Unable to save this set. Please try again.';
      return;
    }
    const result = await response.json(); saving = false; lastWasSkipped = Boolean(result.skipped);
    if (result.complete) { finishWorkout(result.redirect); return; }
    paused = false;
    setState('REST', lastWasSkipped ? `Set ${result.set_number} skipped. Take a break before your next set.` : 'Set complete. Take a break before your next set.');
  };
  const beginNextSet = () => { currentSet += 1; lastWasSkipped = false; updateProgress(); setState('WORK'); };
  const getReady = delay => { state = 'GET_READY'; paused = false; pauseButton.textContent = 'Pause'; label.textContent = 'GET READY'; message.textContent = 'Prepare for your next set.'; remaining = 0; setControls(); render(); window.setTimeout(() => { if (state === 'GET_READY') beginNextSet(); }, delay); };

  setState('WORK');
  timer = window.setInterval(async () => {
    if (saving || paused || state === 'COMPLETE' || state === 'GET_READY') return;
    remaining -= 1; render(); if (remaining > 0) return;
    if (state === 'WORK') await saveSet(false); else getReady(700);
  }, 1000);
  pauseButton.addEventListener('click', () => {
    paused = !paused; pauseButton.textContent = paused ? 'Resume' : 'Pause';
    if (paused) { label.textContent = 'PAUSED'; message.textContent = 'Timer paused. Resume when you are ready.'; }
    else { label.textContent = state; message.textContent = state === 'WORK' ? 'Complete your repetitions during this set.' : 'Take a break before your next set.'; }
  });
  skipSetButton.addEventListener('click', () => { if (state === 'WORK' && !saving) saveSet(true); });
  skipRestButton.addEventListener('click', () => { if (state === 'REST') getReady(250); });
  window.addEventListener('beforeunload', () => clearInterval(timer));
});
