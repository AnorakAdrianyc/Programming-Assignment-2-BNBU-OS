const cEditor = document.getElementById("cEditor");
const analyzeButton = document.getElementById("analyzeButton");
const localButton = document.getElementById("localButton");
const bridgeOutput = document.getElementById("bridgeOutput");
const tableBody = document.getElementById("processTable");
const canvas = document.getElementById("timeline");
const ctx = canvas.getContext("2d");

const BRIDGE_URL = window.BRIDGE_URL || "http://127.0.0.1:8000/bridge";

function parseProcesses(source) {
  const regex = /enqueue_process\("([^"]+)",\s*(\d+),\s*(\d+)\)/g;
  const processes = [];
  let match;
  while ((match = regex.exec(source)) !== null) {
    processes.push({ name: match[1], burst: Number(match[2]), arrival: Number(match[3]) });
  }
  return processes;
}

function computeFcfs(processes) {
  const sorted = [...processes].sort((a, b) => a.arrival - b.arrival);
  let clock = 0;
  return sorted.map((p) => {
    if (clock < p.arrival) clock = p.arrival;
    const start = clock;
    const end = start + p.burst;
    const wait = start - p.arrival;
    const turnaround = end - p.arrival;
    clock = end;
    return { ...p, start, end, wait, turnaround };
  });
}

function render(data) {
  tableBody.innerHTML = "";
  data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.name}</td><td>${row.arrival}</td><td>${row.burst}</td><td>${row.wait}</td><td>${row.turnaround}</td>`;
    tableBody.appendChild(tr);
  });

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const total = data.length ? data[data.length - 1].end : 1;
  const laneWidth = (canvas.width - 40) / total;

  data.forEach((row, idx) => {
    const x = 20 + row.start * laneWidth;
    const width = (row.end - row.start) * laneWidth;
    const y = 20 + idx * 24;
    ctx.fillStyle = "#34d399";
    ctx.fillRect(x, y, width, 18);
    ctx.fillStyle = "#052e16";
    ctx.fillText(`${row.name} [${row.start}-${row.end}]`, x + 4, y + 13);
  });
}

async function analyzeWithBridge() {
  const processes = parseProcesses(cEditor.value);
  if (!processes.length) {
    bridgeOutput.textContent = "No process entries found.";
    render([]);
    return;
  }

  try {
    const response = await fetch(BRIDGE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ processes })
    });

    if (!response.ok) throw new Error(`Bridge error: ${response.status} ${response.statusText}`);
    const data = await response.json();
    bridgeOutput.textContent = JSON.stringify(data, null, 2);
    render(data.timeline || []);
  } catch (error) {
    console.error("Bridge request failed:", error);
    const fallback = { timeline: computeFcfs(processes), source: "local-js" };
    bridgeOutput.textContent = JSON.stringify(fallback, null, 2);
    render(fallback.timeline);
  }
}

function analyzeLocal() {
  const processes = parseProcesses(cEditor.value);
  const data = computeFcfs(processes);
  bridgeOutput.textContent = JSON.stringify({ timeline: data, source: "local-js" }, null, 2);
  render(data);
}

analyzeButton.addEventListener("click", analyzeWithBridge);
localButton.addEventListener("click", analyzeLocal);
analyzeLocal();
