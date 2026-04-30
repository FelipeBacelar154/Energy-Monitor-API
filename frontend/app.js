const API = 'http://localhost:8000';

// 🔐 PROTEÇÃO DE ROTA
const token = localStorage.getItem("token");

if (!token) {
  window.location.href = "login.html";
}

// HEADER PADRÃO COM AUTH
function authHeader() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

// INIT
window.onload = () => {
  loadDashboard();
  loadEquipments();
  setupDownloadButton();
};

// ================= DASHBOARD =================
async function loadDashboard() {
  try {
    const res = await fetch(`${API}/readings/dashboard`, {
      headers: authHeader()
    });

    if (!res.ok) throw new Error();

    const data = await res.json();

    document.getElementById('stat-equipments').textContent = data.total_equipments;
    document.getElementById('stat-consumption').textContent = data.total_consumption_kwh;
    document.getElementById('stat-cost').textContent = `R$ ${data.total_cost_brl}`;
    document.getElementById('stat-top').textContent = data.top_consumer || '--';

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

// ================= EQUIPMENTS =================
async function loadEquipments() {
  try {
    const res = await fetch(`${API}/equipments/`, {
      headers: authHeader()
    });

    if (!res.ok) throw new Error();

    const equipments = await res.json();
    const list = document.getElementById('equipments-list');

    if (equipments.length === 0) {
      list.innerHTML = '<div class="empty-state">No equipments registered yet.</div>';
      return;
    }

    list.innerHTML = `
      <table class="equipment-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Power</th>
            <th>Location</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${equipments.map(eq => `
            <tr>
              <td>${eq.name}</td>
              <td><span class="badge">${eq.power_kw} kW</span></td>
              <td>${eq.location}</td>
              <td>${eq.description || '--'}</td>
              <td>
                <button class="btn-delete" onclick="deleteEquipment(${eq.id})">Delete</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;

    const readingSelect = document.getElementById('reading-equipment');
    const chartSelect = document.getElementById('chart-equipment');

    readingSelect.innerHTML = '<option value="">Select equipment...</option>';
    chartSelect.innerHTML = '<option value="">Select equipment to view chart...</option>';

    equipments.forEach(eq => {
      readingSelect.innerHTML += `<option value="${eq.id}">${eq.name}</option>`;
      chartSelect.innerHTML += `<option value="${eq.id}">${eq.name}</option>`;
    });

  } catch (err) {
    console.error("Equipments error:", err);
  }
}

// ================= ADD EQUIPMENT =================
async function addEquipment() {
  const name = document.getElementById('eq-name').value.trim();
  const power = document.getElementById('eq-power').value;
  const location = document.getElementById('eq-location').value.trim();
  const description = document.getElementById('eq-description').value.trim();
  const msgEl = document.getElementById('eq-message');

  if (!name || !power || !location) {
    msgEl.textContent = 'Name, power and location are required!';
    msgEl.className = 'message error';
    return;
  }

  try {
    const res = await fetch(`${API}/equipments/`, {
      method: 'POST',
      headers: authHeader(),
      body: JSON.stringify({
        name,
        power_kw: parseFloat(power),
        location,
        description: description || null
      })
    });

    if (!res.ok) throw new Error();

    msgEl.textContent = 'Equipment added successfully!';
    msgEl.className = 'message success';

    document.getElementById('eq-name').value = '';
    document.getElementById('eq-power').value = '';
    document.getElementById('eq-location').value = '';
    document.getElementById('eq-description').value = '';

    loadEquipments();
    loadDashboard();

  } catch (err) {
    msgEl.textContent = 'Error adding equipment!';
    msgEl.className = 'message error';
  }
}

// ================= DELETE EQUIPMENT =================
async function deleteEquipment(id) {
  try {
    const res = await fetch(`${API}/equipments/${id}`, {
      method: 'DELETE',
      headers: authHeader()
    });

    if (!res.ok) throw new Error();

    loadEquipments();
    loadDashboard();

  } catch (err) {
    console.error("Delete error:", err);
  }
}

// ================= ADD READING =================
async function addReading() {
  const equipment_id = document.getElementById('reading-equipment').value;
  const consumption = document.getElementById('reading-consumption').value;
  const voltage = document.getElementById('reading-voltage').value;
  const current = document.getElementById('reading-current').value;
  const msgEl = document.getElementById('reading-message');

  if (!equipment_id || !consumption) {
    msgEl.textContent = 'Equipment and consumption are required!';
    msgEl.className = 'message error';
    return;
  }

  try {
    const res = await fetch(`${API}/readings/`, {
      method: 'POST',
      headers: authHeader(),
      body: JSON.stringify({
        equipment_id: parseInt(equipment_id),
        consumption_kwh: parseFloat(consumption),
        voltage: voltage ? parseFloat(voltage) : null,
        current: current ? parseFloat(current) : null
      })
    });

    if (!res.ok) throw new Error();

    msgEl.textContent = 'Reading added successfully!';
    msgEl.className = 'message success';

    document.getElementById('reading-consumption').value = '';
    document.getElementById('reading-voltage').value = '';
    document.getElementById('reading-current').value = '';

    loadDashboard();
    loadChart();

  } catch (err) {
    msgEl.textContent = 'Error adding reading!';
    msgEl.className = 'message error';
  }
}

// ================= CHART =================
async function loadChart() {
  const equipment_id = document.getElementById('chart-equipment').value;
  if (!equipment_id) return;

  try {
    const res = await fetch(`${API}/readings/${equipment_id}`, {
      headers: authHeader()
    });

    if (!res.ok) throw new Error();

    const readings = await res.json();

    if (readings.length === 0) {
      document.getElementById('chart').innerHTML =
        '<div class="empty-state">No readings for this equipment yet.</div>';
      return;
    }

    const timestamps = readings.map(r => r.timestamp).reverse();
    const consumption = readings.map(r => r.consumption_kwh).reverse();

    Plotly.newPlot('chart', [{
      x: timestamps,
      y: consumption,
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#6366f1', width: 2 },
      marker: { size: 6 },
      fill: 'tozeroy'
    }], {
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: { t: 10, b: 40, l: 50, r: 10 }
    }, { responsive: true });

  } catch (err) {
    console.error("Chart error:", err);
  }
}

// ================= DOWNLOAD PDF =================
function setupDownloadButton() {
  const btn = document.getElementById("downloadReport");

  if (!btn) return;

  btn.addEventListener("click", async () => {
    try {
      btn.textContent = "⏳ Generating...";
      btn.disabled = true;

      const chartDiv = document.getElementById("chart");

      let imageBase64 = null;

      if (chartDiv && chartDiv.data) {
        imageBase64 = await Plotly.toImage(chartDiv, {
          format: "png",
          width: 800,
          height: 400
        });
      }

      const response = await fetch(`${API}/reports/download`, {
        method: "POST",
        headers: authHeader(),
        body: JSON.stringify({
          chart_image: imageBase64
        })
      });

      if (!response.ok) throw new Error();

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "energy-report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {
      alert("Error generating PDF");
      console.error(err);
    } finally {
      btn.textContent = "📄 Download PDF Report";
      btn.disabled = false;
    }
  });
}