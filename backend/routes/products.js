// backend/routes/products.js
const express = require("express");
const router = express.Router();
const db = require("../db");

// Lấy danh sách tất cả products
router.get("/", (req, res) => {
  const sql = "SELECT * FROM products";
  db.query(sql, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results);
  });
});

// Thêm mới một product
router.post("/", (req, res) => {
  const { name, current_price, image_url, detail_url, category_id } = req.body;
  const sql =
    "INSERT INTO products (name, current_price, image_url, detail_url, category_id) VALUES (?, ?, ?, ?, ?)";
  db.query(
    sql,
    [name, current_price, image_url, detail_url, category_id],
    (err, result) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({
        id: result.insertId,
        name,
        current_price,
        image_url,
        detail_url,
        category_id,
      });
    }
  );
});

// Sửa thông tin của product
router.put("/:id", (req, res) => {
  const { name, current_price, image_url, detail_url, category_id } = req.body;
  const { id } = req.params;
  const sql =
    "UPDATE products SET name = ?, current_price = ?, image_url = ?, detail_url = ?, category_id = ? WHERE id = ?";
  db.query(
    sql,
    [name, current_price, image_url, detail_url, category_id, id],
    (err, result) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id, name, current_price, image_url, detail_url, category_id });
    }
  );
});

// Xóa một product
router.delete("/:id", (req, res) => {
  const { id } = req.params;
  const sql = "DELETE FROM products WHERE id = ?";
  db.query(sql, [id], (err, result) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ message: "Đã xóa product" });
  });
});

module.exports = router;
