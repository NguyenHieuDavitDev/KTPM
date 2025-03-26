import csv
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Base Task class: tất cả các task kế thừa đều phải triển khai phương thức run()
class Task:
    def __init__(self, name):
        self.name = name

    def run(self, driver):
        raise NotImplementedError("Subclasses must implement run() method.")


# Task 1: Kiểm tra giao diện (UI) - xem các thành phần cần thiết có hiển thị không
class UITask(Task):
    def __init__(self):
        super().__init__("UI Check")

    def run(self, driver):
        start_time = time.time()
        try:
            email_visible = driver.find_element(By.ID, "email").is_displayed()
            password_visible = driver.find_element(By.ID, "password").is_displayed()
            confirm_visible = driver.find_element(By.ID, "passwordConfirm").is_displayed()
            submit_visible = driver.find_element(By.XPATH, "//button[@type='submit']").is_displayed()

            if email_visible and password_visible and confirm_visible and submit_visible:
                result = "Success"
                details = "All essential UI elements are visible."
            else:
                result = "Failure"
                details = "One or more UI elements are not visible."
        except Exception as e:
            result = "Failure"
            details = f"Exception occurred: {e}"
        response_time = round(time.time() - start_time, 2)
        return self.name, result, details, response_time


# Task 2: Kiểm tra ràng buộc đầu vào khi các trường để trống
class EmptyInputTask(Task):
    def __init__(self):
        super().__init__("Empty Input Validation")

    def run(self, driver):
        start_time = time.time()
        try:
            # Clear các trường
            driver.find_element(By.ID, "email").clear()
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "passwordConfirm").clear()
            # Submit form với dữ liệu rỗng
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(2)
            # Kiểm tra thông báo lỗi
            errors = driver.find_elements(By.XPATH, "//*[contains(text(),'Error') or contains(text(),'error')]")
            if errors:
                result = "Success"
                details = "Error messages displayed for empty inputs."
            else:
                result = "Failure"
                details = "No error messages displayed for empty inputs."
        except Exception as e:
            result = "Failure"
            details = f"Exception occurred: {e}"
        response_time = round(time.time() - start_time, 2)
        return self.name, result, details, response_time


# Task 3: Kiểm tra ràng buộc đầu vào cho các trường (Email, Password)
class InputValidationTask(Task):
    def __init__(self, email, password, confirm, description):
        super().__init__(f"Input Validation - {description}")
        self.email = email
        self.password = password
        self.confirm = confirm

    def run(self, driver):
        start_time = time.time()
        try:
            driver.find_element(By.ID, "email").clear()
            driver.find_element(By.ID, "email").send_keys(self.email)
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys(self.password)
            driver.find_element(By.ID, "passwordConfirm").clear()
            driver.find_element(By.ID, "passwordConfirm").send_keys(self.confirm)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(2)
            errors = driver.find_elements(By.XPATH, "//*[contains(text(),'Error') or contains(text(),'error')]")
            if errors:
                result = "Success"
                details = f"Proper error messages displayed for case: {self.email}, {self.password}, {self.confirm}"
            else:
                result = "Failure"
                details = f"No error messages for case: {self.email}, {self.password}, {self.confirm}"
        except Exception as e:
            result = "Failure"
            details = f"Exception occurred: {e}"
        response_time = round(time.time() - start_time, 2)
        return self.name, result, details, response_time


# Task 4: Kiểm tra bảo mật (XSS)
class XSSTask(Task):
    def __init__(self):
        super().__init__("Security Test - XSS")

    def run(self, driver):
        start_time = time.time()
        try:
            driver.find_element(By.ID, "email").clear()
            # Nhập payload XSS vào trường email
            driver.find_element(By.ID, "email").send_keys("<script>alert('XSS')</script>")
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys("ValidPass123")
            driver.find_element(By.ID, "passwordConfirm").clear()
            driver.find_element(By.ID, "passwordConfirm").send_keys("ValidPass123")
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(2)
            # Kiểm tra alert xuất hiện
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                alert.accept()  # Đóng alert
                result = "Failure"
                details = f"XSS vulnerability detected: Alert triggered with text '{alert_text}'"
            except Exception:
                result = "Success"
                details = "No XSS vulnerability detected."
        except Exception as e:
            result = "Failure"
            details = f"Exception occurred: {e}"
        response_time = round(time.time() - start_time, 2)
        return self.name, result, details, response_time


# Task 5: Đo hiệu năng của việc gửi form hợp lệ
class PerformanceTask(Task):
    def __init__(self):
        super().__init__("Performance Test - Valid Submission")

    def run(self, driver):
        start_time = time.time()
        try:
            driver.find_element(By.ID, "email").clear()
            driver.find_element(By.ID, "email").send_keys("test@example.com")
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys("ValidPass123")
            driver.find_element(By.ID, "passwordConfirm").clear()
            driver.find_element(By.ID, "passwordConfirm").send_keys("ValidPass123")
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(2)
            success = driver.find_elements(By.XPATH, "//*[contains(text(),'Success')]")
            if success:
                result = "Success"
                details = "Valid submission processed correctly."
            else:
                result = "Failure"
                details = "Valid submission did not process as expected."
        except Exception as e:
            result = "Failure"
            details = f"Exception occurred: {e}"
        response_time = round(time.time() - start_time, 2)
        return self.name, result, details, response_time


# Helper: Khởi tạo file CSV với header nếu chưa tồn tại
def setup_csv(csv_file):
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Task", "Result", "Details", "Response Time"])
    print(f"CSV file initialized: {csv_file}")


# Helper: Ghi một dòng kết quả vào file CSV
def write_csv_row(csv_file, row):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# Hàm chạy tất cả các task và ghi kết quả vào file CSV
def run_all_tasks(csv_file, html_file):
    # Danh sách các task cần kiểm thử
    tasks = []
    tasks.append(UITask())
    tasks.append(EmptyInputTask())

    # Các test case cho đầu vào không hợp lệ (email & password)
    invalid_cases = [
        {"email": "invalid-email", "password": "ValidPass123", "confirm": "ValidPass123", "desc": "Email missing '@'"},
        {"email": "user@invalid", "password": "ValidPass123", "confirm": "ValidPass123",
         "desc": "Email without proper domain"},
        {"email": "user@@example.com", "password": "ValidPass123", "confirm": "ValidPass123",
         "desc": "Email with multiple '@'"},
        {"email": "test@example.com", "password": "123", "confirm": "123", "desc": "Password too short"},
        {"email": "test@example.com", "password": "ValidPass123", "confirm": "DifferentPass",
         "desc": "Password mismatch"}
    ]
    for case in invalid_cases:
        tasks.append(InputValidationTask(case["email"], case["password"], case["confirm"], case["desc"]))

    tasks.append(XSSTask())
    tasks.append(PerformanceTask())

    # Khởi tạo Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for task in tasks:
        # Đảm bảo mỗi task chạy trên trạng thái trang mới
        driver.get(html_file)
        task_name, result, details, response_time = task.run(driver)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, task_name, result, details, response_time]
        write_csv_row(csv_file, row)
        print(f"{timestamp} | {task_name}: {result} - {details} (Response time: {response_time}s)")
    driver.quit()


if __name__ == '__main__':
    CSV_FILE = "task_results.csv"
    # Đường dẫn file HTML cục bộ (định dạng URL: file:///...)
    HTML_FILE = "file:///Users/hieu/Documents/Python2/First_TC_Automation/signup_form.html"

    setup_csv(CSV_FILE)
    run_all_tasks(CSV_FILE, HTML_FILE)
