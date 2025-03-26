import requests
from bs4 import BeautifulSoup
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import os
import webbrowser


def fix_url(url, base_url):
    if not url:
        return ""
    if url.startswith("/"):
        return base_url + url
    return url


def get_best_image_from_source(srcset_string, base_url):
    """
    srcset_string thường có dạng:
      "https://...1.jpg?w=220 1x, https://...2.jpg?w=220 2x"
    Ta tách theo dấu ',' và ưu tiên dòng có '2x'. Nếu không thấy, lấy dòng cuối.
    """
    if not srcset_string:
        return ""
    # Tách thành các phần tử ["https://...1.jpg 1x", " https://...2.jpg 2x"]
    candidates = [c.strip() for c in srcset_string.split(",") if c.strip()]
    if not candidates:
        return ""

    # Thử tìm dòng có "2x"
    best_url = ""
    for c in candidates:
        if "2x" in c:
            # c dạng "https://...2.jpg 2x"
            best_url = c.split()[0]  # Lấy phần đầu (URL)
            break

    # Nếu không tìm thấy "2x", lấy dòng cuối
    if not best_url:
        last_candidate = candidates[-1]
        best_url = last_candidate.split()[0]

    return fix_url(best_url, base_url)


def crawl_vnexpress():
    """
    Ví dụ crawl trang chủ VnExpress để minh họa cách lấy ảnh trong <picture>.
    """
    base_url = "https://vnexpress.net"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/90.0.4430.93 Safari/537.36")
    }
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print("Không thể truy cập trang web")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    # Duyệt qua tất cả các thẻ <h3> chứa tiêu đề bài báo
    for h3 in soup.find_all('h3'):
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href'):
            title = a_tag.get_text(strip=True)
            link = fix_url(a_tag['href'], base_url)

            # Lấy mô tả: cố gắng lấy thẻ <p> liền sau h3
            description = ""
            next_p = h3.find_next_sibling('p')
            if next_p:
                description = next_p.get_text(strip=True)

            # Lấy URL hình ảnh:
            parent = h3.parent
            img_url = ""

            if parent:
                # Tìm <picture>
                picture_tag = parent.find("picture")
                if picture_tag:
                    # Ưu tiên lấy <source data-srcset> hoặc <source srcset>
                    source_tag = picture_tag.find("source", attrs={"data-srcset": True})
                    if source_tag and source_tag["data-srcset"]:
                        img_url = get_best_image_from_source(source_tag["data-srcset"], base_url)
                    else:
                        # Thử srcset thường
                        source_tag = picture_tag.find("source", attrs={"srcset": True})
                        if source_tag and source_tag["srcset"]:
                            img_url = get_best_image_from_source(source_tag["srcset"], base_url)

                    # Nếu chưa có, fallback sang <img> trong <picture>
                    if not img_url:
                        img_in_picture = picture_tag.find("img")
                        if img_in_picture and img_in_picture.get("src"):
                            img_url = fix_url(img_in_picture["src"], base_url)

                # Nếu không có <picture> hoặc không tìm thấy ảnh, fallback <img> cũ
                if not img_url:
                    img_tag = parent.find("img")
                    if img_tag and img_tag.get('src'):
                        img_url = fix_url(img_tag['src'], base_url)

            news_items.append((title, link, description, img_url))
    return news_items


def store_to_mysql(news_items):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='newsdb', charset='utf8mb4')
        cursor = conn.cursor()
        # Tạo bảng nếu chưa tồn tại (bao gồm trường image_url)
        create_table_query = """
            CREATE TABLE IF NOT EXISTS znews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                link VARCHAR(255),
                description TEXT,
                image_url VARCHAR(512)
            )
        """
        cursor.execute(create_table_query)
        # Chèn dữ liệu (lưu ý: nếu chạy nhiều lần, dữ liệu có thể bị trùng)
        insert_query = "INSERT INTO znews (title, link, description, image_url) VALUES (%s, %s, %s, %s)"
        cursor.executemany(insert_query, news_items)
        conn.commit()
        cursor.close()
        conn.close()
        print("Lưu dữ liệu thành công vào MySQL!")
    except Exception as e:
        print("Lỗi khi lưu dữ liệu:", e)


