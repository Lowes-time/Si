const AUTH_KEY = "si_auth_token";
const USERS_KEY = "si_registered_users";

const DEFAULT_ACCOUNT = { username: "user", password: "123456" };
export const USERNAME_MIN = 3;
export const USERNAME_MAX = 20;
export const PASSWORD_MIN = 6;
export const PASSWORD_MAX = 32;

export function isLoggedIn() {
  return sessionStorage.getItem(AUTH_KEY) === "1";
}

export function setLoggedIn() {
  sessionStorage.setItem(AUTH_KEY, "1");
}

export function clearLogin() {
  sessionStorage.removeItem(AUTH_KEY);
}

function readRegisteredUsers() {
  try {
    const raw = localStorage.getItem(USERS_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function writeRegisteredUsers(list) {
  localStorage.setItem(USERS_KEY, JSON.stringify(list));
}

function normalizeUsername(name) {
  return String(name || "").trim();
}

function usernameKey(name) {
  return normalizeUsername(name).toLowerCase();
}

export function isUsernameTaken(name) {
  const key = usernameKey(name);
  if (!key) return false;
  if (key === usernameKey(DEFAULT_ACCOUNT.username)) return true;
  return readRegisteredUsers().some((u) => usernameKey(u.username) === key);
}

export function registerUser(name, password) {
  const username = normalizeUsername(name);
  const users = readRegisteredUsers();
  users.push({ username, password });
  writeRegisteredUsers(users);
}

export function validateLogin(name, password) {
  const username = normalizeUsername(name);
  if (
    username === DEFAULT_ACCOUNT.username &&
    password === DEFAULT_ACCOUNT.password
  ) {
    return true;
  }
  const hit = readRegisteredUsers().find((u) => u.username === username);
  return Boolean(hit && hit.password === password);
}
