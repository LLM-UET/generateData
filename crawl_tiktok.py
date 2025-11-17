import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


# Đường dẫn profile Edge thật, lấy từ edge://version
PROFILE_PATH = r"C:\Users\OS\AppData\Local\Microsoft\Edge\User Data\Profile 1"

LINK_FILE = "links.txt"
OUTPUT_FILE = "tiktok_comments.csv"


def setup_driver():
    edge_options = Options()

    # Dùng profile thật (đã đăng nhập TikTok)
    edge_options.add_argument(f"user-data-dir={PROFILE_PATH}")

    # Giảm bị phát hiện automation
    edge_options.add_argument("--disable-blink-features=AutomationControlled")

    # Dùng Service theo API Selenium mới
    service = Service("msedgedriver.exe")  # file đặt cùng thư mục script

    driver = webdriver.Edge(service=service, options=edge_options)
    driver.set_window_size(1300, 900)
    return driver


def load_links():
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def scroll_page(driver, num_scroll=25, delay=1.5):
    """
    Scroll toàn trang nhiều lần cho đơn giản để TikTok load thêm comment.
    Nếu cần mình sẽ tối ưu lại để scroll đúng khung comment sau.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(num_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_comments(driver):
    """
    Lấy comment dựa trên DOM thực tế từ ảnh bạn gửi.
    """

    # Selector chính xác bạn đang dùng
    selector = 'span[data-e2e="comment-level-1"]'

    elems = driver.find_elements(By.CSS_SELECTOR, selector)
    comments = []

    for e in elems:
        txt = e.text.strip()
        if txt:
            comments.append(txt)

    print(f"  → Dùng selector: {selector}")
    print(f"  → Thu được {len(comments)} comment.")
    return comments



def save_comments(comments):
    """
    Append vào CSV, mỗi comment được bao trong dấu ngoặc kép để tránh lỗi tách cột.
    """
    is_new_file = not os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as f:
        # QUAN TRỌNG: quotechar='"', quoting=csv.QUOTE_ALL
        writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)

        # Nếu file mới → thêm header
        if is_new_file:
            writer.writerow(["comment"])

        # Ghi từng comment vào dấu ngoặc kép
        for cmt in comments:
            writer.writerow([cmt])



def main():
    print("Đang mở Edge...")
    driver = setup_driver()

    links = load_links()
    print(f"Đã tải {len(links)} link từ {LINK_FILE}.")

    for idx, link in enumerate(links, start=1):
        print(f"\n[{idx}/{len(links)}] Đang crawl: {link}")
        driver.get(link)
        time.sleep(4)  # chờ trang load

        print("  → Scroll để load thêm comment...")
        scroll_page(driver)

        print("  → Đang trích xuất comment...")
        comments = extract_comments(driver)

        print("  → Lưu vào CSV...")
        save_comments(comments)

        time.sleep(2)

    driver.quit()
    print("\nHoàn tất. Comment mới đã được append vào tiktok_comments.csv")


if __name__ == "__main__":
    main()
