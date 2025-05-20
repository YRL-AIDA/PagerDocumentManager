import { useState } from "react";
import axios from "axios";
import { Form, Button, Alert, InputGroup } from "react-bootstrap";

export default function UploadForm(props) {
  const [files, setFiles] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setMsg] = useState(null);

  function sendToApi(base64, name) {
    setMsg({ variant: "info", text: `Загрузка ${name}...` });
    const body = { image64: base64, process: "{}" };

    return axios
      .post("/processing", body, {
        headers: { "Content-Type": "application/json" },
        withCredentials: true,
        onUploadProgress: (e) =>
          setProgress(Math.round((e.loaded / e.total) * 100)),
      })
      .then((res) => {
        const json = JSON.parse(res.data);
        props.addToDataBase(json, name, base64);
      })
      .catch((err) => {
        setMsg({ variant: "danger", text: `Ошибка отправки ${name}` });
        console.error(err);
        throw err;
      });
  }

  const processFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result;
        try {
          await sendToApi(base64, file.name);
          resolve();
        } catch {
          reject();
        }
      };
      reader.onerror = () => {
        setMsg({ variant: "danger", text: `Ошибка чтения файла ${file.name}` });
        reject();
      };
      reader.readAsDataURL(file);
    });
  };

  async function handleUpload() {
    if (!files || files.length === 0) {
      setMsg({ variant: "warning", text: "Файл не выбран" });
      return;
    }

    for (let i = 0; i < files.length; i++) {
      try {
        await processFile(files[i]);
      } catch {
        setMsg({ variant: "danger", text: `Ошибка загрузки ${files[i].name}` });
        return;
      }
    }
    setMsg({ variant: "success", text: "Все файлы загружены" });
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
    </Form>
  );
}
