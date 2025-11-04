// ===========================
//  Simulación Máquina Turing
// ===========================

const WRITE_DELAY = 90;    // ms por carácter al escribir en la cinta
const STEP_DELAY  = 1500;  // ms entre pasos

// Mapa de <option value="..."> a patrón que el backend espera
const REGEX_MAP = {
  r1: "(a|b)*abb",
  r2: "0*1*",
  r3: "(ab)*",
  r4: "1(01)*0",
  // Tu HTML muestra (a+b)*a(a+b)*, pero el parser usa '|' para alternancia
  r5: "(a|b)*a(a|b)*"
};

async function startSimulation() {
  const input = document.getElementById("inputString").value.trim();
  const choice = document.getElementById("regexChoice").value;
  const regexPattern = REGEX_MAP[choice] || choice; // por si algún día pones el patrón directo

  const tape = document.getElementById("tape");
  const wrapper = document.getElementById("tapeWrapper");
  const headAction = document.getElementById("headAction");
  const resultLabel = document.getElementById("result");
  const statesTable = document.getElementById("statesTable");
  const transitionsTable = document.getElementById("transitionsTable");

  if (!input) {
    resultLabel.textContent = "Por favor ingresa una cadena.";
    resultLabel.className = "result-label result-reject";
    return;
  }

  // Reset UI
  resultLabel.textContent = "";
  resultLabel.className = "result-label";
  statesTable.innerHTML = "<tr><th class='px-2 py-1 border'>Estado</th></tr>";
  transitionsTable.innerHTML = `
    <tr>
      <th class="px-2 py-1 border">De</th>
      <th class="px-2 py-1 border">Leer</th>
      <th class="px-2 py-1 border">→ A</th>
      <th class="px-2 py-1 border">Escribir</th>
      <th class="px-2 py-1 border">Mov</th>
    </tr>`;

  // Construir cinta vacía
  const blanks = 25;
  const totalLen = blanks * 2 + input.length;
  tape.innerHTML = "";
  for (let i = 0; i < totalLen; i++) {
    const cell = document.createElement("div");
    cell.classList.add("cell");
    cell.textContent = "_";
    tape.appendChild(cell);
  }
  const cells = Array.from(tape.children);

  // Animación de escritura
  headAction.textContent = "Escribiendo cinta…";
  for (let i = blanks; i < blanks + input.length; i++) {
    cells[i].classList.add("active");
    cells[i].textContent = input[i - blanks];
    await wait(WRITE_DELAY);
    cells[i].classList.remove("active");
  }

  // Posición inicial
  let index = blanks;
  highlightCell(cells, index);
  centerOnCell(wrapper, tape, cells[index]);

  // Llamada al backend Flask (ahora sí, con el patrón correcto)
  headAction.textContent = "Preparando simulación…";
  const res = await fetch("/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input, regex: regexPattern })
  });

  let data;
  try {
    data = await res.json();
  } catch {
    resultLabel.textContent = "Respuesta inválida del servidor.";
    resultLabel.className = "result-label result-reject";
    headAction.textContent = "Error";
    return;
  }

  if (data.error) {
    resultLabel.textContent = data.error;
    resultLabel.className = "result-label result-reject";
    headAction.textContent = "Error";
    return;
  }

  const steps = data.steps || [];
  let currentState = "q0";

  // Paso a paso
  for (let i = 0; i < steps.length; i++) {
    const s = steps[i]; // {from, read, to, write, move}
    headAction.textContent = `q=${currentState} | Leer '${s.read}' → Escribir '${s.write}'`;

    if (cells[index]) cells[index].textContent = s.write;

    statesTable.innerHTML += `<tr><td class="border px-2 py-1">${currentState}</td></tr>`;
    transitionsTable.innerHTML += `
      <tr>
        <td class="border px-2 py-1">${s.from}</td>
        <td class="border px-2 py-1">${s.read}</td>
        <td class="border px-2 py-1">${s.to}</td>
        <td class="border px-2 py-1">${s.write}</td>
        <td class="border px-2 py-1">${s.move}</td>
      </tr>`;

    if (s.move === "R") {
      index += 1;
      headAction.textContent = `q=${currentState} → q=${s.to} | Mover Derecha`;
    } else if (s.move === "L") {
      index -= 1;
      headAction.textContent = `q=${currentState} → q=${s.to} | Mover Izquierda`;
    } else {
      headAction.textContent = `q=${currentState} → q=${s.to} | Detener`;
    }

    highlightCell(cells, index);
    centerOnCell(wrapper, tape, cells[index]);
    currentState = s.to;
    await wait(STEP_DELAY);
  }

  // Resultado
  const final = data.result || "reject";
  highlightCell(cells, index);
  headAction.textContent = final === "accept" ? "Cadena aceptada ✅" : "Cadena rechazada ❌";
  resultLabel.textContent = final === "accept" ? "Cadena Aceptada" : "Cadena Rechazada";
  resultLabel.className = "result-label " + (final === "accept" ? "result-accept" : "result-reject");
}

// ======================
// Utilidades
// ======================
function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function highlightCell(cells, index) {
  cells.forEach(c => c.classList.remove("active"));
  if (cells[index]) cells[index].classList.add("active");
}

// Centra la celda objetivo bajo el cabezal usando posiciones reales
function centerOnCell(wrapper, tape, cell) {
  if (!cell) return;

  const wrapperRect = wrapper.getBoundingClientRect();
  const cellRect = cell.getBoundingClientRect();

  const wrapperCenter = wrapperRect.left + wrapperRect.width / 2;
  const cellCenter = cellRect.left + cellRect.width / 2;

  const delta = wrapperCenter - cellCenter;

  // Obtener translateX actual para no acumular errores por transición CSS
  const style = getComputedStyle(tape).transform;
  let currentX = 0;
  if (style && style !== "none") {
    const parts = style.match(/matrix\(([^)]+)\)/);
    if (parts && parts[1]) {
      const vals = parts[1].split(",").map(v => parseFloat(v.trim()));
      currentX = vals[4] || 0;
    }
  }

  const nextX = currentX + delta;
  tape.style.transform = `translateX(${nextX}px)`;
}
