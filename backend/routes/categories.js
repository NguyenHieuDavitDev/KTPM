// backend/routes/categories.js
const express = require("express");
const router = express.Router();
const db = require("../db");

// Lấy danh sách tất cả categories
router.get("/", (req, res) => {
  const sql = "SELECT * FROM categories";
  db.query(sql, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results);
  });
});

// Thêm mới một category
router.post("/", (req, res) => {
  const { name, slug } = req.body;
  const sql = "INSERT INTO categories (name, slug) VALUES (?, ?)";
  db.query(sql, [name, slug], (err, result) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ id: result.insertId, name, slug });
  });
});

// Sửa thông tin của category
router.put("/:id", (req, res) => {
  const { name, slug } = req.body;
  const { id } = req.params;
  const sql = "UPDATE categories SET name = ?, slug = ? WHERE id = ?";
  db.query(sql, [name, slug, id], (err, result) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ id, name, slug });
  });
});

// Xóa một category
router.delete("/:id", (req, res) => {
  const { id } = req.params;
  const sql = "DELETE FROM categories WHERE id = ?";
  db.query(sql, [id], (err, result) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: "Đã xóa category" });
  });
});

module.exports = router;
