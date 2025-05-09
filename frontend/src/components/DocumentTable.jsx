import { useState, useEffect } from "react";
import { Table } from "react-bootstrap";

export default function DocumentTable() {
  const [sortConfig, setSortConfig] = useState({ key: "name", dir: "asc" });
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5001/api/documents")
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch(console.error);
  }, []);

  const sorted = [...data].sort((a, b) => {
    const { key, dir } = sortConfig;
    let av = a[key],
      bv = b[key];
    if (key === "date") {
      av = new Date(a.date);
      bv = new Date(b.date);
    }
    let cmp = av < bv ? -1 : av > bv ? 1 : 0;
    return dir === "asc" ? cmp : -cmp;
  });

  const sort = (key) => {
    setSortConfig((cfg) => ({
      key,
      dir: cfg.key === key && cfg.dir === "asc" ? "desc" : "asc",
    }));
  };

  return (
    <Table hover striped bordered size="sm">
      <thead>
        <tr>
          {["name", "date", "comment"].map((key) => (
            <th
              key={key}
              onClick={() => sort(key)}
              style={{ cursor: "pointer" }}
            >
              {
                {
                  name: "Имя",
                  date: "Дата",
                  comment: "Комментарий",
                }[key]
              }
              {sortConfig.key === key
                ? sortConfig.dir === "asc"
                  ? " ↑"
                  : " ↓"
                : ""}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((doc, i) => (
          <tr key={i}>
            <td>{doc.name}</td>
            <td>{new Date(doc.date).toLocaleDateString("ru-RU")}</td>
            <td>{doc.comment}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