def generate_report():
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='', db='newsdb', charset='utf8mb4')
        df = pd.read_sql("SELECT * FROM znews", con=conn)
        conn.close()
    except Exception as e:
        print("Lỗi khi đọc dữ liệu từ MySQL:", e)
        return None

    # Tạo biểu đồ: ví dụ so sánh độ dài tiêu đề
    df['title_length'] = df['title'].apply(len)
    plt.figure(figsize=(10, 6))
    plt.bar(df['id'], df['title_length'], color='skyblue')
    plt.xlabel("ID Bài Báo")
    plt.ylabel("Độ Dài Tiêu Đề")
    plt.title("Biểu đồ độ dài tiêu đề của các bài báo")
    chart_file = "chart.png"
    plt.savefig(chart_file)
    plt.close()

    # Xây dựng nội dung HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
      <head>
        <meta charset="utf-8">
        <title>Báo cáo VnExpress</title>
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <!-- Font Awesome -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <!-- DataTables CSS -->
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.25/css/dataTables.bootstrap4.min.css">
        <style>
          body {{
            padding: 20px;
          }}
          .report-header {{
            margin-bottom: 30px;
          }}
          .report-header h1 {{
            font-size: 2.5rem;
            font-weight: bold;
          }}
          .report-header p {{
            font-size: 1.2rem;
          }}
          .chart-section {{
            margin: 40px 0;
          }}
          .img-thumb {{
            max-width: 100px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <header class="report-header text-center">
            <h1><i class="fas fa-newspaper"></i> Báo cáo VnExpress</h1>
            <p><i class="fas fa-chart-pie"></i> Tổng số bài báo: {len(df)}</p>
          </header>
          <section class="chart-section text-center">
            <h2><i class="fas fa-chart-bar"></i> Biểu đồ độ dài tiêu đề</h2>
            <img src="{chart_file}" alt="Biểu đồ độ dài tiêu đề" class="img-fluid">
          </section>
          <section class="news-list">
            <h2 class="mb-3"><i class="fas fa-list"></i> Danh sách bài báo</h2>
            <div class="table-responsive">
              <table id="newsTable" class="table table-striped table-bordered">
                <thead class="thead-dark">
                  <tr>
                    <th>ID</th>
                    <th>Hình ảnh</th>
                    <th>Tiêu đề</th>
                    <th>Mô tả</th>
                    <th>Link</th>
                  </tr>
                </thead>
                <tbody>
    """
    for _, row in df.iterrows():
        if row["image_url"]:
            image_html = f'<img src="{row["image_url"]}" alt="Hình ảnh" class="img-thumbnail img-thumb">'
        else:
            image_html = "Không có"
        html_content += f"""
                  <tr>
                    <td>{row['id']}</td>
                    <td>{image_html}</td>
                    <td>{row['title']}</td>
                    <td>{row['description']}</td>
                    <td><a href="{row['link']}" target="_blank"><i class="fas fa-external-link-alt"></i> {row['link']}</a></td>
                  </tr>
        """
    html_content += """
                </tbody>
              </table>
            </div>
          </section>
        </div>
        <!-- jQuery, Popper.js, Bootstrap JS -->
        <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        <!-- DataTables JS -->
        <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap4.min.js"></script>
        <script>
          $(document).ready(function() {{
            $('#newsTable').DataTable({{
              "pageLength": 10,
              "lengthChange": true,
              "searching": true,
              "ordering": true,
              "info": true,
              "autoWidth": false
            }});
          }});
        </script>
      </body>
    </html>
    """
    report_file = "report.html"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Báo cáo HTML được tạo thành công!")
    return report_file


if __name__ == "__main__":
    news_items = crawl_vnexpress()
    print(f"Tìm thấy {len(news_items)} bài báo.")

    if news_items:
        store_to_mysql(news_items)
    else:
        print("Không có dữ liệu để lưu.")

    report_file = generate_report()
    if report_file:
        full_path = os.path.realpath(report_file)
        print(f"Mở báo cáo: {full_path}")
        webbrowser.open('file://' + full_path)
