const puppeteer = require("puppeteer");
const connection = require("./db");

const CATEGORY_URLS = [
  "https://cellphones.com.vn/mobile.html",
  "https://cellphones.com.vn/tablet.html",
  "https://cellphones.com.vn/laptop.html",
  "https://cellphones.com.vn/thiet-bi-am-thanh.html",
  "https://cellphones.com.vn/do-choi-cong-nghe.html",
  "https://cellphones.com.vn/phu-kien.html",
  "https://cellphones.com.vn/phu-kien/camera.html",
  "https://cellphones.com.vn/do-gia-dung.html",
  "https://cellphones.com.vn/may-tinh-de-ban.html",
  "https://cellphones.com.vn/man-hinh.html",
  "https://cellphones.com.vn/may-in.html",
  "https://cellphones.com.vn/tivi.html",
  "https://cellphones.com.vn/thu-cu-doi-moi",
  "https://cellphones.com.vn/hang-cu.html",
];

async function crawlCategory(url, browser) {
  const page = await browser.newPage();
  try {
    await page.goto(url, { waitUntil: "networkidle2" });
    await page.waitForSelector(".product-info-container");

    const categoryName = await page.$eval("title", (el) =>
      el.textContent.trim()
    );
    const categorySlug = url.split("/").pop().replace(".html", "");

    const categoryQuery = `
      INSERT INTO categories (name, slug)
      VALUES (?, ?)
      ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
    `;
    const [categoryResult] = await connection
      .promise()
      .execute(categoryQuery, [categoryName, categorySlug]);
    const categoryId = categoryResult.insertId;

    console.log(`✅ Category added or found: ${categoryName}`);

    const products = await page.$$eval(".product-info-container", (cards) =>
      cards.map((card) => {
        const name = card
          .querySelector(".product__name h3")
          ?.textContent.trim();
        const current_price = card
          .querySelector(".product__price--show")
          ?.textContent.trim();
        const image_url = card.querySelector(".product__img")?.src;
        const detail_url = card.querySelector("a.product__link")?.href;

        return { name, current_price, image_url, detail_url };
      })
    );

    for (const product of products) {
      if (!product.name || !product.current_price) continue;

      const insertQuery = `
        INSERT INTO products (name, current_price, image_url, detail_url, category_id)
        VALUES (?, ?, ?, ?, ?)
      `;
      const values = [
        product.name,
        product.current_price,
        product.image_url,
        product.detail_url,
        categoryId,
      ];

      const [result] = await connection.promise().execute(insertQuery, values);
      console.log(`✅ Product added: ${product.name}`);
    }
  } catch (err) {
    console.error("❌ Error crawling category:", err.message);
  } finally {
    await page.close();
  }
}

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  for (const url of CATEGORY_URLS) {
    await crawlCategory(url, browser);
  }
  await browser.close();
})();
