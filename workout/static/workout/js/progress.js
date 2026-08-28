(function () {
  const dataElement = document.getElementById('progress-chart-data');
  if (!dataElement) return;
  const data = JSON.parse(dataElement.textContent);

  function drawChart(containerId, series, label, color, suffix) {
    const container = document.getElementById(containerId);
    if (!container || !series.length) return;
    const width = 720, height = 245, pad = { top: 20, right: 18, bottom: 42, left: 48 };
    const max = Math.max(...series.map(point => point.value), 1);
    const usableWidth = width - pad.left - pad.right;
    const usableHeight = height - pad.top - pad.bottom;
    const x = index => pad.left + (series.length === 1 ? usableWidth / 2 : index * usableWidth / (series.length - 1));
    const y = value => pad.top + usableHeight - (value / max) * usableHeight;
    const points = series.map((point, index) => `${x(index)},${y(point.value)}`).join(' ');
    const bars = series.map((point, index) => {
      const barWidth = Math.max(5, Math.min(28, usableWidth / series.length - 3));
      return `<rect class="chart-bar" x="${x(index) - barWidth / 2}" y="${y(point.value)}" width="${barWidth}" height="${pad.top + usableHeight - y(point.value)}" rx="3"><title>${point.date}: ${point.value}${suffix}</title></rect>`;
    }).join('');
    const grid = [0, .5, 1].map(step => `<line x1="${pad.left}" x2="${width - pad.right}" y1="${y(max * step)}" y2="${y(max * step)}" class="chart-grid"/><text x="${pad.left - 9}" y="${y(max * step) + 4}" text-anchor="end" class="chart-axis">${Math.round(max * step)}</text>`).join('');
    const tickIndexes = [...new Set([0, Math.floor((series.length - 1) / 2), series.length - 1])];
    const ticks = tickIndexes.map(index => `<text x="${x(index)}" y="${height - 13}" text-anchor="middle" class="chart-axis">${new Date(series[index].date + 'T00:00:00').toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}</text>`).join('');
    const drawing = label === 'Training Volume'
      ? `<polyline points="${points}" class="chart-line"/><g class="chart-points">${series.map((point, index) => `<circle cx="${x(index)}" cy="${y(point.value)}" r="4"><title>${point.date}: ${point.value}${suffix}</title></circle>`).join('')}</g>`
      : `<g class="chart-bars">${bars}</g>`;
    container.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${label} chart">${grid}${drawing}${ticks}</svg>`;
  }

  drawChart('frequency-chart', data.frequency, 'Workout Frequency', '#006948', ' workouts');
  drawChart('volume-chart', data.volume, 'Training Volume', '#16835a', ' kg');

  const heatmap = document.getElementById('activity-heatmap');
  if (heatmap) {
    const start = new Date(data.heatmapStart + 'T00:00:00');
    const days = 365;
    for (let index = 0; index < days; index += 1) {
      const date = new Date(start); date.setDate(start.getDate() + index);
      const key = date.toISOString().slice(0, 10);
      const count = data.activity[key] || 0;
      const cell = document.createElement('span');
      cell.className = `heatmap-cell level-${Math.min(count, 3)}`;
      cell.tabIndex = 0;
      cell.setAttribute('role', 'img');
      cell.setAttribute('aria-label', `${date.toLocaleDateString(undefined, {month: 'long', day: 'numeric', year: 'numeric'})}: ${count} workout${count === 1 ? '' : 's'}`);
      cell.title = cell.getAttribute('aria-label');
      heatmap.appendChild(cell);
    }
  }
}());
