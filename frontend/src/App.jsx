import UploadForm from "./components/UploadForm";
import SearchBar from "./components/SearchBar";
import SortControls from "./components/SortControls";
import DocumentTable from "./components/DocumentTable";
import { Container } from "react-bootstrap";

function App() {
  return (
    <Container className="py-4">
      <UploadForm />
      <SearchBar />
      <SortControls />
      <DocumentTable />
    </Container>
  );
}

export default App;
