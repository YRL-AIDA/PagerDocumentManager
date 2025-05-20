import React from "react";
import { Modal, Button } from "react-bootstrap";

export default function DocumentModal({ show, onHide, imageUrl, title }) {
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
    </Modal>
  );
}
