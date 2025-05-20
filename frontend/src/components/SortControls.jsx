import { useState } from "react";
import {
  Form,
  Button,
  InputGroup,
  DropdownButton,
  Dropdown,
} from "react-bootstrap";

export default function SortControls(props) {
  const [selectedSortParam, setSelectedSortParam] = useState("sortByName");
  const [selectedSegment, setSelectedSegment] = useState("header");
  const [word, setWord] = useState("");
  const [sortOrder, setSortOrder] = useState("asc"); // "asc" or "desc"

  function handleSubmit(e) {
    e.preventDefault();
    const sortData = { sortBy: selectedSortParam, order: sortOrder };
    if (selectedSortParam === "sortByNumOfWord") {
      sortData.word = word;
    }
    if (selectedSortParam === "sortBySegment") {
      sortData.segment = selectedSegment;
    }

    props.onSortChange(sortData);
  }
  return (
    <Form inline="true" onSubmit={handleSubmit} className="mb-3">
      <InputGroup>
        <DropdownButton
          variant="outline-secondary"
          title={
            {
              sortByName: "По названию документа",
              sortByDate: "По дате",
              sortByComment: "По комментарию",
              sortByNumOfChar: "По колличеству символов",
              sortByNumOfWord: "По встречаемости слова",
              sortBySegment: "По встречаемости сегмента",
            }[selectedSortParam]
          }
          onSelect={(v) => setSelectedSortParam(v)}
        >
          <Dropdown.Item eventKey="sortByName">
            По названию документа
          </Dropdown.Item>
          <Dropdown.Item eventKey="sortByDate">По дате</Dropdown.Item>
          <Dropdown.Item eventKey="sortByComment">По комментарию</Dropdown.Item>
          <Dropdown.Item eventKey="sortByNumOfChar">
            По колличеству символов
          </Dropdown.Item>
          <Dropdown.Item eventKey="sortByNumOfWord">
            По встречаемости слова
          </Dropdown.Item>
          <Dropdown.Item eventKey="sortBySegment">
            По встречаемости сегмента
          </Dropdown.Item>
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
                figure: "Изображение",
              }[selectedSegment]
            }
            onSelect={(v) => setSelectedSegment(v)}
          >
            <Dropdown.Item eventKey="header">Заголовок</Dropdown.Item>
            <Dropdown.Item eventKey="text">Текст</Dropdown.Item>
            <Dropdown.Item eventKey="list">Список</Dropdown.Item>
            <Dropdown.Item eventKey="table">Таблица</Dropdown.Item>
            <Dropdown.Item eventKey="figure">Изображение</Dropdown.Item>
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
