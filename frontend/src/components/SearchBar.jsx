import { useState } from "react";
import { Form, Button, InputGroup } from "react-bootstrap";

export default function SearchBar() {
  const [q, setQ] = useState("");
  const onSubmit = (e) => {
    e.preventDefault();
    console.log(q);
  };

  return (
    <Form onSubmit={onSubmit} inline="true" className="mb-3">
      <InputGroup>
        <Form.Control
          placeholder="Поиск…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <Button type="submit" variant="outline-primary">
          Поиск
        </Button>
      </InputGroup>
    </Form>
  );
}
