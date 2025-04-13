DROP DATABASE IF EXISTS crawl_fpt;
CREATE DATABASE IF NOT EXISTS crawl_fpt;
USE crawl_fpt;

-- Tạo bảng categories (Danh mục sản phẩm)
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  slug VARCHAR(255) UNIQUE
);

-- Tạo bảng products (Sản phẩm)
DROP TABLE IF EXISTS products;
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name TEXT,
  current_price VARCHAR(50),
  image_url TEXT,
  detail_url TEXT,
  category_id INT,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);
