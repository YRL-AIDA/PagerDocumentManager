import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // при монтировании пробуем получить сессию
  useEffect(() => {
    fetch("/api/current_user", { credentials: "include" })
      .then((res) => (res.ok ? res.json() : Promise.resolve(null)))
      .then((u) => setUser(u))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const res = await fetch("/api/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      let errorMsg;
      try {
        const data = await res.json();
        errorMsg = data.message || JSON.stringify(data);
      } catch {
        errorMsg = await res.text();
      }
      throw new Error(errorMsg);
    }
    const u = await res.json();
    setUser(u);
    return u;
  };

  const register = async (username, password) => {
    const res = await fetch("/api/register", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      let errorMsg;
      try {
        const data = await res.json();
        errorMsg = data.message || JSON.stringify(data);
      } catch {
        errorMsg = await res.text();
      }
      throw new Error(errorMsg);
    }
    const u = await res.json();
    setUser(u);
    return u;
  };

  const logout = () =>
    fetch("/api/logout", {
      method: "POST",
      credentials: "include",
    }).then(() => setUser(null));

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
