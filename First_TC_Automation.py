import unittest
import time
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class LocalSignUpTest(unittest.TestCase):
    CSV_FILE = "local_test_results.csv"
    HTML_FILE_PATH = "file:///Users/hieu/Documents/Python2/First_TC_Automation/signup_form.html"

    @classmethod
    def setUpClass(cls):
        """Tạo file CSV nếu chưa tồn tại"""
        if not os.path.exists(cls.CSV_FILE):
            with open(cls.CSV_FILE, mode="w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Email", "Password", "Confirm Password", "Result", "Response Time"])

    def setUp(self):
        """Khởi động Chrome và mở file HTML cục bộ"""
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(self.HTML_FILE_PATH)

    def fill_form_and_submit(self, email, password, confirm_password):
        """Điền form đăng ký và submit"""
        driver = self.driver
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "passwordConfirm").clear()
        driver.find_element(By.ID, "passwordConfirm").send_keys(confirm_password)

        # Kiểm tra nút submit có hoạt động không
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        self.assertTrue(submit_button.is_enabled(), "Nút đăng ký không khả dụng!")

        start_time = time.time()
        submit_button.click()
        time.sleep(2)  # Chờ phản hồi từ trang
        response_time = round(time.time() - start_time, 2)

        # Kiểm tra thông báo thành công (theo nội dung text 'Success' xuất hiện trên trang)
        success_message = driver.find_elements(By.XPATH, "//div[contains(text(),'Success')]")
        result = "Đăng ký thành công" if success_message else "Đăng ký thất bại"

        # Ghi kết quả vào CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.CSV_FILE, mode="a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, email, password, confirm_password, result, response_time])
        return success_message

    def test_ui_elements_present(self):
        """Kiểm tra giao diện các thành phần hiển thị đúng"""
        driver = self.driver
        self.assertTrue(driver.find_element(By.ID, "email").is_displayed(), "Trường email không hiển thị!")
        self.assertTrue(driver.find_element(By.ID, "password").is_displayed(), "Trường password không hiển thị!")
        self.assertTrue(driver.find_element(By.ID, "passwordConfirm").is_displayed(), "Trường confirm password không hiển thị!")
        self.assertTrue(driver.find_element(By.XPATH, "//button[@type='submit']").is_displayed(), "Nút submit không hiển thị!")

    def test_valid_signup(self):
        """Test đăng ký thành công với dữ liệu hợp lệ"""
        result = self.fill_form_and_submit("test@example.com", "ValidPass123", "ValidPass123")
        self.assertTrue(result, "Đăng ký không thành công với dữ liệu hợp lệ!")

    def test_invalid_inputs(self):
        """Test các trường hợp đầu vào không hợp lệ theo nhóm"""
        invalid_email_cases = [
            {"email": "invalid-email", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email thiếu ký tự @"},
            {"email": "user@invalid", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email thiếu domain hợp lệ"},
            {"email": "user@@example.com", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email chứa nhiều @"},
            {"email": "<script>alert('XSS')</script>", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email chứa XSS"},
            {"email": "' OR 1=1 --", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email chứa SQL Injection"},
            {"email": "{\"email\":\"test@example.com\"}", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email chứa JSON"}
        ]

        invalid_password_cases = [
            {"email": "test@example.com", "password": "123", "confirm": "123", "desc": "Mật khẩu quá ngắn"},
            {"email": "test@example.com", "password": "alllowercase123", "confirm": "alllowercase123", "desc": "Mật khẩu không có chữ hoa"},
            {"email": "test@example.com", "password": "ValidPass123", "confirm": "DifferentPass123", "desc": "Mật khẩu không khớp"},
            {"email": "test@example.com", "password": "12345678", "confirm": "12345678", "desc": "Mật khẩu chỉ chứa số"},
            {"email": "test@example.com", "password": "A" * 101, "confirm": "A" * 101, "desc": "Mật khẩu quá dài"},
            {"email": "test@example.com", "password": "<script>alert('Hacked')</script>", "confirm": "<script>alert('Hacked')</script>", "desc": "Mật khẩu chứa XSS"}
        ]

        other_cases = [
            {"email": "", "password": "", "confirm": "", "desc": "Trường để trống"},
            {"email": " ", "password": " ", "confirm": " ", "desc": "Chỉ nhập khoảng trắng"},
            {"email": "   test@example.com   ", "password": "   ValidPass123   ", "confirm": "   ValidPass123   ", "desc": "Email và mật khẩu có khoảng trắng thừa"}
        ]

        # Kiểm thử email không hợp lệ
        for case in invalid_email_cases:
            with self.subTest(msg=case["desc"]):
                result = self.fill_form_and_submit(case["email"], case["password"], case["confirm"])
                self.assertFalse(result, f"Không nên cho phép: {case['desc']}")

        # Kiểm thử mật khẩu không hợp lệ
        for case in invalid_password_cases:
            with self.subTest(msg=case["desc"]):
                result = self.fill_form_and_submit(case["email"], case["password"], case["confirm"])
                self.assertFalse(result, f"Không nên cho phép: {case['desc']}")

        # Kiểm thử các trường hợp khác
        for case in other_cases:
            with self.subTest(msg=case["desc"]):
                result = self.fill_form_and_submit(case["email"], case["password"], case["confirm"])
                self.assertFalse(result, f"Không nên cho phép: {case['desc']}")

    def test_spam_signup(self):
        """Test đăng ký quá nhanh nhiều lần (spam)"""
        # Giả lập spam: thực hiện 5 lần đăng ký liên tiếp với cùng dữ liệu
        result = None
        for _ in range(5):
            result = self.fill_form_and_submit("spam@example.com", "ValidPass123", "ValidPass123")
            time.sleep(0.5)  # Giảm thời gian giữa các lần click để mô phỏng spam
        self.assertFalse(result, "Không nên cho phép spam đăng ký!")

    def tearDown(self):
        """Đóng trình duyệt sau khi test xong"""
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
