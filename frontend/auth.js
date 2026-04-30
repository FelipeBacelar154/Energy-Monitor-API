const API = "http://localhost:8000";

// LOGIN
async function login() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  const msg = document.getElementById("login-msg");

  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    window.location.href = "index.html";
  } else {
    msg.textContent = data.detail || "Login failed";
    msg.className = "message error";
  }
}

// REGISTER
async function register() {
  const name = document.getElementById("reg-name").value;
  const email = document.getElementById("reg-email").value;
  const password = document.getElementById("reg-password").value;
  const msg = document.getElementById("reg-msg");

  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();

  if (res.ok) {
    msg.textContent = "Account created! Redirecting...";
    msg.className = "message success";
    setTimeout(() => window.location.href = "login.html", 1500);
  } else {
    msg.textContent = data.detail || "Error";
    msg.className = "message error";
  }
}