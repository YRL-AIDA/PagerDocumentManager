import UploadForm from "./components/UploadForm";
import SearchBar from "./components/SearchBar";
import SortControls from "./components/SortControls";
import DocumentTable from "./components/DocumentTable";
import { Container } from "react-bootstrap";
import axios from "axios";

function App() {
  function addToDataBase(json, name) {
    const body = {
      date: "2025-05-01",
      owner_id: 1,
      name: name,
      status: "UPLOADED",
      json: json,
    };
    console.log(json);
    fetch("http://localhost:5001/api/documents", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        console.error(err);
      });
  }
  return (
    <Container className="py-4">
      <UploadForm addToDataBase={addToDataBase} />
      <SearchBar />
      <div className="mt-3 p-3 border rounded bg-light">
        <SortControls />
        <DocumentTable />
      </div>
    </Container>
  );
}

export default App;
