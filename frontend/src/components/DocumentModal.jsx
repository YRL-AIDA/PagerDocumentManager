import React from "react";
import { Modal, Button } from "react-bootstrap";

export default function DocumentModal({ show, onHide, imageUrl, title }) {
  const extMatch = imageUrl?.match(/\.(png|jpe?g|pdf)(\?|$)/i);
  const ext = extMatch ? extMatch[0] : "";
  const downloadFilename = `${title || "document"}${ext}`;

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>{title || "Просмотр документа"}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="text-center">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Документ"
            style={{ maxWidth: "100%", height: "auto" }}
          />
        ) : (
          <p>Изображение отсутствует</p>
        )}
      </Modal.Body>
      <Modal.Footer>
        {imageUrl && (
          <a
            href={imageUrl}
            download={downloadFilename}
            className="btn btn-primary"
          >
            Скачать
          </a>
        )}
      </Modal.Footer>
    </Modal>
  );
}
