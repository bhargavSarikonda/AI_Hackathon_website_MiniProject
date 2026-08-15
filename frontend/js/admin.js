const TOKEN_KEY = "hackathon_admin_token";
const USERNAME_KEY = "hackathon_admin_username";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

function showAlert(elementId, message, type = "error") {
  const alertBox = document.getElementById(elementId);
  if (!alertBox) return;
  alertBox.textContent = message;
  alertBox.className = `alert alert-${type} show`;
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleLogin(event) {
  event.preventDefault();

  const loginBtn = document.getElementById("login-btn");
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  loginBtn.disabled = true;
  loginBtn.textContent = "Logging in...";

  try {
    const response = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const result = await response.json();

    if (!response.ok) {
      showAlert(
        "login-alert",
        typeof result.detail === "string" ? result.detail : "Login failed.",
        "error"
      );
      return;
    }

    setSession(result.token, result.username);
    window.location.href = "dashboard.html";
  } catch {
    showAlert("login-alert", "Unable to connect to the server.", "error");
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Login";
  }
}

let allRegistrations = [];

function renderTable(registrations) {
  const tbody = document.getElementById("registrations-body");
  if (!tbody) return;

  if (registrations.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="8" class="empty-state">No registrations found.</td></tr>';
    return;
  }

  tbody.innerHTML = registrations
    .map(
      (item) => `
        <tr>
          <td>${item.id}</td>
          <td>${escapeHtml(item.full_name)}</td>
          <td>${escapeHtml(item.email)}</td>
          <td>${escapeHtml(item.phone)}</td>
          <td>${escapeHtml(item.college)}</td>
          <td>${escapeHtml(item.branch || "-")}</td>
          <td>${escapeHtml(item.year || "-")}</td>
          <td>${escapeHtml(formatDate(item.created_at))}</td>
        </tr>
      `
    )
    .join("");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function filterRegistrations(query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    renderTable(allRegistrations);
    return;
  }

  const filtered = allRegistrations.filter((item) => {
    return (
      item.full_name.toLowerCase().includes(normalized) ||
      item.email.toLowerCase().includes(normalized) ||
      item.college.toLowerCase().includes(normalized)
    );
  });

  renderTable(filtered);
}

async function loadRegistrations() {
  const token = getToken();
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    const response = await fetch("/api/registrations", {
      headers: authHeaders(),
    });

    if (response.status === 401) {
      clearSession();
      window.location.href = "login.html";
      return;
    }

    if (!response.ok) {
      showAlert("dashboard-alert", "Failed to load registrations.", "error");
      return;
    }

    allRegistrations = await response.json();
    renderTable(allRegistrations);
  } catch {
    showAlert("dashboard-alert", "Unable to connect to the server.", "error");
  }
}

async function exportRegistrations() {
  const token = getToken();
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    const response = await fetch("/api/registrations/export", {
      headers: authHeaders(),
    });

    if (response.status === 401) {
      clearSession();
      window.location.href = "login.html";
      return;
    }

    if (!response.ok) {
      showAlert("dashboard-alert", "Failed to export registrations.", "error");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "registrations.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch {
    showAlert("dashboard-alert", "Unable to export registrations.", "error");
  }
}

async function handleLogout() {
  const token = getToken();
  if (token) {
    try {
      await fetch("/api/admin/logout", {
        method: "POST",
        headers: {
          ...authHeaders(),
          "Content-Type": "application/json",
        },
      });
    } catch {
      // Ignore network errors during logout.
    }
  }

  clearSession();
  window.location.href = "login.html";
}

function initLoginPage() {
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    if (getToken()) {
      window.location.href = "dashboard.html";
      return;
    }
    loginForm.addEventListener("submit", handleLogin);
  }
}

function initDashboardPage() {
  const logoutBtn = document.getElementById("logout-btn");
  const refreshBtn = document.getElementById("refresh-btn");
  const exportBtn = document.getElementById("export-btn");
  const searchInput = document.getElementById("search-input");

  if (!logoutBtn) return;

  if (!getToken()) {
    window.location.href = "login.html";
    return;
  }

  loadRegistrations();

  logoutBtn.addEventListener("click", handleLogout);
  refreshBtn.addEventListener("click", loadRegistrations);
  exportBtn.addEventListener("click", exportRegistrations);
  searchInput.addEventListener("input", (event) => {
    filterRegistrations(event.target.value);
  });
}

initLoginPage();
initDashboardPage();
