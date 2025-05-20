import { useState, useEffect } from "react";
import { Table, Button, FormControl, ButtonGroup } from "react-bootstrap";
import DocumentModal from "./DocumentModal";

export default function DocumentTable({
  search,
  labels,
  sortOptions,
  searchParams,
  refreshToggle,
}) {
  const [data, setData] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editValues, setEditValues] = useState({ name: "", comment: "" });

  const [showModal, setShowModal] = useState(false);
  const [modalImageUrl, setModalImageUrl] = useState("");

  // подставные заголовки для метрик
  const metricTitles = {
    sortByNumOfChar: "Символов",
    sortByNumOfWord: "Вхождений слова",
    sortBySegment: "Сегментов",
  };
  const isMetric = [
    "sortByNumOfChar",
    "sortByNumOfWord",
    "sortBySegment",
  ].includes(sortOptions.sortBy);
  const metricTitle = metricTitles[sortOptions.sortBy] || "Метрика";

  // загрузка данных
  const fetchData = () => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    labels.forEach((lbl) => params.append("labels", lbl));
    searchParams.forEach((prm) => params.append("searchParams", prm));
    params.set("sortBy", sortOptions.sortBy);
    params.set("order", sortOptions.order);
    if (sortOptions.word) params.set("word", sortOptions.word);
    if (sortOptions.segment) params.set("segment", sortOptions.segment);

    fetch(`http://localhost:5001/api/documents?${params}`, {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => console.error("Fetch documents failed:", err));
  };

  useEffect(fetchData, [
    search,
    labels,
    searchParams,
    sortOptions,
    refreshToggle,
  ]);

  const onViewClick = (e, doc) => {
    e.stopPropagation();
    if (doc.image_url) {
      setModalImageUrl(doc.image_url);
      setShowModal(true);
    }
  };

  return (
    <>
      <Table hover striped bordered size="sm">
        <thead>
          <tr>
            <th>Имя</th>
            <th>Дата</th>
            <th>Комментарий</th>
            {isMetric && <th>{metricTitle}</th>}
            <th>Действия</th>
          </tr>
        </thead>

        <tbody>
          {data.map((doc) => (
            <tr key={doc.id}>
              {/* Имя */}
              <td>
                {editingId === doc.id ? (
                  <FormControl
                    value={editValues.name}
                    onChange={(e) =>
                      setEditValues((ev) => ({ ...ev, name: e.target.value }))
                    }
                  />
                ) : (
                  doc.name
                )}
              </td>

              {/* Дата */}
              <td>{new Date(doc.date).toLocaleDateString("ru-RU")}</td>

              {/* Комментарий */}
              <td>
                {editingId === doc.id ? (
                  <FormControl
                    value={editValues.comment}
                    onChange={(e) =>
                      setEditValues((ev) => ({
                        ...ev,
                        comment: e.target.value,
                      }))
                    }
                  />
                ) : (
                  doc.comment
                )}
              </td>

              {/* Новый столбец метрики */}
              {isMetric && <td>{doc.score ?? 0}</td>}

              {/* Действия */}
              <td>
                <div className="d-flex w-100 h-100">
                  {editingId === doc.id ? (
                    <ButtonGroup className="d-flex w-100 h-100 mt-1">
                      <Button
                        size="sm"
                        variant="outline-success"
                        onClick={() => {
                          fetch(
                            `http://localhost:5001/api/documents/${doc.id}`,
                            {
                              method: "PATCH",
                              credentials: "include",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify(editValues),
                            }
                          ).then(() => {
                            setEditingId(null);
                            fetchData();
                          });
                        }}
                      >
                        Сохранить
                      </Button>
                      <Button
                        size="sm"
                        variant="outline-danger"
                        onClick={() => setEditingId(null)}
                      >
                        Отмена
                      </Button>
                    </ButtonGroup>
                  ) : (
                    <ButtonGroup className="d-flex w-100 h-100">
                      <Button
                        size="sm"
                        variant="outline-primary"
                        onClick={() => {
                          setEditingId(doc.id);
                          setEditValues({
                            name: doc.name,
                            comment: doc.comment,
                          });
                        }}
                      >
                        Редактировать
                      </Button>
                      <Button
                        size="sm"
                        variant="outline-danger"
                        onClick={() => {
                          if (window.confirm("Удалить документ?")) {
                            fetch(
                              `http://localhost:5001/api/documents/${doc.id}`,
                              {
                                method: "DELETE",
                                credentials: "include",
                              }
                            ).then((res) => {
                              if (res.ok) fetchData();
                            });
                          }
                        }}
                      >
                        Удалить
                      </Button>
                      <Button
                        size="sm"
                        variant="outline-info"
                        onClick={(e) => onViewClick(e, doc)}
                        disabled={!doc.image_url}
                      >
                        Просмотр
                      </Button>
                    </ButtonGroup>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <DocumentModal
        show={showModal}
        onHide={() => setShowModal(false)}
        imageUrl={modalImageUrl}
      />
    </>
  );
}
