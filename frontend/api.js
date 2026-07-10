const API_BASE = "http://127.0.0.1:8000/api";

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(`${path} responded with ${response.status}`);
  return response.json();
}

async function apiPost(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`${path} responded with ${response.status}`);
  return response.json();
}

async function apiPut(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`${path} responded with ${response.status}`);
  return response.json();
}

async function apiDelete(path) {
  const response = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!response.ok) throw new Error(`${path} responded with ${response.status}`);
  return response.status === 204 ? null : response.json();
}
