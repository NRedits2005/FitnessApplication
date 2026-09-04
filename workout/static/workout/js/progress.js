(function () {
  'use strict';

  const dataElement = document.getElementById('progress-chart-data');
  if (!dataElement) return;

  let chartData;
  try {
    chartData = JSON.parse(dataElement.textContent);
  } catch (err) {
    console.error('Failed to parse progress chart data', err);
    return;
  }

  const { frequency = [], volume = [], activity = {}, heatmapStart, heatmapEnd, dayDetails = {} } = chartData;

  // Month names
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function formatDateIso(dateObj) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  function formatShortDate(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length < 3) return dateStr;
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    return `${MONTHS[m]} ${d}`;
  }

  function formatFullDate(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length < 3) return dateStr;
    const y = parts[0];
    const m = parseInt(parts[1], 10) - 1;
    const d = parseInt(parts[2], 10);
    return `${MONTHS[m]} ${d}, ${y}`;
  }

  // --- 1. 12-MONTH ACTIVITY HEATMAP (Horizontal Week Columns) ---
  const heatmapEl = document.getElementById('activity-heatmap');
  const heatmapMonthsEl = document.getElementById('heatmap-months');

  if (heatmapEl && heatmapStart && heatmapEnd) {
    const start = new Date(heatmapStart + 'T00:00:00');
    const end = new Date(heatmapEnd + 'T00:00:00');

    // Align start to preceding Monday (Monday = 0, Sunday = 6)
    const dayOfWeek = (start.getDay() + 6) % 7;
    const alignedStart = new Date(start);
    alignedStart.setDate(alignedStart.getDate() - dayOfWeek);

    const totalDays = Math.round((end - alignedStart) / (1000 * 60 * 60 * 24)) + 1;
    const totalWeeks = Math.ceil(totalDays / 7);

    // Clear previous contents
    if (heatmapMonthsEl) heatmapMonthsEl.innerHTML = '';
    heatmapEl.innerHTML = '';

    let lastMonth = -1;

    for (let w = 0; w < totalWeeks; w++) {
      const weekDate = new Date(alignedStart);
      weekDate.setDate(weekDate.getDate() + w * 7);
      const colMonth = weekDate.getMonth();

      // Month tag for this week column
      if (heatmapMonthsEl) {
        const colSpan = document.createElement('span');
        colSpan.className = 'heatmap-month-label';
        // Show month label when month changes and within first 3 weeks of month
        if (colMonth !== lastMonth && weekDate.getDate() <= 21) {
          colSpan.textContent = MONTHS[colMonth];
          lastMonth = colMonth;
        } else {
          colSpan.textContent = '';
        }
        heatmapMonthsEl.appendChild(colSpan);
      }

      // Week column containing 7 days vertically (Mon=0..Sun=6)
      const weekCol = document.createElement('div');
      weekCol.className = 'heatmap-week-col';

      for (let r = 0; r < 7; r++) {
        const cellDate = new Date(alignedStart);
        cellDate.setDate(cellDate.getDate() + w * 7 + r);
        const iso = formatDateIso(cellDate);

        const cell = document.createElement('button');
        cell.type = 'button';
        cell.className = 'heatmap-cell';
        cell.dataset.date = iso;

        if (cellDate < start || cellDate > end) {
          cell.classList.add('out-of-range');
          cell.disabled = true;
          cell.setAttribute('aria-hidden', 'true');
        } else {
          const count = activity[iso] || 0;
          let level = 0;
          if (count === 1) level = 1;
          else if (count === 2) level = 2;
          else if (count >= 3) level = 3;

          cell.classList.add(`level-${level}`);
          const dateFmt = formatShortDate(iso);
          const workoutText = count === 1 ? '1 workout' : `${count} workouts`;
          cell.setAttribute('aria-label', `${dateFmt}: ${workoutText}`);
          cell.setAttribute('title', `${dateFmt}: ${workoutText}`);

          cell.addEventListener('click', function () {
            document.querySelectorAll('.heatmap-cell.selected-day').forEach(c => c.classList.remove('selected-day'));
            cell.classList.add('selected-day');
            openDayModal(iso);
          });
        }
        weekCol.appendChild(cell);
      }
      heatmapEl.appendChild(weekCol);
    }
  }

  // --- 2. INTERACTIVE DAY DETAILS MODAL ---
  const backdrop = document.getElementById('heatmap-modal-backdrop');
  const closeBtn = document.getElementById('modal-close-btn');
  const modalDateTitle = document.getElementById('modal-date-title');
  const modalHasWorkouts = document.getElementById('modal-content-has-workouts');
  const modalEmpty = document.getElementById('modal-content-empty');
  const modalWorkoutCountText = document.getElementById('modal-workout-count-text');
  const modalTotalTimeText = document.getElementById('modal-total-time-text');
  const modalWorkoutsContainer = document.getElementById('modal-workouts-container');
  const modalSumExercises = document.getElementById('modal-sum-exercises');
  const modalSumSets = document.getElementById('modal-sum-sets');
  const modalSumReps = document.getElementById('modal-sum-reps');
  const modalSumVolume = document.getElementById('modal-sum-volume');
  const modalViewDayDetailsBtn = document.getElementById('modal-view-day-details-btn');

  function openDayModal(dateIso) {
    if (!backdrop) return;
    const formatted = formatFullDate(dateIso);
    if (modalDateTitle) modalDateTitle.textContent = formatted;

    const dayInfo = dayDetails[dateIso];
    const workoutCount = dayInfo ? dayInfo.workout_count : (activity[dateIso] || 0);

    if (workoutCount > 0 && dayInfo) {
      if (modalHasWorkouts) modalHasWorkouts.hidden = false;
      if (modalEmpty) modalEmpty.hidden = true;

      const cText = workoutCount === 1 ? '1 Workout Completed' : `${workoutCount} Workouts Completed`;
      if (modalWorkoutCountText) modalWorkoutCountText.textContent = cText;
      if (modalTotalTimeText) modalTotalTimeText.textContent = dayInfo.total_duration || '—';

      if (modalSumExercises) modalSumExercises.textContent = dayInfo.total_exercises || 0;
      if (modalSumSets) modalSumSets.textContent = dayInfo.total_sets || 0;
      if (modalSumReps) modalSumReps.textContent = dayInfo.total_reps || 0;
      if (modalSumVolume) modalSumVolume.textContent = `${dayInfo.total_volume || '0'} kg`;

      if (modalViewDayDetailsBtn) {
        modalViewDayDetailsBtn.href = dayInfo.primary_detail_url || '/history/';
      }

      if (modalWorkoutsContainer) {
        modalWorkoutsContainer.innerHTML = '';
        (dayInfo.workouts || []).forEach(w => {
          const card = document.createElement('div');
          card.className = 'modal-workout-card';
          card.innerHTML = `
            <div class="workout-card-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M5 9a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V9zm-3 2a1 1 0 0 1 1-1h1v4H3a1 1 0 0 1-1-1v-2zm6-1h8v4H8v-4zm8-1a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1V9zm3 2h1a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-1v-4z"/>
              </svg>
            </div>
            <div class="workout-card-main">
              <div class="workout-card-title">Workout</div>
              <div class="workout-card-sub">${w.time ? w.time + ' • ' : ''}${escapeHtml(w.focus || 'Full Body')}</div>
            </div>
            <div class="workout-card-right">
              <div class="workout-card-dur">${escapeHtml(w.duration)}</div>
              <div class="workout-card-durlbl">Duration</div>
            </div>
          `;
          modalWorkoutsContainer.appendChild(card);
        });
      }
    } else {
      if (modalHasWorkouts) modalHasWorkouts.hidden = true;
      if (modalEmpty) modalEmpty.hidden = false;
    }

    backdrop.style.display = 'flex';
    backdrop.removeAttribute('hidden');
    backdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  }

  function closeDayModal() {
    if (!backdrop) return;
    backdrop.style.display = 'none';
    backdrop.setAttribute('hidden', '');
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
  }

  if (closeBtn) closeBtn.addEventListener('click', closeDayModal);
  if (backdrop) {
    backdrop.addEventListener('click', function (e) {
      if (e.target === backdrop) closeDayModal();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && backdrop && !backdrop.hidden) {
      closeDayModal();
    }
  });

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // --- 3. CHARTS RENDERING (SVG) ---

  // A. Workout Frequency Bar Chart
  const freqContainer = document.getElementById('frequency-chart');
  if (freqContainer) {
    renderFrequencyBarChart(freqContainer, frequency);
  }

  function renderFrequencyBarChart(container, data) {
    container.innerHTML = '';
    if (!data || data.length === 0) {
      container.innerHTML = '<div class="chart-empty">No workouts in this period</div>';
      return;
    }

    const width = 520;
    const height = 230;
    const padLeft = 32;
    const padRight = 20;
    const padTop = 32;
    const padBottom = 54;

    const chartW = width - padLeft - padRight;
    const chartH = height - padTop - padBottom;

    const maxVal = Math.max(6, ...data.map(d => d.value));
    const yTicks = [0, 1, 2, 3, 4, 5, 6];
    if (maxVal > 6) {
      yTicks.length = 0;
      const step = Math.ceil(maxVal / 5);
      for (let i = 0; i <= maxVal; i += step) yTicks.push(i);
      if (yTicks[yTicks.length - 1] < maxVal) yTicks.push(yTicks[yTicks.length - 1] + step);
    }
    const tickMax = yTicks[yTicks.length - 1];

    let svg = `<svg class="analytics-chart-svg" viewBox="0 0 ${width} ${height}">`;

    // Horizontal grid lines & Y labels
    yTicks.forEach(tick => {
      const y = padTop + chartH - (tick / tickMax) * chartH;
      svg += `
        <line class="chart-grid-line" x1="${padLeft}" y1="${y}" x2="${width - padRight}" y2="${y}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,3" />
        <text class="chart-axis-label" x="${padLeft - 10}" y="${y + 4}" text-anchor="end" fill="#64748b" font-size="11" font-weight="600">${tick}</text>
      `;
    });

    // Bars
    const count = data.length;
    const colWidth = chartW / count;
    const barWidth = Math.min(28, Math.max(10, colWidth * 0.45));
    const showEveryN = count <= 10 ? 1 : (count <= 20 ? 2 : (count <= 35 ? 5 : 7));

    data.forEach((d, i) => {
      const barH = d.value > 0 ? (d.value / tickMax) * chartH : 0;
      const x = padLeft + i * colWidth + (colWidth - barWidth) / 2;
      const y = padTop + chartH - barH;
      const label = d.label || formatShortDate(d.date);

      if (d.value > 0) {
        svg += `
          <rect class="chart-bar" x="${x}" y="${y}" width="${barWidth}" height="${barH}" rx="3" ry="3" fill="#006948">
            <title>${label}: ${d.value} workout${d.value > 1 ? 's' : ''}</title>
          </rect>
        `;
      }

      // Value label on top of bar (or at baseline for 0)
      const valY = d.value > 0 ? (y - 8) : (padTop + chartH - 8);
      svg += `
        <text class="chart-bar-value" x="${x + barWidth / 2}" y="${valY}" text-anchor="middle" fill="#0f172a" font-size="12" font-weight="700">${d.value}</text>
      `;

      // X date label
      if (i % showEveryN === 0 || i === count - 1) {
        const textX = padLeft + i * colWidth + colWidth / 2;
        svg += `
          <text class="chart-axis-label" x="${textX}" y="${height - 28}" text-anchor="middle" fill="#64748b" font-size="11" font-weight="500">${label}</text>
        `;
      }
    });

    // Bottom Legend
    svg += `
      <g transform="translate(${width / 2 - 38}, ${height - 8})">
        <rect x="0" y="-10" width="12" height="12" rx="2" fill="#006948" />
        <text x="18" y="0" fill="#475569" font-size="11" font-weight="600">Workouts</text>
      </g>
    `;

    svg += '</svg>';
    container.innerHTML = svg;
  }

  // B. Training Volume Line Chart
  const volContainer = document.getElementById('volume-chart');
  if (volContainer) {
    renderVolumeLineChart(volContainer, volume);
  }

  function renderVolumeLineChart(container, data) {
    container.innerHTML = '';
    if (!data || data.length === 0) {
      container.innerHTML = '<div class="chart-empty">No volume recorded in this period</div>';
      return;
    }

    const width = 520;
    const height = 230;
    const padLeft = 44;
    const padRight = 24;
    const padTop = 32;
    const padBottom = 54;

    const chartW = width - padLeft - padRight;
    const chartH = height - padTop - padBottom;

    const maxVal = Math.max(100, ...data.map(d => d.value));
    // Determine clean tick intervals (e.g. 5 steps)
    const rawStep = maxVal / 5;
    let step = 50;
    if (rawStep > 500) step = Math.ceil(rawStep / 100) * 100;
    else if (rawStep > 100) step = Math.ceil(rawStep / 50) * 50;
    else if (rawStep > 20) step = Math.ceil(rawStep / 10) * 10;
    else step = Math.ceil(rawStep);

    const yTicks = [0];
    while (yTicks[yTicks.length - 1] < maxVal) {
      yTicks.push(yTicks[yTicks.length - 1] + step);
    }
    const tickMax = yTicks[yTicks.length - 1];

    let svg = `<svg class="analytics-chart-svg" viewBox="0 0 ${width} ${height}">`;

    // Linear gradient definition for area under curve
    svg += `
      <defs>
        <linearGradient id="volGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#006948" stop-opacity="0.14" />
          <stop offset="100%" stop-color="#006948" stop-opacity="0.01" />
        </linearGradient>
      </defs>
    `;

    // Horizontal grid lines
    yTicks.forEach((tick) => {
      const y = padTop + chartH - (tick / tickMax) * chartH;
      svg += `
        <line class="chart-grid-line" x1="${padLeft}" y1="${y}" x2="${width - padRight}" y2="${y}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,3" />
        <text class="chart-axis-label" x="${padLeft - 10}" y="${y + 4}" text-anchor="end" fill="#64748b" font-size="11" font-weight="600">${Math.round(tick)}</text>
      `;
    });

    const count = data.length;
    const points = [];
    const showEveryN = count <= 10 ? 1 : (count <= 20 ? 2 : (count <= 35 ? 5 : 7));

    data.forEach((d, i) => {
      const x = count === 1 ? padLeft + chartW / 2 : padLeft + (i / (count - 1)) * chartW;
      const y = padTop + chartH - (d.value / tickMax) * chartH;
      points.push({ x, y, value: d.value, date: d.date, label: d.label });
    });

    // Area fill under line
    if (points.length > 1) {
      const polyPoints = points.map(p => `${p.x},${p.y}`).join(' ');
      const areaPoints = `${padLeft},${padTop + chartH} ${polyPoints} ${points[points.length - 1].x},${padTop + chartH}`;
      svg += `<polygon fill="url(#volGradient)" points="${areaPoints}" />`;
      svg += `<polyline fill="none" stroke="#006948" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" points="${polyPoints}" />`;
    } else if (points.length === 1) {
      svg += `<line x1="${padLeft}" y1="${points[0].y}" x2="${width - padRight}" y2="${points[0].y}" stroke="#006948" stroke-width="2.5" stroke-linecap="round" />`;
    }

    // Circles, numbers on top, and X Labels
    points.forEach((p, i) => {
      const label = p.label || formatShortDate(p.date);
      svg += `
        <circle class="chart-point" cx="${p.x}" cy="${p.y}" r="4.5" fill="#006948" stroke="#ffffff" stroke-width="1.5">
          <title>${label}: ${p.value.toLocaleString()} kg</title>
        </circle>
      `;

      // Value label on top of point
      const valFmt = p.value >= 1000 ? Math.round(p.value).toLocaleString() : Math.round(p.value);
      svg += `
        <text class="chart-point-value" x="${p.x}" y="${p.y - 10}" text-anchor="middle" fill="#006948" font-size="11.5" font-weight="700">${valFmt}</text>
      `;

      // X date label
      if (i % showEveryN === 0 || i === count - 1) {
        svg += `
          <text class="chart-axis-label" x="${p.x}" y="${height - 28}" text-anchor="middle" fill="#64748b" font-size="11" font-weight="500">${label}</text>
        `;
      }
    });

    // Bottom Legend
    svg += `
      <g transform="translate(${width / 2 - 45}, ${height - 8})">
        <line x1="0" y1="-4" x2="16" y2="-4" stroke="#006948" stroke-width="2" />
        <circle cx="8" cy="-4" r="3.5" fill="#006948" />
        <text x="22" y="0" fill="#475569" font-size="11" font-weight="600">Volume (kg)</text>
      </g>
    `;

    svg += '</svg>';
    container.innerHTML = svg;
  }
})();
