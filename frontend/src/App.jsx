import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import UploadForm from "./components/UploadForm";
import SearchBar from "./components/SearchBar";
import SortControls from "./components/SortControls";
import DocumentTable from "./components/DocumentTable";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";
import { Container, Button, Navbar, Nav } from "react-bootstrap";
import { useState, useEffect } from "react";

function MainApp() {
  const { user, logout } = useAuth();
  const [search, setSearch] = useState("");
  const [labels, setLabels] = useState([]);
  const [searchParams, setSearchParams] = useState([]);
  const [sortOptions, setSortOptions] = useState({
    sortBy: "",
    order: "desc",
    word: "",
    segment: "header",
  });
  const [refreshToggle, setRefreshToggle] = useState(false);

  const triggerRefresh = () => setRefreshToggle((r) => !r);

  function addToDataBase(json, name, image64) {
    const now = new Date();
    const date = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
    const body = {
      date,
      owner_id: user.id,
      name: name,
      status: "UPLOADED",
      json: json,
      image64: image64,
    };
    fetch("/api/documents", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    })
      .then((res) => {
        triggerRefresh();
        console.log(res);
      })
      .catch(console.error);
  }

  return (
    <>
      <Navbar bg="light" className="mb-3">
        <Container>
          <Navbar.Brand>Документы</Navbar.Brand>
          <Nav className="ms-auto">
            <Navbar.Text className="me-3">{user.username}</Navbar.Text>
            <Button variant="outline-danger" size="sm" onClick={logout}>
              Выйти
            </Button>
          </Nav>
        </Container>
      </Navbar>

      <Container>
        <UploadForm addToDataBase={addToDataBase} />
        <SearchBar
          onSearch={setSearch}
          onLabelsChange={setLabels}
          onParamsChange={setSearchParams}
        />
        <div className="mt-3 p-3 border rounded bg-light">
          <SortControls onSortChange={setSortOptions} />
          <DocumentTable
            search={search}
            labels={labels}
            searchParams={searchParams}
            sortOptions={sortOptions}
            refreshToggle={refreshToggle}
          />
        </div>
      </Container>
    </>
  );
}

function AppRoutes() {
  const { user, loading } = useAuth();
  if (loading) return <div>Загрузка...</div>;

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/auth/login"
          element={user ? <Navigate to="/" /> : <LoginForm />}
        />
        <Route
          path="/auth/register"
          element={user ? <Navigate to="/" /> : <RegisterForm />}
        />
        <Route
          path="/"
          element={user ? <MainApp /> : <Navigate to="/auth/login" />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
