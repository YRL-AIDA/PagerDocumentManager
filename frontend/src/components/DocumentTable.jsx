import { useState } from "react";
import { Table } from "react-bootstrap";

export default function DocumentTable() {
  const [sortConfig, setSortConfig] = useState({ key: "name", dir: "asc" });
  const data = [
    { name: "Doc 1", date: new Date(2025, 4, 1), size: 50 },
    { name: "Doc 2", date: new Date(2025, 4, 1), size: 60 },
    // …
  ];

  const sorted = [...data].sort((a, b) => {
    const { key, dir } = sortConfig;
    let cmp = a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0;
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
          {["name", "date", "size"].map((key) => (
            <th
              key={key}
              onClick={() => sort(key)}
              style={{ cursor: "pointer" }}
            >
              {
                {
                  name: "Имя",
                  date: "Дата",
                  size: "Размер",
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
            <td>{doc.date.toLocaleDateString("ru-RU")}</td>
            <td>{doc.size}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
