import { useState } from "react";
import {
  Form,
  Button,
  InputGroup,
  Collapse,
  Row,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
} from "react-bootstrap";

export default function SearchBar({
  onSearch,
  onLabelsChange,
  onParamsChange,
}) {
  const [q, setQ] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [value, setValue] = useState();
  const [param, setParam] = useState();
  const [status, setMsg] = useState(null);

  const handleChangeVal = (val) => {
    setValue(val);
  };

  const handleChangeParam = (par) => {
    setParam(par);
  };

  const handleReset = () => {
    setQ("");
    setMsg({ variant: "secondary", text: "Поиск сброшен" });
    onSearch("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const searchData = {
      query: q,
      advanced: showAdvanced,
    };

    if (q === "") {
      setMsg({ variant: "warning", text: "Поле ввода пустое!" });
      return;
    } else {
      setMsg({ variant: "success", text: "Поиск выполнен!" });
    }

    if (showAdvanced) {
      searchData.fields = {
        header: value?.includes("header") || false,
        text: value?.includes("text") || false,
        list: value?.includes("list") || false,
        table: value?.includes("table") || false,
        name: value?.includes("name") || false,
        commentary: value?.includes("commentary") || false,
      };

      searchData.params = {
        caseSensitive: param?.includes("register") || false,
        fullWordMatch: param?.includes("full-word") || false,
        ignorePunctuation: param?.includes("punct-marks") || false,
        ignoreSpaces: param?.includes("spaces") || false,
      };
    }

    onSearch(q.trim());
    onLabelsChange(value || []);
    onParamsChange(param || []);
  };

  return (
    <Form onSubmit={handleSubmit} inline="true" className="mb-3">
      <div className="mt-2 p-3 border rounded bg-light">
        <Form.Label htmlFor="search">
          Искать по содержимому документов
        </Form.Label>
        <InputGroup>
          <Form.Control
            placeholder="Поиск…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            id="search"
          />
          <Button
            type="submit"
            variant="outline-primary"
            style={{ width: "10%" }}
          >
            Поиск
          </Button>
          <Button variant="outline-secondary" onClick={handleReset}>
            Сброс
          </Button>
        </InputGroup>
        {status && (
          <Alert variant={status.variant} className="py-1 mt-2">
            {status.text}
          </Alert>
        )}
        <Button
          variant="outline-primary"
          onClick={() => setShowAdvanced((s) => !s)}
          className="mt-2"
        >
          {showAdvanced ? "Скрыть расширенный поиск" : "Расширенный поиск"}
        </Button>
        <Collapse in={showAdvanced}>
          <div className="mt-2 p-3 border rounded bg-light">
            <Row>
              <p>Искать в</p>
              <ToggleButtonGroup
                type="checkbox"
                value={value}
                onChange={handleChangeVal}
              >
                <ToggleButton
                  id="tbg-btn-1-val"
                  variant="outline-primary"
                  value={"header"}
                >
                  Заголовках
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-2-val"
                  variant="outline-primary"
                  value={"text"}
                >
                  Тексте
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-3-val"
                  variant="outline-primary"
                  value={"list"}
                >
                  Списках
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-4-val"
                  variant="outline-primary"
                  value={"table"}
                >
                  Таблицах
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-5-val"
                  variant="outline-primary"
                  value={"name"}
                >
                  Названии документов
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-6-val"
                  variant="outline-primary"
                  value={"commentary"}
                >
                  Комментариях
                </ToggleButton>
              </ToggleButtonGroup>
            </Row>
            <p className="mt-3">Параметры поиска</p>
            <Row>
              <ToggleButtonGroup
                type="checkbox"
                value={param}
                onChange={handleChangeParam}
              >
                <ToggleButton
                  id="tbg-btn-1-param"
                  variant="outline-primary"
                  value={"register"}
                >
                  Учитывать регистр
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-2-param"
                  variant="outline-primary"
                  value={"full-word"}
                >
                  Слово целиком
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-3-param"
                  variant="outline-primary"
                  value={"punct-marks"}
                >
                  Не учитывать знаки препинания
                </ToggleButton>
                <ToggleButton
                  id="tbg-btn-4-param"
                  variant="outline-primary"
                  value={"spaces"}
                >
                  Не учитывать пробелы
                </ToggleButton>
              </ToggleButtonGroup>
            </Row>
          </div>
        </Collapse>
      </div>
    </Form>
  );
}
