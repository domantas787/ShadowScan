
//Tab switching
function switchTab(tabName) {
  // clear active state from all tabs
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector('.tab[data-tab="' + tabName + '"]').classList.add('active');

  // swap the visible content
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + tabName).classList.add('active');
}


// Chart setup

let intensityChart = null;

function initChart() {
  const ctx = document.getElementById('intensityChart').getContext('2d');
  if (intensityChart) intensityChart.destroy();

  intensityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Packets per second',
        data: [],
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.15)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400 },
      scales: {
        x: {
          ticks: { color: '#8b8fa3', font: { size: 11 } },
          grid: { color: 'rgba(46, 49, 68, 0.5)' },
          title: { display: true, text: 'Time (seconds)', color: '#8b8fa3' },
        },
        y: {
          beginAtZero: true,
          ticks: { color: '#8b8fa3', font: { size: 11 } },
          grid: { color: 'rgba(46, 49, 68, 0.5)' },
          title: { display: true, text: 'Packet rate', color: '#8b8fa3' },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
}


// Packet animation

function spawnPacket(color) {
  const layer = document.getElementById('packetLayer');
  const pkt = document.createElement('div');
  pkt.className = 'packet';
  pkt.style.color = color;
  pkt.style.background = color;

  // jitter the vertical position so packets don't all overlap
  pkt.style.marginTop = (Math.random() * 30 - 15) + 'px';

  layer.appendChild(pkt);

  // clean up the element after the animation finishes
  setTimeout(() => pkt.remove(), 2100);
}

function activateShield() {
  document.getElementById('idsShield').classList.add('shield-active');
}


// Narration feed

function addNarration(text) {
  const feed = document.getElementById('narrationFeed');
  const line = document.createElement('div');
  line.className = 'narration-line';
  line.textContent = text;
  feed.appendChild(line);
  feed.scrollTop = feed.scrollHeight;
}


// Alert rendering

function sevColor(sev) {
  if (sev >= 5) return 'var(--red)';
  if (sev >= 4) return 'var(--orange)';
  if (sev >= 3) return 'var(--yellow)';
  return 'var(--green)';
}

const methodExplanations = {
  signature: '🔍 <strong>Signature detection:</strong> Matched a known attack pattern in the payload.',
  heuristic: '📊 <strong>Heuristic detection:</strong> Statistical threshold exceeded (e.g. too many packets or ports).',
  ml: '🤖 <strong>ML detection:</strong> Pattern deviates from the learned baseline of normal traffic.',
};

function appendAlert(alert) {
  const card = document.createElement('div');
  card.className = 'card mb-12 alert-animated';
  card.style.borderLeft = '3px solid ' + sevColor(alert.severity);

  // Using textContent for the title so XSS payloads don't execute
  const heading = document.createElement('div');
  heading.style.cssText = 'display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;';

  const title = document.createElement('strong');
  title.textContent = alert.alert_type;

  const badges = document.createElement('div');
  badges.style.cssText = 'display:flex; gap:6px;';
  badges.innerHTML =
    '<span class="sev sev-' + alert.severity + '">Severity ' + alert.severity + '</span>' +
    '<span class="method method-' + alert.detection_method + '">' + alert.detection_method + '</span>';

  heading.appendChild(title);
  heading.appendChild(badges);

  // Description (use textContent)
  const desc = document.createElement('p');
  desc.className = 'text-muted text-sm';
  desc.textContent = alert.description;

  // The "how was this detected" explainer
  const explainer = document.createElement('div');
  explainer.style.cssText = 'margin-top:10px; padding:10px; background:var(--bg); border-radius:var(--radius); font-size:12px;';
  explainer.innerHTML = methodExplanations[alert.detection_method] || '';

  card.appendChild(heading);
  card.appendChild(desc);
  card.appendChild(explainer);

  document.getElementById('alertResults').appendChild(card);
}


//Run Simulation

async function runSimulation() {
  const btn = document.getElementById('simulateBtn');
  const status = document.getElementById('simStatus');
  const previousAlerts = document.getElementById('previousAlerts');

  btn.disabled = true;
  btn.textContent = '⏳ Running...';
  status.textContent = '';

  // hide any old results and reset everything
  if (previousAlerts) previousAlerts.style.display = 'none';
  document.getElementById('alertResults').innerHTML = '';
  document.getElementById('narrationFeed').innerHTML = '';
  document.getElementById('packetLayer').innerHTML = '';
  document.getElementById('idsShield').classList.remove('shield-active');
  document.getElementById('alertCount').textContent = '0';

  // fetch the simulation data from the backend
  let data;
  try {
    const res = await fetch('/exercise/' + EXERCISE_ID + '/simulate', { method: 'POST' });
    data = await res.json();
    if (data.status !== 'ok') {
      throw new Error(data.error || 'Failed');
    }
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
    btn.disabled = false;
    btn.textContent = '▶ Start Simulation';
    return;
  }

  const visual = data.visual;
  const alerts = data.alerts;

  // reveal the visualisation cards
  document.getElementById('diagramCard').style.display = 'block';
  document.getElementById('chartCard').style.display = 'block';
  document.getElementById('narrationCard').style.display = 'block';

  // set the attacker/target labels
  document.getElementById('attackerLabel').textContent = visual.attacker.label;
  document.getElementById('attackerIp').textContent = visual.attacker.ip;
  document.getElementById('targetLabel').textContent = visual.target.label;
  document.getElementById('targetIp').textContent = visual.target.ip;

  initChart();

  // narration plays
  const narrationDelay = 600;
  visual.narration.forEach((msg, i) => {
    setTimeout(() => addNarration(msg), i * narrationDelay);
  });

  // schedule the packet bursts
  visual.packet_bursts.forEach(burst => {
    setTimeout(() => {
      // spawn each packet in the burst slightly staggered
      for (let i = 0; i < burst.count; i++) {
        setTimeout(() => spawnPacket(burst.color), i * 80);
      }
      // push a data point onto the chart
      intensityChart.data.labels.push(burst.time.toFixed(1) + 's');
      intensityChart.data.datasets[0].data.push(burst.count);
      intensityChart.update();
    }, burst.time * 1000);
  });

  // activate IDS shield at the detection moment
  setTimeout(() => activateShield(), visual.detection_time * 1000);

  // show alerts after the visualisation finishes
  const lastBurstTime = Math.max(...visual.packet_bursts.map(b => b.time));
  const alertsStartTime = (lastBurstTime + 2) * 1000;

  setTimeout(() => {
    document.getElementById('alertSection').style.display = 'block';
    let count = 0;
    alerts.forEach((alert, i) => {
      setTimeout(() => {
        count++;
        document.getElementById('alertCount').textContent = count;
        appendAlert(alert);
      }, i * 500);
    });

    // enable the button once everything's done
    setTimeout(() => {
      status.innerHTML = '<span style="color:var(--green);">✓ Simulation complete</span>';
      btn.disabled = false;
      btn.textContent = '▶ Run Again';
    }, alerts.length * 500 + 500);
  }, alertsStartTime);
}


//Quiz

async function submitQuiz() {
  const answers = [];
  for (let i = 0; i < QUIZ_DATA.length; i++) {
    const selected = document.querySelector('input[name="q' + i + '"]:checked');
    answers.push(selected ? parseInt(selected.value) : -1);
  }

  if (answers.includes(-1)) {
    alert('Please answer all questions before submitting.');
    return;
  }

  try {
    const res = await fetch('/exercise/' + EXERCISE_ID + '/quiz', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: answers }),
    });
    const data = await res.json();

    const resultsDiv = document.getElementById('quizResults');
    document.getElementById('quizForm').style.display = 'none';
    resultsDiv.style.display = 'block';

    let html = '<h3 style="margin-bottom:16px;">Results: ' + data.correct + ' / ' + data.total + '</h3>';

    data.results.forEach((r, i) => {
      const color = r.is_correct ? 'var(--green)' : 'var(--red)';
      const icon = r.is_correct ? '✓' : '✗';
      html += '<div style="padding:12px; border-left:3px solid ' + color +
              '; margin-bottom:8px; border-radius:0 var(--radius) var(--radius) 0; background:var(--surface2);">';
      html += '<span style="color:' + color + '; font-weight:600;">' + icon + '</span> ';
      html += '<span style="font-size:14px;">' + r.question + '</span>';
      if (!r.is_correct) {
        html += '<p class="text-muted text-sm" style="margin-top:4px;">Correct answer: ' +
                QUIZ_DATA[i].options[r.correct_answer] + '</p>';
      }
      html += '</div>';
    });

    if (data.correct === data.total) {
      html += '<p style="color:var(--green); margin-top:16px; font-weight:600;">Perfect score! Exercise complete. ✓</p>';
    } else {
      html += '<button class="btn mt-16" onclick="location.reload()">Try Again</button>';
    }

    resultsDiv.innerHTML = html;
  } catch (e) {
    alert('Error: ' + e.message);
  }
}
