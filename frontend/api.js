
function highlightActiveNav() {

  const rawSegments = window.location.pathname.split(/[\\/]/).filter(Boolean);
  let path = (rawSegments.pop() || 'index.html').split(/[?#]/)[0].toLowerCase();
  if (!path) path = 'index.html';

  path = path.replace(/\.html$/, '');

  const homeAliases = ['', 'index', 'vuva'];
  let matched = false;

  document.querySelectorAll('nav.links a').forEach((link) => {
    const hrefRaw = (link.getAttribute('href') || '').toLowerCase();
    if (!hrefRaw) return;
    const href = hrefRaw.replace(/\.html$/, '');
    const isActive = href === path || (href === 'index' && homeAliases.includes(path));
    link.classList.toggle('active', isActive);
    if (isActive) matched = true;
  });

  if (!matched) {

    console.warn('[VUVA] highlightActiveNav: no nav link matched current path', {
      pathname: window.location.pathname,
      resolvedPath: path,
    });
  }
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', highlightActiveNav);
} else {
  highlightActiveNav();
}

// Shared HTML-escaping helper. Player/team/announcement text ultimately
// comes from the admin panel, but it's still attacker-controllable if an
// editor account is ever compromised (or someone fat-fingers a "<" into a
// name) - escaping before it goes into innerHTML costs nothing and closes
// off stored-XSS via that content rendering on public pages.
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// Only allow http(s)/relative URLs into src="…"/href="…"/url(…) contexts.
// Blocks a "javascript:" or "data:" URL entered into a logo/photo/website
// field from executing when someone clicks/loads it.
function safeUrl(url) {
  if (!url) return "";
  const trimmed = String(url).trim();
  if (/^(https?:)?\/\//i.test(trimmed) || /^[.\/]/.test(trimmed)) {
    return escapeHtml(trimmed);
  }
  return "";
}

// Falls back to the same hardcoded local dev URL as before if no override
// is provided, so existing local setups keep working unchanged. For a real
// deployment, set `window.VUVA_API_BASE = "https://your-api.example.com/api"`
// in a small inline script (or a separate config.js) loaded before this file.
const API_BASE = "https://northstar-oyhx.onrender.com/api";

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