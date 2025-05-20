import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!username.trim()) {
      setError("Введите логин");
      return;
    }
    if (!password) {
      setError("Введите пароль");
      return;
    }

    try {
      await login(username, password);
      nav("/", { replace: true });
    } catch (err) {
      setError(err.message || "Ошибка входа");
    }
  };

  return (
    <form onSubmit={submit} style={{ maxWidth: 320, margin: "2rem auto" }}>
      <h2>Вход</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <input
        className="form-control mb-2"
        placeholder="Логин"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        className="form-control mb-2"
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="btn btn-primary w-100">Войти</button>
      <div className="mt-2 text-center">
        Нет аккаунта? <a href="/auth/register">Зарегистрироваться</a>
      </div>
    </form>
  );
}
