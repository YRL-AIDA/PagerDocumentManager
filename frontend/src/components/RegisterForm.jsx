import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function RegisterForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(null);
  const { register } = useAuth();
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
    if (!confirm) {
      setError("Подтвердите пароль");
      return;
    }
    if (password !== confirm) {
      setError("Пароли не совпадают");
      return;
    }

    try {
      await register(username, password);
      nav("/", { replace: true });
    } catch (err) {
      setError(err.message || "Ошибка регистрации");
    }
  };

  return (
    <form onSubmit={submit} style={{ maxWidth: 320, margin: "2rem auto" }}>
      <h2>Регистрация</h2>
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
      <input
        className="form-control mb-2"
        type="password"
        placeholder="Повторите пароль"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
      />
      <button className="btn btn-success w-100">Зарегистрироваться</button>
      <div className="mt-2 text-center">
        Уже есть аккаунт? <a href="/auth/login">Войти</a>
      </div>
    </form>
  );
}
