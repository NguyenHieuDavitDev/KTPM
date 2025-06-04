// backend/server.js
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const categoriesRouter = require("./routes/categories");
const productsRouter = require("./routes/products");

const app = express();
const PORT = 5001;

app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use("/api/categories", categoriesRouter);
app.use("/api/products", productsRouter);

app.listen(PORT, () => {
  console.log(`Server đang chạy trên cổng ${PORT}`);
});
