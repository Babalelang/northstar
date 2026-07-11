const API_BASE = "http://127.0.0.1:8000/api";

// Auth token lives in localStorage so a page refresh doesn't log the
// admin out. This is a real deployed static site (not a Claude artifact
// sandbox), so localStorage is the right tool here.
function getToken() {
  return localStorage.getItem("vuva_token");
}

function setSession(token, user) {
  localStorage.setItem("vuva_token", token);
  localStorage.setItem("vuva_user", JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem("vuva_token");
  localStorage.removeItem("vuva_user");
}

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("vuva_user") || "null");
  } catch (err) {
    return null;
  }
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Thrown when a request comes back 401 - callers on admin.html catch this
// specifically to bounce back to the login screen instead of showing a
// generic "backend offline" error.
class AuthError extends Error {}

async function handleResponse(response, path) {
  if (response.status === 401) {
    clearSession();
    throw new AuthError(`${path} responded with 401`);
  }
  if (!response.ok) {
    let detail = `${path} responded with ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch (err) {
      /* response wasn't JSON - stick with the generic message */
    }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`, { headers: { ...authHeaders() } });
  return handleResponse(response, path);
}

async function apiPost(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, path);
}

async function apiPut(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, path);
}

async function apiDelete(path) {
  const response = await fetch(`${API_BASE}${path}`, { method: "DELETE", headers: { ...authHeaders() } });
  return handleResponse(response, path);
}
