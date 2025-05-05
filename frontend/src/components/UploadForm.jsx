import { useState } from "react";
import axios from "axios";
import { Form, Button, ProgressBar, Alert } from "react-bootstrap";

export default function UploadForm() {
  const [files, setFiles] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setMsg] = useState(null);
  function handleUpload() {
    if (!files) {
      setMsg({ variant: "warning", text: "Файл не выбран" });
      return;
    }

    const fd = new FormData();
    for (let i = 0; i < files.length; i++) {
      fd.append(`file${i + 1}`, files[i]);
    }

    setMsg({ variant: "info", text: "Загрузка..." });
    axios
      .post("http://httpbin.org/post", fd, {
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded / e.total) * 100));
        },
        headers: {
          "Custom-Header": "value",
        },
      })
      .then((res) => {
        setMsg({ variant: "success", text: "Успешно" });
        console.log(res.data);
      })
      .catch((err) => {
        setMsg({ variant: "danger", text: "Ошибка загрузки" });
        console.log(err);
      });
  }
  return (
    <Form className="mb-3">
      <Form.Label>Загрузить документ</Form.Label>
      <Form.Control
        type="file"
        multiple
        onChange={(e) => setFiles(e.target.files)}
        accept="image/png, image/jpeg, application/pdf"
        className="mb-2"
      />
      <Button onClick={handleUpload} variant="primary" className="mb-2">
        Загрузить
      </Button>
      {status && (
        <Alert variant={status.variant} className="py-1">
          {status.text}
        </Alert>
      )}
      {progress > 0 && <ProgressBar now={progress} label={`${progress}%`} />}
    </Form>
  );
}
