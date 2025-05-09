import { useState } from "react";
import axios from "axios";
import { Form, Button, ProgressBar, Alert, InputGroup } from "react-bootstrap";

export default function UploadForm(props) {
  const [files, setFiles] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setMsg] = useState(null);

  function sendToApi(base64, name) {
    setMsg({ variant: "info", text: "Загрузка..." });
    const body = { image64: base64, process: "{}" };

    axios
      .post("/processing", body, {
        headers: { "Content-Type": "application/json" },
        onUploadProgress: (e) =>
          setProgress(Math.round((e.loaded / e.total) * 100)),
      })
      .then((res) => {
        const json = JSON.parse(res.data);
        setMsg({ variant: "success", text: "Успешно" });
        props.addToDataBase(json, name);
      })
      .catch((err) => {
        setMsg({ variant: "danger", text: "Ошибка отправки" });
        console.error(err);
      });
  }

  function handleUpload() {
    if (!files || files.length === 0) {
      setMsg({ variant: "warning", text: "Файл не выбран" });
      return;
    }
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result;
      // const base64 = dataUrl;
      sendToApi(base64, file.name);
    };
    reader.onerror = () => {
      setMsg({ variant: "danger", text: "Ошибка чтения файла" });
    };
    reader.readAsDataURL(file);
  }
  return (
    <Form className="mb-3">
      <Form.Label>Загрузить документ</Form.Label>
      <InputGroup>
        <Form.Control
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          accept="image/png, image/jpeg, application/pdf"
          className="mb-2"
        />
        <Button
          onClick={handleUpload}
          variant="primary"
          className="mb-2"
          style={{ width: "10%" }}
        >
          Загрузить
        </Button>
      </InputGroup>
      {status && (
        <Alert variant={status.variant} className="py-1">
          {status.text}
        </Alert>
      )}
      {progress > 0 && <ProgressBar now={progress} label={`${progress}%`} />}
    </Form>
  );
}
