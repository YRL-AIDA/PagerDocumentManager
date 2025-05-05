import { useState } from "react";
import {
  Form,
  Button,
  InputGroup,
  DropdownButton,
  Dropdown,
} from "react-bootstrap";

export default function SortControls() {
  const [selectedSortParam, setSelectedSortParam] = useState("sortByNumOfChar");
  const [selectedSegment, setSelectedSegment] = useState("header");
  const [word, setWord] = useState("");
  const [sortOrder, setSortOrder] = useState("asc"); // "asc" or "desc"

  function handleSubmit(e) {
    // Prevent the browser from reloading the page
    e.preventDefault();
    // Read the form data
    const form = e.target;
    const formData = new FormData(form);
    // // You can pass formData as a fetch body directly:
    // fetch("/some-api", { method: form.method, body: formData });
    const formJson = Object.fromEntries(formData.entries());
    console.log(formJson);
    if (selectedSortParam === "sortByNumOfWord") {
      console.log(word);
    }
  }
  return (
    <Form inline="true" onSubmit={handleSubmit} className="mb-3">
      <InputGroup>
        <DropdownButton
          variant="outline-secondary"
          title={
            {
              sortByNumOfChar: "По символам",
              sortByNumOfWord: "По слову",
              sortBySegment: "По сегменту",
            }[selectedSortParam]
          }
          onSelect={(v) => setSelectedSortParam(v)}
        >
          <Dropdown.Item eventKey="sortByNumOfChar">По символам</Dropdown.Item>
          <Dropdown.Item eventKey="sortByNumOfWord">По слову</Dropdown.Item>
          <Dropdown.Item eventKey="sortBySegment">По сегменту</Dropdown.Item>
        </DropdownButton>

        {selectedSortParam === "sortByNumOfWord" && (
          <Form.Control
            placeholder="Слово"
            value={word}
            onChange={(e) => setWord(e.target.value)}
          />
        )}
        {selectedSortParam === "sortBySegment" && (
          <DropdownButton
            variant="outline-secondary"
            title={
              {
                header: "Заголовок",
                text: "Текст",
                list: "Список",
                table: "Таблица",
                img: "Изображение",
              }[selectedSegment]
            }
            onSelect={(v) => setSelectedSegment(v)}
          >
            <Dropdown.Item eventKey="header">Заголовок</Dropdown.Item>
            <Dropdown.Item eventKey="text">Текст</Dropdown.Item>
            <Dropdown.Item eventKey="list">Список</Dropdown.Item>
            <Dropdown.Item eventKey="table">Таблица</Dropdown.Item>
            <Dropdown.Item eventKey="img">Изображение</Dropdown.Item>
          </DropdownButton>
        )}

        <Button
          variant="outline-secondary"
          onClick={() => setSortOrder((o) => (o === "asc" ? "desc" : "asc"))}
        >
          {sortOrder === "asc" ? "↑" : "↓"}
        </Button>

        <Button type="submit" variant="primary">
          Сортировать
        </Button>
      </InputGroup>
    </Form>
  );
}
