# Product Crawler & Analytics Platform

## Mô Tả Dự Án

Một nền tảng toàn diện để thu thập, phân tích và trực quan hóa dữ liệu sản phẩm từ website FPT, cung cấp insights chi tiết về thị trường công nghệ.

## Cấu Trúc Dự Án

```
project-root/
│
├── crawl/         # Thu thập dữ liệu
│   ├── src/
│   │   ├── crawlers/
│   │   ├── utils/
│   │   └── config/
│   └── package.json
│
├── backend/          # RESTful API Backend
│   ├── src/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   └── middleware/
│   └── package.json
│
└── frontend/         # Ứng dụng React
    ├── src/
    │   ├── components/
    └── package.json
```

## Công Nghệ Chính

### Crawling

- Puppeteer
- Cheerio
- Axios

### Backend

- Node.js
- Express.js
- MySQL

### Frontend

- React.js
- Recharts
- Bootstrap
- Axios

## Cài Đặt & Khởi Chạy

### Yêu Cầu Hệ Thống

- Node.js (v16+)
- npm (v8+)
- MySQL (v8+)

### Bước Cài Đặt

1. **Clone Dự Án**

```bash
git clone https://github.com/yourusername/fpt-product-crawler.git
cd fpt-product-crawler
```

2. **Cài Đặt Các Module**

```bash
# Cài đặt crawl
cd crawlFPT
npm install

# Cài đặt backend
cd ../backend
npm install

# Cài đặt frontend
cd ../frontend
npm install
```

3. **Cấu Hình Môi Trường**

- Tạo file `.env` trong từng thư mục
- Điền các biến môi trường cần thiết

### Khởi Chạy Dự Án

```bash
# Chạy Crawler
cd crawlFPT
npm start

# Chạy Backend (Development)
cd backend
npm run dev

# Chạy Frontend
cd frontend
npm start
```

## Chức Năng Chính

- Thu thập dữ liệu sản phẩm từ FPT
- Lưu trữ dữ liệu có cấu trúc
- Phân tích xu hướng sản phẩm
- Trực quan hóa dữ liệu

## Báo Cáo & Thống Kê

- Biểu đồ giá sản phẩm
- Phân tích danh mục
- Xu hướng thị trường

## Tính Năng Nổi Bật

- **Crawling Thông Minh:** Sử dụng Puppeteer để thu thập dữ liệu động
- **API Linh Hoạt:** RESTful endpoint dễ dàng mở rộng
- **Trực Quan Hóa Ấn Tượng:** Biểu đồ tương tác với Recharts

---

**Lưu Ý:** Luôn tuân thủ quy định pháp lý và điều khoản sử dụng của website nguồn khi crawl dữ liệu.
