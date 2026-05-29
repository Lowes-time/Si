const AUTH_KEY = "si_auth_token";

export function isLoggedIn() {
  return sessionStorage.getItem(AUTH_KEY) === "1";
}

export function setLoggedIn() {
  sessionStorage.setItem(AUTH_KEY, "1");
}

export function clearLogin() {
  sessionStorage.removeItem(AUTH_KEY);
}

export function validateLogin(username, password) {
  return username === "user" && password === "123456";
}
