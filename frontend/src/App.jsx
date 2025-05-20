import UploadForm from "./components/UploadForm";
import SearchBar from "./components/SearchBar";
import SortControls from "./components/SortControls";
import DocumentTable from "./components/DocumentTable";
import { Container } from "react-bootstrap";
import axios from "axios";
import { useState, useEffect } from "react";

function App() {
  const [search, setSearch] = useState("");
  const [labels, setLabels] = useState([]);
  const [refreshToggle, setRefreshToggle] = useState(false);
  const [sortOptions, setSortOptions] = useState({
    sortBy: "",
    order: "asc",
    word: "",
    segment: "header",
  });
  const [searchParams, setSearchParams] = useState([]);

  const triggerRefresh = () => setRefreshToggle((r) => !r);
  function addToDataBase(json, name) {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const day = now.getDate();
    const body = {
      date: `${year}-${month + 1}-${day}`,
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
        triggerRefresh();
        console.log(res);
      })
      .catch((err) => {
        console.error(err);
      });
  }
  return (
    <Container className="py-4">
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
          sortOptions={sortOptions}
          searchParams={searchParams}
          refreshToggle={refreshToggle}
        />
      </div>
    </Container>
  );
}

export default App;
