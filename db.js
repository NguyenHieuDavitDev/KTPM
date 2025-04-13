// db.js
const mysql = require("mysql2");

const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "", // Thay đổi nếu có mật khẩu
  database: "crawl_fpt",
});

connection.connect((err) => {
  if (err) {
    console.error("❌ Kết nối MySQL thất bại:", err.message);
  } else {
    console.log("✅ Kết nối MySQL thành công!");
  }
});

module.exports = connection;
