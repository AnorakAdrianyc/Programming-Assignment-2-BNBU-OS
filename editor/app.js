const cEditor = document.getElementById("cEditor");
const analyzeButton = document.getElementById("analyzeButton");
const localButton = document.getElementById("localButton");
const validateCButton = document.getElementById("validateCButton");
const analyzeBridgeButton = document.getElementById("analyzeBridgeButton");
const suggestButton = document.getElementById("suggestButton");
const ollamaModelSelect = document.getElementById("ollamaModelSelect");
const ollamaGenerateButton = document.getElementById("ollamaGenerateButton");
const ollamaPrompt = document.getElementById("ollamaPrompt");
const ollamaOutput = document.getElementById("ollamaOutput");
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

async function fetchOllamaModels() {
  try {
    const response = await fetch(`${BRIDGE_URL}/cursor/ollama/models`);
    if (!response.ok) throw new Error(`Failed to fetch Ollama models: ${response.statusText}`);
    const models = await response.json();
    ollamaModelSelect.innerHTML = models.map(model => `<option value="${model.name}">${model.name}</option>`).join("");
    if (models.length > 0) {
      ollamaModelSelect.value = models[0].name;
    } else {
      ollamaModelSelect.innerHTML = "<option value=\"\">No models found</option>";
    }
  } catch (error) {
    console.error("Error fetching Ollama models:", error);
    ollamaOutput.textContent = `Error loading Ollama models: ${error.message}`;
  }
}

async function callOllamaGenerate() {
  const model = ollamaModelSelect.value;
  const prompt = ollamaPrompt.value;
  if (!model) {
    ollamaOutput.textContent = "Please select an Ollama model.";
    return;
  }
  if (!prompt.trim()) {
    ollamaOutput.textContent = "Please enter a prompt.";
    return;
  }

  ollamaOutput.textContent = "Generating...";
  try {
    const response = await fetch(`${BRIDGE_URL}/cursor/ollama/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt }),
    });
    if (!response.ok) throw new Error(`Ollama generation error: ${response.statusText}`);
    const data = await response.json();
    ollamaOutput.textContent = data.response || JSON.stringify(data, null, 2);
  } catch (error) {
    console.error("Ollama generation failed:", error);
    ollamaOutput.textContent = `Error: ${error.message}`;
  }
}

async function validateCContent() {
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

async function validateCContent() {
  const code = cEditor.value;
  try {
    const response = await fetch(`${BRIDGE_URL}/cursor/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    if (!response.ok)
      throw new Error(`Validation error: ${response.status} ${response.statusText}`);
    const data = await response.json();
    bridgeOutput.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    console.error("C validation failed:", error);
    bridgeOutput.textContent = `Error: ${error.message}`;
  }
}

async function analyzeSchedulingCodeWithBridge() {
  const code = cEditor.value;
  const processes = parseProcesses(code);
  if (!processes.length) {
    bridgeOutput.textContent = "No process entries found for analysis.";
    render([]);
    return;
  }

  try {
    const response = await fetch(`${BRIDGE_URL}/cursor/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) throw new Error(`Bridge analysis error: ${response.status} ${response.statusText}`);
    const data = await response.json();
    bridgeOutput.textContent = JSON.stringify(data, null, 2);
    render(data.timeline || []);
  } catch (error) {
    console.error("Bridge analysis request failed:", error);
    const fallback = { timeline: computeFcfs(processes), source: "local-js" };
    bridgeOutput.textContent = JSON.stringify(fallback, null, 2);
    render(fallback.timeline);
  }
}

async function suggestProcessesWithBridge() {
  const processes = parseProcesses(cEditor.value);
  if (!processes.length) {
    bridgeOutput.textContent = "No processes found to suggest from.";
    return;
  }

  try {
    const response = await fetch(`${BRIDGE_URL}/cursor/suggest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ processes }),
    });
    if (!response.ok)
      throw new Error(`Suggestion error: ${response.status} ${response.statusText}`);
    const data = await response.json();
    bridgeOutput.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    console.error("Process suggestion failed:", error);
    bridgeOutput.textContent = `Error: ${error.message}`;
  }
}

ollamaGenerateButton.addEventListener("click", callOllamaGenerate);
fetchOllamaModels(); // Call on page load
